<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Topic Architecture Guide for Agentforce Agents
   2 
   3 ## What are Topics?
   4 
   5 Topics are the organizational units that structure your Agentforce agent's capabilities. Each topic is a classification bucket that groups related actions together and defines a distinct area of expertise for your agent.
   6 
   7 Think of topics as departments in a company:
   8 - **Order Management** (like the fulfillment department)
   9 - **Returns & Exchanges** (like customer service)
  10 - **Product Information** (like the sales floor)
  11 - **Account Management** (like the back office)
  12 
  13 Topics serve three critical functions:
  14 
  15 1. **Classification:** Agentforce uses topic classification descriptions to route user utterances to the right set of actions
  16 2. **Scope Definition:** Topics define what your agent CAN do (and by exclusion, what it cannot)
  17 3. **Instruction Organization:** Topics allow you to write specialized behavior instructions for different workflows
  18 
  19 **Key Insight:** Topics are NOT conversation threads or session states—they're classification labels. A single conversation can touch multiple topics, and the agent can switch between topics fluidly based on user intent.
  20 
  21 ---
  22 
  23 ## Bottom-Up Design Methodology
  24 
  25 Many teams make the mistake of starting with topics and then figuring out what actions to put in them. This leads to artificial groupings and overlapping classifications.
  26 
  27 **The right way:** Start with actions, then organize them into topics.
  28 
  29 ### The Bottom-Up Process
  30 
  31 ```
  32 Step 1: List ALL Actions
  33         ↓
  34 Step 2: Group by User Intent
  35         ↓
  36 Step 3: Write Classification Descriptions
  37         ↓
  38 Step 4: Test for Distinctness
  39         ↓
  40 Step 5: Validate with Real Utterances
  41 ```
  42 
  43 Let's walk through each step with a real example.
  44 
  45 ---
  46 
  47 ### Step 1: List ALL Actions the Agent Needs to Perform
  48 
  49 Start by brainstorming every discrete capability your agent should have. Don't worry about organization yet—just capture all the actions.
  50 
  51 **Example: E-Commerce Customer Service Agent**
  52 
  53 ```markdown
  54 Action Inventory (Unsorted):
  55 1. Look up order status by order number
  56 2. Look up order status by email address
  57 3. Track package location
  58 4. Initiate a return for an order
  59 5. Generate a return shipping label
  60 6. Check return eligibility for an item
  61 7. Search product catalog by keyword
  62 8. Get product details (price, sizes, colors)
  63 9. Check product availability/inventory
  64 10. Get product reviews and ratings
  65 11. Update account email address
  66 12. Update account phone number
  67 13. Update account shipping address
  68 14. Reset account password
  69 15. View order history
  70 16. Cancel an order
  71 17. Modify order items (add/remove)
  72 18. Change order shipping address
  73 19. Apply a promo code to an order
  74 20. Check promo code validity
  75 21. Answer questions about return policy
  76 22. Answer questions about shipping policy
  77 23. Answer questions about warranty policy
  78 24. Escalate to human agent
  79 25. Check loyalty points balance
  80 26. Redeem loyalty points
  81 ```
  82 
  83 **Tip:** Include both transactional actions (look up, update, create) and informational actions (answer questions, provide policies).
  84 
  85 ---
  86 
  87 ### Step 2: Group Actions by User Intent Similarity
  88 
  89 Now cluster your actions based on what the USER is trying to accomplish, not what your systems do.
  90 
  91 **Example Grouping:**
  92 
  93 ```markdown
  94 Group A: "I want to know about my order"
  95 - Look up order status by order number
  96 - Look up order status by email address
  97 - Track package location
  98 - View order history
  99 
 100 Group B: "I want to return or cancel something"
 101 - Initiate a return for an order
 102 - Generate a return shipping label
 103 - Check return eligibility for an item
 104 - Cancel an order
 105 
 106 Group C: "I need to change my order"
 107 - Modify order items (add/remove)
 108 - Change order shipping address
 109 - Apply a promo code to an order
 110 
 111 Group D: "I want to learn about products"
 112 - Search product catalog by keyword
 113 - Get product details (price, sizes, colors)
 114 - Check product availability/inventory
 115 - Get product reviews and ratings
 116 
 117 Group E: "I need to update my account"
 118 - Update account email address
 119 - Update account phone number
 120 - Update account shipping address
 121 - Reset account password
 122 - Check loyalty points balance
 123 - Redeem loyalty points
 124 
 125 Group F: "I have questions about policies"
 126 - Answer questions about return policy
 127 - Answer questions about shipping policy
 128 - Answer questions about warranty policy
 129 - Check promo code validity
 130 
 131 Group G: "I need human help"
 132 - Escalate to human agent
 133 ```
 134 
 135 **Key Principle:** Group by USER intent, not by system backend. For example, "Cancel order" and "Initiate return" might both touch the Order Management System, but they're different user intents.
 136 
 137 ---
 138 
 139 ### Step 3: Write Classification Descriptions for Each Group
 140 
 141 For each group, write a classification description that captures the RANGE of user intents in that group. This is what Agentforce will use to route utterances.
 142 
 143 **Classification Description Guidelines:**
 144 
 145 ✅ **DO:**
 146 - Use positive, declarative language ("User wants to...")
 147 - Be specific about the scope
 148 - Include common variations of phrasing
 149 - Use language users would actually use
 150 
 151 ❌ **DON'T:**
 152 - Use negative language ("User does NOT want to...")
 153 - Overlap with other topic descriptions
 154 - Be too vague or too narrow
 155 - Use internal jargon or system names
 156 
 157 **Example Classifications:**
 158 
 159 ```markdown
 160 Topic: Order Tracking & Status
 161 Classification Description:
 162 "User wants to check the status of an order, track a package, view order history, or get information about a current or past order. Includes questions about delivery dates, shipping progress, and order confirmation."
 163 
 164 Topic: Returns & Cancellations
 165 Classification Description:
 166 "User wants to return an item, start a return, generate a return label, cancel an order, or check if an item is eligible for return. Includes questions about the return process and refund timelines."
 167 
 168 Topic: Order Modifications
 169 Classification Description:
 170 "User wants to change something about an existing order before it ships, such as adding or removing items, changing the shipping address, or applying a promo code."
 171 
 172 Topic: Product Information & Search
 173 Classification Description:
 174 "User wants to find products, learn about product details (price, sizes, colors, materials), check if an item is in stock, or read product reviews and ratings."
 175 
 176 Topic: Account Management
 177 Classification Description:
 178 "User wants to update their account information (email, phone, address), reset their password, check loyalty points balance, or redeem rewards."
 179 
 180 Topic: Policies & General Questions
 181 Classification Description:
 182 "User has questions about company policies such as return policies, shipping policies, warranties, or wants to validate a promo code. This is a catch-all for informational questions not tied to a specific order or product."
 183 
 184 Topic: General Escalation (Pre-built)
 185 Classification Description:
 186 "User needs help with something the agent cannot handle, wants to speak to a human, or has a complex issue that requires specialist assistance."
 187 ```
 188 
 189 **Length Guidelines:**
 190 - **Minimum:** 20 words (too short = ambiguous classification)
 191 - **Optimal:** 40-80 words (provides clear scope)
 192 - **Maximum:** 150 words (too long = classification slowdown)
 193 
 194 ---
 195 
 196 ### Step 4: Test for Semantic Distinctness Between Groups
 197 
 198 Your classification descriptions must be mutually exclusive. If they overlap, Agentforce may route utterances to the wrong topic.
 199 
 200 **Overlap Test:**
 201 
 202 For each pair of topics, ask: "Could a reasonable user utterance match both descriptions?"
 203 
 204 **Example Overlap Problem:**
 205 
 206 ```markdown
 207 ❌ BAD EXAMPLE:
 208 
 209 Topic A: Order Management
 210 "User wants to do something with their order."
 211 
 212 Topic B: Order Tracking
 213 "User wants to track their order."
 214 
 215 Problem: "Where's my order?" could match both. Topic B is a subset of Topic A.
 216 ```
 217 
 218 **Fixed:**
 219 
 220 ```markdown
 221 ✅ GOOD EXAMPLE:
 222 
 223 Topic A: Order Tracking & Status
 224 "User wants to CHECK the status of an order, track a package, or view order history. This is about monitoring existing orders, not making changes."
 225 
 226 Topic B: Order Modifications
 227 "User wants to CHANGE something about an existing order before it ships, such as adding items, changing the address, or applying a promo code."
 228 
 229 Why it works: "Where's my order?" → Monitoring → Topic A. "Can I add an item?" → Changing → Topic B.
 230 ```
 231 
 232 **Distinctness Checklist:**
 233 
 234 For each topic pair, verify:
 235 - [ ] They cover different user goals
 236 - [ ] Keywords are distinct (track vs modify, find vs update)
 237 - [ ] No subset relationships (one is not a subcategory of another)
 238 - [ ] Boundary examples clearly belong to one or the other
 239 
 240 **Boundary Testing:**
 241 
 242 For each topic pair, write 5 "boundary utterances" and verify they classify correctly:
 243 
 244 | Utterance | Should Route To | Why |
 245 |-----------|-----------------|-----|
 246 | "Where's my order?" | Order Tracking | Checking status |
 247 | "Can I change my shipping address?" | Order Modifications | Making a change |
 248 | "How do I return this?" | Returns & Cancellations | Return process |
 249 | "Is this sweater in stock?" | Product Information | Product availability |
 250 | "What's your return policy?" | Policies & General Questions | Policy info |
 251 
 252 ---
 253 
 254 ### Step 5: Validate with Real Utterances
 255 
 256 Test your topic architecture with real user language. Collect 50-100 sample utterances from:
 257 - Customer service chat logs
 258 - Support tickets
 259 - User interviews
 260 - Hypothetical scenarios
 261 
 262 **Validation Template:**
 263 
 264 ```markdown
 265 Utterance: "I never received my order and it's been 2 weeks"
 266 Expected Topic: Order Tracking & Status
 267 Actual Classification: [Run in Testing Center]
 268 Pass/Fail: ✅
 269 
 270 Utterance: "Can you add another shirt to my order?"
 271 Expected Topic: Order Modifications
 272 Actual Classification: [Run in Testing Center]
 273 Pass/Fail: ✅
 274 
 275 Utterance: "This doesn't fit, I need to return it"
 276 Expected Topic: Returns & Cancellations
 277 Actual Classification: [Run in Testing Center]
 278 Pass/Fail: ✅
 279 ```
 280 
 281 **Accuracy Goals:**
 282 - **Tier 1 (Critical):** 95%+ accuracy (e.g., order tracking, returns)
 283 - **Tier 2 (Important):** 90%+ accuracy (e.g., product info, account changes)
 284 - **Tier 3 (Nice-to-have):** 85%+ accuracy (e.g., general policies)
 285 
 286 **Iteration:** If accuracy is below target, refine classification descriptions or merge/split topics.
 287 
 288 ---
 289 
 290 ## Classification Descriptions
 291 
 292 Classification descriptions are the most critical part of your topic architecture. They determine whether Agentforce routes user requests correctly.
 293 
 294 ### Anatomy of a Great Classification Description
 295 
 296 **Formula:** [User Goal] + [Common Variations] + [Scope Boundaries]
 297 
 298 **Example:**
 299 
 300 ```markdown
 301 Topic: Order Tracking & Status
 302 
 303 Classification Description:
 304 "User wants to [USER GOAL] check the status of an order, track a package, view order history, or get information about a current or past order. [COMMON VARIATIONS] Includes questions about delivery dates, shipping progress, and order confirmation. [SCOPE BOUNDARY] This is about monitoring orders, not making changes or processing returns."
 305 ```
 306 
 307 **Breakdown:**
 308 1. **User Goal:** "check the status of an order" (primary intent)
 309 2. **Common Variations:** "track a package, view order history, get information"
 310 3. **Scope Boundary:** "not making changes or processing returns" (clarifies exclusions)
 311 
 312 ### Writing Style Guidelines
 313 
 314 | Guideline | Good Example | Bad Example |
 315 |-----------|--------------|-------------|
 316 | **Use positive language** | "User wants to track their order" | "User is NOT asking about returns" |
 317 | **Be specific** | "User wants to check product availability and sizes" | "User has product questions" |
 318 | **Use natural language** | "User wants to return an item" | "User wants to initiate reverse logistics" |
 319 | **Include variations** | "track, monitor, check status, see updates" | "track" (too narrow) |
 320 | **Avoid jargon** | "User wants to update their email address" | "User wants to modify CRM contact record" |
 321 
 322 ### Common Pitfalls
 323 
 324 #### Pitfall 1: Too Vague
 325 
 326 ```markdown
 327 ❌ BAD:
 328 Topic: Order Management
 329 "User has questions about orders."
 330 
 331 Problem: Every order-related utterance will match this.
 332 ```
 333 
 334 ```markdown
 335 ✅ GOOD:
 336 Topic: Order Tracking & Status
 337 "User wants to check the status of an existing order, track package location, view past orders, or get delivery estimates. This is about monitoring orders, not making changes."
 338 ```
 339 
 340 #### Pitfall 2: Too Narrow
 341 
 342 ```markdown
 343 ❌ BAD:
 344 Topic: Order Tracking
 345 "User wants to track a package using a tracking number."
 346 
 347 Problem: Misses "Where's my order?" (no tracking number mentioned)
 348 ```
 349 
 350 ```markdown
 351 ✅ GOOD:
 352 Topic: Order Tracking & Status
 353 "User wants to check the status of an order, track a package, view order history, or get delivery information. User may provide an order number, email address, or tracking number."
 354 ```
 355 
 356 #### Pitfall 3: Overlapping Descriptions
 357 
 358 ```markdown
 359 ❌ BAD:
 360 Topic A: Product Search
 361 "User wants to find products or search the catalog."
 362 
 363 Topic B: Product Information
 364 "User wants to learn about products or get product details."
 365 
 366 Problem: "Tell me about this sweater" could match both.
 367 ```
 368 
 369 ```markdown
 370 ✅ GOOD:
 371 Topic A: Product Search & Discovery
 372 "User wants to FIND products by searching for keywords, browsing categories, or filtering by attributes (size, color, price). This is about discovering what's available."
 373 
 374 Topic B: Product Details & Availability
 375 "User wants detailed information about a SPECIFIC product they've identified, such as price, sizes, colors, materials, inventory status, or customer reviews."
 376 ```
 377 
 378 #### Pitfall 4: System-Centric Language
 379 
 380 ```markdown
 381 ❌ BAD:
 382 Topic: CRM Account Updates
 383 "User wants to modify Salesforce contact records or update Account object fields."
 384 
 385 Problem: Users don't think in terms of "Salesforce objects."
 386 ```
 387 
 388 ```markdown
 389 ✅ GOOD:
 390 Topic: Account Management
 391 "User wants to update their personal information such as email address, phone number, or shipping address, or manage their account settings."
 392 ```
 393 
 394 ### Testing Classification Descriptions
 395 
 396 Use the Agentforce Testing Center to validate:
 397 
 398 1. **Single-topic utterances:** Should route to the correct topic
 399 2. **Ambiguous utterances:** Should route to the most relevant topic
 400 3. **Out-of-scope utterances:** Should route to General Escalation
 401 
 402 **Test Template:**
 403 
 404 | Utterance | Expected Topic | Actual Topic | Pass/Fail |
 405 |-----------|----------------|--------------|-----------|
 406 | "Where is my order?" | Order Tracking | [Test result] | ✅/❌ |
 407 | "I want to return this" | Returns & Cancellations | [Test result] | ✅/❌ |
 408 | "Is this in stock?" | Product Information | [Test result] | ✅/❌ |
 409 | "What's your refund policy?" | Policies & General Questions | [Test result] | ✅/❌ |
 410 | "I need a lawyer" | General Escalation | [Test result] | ✅/❌ |
 411 
 412 **Iteration:** For failures, tweak classification descriptions and re-test.
 413 
 414 ---
 415 
 416 ## Scope Boundaries
 417 
 418 Topics define your agent's scope—what it CAN do. By extension, anything not covered by your topics is OUT OF SCOPE.
 419 
 420 ### Defining In-Scope vs Out-of-Scope
 421 
 422 **In-Scope:** Actions explicitly covered by your topics
 423 
 424 **Out-of-Scope:** Everything else (routes to General Escalation)
 425 
 426 **Example: E-Commerce Agent**
 427 
 428 ```markdown
 429 IN SCOPE:
 430 - Order tracking and status checks
 431 - Return and cancellation requests
 432 - Product search and information
 433 - Account information updates
 434 - Policy questions (returns, shipping, warranty)
 435 
 436 OUT OF SCOPE:
 437 - Technical support for using products
 438 - Medical/legal/financial advice
 439 - Complaints or disputes (escalate to human)
 440 - Marketing feedback or surveys
 441 - Third-party service issues (payment processors, carriers)
 442 ```
 443 
 444 ### Using Topics as Safety Guardrails
 445 
 446 Topics act as a natural safety layer. If a user asks something outside your topic classifications, Agentforce routes it to the General Escalation topic.
 447 
 448 **Example:**
 449 
 450 ```markdown
 451 User: "Can you give me legal advice about my warranty?"
 452 Classification: No topic matches → Routes to General Escalation
 453 Agent Response: "I'm not able to provide legal advice, but I can connect you with our customer care team who can discuss your warranty options."
 454 ```
 455 
 456 **Guardrail Strategy:**
 457 
 458 1. **Narrow topic classifications:** Be specific about what each topic covers
 459 2. **Leverage General Escalation:** Let it catch out-of-scope requests
 460 3. **Test edge cases:** Validate that unsafe/inappropriate requests route to Escalation
 461 
 462 **Test Cases for Guardrails:**
 463 
 464 | Utterance | Expected Behavior |
 465 |-----------|-------------------|
 466 | "Can you give me medical advice?" | → General Escalation |
 467 | "I'm going to sue you!" | → General Escalation |
 468 | "Can I get a refund on this 5-year-old order?" | → General Escalation (policy violation) |
 469 | "Can you hack into my ex's account?" | → General Escalation (inappropriate request) |
 470 | "Tell me a joke" | → General Escalation (chitchat, off-topic) |
 471 
 472 ---
 473 
 474 ## Architecture Rules
 475 
 476 Follow these rules to create a clean, scalable topic architecture:
 477 
 478 ### Rule 1: Maximum 10 Topics per Agent (Recommended)
 479 
 480 **Why:** More topics = harder to classify accurately. Agentforce's classification model performs best with 5-10 distinct topics.
 481 
 482 **Guideline:**
 483 - **5-7 topics:** Optimal for most agents
 484 - **8-10 topics:** Acceptable for complex domains
 485 - **11+ topics:** Consider splitting into multiple agents
 486 
 487 **Example: Overcomplicated Architecture**
 488 
 489 ```markdown
 490 ❌ BAD (15 topics):
 491 1. Order Status Checks
 492 2. Package Tracking
 493 3. Delivery Date Inquiries
 494 4. Return Initiation
 495 5. Return Label Generation
 496 6. Refund Status
 497 7. Product Search
 498 8. Product Details
 499 9. Inventory Checks
 500 10. Email Updates
 501 11. Phone Updates
 502 12. Address Updates
 503 13. Return Policy
 504 14. Shipping Policy
 505 15. Warranty Policy
 506 
 507 Problem: Too many topics with overlapping purposes.
 508 ```
 509 
 510 **Consolidated Architecture:**
 511 
 512 ```markdown
 513 ✅ GOOD (6 topics):
 514 1. Order Tracking & Status (combines 1, 2, 3)
 515 2. Returns & Refunds (combines 4, 5, 6)
 516 3. Product Information (combines 7, 8, 9)
 517 4. Account Management (combines 10, 11, 12)
 518 5. Policies & General Questions (combines 13, 14, 15)
 519 6. General Escalation (pre-built)
 520 
 521 Benefit: Clearer classification, easier to maintain.
 522 ```
 523 
 524 ### Rule 2: Maximum 5 Actions per Topic (Recommended)
 525 
 526 **Why:** Topics with too many actions become "mega-topics" that dilute classification accuracy.
 527 
 528 **Guideline:**
 529 - **3-5 actions:** Optimal per topic
 530 - **6-7 actions:** Acceptable if tightly related
 531 - **8+ actions:** Consider splitting the topic
 532 
 533 **Example: Bloated Topic**
 534 
 535 ```markdown
 536 ❌ BAD:
 537 Topic: Order Management (10 actions)
 538 - Look up order status
 539 - Track package
 540 - View order history
 541 - Cancel order
 542 - Modify order items
 543 - Change shipping address
 544 - Apply promo code
 545 - Initiate return
 546 - Generate return label
 547 - Check refund status
 548 
 549 Problem: Mixing monitoring, modifications, and returns in one topic.
 550 ```
 551 
 552 **Split Topics:**
 553 
 554 ```markdown
 555 ✅ GOOD:
 556 Topic: Order Tracking & Status (3 actions)
 557 - Look up order status
 558 - Track package
 559 - View order history
 560 
 561 Topic: Order Modifications (3 actions)
 562 - Modify order items
 563 - Change shipping address
 564 - Apply promo code
 565 
 566 Topic: Returns & Refunds (4 actions)
 567 - Initiate return
 568 - Generate return label
 569 - Check refund status
 570 - Cancel order (if it includes refund logic)
 571 ```
 572 
 573 ### Rule 3: Each Topic Should Have a Clear, Distinct Purpose
 574 
 575 **Test:** Can you describe the topic's purpose in one sentence?
 576 
 577 ```markdown
 578 ✅ GOOD:
 579 - Order Tracking: "Help users monitor their orders and packages."
 580 - Returns: "Help users process returns and refunds."
 581 - Product Info: "Help users find and learn about products."
 582 
 583 ❌ BAD:
 584 - Miscellaneous: "Handle various user requests."
 585 - General Support: "Provide assistance with customer needs."
 586 ```
 587 
 588 ### Rule 4: No Overlapping Classification Descriptions
 589 
 590 **Test:** For any pair of topics, can you write 5 utterances that CLEARLY belong to one or the other?
 591 
 592 **Overlap Example:**
 593 
 594 ```markdown
 595 ❌ BAD:
 596 Topic A: Product Questions
 597 "User has questions about products."
 598 
 599 Topic B: Product Search
 600 "User wants to find products."
 601 
 602 Overlap: "Tell me about the blue sweater" could match either.
 603 ```
 604 
 605 **Fixed:**
 606 
 607 ```markdown
 608 ✅ GOOD:
 609 Topic A: Product Search & Discovery
 610 "User wants to FIND products they don't know about yet by searching keywords, browsing categories, or filtering."
 611 
 612 Topic B: Product Details & Availability
 613 "User already knows WHICH product they're interested in and wants specific details like price, sizes, inventory, or reviews."
 614 
 615 No Overlap: "Find me a sweater" → Topic A. "Is the blue sweater in stock?" → Topic B.
 616 ```
 617 
 618 ### Rule 5: Every Action Must Belong to Exactly One Topic
 619 
 620 **Why:** Actions in multiple topics create classification confusion.
 621 
 622 **Example:**
 623 
 624 ```markdown
 625 ❌ BAD:
 626 Action: "Check Order Status"
 627 - Assigned to Topic A: Order Tracking
 628 - Assigned to Topic B: Order Management
 629 
 630 Problem: Which topic should "Where's my order?" route to?
 631 ```
 632 
 633 ```markdown
 634 ✅ GOOD:
 635 Action: "Check Order Status"
 636 - Assigned to Topic A: Order Tracking ONLY
 637 ```
 638 
 639 **Edge Case:** If an action truly serves multiple purposes, consider:
 640 1. **Split the action** into two specialized versions
 641 2. **Broaden one topic** to encompass both use cases
 642 3. **Use topic-level instructions** to handle variations
 643 
 644 ---
 645 
 646 ## Topic Interaction Patterns
 647 
 648 Topics aren't isolated—users often move between topics in a single conversation.
 649 
 650 ### Pattern 1: Sequential Topics (Order Tracking → Return Processing)
 651 
 652 **Example:**
 653 
 654 ```
 655 User: "Where's my order?"
 656 Agent: [Order Tracking] "Your order #12345 shipped yesterday and should arrive Friday."
 657 
 658 User: "Actually, I need to return it."
 659 Agent: [Switches to Returns & Cancellations] "I can help with that return. Let me generate a prepaid label for order #12345."
 660 ```
 661 
 662 **Key:** Agentforce automatically switches topics when user intent changes. You don't need to script this—classification handles it.
 663 
 664 ### Pattern 2: Parallel Topics (Multiple Intents in One Turn)
 665 
 666 **Example:**
 667 
 668 ```
 669 User: "Can I change my shipping address and also return an item from last week?"
 670 Agent: [Detects two intents: Account Management + Returns]
 671 "I can help with both. Let me start with updating your shipping address for future orders. What's the new address?"
 672 [After completing] "Now let's process the return. Which item from last week do you need to return?"
 673 ```
 674 
 675 **Key:** Agentforce can detect multiple intents and handle them sequentially.
 676 
 677 ### Pattern 3: Cross-Topic Context Passing
 678 
 679 **Example:**
 680 
 681 ```
 682 User: "I want to return the sweater from order #12345"
 683 [Returns topic is triggered]
 684 
 685 Agent: [Calls "Look Up Order" action from Order Tracking topic to get order details]
 686 Agent: [Then calls "Initiate Return" action from Returns topic]
 687 "I see you ordered a blue sweater in size M. I've started the return and sent a label to your email."
 688 ```
 689 
 690 **Key:** Actions from one topic can be invoked within another topic's context. This is handled automatically by Agentforce's planner.
 691 
 692 ### Designing for Topic Switching
 693 
 694 **Best Practices:**
 695 
 696 1. **Don't over-script transitions:** Let Agentforce handle topic classification dynamically
 697 2. **Use topic-level instructions for context:** If a topic needs specific setup, document it in topic instructions
 698 3. **Test multi-turn conversations:** Validate that switching between topics feels natural
 699 
 700 **Example Test Case:**
 701 
 702 ```markdown
 703 Turn 1 (Order Tracking):
 704 User: "Where's my order?"
 705 Agent: "Your order #12345 shipped yesterday."
 706 
 707 Turn 2 (Returns):
 708 User: "I want to return it."
 709 Agent: "I can help with that return for order #12345." [Maintains context]
 710 
 711 Turn 3 (Product Info):
 712 User: "Do you have the same sweater in large?"
 713 Agent: "Let me check. Yes, the blue sweater is available in size large." [Switches topic]
 714 
 715 Turn 4 (Order Tracking):
 716 User: "OK, when will my original order arrive?"
 717 Agent: "Your original order #12345 should arrive by Friday." [Switches back]
 718 ```
 719 
 720 **Goal:** Transitions should feel seamless, not jarring.
 721 
 722 ---
 723 
 724 ## Salesforce Implementation
 725 
 726 ### Creating Topics in Agent Builder
 727 
 728 **Step-by-Step:**
 729 
 730 1. Navigate to **Setup > Agent Builder > [Your Agent] > Topics**
 731 2. Click **New Topic**
 732 3. Enter **Topic Name** (e.g., "Order Tracking & Status")
 733 4. Write **Classification Description** (40-80 words)
 734 5. (Optional) Add **Topic-Level Instructions** (covered in instruction-writing-guide.md)
 735 6. Click **Save**
 736 
 737 **Repeat for each topic in your architecture.**
 738 
 739 ### Configuring Classification Descriptions
 740 
 741 **UI Fields:**
 742 
 743 - **Topic Name:** Internal label (e.g., "Order_Tracking_Status")
 744 - **Display Name:** User-facing name (e.g., "Order Tracking & Status")
 745 - **Classification Description:** The text Agentforce uses for routing (40-80 words)
 746 
 747 **Example:**
 748 
 749 ```markdown
 750 Topic Name: Order_Tracking_Status
 751 Display Name: Order Tracking & Status
 752 Classification Description:
 753 "User wants to check the status of an order, track a package, view order history, or get information about a current or past order. Includes questions about delivery dates, shipping progress, and order confirmation. This is about monitoring existing orders, not making changes or processing returns."
 754 ```
 755 
 756 ### Assigning Actions to Topics
 757 
 758 **Step-by-Step:**
 759 
 760 1. Navigate to **Setup > Agent Builder > [Your Agent] > Actions**
 761 2. Click **New Action** (or edit existing)
 762 3. Configure action details (name, API reference, inputs/outputs)
 763 4. In **Topic Assignment**, select the topic this action belongs to
 764 5. (Optional) Add **Action-Level Instructions**
 765 6. Click **Save**
 766 
 767 **Example:**
 768 
 769 ```markdown
 770 Action: Look Up Order Status
 771 API Reference: OrderManagementFlow.lookUpOrderStatus
 772 Topic Assignment: Order Tracking & Status
 773 Action-Level Instructions:
 774 "Use this action when the user wants to check the status of a specific order. Require either an order number or the email address used for purchase. If the user doesn't provide this information, ask for it before invoking the action."
 775 ```
 776 
 777 **Rule:** Every action must be assigned to exactly one topic.
 778 
 779 ### Setting Topic-Level Instructions
 780 
 781 Topic-level instructions guide agent behavior within that topic's context.
 782 
 783 **Example:**
 784 
 785 ```markdown
 786 Topic: Order Tracking & Status
 787 
 788 Topic-Level Instructions:
 789 "For all order tracking requests, gather the order number or email address first. If the user doesn't provide it, ask: 'I can look that up for you. Do you have your order number, or would you like me to search by email address?'
 790 
 791 Once you have the order information, use the Look Up Order Status action. Present the results in this format:
 792 - Order number and date
 793 - Current status (e.g., 'Shipped,' 'In Transit,' 'Delivered')
 794 - Expected delivery date
 795 - Tracking link (if available)
 796 
 797 If the order hasn't shipped yet, explain that it's being processed and provide an estimated ship date.
 798 
 799 If the order is delayed, acknowledge the inconvenience and offer to escalate to a specialist if needed."
 800 ```
 801 
 802 **See instruction-writing-guide.md for detailed guidance on writing topic-level instructions.**
 803 
 804 ---
 805 
 806 ## Example: Retail Agent Topic Architecture
 807 
 808 Here's a complete topic architecture for a retail customer service agent.
 809 
 810 ### Agent: Acme Retail Support Agent
 811 
 812 **Agent Scope:** Help customers with orders, returns, product questions, and account management.
 813 
 814 ### Topic 1: Order Tracking & Status
 815 
 816 **Classification Description:**
 817 "User wants to check the status of an order, track a package, view order history, or get information about a current or past order. Includes questions about delivery dates, shipping progress, order confirmation, and 'Where is my order?' type inquiries."
 818 
 819 **Actions (4):**
 820 1. Look Up Order by Order Number
 821 2. Look Up Order by Email Address
 822 3. Get Package Tracking Details
 823 4. View Order History
 824 
 825 **Topic-Level Instructions:**
 826 "Always gather the order number or email address before looking up order information. Present order status clearly with expected delivery date and tracking link if available."
 827 
 828 ---
 829 
 830 ### Topic 2: Returns & Cancellations
 831 
 832 **Classification Description:**
 833 "User wants to return an item, start a return, generate a return shipping label, cancel an order, check refund status, or ask about return eligibility. Includes questions about the return process, return windows, and refund timelines."
 834 
 835 **Actions (5):**
 836 1. Check Return Eligibility
 837 2. Initiate Return Request
 838 3. Generate Return Shipping Label
 839 4. Cancel Pending Order
 840 5. Check Refund Status
 841 
 842 **Topic-Level Instructions:**
 843 "For returns, first check eligibility (30-day window, unused condition). Walk users through the return process step-by-step. For cancellations, check if the order has shipped—if yes, route through the return process instead."
 844 
 845 ---
 846 
 847 ### Topic 3: Order Modifications
 848 
 849 **Classification Description:**
 850 "User wants to make changes to an existing order that hasn't shipped yet, such as adding or removing items, changing the shipping address, applying a promo code, or upgrading shipping speed."
 851 
 852 **Actions (4):**
 853 1. Modify Order Items
 854 2. Update Shipping Address
 855 3. Apply Promo Code to Order
 856 4. Upgrade Shipping Method
 857 
 858 **Topic-Level Instructions:**
 859 "Always check if the order has shipped before attempting modifications. If it has shipped, explain that changes aren't possible and offer alternatives (e.g., return/reorder for different items)."
 860 
 861 ---
 862 
 863 ### Topic 4: Product Information & Search
 864 
 865 **Classification Description:**
 866 "User wants to find products, search the catalog, learn about product details such as price, sizes, colors, materials, check if an item is in stock, or read product reviews and ratings. This is about discovering and researching products."
 867 
 868 **Actions (5):**
 869 1. Search Product Catalog by Keyword
 870 2. Get Product Details
 871 3. Check Product Availability
 872 4. Get Product Reviews
 873 5. Compare Products
 874 
 875 **Topic-Level Instructions:**
 876 "Help users find products that match their needs. If they're browsing, ask clarifying questions about preferences (size, color, price range). Always check availability before recommending a product."
 877 
 878 ---
 879 
 880 ### Topic 5: Account Management
 881 
 882 **Classification Description:**
 883 "User wants to update their account information such as email address, phone number, shipping address, payment methods, password, or manage loyalty points and rewards. This is about personal account settings, not specific orders."
 884 
 885 **Actions (5):**
 886 1. Update Email Address
 887 2. Update Phone Number
 888 3. Update Default Shipping Address
 889 4. Reset Password
 890 5. Check Loyalty Points Balance
 891 
 892 **Topic-Level Instructions:**
 893 "Always verify the user's identity before making account changes. For security-sensitive changes (email, password), explain that we'll send a verification link or code."
 894 
 895 ---
 896 
 897 ### Topic 6: Policies & General Questions
 898 
 899 **Classification Description:**
 900 "User has questions about company policies such as return policies, shipping policies, warranties, price matching, or wants to validate a promo code. This is a catch-all for informational questions not tied to a specific order or product."
 901 
 902 **Actions (4):**
 903 1. Get Return Policy (Knowledge)
 904 2. Get Shipping Policy (Knowledge)
 905 3. Get Warranty Information (Knowledge)
 906 4. Validate Promo Code
 907 
 908 **Topic-Level Instructions:**
 909 "Use Knowledge actions to provide accurate policy information. After answering a policy question, offer to help the user apply that policy to their specific situation (e.g., 'Would you like to start a return?')."
 910 
 911 ---
 912 
 913 ### Topic 7: General Escalation (Pre-Built)
 914 
 915 **Classification Description:**
 916 "User needs help with something outside the agent's capabilities, wants to speak to a human representative, has a complex issue requiring specialist assistance, or makes inappropriate requests."
 917 
 918 **Actions (1):**
 919 1. Escalate to Human Agent (Omni-Channel)
 920 
 921 **Topic-Level Instructions:**
 922 "When escalating, briefly summarize what the user needs so the human agent has context. Example: 'I'm connecting you with a specialist who can help with [specific issue]. One moment please.'"
 923 
 924 ---
 925 
 926 ### Architecture Summary
 927 
 928 | Topic | Actions | Purpose |
 929 |-------|---------|---------|
 930 | Order Tracking & Status | 4 | Monitor existing orders |
 931 | Returns & Cancellations | 5 | Process returns and refunds |
 932 | Order Modifications | 4 | Change orders before shipping |
 933 | Product Information & Search | 5 | Discover and research products |
 934 | Account Management | 5 | Update personal account info |
 935 | Policies & General Questions | 4 | Answer policy/general questions |
 936 | General Escalation | 1 | Escalate to human agents |
 937 
 938 **Total:** 7 topics, 28 actions
 939 
 940 **Classification Distinctness:** ✅ All topics have clear, non-overlapping scopes.
 941 
 942 ---
 943 
 944 ## Common Mistakes
 945 
 946 ### Mistake 1: Starting with Topics Instead of Actions
 947 
 948 **Symptom:** Topics feel arbitrary, actions don't fit naturally.
 949 
 950 **Example:**
 951 
 952 ```markdown
 953 ❌ BAD APPROACH:
 954 "We need topics for... let's see... Orders, Products, and Accounts. Now what actions go in each?"
 955 
 956 Result: Forced groupings that don't match user intent.
 957 ```
 958 
 959 **Fix:** Start with actions. "What can the agent DO?" Then group by user intent.
 960 
 961 ### Mistake 2: Too Many Topics
 962 
 963 **Symptom:** 12+ topics, overlapping classifications, poor routing accuracy.
 964 
 965 **Example:**
 966 
 967 ```markdown
 968 ❌ BAD:
 969 1. Order Status
 970 2. Package Tracking
 971 3. Delivery Dates
 972 4. Order History
 973 5. Return Initiation
 974 6. Return Labels
 975 7. Refund Status
 976 8. Order Cancellation
 977 ... (15 topics total)
 978 ```
 979 
 980 **Fix:** Consolidate into broader, distinct topics (5-7 topics).
 981 
 982 ### Mistake 3: Vague Classification Descriptions
 983 
 984 **Symptom:** Multiple topics match the same utterance.
 985 
 986 **Example:**
 987 
 988 ```markdown
 989 ❌ BAD:
 990 Topic A: "User has order questions"
 991 Topic B: "User needs order help"
 992 
 993 Problem: "Where's my order?" matches both.
 994 ```
 995 
 996 **Fix:** Be specific and include scope boundaries.
 997 
 998 ### Mistake 4: System-Centric Topics
 999 
1000 **Symptom:** Topics named after internal systems or data models.
1001 
1002 **Example:**
1003 
1004 ```markdown
1005 ❌ BAD:
1006 - Order Management System (OMS) Topic
1007 - Customer Relationship Management (CRM) Topic
1008 - Product Information Management (PIM) Topic
1009 ```
1010 
1011 **Fix:** Name topics based on USER goals, not systems.
1012 
1013 ```markdown
1014 ✅ GOOD:
1015 - Order Tracking & Status
1016 - Account Management
1017 - Product Information & Search
1018 ```
1019 
1020 ### Mistake 5: Actions in Multiple Topics
1021 
1022 **Symptom:** Duplicate actions, unclear classification routing.
1023 
1024 **Example:**
1025 
1026 ```markdown
1027 ❌ BAD:
1028 Action: "Look Up Order Status"
1029 - In Topic A: Order Tracking
1030 - In Topic B: Order Management
1031 
1032 Problem: Which topic should "Where's my order?" route to?
1033 ```
1034 
1035 **Fix:** Assign each action to exactly one topic. If truly needed in multiple contexts, create specialized versions.
1036 
1037 ---
1038 
1039 ## Testing Your Topic Architecture
1040 
1041 Use the Agentforce Testing Center to validate:
1042 
1043 ### Test Suite
1044 
1045 1. **Classification Accuracy:** 50+ utterances across all topics
1046 2. **Boundary Cases:** Utterances that might match multiple topics
1047 3. **Out-of-Scope:** Utterances that should route to General Escalation
1048 4. **Multi-Turn:** Conversations that switch between topics
1049 
1050 ### Test Template
1051 
1052 | Utterance | Expected Topic | Actual Topic | Pass/Fail |
1053 |-----------|----------------|--------------|-----------|
1054 | "Where is my order?" | Order Tracking | [Result] | ✅/❌ |
1055 | "I want to return this" | Returns & Cancellations | [Result] | ✅/❌ |
1056 | "Is this sweater in stock?" | Product Information | [Result] | ✅/❌ |
1057 | "Update my email address" | Account Management | [Result] | ✅/❌ |
1058 | "What's your return policy?" | Policies & General Questions | [Result] | ✅/❌ |
1059 | "I need legal advice" | General Escalation | [Result] | ✅/❌ |
1060 | "Can I change my order and also return something?" | Order Modifications (first) | [Result] | ✅/❌ |
1061 
1062 ### Iteration Cycle
1063 
1064 1. Test with 50+ utterances
1065 2. Identify misclassifications
1066 3. Refine classification descriptions
1067 4. Merge or split topics if needed
1068 5. Re-test
1069 
1070 **Goal:** 90%+ accuracy for critical topics, 85%+ for secondary topics.
1071 
1072 ---
1073 
1074 ## Next Steps
1075 
1076 1. Complete the action inventory for your agent
1077 2. Group actions by user intent
1078 3. Write classification descriptions for each topic
1079 4. Test for semantic distinctness
1080 5. Validate with real user utterances
1081 6. Implement in Agentforce Agent Builder
1082 7. Test and iterate
1083 
1084 **Remember:** Topic architecture is foundational. Invest time upfront to get it right, and your agent's performance will be dramatically better.
