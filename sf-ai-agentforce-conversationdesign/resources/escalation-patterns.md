# Escalation Patterns for Agentforce

This guide catalogs escalation triggers, routing patterns, and context handoff mechanisms for Agentforce agents. Effective escalation ensures customers reach human agents at the right time with the right context.

---

## Escalation Philosophy

**Key Principles:**
1. **Escalate Early, Not Late** — Don't exhaust the customer with failed AI attempts before escalating
2. **Context is King** — Pass conversation history, key IDs, sentiment, and attempted solutions
3. **Set Expectations** — Tell the customer what happens next ("You'll be connected in 2-3 minutes")
4. **Measure and Optimize** — Track escalation rate and reasons to improve AI containment

---

## Escalation Trigger Categories

### Trigger Category 1: Sentiment-Based Escalation

**Description:** Detect frustrated, angry, or distressed customers and escalate before the situation worsens.

#### Trigger 1.1: Frustration Detection

**Indicators:**
- Repeated phrases ("I already told you", "This is ridiculous", "For the third time")
- Profanity or strong language (filtered by Einstein Trust Layer, but tone detected)
- All-caps messages ("THIS DOESN'T WORK")
- Short, clipped responses after detailed agent messages

**Priority Level:** High

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the customer shows frustration (repeating themselves, using strong language,
  expressing disappointment), acknowledge their feelings and escalate immediately:

  "I understand this has been frustrating, and I apologize for the trouble. Let me
  connect you with a specialist who can give this their full attention right now."

  Use the "Escalate to Support" action and mark the sentiment as "Frustrated" so
  the human agent is prepared.
```

**Example Conversation:**
```
User: I've been trying to reset my password for 30 minutes!

Agent: I'm truly sorry this has taken so long. That's unacceptable, and I want
       to get this resolved for you right away.

       Let me connect you with a technical specialist who can investigate your
       account and fix this immediately. They'll have all the details from our
       conversation.

       [Escalation triggered with sentiment = "Frustrated"]
```

**Omni-Channel Routing:**
```yaml
Queue: Frustrated Customers
Priority: High (routed ahead of normal queue)
Skill Required: De-escalation Training
```

#### Trigger 1.2: Anger Detection

**Indicators:**
- Threats ("I'm going to cancel my account", "I'll report this")
- Blame statements ("Your company is terrible", "This is a scam")
- Demands ("I demand a refund", "Get me a manager NOW")

**Priority Level:** Urgent

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the customer expresses anger or makes threats, do NOT try to resolve the
  issue yourself. Escalate immediately without prolonging the conversation:

  "I'm very sorry you've had this experience. Let me connect you with a manager
  who can address this right away."

  Use the "Escalate to Manager" action with sentiment = "Angry".
```

**Omni-Channel Routing:**
```yaml
Queue: Manager Escalations
Priority: Urgent (highest priority)
Skill Required: Manager or Senior Agent
```

#### Trigger 1.3: Distress / Self-Harm

**Indicators:**
- References to self-harm, suicide, or harm to others
- Extreme emotional distress

**Priority Level:** Emergency

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the customer mentions self-harm, suicide, or extreme distress, immediately
  provide crisis resources and escalate:

  "I'm very concerned about what you've shared. Please reach out to a crisis
  support line immediately:
  • National Suicide Prevention Lifeline: 988
  • Crisis Text Line: Text HOME to 741741

  I'm also connecting you with a specialist who can provide additional support."

  Use the "Emergency Escalation" action.
```

**Omni-Channel Routing:**
```yaml
Queue: Crisis Escalations
Priority: Emergency (bypasses all queues)
Skill Required: Crisis Intervention Training
Alert: Supervisor notified immediately
```

---

### Trigger Category 2: Complexity-Based Escalation

**Description:** Escalate when the conversation becomes too complex for the AI to handle effectively.

#### Trigger 2.1: High Turn Count

**Definition:** Conversation exceeds 8-10 turns without resolution.

**Indicators:**
- Customer and agent have exchanged 8+ messages
- No clear progress toward resolution
- Same topic, multiple failed attempts

**Priority Level:** Medium

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the conversation reaches 8 turns and the issue isn't resolved, acknowledge
  the complexity and escalate:

  "I can see this is taking longer than it should. Let me connect you with a
  specialist who can dive deeper into this and get it resolved quickly."

  Use the "Escalate to Support" action with reason = "High Complexity".
```

**Example:**
```
Turn 1: User asks for help with feature
Turn 2: Agent asks clarifying question
Turn 3: User responds
Turn 4: Agent suggests solution A
Turn 5: User: "That didn't work"
Turn 6: Agent suggests solution B
Turn 7: User: "Still not working"
Turn 8: Agent escalates → "Let me connect you with a specialist..."
```

#### Trigger 2.2: Repeated Failures

**Definition:** Agent attempts the same action 2-3 times and it fails each time.

**Indicators:**
- API call fails twice
- User reports "still not working" after 2 solution attempts
- Same error occurs multiple times

**Priority Level:** Medium

**Agentforce Implementation:**

```yaml
Action-Level Instructions (for each action):
  If this action fails, apologize and try an alternative approach. If it fails
  a second time, escalate rather than attempting a third time:

  "I'm having trouble resolving this through our system. Let me connect you with
  a technical specialist who can investigate the root cause."
```

**Example (Password Reset Failure):**
```
Turn 1: Agent sends reset link
Turn 2: User: "Link doesn't work"
Turn 3: Agent sends new link with note about expiration
Turn 4: User: "Still doesn't work"
Turn 5: Agent escalates → "Let me connect you with technical support..."
```

#### Trigger 2.3: Multi-Issue Conversation

**Definition:** Customer raises 2+ unrelated issues in one conversation.

**Indicators:**
- Topic switches mid-conversation
- Multiple problems mentioned ("...and also my account is locked, and I need a refund")

**Priority Level:** Medium

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the customer raises multiple unrelated issues, acknowledge them and suggest
  escalation or sequential handling:

  "I can see you have a few things going on—[Issue A], [Issue B], and [Issue C].
  Let me connect you with a specialist who can address all of these together,
  or we can handle them one at a time. Which would you prefer?"
```

---

### Trigger Category 3: Policy-Based Escalation

**Description:** Escalate when the request requires human judgment, policy exceptions, or approval.

#### Trigger 3.1: High-Value Transactions

**Definition:** Request involves amounts exceeding agent's authorization limit.

**Examples:**
- Refund over $500
- Order cancellation over $1,000
- Credit adjustment over $100

**Priority Level:** High

**Agentforce Implementation:**

```yaml
Action: Issue Refund
Action-Level Instructions:
  If the refund amount exceeds $500, you cannot process it directly. Escalate
  to a manager:

  "Refunds over $500 require manager approval to ensure accuracy. Let me create
  an approval request and connect you with a manager who can review and process
  this right away."

  Use the "Escalate to Manager" action with reason = "High Value Refund".
```

**Omni-Channel Routing:**
```yaml
Queue: Manager Approvals
Priority: High
Skill Required: Manager or Approval Authority
Context Passed:
  - Refund Amount
  - Order ID
  - Customer Account ID
  - Reason for Refund
```

#### Trigger 3.2: Policy Exception Requests

**Definition:** Customer requests something outside standard policy.

**Examples:**
- Return after 30-day window
- Waive restocking fee
- Expedite shipping for free
- Refund for personalized/non-refundable item

**Priority Level:** Medium-High

**Agentforce Implementation:**

```yaml
Topic: Returns & Refunds
Instructions:
  If the customer is outside the 30-day return window, explain the policy but
  offer escalation:

  "Our standard return policy is 30 days, but I understand there may be special
  circumstances. Let me connect you with a manager who can review your case and
  see what options are available."

  Use the "Escalate to Manager" action with reason = "Policy Exception Request".
```

**Example Conversation:**
```
User: I bought this 45 days ago but I've been traveling. Can I still return it?

Agent: Our standard policy is 30 days, but I understand you've been traveling.
       Let me connect you with a manager who can review your situation and see
       if we can make an exception. They'll reach out shortly—does that work?

User: Yes, thank you.

Agent: Great! I've created a case and a manager will contact you within 2 hours.
       Your case number is #00284955 for reference.
```

#### Trigger 3.3: VIP / High-Priority Customers

**Definition:** Customer is flagged as VIP, enterprise account, or high-value customer.

**Indicators:**
- Account.VIP__c = true
- Account.Annual_Revenue__c > $100,000
- Account.Type = 'Enterprise'

**Priority Level:** High

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the customer is a VIP (Account.VIP__c = true), offer white-glove service:

  "I see you're one of our valued VIP customers. Let me connect you directly
  with your dedicated account manager who can give this their full attention."

  Use the "Escalate to Account Manager" action.
```

**Omni-Channel Routing:**
```yaml
Queue: VIP Support
Priority: High
Skill Required: Account Manager or VIP Support Specialist
SLA: 5-minute response time (vs. 15 minutes for standard)
```

---

### Trigger Category 4: Explicit Request Escalation

**Description:** Customer directly asks for a human agent.

#### Trigger 4.1: Direct Request for Human

**Phrases:**
- "I want to talk to a person"
- "Transfer me to an agent"
- "Get me a human"
- "I don't want to talk to a bot"

**Priority Level:** Medium

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the customer explicitly asks to speak with a human agent, honor that request
  immediately without trying to convince them to stay with the AI:

  "Of course! Let me connect you with an agent right now. They'll have all the
  details from our conversation."

  Use the "Escalate to Support" action with reason = "Customer Request".
```

**Anti-Pattern (Don't Do This):**
```
❌ User: I want to talk to a person.

❌ Agent: I'd love to help you myself! I can answer most questions. What do you
          need help with? [trying to prevent escalation]
```

**Correct Pattern:**
```
✅ User: I want to talk to a person.

✅ Agent: Of course! Connecting you now. One moment... [immediate escalation]
```

#### Trigger 4.2: Request for Manager/Supervisor

**Phrases:**
- "I want to speak to your manager"
- "Get me a supervisor"
- "Let me talk to someone in charge"

**Priority Level:** High

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the customer asks for a manager, route to the Manager queue:

  "I understand you'd like to speak with a manager. Let me connect you now."

  Use the "Escalate to Manager" action.
```

**Omni-Channel Routing:**
```yaml
Queue: Manager Escalations
Priority: High
```

---

### Trigger Category 5: Safety-Based Escalation

**Description:** Escalate when content suggests safety risk, legal concern, or emergency.

#### Trigger 5.1: Legal / Compliance Concerns

**Indicators:**
- Mentions of lawsuits, lawyers, legal action
- GDPR/privacy concerns (data deletion, access requests)
- Regulatory compliance questions

**Priority Level:** High

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the customer mentions legal action, lawyers, or compliance concerns, escalate
  to the legal team immediately:

  "I understand this is a legal matter. Let me connect you with our compliance
  team who can address this appropriately."

  Use the "Escalate to Legal" action.
```

**Omni-Channel Routing:**
```yaml
Queue: Legal / Compliance
Priority: High
Skill Required: Compliance Officer or Legal Liaison
Alert: Legal team notified via email
```

#### Trigger 5.2: Security Incidents

**Indicators:**
- "My account was hacked"
- "Someone stole my password"
- "Unauthorized charges on my card"

**Priority Level:** Urgent

**Agentforce Implementation:**

```yaml
Agent-Level Instructions:
  If the customer reports a security incident, escalate immediately to the
  security team and advise immediate action:

  "This is a security concern and needs immediate attention. Let me connect you
  with our security team right now. In the meantime:
  • Change your password immediately
  • Check your account for unauthorized activity
  • Do not click any suspicious links"

  Use the "Escalate to Security" action with reason = "Security Incident".
```

**Omni-Channel Routing:**
```yaml
Queue: Security Incidents
Priority: Urgent
Skill Required: Security Analyst
Alert: Security team notified immediately
```

---

## Agentforce Escalation Mechanism

### Built-In: Escalation Topic

Agentforce includes a pre-configured **Escalation Topic** that integrates with Omni-Channel.

**Setup Steps:**

1. **Enable Escalation Topic:**
   - Setup → Agentforce Agents → [Your Agent] → Topics
   - Enable "Escalation Topic"

2. **Configure Omni-Channel Queue:**
   - Setup → Queues → New
   - Name: "Agentforce Escalations"
   - Add Agent Members

3. **Link Queue to Escalation Topic:**
   - Agentforce Agent Settings → Escalation Topic
   - Select Omni-Channel Queue

4. **Configure Routing:**
   - Setup → Routing Configurations
   - Create rules for priority (VIP, frustrated, urgent)

**Escalation Topic Behavior:**
```
User: "I want to talk to someone."

Agent: [Escalation Topic triggered]
       "Of course! I'm transferring you to an agent now. They'll have all the
       details from our conversation."

       [Conversation routed to Omni-Channel → Human agent receives chat]
```

### Custom Escalation Actions

For domain-specific routing (e.g., "Escalate to Billing" vs. "Escalate to Tech Support"), create custom Flow actions.

**Example: Escalate to Technical Support**

```yaml
Flow: Escalate to Technical Support
Inputs:
  - ConversationId (Text)
  - Reason (Text): "High Complexity", "Repeated Failures", "Customer Request"
  - Sentiment (Picklist): "Neutral", "Frustrated", "Angry"

Steps:
  1. Get Messages: Retrieve conversation history from ConversationParticipant records
  2. Summarize Context: Use Flow Text Template to create summary
  3. Create AgentWork:
     - WorkItemId = ConversationId
     - QueueId = Tech_Support_Queue__c
     - Priority = IF(Sentiment = "Angry", "Urgent", IF(Sentiment = "Frustrated", "High", "Medium"))
     - CustomContext__c = JSON.serialize({
         'reason': Reason,
         'sentiment': Sentiment,
         'turn_count': Message count,
         'topics_attempted': List of topics covered,
         'conversation_summary': Summary text
       })
  4. Send Message to Customer:
     - "I'm connecting you with a technical specialist. You should see them join in about 2-3 minutes."
```

---

## Context Handoff Specification

**Critical:** Human agents need context to pick up where the AI left off. Pass this information:

### Essential Context (Always Pass)

| Field | Source | Example |
|-------|--------|---------|
| **Customer Name** | Contact.Name | "John Doe" |
| **Account ID** | Contact.AccountId | "0018X000001AbCd" |
| **Conversation Summary** | AI-generated summary | "Customer unable to reset password after 2 attempts" |
| **Sentiment** | Agent assessment | "Frustrated" |
| **Turn Count** | Count of messages | 8 |
| **Topics Attempted** | List of topics | "Password Reset, Account Settings" |

### Domain-Specific Context

**For Technical Support Escalations:**
- Error messages user reported
- Device/OS information (if collected)
- Troubleshooting steps already attempted
- Reproduction steps

**For Billing Escalations:**
- Order ID or Invoice ID
- Amount in question
- Billing history (last 3 transactions)

**For Refund Escalations:**
- Order ID
- Refund amount requested
- Eligibility check result (eligible vs. ineligible + reason)
- Return status

### AgentWork Custom Context Example

```json
{
  "reason": "High Value Refund",
  "sentiment": "Frustrated",
  "turn_count": 6,
  "topics_attempted": ["Returns & Refunds", "Order Status"],
  "conversation_summary": "Customer requested $800 refund for Order #12345678. Return not yet received. Customer frustrated due to shipping delay.",
  "order_id": "8018X000001XyZ",
  "refund_amount": 800,
  "return_status": "Not Received",
  "shipping_carrier": "FedEx",
  "tracking_number": "1234567890",
  "attempted_solutions": [
    "Checked order status",
    "Verified return eligibility",
    "Explained policy (return must be received first)"
  ]
}
```

**Human Agent View:**

When the human agent accepts the chat, they see:
```
┌─────────────────────────────────────────────────────────────┐
│ New Chat: John Doe (Account: Acme Corp - VIP)              │
├─────────────────────────────────────────────────────────────┤
│ Escalation Reason: High Value Refund                        │
│ Sentiment: Frustrated                                       │
│ Turn Count: 6                                               │
├─────────────────────────────────────────────────────────────┤
│ Summary: Customer requested $800 refund for Order #12345678.│
│ Return not yet received. Customer frustrated due to shipping│
│ delay.                                                       │
├─────────────────────────────────────────────────────────────┤
│ Context:                                                    │
│ • Order ID: 8018X000001XyZ                                  │
│ • Refund Amount: $800                                       │
│ • Return Status: Not Received                               │
│ • Tracking: FedEx 1234567890                                │
│                                                             │
│ AI Attempted:                                               │
│ • Checked order status                                      │
│ • Verified return eligibility                               │
│ • Explained return policy                                   │
├─────────────────────────────────────────────────────────────┤
│ [View Full Transcript] [Accept Chat]                        │
└─────────────────────────────────────────────────────────────┘
```

Human agent can immediately see the context and pick up the conversation without re-asking questions.

---

## Escalation Rate Benchmarks

**Healthy Escalation Rate:** 15-30% of conversations

| Rate | Interpretation | Action |
|------|----------------|--------|
| **<10%** | Under-escalating (customers frustrated, giving up) | Review escalation triggers—are they too strict? |
| **10-30%** | Healthy (AI handling most, escalating when needed) | Monitor and optimize |
| **30-50%** | Over-escalating (AI not confident) | Improve topic classification, add training data |
| **>50%** | AI not adding value (most convos escalate) | Redesign agent scope, simplify topics |

**Track by Reason:**
- **Customer Request:** 5-10% (acceptable, user preference)
- **Complexity:** 5-10% (improve AI training for these scenarios)
- **Frustration:** <5% (if higher, fix root cause—slow responses, repeated failures)
- **Policy Exception:** 3-7% (expected for edge cases)

---

## Escalation Quality Metrics

### Metric 1: Escalation Regret Rate

**Definition:** % of escalations that were unnecessary (human agent resolves in 1-2 turns with information AI already had).

**Target:** <10%

**How to Measure:**
- Post-escalation survey: "Could the AI have resolved this?"
- Agent tagging: "Escalation Not Needed"

**If High:** Agent is escalating too early. Improve instructions or add actions.

### Metric 2: Context Completeness Score

**Definition:** % of escalations where human agent has sufficient context to proceed without re-asking questions.

**Target:** >90%

**How to Measure:**
- Post-escalation survey: "Did you have the context you needed?"
- Track if human agent asks for information AI already collected

**If Low:** Improve context passing in AgentWork.CustomContext__c.

### Metric 3: Re-Escalation Rate

**Definition:** % of escalations that get escalated again by the human agent (e.g., L1 → L2 → Manager).

**Target:** <15%

**How to Measure:** Track AgentWork records that reference prior escalations.

**If High:** Route to higher-skilled agents initially, or improve triage logic.

---

## Summary: Escalation Decision Tree

```
START: Should I escalate?
  ├─ Is customer explicitly asking for human? → YES → Escalate (Customer Request)
  ├─ Is customer frustrated/angry? → YES → Escalate (Sentiment)
  ├─ Have I tried 2+ solutions and failed? → YES → Escalate (Complexity)
  ├─ Is this over 8 turns with no resolution? → YES → Escalate (Complexity)
  ├─ Does this require policy exception? → YES → Escalate (Policy)
  ├─ Does this require manager approval? → YES → Escalate (Policy)
  ├─ Is this a legal/security concern? → YES → Escalate (Safety)
  ├─ Is customer VIP? → Consider → Escalate (Priority)
  └─ None of the above? → NO → Continue assisting
```

**Golden Rule:** When in doubt, escalate. An unnecessary escalation is better than a frustrated customer who gave up.
