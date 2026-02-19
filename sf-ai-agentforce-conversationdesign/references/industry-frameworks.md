<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Industry Frameworks for Agentforce Conversation Design
   2 
   3 This guide maps five leading conversation design frameworks to Salesforce Agentforce implementations. Use these frameworks as lenses to evaluate and improve your agent's conversational quality.
   4 
   5 ---
   6 
   7 ## Framework 1: Google Conversation Design
   8 
   9 **Origin:** Google Assistant design team
  10 **Focus:** Human-centered conversation, cooperative principles, persona development
  11 **Key Resource:** [Google Conversation Design Guide](https://developers.google.com/assistant/conversation-design)
  12 
  13 ### Core Principles
  14 
  15 #### 1. Cooperative Principle (Grice's Maxims)
  16 
  17 Google adapts philosopher Paul Grice's four maxims for conversational AI:
  18 
  19 ##### Maxim of Quantity
  20 **Principle:** Provide the right amount of information—not too much, not too little.
  21 
  22 **Agentforce Application:**
  23 ```yaml
  24 # Topic-Level Instruction Example
  25 Instructions: |
  26   When answering questions, provide 2-3 sentences summarizing the answer.
  27   If the customer needs more detail, offer to expand. Don't dump entire
  28   Knowledge articles—summarize key points and offer "Would you like more details?"
  29 ```
  30 
  31 **Example Violation:**
  32 ```
  33 User: What's your return policy?
  34 
  35 Agent: Our return policy states that all returns must be initiated within
  36        30 days of purchase per Section 4.2 of our Terms of Service, which
  37        was updated on March 15, 2025, to align with federal consumer protection
  38        guidelines established by the FTC in 2024, building on the previous
  39        framework from... [500 more words]
  40 ```
  41 
  42 **Example Adherence:**
  43 ```
  44 User: What's your return policy?
  45 
  46 Agent: You can return items within 30 days of purchase for a full refund.
  47        The item must be unused with original packaging.
  48 
  49        Would you like details on how to start a return?
  50 ```
  51 
  52 ##### Maxim of Quality
  53 **Principle:** Be truthful and evidence-based. Don't guess or hallucinate.
  54 
  55 **Agentforce Application:**
  56 ```yaml
  57 # Agent-Level Instruction Example
  58 Instructions: |
  59   Only provide information you can verify through Knowledge articles, Flow
  60   data, or Apex actions. If you don't know the answer, say "I don't have
  61   that information, but I can connect you with someone who does" rather
  62   than guessing.
  63 
  64   When citing policies or procedures, always reference the Knowledge article ID.
  65 ```
  66 
  67 **Anti-Pattern: Hallucination**
  68 ```
  69 User: Do you offer price matching?
  70 
  71 Agent: Yes, we match any competitor's price within 15 days of purchase!
  72        [WRONG—policy doesn't exist, agent invented it]
  73 ```
  74 
  75 **Correct: Acknowledge Uncertainty**
  76 ```
  77 User: Do you offer price matching?
  78 
  79 Agent: I don't see a price matching policy in our current documentation.
  80        Let me connect you with a sales specialist who can answer that
  81        definitively. Would that work for you?
  82 ```
  83 
  84 ##### Maxim of Relation (Relevance)
  85 **Principle:** Stay on topic. Don't introduce unrelated information.
  86 
  87 **Agentforce Application:**
  88 ```yaml
  89 # Topic-Level Instruction Example
  90 Topic: Password Reset
  91 Instructions: |
  92   Focus exclusively on helping the customer reset their password. Don't
  93   offer information about other account settings, product features, or
  94   promotions unless the customer explicitly asks.
  95 ```
  96 
  97 **Example Violation:**
  98 ```
  99 User: I forgot my password.
 100 
 101 Agent: I can help you reset your password! By the way, did you know we just
 102        launched a new mobile app with biometric login? It's much more secure
 103        than passwords and supports Face ID and fingerprint scanning. You can
 104        download it from... [off-topic tangent]
 105 ```
 106 
 107 **Example Adherence:**
 108 ```
 109 User: I forgot my password.
 110 
 111 Agent: I can help you reset it. What's the email address associated with
 112        your account?
 113 ```
 114 
 115 ##### Maxim of Manner (Clarity)
 116 **Principle:** Be clear, concise, and orderly. Avoid jargon and ambiguity.
 117 
 118 **Agentforce Application:**
 119 ```yaml
 120 # Agent-Level Tone Setting
 121 Tone: Casual
 122 Instructions: |
 123   Use everyday language. Avoid technical jargon unless the customer uses it
 124   first. When providing multi-step instructions, number the steps clearly.
 125 ```
 126 
 127 **Example Violation:**
 128 ```
 129 Agent: To authenticate your identity, we'll need to initiate a verification
 130        protocol via SMS OTP to your registered MSISDN.
 131 ```
 132 
 133 **Example Adherence:**
 134 ```
 135 Agent: To verify your identity, I'll send a code to your phone number.
 136        Let me know when you receive it.
 137 ```
 138 
 139 #### 2. Persona Development
 140 
 141 **Google's Framework:**
 142 - **Professional:** Knowledgeable, formal, authoritative
 143 - **Friendly:** Warm, conversational, empathetic
 144 - **Enthusiastic:** Energetic, motivating, positive
 145 
 146 **Agentforce Mapping:**
 147 
 148 | Google Persona | Agentforce Tone | Use Case |
 149 |----------------|-----------------|----------|
 150 | Professional | Formal | Financial services, healthcare, legal |
 151 | Friendly | Casual | Retail, hospitality, consumer tech |
 152 | Enthusiastic | Casual (with positivity) | Fitness, education, community platforms |
 153 
 154 **Example Configuration:**
 155 ```yaml
 156 Agent Settings:
 157   Tone: Casual
 158   Welcome Message: |
 159     Hey there! I'm here to help with your order, account, or any questions
 160     you have. What can I do for you today?
 161 
 162 Agent-Level Instructions: |
 163   Be conversational and warm, like a helpful friend. Use contractions (I'm,
 164   you're, let's) and casual phrasing. Show empathy when customers are
 165   frustrated. Avoid corporate jargon—say "fix this" not "remediate the issue."
 166 ```
 167 
 168 #### 3. Repair Strategies (Error Handling)
 169 
 170 Google identifies four error types and recovery strategies:
 171 
 172 ##### Error Type 1: No Match
 173 **Problem:** Agent didn't understand the user's input.
 174 
 175 **Google Strategy:** Rapid reprompt with context.
 176 
 177 **Agentforce Implementation:**
 178 ```yaml
 179 Topic: Fallback / Out of Scope
 180 Instructions: |
 181   When you don't understand the request, acknowledge it and offer choices:
 182   "I'm not sure I understood that. Are you looking for help with:
 183    • Order status
 184    • Returns
 185    • Technical support
 186    • Something else
 187   Which is closest to what you need?"
 188 ```
 189 
 190 ##### Error Type 2: Ambiguity
 191 **Problem:** User's intent could match multiple topics.
 192 
 193 **Google Strategy:** Clarify with options.
 194 
 195 **Agentforce Implementation:**
 196 ```
 197 User: I need to change my account.
 198 
 199 Agent: I can help with that! What would you like to change?
 200        • Email address or password
 201        • Billing/payment method
 202        • Shipping address
 203        • Subscription plan
 204 ```
 205 
 206 ##### Error Type 3: System Error
 207 **Problem:** Action failed (API timeout, Flow error).
 208 
 209 **Google Strategy:** Apologize, explain, offer alternative.
 210 
 211 **Agentforce Implementation:**
 212 ```yaml
 213 Action: Create Case (Apex)
 214 Error Handling: |
 215   If this action fails, apologize and offer manual escalation:
 216   "I'm having trouble creating your case in the system right now. Let me
 217   connect you with an agent who can file it manually. This will just take
 218   a moment."
 219 ```
 220 
 221 ##### Error Type 4: Unexpected Input
 222 **Problem:** User provides information in wrong format or context.
 223 
 224 **Google Strategy:** Gentle correction with example.
 225 
 226 **Agentforce Implementation:**
 227 ```
 228 Agent: What's the order number you need help with?
 229 
 230 User: iPhone 15 Pro
 231 
 232 Agent: I'll need the order number to look that up—it's a 8-digit number
 233        like 12345678, usually found in your confirmation email.
 234        Can you find that order number?
 235 ```
 236 
 237 ---
 238 
 239 ## Framework 2: IBM Natural Conversation Framework
 240 
 241 **Origin:** IBM Watson design team
 242 **Focus:** Conversation patterns, state management, intent recognition
 243 **Key Resource:** IBM Watson Assistant documentation
 244 
 245 ### Core Concepts
 246 
 247 #### 1. Five Conversation Patterns
 248 
 249 IBM's patterns map directly to Agentforce implementations (see [conversation-patterns.md](conversation-patterns.md)):
 250 
 251 | IBM Pattern | Agentforce Implementation | Primary Mechanism |
 252 |-------------|---------------------------|-------------------|
 253 | Q&A | Knowledge retrieval, simple lookups | Knowledge actions, Flow queries |
 254 | Information Gathering | Multi-turn data collection | Flow with input variables |
 255 | Process Automation | Guided workflows | Sequential actions with state tracking |
 256 | Troubleshooting | Diagnosis trees | Branching Flow logic |
 257 | Human Handoff | Escalation | Omni-Channel routing |
 258 
 259 **IBM's Key Insight:** Most conversations are combinations of these five patterns, not standalone interactions.
 260 
 261 **Agentforce Application:** Design multi-topic agents where Topic A (Q&A) can transition to Topic B (Information Gathering) based on user response.
 262 
 263 #### 2. Conversation State Management
 264 
 265 **IBM Framework:**
 266 - **Context Variables:** Store data across turns (user inputs, intermediate results)
 267 - **Slots:** Required information to complete an intent
 268 - **Session Variables:** Temporary data cleared after conversation ends
 269 
 270 **Agentforce Equivalent:**
 271 
 272 | IBM Concept | Agentforce Implementation |
 273 |-------------|---------------------------|
 274 | Context Variables | Agentforce maintains turn-by-turn context automatically |
 275 | Slots | Flow Input Variables in Information Gathering actions |
 276 | Session Variables | Flow Variables scoped to conversation session |
 277 
 278 **Example: Multi-Turn State Tracking**
 279 ```yaml
 280 Flow: Collect Case Details
 281 Variables:
 282   - Subject (Text)
 283   - Description (Text)
 284   - Priority (Picklist)
 285   - ProductId (Text)
 286   - HasSubject (Boolean)
 287   - HasDescription (Boolean)
 288 
 289 Decision: What to Ask Next
 290   - If HasSubject = False → Ask for Subject
 291   - If HasDescription = False → Ask for Description
 292   - If Priority = null → Ask for Priority
 293   - If all required filled → Create Case
 294 ```
 295 
 296 #### 3. Intent Confidence Thresholds
 297 
 298 **IBM Recommendation:**
 299 - **High confidence (>0.8):** Execute action immediately
 300 - **Medium confidence (0.5-0.8):** Confirm with user before executing
 301 - **Low confidence (<0.5):** Clarify intent
 302 
 303 **Agentforce Application:**
 304 
 305 Agentforce doesn't expose confidence scores directly, but you can implement confirmation patterns:
 306 
 307 ```yaml
 308 Topic: Delete Account
 309 Instructions: |
 310   This is a high-impact action. Before proceeding, always confirm:
 311   "Just to confirm—you want to permanently delete your account and all
 312   associated data? This cannot be undone. Type YES to confirm."
 313 
 314   Only execute the deletion if the customer explicitly types YES.
 315 ```
 316 
 317 #### 4. Digression Handling
 318 
 319 **IBM Framework:** Allow users to digress (go off-topic mid-conversation), then return to original topic.
 320 
 321 **Example Digression:**
 322 ```
 323 Agent: What's your order number? [Information Gathering for refund]
 324 
 325 User: Actually, quick question—do you ship to Canada? [Digression to Q&A]
 326 
 327 Agent: Yes, we ship to Canada! Shipping takes 5-7 business days.
 328 
 329        Now, back to your refund—what's the order number? [Return to original topic]
 330 ```
 331 
 332 **Agentforce Implementation:**
 333 
 334 Agentforce handles topic switching automatically via classification. To preserve context across digression:
 335 
 336 ```yaml
 337 Agent-Level Instructions: |
 338   If the customer asks an unrelated question mid-conversation, answer it
 339   briefly, then return to the task at hand. For example:
 340 
 341   "Yes, we ship internationally! Now, to process your refund, what's the
 342   order number?"
 343 
 344   This keeps the conversation moving forward without ignoring the customer.
 345 ```
 346 
 347 ---
 348 
 349 ## Framework 3: PatternFly AI Design System
 350 
 351 **Origin:** Red Hat's open-source design system
 352 **Focus:** Enterprise AI UX patterns, transparency, ethical AI
 353 **Key Resource:** [PatternFly AI Design Guidelines](https://www.patternfly.org/ai)
 354 
 355 ### Core Principles for Enterprise AI
 356 
 357 #### 1. Transparency & Explainability
 358 
 359 **Principle:** Users should understand when they're talking to AI, what the AI can/can't do, and how decisions are made.
 360 
 361 **Agentforce Application:**
 362 
 363 ```yaml
 364 Welcome Message (Agent Settings):
 365   Hi! I'm an AI assistant trained to help with orders, returns, and account
 366   questions. I can answer most questions instantly, but I'll connect you with
 367   a specialist for complex issues.
 368 
 369   What can I help you with today?
 370 
 371 Agent-Level Instructions: |
 372   When you use data to make a recommendation, cite the source. For example:
 373   "Based on your order history, I recommend Product X" or "According to our
 374   return policy (Article KB-12345), you're eligible for a full refund."
 375 ```
 376 
 377 **Anti-Pattern: Hidden AI**
 378 ```
 379 ❌ Don't pretend to be human:
 380    "Hi, I'm Sarah from Customer Service!"
 381 
 382 ✅ Be transparent:
 383    "Hi! I'm an AI assistant here to help with your order."
 384 ```
 385 
 386 #### 2. Feedback Loops
 387 
 388 **Principle:** Allow users to correct the AI and provide feedback.
 389 
 390 **Agentforce Application:**
 391 
 392 ```yaml
 393 Agent-Level Instructions: |
 394   After providing an answer or completing an action, ask:
 395   "Did that answer your question?" or "Is there anything else I can help with?"
 396 
 397   If the customer says your answer was wrong or unhelpful, apologize and
 398   offer escalation: "I'm sorry that wasn't helpful. Let me connect you with
 399   a specialist who can assist."
 400 ```
 401 
 402 **Pattern: Thumbs Up/Down**
 403 
 404 While Agentforce doesn't have built-in thumbs up/down UI, you can implement feedback via:
 405 - **Post-Chat Survey:** Triggered via Flow after conversation ends
 406 - **Explicit Feedback Prompt:** "Was this helpful? Reply YES or NO."
 407 
 408 #### 3. Progressive Disclosure
 409 
 410 **Principle:** Show information incrementally—don't overwhelm users upfront.
 411 
 412 **Agentforce Application:**
 413 
 414 ```yaml
 415 # BAD: Information Overload
 416 Agent: Our return policy allows returns within 30 days of purchase with original
 417        packaging and receipt. Items must be unused. Electronics have a 15-day
 418        window. Refunds are processed in 5-7 days. We don't accept returns on
 419        personalized items. You can initiate returns online or mail them to...
 420        [200 more words]
 421 
 422 # GOOD: Progressive Disclosure
 423 Agent: You can return items within 30 days for a full refund.
 424 
 425        Would you like to:
 426        • Start a return now
 427        • See the full return policy
 428        • Ask a specific question about returns
 429 ```
 430 
 431 #### 4. Error Prevention & Recovery
 432 
 433 **Principle:** Design guardrails to prevent errors, and provide clear recovery paths when errors occur.
 434 
 435 **Agentforce Application:**
 436 
 437 **Prevention via Validation:**
 438 ```yaml
 439 Action: Update Email Address
 440 Action-Level Instructions: |
 441   Before updating the email, validate the format. If the customer provides
 442   an invalid email (missing @, no domain), respond:
 443   "That doesn't look like a valid email address. Email addresses look like
 444   name@example.com. Can you double-check and provide it again?"
 445 ```
 446 
 447 **Recovery via Undo:**
 448 ```yaml
 449 Topic: Cancel Subscription
 450 Instructions: |
 451   After canceling, inform the customer: "Your subscription has been canceled.
 452   If you change your mind, you can reactivate it within 30 days by contacting
 453   support—no penalties."
 454 ```
 455 
 456 #### 5. Loading States & Wait Time Communication
 457 
 458 **Principle:** Set expectations when the AI is processing.
 459 
 460 **Agentforce Application:**
 461 
 462 For long-running actions (Apex callouts, complex Flows):
 463 
 464 ```yaml
 465 Action: Run Credit Check (Apex)
 466 Action-Level Instructions: |
 467   This action takes 10-15 seconds. Before calling it, tell the customer:
 468   "Let me run a quick credit check—this will take about 15 seconds."
 469 
 470   This prevents the customer from thinking the agent is frozen.
 471 ```
 472 
 473 **Pattern: Acknowledge Before Acting**
 474 ```
 475 Agent: Let me look up your order details... [acknowledge, then act]
 476        [5 second pause while Flow runs]
 477        Here's what I found: Order #12345, shipped on Jan 15th.
 478 ```
 479 
 480 ---
 481 
 482 ## Framework 4: Salesforce Conversational AI Guide
 483 
 484 **Origin:** Salesforce CX design team
 485 **Focus:** Brand voice, Einstein-specific patterns, accessibility
 486 **Key Resource:** Salesforce Help (search "Conversational AI Best Practices")
 487 
 488 ### Core Principles
 489 
 490 #### 1. Brand Voice Consistency
 491 
 492 **Principle:** Your agent should sound like your brand across all channels (chat, email, phone, social).
 493 
 494 **Agentforce Application:**
 495 
 496 Define brand voice in a style guide, then encode in Agent-Level Instructions:
 497 
 498 **Example: Casual Tech Brand**
 499 ```yaml
 500 Agent-Level Instructions: |
 501   Our brand voice is friendly, approachable, and knowledgeable. Use:
 502   - Contractions (I'm, you're, let's)
 503   - Conversational transitions (Got it, Perfect, No problem)
 504   - Emoji sparingly (only for empathy: "I'm sorry 😔" or celebration: "All set! 🎉")
 505 
 506   Avoid:
 507   - Corporate jargon (leverage, utilize, facilitate)
 508   - Robotic phrasing (Your request has been processed)
 509   - Excessive formality (Dear Valued Customer)
 510 ```
 511 
 512 **Example: Formal Financial Brand**
 513 ```yaml
 514 Agent-Level Instructions: |
 515   Our brand voice is professional, trustworthy, and precise. Use:
 516   - Complete sentences (no contractions)
 517   - Formal transitions (Certainly, I understand, Thank you for confirming)
 518   - No emoji
 519 
 520   Avoid:
 521   - Slang or colloquialisms (sure thing, no worries)
 522   - Overly casual phrasing (Hey! What's up?)
 523   - Humor (this is sensitive financial data)
 524 ```
 525 
 526 #### 2. LLM Prompt Consistency
 527 
 528 **Principle:** Instructions should use consistent phrasing to ensure predictable LLM behavior.
 529 
 530 **Agentforce Application:**
 531 
 532 **Anti-Pattern: Conflicting Instructions**
 533 ```yaml
 534 Agent-Level: |
 535   Always provide detailed explanations for your recommendations.
 536 
 537 Topic-Level: |
 538   Keep responses under 2 sentences.
 539 ```
 540 
 541 **Best Practice: Hierarchical Clarity**
 542 ```yaml
 543 Agent-Level: |
 544   Provide concise responses (2-3 sentences) unless the customer asks for
 545   more detail.
 546 
 547 Topic-Level (Technical Support): |
 548   For troubleshooting steps, provide numbered instructions. You can exceed
 549   3 sentences when walking through multi-step solutions.
 550 ```
 551 
 552 #### 3. Accessibility (WCAG Compliance)
 553 
 554 **Principle:** Conversations should be accessible to users with disabilities.
 555 
 556 **Agentforce Application:**
 557 
 558 | Accessibility Need | Design Pattern |
 559 |--------------------|----------------|
 560 | **Screen Reader Users** | Avoid relying on formatting (bold, italics) to convey meaning. Say "IMPORTANT:" instead of just using bold. |
 561 | **Cognitive Disabilities** | Use simple language, short sentences, bullet points for lists. |
 562 | **Visual Impairments** | Don't use color alone to convey info ("click the red button" → "click the Cancel button") |
 563 | **Motor Impairments** | Offer button-based choices, not just free-text input. |
 564 
 565 **Example: Button-Based Choices**
 566 ```yaml
 567 Agent: What would you like help with today?
 568        [Order Status] [Returns] [Technical Support] [Talk to a Person]
 569 
 570        # Instead of forcing free-text input, provide clickable options
 571 ```
 572 
 573 In Agentforce, you can implement this via:
 574 - **Quick Reply Buttons:** Configured in Chat Settings (Embedded Service)
 575 - **Prompt Text:** "Reply 1 for Order Status, 2 for Returns, 3 for Technical Support"
 576 
 577 ---
 578 
 579 ## Framework 5: Salesforce Architect Agentic Patterns
 580 
 581 **Origin:** Salesforce Architect team
 582 **Focus:** Agent taxonomy, multi-agent systems, orchestration
 583 **Key Resource:** Architect Blog, Dreamforce '25 sessions
 584 
 585 ### Agent Taxonomy
 586 
 587 Salesforce defines five agentic patterns based on autonomy and collaboration:
 588 
 589 #### 1. Conversational Agents (Agentforce)
 590 
 591 **Definition:** React to user input in real-time via chat/voice.
 592 
 593 **Characteristics:**
 594 - User-initiated
 595 - Turn-by-turn interaction
 596 - Context-aware within session
 597 - Scoped to specific domains (Topics)
 598 
 599 **Agentforce Implementation:** This is the default Agentforce pattern.
 600 
 601 **Use Cases:**
 602 - Customer support chatbots
 603 - IT helpdesk assistants
 604 - Sales qualification bots
 605 
 606 #### 2. Proactive Agents
 607 
 608 **Definition:** Initiate conversations based on triggers (e.g., abandoned cart, case SLA breach).
 609 
 610 **Characteristics:**
 611 - System-initiated
 612 - Event-driven
 613 - Outbound messaging (email, SMS, push notification)
 614 
 615 **Agentforce Implementation:**
 616 - **Trigger:** Flow triggered by Platform Event or Scheduled Job
 617 - **Action:** Flow sends message via SMS (Twilio) or Email
 618 - **Handoff:** If customer responds, route to conversational Agentforce agent
 619 
 620 **Example Flow:**
 621 ```
 622 Trigger: Case.Age > 48 hours AND Status = 'Open'
 623 Action: Send SMS to customer: "Your support case hasn't been resolved yet.
 624         Reply YES to chat with an agent now."
 625 If Response = YES: Route to Agentforce agent with case context
 626 ```
 627 
 628 #### 3. Ambient Agents
 629 
 630 **Definition:** Observe user activity and provide suggestions without blocking workflow.
 631 
 632 **Characteristics:**
 633 - Non-intrusive
 634 - Recommendation-based
 635 - Integrated into UI (Einstein for Sales, Einstein Activity Capture)
 636 
 637 **Agentforce Implementation:**
 638 - **Not native to Agentforce** (Agentforce is conversational)
 639 - **Alternative:** Einstein Next Best Action in Salesforce UI
 640 
 641 **Example (Outside Agentforce):**
 642 - Sales rep views Account record → Einstein suggests "This customer is at risk of churn. Recommend scheduling a check-in call."
 643 
 644 #### 4. Autonomous Agents
 645 
 646 **Definition:** Execute multi-step tasks without human approval (within defined guardrails).
 647 
 648 **Characteristics:**
 649 - Long-running workflows
 650 - Multi-action execution
 651 - Operates asynchronously
 652 
 653 **Agentforce Implementation:**
 654 - **Example:** Agent automatically resolves cases when conditions are met
 655   - Trigger: Case with Type = 'Password Reset' AND Email Sent = True
 656   - Action: Wait 24 hours → If no customer response, auto-close case with note
 657   - No human approval needed (within policy)
 658 
 659 **Guardrails Required:**
 660 - Limit to low-risk actions (auto-close cases, send reminders, update fields)
 661 - Never autonomous for high-risk actions (delete data, issue refunds over $X)
 662 
 663 #### 5. Collaborative Agents (Multi-Agent Systems)
 664 
 665 **Definition:** Multiple specialized agents working together, each handling a domain.
 666 
 667 **Characteristics:**
 668 - Agent-to-agent handoff
 669 - Orchestration layer
 670 - Shared context
 671 
 672 **Agentforce Implementation:**
 673 
 674 **Pattern: Domain-Specific Agents**
 675 - **Agent 1:** Pre-Sales (lead qualification, product info)
 676 - **Agent 2:** Order Support (order status, shipping, returns)
 677 - **Agent 3:** Technical Support (troubleshooting, bug reports)
 678 
 679 **Orchestration:**
 680 - **Master Agent:** Routes to specialist agent based on user intent
 681 - **Context Passing:** When Agent 1 hands off to Agent 2, pass conversation summary + key IDs
 682 
 683 **Implementation:**
 684 ```yaml
 685 Master Agent: "Customer Service Hub"
 686   Topic: Route to Specialist
 687     Instructions: |
 688       Determine which specialist the customer needs:
 689       - Pre-sales questions → Transfer to "Sales Agent"
 690       - Order/shipping issues → Transfer to "Order Agent"
 691       - Technical problems → Transfer to "Tech Support Agent"
 692 
 693       Use the Handoff action to transfer, passing the conversation summary.
 694 ```
 695 
 696 ---
 697 
 698 ## Framework Comparison Matrix
 699 
 700 | Framework | Primary Focus | Best Used For | Agentforce Strength |
 701 |-----------|---------------|---------------|---------------------|
 702 | **Google Conversation Design** | Human-centered principles, persona | Defining agent personality, error handling | Agent-level instructions, tone settings |
 703 | **IBM Natural Conversation** | Patterns, state management | Multi-turn flows, slot filling | Flow variables, topic transitions |
 704 | **PatternFly AI** | Enterprise UX, transparency, ethics | Trust-building, accessibility | Welcome messages, feedback loops |
 705 | **Salesforce Conversational AI** | Brand consistency, LLM prompts | Instruction writing, cross-channel voice | Instruction hierarchy, brand voice guide |
 706 | **Salesforce Architect Agentic** | Agent taxonomy, orchestration | Multi-agent systems, autonomy levels | Handoff mechanisms, agent specialization |
 707 
 708 ---
 709 
 710 ## Applying Multiple Frameworks
 711 
 712 Real-world Agentforce agents should blend frameworks:
 713 
 714 ### Example: E-Commerce Support Agent
 715 
 716 | Design Decision | Framework Applied | Agentforce Configuration |
 717 |-----------------|-------------------|--------------------------|
 718 | **Persona: Friendly helper** | Google (Persona) | Tone: Casual, conversational instructions |
 719 | **Pattern: Information Gathering for returns** | IBM (Patterns) | Flow with input variables for return request |
 720 | **Transparency: "I'm an AI assistant"** | PatternFly (Transparency) | Welcome message disclosure |
 721 | **Brand voice: Match website tone** | Salesforce Conv AI (Brand) | Style guide encoded in agent instructions |
 722 | **Handoff to human for refunds >$500** | Salesforce Architect (Autonomy) | Escalation topic with Omni-Channel routing |
 723 
 724 ---
 725 
 726 ## Summary: Framework Integration Checklist
 727 
 728 When designing an Agentforce agent, validate against all five frameworks:
 729 
 730 - [ ] **Google:** Does my agent follow the four maxims (Quantity, Quality, Relation, Manner)?
 731 - [ ] **Google:** Have I defined a clear persona and error recovery strategies?
 732 - [ ] **IBM:** Have I mapped conversation patterns and implemented state management?
 733 - [ ] **PatternFly:** Is my agent transparent about being AI? Do I have feedback loops?
 734 - [ ] **Salesforce Conv AI:** Is my brand voice consistent across all instructions?
 735 - [ ] **Salesforce Architect:** Have I scoped autonomy appropriately and defined handoff points?
 736 
 737 If you answer "no" to any question, revisit your design using that framework's principles.
