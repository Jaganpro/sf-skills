<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
# Industry Frameworks for Agentforce Conversation Design

This guide maps five leading conversation design frameworks to Salesforce Agentforce implementations. Use these frameworks as lenses to evaluate and improve your agent's conversational quality.

---

## Framework 1: Google Conversation Design

**Origin:** Google Assistant design team
**Focus:** Human-centered conversation, cooperative principles, persona development
**Key Resource:** [Google Conversation Design Guide](https://developers.google.com/assistant/conversation-design)

### Core Principles

#### 1. Cooperative Principle (Grice's Maxims)

Google adapts philosopher Paul Grice's four maxims for conversational AI:

##### Maxim of Quantity
**Principle:** Provide the right amount of information—not too much, not too little.

**Agentforce Application:**
```yaml
# Topic-Level Instruction Example
Instructions: |
  When answering questions, provide 2-3 sentences summarizing the answer.
  If the customer needs more detail, offer to expand. Don't dump entire
  Knowledge articles—summarize key points and offer "Would you like more details?"
```

**Example Violation:**
```
User: What's your return policy?

Agent: Our return policy states that all returns must be initiated within
       30 days of purchase per Section 4.2 of our Terms of Service, which
       was updated on March 15, 2025, to align with federal consumer protection
       guidelines established by the FTC in 2024, building on the previous
       framework from... [500 more words]
```

**Example Adherence:**
```
User: What's your return policy?

Agent: You can return items within 30 days of purchase for a full refund.
       The item must be unused with original packaging.

       Would you like details on how to start a return?
```

##### Maxim of Quality
**Principle:** Be truthful and evidence-based. Don't guess or hallucinate.

**Agentforce Application:**
```yaml
# Agent-Level Instruction Example
Instructions: |
  Only provide information you can verify through Knowledge articles, Flow
  data, or Apex actions. If you don't know the answer, say "I don't have
  that information, but I can connect you with someone who does" rather
  than guessing.

  When citing policies or procedures, always reference the Knowledge article ID.
```

**Anti-Pattern: Hallucination**
```
User: Do you offer price matching?

Agent: Yes, we match any competitor's price within 15 days of purchase!
       [WRONG—policy doesn't exist, agent invented it]
```

**Correct: Acknowledge Uncertainty**
```
User: Do you offer price matching?

Agent: I don't see a price matching policy in our current documentation.
       Let me connect you with a sales specialist who can answer that
       definitively. Would that work for you?
```

##### Maxim of Relation (Relevance)
**Principle:** Stay on topic. Don't introduce unrelated information.

**Agentforce Application:**
```yaml
# Topic-Level Instruction Example
Topic: Password Reset
Instructions: |
  Focus exclusively on helping the customer reset their password. Don't
  offer information about other account settings, product features, or
  promotions unless the customer explicitly asks.
```

**Example Violation:**
```
User: I forgot my password.

Agent: I can help you reset your password! By the way, did you know we just
       launched a new mobile app with biometric login? It's much more secure
       than passwords and supports Face ID and fingerprint scanning. You can
       download it from... [off-topic tangent]
```

**Example Adherence:**
```
User: I forgot my password.

Agent: I can help you reset it. What's the email address associated with
       your account?
```

##### Maxim of Manner (Clarity)
**Principle:** Be clear, concise, and orderly. Avoid jargon and ambiguity.

**Agentforce Application:**
```yaml
# Agent-Level Tone Setting
Tone: Casual
Instructions: |
  Use everyday language. Avoid technical jargon unless the customer uses it
  first. When providing multi-step instructions, number the steps clearly.
```

**Example Violation:**
```
Agent: To authenticate your identity, we'll need to initiate a verification
       protocol via SMS OTP to your registered MSISDN.
```

**Example Adherence:**
```
Agent: To verify your identity, I'll send a code to your phone number.
       Let me know when you receive it.
```

#### 2. Persona Development

**Google's Framework:**
- **Professional:** Knowledgeable, formal, authoritative
- **Friendly:** Warm, conversational, empathetic
- **Enthusiastic:** Energetic, motivating, positive

**Agentforce Mapping:**

| Google Persona | Agentforce Tone | Use Case |
|----------------|-----------------|----------|
| Professional | Formal | Financial services, healthcare, legal |
| Friendly | Casual | Retail, hospitality, consumer tech |
| Enthusiastic | Casual (with positivity) | Fitness, education, community platforms |

**Example Configuration:**
```yaml
Agent Settings:
  Tone: Casual
  Welcome Message: |
    Hey there! I'm here to help with your order, account, or any questions
    you have. What can I do for you today?

Agent-Level Instructions: |
  Be conversational and warm, like a helpful friend. Use contractions (I'm,
  you're, let's) and casual phrasing. Show empathy when customers are
  frustrated. Avoid corporate jargon—say "fix this" not "remediate the issue."
```

#### 3. Repair Strategies (Error Handling)

Google identifies four error types and recovery strategies:

##### Error Type 1: No Match
**Problem:** Agent didn't understand the user's input.

**Google Strategy:** Rapid reprompt with context.

**Agentforce Implementation:**
```yaml
Topic: Fallback / Out of Scope
Instructions: |
  When you don't understand the request, acknowledge it and offer choices:
  "I'm not sure I understood that. Are you looking for help with:
   • Order status
   • Returns
   • Technical support
   • Something else
  Which is closest to what you need?"
```

##### Error Type 2: Ambiguity
**Problem:** User's intent could match multiple topics.

**Google Strategy:** Clarify with options.

**Agentforce Implementation:**
```
User: I need to change my account.

Agent: I can help with that! What would you like to change?
       • Email address or password
       • Billing/payment method
       • Shipping address
       • Subscription plan
```

##### Error Type 3: System Error
**Problem:** Action failed (API timeout, Flow error).

**Google Strategy:** Apologize, explain, offer alternative.

**Agentforce Implementation:**
```yaml
Action: Create Case (Apex)
Error Handling: |
  If this action fails, apologize and offer manual escalation:
  "I'm having trouble creating your case in the system right now. Let me
  connect you with an agent who can file it manually. This will just take
  a moment."
```

##### Error Type 4: Unexpected Input
**Problem:** User provides information in wrong format or context.

**Google Strategy:** Gentle correction with example.

**Agentforce Implementation:**
```
Agent: What's the order number you need help with?

User: iPhone 15 Pro

Agent: I'll need the order number to look that up—it's a 8-digit number
       like 12345678, usually found in your confirmation email.
       Can you find that order number?
```

---

## Framework 2: IBM Natural Conversation Framework

**Origin:** IBM Watson design team
**Focus:** Conversation patterns, state management, intent recognition
**Key Resource:** IBM Watson Assistant documentation

### Core Concepts

#### 1. Five Conversation Patterns

IBM's patterns map directly to Agentforce implementations (see [conversation-patterns.md](conversation-patterns.md)):

| IBM Pattern | Agentforce Implementation | Primary Mechanism |
|-------------|---------------------------|-------------------|
| Q&A | Knowledge retrieval, simple lookups | Knowledge actions, Flow queries |
| Information Gathering | Multi-turn data collection | Flow with input variables |
| Process Automation | Guided workflows | Sequential actions with state tracking |
| Troubleshooting | Diagnosis trees | Branching Flow logic |
| Human Handoff | Escalation | Omni-Channel routing |

**IBM's Key Insight:** Most conversations are combinations of these five patterns, not standalone interactions.

**Agentforce Application:** Design multi-topic agents where Topic A (Q&A) can transition to Topic B (Information Gathering) based on user response.

#### 2. Conversation State Management

**IBM Framework:**
- **Context Variables:** Store data across turns (user inputs, intermediate results)
- **Slots:** Required information to complete an intent
- **Session Variables:** Temporary data cleared after conversation ends

**Agentforce Equivalent:**

| IBM Concept | Agentforce Implementation |
|-------------|---------------------------|
| Context Variables | Agentforce maintains turn-by-turn context automatically |
| Slots | Flow Input Variables in Information Gathering actions |
| Session Variables | Flow Variables scoped to conversation session |

**Example: Multi-Turn State Tracking**
```yaml
Flow: Collect Case Details
Variables:
  - Subject (Text)
  - Description (Text)
  - Priority (Picklist)
  - ProductId (Text)
  - HasSubject (Boolean)
  - HasDescription (Boolean)

Decision: What to Ask Next
  - If HasSubject = False → Ask for Subject
  - If HasDescription = False → Ask for Description
  - If Priority = null → Ask for Priority
  - If all required filled → Create Case
```

#### 3. Intent Confidence Thresholds

**IBM Recommendation:**
- **High confidence (>0.8):** Execute action immediately
- **Medium confidence (0.5-0.8):** Confirm with user before executing
- **Low confidence (<0.5):** Clarify intent

**Agentforce Application:**

Agentforce doesn't expose confidence scores directly, but you can implement confirmation patterns:

```yaml
Topic: Delete Account
Instructions: |
  This is a high-impact action. Before proceeding, always confirm:
  "Just to confirm—you want to permanently delete your account and all
  associated data? This cannot be undone. Type YES to confirm."

  Only execute the deletion if the customer explicitly types YES.
```

#### 4. Digression Handling

**IBM Framework:** Allow users to digress (go off-topic mid-conversation), then return to original topic.

**Example Digression:**
```
Agent: What's your order number? [Information Gathering for refund]

User: Actually, quick question—do you ship to Canada? [Digression to Q&A]

Agent: Yes, we ship to Canada! Shipping takes 5-7 business days.

       Now, back to your refund—what's the order number? [Return to original topic]
```

**Agentforce Implementation:**

Agentforce handles topic switching automatically via classification. To preserve context across digression:

```yaml
Agent-Level Instructions: |
  If the customer asks an unrelated question mid-conversation, answer it
  briefly, then return to the task at hand. For example:

  "Yes, we ship internationally! Now, to process your refund, what's the
  order number?"

  This keeps the conversation moving forward without ignoring the customer.
```

---

## Framework 3: PatternFly AI Design System

**Origin:** Red Hat's open-source design system
**Focus:** Enterprise AI UX patterns, transparency, ethical AI
**Key Resource:** [PatternFly AI Design Guidelines](https://www.patternfly.org/ai)

### Core Principles for Enterprise AI

#### 1. Transparency & Explainability

**Principle:** Users should understand when they're talking to AI, what the AI can/can't do, and how decisions are made.

**Agentforce Application:**

```yaml
Welcome Message (Agent Settings):
  Hi! I'm an AI assistant trained to help with orders, returns, and account
  questions. I can answer most questions instantly, but I'll connect you with
  a specialist for complex issues.

  What can I help you with today?

Agent-Level Instructions: |
  When you use data to make a recommendation, cite the source. For example:
  "Based on your order history, I recommend Product X" or "According to our
  return policy (Article KB-12345), you're eligible for a full refund."
```

**Anti-Pattern: Hidden AI**
```
❌ Don't pretend to be human:
   "Hi, I'm Sarah from Customer Service!"

✅ Be transparent:
   "Hi! I'm an AI assistant here to help with your order."
```

#### 2. Feedback Loops

**Principle:** Allow users to correct the AI and provide feedback.

**Agentforce Application:**

```yaml
Agent-Level Instructions: |
  After providing an answer or completing an action, ask:
  "Did that answer your question?" or "Is there anything else I can help with?"

  If the customer says your answer was wrong or unhelpful, apologize and
  offer escalation: "I'm sorry that wasn't helpful. Let me connect you with
  a specialist who can assist."
```

**Pattern: Thumbs Up/Down**

While Agentforce doesn't have built-in thumbs up/down UI, you can implement feedback via:
- **Post-Chat Survey:** Triggered via Flow after conversation ends
- **Explicit Feedback Prompt:** "Was this helpful? Reply YES or NO."

#### 3. Progressive Disclosure

**Principle:** Show information incrementally—don't overwhelm users upfront.

**Agentforce Application:**

```yaml
# BAD: Information Overload
Agent: Our return policy allows returns within 30 days of purchase with original
       packaging and receipt. Items must be unused. Electronics have a 15-day
       window. Refunds are processed in 5-7 days. We don't accept returns on
       personalized items. You can initiate returns online or mail them to...
       [200 more words]

# GOOD: Progressive Disclosure
Agent: You can return items within 30 days for a full refund.

       Would you like to:
       • Start a return now
       • See the full return policy
       • Ask a specific question about returns
```

#### 4. Error Prevention & Recovery

**Principle:** Design guardrails to prevent errors, and provide clear recovery paths when errors occur.

**Agentforce Application:**

**Prevention via Validation:**
```yaml
Action: Update Email Address
Action-Level Instructions: |
  Before updating the email, validate the format. If the customer provides
  an invalid email (missing @, no domain), respond:
  "That doesn't look like a valid email address. Email addresses look like
  name@example.com. Can you double-check and provide it again?"
```

**Recovery via Undo:**
```yaml
Topic: Cancel Subscription
Instructions: |
  After canceling, inform the customer: "Your subscription has been canceled.
  If you change your mind, you can reactivate it within 30 days by contacting
  support—no penalties."
```

#### 5. Loading States & Wait Time Communication

**Principle:** Set expectations when the AI is processing.

**Agentforce Application:**

For long-running actions (Apex callouts, complex Flows):

```yaml
Action: Run Credit Check (Apex)
Action-Level Instructions: |
  This action takes 10-15 seconds. Before calling it, tell the customer:
  "Let me run a quick credit check—this will take about 15 seconds."

  This prevents the customer from thinking the agent is frozen.
```

**Pattern: Acknowledge Before Acting**
```
Agent: Let me look up your order details... [acknowledge, then act]
       [5 second pause while Flow runs]
       Here's what I found: Order #12345, shipped on Jan 15th.
```

---

## Framework 4: Salesforce Conversational AI Guide

**Origin:** Salesforce CX design team
**Focus:** Brand voice, Einstein-specific patterns, accessibility
**Key Resource:** Salesforce Help (search "Conversational AI Best Practices")

### Core Principles

#### 1. Brand Voice Consistency

**Principle:** Your agent should sound like your brand across all channels (chat, email, phone, social).

**Agentforce Application:**

Define brand voice in a style guide, then encode in Agent-Level Instructions:

**Example: Casual Tech Brand**
```yaml
Agent-Level Instructions: |
  Our brand voice is friendly, approachable, and knowledgeable. Use:
  - Contractions (I'm, you're, let's)
  - Conversational transitions (Got it, Perfect, No problem)
  - Emoji sparingly (only for empathy: "I'm sorry 😔" or celebration: "All set! 🎉")

  Avoid:
  - Corporate jargon (leverage, utilize, facilitate)
  - Robotic phrasing (Your request has been processed)
  - Excessive formality (Dear Valued Customer)
```

**Example: Formal Financial Brand**
```yaml
Agent-Level Instructions: |
  Our brand voice is professional, trustworthy, and precise. Use:
  - Complete sentences (no contractions)
  - Formal transitions (Certainly, I understand, Thank you for confirming)
  - No emoji

  Avoid:
  - Slang or colloquialisms (sure thing, no worries)
  - Overly casual phrasing (Hey! What's up?)
  - Humor (this is sensitive financial data)
```

#### 2. LLM Prompt Consistency

**Principle:** Instructions should use consistent phrasing to ensure predictable LLM behavior.

**Agentforce Application:**

**Anti-Pattern: Conflicting Instructions**
```yaml
Agent-Level: |
  Always provide detailed explanations for your recommendations.

Topic-Level: |
  Keep responses under 2 sentences.
```

**Best Practice: Hierarchical Clarity**
```yaml
Agent-Level: |
  Provide concise responses (2-3 sentences) unless the customer asks for
  more detail.

Topic-Level (Technical Support): |
  For troubleshooting steps, provide numbered instructions. You can exceed
  3 sentences when walking through multi-step solutions.
```

#### 3. Accessibility (WCAG Compliance)

**Principle:** Conversations should be accessible to users with disabilities.

**Agentforce Application:**

| Accessibility Need | Design Pattern |
|--------------------|----------------|
| **Screen Reader Users** | Avoid relying on formatting (bold, italics) to convey meaning. Say "IMPORTANT:" instead of just using bold. |
| **Cognitive Disabilities** | Use simple language, short sentences, bullet points for lists. |
| **Visual Impairments** | Don't use color alone to convey info ("click the red button" → "click the Cancel button") |
| **Motor Impairments** | Offer button-based choices, not just free-text input. |

**Example: Button-Based Choices**
```yaml
Agent: What would you like help with today?
       [Order Status] [Returns] [Technical Support] [Talk to a Person]

       # Instead of forcing free-text input, provide clickable options
```

In Agentforce, you can implement this via:
- **Quick Reply Buttons:** Configured in Chat Settings (Embedded Service)
- **Prompt Text:** "Reply 1 for Order Status, 2 for Returns, 3 for Technical Support"

---

## Framework 5: Salesforce Architect Agentic Patterns

**Origin:** Salesforce Architect team
**Focus:** Agent taxonomy, multi-agent systems, orchestration
**Key Resource:** Architect Blog, Dreamforce '25 sessions

### Agent Taxonomy

Salesforce defines five agentic patterns based on autonomy and collaboration:

#### 1. Conversational Agents (Agentforce)

**Definition:** React to user input in real-time via chat/voice.

**Characteristics:**
- User-initiated
- Turn-by-turn interaction
- Context-aware within session
- Scoped to specific domains (Topics)

**Agentforce Implementation:** This is the default Agentforce pattern.

**Use Cases:**
- Customer support chatbots
- IT helpdesk assistants
- Sales qualification bots

#### 2. Proactive Agents

**Definition:** Initiate conversations based on triggers (e.g., abandoned cart, case SLA breach).

**Characteristics:**
- System-initiated
- Event-driven
- Outbound messaging (email, SMS, push notification)

**Agentforce Implementation:**
- **Trigger:** Flow triggered by Platform Event or Scheduled Job
- **Action:** Flow sends message via SMS (Twilio) or Email
- **Handoff:** If customer responds, route to conversational Agentforce agent

**Example Flow:**
```
Trigger: Case.Age > 48 hours AND Status = 'Open'
Action: Send SMS to customer: "Your support case hasn't been resolved yet.
        Reply YES to chat with an agent now."
If Response = YES: Route to Agentforce agent with case context
```

#### 3. Ambient Agents

**Definition:** Observe user activity and provide suggestions without blocking workflow.

**Characteristics:**
- Non-intrusive
- Recommendation-based
- Integrated into UI (Einstein for Sales, Einstein Activity Capture)

**Agentforce Implementation:**
- **Not native to Agentforce** (Agentforce is conversational)
- **Alternative:** Einstein Next Best Action in Salesforce UI

**Example (Outside Agentforce):**
- Sales rep views Account record → Einstein suggests "This customer is at risk of churn. Recommend scheduling a check-in call."

#### 4. Autonomous Agents

**Definition:** Execute multi-step tasks without human approval (within defined guardrails).

**Characteristics:**
- Long-running workflows
- Multi-action execution
- Operates asynchronously

**Agentforce Implementation:**
- **Example:** Agent automatically resolves cases when conditions are met
  - Trigger: Case with Type = 'Password Reset' AND Email Sent = True
  - Action: Wait 24 hours → If no customer response, auto-close case with note
  - No human approval needed (within policy)

**Guardrails Required:**
- Limit to low-risk actions (auto-close cases, send reminders, update fields)
- Never autonomous for high-risk actions (delete data, issue refunds over $X)

#### 5. Collaborative Agents (Multi-Agent Systems)

**Definition:** Multiple specialized agents working together, each handling a domain.

**Characteristics:**
- Agent-to-agent handoff
- Orchestration layer
- Shared context

**Agentforce Implementation:**

**Pattern: Domain-Specific Agents**
- **Agent 1:** Pre-Sales (lead qualification, product info)
- **Agent 2:** Order Support (order status, shipping, returns)
- **Agent 3:** Technical Support (troubleshooting, bug reports)

**Orchestration:**
- **Master Agent:** Routes to specialist agent based on user intent
- **Context Passing:** When Agent 1 hands off to Agent 2, pass conversation summary + key IDs

**Implementation:**
```yaml
Master Agent: "Customer Service Hub"
  Topic: Route to Specialist
    Instructions: |
      Determine which specialist the customer needs:
      - Pre-sales questions → Transfer to "Sales Agent"
      - Order/shipping issues → Transfer to "Order Agent"
      - Technical problems → Transfer to "Tech Support Agent"

      Use the Handoff action to transfer, passing the conversation summary.
```

---

## Framework Comparison Matrix

| Framework | Primary Focus | Best Used For | Agentforce Strength |
|-----------|---------------|---------------|---------------------|
| **Google Conversation Design** | Human-centered principles, persona | Defining agent personality, error handling | Agent-level instructions, tone settings |
| **IBM Natural Conversation** | Patterns, state management | Multi-turn flows, slot filling | Flow variables, topic transitions |
| **PatternFly AI** | Enterprise UX, transparency, ethics | Trust-building, accessibility | Welcome messages, feedback loops |
| **Salesforce Conversational AI** | Brand consistency, LLM prompts | Instruction writing, cross-channel voice | Instruction hierarchy, brand voice guide |
| **Salesforce Architect Agentic** | Agent taxonomy, orchestration | Multi-agent systems, autonomy levels | Handoff mechanisms, agent specialization |

---

## Applying Multiple Frameworks

Real-world Agentforce agents should blend frameworks:

### Example: E-Commerce Support Agent

| Design Decision | Framework Applied | Agentforce Configuration |
|-----------------|-------------------|--------------------------|
| **Persona: Friendly helper** | Google (Persona) | Tone: Casual, conversational instructions |
| **Pattern: Information Gathering for returns** | IBM (Patterns) | Flow with input variables for return request |
| **Transparency: "I'm an AI assistant"** | PatternFly (Transparency) | Welcome message disclosure |
| **Brand voice: Match website tone** | Salesforce Conv AI (Brand) | Style guide encoded in agent instructions |
| **Handoff to human for refunds >$500** | Salesforce Architect (Autonomy) | Escalation topic with Omni-Channel routing |

---

## Summary: Framework Integration Checklist

When designing an Agentforce agent, validate against all five frameworks:

- [ ] **Google:** Does my agent follow the four maxims (Quantity, Quality, Relation, Manner)?
- [ ] **Google:** Have I defined a clear persona and error recovery strategies?
- [ ] **IBM:** Have I mapped conversation patterns and implemented state management?
- [ ] **PatternFly:** Is my agent transparent about being AI? Do I have feedback loops?
- [ ] **Salesforce Conv AI:** Is my brand voice consistent across all instructions?
- [ ] **Salesforce Architect:** Have I scoped autonomy appropriately and defined handoff points?

If you answer "no" to any question, revisit your design using that framework's principles.
