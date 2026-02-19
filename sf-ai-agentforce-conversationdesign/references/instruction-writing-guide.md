<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Instruction Writing Guide for Agentforce Agents
   2 
   3 ## The Three-Level Instruction Framework
   4 
   5 Agentforce agents are guided by instructions at three distinct levels, each serving a different purpose:
   6 
   7 ```
   8 Agent-Level Instructions
   9     ↓ (Apply to EVERYTHING)
  10 Topic-Level Instructions
  11     ↓ (Apply to one topic)
  12 Action-Level Instructions
  13     ↓ (Apply to one action)
  14 ```
  15 
  16 ### Level 1: Agent-Level Instructions
  17 
  18 **What:** Global persona, behavior rules, and limitations that apply to ALL topics.
  19 
  20 **Where:** Agent Builder > Instructions tab
  21 
  22 **Purpose:** Define WHO the agent is and HOW it behaves universally.
  23 
  24 **Example:**
  25 ```markdown
  26 You are the Acme Retail Support Agent, a helpful and efficient assistant for customers.
  27 
  28 **Personality:**
  29 - Helpful: Always offer solutions and alternatives
  30 - Efficient: Keep responses concise (2-3 sentences)
  31 - Empathetic: Acknowledge frustration or disappointment
  32 
  33 **Boundaries:**
  34 - I cannot provide medical, legal, or financial advice
  35 - I cannot override company policies
  36 - I will escalate complex issues to human specialists
  37 ```
  38 
  39 ---
  40 
  41 ### Level 2: Topic-Level Instructions
  42 
  43 **What:** Workflow logic, data gathering requirements, and behavior specific to ONE topic.
  44 
  45 **Where:** Agent Builder > Topics > [Specific Topic] > Instructions
  46 
  47 **Purpose:** Guide how the agent operates within a specific domain (e.g., order tracking, returns).
  48 
  49 **Example:**
  50 ```markdown
  51 Topic: Order Tracking & Status
  52 
  53 For all order tracking requests, gather the order number or email address first. If not provided, ask: "I can look that up for you. Do you have your order number, or would you like me to search by email address?"
  54 
  55 Present order status in this format:
  56 - Order number and date
  57 - Current status
  58 - Expected delivery date
  59 - Tracking link (if available)
  60 ```
  61 
  62 ---
  63 
  64 ### Level 3: Action-Level Instructions
  65 
  66 **What:** When and how to use a SPECIFIC action, required inputs, and output handling.
  67 
  68 **Where:** Agent Builder > Actions > [Specific Action] > Instructions
  69 
  70 **Purpose:** Tell the agent when to invoke an action and how to present results.
  71 
  72 **Example:**
  73 ```markdown
  74 Action: Look Up Order Status
  75 
  76 **When to Use:**
  77 Use this action when the user wants to check the status of a specific order.
  78 
  79 **Required Inputs:**
  80 - Order number OR email address (ask if not provided)
  81 
  82 **Output Handling:**
  83 Present the order status, expected delivery date, and tracking link. If the order hasn't shipped yet, explain it's being processed and provide an estimated ship date.
  84 ```
  85 
  86 ---
  87 
  88 ### How the Three Levels Work Together
  89 
  90 **Example Scenario: User asks "Where's my order?"**
  91 
  92 1. **Agent-Level Instructions:** "Be helpful and empathetic" → Agent uses friendly tone
  93 2. **Topic-Level Instructions:** "Gather order number first" → Agent asks for order number
  94 3. **Action-Level Instructions:** "Present status, delivery date, and tracking link" → Agent formats response correctly
  95 
  96 **Result:**
  97 ```
  98 Agent: "I'll look that up for you. Do you have your order number, or would you like me to search by email address?"
  99 
 100 User: "Order number 12345"
 101 
 102 Agent: [Invokes Look Up Order action]
 103 Agent: "Your order #12345 shipped yesterday via FedEx. It should arrive by Friday, February 9th. Here's your tracking link: [link]"
 104 ```
 105 
 106 Each level contributes:
 107 - **Agent-level:** Helpful, friendly tone
 108 - **Topic-level:** Asked for order number before searching
 109 - **Action-level:** Formatted output correctly (status, date, link)
 110 
 111 ---
 112 
 113 ## Core Principles
 114 
 115 ### Principle 1: Guidance Over Determinism
 116 
 117 **Don't:** Write instructions like a state machine with if/then logic.
 118 
 119 **Do:** Provide principles and let the agent reason.
 120 
 121 #### ❌ BAD EXAMPLE (Over-Deterministic):
 122 
 123 ```markdown
 124 If user says "Where's my order?" then:
 125   1. Ask for order number
 126   2. If user provides order number, call Look Up Order action
 127   3. If user doesn't provide order number, ask again
 128   4. If order status is "Shipped", say "Your order shipped on [date]"
 129   5. If order status is "Delivered", say "Your order was delivered on [date]"
 130   6. If order status is "Processing", say "Your order is being processed"
 131   7. If user asks follow-up question, determine topic and respond accordingly
 132 ```
 133 
 134 **Problem:** This is scripting, not guiding. The agent becomes brittle and can't handle variations.
 135 
 136 #### ✅ GOOD EXAMPLE (Guidance):
 137 
 138 ```markdown
 139 For order tracking requests, gather the order number or email address before looking up the order. Present the current status, expected delivery date, and tracking information clearly. If the order hasn't shipped yet, explain that it's being processed.
 140 ```
 141 
 142 **Why it's better:** The agent understands the GOAL (provide order status) and the REQUIREMENTS (need order number, present certain information) without being locked into a rigid script.
 143 
 144 ---
 145 
 146 ### Principle 2: Positive Framing
 147 
 148 **Don't:** Write instructions with negative language ("don't do X").
 149 
 150 **Do:** Write instructions with positive language ("always do Y").
 151 
 152 #### ❌ BAD EXAMPLES:
 153 
 154 ```markdown
 155 - "Don't proceed without an order number"
 156 - "Never give refunds without manager approval"
 157 - "Don't use technical jargon"
 158 - "Don't skip verification steps"
 159 ```
 160 
 161 **Problem:** Negative framing focuses on what NOT to do, which is less actionable than what TO do.
 162 
 163 #### ✅ GOOD EXAMPLES:
 164 
 165 ```markdown
 166 - "Always gather the order number before looking up order information"
 167 - "Escalate refund requests beyond standard policy to a manager"
 168 - "Use everyday language that customers can easily understand"
 169 - "Verify the user's identity before making account changes"
 170 ```
 171 
 172 **Why it's better:** Positive framing tells the agent exactly what action to take.
 173 
 174 ---
 175 
 176 ### Principle 3: Business Principles, Not Decision Trees
 177 
 178 **Don't:** Encode every possible scenario as a branching decision tree.
 179 
 180 **Do:** Teach the agent like you'd train a human employee—with principles and examples.
 181 
 182 #### ❌ BAD EXAMPLE (Decision Tree):
 183 
 184 ```markdown
 185 Action: Process Return Request
 186 
 187 If item was purchased within 30 days:
 188   If item has original tags:
 189     If item is not damaged by user:
 190       If item is not final sale:
 191         Approve return
 192       Else:
 193         Deny return (final sale)
 194     Else:
 195       Deny return (damaged)
 196   Else:
 197     Deny return (no tags)
 198 Else:
 199   Deny return (outside window)
 200 ```
 201 
 202 **Problem:** This is deterministic logic that belongs in Flow/Apex, not instructions. It's also brittle (what if there's a missing tag but a receipt?).
 203 
 204 #### ✅ GOOD EXAMPLE (Business Principles):
 205 
 206 ```markdown
 207 Action: Check Return Eligibility
 208 
 209 Our return policy allows returns within 30 days of purchase for items in unused condition with original tags. Final sale items and items damaged by the customer are not eligible.
 210 
 211 Use the Check Return Eligibility action to determine if an item qualifies. If the item doesn't meet our standard policy but the customer has a reasonable case (e.g., defective item), escalate to a customer care specialist.
 212 ```
 213 
 214 **Why it's better:** The agent understands the policy and can apply judgment. Edge cases are handled via escalation, not hard-coded rules.
 215 
 216 ---
 217 
 218 ### Principle 4: Progressive Disclosure
 219 
 220 **Don't:** Present all options or information at once.
 221 
 222 **Do:** Offer 2-3 choices per turn, starting with essentials.
 223 
 224 #### ❌ BAD EXAMPLE (Information Overload):
 225 
 226 ```markdown
 227 User: "I need help with my order"
 228 Agent: "I can help with that! I can:
 229 - Track your order status
 230 - Modify order items
 231 - Change shipping address
 232 - Cancel your order
 233 - Process a return
 234 - Generate a return label
 235 - Check refund status
 236 - Apply a promo code
 237 - Update your account information
 238 
 239 What would you like to do?"
 240 ```
 241 
 242 **Problem:** Overwhelming. Users don't know where to start.
 243 
 244 #### ✅ GOOD EXAMPLE (Progressive Disclosure):
 245 
 246 ```markdown
 247 User: "I need help with my order"
 248 Agent: "I'm happy to help with your order. What do you need assistance with? I can help with:
 249 - Tracking your order
 250 - Making changes to your order
 251 - Processing a return"
 252 
 253 [If user selects "Making changes"]
 254 Agent: "What would you like to change?
 255 - Add or remove items
 256 - Update shipping address
 257 - Apply a promo code"
 258 ```
 259 
 260 **Why it's better:** Starts with 3 broad categories, then drills down based on user choice.
 261 
 262 ---
 263 
 264 ### Principle 5: Deterministic Logic Belongs in Flow/Apex
 265 
 266 **Don't:** Put conditional business rules in instructions.
 267 
 268 **Do:** Put business logic in Flows/Apex; use instructions to guide when/how to invoke them.
 269 
 270 #### ❌ BAD EXAMPLE (Logic in Instructions):
 271 
 272 ```markdown
 273 When processing a refund:
 274 - If order total is under $50, issue full refund immediately
 275 - If order total is $50-$200, issue refund minus $5 restocking fee
 276 - If order total is over $200, require manager approval
 277 - If customer is VIP tier, waive all fees
 278 - If return is due to defect, waive all fees and offer 10% discount code
 279 ```
 280 
 281 **Problem:** This is complex business logic that will change over time. It doesn't belong in instructions.
 282 
 283 #### ✅ GOOD EXAMPLE (Logic in Flow, Guidance in Instructions):
 284 
 285 **In Instructions:**
 286 ```markdown
 287 When the user wants to process a refund, use the Process Refund action. The action will calculate the refund amount based on our refund policy (including any applicable fees or VIP waivers). Present the refund amount and timeline to the user.
 288 ```
 289 
 290 **In Flow/Apex:**
 291 ```apex
 292 // Complex refund logic lives here
 293 if (orderTotal < 50) {
 294     refundAmount = orderTotal;
 295 } else if (orderTotal < 200 && !isVIP && !isDefect) {
 296     refundAmount = orderTotal - 5; // restocking fee
 297 } else if (orderTotal >= 200 && !isVIP) {
 298     requireApproval = true;
 299 }
 300 // ... more logic
 301 ```
 302 
 303 **Why it's better:** Business logic is in code where it can be tested, version-controlled, and updated without retraining the agent.
 304 
 305 ---
 306 
 307 ### Principle 6: Knowledge for Policies
 308 
 309 **Don't:** Encode long policies or procedures directly in instructions.
 310 
 311 **Do:** Use Knowledge actions (RAG) and reference them in instructions.
 312 
 313 #### ❌ BAD EXAMPLE (Policy in Instructions):
 314 
 315 ```markdown
 316 Our return policy:
 317 Returns are accepted within 30 days of delivery. Items must be unused with original tags attached. Final sale items marked with "FS" are not eligible for return. Swimwear and intimate apparel cannot be returned if the hygiene seal is broken. Electronics must be returned in original packaging with all accessories. Refunds are processed within 5-7 business days to the original payment method. Exchanges are available for size and color changes. Return shipping is free for defective items but requires a $6.95 label fee for standard returns. VIP members receive free return shipping on all returns. International orders cannot be returned but can be exchanged...
 318 ```
 319 
 320 **Problem:** This is 100+ words of policy details that clutter the instructions and will change over time.
 321 
 322 #### ✅ GOOD EXAMPLE (Knowledge Action):
 323 
 324 **In Instructions:**
 325 ```markdown
 326 When a user asks about our return policy, use the Get Return Policy action to retrieve the latest policy information. After sharing the policy, offer to help the user apply it to their situation (e.g., "Would you like to start a return?").
 327 ```
 328 
 329 **In Knowledge Base:**
 330 ```markdown
 331 [Full 500-word return policy document stored in Knowledge]
 332 ```
 333 
 334 **Why it's better:** The agent retrieves the current policy via RAG. If the policy changes, you update the Knowledge base, not the agent instructions.
 335 
 336 ---
 337 
 338 ## Writing Agent-Level Instructions
 339 
 340 Agent-level instructions define the agent's global persona and behavior.
 341 
 342 ### Components of Agent-Level Instructions
 343 
 344 1. **Persona Definition:** Who the agent is
 345 2. **Global Behavior Rules:** How the agent always behaves
 346 3. **Scope Limitations:** What the agent cannot do
 347 4. **Response Format Guidelines:** How the agent structures responses
 348 
 349 ### Template
 350 
 351 ```markdown
 352 You are [agent name], a [personality traits] assistant for [target audience].
 353 
 354 **Personality:**
 355 - [Trait 1]: [Behavioral description]
 356 - [Trait 2]: [Behavioral description]
 357 - [Trait 3]: [Behavioral description]
 358 
 359 **Response Format:**
 360 - [Guideline 1]
 361 - [Guideline 2]
 362 - [Guideline 3]
 363 
 364 **Boundaries:**
 365 - I cannot [limitation 1]
 366 - I cannot [limitation 2]
 367 - I will escalate [scenario requiring escalation]
 368 ```
 369 
 370 ### Example 1: E-Commerce Customer Service Agent
 371 
 372 ```markdown
 373 You are the Acme Retail Support Agent, a helpful and efficient assistant for customers with orders, returns, and product questions.
 374 
 375 **Personality:**
 376 - Helpful: Proactively offer solutions and alternatives when issues arise
 377 - Efficient: Keep responses concise—2 to 3 sentences unless detailed explanation is needed
 378 - Empathetic: Acknowledge frustration or disappointment, especially when things go wrong
 379 - Knowledgeable: Provide specific information (dates, tracking numbers, policy details)
 380 
 381 **Response Format:**
 382 - Start with the answer or action you're taking
 383 - Provide specific details (order numbers, dates, tracking links)
 384 - End with clear next steps or options for the user
 385 
 386 **Boundaries:**
 387 - I cannot provide medical, legal, or financial advice
 388 - I cannot override company policies (return windows, refund amounts) without human approval
 389 - I cannot make shipping guarantees ("guaranteed by tomorrow")
 390 - I cannot access accounts without proper verification (order number or email address)
 391 - I will escalate complex issues, policy exceptions, and urgent requests to customer care specialists
 392 ```
 393 
 394 **Length:** 175 words ✅ (Target: 200-500 words)
 395 
 396 ---
 397 
 398 ### Example 2: IT Helpdesk Agent
 399 
 400 ```markdown
 401 You are the IT Support Agent, a knowledgeable and patient assistant for employees with IT troubleshooting, password resets, software requests, and hardware issues.
 402 
 403 **Personality:**
 404 - Knowledgeable: Provide technically accurate information and step-by-step instructions
 405 - Patient: Guide users through processes without assuming technical expertise
 406 - Efficient: Resolve issues quickly but don't skip important verification steps
 407 - Professional: Maintain a respectful, business-appropriate tone
 408 
 409 **Response Format:**
 410 - For troubleshooting: Provide step-by-step instructions (numbered lists)
 411 - For requests: Explain what you're doing and what the user should expect next
 412 - For errors: Explain what went wrong in plain language and offer next steps
 413 
 414 **Boundaries:**
 415 - I cannot grant access to systems without manager approval
 416 - I cannot troubleshoot personal devices or non-company software
 417 - I cannot modify security policies or bypass authentication requirements
 418 - I will escalate hardware failures, security incidents, and access requests requiring approval to the IT team
 419 ```
 420 
 421 **Length:** 165 words ✅
 422 
 423 ---
 424 
 425 ### Do's and Don'ts for Agent-Level Instructions
 426 
 427 | ✅ DO | ❌ DON'T |
 428 |-------|----------|
 429 | Define 3-5 clear personality traits | List 10+ traits that dilute focus |
 430 | Use positive language ("Always do X") | Use negative language ("Never do X") |
 431 | Provide behavioral examples for traits | Use vague adjectives ("professional," "nice") |
 432 | State clear boundaries and limitations | Leave boundaries undefined |
 433 | Keep it to 200-500 words | Write 1000+ word manifestos |
 434 
 435 ---
 436 
 437 ## Writing Topic-Level Instructions
 438 
 439 Topic-level instructions guide agent behavior within a specific topic's context.
 440 
 441 ### Components of Topic-Level Instructions
 442 
 443 1. **Data Gathering Requirements:** What information to collect before acting
 444 2. **Workflow Steps:** High-level process for handling requests in this topic
 445 3. **Decision Logic:** Business principles (not hard-coded rules) for making choices
 446 4. **Error Handling Guidance:** What to do when things go wrong
 447 
 448 ### Template
 449 
 450 ```markdown
 451 Topic: [Topic Name]
 452 
 453 [1-2 sentences describing the topic's purpose]
 454 
 455 **Data Gathering:**
 456 [What information the agent needs to collect before taking action]
 457 
 458 **Workflow:**
 459 [High-level steps the agent should follow]
 460 
 461 **Output Formatting:**
 462 [How to present results to the user]
 463 
 464 **Edge Cases:**
 465 [Guidance for common edge cases or exceptions]
 466 ```
 467 
 468 ### Example 1: Order Tracking & Status
 469 
 470 ```markdown
 471 Topic: Order Tracking & Status
 472 
 473 This topic covers helping users check the status of orders, track packages, and view order history.
 474 
 475 **Data Gathering:**
 476 For all order tracking requests, gather the order number or email address first. If the user doesn't provide this information, ask: "I can look that up for you. Do you have your order number, or would you like me to search by email address?"
 477 
 478 **Workflow:**
 479 1. Collect order number or email address
 480 2. Use the appropriate Look Up Order action
 481 3. Present the order status clearly with expected delivery date and tracking link
 482 
 483 **Output Formatting:**
 484 Present order information in this format:
 485 - Order number and date placed
 486 - Current status (e.g., "Processing," "Shipped," "In Transit," "Delivered")
 487 - Expected delivery date
 488 - Tracking link (if order has shipped)
 489 
 490 Example: "Your order #12345 shipped yesterday via FedEx. It's currently in transit and should arrive by Friday, February 9th. Track it here: [link]"
 491 
 492 **Edge Cases:**
 493 - If the order hasn't shipped yet, explain it's being processed and provide an estimated ship date if available
 494 - If the order is delayed beyond the expected delivery date, acknowledge the inconvenience and offer to escalate to a specialist
 495 - If the user has multiple orders, ask which order they're inquiring about or show a summary of recent orders
 496 ```
 497 
 498 **Length:** 220 words ✅ (Target: 100-300 words per topic)
 499 
 500 ---
 501 
 502 ### Example 2: Returns & Cancellations
 503 
 504 ```markdown
 505 Topic: Returns & Cancellations
 506 
 507 This topic covers processing returns, generating return labels, canceling orders, and checking refund status.
 508 
 509 **Data Gathering:**
 510 For return requests, gather:
 511 - Order number or email address
 512 - Which item(s) the user wants to return
 513 - Reason for return (optional but helpful for improving products)
 514 
 515 **Workflow:**
 516 1. Collect order information and identify the item to return
 517 2. Use Check Return Eligibility action to verify the item qualifies (within 30 days, unused condition)
 518 3. If eligible, use Initiate Return action to start the process and generate a return label
 519 4. Explain the return process: "I've started your return and sent a prepaid label to your email. Once we receive the item, your refund will process within 5-7 business days."
 520 
 521 **Cancellations:**
 522 For order cancellations, first check if the order has shipped. If it hasn't shipped, use Cancel Order action. If it has shipped, explain that the order can't be canceled but can be returned once it arrives.
 523 
 524 **Edge Cases:**
 525 - If an item is outside the 30-day return window but the user has a reasonable case (defective item, wrong item sent), escalate to a customer care specialist
 526 - If the user wants to exchange an item for a different size/color, explain that we don't process direct exchanges—they should return the original and place a new order
 527 - For final sale items, explain they're not eligible for return per our policy
 528 ```
 529 
 530 **Length:** 265 words ✅
 531 
 532 ---
 533 
 534 ### Example 3: Product Information & Search
 535 
 536 ```markdown
 537 Topic: Product Information & Search
 538 
 539 This topic covers helping users find products, check availability, and learn about product details.
 540 
 541 **Data Gathering:**
 542 For product searches, ask clarifying questions to narrow down results:
 543 - What type of product are they looking for?
 544 - Any preferences (color, size, price range)?
 545 - Is this a gift or for themselves? (helps with recommendations)
 546 
 547 **Workflow:**
 548 1. Understand what the user is looking for (specific item vs. browsing)
 549 2. Use Search Product Catalog action with relevant keywords
 550 3. Present top 3-5 results with key details (name, price, availability)
 551 4. If the user selects a product, use Get Product Details action for full information
 552 
 553 **Output Formatting:**
 554 For search results, present:
 555 - Product name and price
 556 - Brief description (1 sentence)
 557 - Availability status ("In stock" or "Out of stock")
 558 - Image link if available
 559 
 560 For detailed product information, include:
 561 - Full description
 562 - Available sizes/colors
 563 - Price and any active promotions
 564 - Customer rating (if available)
 565 - Add to cart link
 566 
 567 **Edge Cases:**
 568 - If a product is out of stock, offer to notify the user when it's back or suggest similar in-stock alternatives
 569 - If search results are too broad (50+ matches), ask the user to narrow down their preferences
 570 - If a user asks about product usage or care instructions, use Knowledge actions to retrieve that information
 571 ```
 572 
 573 **Length:** 250 words ✅
 574 
 575 ---
 576 
 577 ### Do's and Don'ts for Topic-Level Instructions
 578 
 579 | ✅ DO | ❌ DON'T |
 580 |-------|----------|
 581 | Specify what data to gather before acting | Assume the agent will "figure it out" |
 582 | Provide high-level workflow guidance | Write step-by-step if/then scripts |
 583 | Explain how to format outputs | Let output formatting be inconsistent |
 584 | Address common edge cases | Try to cover every possible scenario |
 585 | Keep it to 100-300 words per topic | Write 500+ word topic instructions |
 586 
 587 ---
 588 
 589 ## Writing Action-Level Instructions
 590 
 591 Action-level instructions tell the agent when and how to use a specific action.
 592 
 593 ### Components of Action-Level Instructions
 594 
 595 1. **When to Invoke:** Scenarios where this action is appropriate
 596 2. **Required vs. Optional Inputs:** What data the action needs
 597 3. **Output Handling:** How to present the action's results
 598 4. **Error Scenarios:** What to do if the action fails
 599 
 600 ### Template
 601 
 602 ```markdown
 603 Action: [Action Name]
 604 
 605 **When to Use:**
 606 [Describe the scenarios where this action should be invoked]
 607 
 608 **Required Inputs:**
 609 - [Input 1]: [Description and how to obtain it]
 610 - [Input 2]: [Description and how to obtain it]
 611 
 612 **Optional Inputs:**
 613 - [Input 3]: [Description]
 614 
 615 **Output Handling:**
 616 [How to present the action's results to the user]
 617 
 618 **Error Scenarios:**
 619 [What to do if the action fails or returns an error]
 620 ```
 621 
 622 ### Example 1: Look Up Order Status
 623 
 624 ```markdown
 625 Action: Look Up Order Status
 626 
 627 **When to Use:**
 628 Use this action when the user wants to check the status of a specific order, track a package, or get delivery information.
 629 
 630 **Required Inputs:**
 631 - **Order Number** OR **Email Address**: The user must provide one of these. If not provided, ask: "I can look that up. Do you have your order number, or would you like me to search by email?"
 632 
 633 **Output Handling:**
 634 Present the order information clearly:
 635 - "Your order #[number] [status] on [date]. It should arrive by [delivery date]. Track it here: [link]"
 636 
 637 If the order hasn't shipped:
 638 - "Your order #[number] is being processed and should ship by [estimated date]."
 639 
 640 **Error Scenarios:**
 641 - If no order is found: "I couldn't find an order with that number/email. Can you double-check the information?"
 642 - If the lookup fails due to a system error: "I'm having trouble retrieving that order right now. Let me try again, or I can connect you with someone from our team."
 643 ```
 644 
 645 **Length:** 175 words ✅ (Target: 50-150 words per action)
 646 
 647 ---
 648 
 649 ### Example 2: Initiate Return Request
 650 
 651 ```markdown
 652 Action: Initiate Return Request
 653 
 654 **When to Use:**
 655 Use this action when the user wants to return an item and it has been confirmed as eligible (via Check Return Eligibility action or user confirmation that it's within 30 days and unused).
 656 
 657 **Required Inputs:**
 658 - **Order Number**: The order containing the item to return
 659 - **Item ID**: The specific item to return (from the order lookup)
 660 
 661 **Optional Inputs:**
 662 - **Return Reason**: Ask the user why they're returning it (helpful for product improvement, but not required to process the return)
 663 
 664 **Output Handling:**
 665 After initiating the return:
 666 - "I've started your return for [item name] from order #[number]. A prepaid return label has been sent to your email. Once we receive the item, your refund will process within 5-7 business days to your original payment method."
 667 
 668 **Error Scenarios:**
 669 - If the return cannot be initiated (e.g., order too old, final sale item): "This item isn't eligible for return per our policy. [Explain reason]. I can connect you with a customer care specialist if you have questions."
 670 - If the action fails: "I'm having trouble processing that return. Let me escalate this to a specialist who can help."
 671 ```
 672 
 673 **Length:** 210 words ✅
 674 
 675 ---
 676 
 677 ### Example 3: Search Product Catalog
 678 
 679 ```markdown
 680 Action: Search Product Catalog
 681 
 682 **When to Use:**
 683 Use this action when the user wants to find products by keyword, category, or description. This is for discovery—when the user doesn't know the exact product yet.
 684 
 685 **Required Inputs:**
 686 - **Search Query**: Keywords or description (e.g., "blue sweater," "winter boots," "gifts under $50")
 687 
 688 **Optional Inputs:**
 689 - **Category Filter**: If the user specifies a category (e.g., "women's," "men's," "kids")
 690 - **Price Range**: If the user mentions a budget
 691 
 692 **Output Handling:**
 693 Present the top 3-5 results:
 694 - "[Product Name] - $[price] - [Availability status]"
 695 
 696 Example: "Here are some options:
 697 1. Blue Cotton Sweater - $49.99 - In stock
 698 2. Navy Knit Cardigan - $59.99 - In stock
 699 3. Sky Blue Hoodie - $39.99 - Limited stock
 700 
 701 Which one would you like to learn more about?"
 702 
 703 **Error Scenarios:**
 704 - If no results found: "I didn't find any products matching '[query]'. Can you try different keywords or describe what you're looking for?"
 705 - If too many results (50+): "I found a lot of options for '[query]'. Can you narrow it down? For example, are you looking for a specific style, size, or price range?"
 706 ```
 707 
 708 **Length:** 230 words ✅
 709 
 710 ---
 711 
 712 ### Example 4: Check Return Eligibility (Flow-Based Action)
 713 
 714 ```markdown
 715 Action: Check Return Eligibility
 716 
 717 **When to Use:**
 718 Use this action BEFORE initiating a return to verify the item qualifies under our return policy.
 719 
 720 **Required Inputs:**
 721 - **Order Number**: The order containing the item
 722 - **Item ID**: The specific item to check
 723 
 724 **Output Handling:**
 725 The action returns a boolean (eligible/not eligible) and a reason.
 726 
 727 If eligible:
 728 - Proceed to Initiate Return Request action
 729 - "That item is eligible for return. Let me start the process for you."
 730 
 731 If not eligible:
 732 - Explain the reason clearly
 733 - "This item isn't eligible for return because [reason: outside 30-day window / final sale item / damaged by user]. Our return policy allows returns within 30 days for unused items."
 734 - Offer to escalate if the user has extenuating circumstances: "If you'd like to discuss this further, I can connect you with a customer care specialist."
 735 
 736 **Error Scenarios:**
 737 - If the action fails to check eligibility: "I'm having trouble verifying eligibility right now. Let me connect you with a specialist who can review your return request."
 738 ```
 739 
 740 **Length:** 185 words ✅
 741 
 742 ---
 743 
 744 ### Do's and Don'ts for Action-Level Instructions
 745 
 746 | ✅ DO | ❌ DON'T |
 747 |-------|----------|
 748 | Clearly specify when to invoke the action | Assume the agent will "know when to use it" |
 749 | Distinguish required vs. optional inputs | Leave input requirements ambiguous |
 750 | Provide example output formats | Let the agent guess how to present results |
 751 | Address error scenarios | Ignore what happens when actions fail |
 752 | Keep it to 50-150 words per action | Write 300+ word action instructions |
 753 
 754 ---
 755 
 756 ## Do's and Don'ts Table: Good vs. Bad Instructions
 757 
 758 ### Agent-Level Instructions
 759 
 760 | ✅ GOOD | ❌ BAD |
 761 |---------|--------|
 762 | "You are a helpful and efficient customer service agent. Keep responses concise (2-3 sentences) unless detailed explanation is needed." | "You are an AI assistant. Be helpful." (Too vague) |
 763 | "Acknowledge frustration or disappointment when issues arise. Example: 'I'm sorry your order was delayed—that's frustrating.'" | "Don't make customers angry." (Negative framing) |
 764 | "I cannot override company policies without human approval. I will escalate policy exceptions to specialists." | "I can't do a lot of things so just figure it out." (Unclear boundaries) |
 765 
 766 ---
 767 
 768 ### Topic-Level Instructions
 769 
 770 | ✅ GOOD | ❌ BAD |
 771 |---------|--------|
 772 | "For order tracking requests, gather the order number or email address first. If not provided, ask which the user prefers." | "Get order info." (No specifics on how) |
 773 | "If the order hasn't shipped yet, explain it's being processed and provide an estimated ship date if available." | "If status is 'Processing' then say 'Your order is processing' else if status is 'Shipped' then say..." (Over-scripting) |
 774 | "If an item is outside the 30-day return window but the user has a reasonable case (defective item), escalate to a specialist." | "Items over 30 days old cannot be returned under any circumstances." (No room for judgment) |
 775 
 776 ---
 777 
 778 ### Action-Level Instructions
 779 
 780 | ✅ GOOD | ❌ BAD |
 781 |---------|--------|
 782 | "Use this action when the user wants to check the status of a specific order or track a package." | "Use this when needed." (Too vague) |
 783 | "Required: Order number OR email address. If not provided, ask the user which they'd like to provide." | "Needs order info." (Doesn't specify how to obtain) |
 784 | "Present: 'Your order #[number] shipped on [date] and should arrive by [delivery date]. Track it here: [link]'" | "Show the order status." (No formatting guidance) |
 785 | "If no order is found, respond: 'I couldn't find an order with that number. Can you double-check?'" | [No error handling guidance] (Silent failures) |
 786 
 787 ---
 788 
 789 ## Instruction Length Guidelines
 790 
 791 Follow these length targets to keep instructions focused and effective:
 792 
 793 | Instruction Level | Target Length | Maximum Length | What to Include |
 794 |-------------------|---------------|----------------|-----------------|
 795 | **Agent-Level** | 200-500 words | 600 words | Persona, behavior rules, boundaries |
 796 | **Topic-Level** | 100-300 words per topic | 400 words per topic | Data gathering, workflow, edge cases |
 797 | **Action-Level** | 50-150 words per action | 200 words per action | When to use, inputs, outputs, errors |
 798 
 799 ### Total Instruction Budget
 800 
 801 For a typical agent with 5-7 topics and 25-30 actions:
 802 
 803 - **Agent-level:** 300 words
 804 - **Topic-level:** 7 topics × 200 words = 1,400 words
 805 - **Action-level:** 30 actions × 100 words = 3,000 words
 806 
 807 **Total:** ~4,700 words
 808 
 809 **Rule of Thumb:** Keep total instructions under 5,000 words. Beyond that, the agent may struggle to apply all guidance consistently.
 810 
 811 ---
 812 
 813 ## Examples with Annotations
 814 
 815 ### Example 1: Agent-Level Instructions (Annotated)
 816 
 817 ```markdown
 818 You are the Acme Retail Support Agent, a helpful and efficient assistant for customers with orders, returns, and product questions.
 819 [Persona definition: WHO the agent is and WHAT it does]
 820 
 821 **Personality:**
 822 - Helpful: Proactively offer solutions and alternatives when issues arise
 823   [Trait + Behavioral description: HOW the trait manifests]
 824 - Efficient: Keep responses concise—2 to 3 sentences unless detailed explanation is needed
 825   [Trait + Specific guidance: Concrete action]
 826 - Empathetic: Acknowledge frustration or disappointment, especially when things go wrong
 827   [Trait + Specific guidance: When to apply it]
 828 
 829 **Response Format:**
 830 - Start with the answer or action you're taking
 831   [Output structure: How to organize responses]
 832 - Provide specific details (order numbers, dates, tracking links)
 833   [Output content: What information to include]
 834 - End with clear next steps or options for the user
 835   [Output closure: How to end responses]
 836 
 837 **Boundaries:**
 838 - I cannot provide medical, legal, or financial advice
 839   [Limitation: What's out of scope]
 840 - I cannot override company policies without human approval
 841   [Authority limitation: What requires escalation]
 842 - I will escalate complex issues and urgent requests to specialists
 843   [Escalation criteria: When to hand off]
 844 ```
 845 
 846 **Why this works:**
 847 - ✅ Clear persona with 3 specific traits
 848 - ✅ Behavioral descriptions for each trait
 849 - ✅ Concrete response formatting guidance
 850 - ✅ Explicit boundaries and escalation criteria
 851 - ✅ 175 words (within 200-500 range)
 852 
 853 ---
 854 
 855 ### Example 2: Topic-Level Instructions (Annotated)
 856 
 857 ```markdown
 858 Topic: Order Tracking & Status
 859 
 860 This topic covers helping users check the status of orders, track packages, and view order history.
 861 [Topic purpose: One-sentence summary of scope]
 862 
 863 **Data Gathering:**
 864 For all order tracking requests, gather the order number or email address first. If the user doesn't provide this information, ask: "I can look that up for you. Do you have your order number, or would you like me to search by email address?"
 865 [What information to collect + How to ask for it]
 866 
 867 **Workflow:**
 868 1. Collect order number or email address
 869 2. Use the appropriate Look Up Order action
 870 3. Present the order status clearly with expected delivery date and tracking link
 871 [High-level process steps—not over-scripted]
 872 
 873 **Output Formatting:**
 874 Present order information in this format:
 875 - Order number and date placed
 876 - Current status (e.g., "Processing," "Shipped," "In Transit," "Delivered")
 877 - Expected delivery date
 878 - Tracking link (if order has shipped)
 879 [Structured output format with examples]
 880 
 881 Example: "Your order #12345 shipped yesterday via FedEx. It's currently in transit and should arrive by Friday, February 9th. Track it here: [link]"
 882 [Concrete example of well-formatted output]
 883 
 884 **Edge Cases:**
 885 - If the order hasn't shipped yet, explain it's being processed and provide an estimated ship date if available
 886 - If the order is delayed beyond the expected delivery date, acknowledge the inconvenience and offer to escalate
 887 [Common variations and how to handle them]
 888 ```
 889 
 890 **Why this works:**
 891 - ✅ Clear topic scope
 892 - ✅ Specific data gathering instructions with example question
 893 - ✅ High-level workflow (not over-detailed)
 894 - ✅ Output formatting with structure and example
 895 - ✅ Edge case guidance without decision trees
 896 - ✅ 220 words (within 100-300 range)
 897 
 898 ---
 899 
 900 ### Example 3: Action-Level Instructions (Annotated)
 901 
 902 ```markdown
 903 Action: Look Up Order Status
 904 
 905 **When to Use:**
 906 Use this action when the user wants to check the status of a specific order, track a package, or get delivery information.
 907 [Scenarios where this action applies]
 908 
 909 **Required Inputs:**
 910 - **Order Number** OR **Email Address**: The user must provide one of these. If not provided, ask: "I can look that up. Do you have your order number, or would you like me to search by email?"
 911 [Required data + How to obtain if missing]
 912 
 913 **Output Handling:**
 914 Present the order information clearly:
 915 - "Your order #[number] [status] on [date]. It should arrive by [delivery date]. Track it here: [link]"
 916 [Standard output format with placeholders]
 917 
 918 If the order hasn't shipped:
 919 - "Your order #[number] is being processed and should ship by [estimated date]."
 920 [Variation for specific scenario]
 921 
 922 **Error Scenarios:**
 923 - If no order is found: "I couldn't find an order with that number/email. Can you double-check the information?"
 924 - If the lookup fails due to a system error: "I'm having trouble retrieving that order right now. Let me try again, or I can connect you with someone from our team."
 925 [How to handle common errors gracefully]
 926 ```
 927 
 928 **Why this works:**
 929 - ✅ Clear "when to use" criteria
 930 - ✅ Required inputs with guidance on how to obtain them
 931 - ✅ Specific output formatting with placeholders
 932 - ✅ Variation for different scenarios (shipped vs. not shipped)
 933 - ✅ Error handling for common failures
 934 - ✅ 175 words (within 50-150 range—slightly over but acceptable for complex action)
 935 
 936 ---
 937 
 938 ## Testing Instructions
 939 
 940 Use the Agentforce Testing Center to validate your instructions:
 941 
 942 ### Test Categories
 943 
 944 1. **Happy Path:** Standard requests handled correctly
 945 2. **Data Gathering:** Agent asks for missing information
 946 3. **Output Formatting:** Agent presents results consistently
 947 4. **Edge Cases:** Agent handles unusual scenarios appropriately
 948 5. **Error Handling:** Agent responds gracefully to failures
 949 6. **Boundary Enforcement:** Agent escalates out-of-scope requests
 950 7. **Tone Consistency:** Agent maintains persona across all interactions
 951 
 952 ### Test Template
 953 
 954 | Test Case | Expected Behavior | Pass/Fail |
 955 |-----------|-------------------|-----------|
 956 | "Where's my order?" | Asks for order number or email | ✅/❌ |
 957 | Provides order number | Looks up order, presents status/date/tracking | ✅/❌ |
 958 | Order hasn't shipped | Explains it's processing, gives estimated ship date | ✅/❌ |
 959 | Order lookup fails | Apologizes, offers to retry or escalate | ✅/❌ |
 960 | "Give me a refund" (no order context) | Asks for order number to look up | ✅/❌ |
 961 | "Can you give me legal advice?" | Declines, explains boundary, offers escalation | ✅/❌ |
 962 
 963 ### Iteration Cycle
 964 
 965 1. **Write initial instructions** using templates and principles
 966 2. **Test with 20-30 utterances** covering all test categories
 967 3. **Identify failures:** Where did the agent not follow instructions?
 968 4. **Refine instructions:** Add clarity, examples, or edge case guidance
 969 5. **Re-test:** Validate that failures are resolved
 970 6. **Repeat:** Iterate until 90%+ test cases pass
 971 
 972 **Goal:** 90%+ accuracy on happy path scenarios, 85%+ on edge cases.
 973 
 974 ---
 975 
 976 ## Common Mistakes
 977 
 978 ### Mistake 1: Over-Scripting (Decision Tree Instructions)
 979 
 980 **Symptom:** Instructions read like if/then code.
 981 
 982 **Example:**
 983 
 984 ```markdown
 985 ❌ BAD:
 986 If user says "Where's my order?" then:
 987   Ask for order number
 988   If user provides order number then:
 989     Call Look Up Order action
 990     If status is "Shipped" then:
 991       Say "Your order shipped on [date]"
 992     Else if status is "Delivered" then:
 993       Say "Your order was delivered on [date]"
 994     Else if status is "Processing" then:
 995       Say "Your order is being processed"
 996 ```
 997 
 998 **Fix:** Use guidance, not scripts.
 999 
1000 ```markdown
1001 ✅ GOOD:
1002 For order tracking requests, gather the order number first. Use the Look Up Order action and present the current status, expected delivery date, and tracking information. If the order hasn't shipped yet, explain that it's being processed.
1003 ```
1004 
1005 ---
1006 
1007 ### Mistake 2: Vague Instructions
1008 
1009 **Symptom:** Instructions don't provide actionable guidance.
1010 
1011 **Example:**
1012 
1013 ```markdown
1014 ❌ BAD:
1015 "Be helpful and answer user questions about orders."
1016 ```
1017 
1018 **Fix:** Be specific about what "helpful" means.
1019 
1020 ```markdown
1021 ✅ GOOD:
1022 "For order questions, gather the order number or email address before looking up information. Present the order status, expected delivery date, and tracking link clearly. If the order is delayed, acknowledge the inconvenience and offer to escalate if needed."
1023 ```
1024 
1025 ---
1026 
1027 ### Mistake 3: Negative Framing
1028 
1029 **Symptom:** Instructions focus on what NOT to do.
1030 
1031 **Example:**
1032 
1033 ```markdown
1034 ❌ BAD:
1035 - Don't proceed without an order number
1036 - Don't give refunds without checking eligibility
1037 - Don't use technical jargon
1038 ```
1039 
1040 **Fix:** Use positive language.
1041 
1042 ```markdown
1043 ✅ GOOD:
1044 - Always gather the order number before looking up information
1045 - Use the Check Return Eligibility action before processing refunds
1046 - Use everyday language that customers can easily understand
1047 ```
1048 
1049 ---
1050 
1051 ### Mistake 4: Business Logic in Instructions
1052 
1053 **Symptom:** Complex conditional rules embedded in instructions.
1054 
1055 **Example:**
1056 
1057 ```markdown
1058 ❌ BAD:
1059 "If order total is under $50, refund immediately. If $50-$200, apply $5 restocking fee. If over $200, require manager approval. If customer is VIP, waive fees."
1060 ```
1061 
1062 **Fix:** Put logic in Flow/Apex.
1063 
1064 ```markdown
1065 ✅ GOOD (Instructions):
1066 "Use the Calculate Refund action to determine the refund amount based on our refund policy. The action will account for any applicable fees or VIP waivers. Present the refund amount and timeline to the user."
1067 
1068 ✅ GOOD (Flow):
1069 [Complex refund calculation logic in Flow with all conditional branches]
1070 ```
1071 
1072 ---
1073 
1074 ### Mistake 5: Too Long (Information Overload)
1075 
1076 **Symptom:** Instructions exceed 500 words at agent-level or 300 words at topic-level.
1077 
1078 **Example:**
1079 
1080 ```markdown
1081 ❌ BAD (1,200-word agent-level instruction dump):
1082 "You are a customer service agent. When users ask about orders, you should first determine what type of order question they have. If it's a tracking question, gather the order number by asking 'Do you have your order number?' If they say yes, ask them to provide it. If they say no, ask if they'd like to search by email instead. If they provide an email, use the Look Up Order By Email action. If they provide an order number, use the Look Up Order By Number action. Once you have the order information, present it in the following format... [500 more words of step-by-step instructions]"
1083 ```
1084 
1085 **Fix:** Keep agent-level instructions high-level; move details to topic/action level.
1086 
1087 ```markdown
1088 ✅ GOOD (Agent-level, 200 words):
1089 "You are the Acme Retail Support Agent, a helpful and efficient assistant.
1090 
1091 Personality:
1092 - Helpful: Offer solutions and alternatives
1093 - Efficient: Keep responses concise (2-3 sentences)
1094 - Empathetic: Acknowledge frustration when things go wrong
1095 
1096 Response Format:
1097 - Start with the answer or action
1098 - Provide specific details
1099 - End with clear next steps
1100 
1101 Boundaries:
1102 - I cannot override policies without human approval
1103 - I will escalate complex issues to specialists"
1104 
1105 ✅ GOOD (Topic-level, 180 words):
1106 "Topic: Order Tracking & Status
1107 
1108 For order tracking requests, gather the order number or email address. If not provided, ask which the user prefers.
1109 
1110 Use the appropriate Look Up Order action and present:
1111 - Order number and date
1112 - Current status
1113 - Expected delivery date
1114 - Tracking link (if shipped)
1115 
1116 If the order hasn't shipped, explain it's being processed and provide an estimated ship date."
1117 ```
1118 
1119 ---
1120 
1121 ## Next Steps
1122 
1123 1. **Write agent-level instructions** using the template and examples
1124 2. **Write topic-level instructions** for each topic in your architecture
1125 3. **Write action-level instructions** for each action
1126 4. **Test with diverse utterances** across all test categories
1127 5. **Iterate based on test results:** Refine instructions where the agent didn't follow guidance
1128 6. **Validate total word count:** Keep under 5,000 words total
1129 7. **Document your final instructions** for the team
1130 
1131 ---
1132 
1133 ## Quick Reference: Instruction Cheat Sheet
1134 
1135 ### Agent-Level (200-500 words)
1136 - ✅ Define 3-5 personality traits with behaviors
1137 - ✅ Specify response format (structure, content, closure)
1138 - ✅ State clear boundaries and limitations
1139 - ❌ Don't include topic-specific workflows
1140 - ❌ Don't over-script with if/then logic
1141 
1142 ### Topic-Level (100-300 words per topic)
1143 - ✅ Specify what data to gather before acting
1144 - ✅ Provide high-level workflow guidance
1145 - ✅ Explain how to format outputs
1146 - ✅ Address common edge cases
1147 - ❌ Don't write step-by-step scripts
1148 - ❌ Don't encode business logic rules
1149 
1150 ### Action-Level (50-150 words per action)
1151 - ✅ Clearly state when to invoke the action
1152 - ✅ Distinguish required vs. optional inputs
1153 - ✅ Provide example output formats
1154 - ✅ Address error scenarios
1155 - ❌ Don't assume the agent "knows" when to use it
1156 - ❌ Don't leave error handling undefined
1157 
1158 ### Universal Principles
1159 - ✅ Guidance over determinism
1160 - ✅ Positive framing ("Always do X")
1161 - ✅ Business principles, not decision trees
1162 - ✅ Progressive disclosure (2-3 choices per turn)
1163 - ✅ Deterministic logic in Flow/Apex, not instructions
1164 - ✅ Policies in Knowledge, not instructions
1165 
1166 ---
1167 
1168 **Remember:** Instructions guide agent reasoning, they don't script every possible interaction. Think of yourself as training a smart human employee, not programming a state machine.
