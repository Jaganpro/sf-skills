<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Anti-Patterns in Agentforce Conversation Design
   2 
   3 This guide catalogs common mistakes in conversation design with concrete examples and solutions. Learn from these anti-patterns to build better Agentforce agents.
   4 
   5 ---
   6 
   7 ## Category 1: Instruction Design Anti-Patterns
   8 
   9 ### Anti-Pattern 1.1: Over-Constraining with Absolute Language
  10 
  11 **The Problem:** Using "must", "always", "never" in instructions creates brittle behavior that fails in edge cases.
  12 
  13 #### ❌ BAD: Absolute Constraint
  14 ```yaml
  15 Topic: Order Status
  16 Instructions: |
  17   You must always ask for the order number before looking up an order.
  18   Never proceed without the order number.
  19 ```
  20 
  21 **Why It's Bad:**
  22 - Customer might say "What's the status of my order #12345?" — already provided order number
  23 - Agent will re-ask unnecessarily, frustrating user
  24 - LLM interprets "must" and "never" rigidly, ignoring context
  25 
  26 #### ✅ GOOD: Context-Aware Guidance
  27 ```yaml
  28 Topic: Order Status
  29 Instructions: |
  30   To look up an order, you need the order number. If the customer hasn't
  31   provided it yet, ask for it: "What's your order number? It's an 8-digit
  32   number found in your confirmation email."
  33 
  34   If the customer already mentioned the order number earlier in the
  35   conversation, use that—don't re-ask.
  36 ```
  37 
  38 **Fix Applied:**
  39 - Uses "you need" (requirement) without "must" (rigid command)
  40 - Explicitly handles case where info is already provided
  41 - Trusts LLM to track conversational context
  42 
  43 ---
  44 
  45 ### Anti-Pattern 1.2: Negative Framing
  46 
  47 **The Problem:** Telling the agent what NOT to do is less effective than telling it what TO do.
  48 
  49 #### ❌ BAD: Negative Instructions
  50 ```yaml
  51 Agent-Level Instructions: |
  52   Don't ask for the customer's credit card number.
  53   Don't make promises about shipping dates you can't verify.
  54   Don't provide legal or medical advice.
  55   Don't be rude or dismissive.
  56 ```
  57 
  58 **Why It's Bad:**
  59 - LLMs are better at following positive instructions than avoiding negatives
  60 - Doesn't provide alternative behavior (what SHOULD the agent do?)
  61 - Creates ambiguity ("if I don't ask for credit card, how do I verify payment?")
  62 
  63 #### ✅ GOOD: Positive Instructions
  64 ```yaml
  65 Agent-Level Instructions: |
  66   To verify payment information, guide the customer to their account settings
  67   where they can see the last 4 digits of their card on file. Never ask them
  68   to share the full card number in chat.
  69 
  70   For shipping dates, only provide estimates from the Order record's
  71   Estimated_Delivery__c field. If that field is empty, say "I don't have an
  72   estimated delivery date yet, but I can connect you with shipping support
  73   for an update."
  74 
  75   For questions about legal contracts or medical conditions, respond:
  76   "I'm not able to provide legal/medical advice, but I can connect you with
  77   a specialist who can help. Would that work for you?"
  78 
  79   When customers are frustrated, acknowledge their feelings: "I understand
  80   this has been frustrating" and offer solutions or escalation.
  81 ```
  82 
  83 **Fix Applied:**
  84 - Each "don't" is replaced with a "do" (what to do instead)
  85 - Provides specific alternatives and phrasing
  86 - Actionable instructions that guide behavior
  87 
  88 ---
  89 
  90 ### Anti-Pattern 1.3: Business Rules in Instructions
  91 
  92 **The Problem:** Encoding complex business logic (calculations, validations, conditional rules) in natural language instructions instead of Flow/Apex.
  93 
  94 #### ❌ BAD: Business Logic in Instructions
  95 ```yaml
  96 Topic: Refund Request
  97 Instructions: |
  98   Customers are eligible for refunds if:
  99   - Order was placed within 30 days
 100   - Order status is "Delivered" or "In Transit"
 101   - Order total is under $500
 102   - Customer is not on the restricted list
 103   - Product category is not "Personalized" or "Digital"
 104 
 105   Calculate the refund amount as: (Order Total - Shipping) * 0.95 if the
 106   customer used a discount code, otherwise Order Total - Shipping.
 107 ```
 108 
 109 **Why It's Bad:**
 110 - LLMs can misinterpret complex conditionals
 111 - Business rules change over time — updating instructions is error-prone
 112 - No guarantee of accurate calculations
 113 - Can't enforce hard constraints (e.g., prevent refund if ineligible)
 114 
 115 #### ✅ GOOD: Flow for Business Rules
 116 ```yaml
 117 Topic: Refund Request
 118 Instructions: |
 119   To process a refund, use the "Check Refund Eligibility" action, which
 120   requires the Order ID. This action will determine if the customer is
 121   eligible and calculate the refund amount.
 122 
 123   If eligible, confirm the amount with the customer and use the "Issue Refund"
 124   action. If not eligible, explain the reason provided by the action and
 125   offer to escalate if they have special circumstances.
 126 ```
 127 
 128 ```yaml
 129 Flow: Check Refund Eligibility
 130 Inputs:
 131   - OrderId (Text)
 132 Outputs:
 133   - IsEligible (Boolean)
 134   - RefundAmount (Currency)
 135   - IneligibilityReason (Text)
 136 
 137 Logic:
 138   1. Query Order with OrderId
 139   2. Get Account.Restricted__c, Order.CreatedDate, Order.Status, Order.Total_Amount__c,
 140      OrderItems.Product2.Category__c
 141   3. Decision: Eligibility Check
 142      - If (TODAY() - Order.CreatedDate) > 30 → IneligibilityReason = "Order is more than 30 days old"
 143      - If Order.Status NOT IN ('Delivered', 'In Transit') → IneligibilityReason = "Order not yet delivered"
 144      - If Order.Total_Amount__c > 500 → IneligibilityReason = "Orders over $500 require manager approval"
 145      - If Account.Restricted__c = True → IneligibilityReason = "Account restricted"
 146      - If Product2.Category__c IN ('Personalized', 'Digital') → IneligibilityReason = "Category not eligible"
 147   4. Formula: RefundAmount = IF(Order.Discount_Code__c != null,
 148                                  (Order.Total_Amount__c - Order.Shipping_Cost__c) * 0.95,
 149                                  Order.Total_Amount__c - Order.Shipping_Cost__c)
 150   5. Return: IsEligible, RefundAmount, IneligibilityReason
 151 ```
 152 
 153 **Fix Applied:**
 154 - Deterministic logic in Flow (accurate, testable, maintainable)
 155 - Instructions focus on WHEN to call the action and HOW to interpret results
 156 - Clear separation: LLM handles conversation, Flow handles rules
 157 
 158 ---
 159 
 160 ### Anti-Pattern 1.4: Format Validation in Instructions
 161 
 162 **The Problem:** Asking the LLM to validate email addresses, phone numbers, or other formats.
 163 
 164 #### ❌ BAD: LLM Format Validation
 165 ```yaml
 166 Topic: Update Contact Info
 167 Instructions: |
 168   When the customer provides an email address, verify it has an @ symbol
 169   and a domain (like .com or .org). If it doesn't, ask them to provide a
 170   valid email.
 171 
 172   For phone numbers, make sure they're in the format (XXX) XXX-XXXX and
 173   have exactly 10 digits. If not, ask them to reformat it.
 174 ```
 175 
 176 **Why It's Bad:**
 177 - LLMs are unreliable at pattern matching (they may accept invalid formats)
 178 - Users provide formats in many valid ways: "+1-555-123-4567", "555.123.4567"
 179 - Wastes tokens on a task better suited for regex
 180 
 181 #### ✅ GOOD: Flow/Apex Validation
 182 ```yaml
 183 Topic: Update Contact Info
 184 Instructions: |
 185   Ask the customer for their new email address or phone number. Once provided,
 186   use the "Validate and Update Contact" action. If the action returns an error
 187   (invalid format), explain the issue and ask for a corrected value.
 188 ```
 189 
 190 ```apex
 191 // Apex Action: Validate and Update Contact
 192 @InvocableMethod(label='Validate and Update Contact')
 193 public static List<Result> validateAndUpdate(List<Request> requests) {
 194     Request req = requests[0];
 195     Result res = new Result();
 196 
 197     // Email validation
 198     if (String.isNotBlank(req.email)) {
 199         Pattern emailPattern = Pattern.compile('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$');
 200         if (!emailPattern.matcher(req.email).matches()) {
 201             res.success = false;
 202             res.errorMessage = 'Invalid email format. Please provide a valid email like name@example.com';
 203             return new List<Result>{ res };
 204         }
 205     }
 206 
 207     // Phone validation (E.164 or 10-digit US)
 208     if (String.isNotBlank(req.phone)) {
 209         String cleaned = req.phone.replaceAll('[^0-9]', '');
 210         if (cleaned.length() != 10 && cleaned.length() != 11) {
 211             res.success = false;
 212             res.errorMessage = 'Invalid phone format. Please provide a 10-digit phone number';
 213             return new List<Result>{ res };
 214         }
 215         req.phone = cleaned; // Normalize
 216     }
 217 
 218     // Update Contact
 219     Contact contact = [SELECT Id FROM Contact WHERE Id = :req.contactId];
 220     if (String.isNotBlank(req.email)) contact.Email = req.email;
 221     if (String.isNotBlank(req.phone)) contact.Phone = req.phone;
 222     update contact;
 223 
 224     res.success = true;
 225     return new List<Result>{ res };
 226 }
 227 ```
 228 
 229 **Fix Applied:**
 230 - Deterministic regex validation in Apex
 231 - Agent instructions focus on conversation flow, not validation logic
 232 - Normalization (removing dashes, parentheses) handled in code
 233 
 234 ---
 235 
 236 ## Category 2: Topic Architecture Anti-Patterns
 237 
 238 ### Anti-Pattern 2.1: Monolithic Topics
 239 
 240 **The Problem:** Cramming too many actions into a single topic.
 241 
 242 #### ❌ BAD: One Topic for Everything
 243 ```yaml
 244 Topic: Customer Service
 245 Classification Description: |
 246   Customer needs help with orders, returns, account issues, technical support,
 247   product questions, billing, or anything else.
 248 
 249 Actions (20+ actions):
 250   - Check Order Status
 251   - Cancel Order
 252   - Modify Order
 253   - Initiate Return
 254   - Check Return Status
 255   - Update Email
 256   - Reset Password
 257   - Get Product Info
 258   - Search Knowledge Base
 259   - Create Case
 260   - Escalate to Agent
 261   - Process Refund
 262   - Update Billing
 263   - Check Inventory
 264   ... (6 more)
 265 ```
 266 
 267 **Why It's Bad:**
 268 - Topic classification becomes too broad (everything matches)
 269 - LLM struggles to choose the right action from 20+ options
 270 - Maintenance nightmare (changes to one action risk affecting others)
 271 - Can't optimize instructions for specific workflows
 272 
 273 #### ✅ GOOD: Focused Topics
 274 ```yaml
 275 Topic: Order Management
 276 Classification Description: |
 277   Customer needs help with an existing order—checking status, modifying,
 278   or canceling. Includes questions like "Where's my order?", "Cancel my order",
 279   "Change my shipping address".
 280 
 281 Scope: Actions on existing orders (read/update/cancel)
 282 
 283 Actions (5 actions):
 284   - Check Order Status
 285   - Cancel Order
 286   - Modify Order Address
 287   - Expedite Shipping
 288   - Escalate Order Issue
 289 ```
 290 
 291 ```yaml
 292 Topic: Returns and Refunds
 293 Classification Description: |
 294   Customer wants to return a product or request a refund. Includes phrases
 295   like "I want to return this", "Start a return", "Get a refund", "Return policy".
 296 
 297 Scope: Initiating returns, checking return status, processing refunds
 298 
 299 Actions (4 actions):
 300   - Check Return Eligibility
 301   - Initiate Return
 302   - Check Return Status
 303   - Issue Refund
 304 ```
 305 
 306 ```yaml
 307 Topic: Account Settings
 308 Classification Description: |
 309   Customer wants to update account information—email, password, phone, address.
 310   Includes "Change my email", "Reset password", "Update my profile".
 311 
 312 Scope: Account credential and profile updates
 313 
 314 Actions (4 actions):
 315   - Update Email
 316   - Reset Password
 317   - Update Phone
 318   - Update Shipping Address
 319 ```
 320 
 321 **Fix Applied:**
 322 - 20 actions → 3 topics with 4-5 actions each
 323 - Each topic has clear scope and focused classification description
 324 - Instructions can be topic-specific (e.g., Returns requires empathy, Order Management requires urgency)
 325 
 326 **Guideline:** Keep topics to **5-7 actions maximum**. If you need more, split into multiple topics.
 327 
 328 ---
 329 
 330 ### Anti-Pattern 2.2: Overlapping Topic Classification Descriptions
 331 
 332 **The Problem:** Two topics have similar classification descriptions, causing misrouting.
 333 
 334 #### ❌ BAD: Ambiguous Overlap
 335 ```yaml
 336 Topic A: Technical Support
 337 Classification Description: |
 338   Customer is experiencing problems with the product or app. Includes issues
 339   like crashes, errors, performance problems, or features not working.
 340 
 341 Topic B: Product Help
 342 Classification Description: |
 343   Customer has questions about how the product works, how to use features,
 344   or needs help with setup.
 345 ```
 346 
 347 **Overlap Example:**
 348 ```
 349 User: "The app isn't syncing my data."
 350 
 351 Is this Topic A (problem = technical support) or Topic B (how to use sync = product help)?
 352 ```
 353 
 354 **Why It's Bad:**
 355 - Ambiguity causes misclassification
 356 - User gets routed to wrong topic, needs re-routing (bad UX)
 357 - Similar keywords in both descriptions confuse the classifier
 358 
 359 #### ✅ GOOD: Clear Boundaries
 360 ```yaml
 361 Topic A: Technical Support
 362 Classification Description: |
 363   Customer reports an error, crash, bug, or unexpected behavior—something that
 364   should work but doesn't. Includes phrases like "keeps crashing", "error message",
 365   "broken", "not working", "stopped working".
 366 
 367 Scope: Diagnosing and fixing malfunctions, not expected behavior.
 368 
 369 Topic B: Feature Education
 370 Classification Description: |
 371   Customer asks how to use a feature, configure settings, or accomplish a task
 372   they haven't done before. Includes "How do I...", "Where is the setting for...",
 373   "Show me how to...".
 374 
 375 Scope: Teaching expected functionality, not troubleshooting errors.
 376 ```
 377 
 378 **Disambiguation:**
 379 ```
 380 User: "The app isn't syncing my data."
 381 
 382 Topic A matches ("not working" = malfunction → Technical Support)
 383 
 384 vs.
 385 
 386 User: "How do I sync my data?"
 387 
 388 Topic B matches ("How do I" = learning task → Feature Education)
 389 ```
 390 
 391 **Fix Applied:**
 392 - Topic A = things that SHOULD work but DON'T (errors, bugs)
 393 - Topic B = things that DO work, user needs to learn HOW (education)
 394 - Clear keyword distinctions: "error", "crash", "broken" vs. "how do I", "where is", "show me"
 395 
 396 ---
 397 
 398 ### Anti-Pattern 2.3: Missing Escalation Paths
 399 
 400 **The Problem:** No clear path to human agent when AI can't resolve the issue.
 401 
 402 #### ❌ BAD: Dead-End Conversation
 403 ```
 404 User: I've tried resetting my password 3 times and it's still not working.
 405 
 406 Agent: Let me help you reset your password. What's your email address?
 407 
 408 User: I already did this! It's not working!
 409 
 410 Agent: I can send you another reset link. What's your email?
 411 
 412 User: [gives up and leaves]
 413 ```
 414 
 415 **Why It's Bad:**
 416 - Agent stuck in loop, repeating same solution
 417 - No recognition of repeated failure
 418 - User frustration increases, no human fallback
 419 
 420 #### ✅ GOOD: Escalation After N Failures
 421 ```yaml
 422 Topic: Password Reset
 423 Instructions: |
 424   Guide the user through password reset. If the user indicates they've already
 425   tried resetting and it didn't work, or if you've sent 2 reset links and the
 426   issue persists, escalate to technical support:
 427 
 428   "It sounds like there might be a deeper issue with your account. Let me
 429   connect you with a technical specialist who can investigate. They'll have
 430   all the details from our conversation."
 431 
 432   Use the Escalate to Support action to route them to Omni-Channel.
 433 ```
 434 
 435 **Example Conversation:**
 436 ```
 437 User: I've tried resetting my password 3 times and it's still not working.
 438 
 439 Agent: I'm sorry the reset links haven't worked. This sounds like it might be
 440        a deeper issue with your account setup.
 441 
 442        Let me connect you with a technical specialist who can investigate and
 443        resolve this right away. They'll have all the details from our chat.
 444 
 445        [Escalation triggered]
 446 ```
 447 
 448 **Fix Applied:**
 449 - Instructions explicitly define failure condition (2 attempts)
 450 - Escalation is automatic after threshold
 451 - Agent acknowledges frustration and sets expectation
 452 
 453 ---
 454 
 455 ## Category 3: Context and Memory Anti-Patterns
 456 
 457 ### Anti-Pattern 3.1: Ignoring Context Carryover
 458 
 459 **The Problem:** Not referencing information the user provided in earlier turns.
 460 
 461 #### ❌ BAD: Redundant Questions
 462 ```
 463 User: I need to return my order. The order number is 12345678 and my email is
 464       john@example.com.
 465 
 466 Agent: I can help with that! What's your order number?
 467 
 468 User: I just told you, 12345678.
 469 
 470 Agent: Thank you. And what's your email address?
 471 
 472 User: [frustrated] john@example.com, I already said that!
 473 ```
 474 
 475 **Why It's Bad:**
 476 - User explicitly provided both pieces of info in first message
 477 - Agent re-asks both, wasting time and frustrating user
 478 - Makes agent seem "dumb" and non-conversational
 479 
 480 #### ✅ GOOD: Context-Aware Response
 481 ```yaml
 482 Topic: Returns
 483 Instructions: |
 484   To process a return, you need the order number and the customer's email.
 485   Check the conversation history—if the customer already provided these, use
 486   them. Don't re-ask for information the customer has already given.
 487 
 488   Acknowledge what they've provided: "Got it, I have your order number (12345678)
 489   and email (john@example.com). Let me look up your order..."
 490 ```
 491 
 492 **Example Conversation:**
 493 ```
 494 User: I need to return my order. The order number is 12345678 and my email is
 495       john@example.com.
 496 
 497 Agent: Got it! I have your order number (12345678) and email (john@example.com).
 498        Let me pull up your order details...
 499 
 500        [Agent retrieves order]
 501 
 502        I see your order for [Product Name], delivered on Jan 10th. What's the
 503        reason for the return?
 504 ```
 505 
 506 **Fix Applied:**
 507 - Instructions remind agent to check conversation history
 508 - Agent acknowledges received info (builds trust)
 509 - Only asks for missing information
 510 
 511 ---
 512 
 513 ### Anti-Pattern 3.2: Hard-Coding Responses Instead of Using Knowledge
 514 
 515 **The Problem:** Writing specific answers in instructions instead of retrieving from Knowledge articles.
 516 
 517 #### ❌ BAD: Hard-Coded Answer
 518 ```yaml
 519 Topic: Shipping FAQs
 520 Instructions: |
 521   If the customer asks about shipping costs, respond:
 522   "Standard shipping is free for orders over $50. Express shipping is $9.99.
 523   International shipping costs vary by country—Canada is $15, UK is $20,
 524   Australia is $25."
 525 ```
 526 
 527 **Why It's Bad:**
 528 - Shipping costs change → instructions become stale
 529 - Can't update easily (need to edit agent, redeploy)
 530 - No version control or approval workflow for content changes
 531 - Doesn't scale (what about 100+ countries?)
 532 
 533 #### ✅ GOOD: Knowledge Article Retrieval
 534 ```yaml
 535 Topic: Shipping FAQs
 536 Instructions: |
 537   For questions about shipping costs, delivery times, or international shipping,
 538   use the "Search Knowledge: Shipping" action. Summarize the relevant article
 539   and cite the article ID.
 540 
 541   If no article matches, say "I don't have that specific information. Let me
 542   connect you with our shipping team for details."
 543 ```
 544 
 545 ```yaml
 546 Action: Search Knowledge: Shipping
 547 Type: Knowledge Article Search
 548 Query: Dynamically generated based on user question
 549 Filters: ArticleType = 'Shipping_Policy'
 550 ```
 551 
 552 **Example Knowledge Article:**
 553 ```
 554 Title: International Shipping Costs (KB-00482)
 555 Content:
 556   - Canada: $15 (5-7 business days)
 557   - UK: $20 (7-10 business days)
 558   - Australia: $25 (10-14 business days)
 559   - All other countries: Contact shipping team for quote
 560 ```
 561 
 562 **Example Conversation:**
 563 ```
 564 User: How much is shipping to Canada?
 565 
 566 Agent: Shipping to Canada is $15 and takes 5-7 business days.
 567 
 568        [Source: KB-00482]
 569 
 570        Would you like to place an order, or do you have other questions?
 571 ```
 572 
 573 **Fix Applied:**
 574 - Content lives in Knowledge (managed by non-technical teams)
 575 - Easy to update (edit article, no agent redeployment)
 576 - Agent focuses on retrieval and summarization, not content storage
 577 
 578 ---
 579 
 580 ## Category 4: Testing Anti-Patterns
 581 
 582 ### Anti-Pattern 4.1: Testing Only Happy Paths
 583 
 584 **The Problem:** Only testing successful scenarios, ignoring edge cases and failures.
 585 
 586 #### ❌ BAD: Happy-Path-Only Test Cases
 587 ```yaml
 588 Test Case 1: Successful password reset
 589   User: "I forgot my password"
 590   Agent: Asks for email → Sends reset link → User confirms → Success
 591 
 592 Test Case 2: Successful order lookup
 593   User: "Where's my order?" → Provides order number → Agent retrieves order → Success
 594 
 595 Test Case 3: Successful return
 596   User: "I want to return X" → Provides order number → Agent starts return → Success
 597 ```
 598 
 599 **Why It's Bad:**
 600 - Doesn't test error handling (API failures, invalid inputs, out-of-scope requests)
 601 - Doesn't test edge cases (order number not found, reset link expired, ineligible return)
 602 - Real users will encounter these scenarios — agent will fail in production
 603 
 604 #### ✅ GOOD: Comprehensive Test Coverage
 605 ```yaml
 606 # Happy Path
 607 Test Case 1: Successful password reset
 608   User: "I forgot my password"
 609   Expected: Agent asks for email, sends reset link, confirms success
 610 
 611 # Error Handling
 612 Test Case 2: Invalid email format
 613   User: "My email is john@invalid"
 614   Expected: Agent asks for valid email format
 615 
 616 Test Case 3: Reset link expired
 617   User: "The reset link says it's expired"
 618   Expected: Agent sends new link with note about 15-minute expiration
 619 
 620 # Edge Cases
 621 Test Case 4: Customer already reset password
 622   User: "I already reset my password but I'm still locked out"
 623   Expected: Agent escalates to technical support (account issue, not password issue)
 624 
 625 # Out of Scope
 626 Test Case 5: Unrelated question during password reset
 627   User: "I forgot my password"
 628   Agent: Asks for email
 629   User: "Actually, do you ship to Canada?"
 630   Expected: Agent answers shipping question, then returns to password reset
 631 
 632 # Malicious Input
 633 Test Case 6: SQL injection attempt
 634   User: "My email is admin' OR 1=1--"
 635   Expected: Agent treats as invalid email, asks for valid format (sanitization handled by Apex)
 636 ```
 637 
 638 **Fix Applied:**
 639 - 80/20 rule: 20% happy path, 80% edge cases/errors
 640 - Test error recovery (expired links, API failures)
 641 - Test topic switching and out-of-scope handling
 642 - Test input sanitization (security)
 643 
 644 ---
 645 
 646 ## Category 5: Tone and Language Anti-Patterns
 647 
 648 ### Anti-Pattern 5.1: Robotic Corporate Speak
 649 
 650 **The Problem:** Using formal, impersonal language that sounds like a legal document.
 651 
 652 #### ❌ BAD: Corporate Jargon
 653 ```
 654 Agent: Your inquiry has been received and is currently being processed by our
 655        fulfillment system. Please be advised that order modifications are subject
 656        to availability and processing timelines as outlined in our Terms of Service,
 657        Section 4.3. We appreciate your patience as we work to facilitate your request.
 658 ```
 659 
 660 **Why It's Bad:**
 661 - Sounds like a robot, not a conversation
 662 - Uses jargon ("facilitate", "be advised", "fulfillment system")
 663 - No personality or warmth
 664 
 665 #### ✅ GOOD: Conversational Tone
 666 ```yaml
 667 Agent-Level Instructions (Tone: Casual):
 668   Use everyday language. Write like you're texting a friend, but professional.
 669   Use contractions (I'm, you're, we'll). Keep sentences short.
 670 ```
 671 
 672 ```
 673 Agent: Got it! I'm checking if we can still modify your order...
 674 
 675        Good news—your order hasn't shipped yet, so I can update it. What
 676        would you like to change?
 677 ```
 678 
 679 **Fix Applied:**
 680 - Contractions (I'm, hasn't)
 681 - Short sentences
 682 - Active voice ("I'm checking" not "Your inquiry is being processed")
 683 - Conversational transitions ("Got it!", "Good news")
 684 
 685 ---
 686 
 687 ### Anti-Pattern 5.2: Over-Apologizing
 688 
 689 **The Problem:** Apologizing excessively, making the agent sound insincere or weak.
 690 
 691 #### ❌ BAD: Excessive Apologies
 692 ```
 693 User: My order is late.
 694 
 695 Agent: I'm so sorry to hear that your order is late. I sincerely apologize for
 696        any inconvenience this has caused. I'm truly sorry for the delay and I
 697        apologize for the frustration this must have caused. Let me apologize
 698        again and look into this for you. I'm very sorry about this situation.
 699 ```
 700 
 701 **Why It's Bad:**
 702 - 5 apologies in one message (overkill)
 703 - Sounds insincere and robotic
 704 - Wastes time — user wants action, not apologies
 705 
 706 #### ✅ GOOD: One Apology + Action
 707 ```yaml
 708 Agent-Level Instructions:
 709   When something goes wrong, apologize once, then focus on the solution:
 710   "I'm sorry [problem happened]. Let me [action to fix it]."
 711 
 712   Don't repeat apologies. Show empathy through action, not just words.
 713 ```
 714 
 715 ```
 716 User: My order is late.
 717 
 718 Agent: I'm sorry your order is delayed. Let me check the status and see what's
 719        going on...
 720 
 721        [Retrieves order]
 722 
 723        Your order was delayed due to a weather issue at the warehouse. It's now
 724        in transit and will arrive by Friday. I can offer you a $10 credit for
 725        the inconvenience—would that help?
 726 ```
 727 
 728 **Fix Applied:**
 729 - One apology at the start
 730 - Focus shifts immediately to action (checking status)
 731 - Provides explanation and compensation (solution-oriented)
 732 
 733 ---
 734 
 735 ## Summary: Anti-Pattern Checklist
 736 
 737 Before deploying your Agentforce agent, validate against these anti-patterns:
 738 
 739 ### Instructions
 740 - [ ] No absolute language ("must", "always", "never")
 741 - [ ] Positive framing ("do this" not "don't do that")
 742 - [ ] Business rules in Flow/Apex, not instructions
 743 - [ ] Format validation in code, not instructions
 744 
 745 ### Topic Architecture
 746 - [ ] Topics have 5-7 actions max (not monolithic)
 747 - [ ] Classification descriptions don't overlap
 748 - [ ] Escalation paths defined for failure scenarios
 749 
 750 ### Context & Memory
 751 - [ ] Agent checks prior turns before re-asking
 752 - [ ] Content retrieved from Knowledge, not hard-coded
 753 - [ ] Context carried across topic transitions
 754 
 755 ### Testing
 756 - [ ] Tests cover errors and edge cases, not just happy paths
 757 - [ ] Input sanitization tested (security)
 758 - [ ] Out-of-scope handling tested
 759 
 760 ### Tone & Language
 761 - [ ] Conversational tone (contractions, short sentences)
 762 - [ ] One apology + action (not excessive apologies)
 763 - [ ] No corporate jargon or robotic phrasing
 764 
 765 Use this as a pre-launch checklist to catch common mistakes before they reach production.
