<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Data Cloud Query Patterns
   2 
   3 Common query patterns for extracting and analyzing Agentforce session tracing data.
   4 
   5 > **Official Reference**: [Get Insights from Agent Session Tracing Data](https://help.salesforce.com/s/articleView?id=ai.generative_ai_session_trace_use.htm)
   6 
   7 ## Basic Extraction Queries
   8 
   9 ### All Sessions (Last 7 Days)
  10 
  11 ```sql
  12 SELECT
  13     ssot__Id__c,
  14     ssot__AiAgentChannelType__c,
  15     ssot__StartTimestamp__c,
  16     ssot__EndTimestamp__c,
  17     ssot__AiAgentSessionEndType__c
  18 FROM ssot__AIAgentSession__dlm
  19 WHERE ssot__StartTimestamp__c >= '2026-01-21T00:00:00.000Z'
  20 ORDER BY ssot__StartTimestamp__c DESC;
  21 ```
  22 
  23 ### Sessions by Agent (via Moment Join)
  24 
  25 > **Note:** Agent name is stored on the Moment table, not Session. Use a JOIN to filter by agent.
  26 
  27 ```sql
  28 SELECT DISTINCT s.*
  29 FROM ssot__AIAgentSession__dlm s
  30 JOIN ssot__AiAgentMoment__dlm m
  31     ON m.ssot__AiAgentSessionId__c = s.ssot__Id__c
  32 WHERE m.ssot__AiAgentApiName__c = 'Customer_Support_Agent'
  33   AND s.ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
  34 ORDER BY s.ssot__StartTimestamp__c DESC;
  35 ```
  36 
  37 ### Failed/Escalated Sessions
  38 
  39 ```sql
  40 SELECT *
  41 FROM ssot__AIAgentSession__dlm
  42 WHERE ssot__AiAgentSessionEndType__c IN ('Escalated', 'Abandoned', 'Failed')
  43   AND ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
  44 ORDER BY ssot__StartTimestamp__c DESC;
  45 ```
  46 
  47 ---
  48 
  49 ## Aggregation Queries
  50 
  51 ### Session Count by Agent (via Moment)
  52 
  53 > **Note:** Agent name is on the Moment table. Query Moments and count distinct sessions.
  54 
  55 ```sql
  56 SELECT
  57     ssot__AiAgentApiName__c as agent,
  58     COUNT(DISTINCT ssot__AiAgentSessionId__c) as session_count
  59 FROM ssot__AiAgentMoment__dlm
  60 WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
  61 GROUP BY ssot__AiAgentApiName__c
  62 ORDER BY session_count DESC;
  63 ```
  64 
  65 ### End Type Distribution
  66 
  67 ```sql
  68 SELECT
  69     ssot__AiAgentSessionEndType__c as end_type,
  70     COUNT(*) as count
  71 FROM ssot__AIAgentSession__dlm
  72 WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
  73 GROUP BY ssot__AiAgentSessionEndType__c;
  74 ```
  75 
  76 ### Topic Usage
  77 
  78 ```sql
  79 SELECT
  80     ssot__TopicApiName__c as topic,
  81     COUNT(*) as turn_count
  82 FROM ssot__AIAgentInteraction__dlm
  83 WHERE ssot__AiAgentInteractionType__c = 'TURN'
  84 GROUP BY ssot__TopicApiName__c
  85 ORDER BY turn_count DESC;
  86 ```
  87 
  88 ### Action Invocation Frequency
  89 
  90 ```sql
  91 SELECT
  92     ssot__Name__c as action_name,
  93     COUNT(*) as invocation_count
  94 FROM ssot__AIAgentInteractionStep__dlm
  95 WHERE ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
  96 GROUP BY ssot__Name__c
  97 ORDER BY invocation_count DESC;
  98 ```
  99 
 100 ---
 101 
 102 ## Relationship Queries
 103 
 104 ### Session with Turn Count
 105 
 106 ```sql
 107 SELECT
 108     s.ssot__Id__c,
 109     s.ssot__AiAgentChannelType__c,
 110     COUNT(i.ssot__Id__c) as turn_count
 111 FROM ssot__AIAgentSession__dlm s
 112 LEFT JOIN ssot__AIAgentInteraction__dlm i
 113     ON i.ssot__AiAgentSessionId__c = s.ssot__Id__c
 114     AND i.ssot__AiAgentInteractionType__c = 'TURN'
 115 WHERE s.ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
 116 GROUP BY s.ssot__Id__c, s.ssot__AiAgentChannelType__c;
 117 ```
 118 
 119 ### Complete Session Tree
 120 
 121 ```sql
 122 -- Step 1: Get session
 123 SELECT * FROM ssot__AIAgentSession__dlm
 124 WHERE ssot__Id__c = 'a0x1234567890ABC';
 125 
 126 -- Step 2: Get interactions
 127 SELECT * FROM ssot__AIAgentInteraction__dlm
 128 WHERE ssot__AiAgentSessionId__c = 'a0x1234567890ABC';
 129 
 130 -- Step 3: Get steps (using interaction IDs from step 2)
 131 SELECT * FROM ssot__AIAgentInteractionStep__dlm
 132 WHERE ssot__AiAgentInteractionId__c IN ('a0y...', 'a0y...');
 133 
 134 -- Step 4: Get messages (using interaction IDs from step 2)
 135 SELECT * FROM ssot__AIAgentMoment__dlm
 136 WHERE ssot__AiAgentInteractionId__c IN ('a0y...', 'a0y...');
 137 ```
 138 
 139 ---
 140 
 141 ## Time-Based Queries
 142 
 143 ### Daily Session Counts
 144 
 145 ```sql
 146 SELECT
 147     SUBSTRING(ssot__StartTimestamp__c, 1, 10) as date,
 148     COUNT(*) as session_count
 149 FROM ssot__AIAgentSession__dlm
 150 WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
 151 GROUP BY SUBSTRING(ssot__StartTimestamp__c, 1, 10)
 152 ORDER BY date;
 153 ```
 154 
 155 ### Hourly Distribution
 156 
 157 ```sql
 158 SELECT
 159     SUBSTRING(ssot__StartTimestamp__c, 12, 2) as hour,
 160     COUNT(*) as session_count
 161 FROM ssot__AIAgentSession__dlm
 162 WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
 163 GROUP BY SUBSTRING(ssot__StartTimestamp__c, 12, 2)
 164 ORDER BY hour;
 165 ```
 166 
 167 ---
 168 
 169 ## Analysis Queries
 170 
 171 ### Sessions with Topic Switches
 172 
 173 ```sql
 174 SELECT
 175     ssot__AiAgentSessionId__c,
 176     COUNT(DISTINCT ssot__TopicApiName__c) as topic_count
 177 FROM ssot__AIAgentInteraction__dlm
 178 WHERE ssot__AiAgentInteractionType__c = 'TURN'
 179 GROUP BY ssot__AiAgentSessionId__c
 180 HAVING COUNT(DISTINCT ssot__TopicApiName__c) > 1;
 181 ```
 182 
 183 ### Long Sessions (Many Turns)
 184 
 185 ```sql
 186 SELECT
 187     ssot__AiAgentSessionId__c,
 188     COUNT(*) as turn_count
 189 FROM ssot__AIAgentInteraction__dlm
 190 WHERE ssot__AiAgentInteractionType__c = 'TURN'
 191 GROUP BY ssot__AiAgentSessionId__c
 192 HAVING COUNT(*) > 10
 193 ORDER BY turn_count DESC;
 194 ```
 195 
 196 ### Actions with High Failure Rate
 197 
 198 ```sql
 199 -- Note: This requires output parsing for error detection
 200 SELECT
 201     ssot__Name__c as action_name,
 202     COUNT(*) as total_invocations,
 203     COUNT(CASE WHEN ssot__OutputValueText__c LIKE '%error%' THEN 1 END) as errors
 204 FROM ssot__AIAgentInteractionStep__dlm
 205 WHERE ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
 206 GROUP BY ssot__Name__c;
 207 ```
 208 
 209 ---
 210 
 211 ## Performance Tips
 212 
 213 ### Use Date Filters Early
 214 
 215 ```sql
 216 -- Good: Filter by date first
 217 WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
 218   AND ssot__AiAgentSessionEndType__c = 'Completed'
 219 
 220 -- Avoid: No date filter on large tables
 221 WHERE ssot__AiAgentSessionEndType__c = 'Completed'
 222 ```
 223 
 224 ### Limit Result Sets
 225 
 226 ```sql
 227 -- Use LIMIT for exploration
 228 SELECT * FROM ssot__AIAgentSession__dlm
 229 WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
 230 ORDER BY ssot__StartTimestamp__c DESC
 231 LIMIT 100;
 232 ```
 233 
 234 ### Select Only Needed Columns
 235 
 236 ```sql
 237 -- Good: Select specific columns
 238 SELECT ssot__Id__c, ssot__AiAgentChannelType__c, ssot__StartTimestamp__c
 239 FROM ssot__AIAgentSession__dlm;
 240 
 241 -- Avoid: SELECT * on wide tables
 242 SELECT * FROM ssot__AIAgentInteractionStep__dlm;  -- Has large text fields
 243 ```
 244 
 245 ---
 246 
 247 ## Official Example Queries (from Salesforce Help)
 248 
 249 These are official query patterns from the Salesforce documentation.
 250 
 251 ### Full Session Join (All Entities)
 252 
 253 ```sql
 254 SELECT *
 255 FROM "AiAgentSession__dlm"
 256 JOIN "AiAgentSessionParticipant__dlm"
 257     ON "AiAgentSession__dlm"."id__c" = "AiAgentSessionParticipant__dlm"."aiAgentSessionId__c"
 258 JOIN "AiAgentInteraction__dlm"
 259     ON "AiAgentSession__dlm"."id__c" = "AiAgentInteraction__dlm"."aiAgentSessionId__c"
 260 JOIN "AiAgentInteractionMessage__dlm"
 261     ON "AiAgentInteraction__dlm"."id__c" = "AiAgentInteractionMessage__dlm"."aiAgentInteractionId__c"
 262 JOIN "AiAgentInteractionStep__dlm"
 263     ON "AiAgentInteraction__dlm"."id__c" = "AiAgentInteractionStep__dlm"."aiAgentInteractionId__c"
 264 WHERE "AiAgentSession__dlm"."id__c" = '{{SESSION_ID}}'
 265 LIMIT 10;
 266 ```
 267 
 268 ### Recent Sessions (Last N Days)
 269 
 270 ```sql
 271 SELECT
 272     ssot__Id__c,
 273     ssot__StartTimestamp__c
 274 FROM ssot__AiAgentSession__dlm s
 275 WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
 276 ORDER BY s.ssot__StartTimestamp__c DESC;
 277 ```
 278 
 279 ### All Messages in an Interaction
 280 
 281 ```sql
 282 SELECT
 283     ssot__AiAgentInteractionId__c AS InteractionId,
 284     ssot__AiAgentInteractionMessageType__c,     -- user or agent
 285     ssot__AiAgentInteractionMsgContentType__c,  -- e.g., text
 286     ssot__ContentText__c,
 287     ssot__AiAgentSessionParticipantId__c AS SenderParticipantId,
 288     ssot__ParentMessageId__c                    -- if part of a thread
 289 FROM "ssot__AiAgentInteractionMessage__dlm"
 290 WHERE ssot__AiAgentInteractionId__c = '{{INTERACTION_ID}}'
 291 ORDER BY ssot__MessageSentTimestamp__c ASC;
 292 ```
 293 
 294 ### Steps with Errors
 295 
 296 Find all interaction steps that encountered errors:
 297 
 298 ```sql
 299 SELECT
 300     ssot__AiAgentInteractionId__c AS InteractionId,
 301     ssot__Id__c AS StepId,
 302     ssot__Name__c AS StepName,
 303     ssot__InputValueText__c AS Input,
 304     ssot__ErrorMessageText__c AS StepErrorMessage
 305 FROM "ssot__AiAgentInteractionStep__dlm"
 306 WHERE length(ssot__ErrorMessageText__c) > 0
 307   AND ssot__ErrorMessageText__c != 'NOT_SET'
 308 LIMIT 100;
 309 ```
 310 
 311 ### Join with GenAI Feedback Data
 312 
 313 Combine session tracing with feedback and guardrails metrics:
 314 
 315 ```sql
 316 SELECT
 317     ssot__AiAgentInteractionId__c AS InteractionId,
 318     ssot__Name__c AS StepName,
 319     GenAIGatewayRequest__dlm.prompt__c AS Input_Prompt,
 320     GenAIGeneration__dlm.responseText__c AS LLM_Response,
 321     GenAIFeedback__dlm.feedback__c AS Feedback
 322 FROM ssot__AiAgentInteractionStep__dlm
 323 LEFT JOIN GenAIGeneration__dlm
 324     ON ssot__AiAgentInteractionStep__dlm.ssot__GenerationId__c = GenAIGeneration__dlm.generationId__c
 325 LEFT JOIN GenAIGatewayRequest__dlm
 326     ON ssot__AiAgentInteractionStep__dlm.ssot__GenAiGatewayRequestId__c = GenAIGatewayRequest__dlm.gatewayRequestId__c
 327 LEFT JOIN GenAIGatewayResponse__dlm
 328     ON GenAIGatewayRequest__dlm.gatewayRequestId__c = GenAIGatewayResponse__dlm.generationRequestId__c
 329 LEFT JOIN GenAIFeedback__dlm
 330     ON GenAIGeneration__dlm.generationId__c = GenAIFeedback__dlm.generationId__c
 331 WHERE GenAIGatewayResponse__dlm.generationResponseId__c = GenAIGeneration__dlm.generationResponseId__c
 332 LIMIT 100;
 333 ```
 334 
 335 ---
 336 
 337 ## Advanced Session Inspection
 338 
 339 ### Full Session Details (All Related Entities)
 340 
 341 Join all session tracing entities for complete visibility:
 342 
 343 ```sql
 344 SELECT *
 345 FROM ssot__AiAgentSession__dlm s
 346 JOIN ssot__AiAgentSessionParticipant__dlm sp
 347     ON s.ssot__id__c = sp.ssot__AiAgentSessionId__c
 348 JOIN ssot__AiAgentInteraction__dlm i
 349     ON s.ssot__id__c = i.ssot__AiAgentSessionId__c
 350 JOIN ssot__AiAgentInteractionMessage__dlm im
 351     ON i.ssot__id__c = im.ssot__AiAgentInteractionId__c
 352 JOIN ssot__AiAgentInteractionStep__dlm st
 353     ON i.ssot__id__c = st.ssot__AiAgentInteractionId__c
 354 WHERE s.ssot__id__c = '{{SESSION_ID}}'
 355 LIMIT 100;
 356 ```
 357 
 358 **Note:** This query includes `SessionParticipant` and `InteractionMessage` entities not in basic extraction.
 359 
 360 ### Session Insights with CTEs
 361 
 362 Use CTEs for complex session analysis with messages and steps:
 363 
 364 ```sql
 365 WITH
 366   -- Store session ID for reuse
 367   params AS (
 368     SELECT '{{SESSION_ID}}' AS session_id
 369   ),
 370 
 371   -- Get interactions with their messages
 372   interactionsWithMessages AS (
 373     SELECT
 374       i.ssot__Id__c AS InteractionId,
 375       i.ssot__TopicApiName__c AS TopicName,
 376       i.ssot__AiAgentInteractionType__c AS InteractionType,
 377       i.ssot__StartTimestamp__c AS InteractionStartTime,
 378       i.ssot__EndTimestamp__c AS InteractionEndTime,
 379       im.ssot__SentTime__c AS MessageSentTime,
 380       im.ssot__MessageType__c AS InteractionMessageType,
 381       im.ssot__ContextText__c AS ContextText,
 382       NULL AS InteractionStepType,
 383       NULL AS Name,
 384       NULL AS InputValueText,
 385       NULL AS OutputValueText,
 386       NULL AS PreStepVariableText,
 387       NULL AS PostStepVariableText
 388     FROM ssot__AiAgentInteraction__dlm i
 389     JOIN ssot__AiAgentInteractionMessage__dlm im
 390       ON i.ssot__Id__c = im.ssot__AiAgentInteractionId__c
 391     WHERE i.ssot__AiAgentSessionId__c = (SELECT session_id FROM params)
 392   ),
 393 
 394   -- Get interactions with their steps
 395   interactionsWithSteps AS (
 396     SELECT
 397       i.ssot__Id__c AS InteractionId,
 398       i.ssot__TopicApiName__c AS TopicName,
 399       i.ssot__AiAgentInteractionType__c AS InteractionType,
 400       i.ssot__StartTimestamp__c AS InteractionStartTime,
 401       i.ssot__EndTimestamp__c AS InteractionEndTime,
 402       st.ssot__StartTimestamp__c AS MessageSentTime,
 403       NULL AS InteractionMessageType,
 404       NULL AS ContextText,
 405       st.ssot__AiAgentInteractionStepType__c AS InteractionStepType,
 406       st.ssot__Name__c AS Name,
 407       st.ssot__InputValueText__c AS InputValueText,
 408       st.ssot__OutputValueText__c AS OutputValueText,
 409       st.ssot__PreStepVariableText__c AS PreStepVariableText,
 410       st.ssot__PostStepVariableText__c AS PostStepVariableText
 411     FROM ssot__AiAgentInteraction__dlm i
 412     JOIN ssot__AiAgentInteractionStep__dlm st
 413       ON i.ssot__Id__c = st.ssot__AiAgentInteractionId__c
 414     WHERE i.ssot__AiAgentSessionId__c = (SELECT session_id FROM params)
 415   ),
 416 
 417   -- Combine messages and steps
 418   combined AS (
 419     SELECT * FROM interactionsWithMessages
 420     UNION ALL
 421     SELECT * FROM interactionsWithSteps
 422   )
 423 
 424 -- Final output sorted chronologically
 425 SELECT
 426   TopicName,
 427   InteractionType,
 428   InteractionStartTime,
 429   InteractionEndTime,
 430   MessageSentTime,
 431   InteractionMessageType,
 432   ContextText,
 433   InteractionStepType,
 434   Name,
 435   InputValueText,
 436   OutputValueText,
 437   PreStepVariableText,
 438   PostStepVariableText
 439 FROM combined
 440 ORDER BY MessageSentTime ASC;
 441 ```
 442 
 443 **Tips for Finding Session IDs:**
 444 - For Service Agent: Use `ssot__RelatedMessagingSessionId__c` field on `ssot__AiAgentSession__dlm`
 445 - Use start/end timestamp fields to narrow down timeframes
 446 
 447 ---
 448 
 449 ## Quality Analysis Queries
 450 
 451 ### Toxic Response Detection
 452 
 453 Find generations flagged as toxic and trace back to sessions:
 454 
 455 ```sql
 456 SELECT
 457     i.ssot__AiAgentSessionId__c AS SessionId,
 458     i.ssot__TopicApiName__c AS TopicName,
 459     g.responseText__c AS ResponseText,
 460     c.category__c AS ToxicityCategory,
 461     c.value__c AS ConfidenceScore
 462 FROM GenAIContentQuality__dlm AS q
 463 JOIN GenAIContentCategory__dlm AS c
 464     ON c.parent__c = q.id__c
 465 JOIN GenAIGeneration__dlm AS g
 466     ON g.generationId__c = q.parent__c
 467 JOIN ssot__AiAgentInteractionStep__dlm st
 468     ON st.ssot__GenerationId__c = g.generationId__c
 469 JOIN ssot__AiAgentInteraction__dlm i
 470     ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 471 WHERE
 472     q.isToxicityDetected__c = 'true'
 473     AND TRY_CAST(c.value__c AS DECIMAL) >= 0.5
 474 LIMIT 100;
 475 ```
 476 
 477 **Join Chain:** ContentQuality → ContentCategory → Generation → Step → Interaction → Session
 478 
 479 ### Low Instruction Adherence Detection
 480 
 481 Find sessions where agent responses didn't follow instructions well:
 482 
 483 ```sql
 484 SELECT
 485     i.ssot__AiAgentSessionId__c AS SessionId,
 486     i.ssot__TopicApiName__c AS TopicName,
 487     g.responseText__c AS ResponseText,
 488     c.category__c AS AdherenceLevel,
 489     c.value__c AS ConfidenceScore
 490 FROM GenAIContentCategory__dlm AS c
 491 JOIN GenAIGeneration__dlm AS g
 492     ON g.generationId__c = c.parent__c
 493 JOIN ssot__AiAgentInteractionStep__dlm st
 494     ON st.ssot__GenerationId__c = g.generationId__c
 495 JOIN ssot__AiAgentInteraction__dlm i
 496     ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 497 WHERE
 498     c.detectorType__c = 'InstructionAdherence'
 499     AND c.category__c = 'Low'
 500 LIMIT 100;
 501 ```
 502 
 503 **Detector Types (Live API Verified - T6 Discovery):**
 504 
 505 | Detector Type | Occurrences | Categories/Values |
 506 |---------------|-------------|-------------------|
 507 | `TOXICITY` | 627,603 | `hate`, `identity`, `physical`, `profanity`, `safety_score`, `sexual`, `toxicity`, `violence` |
 508 | `PROMPT_DEFENSE` | 119,050 | `aggregatePromptAttackScore`, `isPromptAttackDetected` |
 509 | `PII` | 27,805 | `CREDIT_CARD`, `EMAIL_ADDRESS`, `PERSON`, `US_PHONE_NUMBER` |
 510 | `InstructionAdherence` | 16,380 | `High`, `Low`, `Uncertain` |
 511 
 512 **Detection Thresholds:**
 513 - **Toxicity**: `value__c >= 0.5` indicates toxic content
 514 - **PII**: Any category present indicates PII detection
 515 - **PROMPT_DEFENSE**: `isPromptAttackDetected` = `true` indicates attack
 516 - **InstructionAdherence**: `Low` category indicates poor adherence
 517 
 518 ### Unresolved Tasks Detection
 519 
 520 Find sessions where user requests weren't fully resolved:
 521 
 522 ```sql
 523 SELECT
 524     i.ssot__AiAgentSessionId__c AS SessionId,
 525     i.ssot__TopicApiName__c AS TopicName,
 526     g.responseText__c AS ResponseText,
 527     c.category__c AS ResolutionStatus,
 528     c.value__c AS ConfidenceScore
 529 FROM GenAIContentCategory__dlm AS c
 530 JOIN GenAIGeneration__dlm AS g
 531     ON g.generationId__c = c.parent__c
 532 JOIN ssot__AiAgentInteractionStep__dlm st
 533     ON st.ssot__GenerationId__c = g.generationId__c
 534 JOIN ssot__AiAgentInteraction__dlm i
 535     ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 536 WHERE
 537     c.detectorType__c = 'TaskResolution'
 538     AND c.category__c != 'FULLY_RESOLVED'
 539 LIMIT 100;
 540 ```
 541 
 542 ### PII Detection Analysis ✅ NEW
 543 
 544 Find sessions where PII was detected in user inputs or agent responses:
 545 
 546 ```sql
 547 SELECT
 548     c.category__c AS PiiType,
 549     COUNT(*) AS DetectionCount
 550 FROM GenAIContentCategory__dlm c
 551 WHERE c.detectorType__c = 'PII'
 552   AND c.timestamp__c >= current_date - INTERVAL '30' DAY
 553 GROUP BY c.category__c
 554 ORDER BY DetectionCount DESC;
 555 ```
 556 
 557 **PII Categories:**
 558 | Category | Description |
 559 |----------|-------------|
 560 | `CREDIT_CARD` | Credit card numbers |
 561 | `EMAIL_ADDRESS` | Email addresses |
 562 | `PERSON` | Person names |
 563 | `US_PHONE_NUMBER` | US phone numbers |
 564 
 565 ### Prompt Attack Detection ✅ NEW
 566 
 567 Find sessions with potential prompt injection attacks:
 568 
 569 ```sql
 570 SELECT
 571     i.ssot__AiAgentSessionId__c AS SessionId,
 572     i.ssot__TopicApiName__c AS TopicName,
 573     c.category__c AS AttackCategory,
 574     c.value__c AS Score
 575 FROM GenAIContentCategory__dlm c
 576 JOIN GenAIGeneration__dlm g
 577     ON g.generationId__c = c.parent__c
 578 JOIN ssot__AiAgentInteractionStep__dlm st
 579     ON st.ssot__GenerationId__c = g.generationId__c
 580 JOIN ssot__AiAgentInteraction__dlm i
 581     ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 582 WHERE c.detectorType__c = 'PROMPT_DEFENSE'
 583   AND c.category__c = 'isPromptAttackDetected'
 584   AND c.value__c = 'true'
 585 LIMIT 100;
 586 ```
 587 
 588 ### Hallucination Detection (UNGROUNDED Responses)
 589 
 590 Find responses flagged as ungrounded by the validation prompt:
 591 
 592 ```sql
 593 -- Note: Uses JSON parsing functions
 594 WITH llmResponses AS (
 595     SELECT
 596         i.ssot__AiAgentSessionId__c AS SessionId,
 597         ssot__InputValueText__c::JSON->'messages'->-1->>'content' AS LastMessage,
 598         ssot__OutputValueText__c::JSON->>'llmResponse' AS llmResponse,
 599         st.ssot__StartTimestamp__c AS InteractionStepStartTime
 600     FROM ssot__AiAgentInteractionStep__dlm st
 601     JOIN ssot__AiAgentInteraction__dlm i
 602         ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 603     WHERE
 604         st.ssot__AiAgentInteractionStepType__c = 'LLM_STEP'
 605         AND st.ssot__Name__c = 'AiCopilot__ReactValidationPrompt'
 606         AND st.ssot__OutputValueText__c LIKE '%UNGROUNDED%'
 607     LIMIT 100
 608 )
 609 SELECT
 610     InteractionStepStartTime,
 611     SessionId,
 612     TRIM('"' FROM SPLIT_PART(SPLIT_PART(LastMessage, '"response": "', 2), '"', 1)) AS AgentResponse,
 613     CAST(llmResponse AS JSON)->>'reason' AS UngroundedReason
 614 FROM llmResponses
 615 ORDER BY InteractionStepStartTime;
 616 ```
 617 
 618 **Key Step Names for Analysis:**
 619 
 620 | Step Name | Purpose |
 621 |-----------|---------|
 622 | `AiCopilot__ReactTopicPrompt` | Topic routing decision |
 623 | `AiCopilot__ReactInitialPrompt` | Initial planning/reasoning |
 624 | `AiCopilot__ReactValidationPrompt` | Response validation (hallucination check) |
 625 
 626 ---
 627 
 628 ## GenAI Gateway Analysis ✅ NEW
 629 
 630 Query patterns for analyzing LLM usage, token consumption, and model performance.
 631 
 632 ### Token Usage by Model
 633 
 634 Analyze token consumption across different models:
 635 
 636 ```sql
 637 SELECT
 638     model__c AS Model,
 639     COUNT(*) AS RequestCount,
 640     SUM(promptTokens__c) AS TotalPromptTokens,
 641     SUM(completionTokens__c) AS TotalCompletionTokens,
 642     SUM(totalTokens__c) AS TotalTokens,
 643     AVG(totalTokens__c) AS AvgTokensPerRequest
 644 FROM GenAIGatewayRequest__dlm
 645 WHERE timestamp__c >= current_date - INTERVAL '7' DAY
 646 GROUP BY model__c
 647 ORDER BY TotalTokens DESC;
 648 ```
 649 
 650 ### Prompt Template Usage
 651 
 652 Find which prompt templates are most frequently used:
 653 
 654 ```sql
 655 SELECT
 656     promptTemplateDevName__c AS TemplateName,
 657     promptTemplateVersionNo__c AS Version,
 658     COUNT(*) AS UsageCount,
 659     AVG(totalTokens__c) AS AvgTokens
 660 FROM GenAIGatewayRequest__dlm
 661 WHERE timestamp__c >= current_date - INTERVAL '30' DAY
 662   AND promptTemplateDevName__c IS NOT NULL
 663 GROUP BY promptTemplateDevName__c, promptTemplateVersionNo__c
 664 ORDER BY UsageCount DESC;
 665 ```
 666 
 667 ### Safety Configuration Analysis
 668 
 669 Analyze which safety features are enabled across requests:
 670 
 671 ```sql
 672 SELECT
 673     enableInputSafetyScoring__c AS InputSafety,
 674     enableOutputSafetyScoring__c AS OutputSafety,
 675     enablePiiMasking__c AS PiiMasking,
 676     COUNT(*) AS RequestCount
 677 FROM GenAIGatewayRequest__dlm
 678 WHERE timestamp__c >= current_date - INTERVAL '7' DAY
 679 GROUP BY enableInputSafetyScoring__c, enableOutputSafetyScoring__c, enablePiiMasking__c
 680 ORDER BY RequestCount DESC;
 681 ```
 682 
 683 ### User Feedback Summary
 684 
 685 Analyze user feedback distribution:
 686 
 687 ```sql
 688 SELECT
 689     feedback__c AS FeedbackType,
 690     COUNT(*) AS FeedbackCount
 691 FROM GenAIFeedback__dlm
 692 WHERE timestamp__c >= current_date - INTERVAL '30' DAY
 693 GROUP BY feedback__c
 694 ORDER BY FeedbackCount DESC;
 695 ```
 696 
 697 ### Feedback with Details
 698 
 699 Get detailed feedback with user comments:
 700 
 701 ```sql
 702 SELECT
 703     f.feedbackId__c,
 704     f.feedback__c AS FeedbackType,
 705     f.action__c AS UserAction,
 706     fd.feedbackText__c AS UserComment,
 707     f.timestamp__c
 708 FROM GenAIFeedback__dlm f
 709 LEFT JOIN GenAIFeedbackDetail__dlm fd
 710     ON fd.parent__c = f.feedbackId__c
 711 WHERE f.timestamp__c >= current_date - INTERVAL '7' DAY
 712 ORDER BY f.timestamp__c DESC
 713 LIMIT 100;
 714 ```
 715 
 716 ### High-Cost Requests
 717 
 718 Find requests with unusually high token consumption:
 719 
 720 ```sql
 721 SELECT
 722     gatewayRequestId__c,
 723     model__c AS Model,
 724     promptTokens__c,
 725     completionTokens__c,
 726     totalTokens__c,
 727     feature__c,
 728     timestamp__c
 729 FROM GenAIGatewayRequest__dlm
 730 WHERE totalTokens__c > 4000
 731   AND timestamp__c >= current_date - INTERVAL '7' DAY
 732 ORDER BY totalTokens__c DESC
 733 LIMIT 50;
 734 ```
 735 
 736 ---
 737 
 738 ## Knowledge Retrieval Analysis
 739 
 740 ### Vector Search for Knowledge Gaps
 741 
 742 Query the knowledge search index to understand what chunks were retrieved for a user query:
 743 
 744 ```sql
 745 SELECT
 746     v.Score__c AS Score,
 747     kav.Chat_Answer__c AS KnowledgeAnswer,
 748     c.Chunk__c AS ChunkText,
 749     c.SourceRecordId__c AS SourceRecordId,
 750     c.DataSource__c AS DataSource
 751 FROM vector_search(
 752     TABLE("External_Knowledge_Search_Index_index__dlm"),
 753     '{{USER_QUERY}}',
 754     '{{FILTER_CLAUSE}}',
 755     30
 756 ) v
 757 INNER JOIN "External_Knowledge_Search_Index_chunk__dlm" c
 758     ON c.RecordId__c = v.RecordId__c
 759 INNER JOIN "{{KNOWLEDGE_ARTICLE_DMO}}" kav
 760     ON c.SourceRecordId__c = kav.Id__c
 761 ORDER BY Score DESC
 762 LIMIT 10;
 763 ```
 764 
 765 **Parameters:**
 766 - `{{USER_QUERY}}`: The search query text
 767 - `{{FILTER_CLAUSE}}`: Optional filter like `'Country_Code__c=''US'''`
 768 - `{{KNOWLEDGE_ARTICLE_DMO}}`: Your org's Knowledge DMO name (e.g., `Knowledge_kav_Prod_00D58000000JmkM__dlm`)
 769 
 770 ### Improving Knowledge Articles Workflow
 771 
 772 1. **Identify low-quality moments**: Agentforce Studio → Observe → Optimization → Insights
 773 2. **Filter by topic and quality**: Topics includes `General_FAQ...`, Quality Score < Medium
 774 3. **Get Session ID** from Moments view
 775 4. **Query STDM** with session ID to inspect ACTION_STEP
 776 5. **Examine actionName and actionInput** in step output
 777 6. **Run vector_search** with the user query to see retrieved chunks
 778 7. **Identify SourceRecordId** to find knowledge articles needing improvement
 779 
 780 ### Inspecting Action Steps for Knowledge Calls
 781 
 782 Find ACTION_STEP details for a session:
 783 
 784 ```sql
 785 SELECT
 786     st.ssot__Name__c AS ActionName,
 787     st.ssot__AiAgentInteractionStepType__c AS StepType,
 788     st.ssot__InputValueText__c AS InputValue,
 789     st.ssot__OutputValueText__c AS OutputValue,
 790     st.ssot__StartTimestamp__c AS StartTime
 791 FROM ssot__AiAgentInteractionStep__dlm st
 792 JOIN ssot__AiAgentInteraction__dlm i
 793     ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 794 WHERE
 795     i.ssot__AiAgentSessionId__c = '{{SESSION_ID}}'
 796     AND st.ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
 797 ORDER BY st.ssot__StartTimestamp__c;
 798 ```
 799 
 800 **ACTION_STEP Output Contains:**
 801 - `actionName`: The invoked action (e.g., `General_FAQ0_16jWi00000001...`)
 802 - `actionInput`: Parameters passed to the action
 803 - Retrieved knowledge chunks in the response
 804 
 805 ---
 806 
 807 ## Advanced CTE Patterns
 808 
 809 Complex CTE (Common Table Expression) patterns for advanced session analysis.
 810 
 811 ### CTE Pattern 1: Session Summary with Stats
 812 
 813 Aggregate turn counts and step counts per session:
 814 
 815 ```sql
 816 WITH session_stats AS (
 817     SELECT
 818         s.ssot__Id__c,
 819         s.ssot__AiAgentChannelType__c as channel_type,
 820         s.ssot__AiAgentSessionEndType__c as end_type,
 821         COUNT(DISTINCT i.ssot__Id__c) as turn_count,
 822         COUNT(DISTINCT st.ssot__Id__c) as step_count
 823     FROM ssot__AIAgentSession__dlm s
 824     LEFT JOIN ssot__AIAgentInteraction__dlm i
 825         ON i.ssot__AiAgentSessionId__c = s.ssot__Id__c
 826     LEFT JOIN ssot__AIAgentInteractionStep__dlm st
 827         ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 828     WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
 829     GROUP BY s.ssot__Id__c, s.ssot__AiAgentChannelType__c, s.ssot__AiAgentSessionEndType__c
 830 )
 831 SELECT * FROM session_stats WHERE turn_count > 5
 832 ORDER BY step_count DESC;
 833 ```
 834 
 835 ### CTE Pattern 2: Error Analysis by Topic
 836 
 837 Find which topics have the most action errors:
 838 
 839 ```sql
 840 WITH topic_errors AS (
 841     SELECT
 842         i.ssot__TopicApiName__c as topic,
 843         st.ssot__Name__c as action_name,
 844         st.ssot__ErrorMessageText__c as error
 845     FROM ssot__AIAgentInteractionStep__dlm st
 846     JOIN ssot__AIAgentInteraction__dlm i
 847         ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 848     WHERE length(st.ssot__ErrorMessageText__c) > 0
 849       AND st.ssot__ErrorMessageText__c != 'NOT_SET'
 850       AND st.ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
 851 )
 852 SELECT topic, action_name, COUNT(*) as error_count
 853 FROM topic_errors
 854 GROUP BY topic, action_name
 855 ORDER BY error_count DESC;
 856 ```
 857 
 858 ### CTE Pattern 3: Session Timeline Reconstruction
 859 
 860 Reconstruct the full timeline of events (messages + steps) for a session:
 861 
 862 ```sql
 863 WITH
 864   params AS (
 865     SELECT '{{SESSION_ID}}' AS session_id
 866   ),
 867   session_events AS (
 868     -- Messages
 869     SELECT
 870         'MESSAGE' as event_type,
 871         im.ssot__MessageSentTimestamp__c as timestamp,
 872         im.ssot__AiAgentInteractionMessageType__c as detail,
 873         i.ssot__AiAgentSessionId__c as session_id
 874     FROM ssot__AiAgentInteractionMessage__dlm im
 875     JOIN ssot__AiAgentInteraction__dlm i
 876         ON im.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 877     WHERE i.ssot__AiAgentSessionId__c = (SELECT session_id FROM params)
 878 
 879     UNION ALL
 880 
 881     -- Steps
 882     SELECT
 883         st.ssot__AiAgentInteractionStepType__c as event_type,
 884         st.ssot__StartTimestamp__c as timestamp,
 885         st.ssot__Name__c as detail,
 886         i.ssot__AiAgentSessionId__c as session_id
 887     FROM ssot__AIAgentInteractionStep__dlm st
 888     JOIN ssot__AiAgentInteraction__dlm i
 889         ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
 890     WHERE i.ssot__AiAgentSessionId__c = (SELECT session_id FROM params)
 891   )
 892 SELECT event_type, timestamp, detail
 893 FROM session_events
 894 ORDER BY timestamp ASC;
 895 ```
 896 
 897 ### CTE Pattern 4: Quality Metrics Dashboard
 898 
 899 Aggregate quality metrics by detector type:
 900 
 901 ```sql
 902 WITH quality_summary AS (
 903     SELECT
 904         c.detectorType__c,
 905         c.category__c,
 906         COUNT(*) as count,
 907         AVG(TRY_CAST(c.value__c AS DECIMAL)) as avg_score
 908     FROM GenAIContentCategory__dlm c
 909     GROUP BY c.detectorType__c, c.category__c
 910 )
 911 SELECT
 912     detectorType__c as detector,
 913     category__c as category,
 914     count,
 915     ROUND(avg_score, 3) as avg_confidence
 916 FROM quality_summary
 917 ORDER BY detector, count DESC;
 918 ```
 919 
 920 **Note:** This query requires GenAI Trust Layer DMOs to be enabled.
 921 
 922 ### CTE Pattern 5: Topic Routing Analysis
 923 
 924 Analyze how users are routed between topics within sessions:
 925 
 926 ```sql
 927 WITH topic_transitions AS (
 928     SELECT
 929         curr.ssot__AiAgentSessionId__c as session_id,
 930         prev.ssot__TopicApiName__c as from_topic,
 931         curr.ssot__TopicApiName__c as to_topic,
 932         curr.ssot__StartTimestamp__c as transition_time
 933     FROM ssot__AIAgentInteraction__dlm curr
 934     JOIN ssot__AIAgentInteraction__dlm prev
 935         ON curr.ssot__PrevInteractionId__c = prev.ssot__Id__c
 936     WHERE curr.ssot__TopicApiName__c != prev.ssot__TopicApiName__c
 937       AND curr.ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
 938 )
 939 SELECT
 940     from_topic,
 941     to_topic,
 942     COUNT(*) as transition_count
 943 FROM topic_transitions
 944 GROUP BY from_topic, to_topic
 945 ORDER BY transition_count DESC;
 946 ```
 947 
 948 **Use Cases:**
 949 - Identify common topic escalation paths
 950 - Find topics that frequently need fallback routing
 951 - Understand user journey patterns
 952 
 953 ---
 954 
 955 ## Tag System Queries ✅ NEW
 956 
 957 Query the Agentforce tagging system for session categorization and analytics.
 958 
 959 ### Get Tag Definitions
 960 
 961 List all available tag definitions in the org:
 962 
 963 ```sql
 964 SELECT
 965     ssot__Id__c,
 966     ssot__Name__c,
 967     ssot__DeveloperName__c,
 968     ssot__Description__c,
 969     ssot__DataType__c,
 970     ssot__SourceType__c
 971 FROM ssot__AiAgentTagDefinition__dlm
 972 ORDER BY ssot__CreatedDate__c DESC
 973 LIMIT 50;
 974 ```
 975 
 976 ### Get Tag Values for a Definition
 977 
 978 List all values for a specific tag definition:
 979 
 980 ```sql
 981 SELECT
 982     t.ssot__Id__c,
 983     t.ssot__Description__c,
 984     t.ssot__IsActive__c,
 985     td.ssot__Name__c as TagDefinitionName
 986 FROM ssot__AiAgentTag__dlm t
 987 JOIN ssot__AiAgentTagDefinition__dlm td
 988     ON t.ssot__AiAgentTagDefinitionId__c = td.ssot__Id__c
 989 WHERE td.ssot__DeveloperName__c = 'Escalation_Reason'
 990   AND t.ssot__IsActive__c = true
 991 ORDER BY t.ssot__CreatedDate__c DESC;
 992 ```
 993 
 994 ### Sessions with Tag Associations
 995 
 996 Find sessions that have been tagged:
 997 
 998 ```sql
 999 SELECT
1000     s.ssot__Id__c AS SessionId,
1001     s.ssot__StartTimestamp__c,
1002     ta.ssot__AiAgentTagDefinitionAssociationId__c AS TagAssociation,
1003     ta.ssot__CreatedDate__c AS TaggedAt
1004 FROM ssot__AIAgentSession__dlm s
1005 JOIN ssot__AiAgentTagAssociation__dlm ta
1006     ON s.ssot__Id__c = ta.ssot__AiAgentSessionId__c
1007 WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
1008 ORDER BY s.ssot__StartTimestamp__c DESC
1009 LIMIT 100;
1010 ```
1011 
1012 ### Tag Distribution Analysis
1013 
1014 Count sessions by tag:
1015 
1016 ```sql
1017 SELECT
1018     td.ssot__Name__c AS TagName,
1019     COUNT(DISTINCT ta.ssot__AiAgentSessionId__c) AS SessionCount
1020 FROM ssot__AiAgentTagAssociation__dlm ta
1021 JOIN ssot__AiAgentTagDefinitionAssociation__dlm tda
1022     ON ta.ssot__AiAgentTagDefinitionAssociationId__c = tda.ssot__Id__c
1023 JOIN ssot__AiAgentTagDefinition__dlm td
1024     ON tda.ssot__AiAgentTagDefinitionId__c = td.ssot__Id__c
1025 WHERE ta.ssot__CreatedDate__c >= current_date - INTERVAL '30' DAY
1026 GROUP BY td.ssot__Name__c
1027 ORDER BY SessionCount DESC;
1028 ```
1029 
1030 ### Tags by Agent
1031 
1032 Find which tags are configured for each agent:
1033 
1034 ```sql
1035 SELECT
1036     tda.ssot__AiAgentApiName__c AS AgentName,
1037     td.ssot__Name__c AS TagName,
1038     td.ssot__DataType__c AS DataType,
1039     td.ssot__SourceType__c AS SourceType
1040 FROM ssot__AiAgentTagDefinitionAssociation__dlm tda
1041 JOIN ssot__AiAgentTagDefinition__dlm td
1042     ON tda.ssot__AiAgentTagDefinitionId__c = td.ssot__Id__c
1043 ORDER BY tda.ssot__AiAgentApiName__c, td.ssot__Name__c;
1044 ```
1045 
1046 ### Tag Values with Ratings
1047 
1048 Get tag values (useful for rating-based tags):
1049 
1050 ```sql
1051 SELECT
1052     td.ssot__Name__c AS TagName,
1053     t.ssot__Value__c AS Value,
1054     t.ssot__Description__c AS Description,
1055     t.ssot__IsActive__c AS IsActive
1056 FROM ssot__AiAgentTag__dlm t
1057 JOIN ssot__AiAgentTagDefinition__dlm td
1058     ON t.ssot__AiAgentTagDefinitionId__c = td.ssot__Id__c
1059 WHERE t.ssot__IsActive__c = true
1060 ORDER BY td.ssot__Name__c, t.ssot__Value__c;
1061 ```
1062 
1063 ---
1064 
1065 ## Step Analysis Patterns ✅ NEW
1066 
1067 Query patterns for analyzing step execution, LLM calls, and action performance.
1068 
1069 ### LLM Step Analysis by Prompt Type
1070 
1071 Analyze LLM steps by the prompt type:
1072 
1073 ```sql
1074 SELECT
1075     ssot__Name__c AS PromptName,
1076     COUNT(*) AS Invocations,
1077     AVG(EXTRACT(EPOCH FROM (ssot__EndTimestamp__c - ssot__StartTimestamp__c))) AS AvgDurationSeconds
1078 FROM ssot__AIAgentInteractionStep__dlm
1079 WHERE ssot__AiAgentInteractionStepType__c = 'LLM_STEP'
1080   AND ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
1081   AND ssot__Name__c LIKE 'AiCopilot%'
1082 GROUP BY ssot__Name__c
1083 ORDER BY Invocations DESC;
1084 ```
1085 
1086 ### Common LLM Prompts
1087 
1088 | Prompt Name | Purpose |
1089 |-------------|---------|
1090 | `AiCopilot__ReactInitialPrompt` | Initial planning/reasoning |
1091 | `AiCopilot__ReactTopicPrompt` | Topic classification/routing |
1092 | `AiCopilot__ReactValidationPrompt` | Response validation (hallucination check) |
1093 
1094 ### Top Actions by Invocation
1095 
1096 Find the most frequently called actions:
1097 
1098 ```sql
1099 SELECT
1100     ssot__Name__c AS ActionName,
1101     COUNT(*) AS InvocationCount,
1102     COUNT(CASE WHEN length(ssot__ErrorMessageText__c) > 0
1103                AND ssot__ErrorMessageText__c != 'NOT_SET' THEN 1 END) AS ErrorCount
1104 FROM ssot__AIAgentInteractionStep__dlm
1105 WHERE ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
1106   AND ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
1107 GROUP BY ssot__Name__c
1108 ORDER BY InvocationCount DESC
1109 LIMIT 20;
1110 ```
1111 
1112 ### Step Chain Analysis (Following PrevStepId)
1113 
1114 Trace the step execution chain within an interaction:
1115 
1116 ```sql
1117 WITH RECURSIVE step_chain AS (
1118     -- Base: find the first step (no PrevStepId)
1119     SELECT
1120         ssot__Id__c,
1121         ssot__Name__c,
1122         ssot__AiAgentInteractionStepType__c,
1123         ssot__PrevStepId__c,
1124         1 as depth
1125     FROM ssot__AIAgentInteractionStep__dlm
1126     WHERE ssot__AiAgentInteractionId__c = '{{INTERACTION_ID}}'
1127       AND ssot__PrevStepId__c IS NULL
1128 
1129     UNION ALL
1130 
1131     -- Recursive: follow PrevStepId chain
1132     SELECT
1133         s.ssot__Id__c,
1134         s.ssot__Name__c,
1135         s.ssot__AiAgentInteractionStepType__c,
1136         s.ssot__PrevStepId__c,
1137         sc.depth + 1
1138     FROM ssot__AIAgentInteractionStep__dlm s
1139     JOIN step_chain sc ON s.ssot__PrevStepId__c = sc.ssot__Id__c
1140     WHERE sc.depth < 20
1141 )
1142 SELECT depth, ssot__AiAgentInteractionStepType__c, ssot__Name__c
1143 FROM step_chain
1144 ORDER BY depth;
1145 ```
1146 
1147 **Note:** Steps use linear `PrevStepId` sequencing. There is no hierarchical parent-child relationship.
1148 
1149 ---
1150 
1151 ## Moment-Interaction Junction Queries ✅ NEW
1152 
1153 Query the junction table linking Moments to Interactions for many-to-many analysis.
1154 
1155 ### Moments with Their Interactions
1156 
1157 Get all interactions associated with a moment:
1158 
1159 ```sql
1160 SELECT
1161     m.ssot__Id__c AS MomentId,
1162     m.ssot__RequestSummaryText__c,
1163     mi.ssot__AiAgentInteractionId__c AS InteractionId,
1164     i.ssot__TopicApiName__c AS Topic
1165 FROM ssot__AiAgentMoment__dlm m
1166 JOIN ssot__AiAgentMomentInteraction__dlm mi
1167     ON m.ssot__Id__c = mi.ssot__AiAgentMomentId__c
1168 JOIN ssot__AIAgentInteraction__dlm i
1169     ON mi.ssot__AiAgentInteractionId__c = i.ssot__Id__c
1170 WHERE m.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
1171 LIMIT 50;
1172 ```
1173 
1174 ### Interactions per Moment (Aggregated)
1175 
1176 Count interactions associated with each moment:
1177 
1178 ```sql
1179 SELECT
1180     mi.ssot__AiAgentMomentId__c AS MomentId,
1181     COUNT(*) AS InteractionCount
1182 FROM ssot__AiAgentMomentInteraction__dlm mi
1183 GROUP BY mi.ssot__AiAgentMomentId__c
1184 HAVING COUNT(*) > 1
1185 ORDER BY InteractionCount DESC
1186 LIMIT 20;
1187 ```
1188 
1189 ### Full Session Tree with Moments
1190 
1191 Get complete session data including the Moment-Interaction relationship:
1192 
1193 ```sql
1194 SELECT
1195     s.ssot__Id__c AS SessionId,
1196     m.ssot__AiAgentApiName__c AS AgentName,
1197     m.ssot__RequestSummaryText__c AS RequestSummary,
1198     m.ssot__ResponseSummaryText__c AS ResponseSummary,
1199     i.ssot__Id__c AS InteractionId,
1200     i.ssot__TopicApiName__c AS Topic
1201 FROM ssot__AIAgentSession__dlm s
1202 JOIN ssot__AiAgentMoment__dlm m
1203     ON s.ssot__Id__c = m.ssot__AiAgentSessionId__c
1204 LEFT JOIN ssot__AiAgentMomentInteraction__dlm mi
1205     ON m.ssot__Id__c = mi.ssot__AiAgentMomentId__c
1206 LEFT JOIN ssot__AIAgentInteraction__dlm i
1207     ON mi.ssot__AiAgentInteractionId__c = i.ssot__Id__c
1208 WHERE s.ssot__Id__c = '{{SESSION_ID}}'
1209 ORDER BY m.ssot__StartTimestamp__c, i.ssot__StartTimestamp__c;
1210 ```
1211 
1212 ---
1213 
1214 ## Entity Relationship Reference
1215 
1216 ### Session Tracing Data Model (STDM)
1217 
1218 ```
1219 Session (ssot__AiAgentSession__dlm)
1220 ├── SessionParticipant (ssot__AIAgentSessionParticipant__dlm)  [1:N]
1221 ├── Interaction (ssot__AiAgentInteraction__dlm)                [1:N]
1222 │   ├── InteractionMessage (ssot__AiAgentInteractionMessage__dlm)  [1:N]
1223 │   └── InteractionStep (ssot__AiAgentInteractionStep__dlm)        [1:N]
1224 │       └── → links to GenAIGeneration via GenerationId
1225 ├── Moment (ssot__AiAgentMoment__dlm)                          [1:N]
1226 │   └── MomentInteraction (ssot__AiAgentMomentInteraction__dlm)    [N:M junction]
1227 │       └── → links Moment ↔ Interaction
1228 └── TagAssociation (ssot__AiAgentTagAssociation__dlm)          [1:N] ✅ NEW
1229     └── → links to TagDefinition & Tag
1230 ```
1231 
1232 ### Tagging Data Model ✅ NEW
1233 
1234 ```
1235 TagDefinition (ssot__AiAgentTagDefinition__dlm)
1236 └── Tag (ssot__AiAgentTag__dlm)                    [1:N]
1237     └── TagAssociation                              [N:M]
1238         ├── → Session (AiAgentSessionId)
1239         └── → Moment (AiAgentMomentId)
1240 ```
1241 
1242 ### Quality Data Model (GenAI Trust Layer) ✅ T6 Verified
1243 
1244 ```
1245 GenAIGeneration__dlm
1246 ├── GenAIContentQuality__dlm          [1:1]
1247 │   └── GenAIContentCategory__dlm     [1:N]
1248 │       ├── detectorType__c: 'TOXICITY' | 'PII' | 'PROMPT_DEFENSE' | 'InstructionAdherence'
1249 │       ├── category__c: Result category (see tables below)
1250 │       └── value__c: Confidence score (0.0-1.0, string format)
1251 └── GenAIFeedback__dlm                [1:N]
1252     └── GenAIFeedbackDetail__dlm      [1:N]
1253 ```
1254 
1255 **Detector Categories (Live API Verified):**
1256 
1257 | Detector | Categories |
1258 |----------|------------|
1259 | `TOXICITY` | `hate`, `identity`, `physical`, `profanity`, `safety_score`, `sexual`, `toxicity`, `violence` |
1260 | `PII` | `CREDIT_CARD`, `EMAIL_ADDRESS`, `PERSON`, `US_PHONE_NUMBER` |
1261 | `PROMPT_DEFENSE` | `aggregatePromptAttackScore`, `isPromptAttackDetected` |
1262 | `InstructionAdherence` | `High`, `Low`, `Uncertain` |
1263 
1264 ### Gateway Data Model (GenAI Request/Response) ✅ T6 Verified
1265 
1266 ```
1267 GenAIGatewayRequest__dlm (30 fields)
1268 ├── GenAIGatewayResponse__dlm         [1:1]
1269 ├── GenAIGatewayRequestTag__dlm       [1:N]
1270 ├── GenAIGtwyRequestMetadata__dlm     [1:N]
1271 ├── GenAIGtwyObjRecord__dlm           [1:N]
1272 │   └── GenAIGtwyObjRecCitationRef__dlm  [1:N]
1273 └── GenAIGeneration__dlm              [1:N] (via generationGroupId)
1274 ```
1275 
1276 **Key Join Fields:**
1277 - `ssot__GenerationId__c` on Steps → `generationId__c` on Generation
1278 - `ssot__GenAiGatewayRequestId__c` on Steps → `gatewayRequestId__c` on GatewayRequest
1279 - `parent__c` on ContentQuality → `generationId__c` on Generation
1280 - `parent__c` on ContentCategory → `id__c` on ContentQuality
1281 - `parent__c` on FeedbackDetail → `feedbackId__c` on Feedback
1282 
1283 ---
1284 
1285 ## Template Variables
1286 
1287 The query templates use these placeholders:
1288 
1289 | Variable | Description | Example |
1290 |----------|-------------|---------|
1291 | `{{START_DATE}}` | Start timestamp | `2026-01-01T00:00:00.000Z` |
1292 | `{{END_DATE}}` | End timestamp | `2026-01-28T23:59:59.000Z` |
1293 | `{{AGENT_NAMES}}` | Comma-separated agent names | `'Agent1', 'Agent2'` |
1294 | `{{SESSION_IDS}}` | Comma-separated session IDs | `'a0x...', 'a0x...'` |
1295 | `{{SESSION_ID}}` | Single session ID | `'01999669-0a54-724f-80d6-9cb495a7cee4'` |
1296 | `{{INTERACTION_IDS}}` | Comma-separated interaction IDs | `'a0y...', 'a0y...'` |
