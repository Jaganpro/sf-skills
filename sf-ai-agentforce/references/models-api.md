<!-- Parent: sf-ai-agentforce/SKILL.md -->
   1 <!-- TIER: 3 | DETAILED REFERENCE -->
   2 <!-- Read after: SKILL.md, agent-script-reference.md -->
   3 <!-- Purpose: Native AI API (aiplatform.ModelsAPI) patterns for Apex -->
   4 
   5 # Agentforce Models API
   6 
   7 > Native AI generation in Apex using `aiplatform.ModelsAPI` namespace
   8 
   9 ## Overview
  10 
  11 The **Agentforce Models API** enables native LLM access directly from Apex code without external HTTP callouts. This API is part of the `aiplatform` namespace and provides access to Salesforce-managed AI models.
  12 
  13 ```
  14 ┌─────────────────────────────────────────────────────────────────────────────┐
  15 │                    MODELS API ARCHITECTURE                                   │
  16 ├─────────────────────────────────────────────────────────────────────────────┤
  17 │                                                                             │
  18 │  Your Apex Code                                                             │
  19 │       │                                                                     │
  20 │       ▼                                                                     │
  21 │  aiplatform.ModelsAPI.createGenerations()                                   │
  22 │       │                                                                     │
  23 │       ▼                                                                     │
  24 │  Salesforce AI Gateway                                                      │
  25 │       │                                                                     │
  26 │       ▼                                                                     │
  27 │  Foundation Model (GPT-4o Mini, etc.)                                       │
  28 │                                                                             │
  29 └─────────────────────────────────────────────────────────────────────────────┘
  30 ```
  31 
  32 ---
  33 
  34 ## Prerequisites
  35 
  36 ### API Version Requirement
  37 
  38 **Minimum API v61.0+ (Spring '25)** for Models API support.
  39 
  40 ```bash
  41 # Verify org API version
  42 sf org display --target-org [alias] --json | jq '.result.apiVersion'
  43 ```
  44 
  45 ### Einstein Generative AI Setup
  46 
  47 1. **Einstein Generative AI** must be enabled in Setup
  48 2. User must have **Einstein Generative AI User** permission set
  49 3. Organization must have Einstein AI entitlement
  50 
  51 ```
  52 Setup → Einstein Setup → Turn on Einstein
  53 Setup → Permission Sets → Einstein Generative AI User → Assign to users
  54 ```
  55 
  56 ---
  57 
  58 ## Available Models
  59 
  60 | Model Name | Description | Use Case |
  61 |------------|-------------|----------|
  62 | `sfdc_ai__DefaultOpenAIGPT4OmniMini` | GPT-4o Mini | Cost-effective general tasks |
  63 | `sfdc_ai__DefaultOpenAIGPT4Omni` | GPT-4o | Complex reasoning tasks |
  64 | `sfdc_ai__DefaultAnthropic` | Claude (Anthropic) | Nuanced understanding |
  65 | `sfdc_ai__DefaultGoogleGemini` | Google Gemini | Multimodal tasks |
  66 
  67 > **Note**: Available models depend on your Salesforce edition and Einstein entitlements.
  68 
  69 ---
  70 
  71 ## Basic Usage
  72 
  73 ### Simple Text Generation
  74 
  75 ```apex
  76 public class ModelsApiExample {
  77 
  78     public static String generateText(String prompt) {
  79         // Create the request
  80         aiplatform.ModelsAPI.createGenerations_Request request =
  81             new aiplatform.ModelsAPI.createGenerations_Request();
  82 
  83         // Set the model
  84         request.modelName = 'sfdc_ai__DefaultOpenAIGPT4OmniMini';
  85 
  86         // Create the generation input
  87         aiplatform.ModelsAPI_GenerationRequest genRequest =
  88             new aiplatform.ModelsAPI_GenerationRequest();
  89         genRequest.prompt = prompt;
  90 
  91         request.body = genRequest;
  92 
  93         // Call the API
  94         aiplatform.ModelsAPI.createGenerations_Response response =
  95             aiplatform.ModelsAPI.createGenerations(request);
  96 
  97         // Extract the generated text
  98         if (response.Code200 != null &&
  99             response.Code200.generations != null &&
 100             !response.Code200.generations.isEmpty()) {
 101             return response.Code200.generations[0].text;
 102         }
 103 
 104         return null;
 105     }
 106 }
 107 ```
 108 
 109 ---
 110 
 111 ## Queueable Integration
 112 
 113 Use Queueable for async AI processing with record context:
 114 
 115 ### ❌ BAD: Synchronous AI Calls in Triggers
 116 
 117 ```apex
 118 // DON'T DO THIS - blocks transaction, hits limits
 119 trigger CaseTrigger on Case (after insert) {
 120     for (Case c : Trigger.new) {
 121         String summary = ModelsApiExample.generateText(c.Description);
 122         // This will fail or timeout
 123     }
 124 }
 125 ```
 126 
 127 ### ✅ GOOD: Queueable for Async AI Processing
 128 
 129 ```apex
 130 /**
 131  * @description Queueable job for generating AI summaries
 132  * @implements Database.AllowsCallouts - Required for API calls
 133  */
 134 public with sharing class CaseSummaryQueueable implements Queueable, Database.AllowsCallouts {
 135 
 136     private List<Id> caseIds;
 137 
 138     public CaseSummaryQueueable(List<Id> caseIds) {
 139         this.caseIds = caseIds;
 140     }
 141 
 142     public void execute(QueueableContext context) {
 143         // Query cases
 144         List<Case> cases = [
 145             SELECT Id, Subject, Description
 146             FROM Case
 147             WHERE Id IN :caseIds
 148             WITH USER_MODE
 149         ];
 150 
 151         List<Case> toUpdate = new List<Case>();
 152 
 153         for (Case c : cases) {
 154             try {
 155                 // Generate summary using Models API
 156                 String summary = generateCaseSummary(c);
 157 
 158                 if (String.isNotBlank(summary)) {
 159                     c.AI_Summary__c = summary;
 160                     toUpdate.add(c);
 161                 }
 162             } catch (Exception e) {
 163                 System.debug(LoggingLevel.ERROR,
 164                     'AI Summary Error for Case ' + c.Id + ': ' + e.getMessage());
 165             }
 166         }
 167 
 168         // Update records
 169         if (!toUpdate.isEmpty()) {
 170             update toUpdate;
 171         }
 172     }
 173 
 174     private String generateCaseSummary(Case c) {
 175         String prompt = 'Summarize this customer support case in 2-3 sentences:\n\n' +
 176             'Subject: ' + c.Subject + '\n' +
 177             'Description: ' + c.Description;
 178 
 179         aiplatform.ModelsAPI.createGenerations_Request request =
 180             new aiplatform.ModelsAPI.createGenerations_Request();
 181         request.modelName = 'sfdc_ai__DefaultOpenAIGPT4OmniMini';
 182 
 183         aiplatform.ModelsAPI_GenerationRequest genRequest =
 184             new aiplatform.ModelsAPI_GenerationRequest();
 185         genRequest.prompt = prompt;
 186         request.body = genRequest;
 187 
 188         aiplatform.ModelsAPI.createGenerations_Response response =
 189             aiplatform.ModelsAPI.createGenerations(request);
 190 
 191         if (response.Code200 != null &&
 192             response.Code200.generations != null &&
 193             !response.Code200.generations.isEmpty()) {
 194             return response.Code200.generations[0].text;
 195         }
 196 
 197         return null;
 198     }
 199 }
 200 ```
 201 
 202 ### Invoking from Trigger
 203 
 204 ```apex
 205 trigger CaseTrigger on Case (after insert) {
 206     List<Id> newCaseIds = new List<Id>();
 207 
 208     for (Case c : Trigger.new) {
 209         if (String.isNotBlank(c.Description)) {
 210             newCaseIds.add(c.Id);
 211         }
 212     }
 213 
 214     if (!newCaseIds.isEmpty()) {
 215         // Enqueue async processing - non-blocking
 216         System.enqueueJob(new CaseSummaryQueueable(newCaseIds));
 217     }
 218 }
 219 ```
 220 
 221 ---
 222 
 223 ## Batch Class Integration
 224 
 225 For bulk AI processing, use Batch Apex:
 226 
 227 ```apex
 228 /**
 229  * @description Batch job for generating AI content on records
 230  * @implements Database.AllowsCallouts, Database.Stateful
 231  */
 232 public with sharing class OpportunitySummaryBatch
 233     implements Database.Batchable<sObject>, Database.AllowsCallouts, Database.Stateful {
 234 
 235     // Track statistics across batches
 236     private Integer successCount = 0;
 237     private Integer errorCount = 0;
 238 
 239     public Database.QueryLocator start(Database.BatchableContext bc) {
 240         // Query records needing AI summary
 241         return Database.getQueryLocator([
 242             SELECT Id, Name, Description, StageName, Amount
 243             FROM Opportunity
 244             WHERE AI_Summary__c = null
 245             AND Description != null
 246             ORDER BY CreatedDate DESC
 247         ]);
 248     }
 249 
 250     public void execute(Database.BatchableContext bc, List<Opportunity> scope) {
 251         List<Opportunity> toUpdate = new List<Opportunity>();
 252 
 253         for (Opportunity opp : scope) {
 254             try {
 255                 String summary = generateOpportunitySummary(opp);
 256 
 257                 if (String.isNotBlank(summary)) {
 258                     opp.AI_Summary__c = summary;
 259                     toUpdate.add(opp);
 260                     successCount++;
 261                 }
 262             } catch (Exception e) {
 263                 errorCount++;
 264                 System.debug(LoggingLevel.ERROR,
 265                     'AI Summary Error for Opp ' + opp.Id + ': ' + e.getMessage());
 266             }
 267         }
 268 
 269         if (!toUpdate.isEmpty()) {
 270             update toUpdate;
 271         }
 272     }
 273 
 274     public void finish(Database.BatchableContext bc) {
 275         System.debug('Batch Complete. Success: ' + successCount + ', Errors: ' + errorCount);
 276 
 277         // Optional: Send completion notification
 278         // Messaging.SingleEmailMessage email = ...
 279     }
 280 
 281     private String generateOpportunitySummary(Opportunity opp) {
 282         String prompt = 'Create a brief sales summary for this opportunity:\n\n' +
 283             'Name: ' + opp.Name + '\n' +
 284             'Stage: ' + opp.StageName + '\n' +
 285             'Amount: $' + opp.Amount + '\n' +
 286             'Description: ' + opp.Description + '\n\n' +
 287             'Summarize in 2-3 sentences focusing on key points.';
 288 
 289         // Use same API pattern as Queueable
 290         aiplatform.ModelsAPI.createGenerations_Request request =
 291             new aiplatform.ModelsAPI.createGenerations_Request();
 292         request.modelName = 'sfdc_ai__DefaultOpenAIGPT4OmniMini';
 293 
 294         aiplatform.ModelsAPI_GenerationRequest genRequest =
 295             new aiplatform.ModelsAPI_GenerationRequest();
 296         genRequest.prompt = prompt;
 297         request.body = genRequest;
 298 
 299         aiplatform.ModelsAPI.createGenerations_Response response =
 300             aiplatform.ModelsAPI.createGenerations(request);
 301 
 302         if (response.Code200 != null &&
 303             response.Code200.generations != null &&
 304             !response.Code200.generations.isEmpty()) {
 305             return response.Code200.generations[0].text;
 306         }
 307 
 308         return null;
 309     }
 310 }
 311 ```
 312 
 313 ### Batch Size Considerations
 314 
 315 | Batch Size | AI Calls/Batch | Recommended For |
 316 |------------|----------------|-----------------|
 317 | 1-5 | 1-5 | Complex prompts, detailed output |
 318 | 10-20 | 10-20 | Standard summaries |
 319 | 50+ | Avoid | Risk of timeout, use smaller batches |
 320 
 321 ```apex
 322 // Execute with smaller batch size for AI processing
 323 Database.executeBatch(new OpportunitySummaryBatch(), 10);
 324 ```
 325 
 326 ---
 327 
 328 ## Chatter Integration
 329 
 330 Post AI-generated content to Chatter:
 331 
 332 ```apex
 333 public with sharing class ChatterAIService {
 334 
 335     /**
 336      * @description Generate and post AI insight to Chatter
 337      * @param recordId The record to analyze
 338      * @param feedMessage Additional context for the post
 339      */
 340     public static void postAIInsight(Id recordId, String feedMessage) {
 341         // Query record context
 342         Account acc = [
 343             SELECT Name, Industry, AnnualRevenue, Description
 344             FROM Account
 345             WHERE Id = :recordId
 346             LIMIT 1
 347         ];
 348 
 349         // Generate insight using Models API
 350         String prompt = 'Analyze this account and provide 3 key business insights:\n\n' +
 351             'Company: ' + acc.Name + '\n' +
 352             'Industry: ' + acc.Industry + '\n' +
 353             'Revenue: $' + acc.AnnualRevenue + '\n' +
 354             'Description: ' + acc.Description + '\n\n' +
 355             'Format as numbered bullet points.';
 356 
 357         String insight = generateText(prompt);
 358 
 359         if (String.isNotBlank(insight)) {
 360             // Create Chatter post
 361             ConnectApi.FeedItemInput feedInput = new ConnectApi.FeedItemInput();
 362             ConnectApi.MessageBodyInput messageInput = new ConnectApi.MessageBodyInput();
 363             ConnectApi.TextSegmentInput textSegment = new ConnectApi.TextSegmentInput();
 364 
 365             textSegment.text = '🤖 AI Account Insight:\n\n' + insight;
 366             messageInput.messageSegments = new List<ConnectApi.MessageSegmentInput>{ textSegment };
 367             feedInput.body = messageInput;
 368             feedInput.feedElementType = ConnectApi.FeedElementType.FeedItem;
 369             feedInput.subjectId = recordId;
 370 
 371             ConnectApi.ChatterFeeds.postFeedElement(
 372                 Network.getNetworkId(),
 373                 feedInput
 374             );
 375         }
 376     }
 377 
 378     private static String generateText(String prompt) {
 379         aiplatform.ModelsAPI.createGenerations_Request request =
 380             new aiplatform.ModelsAPI.createGenerations_Request();
 381         request.modelName = 'sfdc_ai__DefaultOpenAIGPT4OmniMini';
 382 
 383         aiplatform.ModelsAPI_GenerationRequest genRequest =
 384             new aiplatform.ModelsAPI_GenerationRequest();
 385         genRequest.prompt = prompt;
 386         request.body = genRequest;
 387 
 388         aiplatform.ModelsAPI.createGenerations_Response response =
 389             aiplatform.ModelsAPI.createGenerations(request);
 390 
 391         if (response.Code200 != null &&
 392             response.Code200.generations != null &&
 393             !response.Code200.generations.isEmpty()) {
 394             return response.Code200.generations[0].text;
 395         }
 396 
 397         return null;
 398     }
 399 }
 400 ```
 401 
 402 ---
 403 
 404 ## Governor Limits & Best Practices
 405 
 406 ### Limits to Consider
 407 
 408 | Limit | Value | Mitigation |
 409 |-------|-------|------------|
 410 | Callout time | 120s total | Use smaller batches, Queueable chaining |
 411 | Callouts per transaction | 100 | Batch records, use async |
 412 | CPU time | 10s sync, 60s async | Use Queueable/Batch |
 413 | Heap size | 6MB sync, 12MB async | Limit prompt/response size |
 414 
 415 ### Best Practices
 416 
 417 ```
 418 ┌─────────────────────────────────────────────────────────────────────────────┐
 419 │                    MODELS API BEST PRACTICES                                │
 420 ├─────────────────────────────────────────────────────────────────────────────┤
 421 │                                                                             │
 422 │  ARCHITECTURE                                                               │
 423 │  ─────────────────────────────────────────────────────────────────────────  │
 424 │  ✅ Use Queueable for single-record async processing                        │
 425 │  ✅ Use Batch for bulk processing (scope size 10-20)                        │
 426 │  ✅ Use Platform Events for notification when AI completes                  │
 427 │  ✅ Cache common AI responses if possible                                   │
 428 │  ❌ Don't call Models API synchronously in triggers                         │
 429 │  ❌ Don't process unbounded record sets                                     │
 430 │                                                                             │
 431 │  PROMPTS                                                                    │
 432 │  ─────────────────────────────────────────────────────────────────────────  │
 433 │  ✅ Be specific about expected output format                                │
 434 │  ✅ Set length constraints ("summarize in 2 sentences")                     │
 435 │  ✅ Include context needed for accurate responses                           │
 436 │  ❌ Don't include PII in prompts unless necessary                           │
 437 │  ❌ Don't rely on AI for compliance-critical decisions                      │
 438 │                                                                             │
 439 │  ERROR HANDLING                                                             │
 440 │  ─────────────────────────────────────────────────────────────────────────  │
 441 │  ✅ Wrap API calls in try-catch                                             │
 442 │  ✅ Log errors with context for debugging                                   │
 443 │  ✅ Implement retry logic for transient failures                            │
 444 │  ✅ Check response.Code200 before accessing results                         │
 445 │  ❌ Don't assume AI responses are always successful                         │
 446 │                                                                             │
 447 └─────────────────────────────────────────────────────────────────────────────┘
 448 ```
 449 
 450 ---
 451 
 452 ## Common Patterns
 453 
 454 ### Pattern 1: Service Layer Abstraction
 455 
 456 ```apex
 457 public with sharing class AIGenerationService {
 458 
 459     private static final String DEFAULT_MODEL = 'sfdc_ai__DefaultOpenAIGPT4OmniMini';
 460 
 461     /**
 462      * @description Generate text with standard configuration
 463      */
 464     public static String generate(String prompt) {
 465         return generate(prompt, DEFAULT_MODEL);
 466     }
 467 
 468     /**
 469      * @description Generate text with specific model
 470      */
 471     public static String generate(String prompt, String modelName) {
 472         try {
 473             aiplatform.ModelsAPI.createGenerations_Request request =
 474                 new aiplatform.ModelsAPI.createGenerations_Request();
 475             request.modelName = modelName;
 476 
 477             aiplatform.ModelsAPI_GenerationRequest genRequest =
 478                 new aiplatform.ModelsAPI_GenerationRequest();
 479             genRequest.prompt = prompt;
 480             request.body = genRequest;
 481 
 482             aiplatform.ModelsAPI.createGenerations_Response response =
 483                 aiplatform.ModelsAPI.createGenerations(request);
 484 
 485             if (response.Code200 != null &&
 486                 response.Code200.generations != null &&
 487                 !response.Code200.generations.isEmpty()) {
 488                 return response.Code200.generations[0].text;
 489             }
 490         } catch (Exception e) {
 491             System.debug(LoggingLevel.ERROR, 'AI Generation Error: ' + e.getMessage());
 492         }
 493 
 494         return null;
 495     }
 496 }
 497 ```
 498 
 499 ### Pattern 2: Notify Completion via Platform Events
 500 
 501 ```apex
 502 // Platform Event: AI_Generation_Complete__e
 503 // Fields: Record_Id__c (Text), Status__c (Text), Summary__c (Long Text)
 504 
 505 public with sharing class AIQueueableWithNotification
 506     implements Queueable, Database.AllowsCallouts {
 507 
 508     private Id recordId;
 509 
 510     public AIQueueableWithNotification(Id recordId) {
 511         this.recordId = recordId;
 512     }
 513 
 514     public void execute(QueueableContext context) {
 515         String summary;
 516         String status = 'Success';
 517 
 518         try {
 519             // Generate AI content
 520             summary = AIGenerationService.generate('...');
 521         } catch (Exception e) {
 522             status = 'Error: ' + e.getMessage();
 523         }
 524 
 525         // Publish completion event
 526         AI_Generation_Complete__e event = new AI_Generation_Complete__e();
 527         event.Record_Id__c = recordId;
 528         event.Status__c = status;
 529         event.Summary__c = summary;
 530 
 531         EventBus.publish(event);
 532     }
 533 }
 534 ```
 535 
 536 ### Pattern 3: LWC Subscribes to Completion
 537 
 538 ```javascript
 539 // In your LWC controller
 540 import { subscribe, unsubscribe, onError } from 'lightning/empApi';
 541 
 542 connectedCallback() {
 543     this.subscribeToAICompletion();
 544 }
 545 
 546 subscribeToAICompletion() {
 547     const channelName = '/event/AI_Generation_Complete__e';
 548 
 549     subscribe(channelName, -1, (message) => {
 550         const payload = message.data.payload;
 551 
 552         if (payload.Record_Id__c === this.recordId) {
 553             this.aiSummary = payload.Summary__c;
 554             this.isLoading = false;
 555         }
 556     }).then((response) => {
 557         this.subscription = response;
 558     });
 559 }
 560 ```
 561 
 562 ---
 563 
 564 ## Troubleshooting
 565 
 566 | Issue | Cause | Solution |
 567 |-------|-------|----------|
 568 | "Model not found" | Invalid model name | Use exact name: `sfdc_ai__DefaultOpenAIGPT4OmniMini` |
 569 | "Access denied" | Missing permission | Assign Einstein Generative AI User permission set |
 570 | "Callout not allowed" | Sync context restriction | Use Queueable with `Database.AllowsCallouts` |
 571 | Timeout errors | Large prompt/response | Reduce prompt size, use batch with smaller scope |
 572 | Empty response | Null check failed | Always validate `response.Code200` and `generations` |
 573 
 574 ---
 575 
 576 ## Related Documentation
 577 
 578 - [Prompt Templates](prompt-templates.md) - Using AI via metadata
 579 - [Actions Reference](actions-reference.md) - Agent actions with AI
 580 - [Salesforce AI Documentation](https://developer.salesforce.com/docs/einstein/genai/overview)
 581 
 582 ---
 583 
 584 ## Source
 585 
 586 > **Reference**: [Agentforce API Generating Case Summaries with Apex Queueable](https://salesforcediaries.com/2025/07/15/agentforce-api-generating-case-summaries-with-apex-queueable/) - Salesforce Diaries
