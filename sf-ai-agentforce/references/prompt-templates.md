<!-- Parent: sf-ai-agentforce/SKILL.md -->
   1 <!-- TIER: 3 | DETAILED REFERENCE -->
   2 <!-- Read after: SKILL.md, agent-script-reference.md -->
   3 <!-- Purpose: PromptTemplate metadata and generatePromptResponse:// actions -->
   4 
   5 # Prompt Templates
   6 
   7 > Complete guide to creating PromptTemplate metadata for Salesforce Einstein and Agentforce
   8 
   9 ## Overview
  10 
  11 `PromptTemplate` is the metadata type for creating reusable AI prompts in Salesforce. Templates can be used by Einstein features, Agentforce agents, and custom Apex code.
  12 
  13 ```
  14 ┌─────────────────────────────────────────────────────────────────────────────┐
  15 │                    PROMPT TEMPLATE ECOSYSTEM                                │
  16 ├─────────────────────────────────────────────────────────────────────────────┤
  17 │                                                                             │
  18 │  PromptTemplate  ──────►  Einstein Prompt Builder (UI)                      │
  19 │                  ──────►  GenAiFunction (Agent Actions)                     │
  20 │                  ──────►  ConnectApi.Einstein.evaluatePrompt() (Apex)       │
  21 │                  ──────►  Flow Prompt Template Action                       │
  22 │                                                                             │
  23 └─────────────────────────────────────────────────────────────────────────────┘
  24 ```
  25 
  26 ---
  27 
  28 ## Template Types
  29 
  30 | Type | Use Case | Example |
  31 |------|----------|---------|
  32 | `flexPrompt` | General purpose, maximum flexibility | Custom AI tasks |
  33 | `salesGeneration` | Sales content creation | Email drafts, proposals |
  34 | `fieldCompletion` | Suggest field values | Auto-populate fields |
  35 | `recordSummary` | Summarize record data | Case summaries, account briefs |
  36 
  37 ---
  38 
  39 ## Metadata Structure
  40 
  41 ### Full Schema
  42 
  43 ```xml
  44 <?xml version="1.0" encoding="UTF-8"?>
  45 <PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
  46     <!-- Required: API name -->
  47     <fullName>{{TemplateName}}</fullName>
  48 
  49     <!-- Required: Display name -->
  50     <masterLabel>{{Template Display Label}}</masterLabel>
  51 
  52     <!-- Required: Description -->
  53     <description>{{What this template does}}</description>
  54 
  55     <!-- Required: Template type -->
  56     <type>{{flexPrompt|salesGeneration|fieldCompletion|recordSummary}}</type>
  57 
  58     <!-- Required: Active status -->
  59     <isActive>true</isActive>
  60 
  61     <!-- Optional: Primary object (for record-bound templates) -->
  62     <objectType>{{ObjectApiName}}</objectType>
  63 
  64     <!-- Required: The prompt content -->
  65     <promptContent>
  66         {{Your prompt with {!variable} placeholders}}
  67     </promptContent>
  68 
  69     <!-- Variable definitions (0 or more) -->
  70     <promptTemplateVariables>
  71         <developerName>{{variableName}}</developerName>
  72         <promptTemplateVariableType>{{freeText|recordField|relatedList|resource}}</promptTemplateVariableType>
  73         <isRequired>{{true|false}}</isRequired>
  74         <!-- For recordField type -->
  75         <objectType>{{ObjectApiName}}</objectType>
  76         <fieldName>{{FieldApiName}}</fieldName>
  77     </promptTemplateVariables>
  78 </PromptTemplate>
  79 ```
  80 
  81 ---
  82 
  83 ## Variable Types
  84 
  85 ### freeText
  86 
  87 User-provided text input at runtime.
  88 
  89 ```xml
  90 <promptTemplateVariables>
  91     <developerName>customerQuestion</developerName>
  92     <promptTemplateVariableType>freeText</promptTemplateVariableType>
  93     <isRequired>true</isRequired>
  94 </promptTemplateVariables>
  95 ```
  96 
  97 **Usage in prompt:**
  98 ```
  99 Customer Question: {!customerQuestion}
 100 ```
 101 
 102 ### recordField
 103 
 104 Binds to a specific field on a Salesforce record.
 105 
 106 ```xml
 107 <promptTemplateVariables>
 108     <developerName>accountName</developerName>
 109     <promptTemplateVariableType>recordField</promptTemplateVariableType>
 110     <objectType>Account</objectType>
 111     <fieldName>Name</fieldName>
 112     <isRequired>true</isRequired>
 113 </promptTemplateVariables>
 114 ```
 115 
 116 **Relationship traversal:**
 117 ```xml
 118 <promptTemplateVariables>
 119     <developerName>ownerEmail</developerName>
 120     <promptTemplateVariableType>recordField</promptTemplateVariableType>
 121     <objectType>Case</objectType>
 122     <fieldName>Owner.Email</fieldName>
 123     <isRequired>false</isRequired>
 124 </promptTemplateVariables>
 125 ```
 126 
 127 ### relatedList
 128 
 129 Data from related records.
 130 
 131 ```xml
 132 <promptTemplateVariables>
 133     <developerName>recentCases</developerName>
 134     <promptTemplateVariableType>relatedList</promptTemplateVariableType>
 135     <objectType>Account</objectType>
 136     <fieldName>Cases</fieldName>
 137     <isRequired>false</isRequired>
 138 </promptTemplateVariables>
 139 ```
 140 
 141 ### resource
 142 
 143 Content from a Static Resource.
 144 
 145 ```xml
 146 <promptTemplateVariables>
 147     <developerName>brandGuidelines</developerName>
 148     <promptTemplateVariableType>resource</promptTemplateVariableType>
 149     <resourceName>Brand_Voice_Guidelines</resourceName>
 150     <isRequired>false</isRequired>
 151 </promptTemplateVariables>
 152 ```
 153 
 154 ---
 155 
 156 ## Complete Examples
 157 
 158 ### Example 1: Flex Prompt (General Purpose)
 159 
 160 **Use Case:** Answer questions using knowledge base context.
 161 
 162 ```xml
 163 <?xml version="1.0" encoding="UTF-8"?>
 164 <PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
 165     <fullName>Knowledge_Assistant</fullName>
 166     <masterLabel>Knowledge Assistant</masterLabel>
 167     <description>Answers questions using knowledge article context</description>
 168 
 169     <type>flexPrompt</type>
 170     <isActive>true</isActive>
 171 
 172     <promptContent>
 173 You are a helpful customer support assistant for {{CompanyName}}.
 174 
 175 Use the following knowledge base context to answer the customer's question:
 176 
 177 --- KNOWLEDGE CONTEXT ---
 178 {!knowledgeContext}
 179 --- END CONTEXT ---
 180 
 181 Customer Question:
 182 {!customerQuestion}
 183 
 184 Instructions:
 185 1. Answer based ONLY on the provided context
 186 2. If the context doesn't contain the answer, say "I don't have that information"
 187 3. Be concise but complete
 188 4. Use a friendly, professional tone
 189 5. Include relevant article references when applicable
 190 
 191 Response:
 192     </promptContent>
 193 
 194     <promptTemplateVariables>
 195         <developerName>knowledgeContext</developerName>
 196         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 197         <isRequired>true</isRequired>
 198     </promptTemplateVariables>
 199 
 200     <promptTemplateVariables>
 201         <developerName>customerQuestion</developerName>
 202         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 203         <isRequired>true</isRequired>
 204     </promptTemplateVariables>
 205 </PromptTemplate>
 206 ```
 207 
 208 **File Location:**
 209 ```
 210 force-app/main/default/promptTemplates/Knowledge_Assistant.promptTemplate-meta.xml
 211 ```
 212 
 213 ---
 214 
 215 ### Example 2: Record Summary
 216 
 217 **Use Case:** Generate executive summary for Opportunity records.
 218 
 219 ```xml
 220 <?xml version="1.0" encoding="UTF-8"?>
 221 <PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
 222     <fullName>Opportunity_Executive_Summary</fullName>
 223     <masterLabel>Opportunity Executive Summary</masterLabel>
 224     <description>Generates executive briefing for opportunity reviews</description>
 225 
 226     <type>recordSummary</type>
 227     <isActive>true</isActive>
 228     <objectType>Opportunity</objectType>
 229 
 230     <promptContent>
 231 Generate an executive summary for the following sales opportunity:
 232 
 233 OPPORTUNITY DETAILS
 234 ═══════════════════════════════════════════════════════════════════
 235 Name: {!opportunityName}
 236 Account: {!accountName}
 237 Amount: ${!amount}
 238 Stage: {!stageName}
 239 Close Date: {!closeDate}
 240 Probability: {!probability}%
 241 Owner: {!ownerName}
 242 
 243 Description:
 244 {!description}
 245 
 246 Next Steps:
 247 {!nextStep}
 248 
 249 Competitor Information:
 250 {!competitorInfo}
 251 ═══════════════════════════════════════════════════════════════════
 252 
 253 Create an executive summary (150 words max) that includes:
 254 
 255 1. **Deal Overview**: One sentence on what we're selling and to whom
 256 2. **Current Status**: Where we are in the sales cycle
 257 3. **Key Risks**: Top 2-3 risks to closing
 258 4. **Recommended Actions**: Priority actions for the sales team
 259 5. **Win Probability Assessment**: Your assessment of likelihood to close
 260 
 261 Format the output with clear section headers.
 262     </promptContent>
 263 
 264     <!-- Core opportunity fields -->
 265     <promptTemplateVariables>
 266         <developerName>opportunityName</developerName>
 267         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 268         <objectType>Opportunity</objectType>
 269         <fieldName>Name</fieldName>
 270         <isRequired>true</isRequired>
 271     </promptTemplateVariables>
 272 
 273     <promptTemplateVariables>
 274         <developerName>accountName</developerName>
 275         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 276         <objectType>Opportunity</objectType>
 277         <fieldName>Account.Name</fieldName>
 278         <isRequired>true</isRequired>
 279     </promptTemplateVariables>
 280 
 281     <promptTemplateVariables>
 282         <developerName>amount</developerName>
 283         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 284         <objectType>Opportunity</objectType>
 285         <fieldName>Amount</fieldName>
 286         <isRequired>false</isRequired>
 287     </promptTemplateVariables>
 288 
 289     <promptTemplateVariables>
 290         <developerName>stageName</developerName>
 291         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 292         <objectType>Opportunity</objectType>
 293         <fieldName>StageName</fieldName>
 294         <isRequired>true</isRequired>
 295     </promptTemplateVariables>
 296 
 297     <promptTemplateVariables>
 298         <developerName>closeDate</developerName>
 299         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 300         <objectType>Opportunity</objectType>
 301         <fieldName>CloseDate</fieldName>
 302         <isRequired>true</isRequired>
 303     </promptTemplateVariables>
 304 
 305     <promptTemplateVariables>
 306         <developerName>probability</developerName>
 307         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 308         <objectType>Opportunity</objectType>
 309         <fieldName>Probability</fieldName>
 310         <isRequired>false</isRequired>
 311     </promptTemplateVariables>
 312 
 313     <promptTemplateVariables>
 314         <developerName>ownerName</developerName>
 315         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 316         <objectType>Opportunity</objectType>
 317         <fieldName>Owner.Name</fieldName>
 318         <isRequired>false</isRequired>
 319     </promptTemplateVariables>
 320 
 321     <promptTemplateVariables>
 322         <developerName>description</developerName>
 323         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 324         <objectType>Opportunity</objectType>
 325         <fieldName>Description</fieldName>
 326         <isRequired>false</isRequired>
 327     </promptTemplateVariables>
 328 
 329     <promptTemplateVariables>
 330         <developerName>nextStep</developerName>
 331         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 332         <objectType>Opportunity</objectType>
 333         <fieldName>NextStep</fieldName>
 334         <isRequired>false</isRequired>
 335     </promptTemplateVariables>
 336 
 337     <promptTemplateVariables>
 338         <developerName>competitorInfo</developerName>
 339         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 340         <isRequired>false</isRequired>
 341     </promptTemplateVariables>
 342 </PromptTemplate>
 343 ```
 344 
 345 ---
 346 
 347 ### Example 3: Sales Generation (Email Draft)
 348 
 349 **Use Case:** Generate follow-up email after a sales call.
 350 
 351 ```xml
 352 <?xml version="1.0" encoding="UTF-8"?>
 353 <PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
 354     <fullName>Sales_Follow_Up_Email</fullName>
 355     <masterLabel>Sales Follow-Up Email Generator</masterLabel>
 356     <description>Generates personalized follow-up emails after sales meetings</description>
 357 
 358     <type>salesGeneration</type>
 359     <isActive>true</isActive>
 360     <objectType>Contact</objectType>
 361 
 362     <promptContent>
 363 Generate a professional follow-up email after a sales meeting.
 364 
 365 RECIPIENT INFORMATION
 366 ─────────────────────────────────────────────────────────────────
 367 Contact Name: {!contactName}
 368 Title: {!contactTitle}
 369 Company: {!accountName}
 370 Industry: {!accountIndustry}
 371 
 372 MEETING CONTEXT
 373 ─────────────────────────────────────────────────────────────────
 374 Meeting Date: {!meetingDate}
 375 Discussion Topics: {!discussionTopics}
 376 Key Pain Points: {!painPoints}
 377 Next Steps Agreed: {!nextSteps}
 378 
 379 SENDER INFORMATION
 380 ─────────────────────────────────────────────────────────────────
 381 Sender Name: {!senderName}
 382 Sender Title: {!senderTitle}
 383 
 384 TONE PREFERENCE
 385 ─────────────────────────────────────────────────────────────────
 386 {!tonePreference}
 387 
 388 Generate a follow-up email that:
 389 1. Thanks them for their time
 390 2. Summarizes key discussion points (2-3 bullets)
 391 3. Reiterates agreed next steps
 392 4. Proposes a specific follow-up action
 393 5. Ends with a professional sign-off
 394 
 395 Keep the email under 200 words. Match the specified tone.
 396     </promptContent>
 397 
 398     <!-- Contact fields -->
 399     <promptTemplateVariables>
 400         <developerName>contactName</developerName>
 401         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 402         <objectType>Contact</objectType>
 403         <fieldName>Name</fieldName>
 404         <isRequired>true</isRequired>
 405     </promptTemplateVariables>
 406 
 407     <promptTemplateVariables>
 408         <developerName>contactTitle</developerName>
 409         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 410         <objectType>Contact</objectType>
 411         <fieldName>Title</fieldName>
 412         <isRequired>false</isRequired>
 413     </promptTemplateVariables>
 414 
 415     <promptTemplateVariables>
 416         <developerName>accountName</developerName>
 417         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 418         <objectType>Contact</objectType>
 419         <fieldName>Account.Name</fieldName>
 420         <isRequired>true</isRequired>
 421     </promptTemplateVariables>
 422 
 423     <promptTemplateVariables>
 424         <developerName>accountIndustry</developerName>
 425         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 426         <objectType>Contact</objectType>
 427         <fieldName>Account.Industry</fieldName>
 428         <isRequired>false</isRequired>
 429     </promptTemplateVariables>
 430 
 431     <!-- Runtime inputs -->
 432     <promptTemplateVariables>
 433         <developerName>meetingDate</developerName>
 434         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 435         <isRequired>true</isRequired>
 436     </promptTemplateVariables>
 437 
 438     <promptTemplateVariables>
 439         <developerName>discussionTopics</developerName>
 440         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 441         <isRequired>true</isRequired>
 442     </promptTemplateVariables>
 443 
 444     <promptTemplateVariables>
 445         <developerName>painPoints</developerName>
 446         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 447         <isRequired>true</isRequired>
 448     </promptTemplateVariables>
 449 
 450     <promptTemplateVariables>
 451         <developerName>nextSteps</developerName>
 452         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 453         <isRequired>true</isRequired>
 454     </promptTemplateVariables>
 455 
 456     <promptTemplateVariables>
 457         <developerName>senderName</developerName>
 458         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 459         <isRequired>true</isRequired>
 460     </promptTemplateVariables>
 461 
 462     <promptTemplateVariables>
 463         <developerName>senderTitle</developerName>
 464         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 465         <isRequired>false</isRequired>
 466     </promptTemplateVariables>
 467 
 468     <promptTemplateVariables>
 469         <developerName>tonePreference</developerName>
 470         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 471         <isRequired>false</isRequired>
 472     </promptTemplateVariables>
 473 </PromptTemplate>
 474 ```
 475 
 476 ---
 477 
 478 ### Example 4: Field Completion
 479 
 480 **Use Case:** Suggest case resolution notes based on case history.
 481 
 482 ```xml
 483 <?xml version="1.0" encoding="UTF-8"?>
 484 <PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
 485     <fullName>Case_Resolution_Suggestion</fullName>
 486     <masterLabel>Case Resolution Suggestion</masterLabel>
 487     <description>Suggests resolution notes for cases based on history</description>
 488 
 489     <type>fieldCompletion</type>
 490     <isActive>true</isActive>
 491     <objectType>Case</objectType>
 492 
 493     <promptContent>
 494 Based on the following case information, suggest appropriate resolution notes:
 495 
 496 CASE INFORMATION
 497 ═══════════════════════════════════════════════════════════════════
 498 Case Number: {!caseNumber}
 499 Subject: {!subject}
 500 Type: {!caseType}
 501 Priority: {!priority}
 502 
 503 Original Description:
 504 {!description}
 505 
 506 Comments/Activities:
 507 {!caseComments}
 508 
 509 Resolution Category: {!resolutionCategory}
 510 ═══════════════════════════════════════════════════════════════════
 511 
 512 Generate resolution notes that:
 513 1. Summarize the issue (1 sentence)
 514 2. Describe the resolution steps taken (2-3 bullets)
 515 3. Note any follow-up actions or recommendations
 516 4. Include relevant KB article references if applicable
 517 
 518 Keep the resolution notes under 150 words.
 519 Maintain a professional, factual tone.
 520     </promptContent>
 521 
 522     <promptTemplateVariables>
 523         <developerName>caseNumber</developerName>
 524         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 525         <objectType>Case</objectType>
 526         <fieldName>CaseNumber</fieldName>
 527         <isRequired>true</isRequired>
 528     </promptTemplateVariables>
 529 
 530     <promptTemplateVariables>
 531         <developerName>subject</developerName>
 532         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 533         <objectType>Case</objectType>
 534         <fieldName>Subject</fieldName>
 535         <isRequired>true</isRequired>
 536     </promptTemplateVariables>
 537 
 538     <promptTemplateVariables>
 539         <developerName>caseType</developerName>
 540         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 541         <objectType>Case</objectType>
 542         <fieldName>Type</fieldName>
 543         <isRequired>false</isRequired>
 544     </promptTemplateVariables>
 545 
 546     <promptTemplateVariables>
 547         <developerName>priority</developerName>
 548         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 549         <objectType>Case</objectType>
 550         <fieldName>Priority</fieldName>
 551         <isRequired>false</isRequired>
 552     </promptTemplateVariables>
 553 
 554     <promptTemplateVariables>
 555         <developerName>description</developerName>
 556         <promptTemplateVariableType>recordField</promptTemplateVariableType>
 557         <objectType>Case</objectType>
 558         <fieldName>Description</fieldName>
 559         <isRequired>true</isRequired>
 560     </promptTemplateVariables>
 561 
 562     <promptTemplateVariables>
 563         <developerName>caseComments</developerName>
 564         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 565         <isRequired>false</isRequired>
 566     </promptTemplateVariables>
 567 
 568     <promptTemplateVariables>
 569         <developerName>resolutionCategory</developerName>
 570         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 571         <isRequired>false</isRequired>
 572     </promptTemplateVariables>
 573 </PromptTemplate>
 574 ```
 575 
 576 ---
 577 
 578 ## Using Prompt Templates
 579 
 580 ### In Agentforce (via GenAiFunction)
 581 
 582 ```xml
 583 <GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
 584     <masterLabel>Generate Opportunity Summary</masterLabel>
 585     <developerName>Generate_Opp_Summary</developerName>
 586     <description>Generates executive summary for an opportunity</description>
 587 
 588     <invocationTarget>Opportunity_Executive_Summary</invocationTarget>
 589     <invocationTargetType>prompt</invocationTargetType>
 590 
 591     <capability>
 592         Generate executive summaries for sales opportunities.
 593     </capability>
 594 
 595     <genAiFunctionInputs>
 596         <developerName>recordId</developerName>
 597         <description>Opportunity record ID</description>
 598         <dataType>Text</dataType>
 599         <isRequired>true</isRequired>
 600     </genAiFunctionInputs>
 601 </GenAiFunction>
 602 ```
 603 
 604 ### In Agent Script (Direct Invocation)
 605 
 606 **NEW - December 2025**: You can invoke PromptTemplates directly from Agent Script without creating a separate GenAiFunction wrapper.
 607 
 608 ```agentscript
 609 topic content_generation:
 610     description: "Generates personalized content using AI"
 611 
 612     actions:
 613         # Prompt Template Action - direct invocation
 614         Generate_Personalized_Schedule:
 615             description: "Generate a personalized schedule with a prompt template."
 616             inputs:
 617                 # CRITICAL: Input names MUST use "Input:" prefix
 618                 "Input:email": string
 619                     description: "User's email address to look up preferences"
 620                     is_required: True
 621                 "Input:timezone": string
 622                     description: "User's timezone for schedule formatting"
 623                     is_required: False
 624             outputs:
 625                 # Standard output field name for prompt responses
 626                 promptResponse: string
 627                     description: "The AI-generated schedule content"
 628                     is_used_by_planner: True
 629                     is_displayable: True
 630             # Target uses generatePromptResponse:// protocol
 631             target: "generatePromptResponse://Generate_Personalized_Schedule"
 632 
 633     reasoning:
 634         instructions: ->
 635             | Help the user create a personalized schedule.
 636             | Ask for their email and timezone preference.
 637         actions:
 638             create_schedule: @actions.Generate_Personalized_Schedule
 639                 with "Input:email"=...
 640                 with "Input:timezone"=...
 641                 set @variables.generated_content = @outputs.promptResponse
 642 ```
 643 
 644 **Key Syntax Points:**
 645 
 646 | Element | Requirement | Example |
 647 |---------|-------------|---------|
 648 | Target protocol | `generatePromptResponse://` | `target: "generatePromptResponse://My_Template"` |
 649 | Input naming | Must have `"Input:"` prefix | `"Input:customerName": string` |
 650 | Output field | Use `promptResponse` | `promptResponse: string` |
 651 | Template name | Must match PromptTemplate API name | Template file: `My_Template.promptTemplate-meta.xml` |
 652 
 653 **Mapping Template Variables:**
 654 
 655 The `"Input:variableName"` in Agent Script maps to `{!variableName}` in your PromptTemplate:
 656 
 657 ```
 658 Agent Script Input          →  PromptTemplate Variable
 659 ────────────────────────────────────────────────────────
 660 "Input:email"              →  {!email}
 661 "Input:customerQuestion"   →  {!customerQuestion}
 662 "Input:context"            →  {!context}
 663 ```
 664 
 665 **Complete Example Workflow:**
 666 
 667 1. **Create PromptTemplate** (`force-app/main/default/promptTemplates/Generate_Personalized_Schedule.promptTemplate-meta.xml`):
 668 
 669 ```xml
 670 <?xml version="1.0" encoding="UTF-8"?>
 671 <PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
 672     <fullName>Generate_Personalized_Schedule</fullName>
 673     <masterLabel>Generate Personalized Schedule</masterLabel>
 674     <description>Creates personalized schedules based on user preferences</description>
 675     <type>flexPrompt</type>
 676     <isActive>true</isActive>
 677 
 678     <promptContent>
 679 Create a personalized daily schedule for the user.
 680 
 681 User Email: {!email}
 682 Timezone: {!timezone}
 683 
 684 Generate a structured schedule that includes:
 685 1. Morning routine
 686 2. Work blocks with breaks
 687 3. Lunch break
 688 4. Afternoon focus time
 689 5. Evening wind-down
 690 
 691 Format as a clean, readable schedule.
 692     </promptContent>
 693 
 694     <promptTemplateVariables>
 695         <developerName>email</developerName>
 696         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 697         <isRequired>true</isRequired>
 698     </promptTemplateVariables>
 699 
 700     <promptTemplateVariables>
 701         <developerName>timezone</developerName>
 702         <promptTemplateVariableType>freeText</promptTemplateVariableType>
 703         <isRequired>false</isRequired>
 704     </promptTemplateVariables>
 705 </PromptTemplate>
 706 ```
 707 
 708 2. **Deploy the PromptTemplate first:**
 709 
 710 ```bash
 711 sf project deploy start -m "PromptTemplate:Generate_Personalized_Schedule"
 712 ```
 713 
 714 3. **Then publish the agent** that references it.
 715 
 716 > ⚠️ **Deployment Order Matters**: The PromptTemplate must exist in the org before publishing an agent that references it via `generatePromptResponse://`.
 717 
 718 ### In Apex
 719 
 720 ```apex
 721 public class PromptTemplateService {
 722 
 723     public static String generateSummary(Id recordId, String templateName) {
 724         // Build input map
 725         Map<String, String> inputMap = new Map<String, String>();
 726         inputMap.put('recordId', recordId);
 727 
 728         // Build prompt input
 729         ConnectApi.EinsteinPromptTemplateGenerationsInput input =
 730             new ConnectApi.EinsteinPromptTemplateGenerationsInput();
 731         input.isPreview = false;
 732         input.inputParams = inputMap;
 733 
 734         // Evaluate prompt
 735         ConnectApi.EinsteinPromptTemplateGenerationsRepresentation result =
 736             ConnectApi.EinsteinLlm.generateMessagesForPromptTemplate(
 737                 templateName,
 738                 input
 739             );
 740 
 741         // Return generated text
 742         return result.generations[0].text;
 743     }
 744 }
 745 ```
 746 
 747 ### In Flow
 748 
 749 1. Add "Prompt Template" action element
 750 2. Select your PromptTemplate
 751 3. Map input variables
 752 4. Store output to a text variable
 753 
 754 ---
 755 
 756 ## Data Cloud Grounding
 757 
 758 For enhanced context using Data Cloud:
 759 
 760 ```xml
 761 <PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
 762     <!-- ... standard elements ... -->
 763 
 764     <dataCloudConfig>
 765         <dataCloudObjectName>Customer_Profile__dlm</dataCloudObjectName>
 766         <retrievalStrategy>semantic</retrievalStrategy>
 767     </dataCloudConfig>
 768 </PromptTemplate>
 769 ```
 770 
 771 ### Retrieval Strategies
 772 
 773 | Strategy | Description |
 774 |----------|-------------|
 775 | `semantic` | Vector-based semantic search |
 776 | `keyword` | Traditional keyword matching |
 777 | `hybrid` | Combination of semantic + keyword |
 778 
 779 ---
 780 
 781 ## Deployment
 782 
 783 ### package.xml Entry
 784 
 785 ```xml
 786 <?xml version="1.0" encoding="UTF-8"?>
 787 <Package xmlns="http://soap.sforce.com/2006/04/metadata">
 788     <types>
 789         <members>*</members>
 790         <name>PromptTemplate</name>
 791     </types>
 792     <version>65.0</version>
 793 </Package>
 794 ```
 795 
 796 ### Deploy Command
 797 
 798 ```bash
 799 # Deploy specific template
 800 sf project deploy start -m "PromptTemplate:Knowledge_Assistant"
 801 
 802 # Deploy all templates
 803 sf project deploy start -m "PromptTemplate:*"
 804 ```
 805 
 806 ---
 807 
 808 ## Best Practices
 809 
 810 ```
 811 ┌─────────────────────────────────────────────────────────────────────────────┐
 812 │                    PROMPT TEMPLATE BEST PRACTICES                           │
 813 ├─────────────────────────────────────────────────────────────────────────────┤
 814 │                                                                             │
 815 │  PROMPT DESIGN                                                              │
 816 │  ─────────────────────────────────────────────────────────────────────────  │
 817 │  ✅ Be specific about output format                                         │
 818 │  ✅ Include examples when helpful                                           │
 819 │  ✅ Set clear constraints (word limits, tone)                               │
 820 │  ✅ Use structured sections with headers                                    │
 821 │  ❌ Don't be vague or overly general                                        │
 822 │                                                                             │
 823 │  VARIABLES                                                                  │
 824 │  ─────────────────────────────────────────────────────────────────────────  │
 825 │  ✅ Use recordField for data from records                                   │
 826 │  ✅ Use freeText for runtime context                                        │
 827 │  ✅ Mark optional variables as isRequired=false                             │
 828 │  ❌ Don't hardcode values that should be dynamic                            │
 829 │                                                                             │
 830 │  SECURITY                                                                   │
 831 │  ─────────────────────────────────────────────────────────────────────────  │
 832 │  ✅ Consider field-level security                                           │
 833 │  ✅ Respect sharing rules                                                   │
 834 │  ✅ Don't expose sensitive data                                             │
 835 │  ❌ Don't include PII in prompt instructions                                │
 836 │                                                                             │
 837 │  MAINTENANCE                                                                │
 838 │  ─────────────────────────────────────────────────────────────────────────  │
 839 │  ✅ Version your templates logically                                        │
 840 │  ✅ Document template purpose                                               │
 841 │  ✅ Test with various input combinations                                    │
 842 │  ❌ Don't create one-off templates for each use case                        │
 843 │                                                                             │
 844 └─────────────────────────────────────────────────────────────────────────────┘
 845 ```
 846 
 847 ---
 848 
 849 ## Troubleshooting
 850 
 851 | Issue | Cause | Solution |
 852 |-------|-------|----------|
 853 | Variable not replaced | Typo in {!name} | Check variable developerName exactly matches |
 854 | "Field not accessible" | FLS issue | Check profile/permission set |
 855 | Empty output | Required field is null | Make variable optional or add fallback |
 856 | Unexpected format | Model interpretation | Be more specific in instructions |
 857 
 858 ---
 859 
 860 ## Related Documentation
 861 
 862 - [Actions Reference](actions-reference.md) - Action configuration and metadata
 863 - [Agent Script Reference](agent-script-reference.md) - Complete syntax guide
 864 - [Einstein Prompt Builder (Salesforce Help)](https://help.salesforce.com/s/articleView?id=sf.prompt_builder.htm)
