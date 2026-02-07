# Topic Architecture Guide for Agentforce Agents

## What are Topics?

Topics are the organizational units that structure your Agentforce agent's capabilities. Each topic is a classification bucket that groups related actions together and defines a distinct area of expertise for your agent.

Think of topics as departments in a company:
- **Order Management** (like the fulfillment department)
- **Returns & Exchanges** (like customer service)
- **Product Information** (like the sales floor)
- **Account Management** (like the back office)

Topics serve three critical functions:

1. **Classification:** Agentforce uses topic classification descriptions to route user utterances to the right set of actions
2. **Scope Definition:** Topics define what your agent CAN do (and by exclusion, what it cannot)
3. **Instruction Organization:** Topics allow you to write specialized behavior instructions for different workflows

**Key Insight:** Topics are NOT conversation threads or session states—they're classification labels. A single conversation can touch multiple topics, and the agent can switch between topics fluidly based on user intent.

---

## Bottom-Up Design Methodology

Many teams make the mistake of starting with topics and then figuring out what actions to put in them. This leads to artificial groupings and overlapping classifications.

**The right way:** Start with actions, then organize them into topics.

### The Bottom-Up Process

```
Step 1: List ALL Actions
        ↓
Step 2: Group by User Intent
        ↓
Step 3: Write Classification Descriptions
        ↓
Step 4: Test for Distinctness
        ↓
Step 5: Validate with Real Utterances
```

Let's walk through each step with a real example.

---

### Step 1: List ALL Actions the Agent Needs to Perform

Start by brainstorming every discrete capability your agent should have. Don't worry about organization yet—just capture all the actions.

**Example: E-Commerce Customer Service Agent**

```markdown
Action Inventory (Unsorted):
1. Look up order status by order number
2. Look up order status by email address
3. Track package location
4. Initiate a return for an order
5. Generate a return shipping label
6. Check return eligibility for an item
7. Search product catalog by keyword
8. Get product details (price, sizes, colors)
9. Check product availability/inventory
10. Get product reviews and ratings
11. Update account email address
12. Update account phone number
13. Update account shipping address
14. Reset account password
15. View order history
16. Cancel an order
17. Modify order items (add/remove)
18. Change order shipping address
19. Apply a promo code to an order
20. Check promo code validity
21. Answer questions about return policy
22. Answer questions about shipping policy
23. Answer questions about warranty policy
24. Escalate to human agent
25. Check loyalty points balance
26. Redeem loyalty points
```

**Tip:** Include both transactional actions (look up, update, create) and informational actions (answer questions, provide policies).

---

### Step 2: Group Actions by User Intent Similarity

Now cluster your actions based on what the USER is trying to accomplish, not what your systems do.

**Example Grouping:**

```markdown
Group A: "I want to know about my order"
- Look up order status by order number
- Look up order status by email address
- Track package location
- View order history

Group B: "I want to return or cancel something"
- Initiate a return for an order
- Generate a return shipping label
- Check return eligibility for an item
- Cancel an order

Group C: "I need to change my order"
- Modify order items (add/remove)
- Change order shipping address
- Apply a promo code to an order

Group D: "I want to learn about products"
- Search product catalog by keyword
- Get product details (price, sizes, colors)
- Check product availability/inventory
- Get product reviews and ratings

Group E: "I need to update my account"
- Update account email address
- Update account phone number
- Update account shipping address
- Reset account password
- Check loyalty points balance
- Redeem loyalty points

Group F: "I have questions about policies"
- Answer questions about return policy
- Answer questions about shipping policy
- Answer questions about warranty policy
- Check promo code validity

Group G: "I need human help"
- Escalate to human agent
```

**Key Principle:** Group by USER intent, not by system backend. For example, "Cancel order" and "Initiate return" might both touch the Order Management System, but they're different user intents.

---

### Step 3: Write Classification Descriptions for Each Group

For each group, write a classification description that captures the RANGE of user intents in that group. This is what Agentforce will use to route utterances.

**Classification Description Guidelines:**

✅ **DO:**
- Use positive, declarative language ("User wants to...")
- Be specific about the scope
- Include common variations of phrasing
- Use language users would actually use

❌ **DON'T:**
- Use negative language ("User does NOT want to...")
- Overlap with other topic descriptions
- Be too vague or too narrow
- Use internal jargon or system names

**Example Classifications:**

```markdown
Topic: Order Tracking & Status
Classification Description:
"User wants to check the status of an order, track a package, view order history, or get information about a current or past order. Includes questions about delivery dates, shipping progress, and order confirmation."

Topic: Returns & Cancellations
Classification Description:
"User wants to return an item, start a return, generate a return label, cancel an order, or check if an item is eligible for return. Includes questions about the return process and refund timelines."

Topic: Order Modifications
Classification Description:
"User wants to change something about an existing order before it ships, such as adding or removing items, changing the shipping address, or applying a promo code."

Topic: Product Information & Search
Classification Description:
"User wants to find products, learn about product details (price, sizes, colors, materials), check if an item is in stock, or read product reviews and ratings."

Topic: Account Management
Classification Description:
"User wants to update their account information (email, phone, address), reset their password, check loyalty points balance, or redeem rewards."

Topic: Policies & General Questions
Classification Description:
"User has questions about company policies such as return policies, shipping policies, warranties, or wants to validate a promo code. This is a catch-all for informational questions not tied to a specific order or product."

Topic: General Escalation (Pre-built)
Classification Description:
"User needs help with something the agent cannot handle, wants to speak to a human, or has a complex issue that requires specialist assistance."
```

**Length Guidelines:**
- **Minimum:** 20 words (too short = ambiguous classification)
- **Optimal:** 40-80 words (provides clear scope)
- **Maximum:** 150 words (too long = classification slowdown)

---

### Step 4: Test for Semantic Distinctness Between Groups

Your classification descriptions must be mutually exclusive. If they overlap, Agentforce may route utterances to the wrong topic.

**Overlap Test:**

For each pair of topics, ask: "Could a reasonable user utterance match both descriptions?"

**Example Overlap Problem:**

```markdown
❌ BAD EXAMPLE:

Topic A: Order Management
"User wants to do something with their order."

Topic B: Order Tracking
"User wants to track their order."

Problem: "Where's my order?" could match both. Topic B is a subset of Topic A.
```

**Fixed:**

```markdown
✅ GOOD EXAMPLE:

Topic A: Order Tracking & Status
"User wants to CHECK the status of an order, track a package, or view order history. This is about monitoring existing orders, not making changes."

Topic B: Order Modifications
"User wants to CHANGE something about an existing order before it ships, such as adding items, changing the address, or applying a promo code."

Why it works: "Where's my order?" → Monitoring → Topic A. "Can I add an item?" → Changing → Topic B.
```

**Distinctness Checklist:**

For each topic pair, verify:
- [ ] They cover different user goals
- [ ] Keywords are distinct (track vs modify, find vs update)
- [ ] No subset relationships (one is not a subcategory of another)
- [ ] Boundary examples clearly belong to one or the other

**Boundary Testing:**

For each topic pair, write 5 "boundary utterances" and verify they classify correctly:

| Utterance | Should Route To | Why |
|-----------|-----------------|-----|
| "Where's my order?" | Order Tracking | Checking status |
| "Can I change my shipping address?" | Order Modifications | Making a change |
| "How do I return this?" | Returns & Cancellations | Return process |
| "Is this sweater in stock?" | Product Information | Product availability |
| "What's your return policy?" | Policies & General Questions | Policy info |

---

### Step 5: Validate with Real Utterances

Test your topic architecture with real user language. Collect 50-100 sample utterances from:
- Customer service chat logs
- Support tickets
- User interviews
- Hypothetical scenarios

**Validation Template:**

```markdown
Utterance: "I never received my order and it's been 2 weeks"
Expected Topic: Order Tracking & Status
Actual Classification: [Run in Testing Center]
Pass/Fail: ✅

Utterance: "Can you add another shirt to my order?"
Expected Topic: Order Modifications
Actual Classification: [Run in Testing Center]
Pass/Fail: ✅

Utterance: "This doesn't fit, I need to return it"
Expected Topic: Returns & Cancellations
Actual Classification: [Run in Testing Center]
Pass/Fail: ✅
```

**Accuracy Goals:**
- **Tier 1 (Critical):** 95%+ accuracy (e.g., order tracking, returns)
- **Tier 2 (Important):** 90%+ accuracy (e.g., product info, account changes)
- **Tier 3 (Nice-to-have):** 85%+ accuracy (e.g., general policies)

**Iteration:** If accuracy is below target, refine classification descriptions or merge/split topics.

---

## Classification Descriptions

Classification descriptions are the most critical part of your topic architecture. They determine whether Agentforce routes user requests correctly.

### Anatomy of a Great Classification Description

**Formula:** [User Goal] + [Common Variations] + [Scope Boundaries]

**Example:**

```markdown
Topic: Order Tracking & Status

Classification Description:
"User wants to [USER GOAL] check the status of an order, track a package, view order history, or get information about a current or past order. [COMMON VARIATIONS] Includes questions about delivery dates, shipping progress, and order confirmation. [SCOPE BOUNDARY] This is about monitoring orders, not making changes or processing returns."
```

**Breakdown:**
1. **User Goal:** "check the status of an order" (primary intent)
2. **Common Variations:** "track a package, view order history, get information"
3. **Scope Boundary:** "not making changes or processing returns" (clarifies exclusions)

### Writing Style Guidelines

| Guideline | Good Example | Bad Example |
|-----------|--------------|-------------|
| **Use positive language** | "User wants to track their order" | "User is NOT asking about returns" |
| **Be specific** | "User wants to check product availability and sizes" | "User has product questions" |
| **Use natural language** | "User wants to return an item" | "User wants to initiate reverse logistics" |
| **Include variations** | "track, monitor, check status, see updates" | "track" (too narrow) |
| **Avoid jargon** | "User wants to update their email address" | "User wants to modify CRM contact record" |

### Common Pitfalls

#### Pitfall 1: Too Vague

```markdown
❌ BAD:
Topic: Order Management
"User has questions about orders."

Problem: Every order-related utterance will match this.
```

```markdown
✅ GOOD:
Topic: Order Tracking & Status
"User wants to check the status of an existing order, track package location, view past orders, or get delivery estimates. This is about monitoring orders, not making changes."
```

#### Pitfall 2: Too Narrow

```markdown
❌ BAD:
Topic: Order Tracking
"User wants to track a package using a tracking number."

Problem: Misses "Where's my order?" (no tracking number mentioned)
```

```markdown
✅ GOOD:
Topic: Order Tracking & Status
"User wants to check the status of an order, track a package, view order history, or get delivery information. User may provide an order number, email address, or tracking number."
```

#### Pitfall 3: Overlapping Descriptions

```markdown
❌ BAD:
Topic A: Product Search
"User wants to find products or search the catalog."

Topic B: Product Information
"User wants to learn about products or get product details."

Problem: "Tell me about this sweater" could match both.
```

```markdown
✅ GOOD:
Topic A: Product Search & Discovery
"User wants to FIND products by searching for keywords, browsing categories, or filtering by attributes (size, color, price). This is about discovering what's available."

Topic B: Product Details & Availability
"User wants detailed information about a SPECIFIC product they've identified, such as price, sizes, colors, materials, inventory status, or customer reviews."
```

#### Pitfall 4: System-Centric Language

```markdown
❌ BAD:
Topic: CRM Account Updates
"User wants to modify Salesforce contact records or update Account object fields."

Problem: Users don't think in terms of "Salesforce objects."
```

```markdown
✅ GOOD:
Topic: Account Management
"User wants to update their personal information such as email address, phone number, or shipping address, or manage their account settings."
```

### Testing Classification Descriptions

Use the Agentforce Testing Center to validate:

1. **Single-topic utterances:** Should route to the correct topic
2. **Ambiguous utterances:** Should route to the most relevant topic
3. **Out-of-scope utterances:** Should route to General Escalation

**Test Template:**

| Utterance | Expected Topic | Actual Topic | Pass/Fail |
|-----------|----------------|--------------|-----------|
| "Where is my order?" | Order Tracking | [Test result] | ✅/❌ |
| "I want to return this" | Returns & Cancellations | [Test result] | ✅/❌ |
| "Is this in stock?" | Product Information | [Test result] | ✅/❌ |
| "What's your refund policy?" | Policies & General Questions | [Test result] | ✅/❌ |
| "I need a lawyer" | General Escalation | [Test result] | ✅/❌ |

**Iteration:** For failures, tweak classification descriptions and re-test.

---

## Scope Boundaries

Topics define your agent's scope—what it CAN do. By extension, anything not covered by your topics is OUT OF SCOPE.

### Defining In-Scope vs Out-of-Scope

**In-Scope:** Actions explicitly covered by your topics

**Out-of-Scope:** Everything else (routes to General Escalation)

**Example: E-Commerce Agent**

```markdown
IN SCOPE:
- Order tracking and status checks
- Return and cancellation requests
- Product search and information
- Account information updates
- Policy questions (returns, shipping, warranty)

OUT OF SCOPE:
- Technical support for using products
- Medical/legal/financial advice
- Complaints or disputes (escalate to human)
- Marketing feedback or surveys
- Third-party service issues (payment processors, carriers)
```

### Using Topics as Safety Guardrails

Topics act as a natural safety layer. If a user asks something outside your topic classifications, Agentforce routes it to the General Escalation topic.

**Example:**

```markdown
User: "Can you give me legal advice about my warranty?"
Classification: No topic matches → Routes to General Escalation
Agent Response: "I'm not able to provide legal advice, but I can connect you with our customer care team who can discuss your warranty options."
```

**Guardrail Strategy:**

1. **Narrow topic classifications:** Be specific about what each topic covers
2. **Leverage General Escalation:** Let it catch out-of-scope requests
3. **Test edge cases:** Validate that unsafe/inappropriate requests route to Escalation

**Test Cases for Guardrails:**

| Utterance | Expected Behavior |
|-----------|-------------------|
| "Can you give me medical advice?" | → General Escalation |
| "I'm going to sue you!" | → General Escalation |
| "Can I get a refund on this 5-year-old order?" | → General Escalation (policy violation) |
| "Can you hack into my ex's account?" | → General Escalation (inappropriate request) |
| "Tell me a joke" | → General Escalation (chitchat, off-topic) |

---

## Architecture Rules

Follow these rules to create a clean, scalable topic architecture:

### Rule 1: Maximum 10 Topics per Agent (Recommended)

**Why:** More topics = harder to classify accurately. Agentforce's classification model performs best with 5-10 distinct topics.

**Guideline:**
- **5-7 topics:** Optimal for most agents
- **8-10 topics:** Acceptable for complex domains
- **11+ topics:** Consider splitting into multiple agents

**Example: Overcomplicated Architecture**

```markdown
❌ BAD (15 topics):
1. Order Status Checks
2. Package Tracking
3. Delivery Date Inquiries
4. Return Initiation
5. Return Label Generation
6. Refund Status
7. Product Search
8. Product Details
9. Inventory Checks
10. Email Updates
11. Phone Updates
12. Address Updates
13. Return Policy
14. Shipping Policy
15. Warranty Policy

Problem: Too many topics with overlapping purposes.
```

**Consolidated Architecture:**

```markdown
✅ GOOD (6 topics):
1. Order Tracking & Status (combines 1, 2, 3)
2. Returns & Refunds (combines 4, 5, 6)
3. Product Information (combines 7, 8, 9)
4. Account Management (combines 10, 11, 12)
5. Policies & General Questions (combines 13, 14, 15)
6. General Escalation (pre-built)

Benefit: Clearer classification, easier to maintain.
```

### Rule 2: Maximum 5 Actions per Topic (Recommended)

**Why:** Topics with too many actions become "mega-topics" that dilute classification accuracy.

**Guideline:**
- **3-5 actions:** Optimal per topic
- **6-7 actions:** Acceptable if tightly related
- **8+ actions:** Consider splitting the topic

**Example: Bloated Topic**

```markdown
❌ BAD:
Topic: Order Management (10 actions)
- Look up order status
- Track package
- View order history
- Cancel order
- Modify order items
- Change shipping address
- Apply promo code
- Initiate return
- Generate return label
- Check refund status

Problem: Mixing monitoring, modifications, and returns in one topic.
```

**Split Topics:**

```markdown
✅ GOOD:
Topic: Order Tracking & Status (3 actions)
- Look up order status
- Track package
- View order history

Topic: Order Modifications (3 actions)
- Modify order items
- Change shipping address
- Apply promo code

Topic: Returns & Refunds (4 actions)
- Initiate return
- Generate return label
- Check refund status
- Cancel order (if it includes refund logic)
```

### Rule 3: Each Topic Should Have a Clear, Distinct Purpose

**Test:** Can you describe the topic's purpose in one sentence?

```markdown
✅ GOOD:
- Order Tracking: "Help users monitor their orders and packages."
- Returns: "Help users process returns and refunds."
- Product Info: "Help users find and learn about products."

❌ BAD:
- Miscellaneous: "Handle various user requests."
- General Support: "Provide assistance with customer needs."
```

### Rule 4: No Overlapping Classification Descriptions

**Test:** For any pair of topics, can you write 5 utterances that CLEARLY belong to one or the other?

**Overlap Example:**

```markdown
❌ BAD:
Topic A: Product Questions
"User has questions about products."

Topic B: Product Search
"User wants to find products."

Overlap: "Tell me about the blue sweater" could match either.
```

**Fixed:**

```markdown
✅ GOOD:
Topic A: Product Search & Discovery
"User wants to FIND products they don't know about yet by searching keywords, browsing categories, or filtering."

Topic B: Product Details & Availability
"User already knows WHICH product they're interested in and wants specific details like price, sizes, inventory, or reviews."

No Overlap: "Find me a sweater" → Topic A. "Is the blue sweater in stock?" → Topic B.
```

### Rule 5: Every Action Must Belong to Exactly One Topic

**Why:** Actions in multiple topics create classification confusion.

**Example:**

```markdown
❌ BAD:
Action: "Check Order Status"
- Assigned to Topic A: Order Tracking
- Assigned to Topic B: Order Management

Problem: Which topic should "Where's my order?" route to?
```

```markdown
✅ GOOD:
Action: "Check Order Status"
- Assigned to Topic A: Order Tracking ONLY
```

**Edge Case:** If an action truly serves multiple purposes, consider:
1. **Split the action** into two specialized versions
2. **Broaden one topic** to encompass both use cases
3. **Use topic-level instructions** to handle variations

---

## Topic Interaction Patterns

Topics aren't isolated—users often move between topics in a single conversation.

### Pattern 1: Sequential Topics (Order Tracking → Return Processing)

**Example:**

```
User: "Where's my order?"
Agent: [Order Tracking] "Your order #12345 shipped yesterday and should arrive Friday."

User: "Actually, I need to return it."
Agent: [Switches to Returns & Cancellations] "I can help with that return. Let me generate a prepaid label for order #12345."
```

**Key:** Agentforce automatically switches topics when user intent changes. You don't need to script this—classification handles it.

### Pattern 2: Parallel Topics (Multiple Intents in One Turn)

**Example:**

```
User: "Can I change my shipping address and also return an item from last week?"
Agent: [Detects two intents: Account Management + Returns]
"I can help with both. Let me start with updating your shipping address for future orders. What's the new address?"
[After completing] "Now let's process the return. Which item from last week do you need to return?"
```

**Key:** Agentforce can detect multiple intents and handle them sequentially.

### Pattern 3: Cross-Topic Context Passing

**Example:**

```
User: "I want to return the sweater from order #12345"
[Returns topic is triggered]

Agent: [Calls "Look Up Order" action from Order Tracking topic to get order details]
Agent: [Then calls "Initiate Return" action from Returns topic]
"I see you ordered a blue sweater in size M. I've started the return and sent a label to your email."
```

**Key:** Actions from one topic can be invoked within another topic's context. This is handled automatically by Agentforce's planner.

### Designing for Topic Switching

**Best Practices:**

1. **Don't over-script transitions:** Let Agentforce handle topic classification dynamically
2. **Use topic-level instructions for context:** If a topic needs specific setup, document it in topic instructions
3. **Test multi-turn conversations:** Validate that switching between topics feels natural

**Example Test Case:**

```markdown
Turn 1 (Order Tracking):
User: "Where's my order?"
Agent: "Your order #12345 shipped yesterday."

Turn 2 (Returns):
User: "I want to return it."
Agent: "I can help with that return for order #12345." [Maintains context]

Turn 3 (Product Info):
User: "Do you have the same sweater in large?"
Agent: "Let me check. Yes, the blue sweater is available in size large." [Switches topic]

Turn 4 (Order Tracking):
User: "OK, when will my original order arrive?"
Agent: "Your original order #12345 should arrive by Friday." [Switches back]
```

**Goal:** Transitions should feel seamless, not jarring.

---

## Salesforce Implementation

### Creating Topics in Agent Builder

**Step-by-Step:**

1. Navigate to **Setup > Agent Builder > [Your Agent] > Topics**
2. Click **New Topic**
3. Enter **Topic Name** (e.g., "Order Tracking & Status")
4. Write **Classification Description** (40-80 words)
5. (Optional) Add **Topic-Level Instructions** (covered in instruction-writing-guide.md)
6. Click **Save**

**Repeat for each topic in your architecture.**

### Configuring Classification Descriptions

**UI Fields:**

- **Topic Name:** Internal label (e.g., "Order_Tracking_Status")
- **Display Name:** User-facing name (e.g., "Order Tracking & Status")
- **Classification Description:** The text Agentforce uses for routing (40-80 words)

**Example:**

```markdown
Topic Name: Order_Tracking_Status
Display Name: Order Tracking & Status
Classification Description:
"User wants to check the status of an order, track a package, view order history, or get information about a current or past order. Includes questions about delivery dates, shipping progress, and order confirmation. This is about monitoring existing orders, not making changes or processing returns."
```

### Assigning Actions to Topics

**Step-by-Step:**

1. Navigate to **Setup > Agent Builder > [Your Agent] > Actions**
2. Click **New Action** (or edit existing)
3. Configure action details (name, API reference, inputs/outputs)
4. In **Topic Assignment**, select the topic this action belongs to
5. (Optional) Add **Action-Level Instructions**
6. Click **Save**

**Example:**

```markdown
Action: Look Up Order Status
API Reference: OrderManagementFlow.lookUpOrderStatus
Topic Assignment: Order Tracking & Status
Action-Level Instructions:
"Use this action when the user wants to check the status of a specific order. Require either an order number or the email address used for purchase. If the user doesn't provide this information, ask for it before invoking the action."
```

**Rule:** Every action must be assigned to exactly one topic.

### Setting Topic-Level Instructions

Topic-level instructions guide agent behavior within that topic's context.

**Example:**

```markdown
Topic: Order Tracking & Status

Topic-Level Instructions:
"For all order tracking requests, gather the order number or email address first. If the user doesn't provide it, ask: 'I can look that up for you. Do you have your order number, or would you like me to search by email address?'

Once you have the order information, use the Look Up Order Status action. Present the results in this format:
- Order number and date
- Current status (e.g., 'Shipped,' 'In Transit,' 'Delivered')
- Expected delivery date
- Tracking link (if available)

If the order hasn't shipped yet, explain that it's being processed and provide an estimated ship date.

If the order is delayed, acknowledge the inconvenience and offer to escalate to a specialist if needed."
```

**See instruction-writing-guide.md for detailed guidance on writing topic-level instructions.**

---

## Example: Retail Agent Topic Architecture

Here's a complete topic architecture for a retail customer service agent.

### Agent: Acme Retail Support Agent

**Agent Scope:** Help customers with orders, returns, product questions, and account management.

### Topic 1: Order Tracking & Status

**Classification Description:**
"User wants to check the status of an order, track a package, view order history, or get information about a current or past order. Includes questions about delivery dates, shipping progress, order confirmation, and 'Where is my order?' type inquiries."

**Actions (4):**
1. Look Up Order by Order Number
2. Look Up Order by Email Address
3. Get Package Tracking Details
4. View Order History

**Topic-Level Instructions:**
"Always gather the order number or email address before looking up order information. Present order status clearly with expected delivery date and tracking link if available."

---

### Topic 2: Returns & Cancellations

**Classification Description:**
"User wants to return an item, start a return, generate a return shipping label, cancel an order, check refund status, or ask about return eligibility. Includes questions about the return process, return windows, and refund timelines."

**Actions (5):**
1. Check Return Eligibility
2. Initiate Return Request
3. Generate Return Shipping Label
4. Cancel Pending Order
5. Check Refund Status

**Topic-Level Instructions:**
"For returns, first check eligibility (30-day window, unused condition). Walk users through the return process step-by-step. For cancellations, check if the order has shipped—if yes, route through the return process instead."

---

### Topic 3: Order Modifications

**Classification Description:**
"User wants to make changes to an existing order that hasn't shipped yet, such as adding or removing items, changing the shipping address, applying a promo code, or upgrading shipping speed."

**Actions (4):**
1. Modify Order Items
2. Update Shipping Address
3. Apply Promo Code to Order
4. Upgrade Shipping Method

**Topic-Level Instructions:**
"Always check if the order has shipped before attempting modifications. If it has shipped, explain that changes aren't possible and offer alternatives (e.g., return/reorder for different items)."

---

### Topic 4: Product Information & Search

**Classification Description:**
"User wants to find products, search the catalog, learn about product details such as price, sizes, colors, materials, check if an item is in stock, or read product reviews and ratings. This is about discovering and researching products."

**Actions (5):**
1. Search Product Catalog by Keyword
2. Get Product Details
3. Check Product Availability
4. Get Product Reviews
5. Compare Products

**Topic-Level Instructions:**
"Help users find products that match their needs. If they're browsing, ask clarifying questions about preferences (size, color, price range). Always check availability before recommending a product."

---

### Topic 5: Account Management

**Classification Description:**
"User wants to update their account information such as email address, phone number, shipping address, payment methods, password, or manage loyalty points and rewards. This is about personal account settings, not specific orders."

**Actions (5):**
1. Update Email Address
2. Update Phone Number
3. Update Default Shipping Address
4. Reset Password
5. Check Loyalty Points Balance

**Topic-Level Instructions:**
"Always verify the user's identity before making account changes. For security-sensitive changes (email, password), explain that we'll send a verification link or code."

---

### Topic 6: Policies & General Questions

**Classification Description:**
"User has questions about company policies such as return policies, shipping policies, warranties, price matching, or wants to validate a promo code. This is a catch-all for informational questions not tied to a specific order or product."

**Actions (4):**
1. Get Return Policy (Knowledge)
2. Get Shipping Policy (Knowledge)
3. Get Warranty Information (Knowledge)
4. Validate Promo Code

**Topic-Level Instructions:**
"Use Knowledge actions to provide accurate policy information. After answering a policy question, offer to help the user apply that policy to their specific situation (e.g., 'Would you like to start a return?')."

---

### Topic 7: General Escalation (Pre-Built)

**Classification Description:**
"User needs help with something outside the agent's capabilities, wants to speak to a human representative, has a complex issue requiring specialist assistance, or makes inappropriate requests."

**Actions (1):**
1. Escalate to Human Agent (Omni-Channel)

**Topic-Level Instructions:**
"When escalating, briefly summarize what the user needs so the human agent has context. Example: 'I'm connecting you with a specialist who can help with [specific issue]. One moment please.'"

---

### Architecture Summary

| Topic | Actions | Purpose |
|-------|---------|---------|
| Order Tracking & Status | 4 | Monitor existing orders |
| Returns & Cancellations | 5 | Process returns and refunds |
| Order Modifications | 4 | Change orders before shipping |
| Product Information & Search | 5 | Discover and research products |
| Account Management | 5 | Update personal account info |
| Policies & General Questions | 4 | Answer policy/general questions |
| General Escalation | 1 | Escalate to human agents |

**Total:** 7 topics, 28 actions

**Classification Distinctness:** ✅ All topics have clear, non-overlapping scopes.

---

## Common Mistakes

### Mistake 1: Starting with Topics Instead of Actions

**Symptom:** Topics feel arbitrary, actions don't fit naturally.

**Example:**

```markdown
❌ BAD APPROACH:
"We need topics for... let's see... Orders, Products, and Accounts. Now what actions go in each?"

Result: Forced groupings that don't match user intent.
```

**Fix:** Start with actions. "What can the agent DO?" Then group by user intent.

### Mistake 2: Too Many Topics

**Symptom:** 12+ topics, overlapping classifications, poor routing accuracy.

**Example:**

```markdown
❌ BAD:
1. Order Status
2. Package Tracking
3. Delivery Dates
4. Order History
5. Return Initiation
6. Return Labels
7. Refund Status
8. Order Cancellation
... (15 topics total)
```

**Fix:** Consolidate into broader, distinct topics (5-7 topics).

### Mistake 3: Vague Classification Descriptions

**Symptom:** Multiple topics match the same utterance.

**Example:**

```markdown
❌ BAD:
Topic A: "User has order questions"
Topic B: "User needs order help"

Problem: "Where's my order?" matches both.
```

**Fix:** Be specific and include scope boundaries.

### Mistake 4: System-Centric Topics

**Symptom:** Topics named after internal systems or data models.

**Example:**

```markdown
❌ BAD:
- Order Management System (OMS) Topic
- Customer Relationship Management (CRM) Topic
- Product Information Management (PIM) Topic
```

**Fix:** Name topics based on USER goals, not systems.

```markdown
✅ GOOD:
- Order Tracking & Status
- Account Management
- Product Information & Search
```

### Mistake 5: Actions in Multiple Topics

**Symptom:** Duplicate actions, unclear classification routing.

**Example:**

```markdown
❌ BAD:
Action: "Look Up Order Status"
- In Topic A: Order Tracking
- In Topic B: Order Management

Problem: Which topic should "Where's my order?" route to?
```

**Fix:** Assign each action to exactly one topic. If truly needed in multiple contexts, create specialized versions.

---

## Testing Your Topic Architecture

Use the Agentforce Testing Center to validate:

### Test Suite

1. **Classification Accuracy:** 50+ utterances across all topics
2. **Boundary Cases:** Utterances that might match multiple topics
3. **Out-of-Scope:** Utterances that should route to General Escalation
4. **Multi-Turn:** Conversations that switch between topics

### Test Template

| Utterance | Expected Topic | Actual Topic | Pass/Fail |
|-----------|----------------|--------------|-----------|
| "Where is my order?" | Order Tracking | [Result] | ✅/❌ |
| "I want to return this" | Returns & Cancellations | [Result] | ✅/❌ |
| "Is this sweater in stock?" | Product Information | [Result] | ✅/❌ |
| "Update my email address" | Account Management | [Result] | ✅/❌ |
| "What's your return policy?" | Policies & General Questions | [Result] | ✅/❌ |
| "I need legal advice" | General Escalation | [Result] | ✅/❌ |
| "Can I change my order and also return something?" | Order Modifications (first) | [Result] | ✅/❌ |

### Iteration Cycle

1. Test with 50+ utterances
2. Identify misclassifications
3. Refine classification descriptions
4. Merge or split topics if needed
5. Re-test

**Goal:** 90%+ accuracy for critical topics, 85%+ for secondary topics.

---

## Next Steps

1. Complete the action inventory for your agent
2. Group actions by user intent
3. Write classification descriptions for each topic
4. Test for semantic distinctness
5. Validate with real user utterances
6. Implement in Agentforce Agent Builder
7. Test and iterate

**Remember:** Topic architecture is foundational. Invest time upfront to get it right, and your agent's performance will be dramatically better.
