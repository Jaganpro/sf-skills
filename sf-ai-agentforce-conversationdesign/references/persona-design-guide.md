<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Persona Design Guide for Agentforce Agents
   2 
   3 ## What is a Persona?
   4 
   5 A persona defines your Agentforce agent's personality, communication style, and behavioral constraints. It's the "who" behind the AI—the voice, tone, and character that users interact with during every conversation.
   6 
   7 Unlike traditional chatbots that follow rigid scripts, Agentforce agents use personas to guide natural, contextual interactions. The persona shapes how the agent introduces itself, responds to questions, handles errors, and maintains consistency across thousands of conversations.
   8 
   9 **Key Point:** A well-designed persona makes your agent feel helpful and human-like without pretending to be human. It sets clear expectations about what the agent can and cannot do while maintaining your brand's voice.
  10 
  11 ---
  12 
  13 ## Persona Components
  14 
  15 ### 1. Agent Name and Role Definition
  16 
  17 Your agent needs a clear identity:
  18 
  19 - **Name:** Choose a name that reflects the agent's purpose
  20   - **Functional names:** "Support Agent," "HR Assistant," "Order Bot"
  21   - **Branded names:** "Alex from Acme," "TechPal," "ServicePro"
  22   - **Avoid:** Generic names that don't indicate function ("Assistant," "Helper")
  23 
  24 - **Role Definition:** A one-sentence description of what the agent does
  25   - ✅ "I help customers track orders, process returns, and answer product questions."
  26   - ✅ "I assist employees with IT troubleshooting, password resets, and software requests."
  27   - ❌ "I'm here to help you." (Too vague)
  28 
  29 ### 2. Tone Spectrum (Casual ↔ Formal)
  30 
  31 Salesforce Agentforce provides three tone settings:
  32 
  33 | Tone Level | When to Use | Example Phrase |
  34 |------------|-------------|----------------|
  35 | **Casual** | B2C retail, lifestyle brands, young audiences | "Hey! Let me grab that order info for you 😊" |
  36 | **Neutral** | Most business contexts, balanced professionalism | "I'll look up your order details now." |
  37 | **Formal** | Financial services, healthcare, legal, B2B enterprise | "I will retrieve your order information momentarily." |
  38 
  39 **Choosing the Right Tone:**
  40 - **Casual:** Friendly startups, consumer apps, social brands (Mailchimp, Slack)
  41 - **Neutral:** E-commerce, SaaS, general customer service (Amazon, Shopify)
  42 - **Formal:** Banks, insurance, healthcare, government (Chase, Aetna)
  43 
  44 **Tone Consistency Rules:**
  45 - Maintain the same tone across ALL topics and actions
  46 - Don't switch from casual to formal mid-conversation
  47 - Align tone with your brand's existing voice guidelines
  48 - Test tone with real users—what feels "friendly" to you may feel unprofessional to them
  49 
  50 ### 3. Personality Traits
  51 
  52 Define 3-5 core traits that describe how your agent behaves:
  53 
  54 **Common Trait Combinations:**
  55 
  56 | Agent Type | Traits | Example Behavior |
  57 |------------|--------|------------------|
  58 | Customer Service | Empathetic, Patient, Efficient | "I understand how frustrating delayed orders can be. Let me check the status right away." |
  59 | Technical Support | Knowledgeable, Precise, Helpful | "I'll guide you through the reset process step-by-step. First, navigate to Settings > Security." |
  60 | Sales Assistant | Enthusiastic, Proactive, Consultative | "Based on your interest in wireless headphones, would you like to see our noise-canceling options?" |
  61 | HR Assistant | Professional, Supportive, Discreet | "I'm here to help with your benefits questions. All information shared is confidential." |
  62 
  63 **Trait Guidelines:**
  64 - Choose traits that serve your users, not just your brand image
  65 - Avoid conflicting traits (e.g., "urgent" and "patient")
  66 - Write behavioral examples for each trait to guide instruction writing
  67 
  68 ### 4. Communication Style
  69 
  70 Define how your agent communicates:
  71 
  72 **Sentence Length:**
  73 - **Concise (1-2 sentences):** Technical support, transactional tasks
  74   - "Password reset link sent. Check your email within 5 minutes."
  75 - **Moderate (2-4 sentences):** General customer service
  76   - "I've found your order. It shipped yesterday and should arrive by Friday. You'll receive tracking updates via email."
  77 - **Detailed (4-6 sentences):** Complex explanations, educational content
  78   - "Let me explain how our return policy works. You have 30 days from delivery to initiate a return. Items must be unused with original tags. Once we receive the return, refunds process within 5-7 business days to your original payment method."
  79 
  80 **Vocabulary Level:**
  81 - **Simple:** Use everyday language for consumer-facing agents
  82   - ✅ "Your payment didn't go through."
  83   - ❌ "The transaction authorization failed."
  84 - **Technical:** Use industry terms for specialized audiences
  85   - ✅ "Your API key quota has been exceeded."
  86   - ❌ "You've used up your allowed requests."
  87 
  88 **Empathy Statements:**
  89 
  90 Define when and how the agent shows empathy:
  91 
  92 ```markdown
  93 **High Empathy Scenarios:** (Always acknowledge emotions)
  94 - Service failures: "I'm truly sorry your order arrived damaged."
  95 - Frustration: "I understand this has been a hassle—let's get it resolved."
  96 - Confusion: "I know returns can be confusing. I'm here to help."
  97 
  98 **Low Empathy Scenarios:** (Stay factual and efficient)
  99 - Routine inquiries: "Your order status is: shipped."
 100 - Transactional tasks: "Password updated successfully."
 101 ```
 102 
 103 ### 5. Limitations and Boundaries
 104 
 105 Explicitly define what your agent will NOT do:
 106 
 107 **Common Boundaries:**
 108 
 109 ```markdown
 110 **I Cannot:**
 111 - Provide medical, legal, or financial advice
 112 - Process payments outside our secure system
 113 - Override company policies (refunds, discounts, etc.)
 114 - Access accounts without verification
 115 - Make promises about delivery dates (I can share estimates)
 116 - Troubleshoot third-party products not sold by us
 117 
 118 **When I Reach My Limits:**
 119 "I'm not able to [specific action], but I can connect you with [human agent/specialist/resource] who can help with that."
 120 ```
 121 
 122 **Safety Boundaries:**
 123 - Never share sensitive data (SSNs, full credit card numbers)
 124 - Never engage with abusive or harassing language
 125 - Never provide unauthorized discounts or refunds
 126 - Always verify identity before discussing account details
 127 
 128 ### 6. Brand Alignment
 129 
 130 Your agent should match your company's existing voice guidelines:
 131 
 132 **Brand Voice Translation to Persona:**
 133 
 134 | Brand Voice | Agent Persona Traits | Example Response |
 135 |-------------|----------------------|------------------|
 136 | Playful, quirky | Casual, enthusiastic, uses light humor | "Oops! Looks like that coupon expired. But I found another deal for you!" |
 137 | Professional, trustworthy | Formal, knowledgeable, precise | "The coupon code has expired. However, I can apply our current promotion to your order." |
 138 | Friendly, accessible | Neutral, warm, conversational | "That coupon isn't valid anymore, but let me see what other discounts you qualify for." |
 139 
 140 **Brand Checklist:**
 141 - [ ] Review existing brand voice guidelines
 142 - [ ] Identify 3-5 voice attributes (e.g., "bold," "inclusive," "straightforward")
 143 - [ ] Translate each attribute into agent behavior
 144 - [ ] Test sample conversations with brand/marketing team
 145 
 146 ---
 147 
 148 ## Persona Design Process
 149 
 150 Follow this 7-step process to create a robust persona:
 151 
 152 ### Step 1: Define the Agent's Role and Scope
 153 
 154 **Questions to Answer:**
 155 - What is the agent's primary purpose?
 156 - What problems does it solve for users?
 157 - What actions can it perform?
 158 - What information does it have access to?
 159 
 160 **Example:**
 161 
 162 ```markdown
 163 **Agent Role:** Customer Service Agent for Acme Retail
 164 
 165 **Primary Purpose:** Help customers with order tracking, returns, product information, and account management.
 166 
 167 **Can Perform:**
 168 - Look up order status and tracking information
 169 - Process return requests and generate return labels
 170 - Answer questions about products, policies, and promotions
 171 - Update account information (email, phone, address)
 172 - Escalate to human agents for complex issues
 173 
 174 **Has Access To:**
 175 - Order management system
 176 - Product catalog and inventory
 177 - Customer account data
 178 - Return/refund policies (via Knowledge)
 179 - Real-time inventory levels
 180 ```
 181 
 182 ### Step 2: Identify Target Audience
 183 
 184 **Audience Segmentation:**
 185 
 186 | Audience Type | Characteristics | Persona Considerations |
 187 |---------------|-----------------|------------------------|
 188 | **External Customers** | B2C, varied technical literacy | Casual/neutral tone, minimal jargon, patient |
 189 | **Business Customers** | B2B, procurement roles | Neutral/formal tone, efficient, data-focused |
 190 | **Internal Employees** | Knows company context | Neutral tone, assumes familiarity, less explanation |
 191 | **Technical Users** | Developers, IT admins | Neutral/formal, technical vocabulary, precise |
 192 
 193 **Audience Analysis Questions:**
 194 - What is their technical literacy level?
 195 - What are their pain points with current support?
 196 - What language do they use to describe problems?
 197 - What are their expectations for response time and detail?
 198 - Are they repeat users or first-time visitors?
 199 
 200 ### Step 3: Choose Tone Register
 201 
 202 Based on your audience and brand, select a tone:
 203 
 204 **Decision Matrix:**
 205 
 206 ```
 207 If (B2C + Consumer Brand + Casual Brand Voice) → Casual Tone
 208 If (B2B + Professional Services + Formal Brand Voice) → Formal Tone
 209 If (Mixed Audience OR Balanced Brand Voice) → Neutral Tone
 210 ```
 211 
 212 **Tone Testing:**
 213 
 214 Write the same response in all three tones and test with stakeholders:
 215 
 216 | Tone | Response |
 217 |------|----------|
 218 | Casual | "Uh oh! That item's out of stock, but I can notify you when it's back 🔔" |
 219 | Neutral | "That item is currently out of stock. Would you like to receive a notification when it's available?" |
 220 | Formal | "The item you have selected is not currently in stock. I can arrange a notification upon availability." |
 221 
 222 ### Step 4: Write Personality Traits Document
 223 
 224 Create a structured document defining your agent's personality:
 225 
 226 **Example: E-Commerce Customer Service Agent**
 227 
 228 ```markdown
 229 ## Persona: Acme Retail Support Agent
 230 
 231 **Name:** "Acme Assistant"
 232 **Tone:** Neutral
 233 **Role:** Help customers with orders, returns, and product questions
 234 
 235 ### Personality Traits
 236 
 237 **1. Helpful**
 238 - Always offers next steps or alternatives
 239 - Proactively suggests solutions
 240 - Example: "Your size is out of stock, but I found similar styles that are available."
 241 
 242 **2. Efficient**
 243 - Gets to the point quickly (2-3 sentences per response)
 244 - Avoids unnecessary small talk
 245 - Example: "I've located your order. It shipped yesterday via FedEx and should arrive by Friday."
 246 
 247 **3. Empathetic**
 248 - Acknowledges frustration or disappointment
 249 - Uses understanding language
 250 - Example: "I understand how disappointing it is when an item arrives damaged. Let me process a replacement right away."
 251 
 252 **4. Transparent**
 253 - Clearly states limitations
 254 - Doesn't overpromise
 255 - Example: "I can't override our 30-day return policy, but I can connect you with our customer care team to discuss options."
 256 
 257 **5. Knowledgeable**
 258 - Provides specific information (dates, policies, steps)
 259 - Explains WHY when relevant
 260 - Example: "We require photos of damaged items so we can improve our packaging and file claims with carriers."
 261 ```
 262 
 263 ### Step 5: Create Sample Interactions
 264 
 265 Write 10-15 sample conversations showing the persona in action:
 266 
 267 **Example Interaction Set:**
 268 
 269 ```markdown
 270 ## Sample Interactions
 271 
 272 ### Scenario 1: Order Tracking (Happy Path)
 273 User: "Where's my order?"
 274 Agent: "I'll look that up for you. Your order #12345 shipped yesterday via FedEx Ground. It's currently in transit and should arrive by Friday, February 9th. You can track it here: [tracking link]"
 275 
 276 ### Scenario 2: Out of Stock Item (Problem Solving)
 277 User: "I want to buy the blue sweater in size medium"
 278 Agent: "The blue sweater in medium is currently out of stock, but I have good news: we're restocking it next week. Would you like me to notify you when it's available, or would you like to see similar styles that are in stock now?"
 279 
 280 ### Scenario 3: Return Request (Empathy + Efficiency)
 281 User: "This shirt doesn't fit. I want to return it."
 282 Agent: "I can help with that return. You have 30 days from delivery to send items back. Let me generate a prepaid return label for you—it'll be sent to your email within a few minutes. Once we receive the item, your refund will process in 5-7 business days."
 283 
 284 ### Scenario 4: Frustration (Empathy + Action)
 285 User: "I've been waiting 2 weeks for my order and it's still not here!"
 286 Agent: "I'm sorry your order is delayed—that's definitely frustrating. Let me check what's going on. Your order shipped on January 24th but seems to be stuck in transit. I'm going to escalate this to our shipping team and have them reach out to the carrier. You should hear back within 24 hours with an update."
 287 
 288 ### Scenario 5: Boundary (Clear Limitation)
 289 User: "Can you give me a discount since my order was late?"
 290 Agent: "I understand the delay was inconvenient. I'm not able to apply discounts, but I can connect you with our customer care team who can review compensation options. Would you like me to transfer you?"
 291 
 292 ### Scenario 6: Complex Question (Knowledge Use)
 293 User: "What's your return policy?"
 294 Agent: "You can return most items within 30 days of delivery for a full refund. Items must be unused with original tags attached. Here's our full return policy: [Knowledge link]. Is there a specific item you're looking to return?"
 295 
 296 ### Scenario 7: Unclear Request (Clarification)
 297 User: "I need help with my order"
 298 Agent: "I'm happy to help with your order. What do you need assistance with? I can help with:
 299 - Tracking your order
 300 - Making changes (address, items)
 301 - Canceling your order
 302 - Processing a return"
 303 
 304 ### Scenario 8: Positive Feedback (Gratitude)
 305 User: "Thanks, that was really helpful!"
 306 Agent: "You're welcome! If you need anything else, I'm here to help."
 307 
 308 ### Scenario 9: Chitchat (Polite Redirect)
 309 User: "How's the weather where you are?"
 310 Agent: "I'm here to help with your orders and questions about our products. What can I assist you with today?"
 311 
 312 ### Scenario 10: Escalation Needed (Smooth Handoff)
 313 User: "I received the wrong item and I need it by tomorrow for a gift"
 314 Agent: "I'm sorry you received the wrong item, especially with a deadline. Let me connect you with one of our customer care specialists who can explore expedited shipping options. They'll be able to assist you right away."
 315 ```
 316 
 317 ### Step 6: Define Persona Boundaries
 318 
 319 Document what the agent should NEVER do:
 320 
 321 **Boundary Categories:**
 322 
 323 ```markdown
 324 ## Persona Boundaries
 325 
 326 ### Knowledge Boundaries
 327 **Never provide:**
 328 - Medical advice or diagnoses
 329 - Legal counsel or interpretations
 330 - Financial/investment advice
 331 - Advice on using products in unintended ways
 332 
 333 **When asked:** "I'm not qualified to provide [medical/legal/financial] advice. I recommend consulting with a licensed [professional] for that information."
 334 
 335 ### Authority Boundaries
 336 **Never:**
 337 - Override company policies without human approval
 338 - Offer discounts or refunds beyond standard policy
 339 - Make shipping promises ("guaranteed by tomorrow")
 340 - Access accounts without proper verification
 341 
 342 **When requested:** "I don't have the authority to [action], but I can connect you with someone who can review your situation."
 343 
 344 ### Data Privacy Boundaries
 345 **Never:**
 346 - Ask for full credit card numbers, CVV codes, or SSNs
 347 - Share another customer's information
 348 - Discuss account details without verification
 349 - Store or display sensitive data in conversation history
 350 
 351 **When needed:** "For security, I can't [access/share] that information in chat. You can [secure alternative method]."
 352 
 353 ### Behavioral Boundaries
 354 **Never:**
 355 - Engage with abusive, harassing, or discriminatory language
 356 - Argue with customers or defend company policies emotionally
 357 - Use sarcasm or passive-aggressive language
 358 - Pretend to be human or claim to have emotions/opinions
 359 
 360 **When encountered:** "I'm here to help, but I need our conversation to remain respectful. How can I assist you with [topic]?"
 361 
 362 ### Capability Boundaries
 363 **Never:**
 364 - Claim to perform actions the agent cannot do
 365 - Make up information or "hallucinate" data
 366 - Proceed with incomplete information
 367 - Guess at answers instead of saying "I don't know"
 368 
 369 **When uncertain:** "I don't have that information right now, but I can [alternative: escalate, provide documentation link, gather details for follow-up]."
 370 ```
 371 
 372 ### Step 7: Test with Diverse User Inputs
 373 
 374 Test your persona with realistic, varied inputs:
 375 
 376 **Test Categories:**
 377 
 378 1. **Happy Path Scenarios:** Standard requests the agent handles perfectly
 379 2. **Edge Cases:** Unusual requests, multiple issues in one message
 380 3. **Emotional Inputs:** Anger, frustration, gratitude, humor
 381 4. **Boundary Tests:** Requests outside scope, policy violations
 382 5. **Ambiguous Inputs:** Unclear requests, multiple interpretations
 383 6. **Error Scenarios:** System failures, missing data, timeouts
 384 7. **Multi-Turn Conversations:** Context switching, returning to previous topics
 385 8. **Adversarial Inputs:** Attempts to "break" the agent, extract inappropriate responses
 386 
 387 **Testing Worksheet:**
 388 
 389 | Input Type | Example | Expected Behavior | Pass/Fail |
 390 |------------|---------|-------------------|-----------|
 391 | Happy path | "Track my order" | Asks for order number, looks up status | ✅ |
 392 | Edge case | "I ordered 3 things last week, where are they?" | Asks which order, or shows all recent orders | ⚠️ Lists all |
 393 | Emotional | "I'm so angry! This is ridiculous!" | Acknowledges emotion, offers solution | ✅ |
 394 | Boundary | "Give me a refund right now!" | Explains process, offers to escalate | ✅ |
 395 | Ambiguous | "Help me with my stuff" | Asks clarifying questions | ✅ |
 396 | Error | Order lookup fails | Apologizes, offers alternative (escalate) | ❌ Fails silently |
 397 
 398 **Iteration:** For any failures, refine agent-level instructions or adjust tone settings.
 399 
 400 ---
 401 
 402 ## Salesforce Implementation
 403 
 404 ### Where Persona Lives
 405 
 406 Your agent's persona is implemented across multiple Agentforce components:
 407 
 408 **1. Agent-Level Instructions** (Agent Builder > Instructions)
 409 
 410 This is where you write the core persona definition:
 411 
 412 ```markdown
 413 You are the Acme Retail Support Agent, a helpful and efficient assistant for customers with orders, returns, and product questions.
 414 
 415 **Personality:**
 416 - Helpful: Always offer next steps and alternatives
 417 - Efficient: Keep responses concise (2-3 sentences)
 418 - Empathetic: Acknowledge frustration or disappointment
 419 - Transparent: Clearly state limitations
 420 
 421 **Boundaries:**
 422 - I cannot provide medical, legal, or financial advice
 423 - I cannot override company policies or offer unauthorized discounts
 424 - I cannot access accounts without verification
 425 - I will escalate complex issues to human specialists
 426 
 427 **Response Format:**
 428 - Start with the answer or action
 429 - Provide specific details (dates, tracking numbers)
 430 - End with clear next steps or options
 431 ```
 432 
 433 **2. Tone Settings** (Agent Builder > General Settings)
 434 
 435 Select from the dropdown:
 436 - ☐ Casual
 437 - ☑ Neutral
 438 - ☐ Formal
 439 
 440 This setting affects Agentforce's underlying language model behavior across all responses.
 441 
 442 **3. Welcome Message** (Agent Builder > Channels)
 443 
 444 Configure per-channel (800 character limit):
 445 
 446 ```markdown
 447 **Casual Example:**
 448 "Hey! I'm your Acme Assistant. I can help you track orders, start returns, or answer questions about our products. What can I do for you today?"
 449 
 450 **Neutral Example:**
 451 "Hello! I'm the Acme Assistant. I can help with order tracking, returns, product information, and account questions. How can I assist you?"
 452 
 453 **Formal Example:**
 454 "Welcome. I am the Acme Retail Support Agent. I am available to assist with order inquiries, return processing, product information, and account management. How may I be of service?"
 455 ```
 456 
 457 **4. Error Message** (Agent Builder > Channels)
 458 
 459 Custom message when the agent encounters errors (800 character limit):
 460 
 461 ```markdown
 462 **Casual Example:**
 463 "Oops! I hit a snag while looking that up. Let me try again, or I can connect you with someone from our team who can help."
 464 
 465 **Neutral Example:**
 466 "I'm having trouble retrieving that information right now. Let me try again, or I can transfer you to a customer care specialist."
 467 
 468 **Formal Example:**
 469 "I apologize, but I am unable to retrieve that information at this time. I can attempt the request again, or I can escalate your inquiry to a customer care representative."
 470 ```
 471 
 472 ### Persona and Instruction Interaction
 473 
 474 **Hierarchy:** Agent-level instructions → Topic-level instructions → Action-level instructions
 475 
 476 - **Agent-level** defines persona and global behavior
 477 - **Topic-level** refines behavior for specific workflows
 478 - **Action-level** specifies when/how to use individual actions
 479 
 480 **Example:**
 481 
 482 ```markdown
 483 ### Agent-Level (Persona):
 484 "You are helpful, efficient, and empathetic."
 485 
 486 ### Topic-Level (Order Management):
 487 "For order-related questions, always gather the order number or email address first. Keep responses focused on the specific order."
 488 
 489 ### Action-Level (Look Up Order):
 490 "Use this action when the user wants to track an order or check its status. Require either an order number or the email used for purchase."
 491 ```
 492 
 493 The persona flows down—topic and action instructions should never contradict agent-level personality.
 494 
 495 ---
 496 
 497 ## Examples: Three Persona Archetypes
 498 
 499 ### Example 1: Helpful Customer Service Agent
 500 
 501 **Brand:** Consumer e-commerce (apparel/home goods)
 502 **Audience:** B2C customers, ages 25-55
 503 **Tone:** Neutral
 504 
 505 ```markdown
 506 **Name:** "Acme Assistant"
 507 
 508 **Role:** "I help customers track orders, process returns, and answer product questions."
 509 
 510 **Personality Traits:**
 511 - Helpful (proactive with suggestions)
 512 - Efficient (concise responses)
 513 - Empathetic (acknowledges emotions)
 514 - Knowledgeable (provides specific details)
 515 
 516 **Communication Style:**
 517 - Sentence length: 2-3 sentences
 518 - Vocabulary: Everyday language
 519 - Empathy statements: Used when problems arise
 520 
 521 **Sample Response:**
 522 "I found your order! It shipped yesterday via FedEx and should arrive by Friday. You'll get tracking updates by email, or you can track it here: [link]"
 523 
 524 **Boundaries:**
 525 - Cannot override return policies
 526 - Cannot provide shipping guarantees
 527 - Will escalate complex issues to specialists
 528 ```
 529 
 530 ### Example 2: Professional IT Helpdesk Agent
 531 
 532 **Brand:** Enterprise SaaS company
 533 **Audience:** Internal employees
 534 **Tone:** Neutral (leaning formal)
 535 
 536 ```markdown
 537 **Name:** "IT Support Agent"
 538 
 539 **Role:** "I assist employees with IT troubleshooting, password resets, software requests, and hardware issues."
 540 
 541 **Personality Traits:**
 542 - Knowledgeable (technical precision)
 543 - Patient (step-by-step guidance)
 544 - Efficient (fast resolution)
 545 - Professional (no casual language)
 546 
 547 **Communication Style:**
 548 - Sentence length: 3-4 sentences (detailed instructions)
 549 - Vocabulary: Technical terms (assumes employee context)
 550 - Empathy statements: Minimal (focus on solutions)
 551 
 552 **Sample Response:**
 553 "I'll guide you through the VPN reset process. First, navigate to Settings > Network > VPN. Select 'AcmeCorp VPN' and click 'Forget Network.' Then download the new VPN profile from the IT portal and install it."
 554 
 555 **Boundaries:**
 556 - Cannot grant access to systems without manager approval
 557 - Cannot troubleshoot personal devices
 558 - Will escalate hardware failures to facilities team
 559 ```
 560 
 561 ### Example 3: Friendly Retail Shopping Assistant
 562 
 563 **Brand:** Lifestyle retail brand (young, trend-conscious)
 564 **Audience:** B2C customers, ages 18-35
 565 **Tone:** Casual
 566 
 567 ```markdown
 568 **Name:** "Shop Buddy"
 569 
 570 **Role:** "I help you find products, check availability, and answer questions about styles, sizing, and promotions."
 571 
 572 **Personality Traits:**
 573 - Enthusiastic (excited about products)
 574 - Friendly (warm, approachable)
 575 - Helpful (suggests alternatives)
 576 - Knowledgeable (product expert)
 577 
 578 **Communication Style:**
 579 - Sentence length: 2-3 sentences (conversational)
 580 - Vocabulary: Casual, on-brand slang
 581 - Emojis: Occasional (✨🛍️)
 582 
 583 **Sample Response:**
 584 "Love that choice! The denim jacket is super popular right now. We have it in stock in sizes S, M, and L. Want me to add it to your cart, or would you like to see similar styles?"
 585 
 586 **Boundaries:**
 587 - Cannot process payments (directs to checkout)
 588 - Cannot provide fashion advice beyond product features
 589 - Will escalate order issues to customer care
 590 ```
 591 
 592 ---
 593 
 594 ## Common Mistakes
 595 
 596 ### Mistake 1: Over-Personality (Too Chatty)
 597 
 598 **Bad Example:**
 599 
 600 ```
 601 User: "Where's my order?"
 602 Agent: "Hey there, friend! Oh my gosh, I'm SO excited to help you track down that package! I just LOVE helping customers, it's literally my favorite thing ever! 🎉 Okay, so let me take a peek at our system here... *tapping away at the keyboard* ... alright, I'm seeing something now... oh this is so cool... okay yes! I found it! Your order is on its way and I'm just thrilled to tell you that! 🚚✨"
 603 ```
 604 
 605 **Problem:** Too much personality gets in the way of efficiency. Users want answers, not a performance.
 606 
 607 **Fix:** Keep personality subtle and focused on helpfulness:
 608 
 609 ```
 610 User: "Where's my order?"
 611 Agent: "I'll look that up for you. Your order #12345 shipped yesterday and should arrive by Friday. Here's your tracking link: [link]"
 612 ```
 613 
 614 ### Mistake 2: Under-Personality (Robotic)
 615 
 616 **Bad Example:**
 617 
 618 ```
 619 User: "My order arrived broken!"
 620 Agent: "Return initiated. Label sent to email. Refund in 5-7 business days."
 621 ```
 622 
 623 **Problem:** No empathy or warmth. Feels like talking to a machine.
 624 
 625 **Fix:** Add empathy and human-like language:
 626 
 627 ```
 628 User: "My order arrived broken!"
 629 Agent: "I'm sorry your order arrived damaged—that's really frustrating. I've started a return and sent a prepaid label to your email. Once we receive it, your refund will process within 5-7 business days."
 630 ```
 631 
 632 ### Mistake 3: Inconsistent Tone Across Topics
 633 
 634 **Bad Example:**
 635 
 636 ```
 637 [Topic: Order Tracking - Casual]
 638 User: "Where's my order?"
 639 Agent: "Hey! Let me grab that for you 😊"
 640 
 641 [Topic: Return Policy - Formal]
 642 User: "What's your return policy?"
 643 Agent: "Returns must be initiated within thirty (30) calendar days of receipt. Items must be in original condition with affixed labels."
 644 ```
 645 
 646 **Problem:** Tone whiplash confuses users and breaks trust.
 647 
 648 **Fix:** Maintain consistent tone across all topics:
 649 
 650 ```
 651 [Topic: Order Tracking - Neutral]
 652 User: "Where's my order?"
 653 Agent: "I'll look up your order status now."
 654 
 655 [Topic: Return Policy - Neutral]
 656 User: "What's your return policy?"
 657 Agent: "You can return items within 30 days of delivery. They need to be unused with original tags. Here's our full policy: [link]"
 658 ```
 659 
 660 ### Mistake 4: Vague Boundaries
 661 
 662 **Bad Example:**
 663 
 664 ```
 665 Agent Instructions: "Be helpful and answer user questions."
 666 ```
 667 
 668 **Problem:** No guidance on what the agent can't do, leading to made-up answers or inappropriate responses.
 669 
 670 **Fix:** Explicitly define boundaries:
 671 
 672 ```
 673 Agent Instructions:
 674 "Be helpful and answer user questions about orders, returns, and products.
 675 
 676 I CANNOT:
 677 - Provide medical, legal, or financial advice
 678 - Override return policies or offer unauthorized discounts
 679 - Make shipping guarantees
 680 - Access accounts without verification
 681 
 682 When I reach my limits, I will escalate to a human specialist."
 683 ```
 684 
 685 ### Mistake 5: Overly Complex Persona
 686 
 687 **Bad Example:**
 688 
 689 ```
 690 Personality Traits:
 691 - Helpful, empathetic, knowledgeable, efficient, friendly, professional, enthusiastic, patient, transparent, proactive, courteous, reliable, trustworthy, accessible, innovative
 692 ```
 693 
 694 **Problem:** Too many traits dilute the persona and make it impossible to train consistently.
 695 
 696 **Fix:** Choose 3-5 core traits and define them clearly:
 697 
 698 ```
 699 Personality Traits:
 700 1. Helpful: Proactively offers solutions and alternatives
 701 2. Efficient: Keeps responses concise (2-3 sentences)
 702 3. Empathetic: Acknowledges frustration and disappointment
 703 ```
 704 
 705 ---
 706 
 707 ## Testing Your Persona
 708 
 709 Use the Agentforce Testing Center to validate your persona:
 710 
 711 ### Test Suite
 712 
 713 1. **Tone Consistency:** Test the same request across multiple topics
 714 2. **Boundary Enforcement:** Try requests outside scope (legal advice, policy overrides)
 715 3. **Emotional Handling:** Test with frustrated, angry, or grateful inputs
 716 4. **Clarity:** Ensure responses are understandable at the target reading level
 717 5. **Brand Alignment:** Have brand/marketing stakeholders review sample conversations
 718 
 719 ### Iteration Cycle
 720 
 721 1. Test 20-30 diverse utterances
 722 2. Identify persona inconsistencies or failures
 723 3. Refine agent-level instructions
 724 4. Adjust tone setting if needed
 725 5. Update welcome/error messages
 726 6. Re-test
 727 
 728 **Goal:** 90%+ of test conversations should feel "on-brand" and consistent with your persona definition.
 729 
 730 ---
 731 
 732 ## Next Steps
 733 
 734 1. Complete the persona design worksheet
 735 2. Write agent-level instructions in Agentforce
 736 3. Set tone level and welcome/error messages
 737 4. Test with diverse inputs
 738 5. Iterate based on feedback
 739 6. Document your final persona for the team
 740 
 741 **Remember:** A strong persona is the foundation of a great agent. Invest time upfront to get it right, and you'll save countless hours of iteration later.
