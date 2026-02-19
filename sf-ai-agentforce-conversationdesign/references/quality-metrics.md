<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Quality Metrics for Agentforce Conversation Design
   2 
   3 This guide defines key performance indicators (KPIs), benchmarks, and improvement strategies for evaluating Agentforce agent quality. Use these metrics to measure success and identify areas for optimization.
   4 
   5 ---
   6 
   7 ## Core Metrics Framework
   8 
   9 Agentforce quality should be measured across four dimensions:
  10 
  11 1. **Resolution** — Did the agent solve the customer's problem?
  12 2. **Accuracy** — Did the agent route correctly and provide correct information?
  13 3. **Efficiency** — Did the agent resolve the issue quickly?
  14 4. **Satisfaction** — Is the customer happy with the experience?
  15 
  16 ---
  17 
  18 ## Metric 1: Resolution Rate
  19 
  20 **Definition:** Percentage of conversations resolved without escalation to a human agent.
  21 
  22 **Formula:**
  23 ```
  24 Resolution Rate = (Conversations Resolved by AI / Total Conversations) × 100
  25 ```
  26 
  27 **Target Benchmark:** >70%
  28 
  29 **Grade Scale:**
  30 - **Excellent:** >80%
  31 - **Good:** 70-80%
  32 - **Fair:** 60-70%
  33 - **Poor:** <60%
  34 
  35 ### How to Measure
  36 
  37 **Method 1: Escalation Tracking (Proxy)**
  38 ```
  39 Resolution Rate ≈ 100% - Escalation Rate
  40 ```
  41 
  42 If 25% of conversations escalate, resolution rate ≈ 75%.
  43 
  44 **Method 2: Post-Conversation Survey**
  45 ```
  46 Survey Question: "Was your issue resolved?"
  47   - Yes (resolved)
  48   - Partially (some help, but not fully resolved)
  49   - No (not resolved)
  50 
  51 Resolution Rate = % who answered "Yes"
  52 ```
  53 
  54 **Method 3: AgentWork Analysis**
  55 ```
  56 Query AgentWork records:
  57   - Total conversations: COUNT(*)
  58   - Escalations: COUNT(*) WHERE WorkItemType = 'Escalation'
  59   - Resolution Rate = 100% - (Escalations / Total)
  60 ```
  61 
  62 ### Interpretation
  63 
  64 | Resolution Rate | What It Means | Action |
  65 |-----------------|---------------|--------|
  66 | **>85%** | AI is highly effective | Maintain current design, look for edge case improvements |
  67 | **70-85%** | AI is performing well | Identify top escalation reasons and address |
  68 | **60-70%** | AI is struggling | Major redesign needed—check topic scope, instructions, actions |
  69 | **<60%** | AI is not adding value | Consider if the use case is suitable for AI |
  70 
  71 ### Improvement Strategies
  72 
  73 **If Resolution Rate is Low:**
  74 
  75 1. **Analyze Escalation Reasons:**
  76    ```
  77    Top Escalation Reasons:
  78      - 35%: Complexity (multi-issue conversations)
  79      - 25%: Customer request for human
  80      - 20%: Repeated failures (same action fails 2+ times)
  81      - 10%: Frustration
  82      - 10%: Policy exceptions
  83    ```
  84 
  85    **Action:** Focus on the top 1-2 reasons. If "Complexity" is #1, add actions or split topics.
  86 
  87 2. **Add Missing Actions:**
  88    - If customers escalate because "I can't find X", add a Search Knowledge action for X
  89    - If customers escalate for "Change Y", add an Update Y action
  90 
  91 3. **Improve Instructions:**
  92    - Review conversations where agent gave incorrect info → update instructions
  93    - Review conversations where agent asked redundant questions → improve context handling
  94 
  95 4. **Expand Topic Coverage:**
  96    - If 20% of escalations are "Out of Scope", consider adding a topic for that domain
  97 
  98 ---
  99 
 100 ## Metric 2: Topic Classification Accuracy
 101 
 102 **Definition:** Percentage of conversations correctly routed to the right topic on first intent.
 103 
 104 **Formula:**
 105 ```
 106 Classification Accuracy = (Correct Topic Matches / Total Conversations) × 100
 107 ```
 108 
 109 **Target Benchmark:** >90%
 110 
 111 **Grade Scale:**
 112 - **Excellent:** >95%
 113 - **Good:** 90-95%
 114 - **Fair:** 85-90%
 115 - **Poor:** <85%
 116 
 117 ### How to Measure
 118 
 119 **Method 1: Manual Review (Gold Standard)**
 120 
 121 Sample 100 conversations. For each, answer:
 122 - Did the agent route to the correct topic on the first message?
 123 - If topic switched mid-conversation, was it appropriate?
 124 
 125 ```
 126 Example:
 127   User: "I want to return my order"
 128   Agent: [Routes to "Returns & Refunds" topic] ✅ Correct
 129 
 130   User: "I forgot my password"
 131   Agent: [Routes to "Product Help" topic] ❌ Incorrect (should be "Account Settings")
 132 ```
 133 
 134 **Method 2: Topic Switch Rate (Proxy)**
 135 
 136 If the agent frequently switches topics mid-conversation, it suggests initial classification was wrong.
 137 
 138 ```
 139 Topic Switch Rate = (Conversations with Topic Switch / Total) × 100
 140 
 141 Target: <10% (most conversations should stay in one topic)
 142 ```
 143 
 144 **Method 3: Fallback Topic Rate**
 145 
 146 If >15% of conversations land in the Fallback/Out-of-Scope topic, classification is failing.
 147 
 148 ```
 149 Fallback Rate = (Fallback Topic Conversations / Total) × 100
 150 
 151 Target: <15%
 152 ```
 153 
 154 ### Interpretation
 155 
 156 | Classification Accuracy | What It Means | Action |
 157 |-------------------------|---------------|--------|
 158 | **>95%** | Topic descriptions are clear and well-differentiated | Maintain current design |
 159 | **90-95%** | Generally good, minor ambiguities | Review top misclassification pairs |
 160 | **85-90%** | Significant ambiguity | Rewrite overlapping topic descriptions |
 161 | **<85%** | Topics are poorly defined | Major topic architecture redesign |
 162 
 163 ### Improvement Strategies
 164 
 165 **If Classification Accuracy is Low:**
 166 
 167 1. **Identify Ambiguous Topic Pairs:**
 168    ```
 169    Misclassification Analysis:
 170      - 40% of "Technical Support" conversations misclassified as "Product Help"
 171      - 30% of "Account Settings" misclassified as "Order Management"
 172    ```
 173 
 174    **Action:** Disambiguate the overlapping topics:
 175    ```yaml
 176    # Before (Ambiguous)
 177    Topic A: Technical Support
 178    Description: Customer has problems with the product or needs help.
 179 
 180    Topic B: Product Help
 181    Description: Customer needs help with the product or has questions.
 182 
 183    # After (Clear)
 184    Topic A: Technical Support
 185    Description: Customer reports an error, crash, bug, or unexpected behavior—
 186                 something that should work but doesn't. Keywords: "error",
 187                 "crash", "broken", "not working", "stopped working".
 188 
 189    Topic B: Product Help
 190    Description: Customer asks how to use a feature, configure settings, or
 191                 accomplish a task. Keywords: "how do I", "where is", "show me".
 192    ```
 193 
 194 2. **Add Keyword Indicators:**
 195    - Include explicit keywords in classification descriptions
 196    - Example: "Includes phrases like 'I want to return', 'start a return', 'return policy'"
 197 
 198 3. **Test with Real User Queries:**
 199    - Use historical conversation data to test topic classification
 200    - For each query, predict which topic should match, then validate
 201 
 202 4. **Split Overly Broad Topics:**
 203    - If one topic handles 50%+ of conversations, it's too broad
 204    - Example: Split "Customer Service" into "Order Support", "Returns", "Account Settings"
 205 
 206 ---
 207 
 208 ## Metric 3: Average Turns to Resolution
 209 
 210 **Definition:** Average number of back-and-forth messages (turns) from start to resolution.
 211 
 212 **Formula:**
 213 ```
 214 Avg Turns to Resolution = Total Message Count / Total Resolved Conversations
 215 ```
 216 
 217 **Target Benchmark:** <6 turns
 218 
 219 **Grade Scale:**
 220 - **Excellent:** <4 turns (efficient, concise)
 221 - **Good:** 4-6 turns (acceptable for most use cases)
 222 - **Fair:** 6-8 turns (slow, needs optimization)
 223 - **Poor:** >8 turns (inefficient, frustrating)
 224 
 225 ### How to Measure
 226 
 227 **Method 1: Conversation Message Count**
 228 
 229 Query conversation records:
 230 ```sql
 231 SELECT AVG(MessageCount)
 232 FROM Conversation
 233 WHERE Status = 'Resolved'
 234 AND EscalatedToHuman__c = FALSE
 235 ```
 236 
 237 **Method 2: By Topic**
 238 
 239 Compare turn counts across topics to identify inefficiencies:
 240 ```
 241 Topic                  | Avg Turns | Status
 242 -------------------------------------------------
 243 Order Status           | 2.3       | ✅ Excellent
 244 Returns & Refunds      | 5.1       | ✅ Good
 245 Technical Support      | 8.7       | ❌ Poor (needs optimization)
 246 Account Settings       | 4.2       | ✅ Good
 247 ```
 248 
 249 ### Interpretation
 250 
 251 | Avg Turns | What It Means | Action |
 252 |-----------|---------------|--------|
 253 | **<4** | Highly efficient (likely simple Q&A) | Maintain efficiency |
 254 | **4-6** | Normal for multi-step workflows | Acceptable, monitor for increases |
 255 | **6-8** | Agent is slow or inefficient | Optimize instructions, reduce redundant questions |
 256 | **>8** | Major inefficiency, customer frustration | Immediate redesign needed |
 257 
 258 ### Improvement Strategies
 259 
 260 **If Turn Count is High:**
 261 
 262 1. **Reduce Redundant Questions:**
 263    ```yaml
 264    # Before (Redundant)
 265    Agent: What's your order number?
 266    User: 12345678
 267    Agent: Thanks. And what's your email?
 268    User: john@example.com
 269    Agent: And your phone number?
 270 
 271    # After (Batch Questions)
 272    Agent: To look up your order, I'll need your order number and the email
 273           address you used for the purchase. What are those?
 274    User: Order 12345678, email john@example.com
 275    Agent: Got it! Let me pull that up...
 276    ```
 277 
 278 2. **Use Smarter Actions:**
 279    - Instead of asking for email separately, look up order by order number and auto-retrieve email
 280    - Use Flow Get Records to pre-fetch data
 281 
 282 3. **Eliminate Unnecessary Confirmations:**
 283    ```yaml
 284    # Before (Excessive Confirmation)
 285    Agent: I'll check your order status now. Is that okay?
 286    User: Yes.
 287    Agent: [Retrieves order]
 288 
 289    # After (Just Act)
 290    Agent: Let me check your order status...
 291    Agent: [Retrieves order immediately]
 292    ```
 293 
 294 4. **Parallelize Data Collection:**
 295    ```yaml
 296    # Before (Sequential)
 297    Turn 1: Agent asks for order number
 298    Turn 2: User provides
 299    Turn 3: Agent asks for reason for return
 300    Turn 4: User provides
 301    Turn 5: Agent asks for preferred refund method
 302    Turn 6: User provides
 303 
 304    # After (Combined)
 305    Turn 1: Agent asks for order number and reason in one question
 306    Turn 2: User provides both
 307    Turn 3: Agent asks for refund method
 308    Turn 4: User provides
 309    ```
 310 
 311 ---
 312 
 313 ## Metric 4: Customer Satisfaction (CSAT)
 314 
 315 **Definition:** Percentage of customers who rate their experience positively.
 316 
 317 **Formula:**
 318 ```
 319 CSAT = (Positive Ratings / Total Ratings) × 100
 320 ```
 321 
 322 **Target Benchmark:** >80% (4+ out of 5 stars)
 323 
 324 **Grade Scale:**
 325 - **Excellent:** >90%
 326 - **Good:** 80-90%
 327 - **Fair:** 70-80%
 328 - **Poor:** <70%
 329 
 330 ### How to Measure
 331 
 332 **Method 1: Post-Conversation Survey**
 333 
 334 After conversation ends, trigger a survey:
 335 ```
 336 Survey Question: "How satisfied were you with this conversation?"
 337   ⭐ ⭐ ⭐ ⭐ ⭐ (5 stars)
 338 
 339 Positive = 4-5 stars
 340 Neutral = 3 stars
 341 Negative = 1-2 stars
 342 
 343 CSAT = (4-5 star ratings / Total ratings) × 100
 344 ```
 345 
 346 **Method 2: Thumbs Up/Down**
 347 
 348 Simpler binary feedback:
 349 ```
 350 Survey Question: "Was this conversation helpful?"
 351   👍 Helpful  |  👎 Not Helpful
 352 
 353 CSAT = (Thumbs Up / Total) × 100
 354 ```
 355 
 356 **Method 3: Net Promoter Score (NPS)**
 357 
 358 For deeper loyalty measurement:
 359 ```
 360 Survey Question: "How likely are you to recommend our support to a friend?"
 361   0 (Not Likely) ... 10 (Very Likely)
 362 
 363 Promoters (9-10): Highly satisfied
 364 Passives (7-8): Neutral
 365 Detractors (0-6): Dissatisfied
 366 
 367 NPS = % Promoters - % Detractors
 368 ```
 369 
 370 ### Interpretation
 371 
 372 | CSAT Score | What It Means | Action |
 373 |------------|---------------|--------|
 374 | **>90%** | Customers are very happy | Maintain quality, scale to more use cases |
 375 | **80-90%** | Generally satisfied | Identify and fix pain points |
 376 | **70-80%** | Mixed feedback | Major improvements needed |
 377 | **<70%** | Customers are unhappy | Urgent redesign or consider removing AI |
 378 
 379 ### Improvement Strategies
 380 
 381 **If CSAT is Low:**
 382 
 383 1. **Analyze Low-Rating Conversations:**
 384    - Review 1-2 star ratings to find patterns
 385    - Common themes: "Agent didn't understand me", "Too slow", "Didn't solve my problem"
 386 
 387 2. **Improve Empathy and Tone:**
 388    ```yaml
 389    # Before (Robotic)
 390    Agent: Your request has been processed. Reference number: 12345.
 391 
 392    # After (Empathetic)
 393    Agent: All set! I've processed your request and you should receive confirmation
 394           shortly. Your reference number is 12345 if you need to follow up.
 395           Is there anything else I can help with?
 396    ```
 397 
 398 3. **Set Expectations:**
 399    - If an action takes time, tell the customer: "This will take about 10 seconds..."
 400    - If escalating, say: "You'll be connected in 2-3 minutes"
 401 
 402 4. **Follow Up After Resolution:**
 403    - End every conversation with: "Did that solve your issue? Is there anything else?"
 404    - This ensures the customer feels heard
 405 
 406 ---
 407 
 408 ## Metric 5: Escalation Rate
 409 
 410 **Definition:** Percentage of conversations that escalate to a human agent.
 411 
 412 **Formula:**
 413 ```
 414 Escalation Rate = (Escalations / Total Conversations) × 100
 415 ```
 416 
 417 **Target Benchmark:** 15-30%
 418 
 419 **Grade Scale:**
 420 - **Excellent:** 10-20% (AI handling most, escalating when needed)
 421 - **Good:** 20-30% (healthy balance)
 422 - **Fair:** 30-40% (over-escalating, AI not confident)
 423 - **Poor:** >40% (AI not adding value)
 424 
 425 **Note:** <10% is also concerning — may indicate under-escalation (customers frustrated but not escalating).
 426 
 427 ### How to Measure
 428 
 429 ```sql
 430 SELECT COUNT(*) AS Total,
 431        SUM(CASE WHEN Escalated__c = TRUE THEN 1 ELSE 0 END) AS Escalations,
 432        (SUM(CASE WHEN Escalated__c = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS EscalationRate
 433 FROM Conversation
 434 ```
 435 
 436 **Breakdown by Reason:**
 437 ```sql
 438 SELECT EscalationReason__c, COUNT(*) AS Count
 439 FROM Conversation
 440 WHERE Escalated__c = TRUE
 441 GROUP BY EscalationReason__c
 442 ORDER BY Count DESC
 443 ```
 444 
 445 ### Interpretation
 446 
 447 | Escalation Rate | What It Means | Action |
 448 |-----------------|---------------|--------|
 449 | **<10%** | Under-escalating (customers giving up?) | Review CSAT—are customers frustrated? |
 450 | **10-30%** | Healthy (AI handles most, escalates when needed) | Maintain and optimize |
 451 | **30-50%** | Over-escalating (AI not confident) | Improve topic classification, add actions |
 452 | **>50%** | AI is barely helping | Major redesign or consider removing AI |
 453 
 454 ### Improvement Strategies
 455 
 456 **If Escalation Rate is High:**
 457 
 458 1. **Analyze Top Escalation Reasons:**
 459    ```
 460    Top Reasons:
 461      - 40%: Complexity (multi-issue conversations)
 462      - 30%: Customer request for human
 463      - 20%: Repeated failures
 464      - 10%: Out of scope
 465    ```
 466 
 467    **Action:** Address the top reason first.
 468 
 469 2. **Reduce "Complexity" Escalations:**
 470    - Add more actions (e.g., if customers escalate for "Can't modify order", add a Modify Order action)
 471    - Improve multi-turn workflows (reduce turn count)
 472 
 473 3. **Reduce "Customer Request" Escalations:**
 474    - Some customers prefer humans — this is acceptable (target: <10%)
 475    - If >15%, customers may not trust AI — improve transparency and empathy
 476 
 477 4. **Reduce "Repeated Failures" Escalations:**
 478    - If actions fail frequently (API errors, timeouts), fix underlying systems
 479    - If solutions don't work, improve troubleshooting logic
 480 
 481 ---
 482 
 483 ## Metric 6: Containment Rate
 484 
 485 **Definition:** Percentage of conversations that stay within the AI agent (inverse of escalation rate).
 486 
 487 **Formula:**
 488 ```
 489 Containment Rate = 100% - Escalation Rate
 490 ```
 491 
 492 **Target Benchmark:** >70%
 493 
 494 **Grade Scale:**
 495 - **Excellent:** >80%
 496 - **Good:** 70-80%
 497 - **Fair:** 60-70%
 498 - **Poor:** <60%
 499 
 500 **Note:** Containment Rate and Resolution Rate are related but not identical:
 501 - **Containment Rate:** Did the conversation stay in AI? (No escalation)
 502 - **Resolution Rate:** Did the AI resolve the issue? (Successful outcome)
 503 
 504 Example:
 505 - Conversation stays in AI but doesn't resolve issue → High containment, low resolution (bad)
 506 - Conversation escalates after AI partially helps → Low containment, medium resolution (acceptable)
 507 
 508 ---
 509 
 510 ## Metric 7: First Contact Resolution (FCR)
 511 
 512 **Definition:** Percentage of issues resolved in the first conversation session (no follow-up needed).
 513 
 514 **Formula:**
 515 ```
 516 FCR = (Single-Session Resolutions / Total Resolved) × 100
 517 ```
 518 
 519 **Target Benchmark:** >60%
 520 
 521 **Grade Scale:**
 522 - **Excellent:** >75%
 523 - **Good:** 60-75%
 524 - **Fair:** 50-60%
 525 - **Poor:** <50%
 526 
 527 ### How to Measure
 528 
 529 **Method 1: Track Repeat Conversations**
 530 
 531 If a customer returns within 24 hours with the same issue, FCR failed.
 532 
 533 ```sql
 534 SELECT ContactId, COUNT(*) AS ConversationCount
 535 FROM Conversation
 536 WHERE CreatedDate >= LAST_N_DAYS:7
 537 GROUP BY ContactId
 538 HAVING COUNT(*) > 1
 539 ```
 540 
 541 **Method 2: Post-Conversation Survey**
 542 
 543 ```
 544 Survey Question: "Did we fully resolve your issue today?"
 545   - Yes, completely resolved
 546   - Partially resolved
 547   - Not resolved
 548 
 549 FCR = % who answered "Yes"
 550 ```
 551 
 552 ### Improvement Strategies
 553 
 554 **If FCR is Low:**
 555 
 556 1. **Check for Incomplete Resolutions:**
 557    - Review conversations where customers return within 24 hours
 558    - Common issue: Agent said "issue resolved" but customer didn't confirm
 559 
 560 2. **Improve Confirmation:**
 561    ```yaml
 562    # Before (No Confirmation)
 563    Agent: I've reset your password. The reset link has been sent.
 564 
 565    # After (Confirmation)
 566    Agent: I've sent the reset link to your email. Let me know when you've
 567           received it and successfully reset your password so I can confirm
 568           everything is working.
 569    ```
 570 
 571 3. **Offer Follow-Up:**
 572    ```
 573    Agent: Your order has been canceled and you'll receive a refund in 5-7 days.
 574           If you don't see the refund by [date], reach out and I'll escalate it.
 575           Does that work for you?
 576    ```
 577 
 578 ---
 579 
 580 ## Metric 8: Error Recovery Rate
 581 
 582 **Definition:** Percentage of errors (misunderstandings, failed actions, wrong topic routing) that are gracefully recovered without escalation.
 583 
 584 **Formula:**
 585 ```
 586 Error Recovery Rate = (Errors Recovered / Total Errors) × 100
 587 ```
 588 
 589 **Target Benchmark:** >70%
 590 
 591 **Grade Scale:**
 592 - **Excellent:** >85%
 593 - **Good:** 70-85%
 594 - **Fair:** 60-70%
 595 - **Poor:** <60%
 596 
 597 ### How to Measure
 598 
 599 **Method 1: Manual Review**
 600 
 601 Sample 100 conversations with errors:
 602 - Misclassification (wrong topic)
 603 - Failed action (API error, timeout)
 604 - Misunderstanding (agent gives wrong answer)
 605 
 606 For each error, did the agent recover?
 607 ```
 608 Example 1 (Recovered):
 609   Agent: [Routes to wrong topic]
 610   User: "No, I need help with X"
 611   Agent: "Got it, let me switch to [correct topic]"
 612   [Conversation continues successfully]
 613 
 614 Example 2 (Not Recovered):
 615   Agent: [Routes to wrong topic]
 616   User: "No, I need help with X"
 617   Agent: [Still in wrong topic, doesn't switch]
 618   User: "Forget it, get me a human"
 619 ```
 620 
 621 **Method 2: Track Topic Switches**
 622 
 623 If the agent switches topics mid-conversation, it suggests initial classification was wrong. Did it recover?
 624 
 625 ```
 626 Topic Switch + Resolution = Error Recovered ✅
 627 Topic Switch + Escalation = Error Not Recovered ❌
 628 ```
 629 
 630 ### Improvement Strategies
 631 
 632 **If Error Recovery Rate is Low:**
 633 
 634 1. **Improve Fallback Responses:**
 635    ```yaml
 636    Fallback Topic Instructions:
 637    If you don't understand the customer's request, offer choices:
 638    "I'm not sure I understood that. Are you looking for help with:
 639     • Order status
 640     • Returns
 641     • Technical support
 642     Which is closest to what you need?"
 643    ```
 644 
 645 2. **Add Error Handling to Actions:**
 646    ```yaml
 647    Action: Get Order Status
 648    Action-Level Instructions:
 649    If this action fails (order not found, API error), apologize and offer
 650    alternatives:
 651    "I'm having trouble looking up that order. Let's try this:
 652     • Double-check the order number (it's 8 digits)
 653     • Or, I can look it up by your email address instead
 654     Which would you prefer?"
 655    ```
 656 
 657 3. **Train on Edge Cases:**
 658    - Add conversation examples (training data) for common errors
 659    - Example: "User says 'no' after agent proposes solution → agent asks clarifying question"
 660 
 661 ---
 662 
 663 ## Metric 9: Conversation Duration
 664 
 665 **Definition:** Average time (in seconds) from first message to resolution or escalation.
 666 
 667 **Formula:**
 668 ```
 669 Avg Duration = SUM(ConversationDuration) / Total Conversations
 670 ```
 671 
 672 **Target Benchmark:** <5 minutes (300 seconds)
 673 
 674 **Grade Scale:**
 675 - **Excellent:** <3 minutes
 676 - **Good:** 3-5 minutes
 677 - **Fair:** 5-7 minutes
 678 - **Poor:** >7 minutes
 679 
 680 ### Interpretation
 681 
 682 | Duration | What It Means | Action |
 683 |----------|---------------|--------|
 684 | **<3 min** | Efficient (likely Q&A or simple workflows) | Maintain efficiency |
 685 | **3-5 min** | Normal for multi-turn workflows | Acceptable |
 686 | **5-7 min** | Slow, customer may be frustrated | Optimize for speed |
 687 | **>7 min** | Too slow, high abandonment risk | Immediate optimization |
 688 
 689 **Note:** Duration is affected by:
 690 - User response time (not in agent's control)
 691 - Action execution time (API latency, Flow complexity)
 692 - Agent turn count (more turns = longer duration)
 693 
 694 ### Improvement Strategies
 695 
 696 **If Duration is High:**
 697 
 698 1. **Optimize Action Performance:**
 699    - Review Flow execution times (Setup → Flow → Execution History)
 700    - Optimize SOQL queries (add indexes, reduce record counts)
 701    - Cache frequently-accessed data (Knowledge articles, picklist values)
 702 
 703 2. **Reduce Turn Count:** See Metric 3 (Avg Turns to Resolution)
 704 
 705 3. **Set Expectations for Slow Actions:**
 706    ```
 707    Agent: Let me run a credit check—this will take about 15 seconds...
 708    ```
 709 
 710 ---
 711 
 712 ## Metric 10: Abandonment Rate
 713 
 714 **Definition:** Percentage of conversations where the customer stops responding before resolution.
 715 
 716 **Formula:**
 717 ```
 718 Abandonment Rate = (Abandoned Conversations / Total Conversations) × 100
 719 ```
 720 
 721 **Target Benchmark:** <20%
 722 
 723 **Grade Scale:**
 724 - **Excellent:** <10%
 725 - **Good:** 10-20%
 726 - **Fair:** 20-30%
 727 - **Poor:** >30%
 728 
 729 ### How to Measure
 730 
 731 **Definition of Abandonment:**
 732 - Agent sends a message, customer doesn't respond within 5 minutes
 733 - Conversation ends without resolution or escalation
 734 
 735 ```sql
 736 SELECT COUNT(*) AS Abandoned
 737 FROM Conversation
 738 WHERE Status = 'Abandoned'
 739 AND LastMessageSender = 'Agent'
 740 AND TimeSinceLastMessage > 5 minutes
 741 ```
 742 
 743 ### Interpretation
 744 
 745 | Abandonment Rate | What It Means | Action |
 746 |------------------|---------------|--------|
 747 | **<10%** | Customers are engaged | Maintain quality |
 748 | **10-20%** | Acceptable (some drop-off is normal) | Monitor for increases |
 749 | **20-30%** | High abandonment, customers giving up | Immediate investigation |
 750 | **>30%** | Major UX problem | Urgent redesign |
 751 
 752 ### Improvement Strategies
 753 
 754 **If Abandonment Rate is High:**
 755 
 756 1. **Analyze When Abandonment Happens:**
 757    ```
 758    Turn Abandonment Rate:
 759      - Turn 1: 5% (normal, user may have changed mind)
 760      - Turn 3: 10%
 761      - Turn 5: 25% ← Peak abandonment (investigate)
 762      - Turn 7: 15%
 763    ```
 764 
 765    **Action:** Review what happens at Turn 5. Is the agent asking a confusing question? Is an action failing?
 766 
 767 2. **Reduce Friction:**
 768    - If customers abandon after "What's your order number?", they may not have it handy
 769    - Offer alternative: "If you don't have your order number, I can look it up by email address"
 770 
 771 3. **Improve Engagement:**
 772    ```yaml
 773    # Before (Dry)
 774    Agent: What's your order number?
 775 
 776    # After (Engaging)
 777    Agent: I can check your order status! What's your order number? (It's usually
 778           in your confirmation email.)
 779    ```
 780 
 781 ---
 782 
 783 ## Summary: Metrics Dashboard
 784 
 785 Track these 10 metrics in a Salesforce Dashboard:
 786 
 787 | Metric | Target | Current | Status |
 788 |--------|--------|---------|--------|
 789 | **Resolution Rate** | >70% | 78% | ✅ Good |
 790 | **Classification Accuracy** | >90% | 92% | ✅ Good |
 791 | **Avg Turns to Resolution** | <6 | 5.2 | ✅ Good |
 792 | **Customer Satisfaction (CSAT)** | >80% | 85% | ✅ Good |
 793 | **Escalation Rate** | 15-30% | 22% | ✅ Good |
 794 | **Containment Rate** | >70% | 78% | ✅ Good |
 795 | **First Contact Resolution (FCR)** | >60% | 68% | ✅ Good |
 796 | **Error Recovery Rate** | >70% | 74% | ✅ Good |
 797 | **Avg Duration** | <5 min | 4.2 min | ✅ Good |
 798 | **Abandonment Rate** | <20% | 12% | ✅ Good |
 799 
 800 **Overall Agent Health:** 🟢 Healthy
 801 
 802 ---
 803 
 804 ## Continuous Improvement Process
 805 
 806 ### Step 1: Monitor Weekly
 807 - Review top 3 metrics: Resolution Rate, CSAT, Escalation Rate
 808 - Flag any metric that drops >5% week-over-week
 809 
 810 ### Step 2: Investigate Monthly
 811 - Deep-dive into failing conversations (low CSAT, high turns, abandonment)
 812 - Identify patterns (specific topics, specific actions, specific times of day)
 813 
 814 ### Step 3: Optimize Quarterly
 815 - Implement fixes for top 3 pain points
 816 - A/B test instruction changes (old vs. new instructions)
 817 - Measure impact of changes
 818 
 819 ### Step 4: Benchmark Annually
 820 - Compare year-over-year metrics
 821 - Adjust targets based on industry benchmarks and business goals
 822 - Celebrate wins and share learnings across teams
 823 
 824 ---
 825 
 826 ## Final Checklist: Is My Agent High-Quality?
 827 
 828 - [ ] Resolution Rate >70%
 829 - [ ] Classification Accuracy >90%
 830 - [ ] CSAT >80%
 831 - [ ] Escalation Rate 15-30%
 832 - [ ] FCR >60%
 833 - [ ] Error Recovery Rate >70%
 834 - [ ] Avg Duration <5 min
 835 - [ ] Abandonment Rate <20%
 836 
 837 If you check 7+ boxes, your agent is high-quality. If <5, focus on improvement areas.
