<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Escalation Patterns for Agentforce
   2 
   3 This guide catalogs escalation triggers, routing patterns, and context handoff mechanisms for Agentforce agents. Effective escalation ensures customers reach human agents at the right time with the right context.
   4 
   5 ---
   6 
   7 ## Escalation Philosophy
   8 
   9 **Key Principles:**
  10 1. **Escalate Early, Not Late** — Don't exhaust the customer with failed AI attempts before escalating
  11 2. **Context is King** — Pass conversation history, key IDs, sentiment, and attempted solutions
  12 3. **Set Expectations** — Tell the customer what happens next ("You'll be connected in 2-3 minutes")
  13 4. **Measure and Optimize** — Track escalation rate and reasons to improve AI containment
  14 
  15 ---
  16 
  17 ## Escalation Trigger Categories
  18 
  19 ### Trigger Category 1: Sentiment-Based Escalation
  20 
  21 **Description:** Detect frustrated, angry, or distressed customers and escalate before the situation worsens.
  22 
  23 #### Trigger 1.1: Frustration Detection
  24 
  25 **Indicators:**
  26 - Repeated phrases ("I already told you", "This is ridiculous", "For the third time")
  27 - Profanity or strong language (filtered by Einstein Trust Layer, but tone detected)
  28 - All-caps messages ("THIS DOESN'T WORK")
  29 - Short, clipped responses after detailed agent messages
  30 
  31 **Priority Level:** High
  32 
  33 **Agentforce Implementation:**
  34 
  35 ```yaml
  36 Agent-Level Instructions:
  37   If the customer shows frustration (repeating themselves, using strong language,
  38   expressing disappointment), acknowledge their feelings and escalate immediately:
  39 
  40   "I understand this has been frustrating, and I apologize for the trouble. Let me
  41   connect you with a specialist who can give this their full attention right now."
  42 
  43   Use the "Escalate to Support" action and mark the sentiment as "Frustrated" so
  44   the human agent is prepared.
  45 ```
  46 
  47 **Example Conversation:**
  48 ```
  49 User: I've been trying to reset my password for 30 minutes!
  50 
  51 Agent: I'm truly sorry this has taken so long. That's unacceptable, and I want
  52        to get this resolved for you right away.
  53 
  54        Let me connect you with a technical specialist who can investigate your
  55        account and fix this immediately. They'll have all the details from our
  56        conversation.
  57 
  58        [Escalation triggered with sentiment = "Frustrated"]
  59 ```
  60 
  61 **Omni-Channel Routing:**
  62 ```yaml
  63 Queue: Frustrated Customers
  64 Priority: High (routed ahead of normal queue)
  65 Skill Required: De-escalation Training
  66 ```
  67 
  68 #### Trigger 1.2: Anger Detection
  69 
  70 **Indicators:**
  71 - Threats ("I'm going to cancel my account", "I'll report this")
  72 - Blame statements ("Your company is terrible", "This is a scam")
  73 - Demands ("I demand a refund", "Get me a manager NOW")
  74 
  75 **Priority Level:** Urgent
  76 
  77 **Agentforce Implementation:**
  78 
  79 ```yaml
  80 Agent-Level Instructions:
  81   If the customer expresses anger or makes threats, do NOT try to resolve the
  82   issue yourself. Escalate immediately without prolonging the conversation:
  83 
  84   "I'm very sorry you've had this experience. Let me connect you with a manager
  85   who can address this right away."
  86 
  87   Use the "Escalate to Manager" action with sentiment = "Angry".
  88 ```
  89 
  90 **Omni-Channel Routing:**
  91 ```yaml
  92 Queue: Manager Escalations
  93 Priority: Urgent (highest priority)
  94 Skill Required: Manager or Senior Agent
  95 ```
  96 
  97 #### Trigger 1.3: Distress / Self-Harm
  98 
  99 **Indicators:**
 100 - References to self-harm, suicide, or harm to others
 101 - Extreme emotional distress
 102 
 103 **Priority Level:** Emergency
 104 
 105 **Agentforce Implementation:**
 106 
 107 ```yaml
 108 Agent-Level Instructions:
 109   If the customer mentions self-harm, suicide, or extreme distress, immediately
 110   provide crisis resources and escalate:
 111 
 112   "I'm very concerned about what you've shared. Please reach out to a crisis
 113   support line immediately:
 114   • National Suicide Prevention Lifeline: 988
 115   • Crisis Text Line: Text HOME to 741741
 116 
 117   I'm also connecting you with a specialist who can provide additional support."
 118 
 119   Use the "Emergency Escalation" action.
 120 ```
 121 
 122 **Omni-Channel Routing:**
 123 ```yaml
 124 Queue: Crisis Escalations
 125 Priority: Emergency (bypasses all queues)
 126 Skill Required: Crisis Intervention Training
 127 Alert: Supervisor notified immediately
 128 ```
 129 
 130 ---
 131 
 132 ### Trigger Category 2: Complexity-Based Escalation
 133 
 134 **Description:** Escalate when the conversation becomes too complex for the AI to handle effectively.
 135 
 136 #### Trigger 2.1: High Turn Count
 137 
 138 **Definition:** Conversation exceeds 8-10 turns without resolution.
 139 
 140 **Indicators:**
 141 - Customer and agent have exchanged 8+ messages
 142 - No clear progress toward resolution
 143 - Same topic, multiple failed attempts
 144 
 145 **Priority Level:** Medium
 146 
 147 **Agentforce Implementation:**
 148 
 149 ```yaml
 150 Agent-Level Instructions:
 151   If the conversation reaches 8 turns and the issue isn't resolved, acknowledge
 152   the complexity and escalate:
 153 
 154   "I can see this is taking longer than it should. Let me connect you with a
 155   specialist who can dive deeper into this and get it resolved quickly."
 156 
 157   Use the "Escalate to Support" action with reason = "High Complexity".
 158 ```
 159 
 160 **Example:**
 161 ```
 162 Turn 1: User asks for help with feature
 163 Turn 2: Agent asks clarifying question
 164 Turn 3: User responds
 165 Turn 4: Agent suggests solution A
 166 Turn 5: User: "That didn't work"
 167 Turn 6: Agent suggests solution B
 168 Turn 7: User: "Still not working"
 169 Turn 8: Agent escalates → "Let me connect you with a specialist..."
 170 ```
 171 
 172 #### Trigger 2.2: Repeated Failures
 173 
 174 **Definition:** Agent attempts the same action 2-3 times and it fails each time.
 175 
 176 **Indicators:**
 177 - API call fails twice
 178 - User reports "still not working" after 2 solution attempts
 179 - Same error occurs multiple times
 180 
 181 **Priority Level:** Medium
 182 
 183 **Agentforce Implementation:**
 184 
 185 ```yaml
 186 Action-Level Instructions (for each action):
 187   If this action fails, apologize and try an alternative approach. If it fails
 188   a second time, escalate rather than attempting a third time:
 189 
 190   "I'm having trouble resolving this through our system. Let me connect you with
 191   a technical specialist who can investigate the root cause."
 192 ```
 193 
 194 **Example (Password Reset Failure):**
 195 ```
 196 Turn 1: Agent sends reset link
 197 Turn 2: User: "Link doesn't work"
 198 Turn 3: Agent sends new link with note about expiration
 199 Turn 4: User: "Still doesn't work"
 200 Turn 5: Agent escalates → "Let me connect you with technical support..."
 201 ```
 202 
 203 #### Trigger 2.3: Multi-Issue Conversation
 204 
 205 **Definition:** Customer raises 2+ unrelated issues in one conversation.
 206 
 207 **Indicators:**
 208 - Topic switches mid-conversation
 209 - Multiple problems mentioned ("...and also my account is locked, and I need a refund")
 210 
 211 **Priority Level:** Medium
 212 
 213 **Agentforce Implementation:**
 214 
 215 ```yaml
 216 Agent-Level Instructions:
 217   If the customer raises multiple unrelated issues, acknowledge them and suggest
 218   escalation or sequential handling:
 219 
 220   "I can see you have a few things going on—[Issue A], [Issue B], and [Issue C].
 221   Let me connect you with a specialist who can address all of these together,
 222   or we can handle them one at a time. Which would you prefer?"
 223 ```
 224 
 225 ---
 226 
 227 ### Trigger Category 3: Policy-Based Escalation
 228 
 229 **Description:** Escalate when the request requires human judgment, policy exceptions, or approval.
 230 
 231 #### Trigger 3.1: High-Value Transactions
 232 
 233 **Definition:** Request involves amounts exceeding agent's authorization limit.
 234 
 235 **Examples:**
 236 - Refund over $500
 237 - Order cancellation over $1,000
 238 - Credit adjustment over $100
 239 
 240 **Priority Level:** High
 241 
 242 **Agentforce Implementation:**
 243 
 244 ```yaml
 245 Action: Issue Refund
 246 Action-Level Instructions:
 247   If the refund amount exceeds $500, you cannot process it directly. Escalate
 248   to a manager:
 249 
 250   "Refunds over $500 require manager approval to ensure accuracy. Let me create
 251   an approval request and connect you with a manager who can review and process
 252   this right away."
 253 
 254   Use the "Escalate to Manager" action with reason = "High Value Refund".
 255 ```
 256 
 257 **Omni-Channel Routing:**
 258 ```yaml
 259 Queue: Manager Approvals
 260 Priority: High
 261 Skill Required: Manager or Approval Authority
 262 Context Passed:
 263   - Refund Amount
 264   - Order ID
 265   - Customer Account ID
 266   - Reason for Refund
 267 ```
 268 
 269 #### Trigger 3.2: Policy Exception Requests
 270 
 271 **Definition:** Customer requests something outside standard policy.
 272 
 273 **Examples:**
 274 - Return after 30-day window
 275 - Waive restocking fee
 276 - Expedite shipping for free
 277 - Refund for personalized/non-refundable item
 278 
 279 **Priority Level:** Medium-High
 280 
 281 **Agentforce Implementation:**
 282 
 283 ```yaml
 284 Topic: Returns & Refunds
 285 Instructions:
 286   If the customer is outside the 30-day return window, explain the policy but
 287   offer escalation:
 288 
 289   "Our standard return policy is 30 days, but I understand there may be special
 290   circumstances. Let me connect you with a manager who can review your case and
 291   see what options are available."
 292 
 293   Use the "Escalate to Manager" action with reason = "Policy Exception Request".
 294 ```
 295 
 296 **Example Conversation:**
 297 ```
 298 User: I bought this 45 days ago but I've been traveling. Can I still return it?
 299 
 300 Agent: Our standard policy is 30 days, but I understand you've been traveling.
 301        Let me connect you with a manager who can review your situation and see
 302        if we can make an exception. They'll reach out shortly—does that work?
 303 
 304 User: Yes, thank you.
 305 
 306 Agent: Great! I've created a case and a manager will contact you within 2 hours.
 307        Your case number is #00284955 for reference.
 308 ```
 309 
 310 #### Trigger 3.3: VIP / High-Priority Customers
 311 
 312 **Definition:** Customer is flagged as VIP, enterprise account, or high-value customer.
 313 
 314 **Indicators:**
 315 - Account.VIP__c = true
 316 - Account.Annual_Revenue__c > $100,000
 317 - Account.Type = 'Enterprise'
 318 
 319 **Priority Level:** High
 320 
 321 **Agentforce Implementation:**
 322 
 323 ```yaml
 324 Agent-Level Instructions:
 325   If the customer is a VIP (Account.VIP__c = true), offer white-glove service:
 326 
 327   "I see you're one of our valued VIP customers. Let me connect you directly
 328   with your dedicated account manager who can give this their full attention."
 329 
 330   Use the "Escalate to Account Manager" action.
 331 ```
 332 
 333 **Omni-Channel Routing:**
 334 ```yaml
 335 Queue: VIP Support
 336 Priority: High
 337 Skill Required: Account Manager or VIP Support Specialist
 338 SLA: 5-minute response time (vs. 15 minutes for standard)
 339 ```
 340 
 341 ---
 342 
 343 ### Trigger Category 4: Explicit Request Escalation
 344 
 345 **Description:** Customer directly asks for a human agent.
 346 
 347 #### Trigger 4.1: Direct Request for Human
 348 
 349 **Phrases:**
 350 - "I want to talk to a person"
 351 - "Transfer me to an agent"
 352 - "Get me a human"
 353 - "I don't want to talk to a bot"
 354 
 355 **Priority Level:** Medium
 356 
 357 **Agentforce Implementation:**
 358 
 359 ```yaml
 360 Agent-Level Instructions:
 361   If the customer explicitly asks to speak with a human agent, honor that request
 362   immediately without trying to convince them to stay with the AI:
 363 
 364   "Of course! Let me connect you with an agent right now. They'll have all the
 365   details from our conversation."
 366 
 367   Use the "Escalate to Support" action with reason = "Customer Request".
 368 ```
 369 
 370 **Anti-Pattern (Don't Do This):**
 371 ```
 372 ❌ User: I want to talk to a person.
 373 
 374 ❌ Agent: I'd love to help you myself! I can answer most questions. What do you
 375           need help with? [trying to prevent escalation]
 376 ```
 377 
 378 **Correct Pattern:**
 379 ```
 380 ✅ User: I want to talk to a person.
 381 
 382 ✅ Agent: Of course! Connecting you now. One moment... [immediate escalation]
 383 ```
 384 
 385 #### Trigger 4.2: Request for Manager/Supervisor
 386 
 387 **Phrases:**
 388 - "I want to speak to your manager"
 389 - "Get me a supervisor"
 390 - "Let me talk to someone in charge"
 391 
 392 **Priority Level:** High
 393 
 394 **Agentforce Implementation:**
 395 
 396 ```yaml
 397 Agent-Level Instructions:
 398   If the customer asks for a manager, route to the Manager queue:
 399 
 400   "I understand you'd like to speak with a manager. Let me connect you now."
 401 
 402   Use the "Escalate to Manager" action.
 403 ```
 404 
 405 **Omni-Channel Routing:**
 406 ```yaml
 407 Queue: Manager Escalations
 408 Priority: High
 409 ```
 410 
 411 ---
 412 
 413 ### Trigger Category 5: Safety-Based Escalation
 414 
 415 **Description:** Escalate when content suggests safety risk, legal concern, or emergency.
 416 
 417 #### Trigger 5.1: Legal / Compliance Concerns
 418 
 419 **Indicators:**
 420 - Mentions of lawsuits, lawyers, legal action
 421 - GDPR/privacy concerns (data deletion, access requests)
 422 - Regulatory compliance questions
 423 
 424 **Priority Level:** High
 425 
 426 **Agentforce Implementation:**
 427 
 428 ```yaml
 429 Agent-Level Instructions:
 430   If the customer mentions legal action, lawyers, or compliance concerns, escalate
 431   to the legal team immediately:
 432 
 433   "I understand this is a legal matter. Let me connect you with our compliance
 434   team who can address this appropriately."
 435 
 436   Use the "Escalate to Legal" action.
 437 ```
 438 
 439 **Omni-Channel Routing:**
 440 ```yaml
 441 Queue: Legal / Compliance
 442 Priority: High
 443 Skill Required: Compliance Officer or Legal Liaison
 444 Alert: Legal team notified via email
 445 ```
 446 
 447 #### Trigger 5.2: Security Incidents
 448 
 449 **Indicators:**
 450 - "My account was hacked"
 451 - "Someone stole my password"
 452 - "Unauthorized charges on my card"
 453 
 454 **Priority Level:** Urgent
 455 
 456 **Agentforce Implementation:**
 457 
 458 ```yaml
 459 Agent-Level Instructions:
 460   If the customer reports a security incident, escalate immediately to the
 461   security team and advise immediate action:
 462 
 463   "This is a security concern and needs immediate attention. Let me connect you
 464   with our security team right now. In the meantime:
 465   • Change your password immediately
 466   • Check your account for unauthorized activity
 467   • Do not click any suspicious links"
 468 
 469   Use the "Escalate to Security" action with reason = "Security Incident".
 470 ```
 471 
 472 **Omni-Channel Routing:**
 473 ```yaml
 474 Queue: Security Incidents
 475 Priority: Urgent
 476 Skill Required: Security Analyst
 477 Alert: Security team notified immediately
 478 ```
 479 
 480 ---
 481 
 482 ## Agentforce Escalation Mechanism
 483 
 484 ### Built-In: Escalation Topic
 485 
 486 Agentforce includes a pre-configured **Escalation Topic** that integrates with Omni-Channel.
 487 
 488 **Setup Steps:**
 489 
 490 1. **Enable Escalation Topic:**
 491    - Setup → Agentforce Agents → [Your Agent] → Topics
 492    - Enable "Escalation Topic"
 493 
 494 2. **Configure Omni-Channel Queue:**
 495    - Setup → Queues → New
 496    - Name: "Agentforce Escalations"
 497    - Add Agent Members
 498 
 499 3. **Link Queue to Escalation Topic:**
 500    - Agentforce Agent Settings → Escalation Topic
 501    - Select Omni-Channel Queue
 502 
 503 4. **Configure Routing:**
 504    - Setup → Routing Configurations
 505    - Create rules for priority (VIP, frustrated, urgent)
 506 
 507 **Escalation Topic Behavior:**
 508 ```
 509 User: "I want to talk to someone."
 510 
 511 Agent: [Escalation Topic triggered]
 512        "Of course! I'm transferring you to an agent now. They'll have all the
 513        details from our conversation."
 514 
 515        [Conversation routed to Omni-Channel → Human agent receives chat]
 516 ```
 517 
 518 ### Custom Escalation Actions
 519 
 520 For domain-specific routing (e.g., "Escalate to Billing" vs. "Escalate to Tech Support"), create custom Flow actions.
 521 
 522 **Example: Escalate to Technical Support**
 523 
 524 ```yaml
 525 Flow: Escalate to Technical Support
 526 Inputs:
 527   - ConversationId (Text)
 528   - Reason (Text): "High Complexity", "Repeated Failures", "Customer Request"
 529   - Sentiment (Picklist): "Neutral", "Frustrated", "Angry"
 530 
 531 Steps:
 532   1. Get Messages: Retrieve conversation history from ConversationParticipant records
 533   2. Summarize Context: Use Flow Text Template to create summary
 534   3. Create AgentWork:
 535      - WorkItemId = ConversationId
 536      - QueueId = Tech_Support_Queue__c
 537      - Priority = IF(Sentiment = "Angry", "Urgent", IF(Sentiment = "Frustrated", "High", "Medium"))
 538      - CustomContext__c = JSON.serialize({
 539          'reason': Reason,
 540          'sentiment': Sentiment,
 541          'turn_count': Message count,
 542          'topics_attempted': List of topics covered,
 543          'conversation_summary': Summary text
 544        })
 545   4. Send Message to Customer:
 546      - "I'm connecting you with a technical specialist. You should see them join in about 2-3 minutes."
 547 ```
 548 
 549 ---
 550 
 551 ## Context Handoff Specification
 552 
 553 **Critical:** Human agents need context to pick up where the AI left off. Pass this information:
 554 
 555 ### Essential Context (Always Pass)
 556 
 557 | Field | Source | Example |
 558 |-------|--------|---------|
 559 | **Customer Name** | Contact.Name | "John Doe" |
 560 | **Account ID** | Contact.AccountId | "0018X000001AbCd" |
 561 | **Conversation Summary** | AI-generated summary | "Customer unable to reset password after 2 attempts" |
 562 | **Sentiment** | Agent assessment | "Frustrated" |
 563 | **Turn Count** | Count of messages | 8 |
 564 | **Topics Attempted** | List of topics | "Password Reset, Account Settings" |
 565 
 566 ### Domain-Specific Context
 567 
 568 **For Technical Support Escalations:**
 569 - Error messages user reported
 570 - Device/OS information (if collected)
 571 - Troubleshooting steps already attempted
 572 - Reproduction steps
 573 
 574 **For Billing Escalations:**
 575 - Order ID or Invoice ID
 576 - Amount in question
 577 - Billing history (last 3 transactions)
 578 
 579 **For Refund Escalations:**
 580 - Order ID
 581 - Refund amount requested
 582 - Eligibility check result (eligible vs. ineligible + reason)
 583 - Return status
 584 
 585 ### AgentWork Custom Context Example
 586 
 587 ```json
 588 {
 589   "reason": "High Value Refund",
 590   "sentiment": "Frustrated",
 591   "turn_count": 6,
 592   "topics_attempted": ["Returns & Refunds", "Order Status"],
 593   "conversation_summary": "Customer requested $800 refund for Order #12345678. Return not yet received. Customer frustrated due to shipping delay.",
 594   "order_id": "8018X000001XyZ",
 595   "refund_amount": 800,
 596   "return_status": "Not Received",
 597   "shipping_carrier": "FedEx",
 598   "tracking_number": "1234567890",
 599   "attempted_solutions": [
 600     "Checked order status",
 601     "Verified return eligibility",
 602     "Explained policy (return must be received first)"
 603   ]
 604 }
 605 ```
 606 
 607 **Human Agent View:**
 608 
 609 When the human agent accepts the chat, they see:
 610 ```
 611 ┌─────────────────────────────────────────────────────────────┐
 612 │ New Chat: John Doe (Account: Acme Corp - VIP)              │
 613 ├─────────────────────────────────────────────────────────────┤
 614 │ Escalation Reason: High Value Refund                        │
 615 │ Sentiment: Frustrated                                       │
 616 │ Turn Count: 6                                               │
 617 ├─────────────────────────────────────────────────────────────┤
 618 │ Summary: Customer requested $800 refund for Order #12345678.│
 619 │ Return not yet received. Customer frustrated due to shipping│
 620 │ delay.                                                       │
 621 ├─────────────────────────────────────────────────────────────┤
 622 │ Context:                                                    │
 623 │ • Order ID: 8018X000001XyZ                                  │
 624 │ • Refund Amount: $800                                       │
 625 │ • Return Status: Not Received                               │
 626 │ • Tracking: FedEx 1234567890                                │
 627 │                                                             │
 628 │ AI Attempted:                                               │
 629 │ • Checked order status                                      │
 630 │ • Verified return eligibility                               │
 631 │ • Explained return policy                                   │
 632 ├─────────────────────────────────────────────────────────────┤
 633 │ [View Full Transcript] [Accept Chat]                        │
 634 └─────────────────────────────────────────────────────────────┘
 635 ```
 636 
 637 Human agent can immediately see the context and pick up the conversation without re-asking questions.
 638 
 639 ---
 640 
 641 ## Escalation Rate Benchmarks
 642 
 643 **Healthy Escalation Rate:** 15-30% of conversations
 644 
 645 | Rate | Interpretation | Action |
 646 |------|----------------|--------|
 647 | **<10%** | Under-escalating (customers frustrated, giving up) | Review escalation triggers—are they too strict? |
 648 | **10-30%** | Healthy (AI handling most, escalating when needed) | Monitor and optimize |
 649 | **30-50%** | Over-escalating (AI not confident) | Improve topic classification, add training data |
 650 | **>50%** | AI not adding value (most convos escalate) | Redesign agent scope, simplify topics |
 651 
 652 **Track by Reason:**
 653 - **Customer Request:** 5-10% (acceptable, user preference)
 654 - **Complexity:** 5-10% (improve AI training for these scenarios)
 655 - **Frustration:** <5% (if higher, fix root cause—slow responses, repeated failures)
 656 - **Policy Exception:** 3-7% (expected for edge cases)
 657 
 658 ---
 659 
 660 ## Escalation Quality Metrics
 661 
 662 ### Metric 1: Escalation Regret Rate
 663 
 664 **Definition:** % of escalations that were unnecessary (human agent resolves in 1-2 turns with information AI already had).
 665 
 666 **Target:** <10%
 667 
 668 **How to Measure:**
 669 - Post-escalation survey: "Could the AI have resolved this?"
 670 - Agent tagging: "Escalation Not Needed"
 671 
 672 **If High:** Agent is escalating too early. Improve instructions or add actions.
 673 
 674 ### Metric 2: Context Completeness Score
 675 
 676 **Definition:** % of escalations where human agent has sufficient context to proceed without re-asking questions.
 677 
 678 **Target:** >90%
 679 
 680 **How to Measure:**
 681 - Post-escalation survey: "Did you have the context you needed?"
 682 - Track if human agent asks for information AI already collected
 683 
 684 **If Low:** Improve context passing in AgentWork.CustomContext__c.
 685 
 686 ### Metric 3: Re-Escalation Rate
 687 
 688 **Definition:** % of escalations that get escalated again by the human agent (e.g., L1 → L2 → Manager).
 689 
 690 **Target:** <15%
 691 
 692 **How to Measure:** Track AgentWork records that reference prior escalations.
 693 
 694 **If High:** Route to higher-skilled agents initially, or improve triage logic.
 695 
 696 ---
 697 
 698 ## Summary: Escalation Decision Tree
 699 
 700 ```
 701 START: Should I escalate?
 702   ├─ Is customer explicitly asking for human? → YES → Escalate (Customer Request)
 703   ├─ Is customer frustrated/angry? → YES → Escalate (Sentiment)
 704   ├─ Have I tried 2+ solutions and failed? → YES → Escalate (Complexity)
 705   ├─ Is this over 8 turns with no resolution? → YES → Escalate (Complexity)
 706   ├─ Does this require policy exception? → YES → Escalate (Policy)
 707   ├─ Does this require manager approval? → YES → Escalate (Policy)
 708   ├─ Is this a legal/security concern? → YES → Escalate (Safety)
 709   ├─ Is customer VIP? → Consider → Escalate (Priority)
 710   └─ None of the above? → NO → Continue assisting
 711 ```
 712 
 713 **Golden Rule:** When in doubt, escalate. An unnecessary escalation is better than a frustrated customer who gave up.
