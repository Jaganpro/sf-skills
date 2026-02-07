# Anti-Patterns in Agentforce Conversation Design

This guide catalogs common mistakes in conversation design with concrete examples and solutions. Learn from these anti-patterns to build better Agentforce agents.

---

## Category 1: Instruction Design Anti-Patterns

### Anti-Pattern 1.1: Over-Constraining with Absolute Language

**The Problem:** Using "must", "always", "never" in instructions creates brittle behavior that fails in edge cases.

#### ❌ BAD: Absolute Constraint
```yaml
Topic: Order Status
Instructions: |
  You must always ask for the order number before looking up an order.
  Never proceed without the order number.
```

**Why It's Bad:**
- Customer might say "What's the status of my order #12345?" — already provided order number
- Agent will re-ask unnecessarily, frustrating user
- LLM interprets "must" and "never" rigidly, ignoring context

#### ✅ GOOD: Context-Aware Guidance
```yaml
Topic: Order Status
Instructions: |
  To look up an order, you need the order number. If the customer hasn't
  provided it yet, ask for it: "What's your order number? It's an 8-digit
  number found in your confirmation email."

  If the customer already mentioned the order number earlier in the
  conversation, use that—don't re-ask.
```

**Fix Applied:**
- Uses "you need" (requirement) without "must" (rigid command)
- Explicitly handles case where info is already provided
- Trusts LLM to track conversational context

---

### Anti-Pattern 1.2: Negative Framing

**The Problem:** Telling the agent what NOT to do is less effective than telling it what TO do.

#### ❌ BAD: Negative Instructions
```yaml
Agent-Level Instructions: |
  Don't ask for the customer's credit card number.
  Don't make promises about shipping dates you can't verify.
  Don't provide legal or medical advice.
  Don't be rude or dismissive.
```

**Why It's Bad:**
- LLMs are better at following positive instructions than avoiding negatives
- Doesn't provide alternative behavior (what SHOULD the agent do?)
- Creates ambiguity ("if I don't ask for credit card, how do I verify payment?")

#### ✅ GOOD: Positive Instructions
```yaml
Agent-Level Instructions: |
  To verify payment information, guide the customer to their account settings
  where they can see the last 4 digits of their card on file. Never ask them
  to share the full card number in chat.

  For shipping dates, only provide estimates from the Order record's
  Estimated_Delivery__c field. If that field is empty, say "I don't have an
  estimated delivery date yet, but I can connect you with shipping support
  for an update."

  For questions about legal contracts or medical conditions, respond:
  "I'm not able to provide legal/medical advice, but I can connect you with
  a specialist who can help. Would that work for you?"

  When customers are frustrated, acknowledge their feelings: "I understand
  this has been frustrating" and offer solutions or escalation.
```

**Fix Applied:**
- Each "don't" is replaced with a "do" (what to do instead)
- Provides specific alternatives and phrasing
- Actionable instructions that guide behavior

---

### Anti-Pattern 1.3: Business Rules in Instructions

**The Problem:** Encoding complex business logic (calculations, validations, conditional rules) in natural language instructions instead of Flow/Apex.

#### ❌ BAD: Business Logic in Instructions
```yaml
Topic: Refund Request
Instructions: |
  Customers are eligible for refunds if:
  - Order was placed within 30 days
  - Order status is "Delivered" or "In Transit"
  - Order total is under $500
  - Customer is not on the restricted list
  - Product category is not "Personalized" or "Digital"

  Calculate the refund amount as: (Order Total - Shipping) * 0.95 if the
  customer used a discount code, otherwise Order Total - Shipping.
```

**Why It's Bad:**
- LLMs can misinterpret complex conditionals
- Business rules change over time — updating instructions is error-prone
- No guarantee of accurate calculations
- Can't enforce hard constraints (e.g., prevent refund if ineligible)

#### ✅ GOOD: Flow for Business Rules
```yaml
Topic: Refund Request
Instructions: |
  To process a refund, use the "Check Refund Eligibility" action, which
  requires the Order ID. This action will determine if the customer is
  eligible and calculate the refund amount.

  If eligible, confirm the amount with the customer and use the "Issue Refund"
  action. If not eligible, explain the reason provided by the action and
  offer to escalate if they have special circumstances.
```

```yaml
Flow: Check Refund Eligibility
Inputs:
  - OrderId (Text)
Outputs:
  - IsEligible (Boolean)
  - RefundAmount (Currency)
  - IneligibilityReason (Text)

Logic:
  1. Query Order with OrderId
  2. Get Account.Restricted__c, Order.CreatedDate, Order.Status, Order.Total_Amount__c,
     OrderItems.Product2.Category__c
  3. Decision: Eligibility Check
     - If (TODAY() - Order.CreatedDate) > 30 → IneligibilityReason = "Order is more than 30 days old"
     - If Order.Status NOT IN ('Delivered', 'In Transit') → IneligibilityReason = "Order not yet delivered"
     - If Order.Total_Amount__c > 500 → IneligibilityReason = "Orders over $500 require manager approval"
     - If Account.Restricted__c = True → IneligibilityReason = "Account restricted"
     - If Product2.Category__c IN ('Personalized', 'Digital') → IneligibilityReason = "Category not eligible"
  4. Formula: RefundAmount = IF(Order.Discount_Code__c != null,
                                 (Order.Total_Amount__c - Order.Shipping_Cost__c) * 0.95,
                                 Order.Total_Amount__c - Order.Shipping_Cost__c)
  5. Return: IsEligible, RefundAmount, IneligibilityReason
```

**Fix Applied:**
- Deterministic logic in Flow (accurate, testable, maintainable)
- Instructions focus on WHEN to call the action and HOW to interpret results
- Clear separation: LLM handles conversation, Flow handles rules

---

### Anti-Pattern 1.4: Format Validation in Instructions

**The Problem:** Asking the LLM to validate email addresses, phone numbers, or other formats.

#### ❌ BAD: LLM Format Validation
```yaml
Topic: Update Contact Info
Instructions: |
  When the customer provides an email address, verify it has an @ symbol
  and a domain (like .com or .org). If it doesn't, ask them to provide a
  valid email.

  For phone numbers, make sure they're in the format (XXX) XXX-XXXX and
  have exactly 10 digits. If not, ask them to reformat it.
```

**Why It's Bad:**
- LLMs are unreliable at pattern matching (they may accept invalid formats)
- Users provide formats in many valid ways: "+1-555-123-4567", "555.123.4567"
- Wastes tokens on a task better suited for regex

#### ✅ GOOD: Flow/Apex Validation
```yaml
Topic: Update Contact Info
Instructions: |
  Ask the customer for their new email address or phone number. Once provided,
  use the "Validate and Update Contact" action. If the action returns an error
  (invalid format), explain the issue and ask for a corrected value.
```

```apex
// Apex Action: Validate and Update Contact
@InvocableMethod(label='Validate and Update Contact')
public static List<Result> validateAndUpdate(List<Request> requests) {
    Request req = requests[0];
    Result res = new Result();

    // Email validation
    if (String.isNotBlank(req.email)) {
        Pattern emailPattern = Pattern.compile('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$');
        if (!emailPattern.matcher(req.email).matches()) {
            res.success = false;
            res.errorMessage = 'Invalid email format. Please provide a valid email like name@example.com';
            return new List<Result>{ res };
        }
    }

    // Phone validation (E.164 or 10-digit US)
    if (String.isNotBlank(req.phone)) {
        String cleaned = req.phone.replaceAll('[^0-9]', '');
        if (cleaned.length() != 10 && cleaned.length() != 11) {
            res.success = false;
            res.errorMessage = 'Invalid phone format. Please provide a 10-digit phone number';
            return new List<Result>{ res };
        }
        req.phone = cleaned; // Normalize
    }

    // Update Contact
    Contact contact = [SELECT Id FROM Contact WHERE Id = :req.contactId];
    if (String.isNotBlank(req.email)) contact.Email = req.email;
    if (String.isNotBlank(req.phone)) contact.Phone = req.phone;
    update contact;

    res.success = true;
    return new List<Result>{ res };
}
```

**Fix Applied:**
- Deterministic regex validation in Apex
- Agent instructions focus on conversation flow, not validation logic
- Normalization (removing dashes, parentheses) handled in code

---

## Category 2: Topic Architecture Anti-Patterns

### Anti-Pattern 2.1: Monolithic Topics

**The Problem:** Cramming too many actions into a single topic.

#### ❌ BAD: One Topic for Everything
```yaml
Topic: Customer Service
Classification Description: |
  Customer needs help with orders, returns, account issues, technical support,
  product questions, billing, or anything else.

Actions (20+ actions):
  - Check Order Status
  - Cancel Order
  - Modify Order
  - Initiate Return
  - Check Return Status
  - Update Email
  - Reset Password
  - Get Product Info
  - Search Knowledge Base
  - Create Case
  - Escalate to Agent
  - Process Refund
  - Update Billing
  - Check Inventory
  ... (6 more)
```

**Why It's Bad:**
- Topic classification becomes too broad (everything matches)
- LLM struggles to choose the right action from 20+ options
- Maintenance nightmare (changes to one action risk affecting others)
- Can't optimize instructions for specific workflows

#### ✅ GOOD: Focused Topics
```yaml
Topic: Order Management
Classification Description: |
  Customer needs help with an existing order—checking status, modifying,
  or canceling. Includes questions like "Where's my order?", "Cancel my order",
  "Change my shipping address".

Scope: Actions on existing orders (read/update/cancel)

Actions (5 actions):
  - Check Order Status
  - Cancel Order
  - Modify Order Address
  - Expedite Shipping
  - Escalate Order Issue
```

```yaml
Topic: Returns and Refunds
Classification Description: |
  Customer wants to return a product or request a refund. Includes phrases
  like "I want to return this", "Start a return", "Get a refund", "Return policy".

Scope: Initiating returns, checking return status, processing refunds

Actions (4 actions):
  - Check Return Eligibility
  - Initiate Return
  - Check Return Status
  - Issue Refund
```

```yaml
Topic: Account Settings
Classification Description: |
  Customer wants to update account information—email, password, phone, address.
  Includes "Change my email", "Reset password", "Update my profile".

Scope: Account credential and profile updates

Actions (4 actions):
  - Update Email
  - Reset Password
  - Update Phone
  - Update Shipping Address
```

**Fix Applied:**
- 20 actions → 3 topics with 4-5 actions each
- Each topic has clear scope and focused classification description
- Instructions can be topic-specific (e.g., Returns requires empathy, Order Management requires urgency)

**Guideline:** Keep topics to **5-7 actions maximum**. If you need more, split into multiple topics.

---

### Anti-Pattern 2.2: Overlapping Topic Classification Descriptions

**The Problem:** Two topics have similar classification descriptions, causing misrouting.

#### ❌ BAD: Ambiguous Overlap
```yaml
Topic A: Technical Support
Classification Description: |
  Customer is experiencing problems with the product or app. Includes issues
  like crashes, errors, performance problems, or features not working.

Topic B: Product Help
Classification Description: |
  Customer has questions about how the product works, how to use features,
  or needs help with setup.
```

**Overlap Example:**
```
User: "The app isn't syncing my data."

Is this Topic A (problem = technical support) or Topic B (how to use sync = product help)?
```

**Why It's Bad:**
- Ambiguity causes misclassification
- User gets routed to wrong topic, needs re-routing (bad UX)
- Similar keywords in both descriptions confuse the classifier

#### ✅ GOOD: Clear Boundaries
```yaml
Topic A: Technical Support
Classification Description: |
  Customer reports an error, crash, bug, or unexpected behavior—something that
  should work but doesn't. Includes phrases like "keeps crashing", "error message",
  "broken", "not working", "stopped working".

Scope: Diagnosing and fixing malfunctions, not expected behavior.

Topic B: Feature Education
Classification Description: |
  Customer asks how to use a feature, configure settings, or accomplish a task
  they haven't done before. Includes "How do I...", "Where is the setting for...",
  "Show me how to...".

Scope: Teaching expected functionality, not troubleshooting errors.
```

**Disambiguation:**
```
User: "The app isn't syncing my data."

Topic A matches ("not working" = malfunction → Technical Support)

vs.

User: "How do I sync my data?"

Topic B matches ("How do I" = learning task → Feature Education)
```

**Fix Applied:**
- Topic A = things that SHOULD work but DON'T (errors, bugs)
- Topic B = things that DO work, user needs to learn HOW (education)
- Clear keyword distinctions: "error", "crash", "broken" vs. "how do I", "where is", "show me"

---

### Anti-Pattern 2.3: Missing Escalation Paths

**The Problem:** No clear path to human agent when AI can't resolve the issue.

#### ❌ BAD: Dead-End Conversation
```
User: I've tried resetting my password 3 times and it's still not working.

Agent: Let me help you reset your password. What's your email address?

User: I already did this! It's not working!

Agent: I can send you another reset link. What's your email?

User: [gives up and leaves]
```

**Why It's Bad:**
- Agent stuck in loop, repeating same solution
- No recognition of repeated failure
- User frustration increases, no human fallback

#### ✅ GOOD: Escalation After N Failures
```yaml
Topic: Password Reset
Instructions: |
  Guide the user through password reset. If the user indicates they've already
  tried resetting and it didn't work, or if you've sent 2 reset links and the
  issue persists, escalate to technical support:

  "It sounds like there might be a deeper issue with your account. Let me
  connect you with a technical specialist who can investigate. They'll have
  all the details from our conversation."

  Use the Escalate to Support action to route them to Omni-Channel.
```

**Example Conversation:**
```
User: I've tried resetting my password 3 times and it's still not working.

Agent: I'm sorry the reset links haven't worked. This sounds like it might be
       a deeper issue with your account setup.

       Let me connect you with a technical specialist who can investigate and
       resolve this right away. They'll have all the details from our chat.

       [Escalation triggered]
```

**Fix Applied:**
- Instructions explicitly define failure condition (2 attempts)
- Escalation is automatic after threshold
- Agent acknowledges frustration and sets expectation

---

## Category 3: Context and Memory Anti-Patterns

### Anti-Pattern 3.1: Ignoring Context Carryover

**The Problem:** Not referencing information the user provided in earlier turns.

#### ❌ BAD: Redundant Questions
```
User: I need to return my order. The order number is 12345678 and my email is
      john@example.com.

Agent: I can help with that! What's your order number?

User: I just told you, 12345678.

Agent: Thank you. And what's your email address?

User: [frustrated] john@example.com, I already said that!
```

**Why It's Bad:**
- User explicitly provided both pieces of info in first message
- Agent re-asks both, wasting time and frustrating user
- Makes agent seem "dumb" and non-conversational

#### ✅ GOOD: Context-Aware Response
```yaml
Topic: Returns
Instructions: |
  To process a return, you need the order number and the customer's email.
  Check the conversation history—if the customer already provided these, use
  them. Don't re-ask for information the customer has already given.

  Acknowledge what they've provided: "Got it, I have your order number (12345678)
  and email (john@example.com). Let me look up your order..."
```

**Example Conversation:**
```
User: I need to return my order. The order number is 12345678 and my email is
      john@example.com.

Agent: Got it! I have your order number (12345678) and email (john@example.com).
       Let me pull up your order details...

       [Agent retrieves order]

       I see your order for [Product Name], delivered on Jan 10th. What's the
       reason for the return?
```

**Fix Applied:**
- Instructions remind agent to check conversation history
- Agent acknowledges received info (builds trust)
- Only asks for missing information

---

### Anti-Pattern 3.2: Hard-Coding Responses Instead of Using Knowledge

**The Problem:** Writing specific answers in instructions instead of retrieving from Knowledge articles.

#### ❌ BAD: Hard-Coded Answer
```yaml
Topic: Shipping FAQs
Instructions: |
  If the customer asks about shipping costs, respond:
  "Standard shipping is free for orders over $50. Express shipping is $9.99.
  International shipping costs vary by country—Canada is $15, UK is $20,
  Australia is $25."
```

**Why It's Bad:**
- Shipping costs change → instructions become stale
- Can't update easily (need to edit agent, redeploy)
- No version control or approval workflow for content changes
- Doesn't scale (what about 100+ countries?)

#### ✅ GOOD: Knowledge Article Retrieval
```yaml
Topic: Shipping FAQs
Instructions: |
  For questions about shipping costs, delivery times, or international shipping,
  use the "Search Knowledge: Shipping" action. Summarize the relevant article
  and cite the article ID.

  If no article matches, say "I don't have that specific information. Let me
  connect you with our shipping team for details."
```

```yaml
Action: Search Knowledge: Shipping
Type: Knowledge Article Search
Query: Dynamically generated based on user question
Filters: ArticleType = 'Shipping_Policy'
```

**Example Knowledge Article:**
```
Title: International Shipping Costs (KB-00482)
Content:
  - Canada: $15 (5-7 business days)
  - UK: $20 (7-10 business days)
  - Australia: $25 (10-14 business days)
  - All other countries: Contact shipping team for quote
```

**Example Conversation:**
```
User: How much is shipping to Canada?

Agent: Shipping to Canada is $15 and takes 5-7 business days.

       [Source: KB-00482]

       Would you like to place an order, or do you have other questions?
```

**Fix Applied:**
- Content lives in Knowledge (managed by non-technical teams)
- Easy to update (edit article, no agent redeployment)
- Agent focuses on retrieval and summarization, not content storage

---

## Category 4: Testing Anti-Patterns

### Anti-Pattern 4.1: Testing Only Happy Paths

**The Problem:** Only testing successful scenarios, ignoring edge cases and failures.

#### ❌ BAD: Happy-Path-Only Test Cases
```yaml
Test Case 1: Successful password reset
  User: "I forgot my password"
  Agent: Asks for email → Sends reset link → User confirms → Success

Test Case 2: Successful order lookup
  User: "Where's my order?" → Provides order number → Agent retrieves order → Success

Test Case 3: Successful return
  User: "I want to return X" → Provides order number → Agent starts return → Success
```

**Why It's Bad:**
- Doesn't test error handling (API failures, invalid inputs, out-of-scope requests)
- Doesn't test edge cases (order number not found, reset link expired, ineligible return)
- Real users will encounter these scenarios — agent will fail in production

#### ✅ GOOD: Comprehensive Test Coverage
```yaml
# Happy Path
Test Case 1: Successful password reset
  User: "I forgot my password"
  Expected: Agent asks for email, sends reset link, confirms success

# Error Handling
Test Case 2: Invalid email format
  User: "My email is john@invalid"
  Expected: Agent asks for valid email format

Test Case 3: Reset link expired
  User: "The reset link says it's expired"
  Expected: Agent sends new link with note about 15-minute expiration

# Edge Cases
Test Case 4: Customer already reset password
  User: "I already reset my password but I'm still locked out"
  Expected: Agent escalates to technical support (account issue, not password issue)

# Out of Scope
Test Case 5: Unrelated question during password reset
  User: "I forgot my password"
  Agent: Asks for email
  User: "Actually, do you ship to Canada?"
  Expected: Agent answers shipping question, then returns to password reset

# Malicious Input
Test Case 6: SQL injection attempt
  User: "My email is admin' OR 1=1--"
  Expected: Agent treats as invalid email, asks for valid format (sanitization handled by Apex)
```

**Fix Applied:**
- 80/20 rule: 20% happy path, 80% edge cases/errors
- Test error recovery (expired links, API failures)
- Test topic switching and out-of-scope handling
- Test input sanitization (security)

---

## Category 5: Tone and Language Anti-Patterns

### Anti-Pattern 5.1: Robotic Corporate Speak

**The Problem:** Using formal, impersonal language that sounds like a legal document.

#### ❌ BAD: Corporate Jargon
```
Agent: Your inquiry has been received and is currently being processed by our
       fulfillment system. Please be advised that order modifications are subject
       to availability and processing timelines as outlined in our Terms of Service,
       Section 4.3. We appreciate your patience as we work to facilitate your request.
```

**Why It's Bad:**
- Sounds like a robot, not a conversation
- Uses jargon ("facilitate", "be advised", "fulfillment system")
- No personality or warmth

#### ✅ GOOD: Conversational Tone
```yaml
Agent-Level Instructions (Tone: Casual):
  Use everyday language. Write like you're texting a friend, but professional.
  Use contractions (I'm, you're, we'll). Keep sentences short.
```

```
Agent: Got it! I'm checking if we can still modify your order...

       Good news—your order hasn't shipped yet, so I can update it. What
       would you like to change?
```

**Fix Applied:**
- Contractions (I'm, hasn't)
- Short sentences
- Active voice ("I'm checking" not "Your inquiry is being processed")
- Conversational transitions ("Got it!", "Good news")

---

### Anti-Pattern 5.2: Over-Apologizing

**The Problem:** Apologizing excessively, making the agent sound insincere or weak.

#### ❌ BAD: Excessive Apologies
```
User: My order is late.

Agent: I'm so sorry to hear that your order is late. I sincerely apologize for
       any inconvenience this has caused. I'm truly sorry for the delay and I
       apologize for the frustration this must have caused. Let me apologize
       again and look into this for you. I'm very sorry about this situation.
```

**Why It's Bad:**
- 5 apologies in one message (overkill)
- Sounds insincere and robotic
- Wastes time — user wants action, not apologies

#### ✅ GOOD: One Apology + Action
```yaml
Agent-Level Instructions:
  When something goes wrong, apologize once, then focus on the solution:
  "I'm sorry [problem happened]. Let me [action to fix it]."

  Don't repeat apologies. Show empathy through action, not just words.
```

```
User: My order is late.

Agent: I'm sorry your order is delayed. Let me check the status and see what's
       going on...

       [Retrieves order]

       Your order was delayed due to a weather issue at the warehouse. It's now
       in transit and will arrive by Friday. I can offer you a $10 credit for
       the inconvenience—would that help?
```

**Fix Applied:**
- One apology at the start
- Focus shifts immediately to action (checking status)
- Provides explanation and compensation (solution-oriented)

---

## Summary: Anti-Pattern Checklist

Before deploying your Agentforce agent, validate against these anti-patterns:

### Instructions
- [ ] No absolute language ("must", "always", "never")
- [ ] Positive framing ("do this" not "don't do that")
- [ ] Business rules in Flow/Apex, not instructions
- [ ] Format validation in code, not instructions

### Topic Architecture
- [ ] Topics have 5-7 actions max (not monolithic)
- [ ] Classification descriptions don't overlap
- [ ] Escalation paths defined for failure scenarios

### Context & Memory
- [ ] Agent checks prior turns before re-asking
- [ ] Content retrieved from Knowledge, not hard-coded
- [ ] Context carried across topic transitions

### Testing
- [ ] Tests cover errors and edge cases, not just happy paths
- [ ] Input sanitization tested (security)
- [ ] Out-of-scope handling tested

### Tone & Language
- [ ] Conversational tone (contractions, short sentences)
- [ ] One apology + action (not excessive apologies)
- [ ] No corporate jargon or robotic phrasing

Use this as a pre-launch checklist to catch common mistakes before they reach production.
