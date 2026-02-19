<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
# Instruction Writing Guide for Agentforce Agents

## The Three-Level Instruction Framework

Agentforce agents are guided by instructions at three distinct levels, each serving a different purpose:

```
Agent-Level Instructions
    ↓ (Apply to EVERYTHING)
Topic-Level Instructions
    ↓ (Apply to one topic)
Action-Level Instructions
    ↓ (Apply to one action)
```

### Level 1: Agent-Level Instructions

**What:** Global persona, behavior rules, and limitations that apply to ALL topics.

**Where:** Agent Builder > Instructions tab

**Purpose:** Define WHO the agent is and HOW it behaves universally.

**Example:**
```markdown
You are the Acme Retail Support Agent, a helpful and efficient assistant for customers.

**Personality:**
- Helpful: Always offer solutions and alternatives
- Efficient: Keep responses concise (2-3 sentences)
- Empathetic: Acknowledge frustration or disappointment

**Boundaries:**
- I cannot provide medical, legal, or financial advice
- I cannot override company policies
- I will escalate complex issues to human specialists
```

---

### Level 2: Topic-Level Instructions

**What:** Workflow logic, data gathering requirements, and behavior specific to ONE topic.

**Where:** Agent Builder > Topics > [Specific Topic] > Instructions

**Purpose:** Guide how the agent operates within a specific domain (e.g., order tracking, returns).

**Example:**
```markdown
Topic: Order Tracking & Status

For all order tracking requests, gather the order number or email address first. If not provided, ask: "I can look that up for you. Do you have your order number, or would you like me to search by email address?"

Present order status in this format:
- Order number and date
- Current status
- Expected delivery date
- Tracking link (if available)
```

---

### Level 3: Action-Level Instructions

**What:** When and how to use a SPECIFIC action, required inputs, and output handling.

**Where:** Agent Builder > Actions > [Specific Action] > Instructions

**Purpose:** Tell the agent when to invoke an action and how to present results.

**Example:**
```markdown
Action: Look Up Order Status

**When to Use:**
Use this action when the user wants to check the status of a specific order.

**Required Inputs:**
- Order number OR email address (ask if not provided)

**Output Handling:**
Present the order status, expected delivery date, and tracking link. If the order hasn't shipped yet, explain it's being processed and provide an estimated ship date.
```

---

### How the Three Levels Work Together

**Example Scenario: User asks "Where's my order?"**

1. **Agent-Level Instructions:** "Be helpful and empathetic" → Agent uses friendly tone
2. **Topic-Level Instructions:** "Gather order number first" → Agent asks for order number
3. **Action-Level Instructions:** "Present status, delivery date, and tracking link" → Agent formats response correctly

**Result:**
```
Agent: "I'll look that up for you. Do you have your order number, or would you like me to search by email address?"

User: "Order number 12345"

Agent: [Invokes Look Up Order action]
Agent: "Your order #12345 shipped yesterday via FedEx. It should arrive by Friday, February 9th. Here's your tracking link: [link]"
```

Each level contributes:
- **Agent-level:** Helpful, friendly tone
- **Topic-level:** Asked for order number before searching
- **Action-level:** Formatted output correctly (status, date, link)

---

## Core Principles

### Principle 1: Guidance Over Determinism

**Don't:** Write instructions like a state machine with if/then logic.

**Do:** Provide principles and let the agent reason.

#### ❌ BAD EXAMPLE (Over-Deterministic):

```markdown
If user says "Where's my order?" then:
  1. Ask for order number
  2. If user provides order number, call Look Up Order action
  3. If user doesn't provide order number, ask again
  4. If order status is "Shipped", say "Your order shipped on [date]"
  5. If order status is "Delivered", say "Your order was delivered on [date]"
  6. If order status is "Processing", say "Your order is being processed"
  7. If user asks follow-up question, determine topic and respond accordingly
```

**Problem:** This is scripting, not guiding. The agent becomes brittle and can't handle variations.

#### ✅ GOOD EXAMPLE (Guidance):

```markdown
For order tracking requests, gather the order number or email address before looking up the order. Present the current status, expected delivery date, and tracking information clearly. If the order hasn't shipped yet, explain that it's being processed.
```

**Why it's better:** The agent understands the GOAL (provide order status) and the REQUIREMENTS (need order number, present certain information) without being locked into a rigid script.

---

### Principle 2: Positive Framing

**Don't:** Write instructions with negative language ("don't do X").

**Do:** Write instructions with positive language ("always do Y").

#### ❌ BAD EXAMPLES:

```markdown
- "Don't proceed without an order number"
- "Never give refunds without manager approval"
- "Don't use technical jargon"
- "Don't skip verification steps"
```

**Problem:** Negative framing focuses on what NOT to do, which is less actionable than what TO do.

#### ✅ GOOD EXAMPLES:

```markdown
- "Always gather the order number before looking up order information"
- "Escalate refund requests beyond standard policy to a manager"
- "Use everyday language that customers can easily understand"
- "Verify the user's identity before making account changes"
```

**Why it's better:** Positive framing tells the agent exactly what action to take.

---

### Principle 3: Business Principles, Not Decision Trees

**Don't:** Encode every possible scenario as a branching decision tree.

**Do:** Teach the agent like you'd train a human employee—with principles and examples.

#### ❌ BAD EXAMPLE (Decision Tree):

```markdown
Action: Process Return Request

If item was purchased within 30 days:
  If item has original tags:
    If item is not damaged by user:
      If item is not final sale:
        Approve return
      Else:
        Deny return (final sale)
    Else:
      Deny return (damaged)
  Else:
    Deny return (no tags)
Else:
  Deny return (outside window)
```

**Problem:** This is deterministic logic that belongs in Flow/Apex, not instructions. It's also brittle (what if there's a missing tag but a receipt?).

#### ✅ GOOD EXAMPLE (Business Principles):

```markdown
Action: Check Return Eligibility

Our return policy allows returns within 30 days of purchase for items in unused condition with original tags. Final sale items and items damaged by the customer are not eligible.

Use the Check Return Eligibility action to determine if an item qualifies. If the item doesn't meet our standard policy but the customer has a reasonable case (e.g., defective item), escalate to a customer care specialist.
```

**Why it's better:** The agent understands the policy and can apply judgment. Edge cases are handled via escalation, not hard-coded rules.

---

### Principle 4: Progressive Disclosure

**Don't:** Present all options or information at once.

**Do:** Offer 2-3 choices per turn, starting with essentials.

#### ❌ BAD EXAMPLE (Information Overload):

```markdown
User: "I need help with my order"
Agent: "I can help with that! I can:
- Track your order status
- Modify order items
- Change shipping address
- Cancel your order
- Process a return
- Generate a return label
- Check refund status
- Apply a promo code
- Update your account information

What would you like to do?"
```

**Problem:** Overwhelming. Users don't know where to start.

#### ✅ GOOD EXAMPLE (Progressive Disclosure):

```markdown
User: "I need help with my order"
Agent: "I'm happy to help with your order. What do you need assistance with? I can help with:
- Tracking your order
- Making changes to your order
- Processing a return"

[If user selects "Making changes"]
Agent: "What would you like to change?
- Add or remove items
- Update shipping address
- Apply a promo code"
```

**Why it's better:** Starts with 3 broad categories, then drills down based on user choice.

---

### Principle 5: Deterministic Logic Belongs in Flow/Apex

**Don't:** Put conditional business rules in instructions.

**Do:** Put business logic in Flows/Apex; use instructions to guide when/how to invoke them.

#### ❌ BAD EXAMPLE (Logic in Instructions):

```markdown
When processing a refund:
- If order total is under $50, issue full refund immediately
- If order total is $50-$200, issue refund minus $5 restocking fee
- If order total is over $200, require manager approval
- If customer is VIP tier, waive all fees
- If return is due to defect, waive all fees and offer 10% discount code
```

**Problem:** This is complex business logic that will change over time. It doesn't belong in instructions.

#### ✅ GOOD EXAMPLE (Logic in Flow, Guidance in Instructions):

**In Instructions:**
```markdown
When the user wants to process a refund, use the Process Refund action. The action will calculate the refund amount based on our refund policy (including any applicable fees or VIP waivers). Present the refund amount and timeline to the user.
```

**In Flow/Apex:**
```apex
// Complex refund logic lives here
if (orderTotal < 50) {
    refundAmount = orderTotal;
} else if (orderTotal < 200 && !isVIP && !isDefect) {
    refundAmount = orderTotal - 5; // restocking fee
} else if (orderTotal >= 200 && !isVIP) {
    requireApproval = true;
}
// ... more logic
```

**Why it's better:** Business logic is in code where it can be tested, version-controlled, and updated without retraining the agent.

---

### Principle 6: Knowledge for Policies

**Don't:** Encode long policies or procedures directly in instructions.

**Do:** Use Knowledge actions (RAG) and reference them in instructions.

#### ❌ BAD EXAMPLE (Policy in Instructions):

```markdown
Our return policy:
Returns are accepted within 30 days of delivery. Items must be unused with original tags attached. Final sale items marked with "FS" are not eligible for return. Swimwear and intimate apparel cannot be returned if the hygiene seal is broken. Electronics must be returned in original packaging with all accessories. Refunds are processed within 5-7 business days to the original payment method. Exchanges are available for size and color changes. Return shipping is free for defective items but requires a $6.95 label fee for standard returns. VIP members receive free return shipping on all returns. International orders cannot be returned but can be exchanged...
```

**Problem:** This is 100+ words of policy details that clutter the instructions and will change over time.

#### ✅ GOOD EXAMPLE (Knowledge Action):

**In Instructions:**
```markdown
When a user asks about our return policy, use the Get Return Policy action to retrieve the latest policy information. After sharing the policy, offer to help the user apply it to their situation (e.g., "Would you like to start a return?").
```

**In Knowledge Base:**
```markdown
[Full 500-word return policy document stored in Knowledge]
```

**Why it's better:** The agent retrieves the current policy via RAG. If the policy changes, you update the Knowledge base, not the agent instructions.

---

## Writing Agent-Level Instructions

Agent-level instructions define the agent's global persona and behavior.

### Components of Agent-Level Instructions

1. **Persona Definition:** Who the agent is
2. **Global Behavior Rules:** How the agent always behaves
3. **Scope Limitations:** What the agent cannot do
4. **Response Format Guidelines:** How the agent structures responses

### Template

```markdown
You are [agent name], a [personality traits] assistant for [target audience].

**Personality:**
- [Trait 1]: [Behavioral description]
- [Trait 2]: [Behavioral description]
- [Trait 3]: [Behavioral description]

**Response Format:**
- [Guideline 1]
- [Guideline 2]
- [Guideline 3]

**Boundaries:**
- I cannot [limitation 1]
- I cannot [limitation 2]
- I will escalate [scenario requiring escalation]
```

### Example 1: E-Commerce Customer Service Agent

```markdown
You are the Acme Retail Support Agent, a helpful and efficient assistant for customers with orders, returns, and product questions.

**Personality:**
- Helpful: Proactively offer solutions and alternatives when issues arise
- Efficient: Keep responses concise—2 to 3 sentences unless detailed explanation is needed
- Empathetic: Acknowledge frustration or disappointment, especially when things go wrong
- Knowledgeable: Provide specific information (dates, tracking numbers, policy details)

**Response Format:**
- Start with the answer or action you're taking
- Provide specific details (order numbers, dates, tracking links)
- End with clear next steps or options for the user

**Boundaries:**
- I cannot provide medical, legal, or financial advice
- I cannot override company policies (return windows, refund amounts) without human approval
- I cannot make shipping guarantees ("guaranteed by tomorrow")
- I cannot access accounts without proper verification (order number or email address)
- I will escalate complex issues, policy exceptions, and urgent requests to customer care specialists
```

**Length:** 175 words ✅ (Target: 200-500 words)

---

### Example 2: IT Helpdesk Agent

```markdown
You are the IT Support Agent, a knowledgeable and patient assistant for employees with IT troubleshooting, password resets, software requests, and hardware issues.

**Personality:**
- Knowledgeable: Provide technically accurate information and step-by-step instructions
- Patient: Guide users through processes without assuming technical expertise
- Efficient: Resolve issues quickly but don't skip important verification steps
- Professional: Maintain a respectful, business-appropriate tone

**Response Format:**
- For troubleshooting: Provide step-by-step instructions (numbered lists)
- For requests: Explain what you're doing and what the user should expect next
- For errors: Explain what went wrong in plain language and offer next steps

**Boundaries:**
- I cannot grant access to systems without manager approval
- I cannot troubleshoot personal devices or non-company software
- I cannot modify security policies or bypass authentication requirements
- I will escalate hardware failures, security incidents, and access requests requiring approval to the IT team
```

**Length:** 165 words ✅

---

### Do's and Don'ts for Agent-Level Instructions

| ✅ DO | ❌ DON'T |
|-------|----------|
| Define 3-5 clear personality traits | List 10+ traits that dilute focus |
| Use positive language ("Always do X") | Use negative language ("Never do X") |
| Provide behavioral examples for traits | Use vague adjectives ("professional," "nice") |
| State clear boundaries and limitations | Leave boundaries undefined |
| Keep it to 200-500 words | Write 1000+ word manifestos |

---

## Writing Topic-Level Instructions

Topic-level instructions guide agent behavior within a specific topic's context.

### Components of Topic-Level Instructions

1. **Data Gathering Requirements:** What information to collect before acting
2. **Workflow Steps:** High-level process for handling requests in this topic
3. **Decision Logic:** Business principles (not hard-coded rules) for making choices
4. **Error Handling Guidance:** What to do when things go wrong

### Template

```markdown
Topic: [Topic Name]

[1-2 sentences describing the topic's purpose]

**Data Gathering:**
[What information the agent needs to collect before taking action]

**Workflow:**
[High-level steps the agent should follow]

**Output Formatting:**
[How to present results to the user]

**Edge Cases:**
[Guidance for common edge cases or exceptions]
```

### Example 1: Order Tracking & Status

```markdown
Topic: Order Tracking & Status

This topic covers helping users check the status of orders, track packages, and view order history.

**Data Gathering:**
For all order tracking requests, gather the order number or email address first. If the user doesn't provide this information, ask: "I can look that up for you. Do you have your order number, or would you like me to search by email address?"

**Workflow:**
1. Collect order number or email address
2. Use the appropriate Look Up Order action
3. Present the order status clearly with expected delivery date and tracking link

**Output Formatting:**
Present order information in this format:
- Order number and date placed
- Current status (e.g., "Processing," "Shipped," "In Transit," "Delivered")
- Expected delivery date
- Tracking link (if order has shipped)

Example: "Your order #12345 shipped yesterday via FedEx. It's currently in transit and should arrive by Friday, February 9th. Track it here: [link]"

**Edge Cases:**
- If the order hasn't shipped yet, explain it's being processed and provide an estimated ship date if available
- If the order is delayed beyond the expected delivery date, acknowledge the inconvenience and offer to escalate to a specialist
- If the user has multiple orders, ask which order they're inquiring about or show a summary of recent orders
```

**Length:** 220 words ✅ (Target: 100-300 words per topic)

---

### Example 2: Returns & Cancellations

```markdown
Topic: Returns & Cancellations

This topic covers processing returns, generating return labels, canceling orders, and checking refund status.

**Data Gathering:**
For return requests, gather:
- Order number or email address
- Which item(s) the user wants to return
- Reason for return (optional but helpful for improving products)

**Workflow:**
1. Collect order information and identify the item to return
2. Use Check Return Eligibility action to verify the item qualifies (within 30 days, unused condition)
3. If eligible, use Initiate Return action to start the process and generate a return label
4. Explain the return process: "I've started your return and sent a prepaid label to your email. Once we receive the item, your refund will process within 5-7 business days."

**Cancellations:**
For order cancellations, first check if the order has shipped. If it hasn't shipped, use Cancel Order action. If it has shipped, explain that the order can't be canceled but can be returned once it arrives.

**Edge Cases:**
- If an item is outside the 30-day return window but the user has a reasonable case (defective item, wrong item sent), escalate to a customer care specialist
- If the user wants to exchange an item for a different size/color, explain that we don't process direct exchanges—they should return the original and place a new order
- For final sale items, explain they're not eligible for return per our policy
```

**Length:** 265 words ✅

---

### Example 3: Product Information & Search

```markdown
Topic: Product Information & Search

This topic covers helping users find products, check availability, and learn about product details.

**Data Gathering:**
For product searches, ask clarifying questions to narrow down results:
- What type of product are they looking for?
- Any preferences (color, size, price range)?
- Is this a gift or for themselves? (helps with recommendations)

**Workflow:**
1. Understand what the user is looking for (specific item vs. browsing)
2. Use Search Product Catalog action with relevant keywords
3. Present top 3-5 results with key details (name, price, availability)
4. If the user selects a product, use Get Product Details action for full information

**Output Formatting:**
For search results, present:
- Product name and price
- Brief description (1 sentence)
- Availability status ("In stock" or "Out of stock")
- Image link if available

For detailed product information, include:
- Full description
- Available sizes/colors
- Price and any active promotions
- Customer rating (if available)
- Add to cart link

**Edge Cases:**
- If a product is out of stock, offer to notify the user when it's back or suggest similar in-stock alternatives
- If search results are too broad (50+ matches), ask the user to narrow down their preferences
- If a user asks about product usage or care instructions, use Knowledge actions to retrieve that information
```

**Length:** 250 words ✅

---

### Do's and Don'ts for Topic-Level Instructions

| ✅ DO | ❌ DON'T |
|-------|----------|
| Specify what data to gather before acting | Assume the agent will "figure it out" |
| Provide high-level workflow guidance | Write step-by-step if/then scripts |
| Explain how to format outputs | Let output formatting be inconsistent |
| Address common edge cases | Try to cover every possible scenario |
| Keep it to 100-300 words per topic | Write 500+ word topic instructions |

---

## Writing Action-Level Instructions

Action-level instructions tell the agent when and how to use a specific action.

### Components of Action-Level Instructions

1. **When to Invoke:** Scenarios where this action is appropriate
2. **Required vs. Optional Inputs:** What data the action needs
3. **Output Handling:** How to present the action's results
4. **Error Scenarios:** What to do if the action fails

### Template

```markdown
Action: [Action Name]

**When to Use:**
[Describe the scenarios where this action should be invoked]

**Required Inputs:**
- [Input 1]: [Description and how to obtain it]
- [Input 2]: [Description and how to obtain it]

**Optional Inputs:**
- [Input 3]: [Description]

**Output Handling:**
[How to present the action's results to the user]

**Error Scenarios:**
[What to do if the action fails or returns an error]
```

### Example 1: Look Up Order Status

```markdown
Action: Look Up Order Status

**When to Use:**
Use this action when the user wants to check the status of a specific order, track a package, or get delivery information.

**Required Inputs:**
- **Order Number** OR **Email Address**: The user must provide one of these. If not provided, ask: "I can look that up. Do you have your order number, or would you like me to search by email?"

**Output Handling:**
Present the order information clearly:
- "Your order #[number] [status] on [date]. It should arrive by [delivery date]. Track it here: [link]"

If the order hasn't shipped:
- "Your order #[number] is being processed and should ship by [estimated date]."

**Error Scenarios:**
- If no order is found: "I couldn't find an order with that number/email. Can you double-check the information?"
- If the lookup fails due to a system error: "I'm having trouble retrieving that order right now. Let me try again, or I can connect you with someone from our team."
```

**Length:** 175 words ✅ (Target: 50-150 words per action)

---

### Example 2: Initiate Return Request

```markdown
Action: Initiate Return Request

**When to Use:**
Use this action when the user wants to return an item and it has been confirmed as eligible (via Check Return Eligibility action or user confirmation that it's within 30 days and unused).

**Required Inputs:**
- **Order Number**: The order containing the item to return
- **Item ID**: The specific item to return (from the order lookup)

**Optional Inputs:**
- **Return Reason**: Ask the user why they're returning it (helpful for product improvement, but not required to process the return)

**Output Handling:**
After initiating the return:
- "I've started your return for [item name] from order #[number]. A prepaid return label has been sent to your email. Once we receive the item, your refund will process within 5-7 business days to your original payment method."

**Error Scenarios:**
- If the return cannot be initiated (e.g., order too old, final sale item): "This item isn't eligible for return per our policy. [Explain reason]. I can connect you with a customer care specialist if you have questions."
- If the action fails: "I'm having trouble processing that return. Let me escalate this to a specialist who can help."
```

**Length:** 210 words ✅

---

### Example 3: Search Product Catalog

```markdown
Action: Search Product Catalog

**When to Use:**
Use this action when the user wants to find products by keyword, category, or description. This is for discovery—when the user doesn't know the exact product yet.

**Required Inputs:**
- **Search Query**: Keywords or description (e.g., "blue sweater," "winter boots," "gifts under $50")

**Optional Inputs:**
- **Category Filter**: If the user specifies a category (e.g., "women's," "men's," "kids")
- **Price Range**: If the user mentions a budget

**Output Handling:**
Present the top 3-5 results:
- "[Product Name] - $[price] - [Availability status]"

Example: "Here are some options:
1. Blue Cotton Sweater - $49.99 - In stock
2. Navy Knit Cardigan - $59.99 - In stock
3. Sky Blue Hoodie - $39.99 - Limited stock

Which one would you like to learn more about?"

**Error Scenarios:**
- If no results found: "I didn't find any products matching '[query]'. Can you try different keywords or describe what you're looking for?"
- If too many results (50+): "I found a lot of options for '[query]'. Can you narrow it down? For example, are you looking for a specific style, size, or price range?"
```

**Length:** 230 words ✅

---

### Example 4: Check Return Eligibility (Flow-Based Action)

```markdown
Action: Check Return Eligibility

**When to Use:**
Use this action BEFORE initiating a return to verify the item qualifies under our return policy.

**Required Inputs:**
- **Order Number**: The order containing the item
- **Item ID**: The specific item to check

**Output Handling:**
The action returns a boolean (eligible/not eligible) and a reason.

If eligible:
- Proceed to Initiate Return Request action
- "That item is eligible for return. Let me start the process for you."

If not eligible:
- Explain the reason clearly
- "This item isn't eligible for return because [reason: outside 30-day window / final sale item / damaged by user]. Our return policy allows returns within 30 days for unused items."
- Offer to escalate if the user has extenuating circumstances: "If you'd like to discuss this further, I can connect you with a customer care specialist."

**Error Scenarios:**
- If the action fails to check eligibility: "I'm having trouble verifying eligibility right now. Let me connect you with a specialist who can review your return request."
```

**Length:** 185 words ✅

---

### Do's and Don'ts for Action-Level Instructions

| ✅ DO | ❌ DON'T |
|-------|----------|
| Clearly specify when to invoke the action | Assume the agent will "know when to use it" |
| Distinguish required vs. optional inputs | Leave input requirements ambiguous |
| Provide example output formats | Let the agent guess how to present results |
| Address error scenarios | Ignore what happens when actions fail |
| Keep it to 50-150 words per action | Write 300+ word action instructions |

---

## Do's and Don'ts Table: Good vs. Bad Instructions

### Agent-Level Instructions

| ✅ GOOD | ❌ BAD |
|---------|--------|
| "You are a helpful and efficient customer service agent. Keep responses concise (2-3 sentences) unless detailed explanation is needed." | "You are an AI assistant. Be helpful." (Too vague) |
| "Acknowledge frustration or disappointment when issues arise. Example: 'I'm sorry your order was delayed—that's frustrating.'" | "Don't make customers angry." (Negative framing) |
| "I cannot override company policies without human approval. I will escalate policy exceptions to specialists." | "I can't do a lot of things so just figure it out." (Unclear boundaries) |

---

### Topic-Level Instructions

| ✅ GOOD | ❌ BAD |
|---------|--------|
| "For order tracking requests, gather the order number or email address first. If not provided, ask which the user prefers." | "Get order info." (No specifics on how) |
| "If the order hasn't shipped yet, explain it's being processed and provide an estimated ship date if available." | "If status is 'Processing' then say 'Your order is processing' else if status is 'Shipped' then say..." (Over-scripting) |
| "If an item is outside the 30-day return window but the user has a reasonable case (defective item), escalate to a specialist." | "Items over 30 days old cannot be returned under any circumstances." (No room for judgment) |

---

### Action-Level Instructions

| ✅ GOOD | ❌ BAD |
|---------|--------|
| "Use this action when the user wants to check the status of a specific order or track a package." | "Use this when needed." (Too vague) |
| "Required: Order number OR email address. If not provided, ask the user which they'd like to provide." | "Needs order info." (Doesn't specify how to obtain) |
| "Present: 'Your order #[number] shipped on [date] and should arrive by [delivery date]. Track it here: [link]'" | "Show the order status." (No formatting guidance) |
| "If no order is found, respond: 'I couldn't find an order with that number. Can you double-check?'" | [No error handling guidance] (Silent failures) |

---

## Instruction Length Guidelines

Follow these length targets to keep instructions focused and effective:

| Instruction Level | Target Length | Maximum Length | What to Include |
|-------------------|---------------|----------------|-----------------|
| **Agent-Level** | 200-500 words | 600 words | Persona, behavior rules, boundaries |
| **Topic-Level** | 100-300 words per topic | 400 words per topic | Data gathering, workflow, edge cases |
| **Action-Level** | 50-150 words per action | 200 words per action | When to use, inputs, outputs, errors |

### Total Instruction Budget

For a typical agent with 5-7 topics and 25-30 actions:

- **Agent-level:** 300 words
- **Topic-level:** 7 topics × 200 words = 1,400 words
- **Action-level:** 30 actions × 100 words = 3,000 words

**Total:** ~4,700 words

**Rule of Thumb:** Keep total instructions under 5,000 words. Beyond that, the agent may struggle to apply all guidance consistently.

---

## Examples with Annotations

### Example 1: Agent-Level Instructions (Annotated)

```markdown
You are the Acme Retail Support Agent, a helpful and efficient assistant for customers with orders, returns, and product questions.
[Persona definition: WHO the agent is and WHAT it does]

**Personality:**
- Helpful: Proactively offer solutions and alternatives when issues arise
  [Trait + Behavioral description: HOW the trait manifests]
- Efficient: Keep responses concise—2 to 3 sentences unless detailed explanation is needed
  [Trait + Specific guidance: Concrete action]
- Empathetic: Acknowledge frustration or disappointment, especially when things go wrong
  [Trait + Specific guidance: When to apply it]

**Response Format:**
- Start with the answer or action you're taking
  [Output structure: How to organize responses]
- Provide specific details (order numbers, dates, tracking links)
  [Output content: What information to include]
- End with clear next steps or options for the user
  [Output closure: How to end responses]

**Boundaries:**
- I cannot provide medical, legal, or financial advice
  [Limitation: What's out of scope]
- I cannot override company policies without human approval
  [Authority limitation: What requires escalation]
- I will escalate complex issues and urgent requests to specialists
  [Escalation criteria: When to hand off]
```

**Why this works:**
- ✅ Clear persona with 3 specific traits
- ✅ Behavioral descriptions for each trait
- ✅ Concrete response formatting guidance
- ✅ Explicit boundaries and escalation criteria
- ✅ 175 words (within 200-500 range)

---

### Example 2: Topic-Level Instructions (Annotated)

```markdown
Topic: Order Tracking & Status

This topic covers helping users check the status of orders, track packages, and view order history.
[Topic purpose: One-sentence summary of scope]

**Data Gathering:**
For all order tracking requests, gather the order number or email address first. If the user doesn't provide this information, ask: "I can look that up for you. Do you have your order number, or would you like me to search by email address?"
[What information to collect + How to ask for it]

**Workflow:**
1. Collect order number or email address
2. Use the appropriate Look Up Order action
3. Present the order status clearly with expected delivery date and tracking link
[High-level process steps—not over-scripted]

**Output Formatting:**
Present order information in this format:
- Order number and date placed
- Current status (e.g., "Processing," "Shipped," "In Transit," "Delivered")
- Expected delivery date
- Tracking link (if order has shipped)
[Structured output format with examples]

Example: "Your order #12345 shipped yesterday via FedEx. It's currently in transit and should arrive by Friday, February 9th. Track it here: [link]"
[Concrete example of well-formatted output]

**Edge Cases:**
- If the order hasn't shipped yet, explain it's being processed and provide an estimated ship date if available
- If the order is delayed beyond the expected delivery date, acknowledge the inconvenience and offer to escalate
[Common variations and how to handle them]
```

**Why this works:**
- ✅ Clear topic scope
- ✅ Specific data gathering instructions with example question
- ✅ High-level workflow (not over-detailed)
- ✅ Output formatting with structure and example
- ✅ Edge case guidance without decision trees
- ✅ 220 words (within 100-300 range)

---

### Example 3: Action-Level Instructions (Annotated)

```markdown
Action: Look Up Order Status

**When to Use:**
Use this action when the user wants to check the status of a specific order, track a package, or get delivery information.
[Scenarios where this action applies]

**Required Inputs:**
- **Order Number** OR **Email Address**: The user must provide one of these. If not provided, ask: "I can look that up. Do you have your order number, or would you like me to search by email?"
[Required data + How to obtain if missing]

**Output Handling:**
Present the order information clearly:
- "Your order #[number] [status] on [date]. It should arrive by [delivery date]. Track it here: [link]"
[Standard output format with placeholders]

If the order hasn't shipped:
- "Your order #[number] is being processed and should ship by [estimated date]."
[Variation for specific scenario]

**Error Scenarios:**
- If no order is found: "I couldn't find an order with that number/email. Can you double-check the information?"
- If the lookup fails due to a system error: "I'm having trouble retrieving that order right now. Let me try again, or I can connect you with someone from our team."
[How to handle common errors gracefully]
```

**Why this works:**
- ✅ Clear "when to use" criteria
- ✅ Required inputs with guidance on how to obtain them
- ✅ Specific output formatting with placeholders
- ✅ Variation for different scenarios (shipped vs. not shipped)
- ✅ Error handling for common failures
- ✅ 175 words (within 50-150 range—slightly over but acceptable for complex action)

---

## Testing Instructions

Use the Agentforce Testing Center to validate your instructions:

### Test Categories

1. **Happy Path:** Standard requests handled correctly
2. **Data Gathering:** Agent asks for missing information
3. **Output Formatting:** Agent presents results consistently
4. **Edge Cases:** Agent handles unusual scenarios appropriately
5. **Error Handling:** Agent responds gracefully to failures
6. **Boundary Enforcement:** Agent escalates out-of-scope requests
7. **Tone Consistency:** Agent maintains persona across all interactions

### Test Template

| Test Case | Expected Behavior | Pass/Fail |
|-----------|-------------------|-----------|
| "Where's my order?" | Asks for order number or email | ✅/❌ |
| Provides order number | Looks up order, presents status/date/tracking | ✅/❌ |
| Order hasn't shipped | Explains it's processing, gives estimated ship date | ✅/❌ |
| Order lookup fails | Apologizes, offers to retry or escalate | ✅/❌ |
| "Give me a refund" (no order context) | Asks for order number to look up | ✅/❌ |
| "Can you give me legal advice?" | Declines, explains boundary, offers escalation | ✅/❌ |

### Iteration Cycle

1. **Write initial instructions** using templates and principles
2. **Test with 20-30 utterances** covering all test categories
3. **Identify failures:** Where did the agent not follow instructions?
4. **Refine instructions:** Add clarity, examples, or edge case guidance
5. **Re-test:** Validate that failures are resolved
6. **Repeat:** Iterate until 90%+ test cases pass

**Goal:** 90%+ accuracy on happy path scenarios, 85%+ on edge cases.

---

## Common Mistakes

### Mistake 1: Over-Scripting (Decision Tree Instructions)

**Symptom:** Instructions read like if/then code.

**Example:**

```markdown
❌ BAD:
If user says "Where's my order?" then:
  Ask for order number
  If user provides order number then:
    Call Look Up Order action
    If status is "Shipped" then:
      Say "Your order shipped on [date]"
    Else if status is "Delivered" then:
      Say "Your order was delivered on [date]"
    Else if status is "Processing" then:
      Say "Your order is being processed"
```

**Fix:** Use guidance, not scripts.

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
