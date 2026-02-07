# Conversation Patterns for Agentforce

This guide maps IBM's Natural Conversation Framework patterns to Salesforce Agentforce implementations. Each pattern represents a fundamental conversation structure that solves specific user needs.

---

## Pattern 1: Q&A (Question & Answer)

### Description

The simplest conversation pattern—user asks a question, agent provides an answer. Typically one turn, drawing from a knowledge base or deterministic data source.

**Best for:**
- Knowledge article retrieval
- FAQ responses
- Status lookups (order status, case status)
- Policy/procedure queries

### Agentforce Implementation

**Topic Configuration:**
```yaml
Topic: Product FAQs
Classification Description: |
  Customer asks questions about product features, specifications,
  pricing, compatibility, or availability. Includes questions like
  "What does X do?", "How much does Y cost?", "Is Z compatible with...?"

Scope: Questions seeking factual information about products
```

**Actions:**
- **Search Knowledge Base** — Salesforce Knowledge article retrieval
- **Get Product Details** — Autolaunched Flow reading Product2/PricebookEntry
- **Check Inventory** — Real-time availability lookup

**Instructions (Topic-Level):**
```
Provide direct, concise answers to product questions. If multiple
articles match, offer the top 3 results and ask which is most relevant.
When inventory is low, mention availability without using urgent language.
Always cite the Knowledge article ID when referencing documentation.
```

### Conversation Example

```
User: What's the return policy for electronics?

Agent: Electronics can be returned within 30 days of purchase with original
       packaging and receipt. The item must be unused and include all
       accessories.

       Refunds are processed within 5-7 business days after we receive
       the return.

       [Source: Knowledge Article KA-03482]

       Would you like instructions on how to start a return?
```

### Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| **Returning full article text** | Information overload, poor UX | Summarize key points, offer "Would you like more details?" |
| **No follow-up offer** | Missed engagement | End with action-oriented question |
| **Multiple topics for simple FAQs** | Maintenance overhead | Use one "General FAQs" topic with many Knowledge actions |
| **Hard-coded answers in instructions** | Stale data, hard to update | Always use Knowledge actions or Flow data lookups |

### Topic Boundaries

**In Scope:**
- Factual questions with definitive answers
- Single-turn exchanges
- Information retrieval

**Out of Scope:**
- Multi-step processes (use Information Gathering pattern)
- Troubleshooting requiring diagnosis (use Troubleshooting pattern)
- Requests requiring human judgment (use Handoff pattern)

---

## Pattern 2: Information Gathering

### Description

Multi-turn conversation collecting data to complete a task. Agent asks questions sequentially, validates responses, and uses collected data to trigger an action (create record, start process, etc.).

**Best for:**
- Case creation
- Lead qualification
- Survey/feedback collection
- Appointment booking

### Agentforce Implementation

**Topic Configuration:**
```yaml
Topic: Create Support Case
Classification Description: |
  Customer wants to report a problem, open a support ticket, or
  request help with an issue. Includes phrases like "I need help",
  "Something's wrong", "Create a case", "Report an issue".

Scope: Requests to document and track a problem requiring support
```

**Actions:**
- **Collect Case Details** — Autolaunched Flow with Input Variables (Subject, Description, Priority)
- **Validate Product Serial** — Apex action checking warranty status
- **Create Case Record** — Flow creating Case with gathered data
- **Send Confirmation** — Flow sending email with case number

**Instructions (Topic-Level):**
```
Gather case details through natural conversation, not interrogation.
Required fields: Subject (brief description), Description (detailed context),
Product (from picklist), Priority (Low/Medium/High).

Ask for information you don't have yet, but don't re-ask questions if the
customer already provided the answer earlier in the conversation.

After creating the case, confirm the case number and set expectations
for response time based on priority.
```

**Instructions (Action-Level: Collect Case Details):**
```
Use this action when you have Subject, Description, Product, and Priority.
Don't call this action multiple times—wait until all required data is collected.
If the customer mentions urgency keywords (down, critical, outage), default
Priority to High.
```

### Conversation Example

```
User: I need help, my software keeps crashing.

Agent: I'm sorry to hear that! I'll create a support case to get this resolved.

       Which product are you experiencing issues with?

User: The mobile app on iOS.

Agent: Got it. Can you describe what happens when it crashes? For example,
       does it happen when you open the app, or during a specific action?

User: It crashes whenever I try to upload a photo.

Agent: Thank you. How urgent is this issue for you—is it blocking your work,
       or can you use a workaround for now?

User: I can use the web version, so it's not blocking me.

Agent: Perfect. I've created Case #00284731 for this issue: "iOS app crashes
       during photo upload". Since you have a workaround, I've set the priority
       to Medium—you'll receive a response from our team within 24 hours.

       You'll get an email confirmation shortly. Is there anything else I can
       help you with?
```

### Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| **Asking all questions upfront** | Feels like a form, not a conversation | Ask one question per turn, adapt based on answers |
| **Repeating questions** | Frustrating user experience | Track context—check previous turns before asking |
| **No validation** | Garbage data in records | Use Flow formulas for email/phone format, Apex for complex rules |
| **Creating record before confirmation** | Hard to undo, no user control | Summarize collected data and ask "Should I create the case?" |
| **Ignoring partial info in first message** | Inefficient, redundant | Parse first message—if user says "My email is X, phone is Y", don't re-ask |

### Context Management

**Critical:** Agentforce maintains conversational context across turns. Design instructions to reference prior turns:

```
When the customer provides multiple pieces of information in one message,
acknowledge all of them. For example, if they say "My email is X and my
phone is Y", respond "Got it, I have your email (X) and phone (Y) recorded."
```

### Topic Boundaries

**In Scope:**
- Collecting 3-8 fields over 3-6 turns
- Linear data collection (no branching logic)
- Creating a single record

**Out of Scope:**
- Complex branching (use Step-by-Step pattern)
- More than 8 fields (break into multiple topics or use web form)
- Updating existing records (different topic/pattern)

---

## Pattern 3: Handoff (Escalation to Human)

### Description

Transferring the conversation to a human agent when the AI cannot resolve the issue. Includes context passing, routing, and setting user expectations.

**Best for:**
- Frustrated/angry customers
- Complex edge cases outside AI scope
- Policy exceptions requiring human judgment
- Explicit requests for human agent

### Agentforce Implementation

**Built-in Mechanism: Escalation Topic**

Agentforce includes a pre-configured **Escalation Topic** that routes to Omni-Channel. Enable it in Setup → Agentforce Agents → [Your Agent] → Topics → Escalation Topic.

**Custom Topic Configuration (for domain-specific escalation):**
```yaml
Topic: Request Account Manager
Classification Description: |
  Customer wants to speak with their dedicated account manager,
  sales representative, or account executive. Includes requests
  like "Connect me with my rep", "I want to talk to sales",
  "Who's my account manager?".

Scope: Requests for personalized human contact in sales context
```

**Actions:**
- **Get Account Manager** — Flow querying Account.Owner or custom Account_Manager__c field
- **Check Manager Availability** — Omni-Channel API checking online status
- **Create Omni-Channel Work Item** — Flow creating AgentWork record with context
- **Send Unavailable Message** — Flow triggering email/SMS if manager offline

**Instructions (Topic-Level):**
```
When a customer requests their account manager, look up the assigned
representative. If the manager is available via Omni-Channel, route the
conversation immediately with context.

If the manager is unavailable, provide their contact information (email, phone)
and offer to schedule a callback. Always set the expectation that a human
will reach out.

Context to pass to human agent: Customer name, Account ID, last purchase date,
open cases count, conversation summary (what the customer needs).
```

### Conversation Example (Explicit Request)

```
User: I've been trying to fix this for 20 minutes. Can I just talk to someone?

Agent: Of course—let me connect you with a specialist who can help right away.

       I'm transferring our conversation now, and they'll have all the details
       we've discussed. You should see them join in just a moment.

       [Escalation triggered → Omni-Channel routing → Human agent receives
        conversation history + context summary]
```

### Conversation Example (Sentiment-Based Auto-Escalation)

```
User: This is ridiculous! The app has been broken for a week and nobody cares!

Agent: I understand this has been incredibly frustrating, and I'm truly sorry
       for the trouble. Let me connect you with a specialist who can prioritize
       your case and make sure this gets resolved today.

       Transferring you now—they'll have all the details.

       [Auto-escalation triggered by frustration detection]
```

### Omni-Channel Integration

**Configuration Steps:**
1. Create Queue (Setup → Queues → New)
2. Add Agent Members to Queue
3. Configure Service Channel (Setup → Service Channels)
4. Create Routing Configuration (Setup → Routing Configurations)
5. Link Escalation Topic to Queue

**Context Passing (AgentWork Record):**
```apex
// Example: Custom Apex Action for escalation with context
AgentWork work = new AgentWork(
    WorkItemId = chatTranscript.Id,
    UserId = assignedAgentId,
    ServiceChannelId = channelId,
    PriorityGroup = 'High',
    CustomContext__c = JSON.serialize(new Map<String, Object>{
        'conversation_summary' => 'Customer unable to upload photos in iOS app',
        'case_number' => '00284731',
        'sentiment' => 'frustrated',
        'turns_count' => 8,
        'topics_attempted' => 'Technical Support, Troubleshooting'
    })
);
insert work;
```

### Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| **No human availability check** | User waits indefinitely, no fallback | Always check Omni-Channel status, offer callback if offline |
| **Apologizing excessively** | Sounds insincere, wastes time | One apology + action: "I'm sorry. Let me connect you now." |
| **Not passing context** | Human agent asks same questions | Send conversation summary, key IDs, sentiment |
| **Vague wait times** | Frustration increases | Give specific estimates: "2-3 minutes" not "shortly" |
| **Trying to solve after user asks for human** | Ignoring user preference, bad UX | Immediate escalation when explicitly requested |

### Topic Boundaries

**Trigger Escalation When:**
- User explicitly requests human ("talk to a person", "speak with agent")
- Sentiment analysis detects frustration/anger
- Conversation exceeds 8-10 turns without resolution
- Issue requires policy exception or judgment call
- Technical complexity beyond AI training

**Don't Escalate When:**
- User is still engaged and making progress
- Issue can be resolved with one more action
- User hasn't indicated frustration
- Human agents are offline AND issue is non-urgent (offer callback instead)

---

## Pattern 4: Step-by-Step (Guided Workflow)

### Description

Multi-turn conversation guiding a user through a linear or branching process. Agent provides instructions, waits for confirmation, adapts to user's progress.

**Best for:**
- Troubleshooting guides
- Setup/configuration assistance
- Onboarding flows
- How-to tutorials

### Agentforce Implementation

**Topic Configuration:**
```yaml
Topic: Password Reset Assistance
Classification Description: |
  Customer is unable to log in, forgot their password, or needs help
  resetting credentials. Includes phrases like "can't log in",
  "forgot password", "reset my password", "locked out".

Scope: Login/authentication issues requiring password reset guidance
```

**Actions:**
- **Check Account Status** — Flow checking User.IsActive, IsPasswordLocked
- **Send Reset Link** — Apex triggering PasswordReset email
- **Verify Identity** — Flow asking security question or MFA code
- **Get Step Instructions** — Knowledge article for each step
- **Confirm Step Complete** — Wait for user confirmation before next step

**Instructions (Topic-Level):**
```
Guide the user through password reset step-by-step. Don't provide all
steps at once—give one step, wait for confirmation, then proceed.

Adapt to the user's technical level. If they say "Done" quickly, they're
confident—move fast. If they ask clarifying questions, slow down and
provide more detail.

If the user gets stuck on a step, offer to escalate to technical support
rather than repeating the same instruction.
```

### Conversation Example

```
User: I forgot my password and can't log in.

Agent: No problem, I can help you reset it. First, I need to verify your
       identity—what's the email address associated with your account?

User: john@example.com

Agent: Thanks! I'm sending a password reset link to john@example.com right now.

       It should arrive within 1-2 minutes. Let me know when you see the email.

User: Got it.

Agent: Great! Click the "Reset Password" button in that email. It will take you
       to a page where you can create a new password.

       Your new password must be at least 8 characters and include one number
       and one special character.

       Let me know when you've created the new password.

User: Done, I set a new password.

Agent: Perfect! Now try logging in with your email (john@example.com) and the
       new password you just created.

       Did the login work?

User: Yes, I'm in!

Agent: Excellent! Your password has been successfully reset. Make sure to save
       it securely. Is there anything else I can help you with?
```

### Branching Logic Example

```
User: The reset link isn't working.

Agent: Let me check what's happening. When you click the link, what do you see?

       A) An error message (please tell me what it says)
       B) A login page (no error)
       C) Nothing happens / page doesn't load

User: It says "This link has expired."

Agent: That means the reset link was open for too long—they expire after
       15 minutes for security.

       I'll send you a fresh link right now. This time, click it as soon as
       you receive the email. Ready?

User: Yes, send it.

Agent: New link sent to john@example.com. Check your inbox and click the link
       within the next 15 minutes.
```

### Agentforce Flow Integration for Steps

**Pattern: Use Flow Variables for State Tracking**

```yaml
Flow: Password Reset Steps
Variables:
  - CurrentStep (Text): "verify_identity", "send_link", "create_password", "test_login"
  - EmailVerified (Boolean)
  - LinkSent (Boolean)
  - PasswordCreated (Boolean)

Decision Element: Next Step Logic
  - If CurrentStep = "verify_identity" AND EmailVerified = True → Set CurrentStep = "send_link"
  - If CurrentStep = "send_link" AND LinkSent = True → Set CurrentStep = "create_password"
  - If CurrentStep = "create_password" AND PasswordCreated = True → Set CurrentStep = "test_login"
```

### Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| **Dumping all steps at once** | Overwhelming, user loses track | One step per turn, wait for confirmation |
| **Not tracking progress** | Repeating completed steps, confusing | Use Flow variables to track current step |
| **Assuming user knows what "Done" means** | Miscommunication, false progress | Be explicit: "Let me know when you've clicked the button" |
| **No error branches** | Dead-end when user hits problem | For every step, anticipate 2-3 common failures |
| **Technical jargon** | User doesn't understand instructions | Use simple language: "click the blue button" not "invoke the CTA element" |

### Topic Boundaries

**In Scope:**
- 5-10 step processes
- 2-3 decision branches per step
- User can complete steps independently

**Out of Scope:**
- Processes requiring screen sharing (escalate to human)
- More than 15 total steps (break into multiple topics or provide link to docs)
- Steps requiring admin/elevated permissions

---

## Pattern 5: Troubleshooting (Diagnosis & Resolution)

### Description

Conversational decision tree identifying the root cause of a problem and providing resolution steps. Agent asks diagnostic questions, narrows down possibilities, and recommends fixes.

**Best for:**
- Technical support
- Error resolution
- Performance issues
- Product malfunctions

### Agentforce Implementation

**Topic Configuration:**
```yaml
Topic: App Troubleshooting
Classification Description: |
  Customer reports the mobile app is not working correctly—crashes,
  errors, slow performance, features not loading, or unexpected behavior.
  Includes phrases like "app won't open", "keeps crashing", "error message",
  "not working", "slow", "frozen".

Scope: Technical issues with the mobile application requiring diagnosis
```

**Actions:**
- **Gather Symptoms** — Flow collecting OS version, app version, error message, reproduction steps
- **Check Service Status** — API call to status.company.com checking outages
- **Query Known Issues** — Knowledge search for error code or symptom pattern
- **Recommend Fix** — Knowledge article for resolution steps
- **Escalate to L2 Support** — Flow creating high-priority case with diagnostics

**Instructions (Topic-Level):**
```
Diagnose the issue through targeted questions before recommending solutions.
Don't guess—ask for specific details:
- What exactly happens? (symptom)
- When did it start? (timeline)
- Does it happen every time or intermittently? (pattern)
- What were you trying to do when it happened? (context)

After gathering symptoms, check for known issues and service outages before
troubleshooting. If a widespread outage exists, inform the customer and
provide status page link.

Recommend solutions from simplest to most complex. After each solution,
ask "Did that fix the issue?" before proceeding.
```

### Conversation Example

```
User: The app keeps crashing on me.

Agent: I'm sorry to hear that. Let me help you figure out what's causing this.

       When does the crash happen—right when you open the app, or while you're
       using a specific feature?

User: When I try to upload a photo.

Agent: Got it. A few questions to narrow this down:

       1. What type of phone are you using? (iPhone, Android, other)
       2. Do you see an error message, or does the app just close?

User: iPhone 14, and it just closes—no error message.

Agent: Thank you. When the app closes, are you able to reopen it right away,
       or does it keep crashing when you try to upload again?

User: It reopens fine, but if I try to upload again, it crashes again.

Agent: That's helpful. This sounds like a memory issue with large photos.
       Let me walk you through a fix:

       **Step 1:** Go to your iPhone Settings → [App Name] → Photos
       **Step 2:** Change the setting from "All Photos" to "Selected Photos"
       **Step 3:** Reopen the app and try uploading again

       This limits the app's photo library access, which often resolves crash
       issues. Let me know if that works.

User: That fixed it! It's working now.

Agent: Excellent! The crash was happening because the app was trying to load
       thumbnails for your entire photo library. Limiting access reduces memory
       usage.

       If you need to upload photos that aren't in your "Selected" list, just
       add them in Settings first. Anything else I can help with?
```

### Decision Tree Example (Pseudo-Flow Logic)

```
START: App Crashing
  ├─ Q: When does it crash?
  │    ├─ On launch
  │    │    ├─ Q: Recently updated?
  │    │    │    ├─ Yes → Solution: Reinstall app
  │    │    │    └─ No → Solution: Clear cache
  │    │    └─ Next: Test solution
  │    ├─ During photo upload
  │    │    ├─ Q: Phone type?
  │    │    │    ├─ iPhone → Solution: Limit photo access
  │    │    │    └─ Android → Solution: Check storage space
  │    │    └─ Next: Test solution
  │    └─ During specific feature
  │         ├─ Check: Service outage for that feature?
  │         │    ├─ Yes → Inform: Outage, ETA to fix
  │         │    └─ No → Q: Reproduce steps?
  │         └─ Escalate: Create case with steps
```

### Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| **Jumping to solutions** | Wrong fix, wasted time | Ask 3-5 diagnostic questions first |
| **Yes/no questions only** | Limited information | Mix with open-ended: "What do you see when...?" |
| **Not checking service status** | Troubleshooting during outage | Always check status page first |
| **Giving 5 solutions at once** | Overwhelming, can't track what worked | One solution per turn, wait for result |
| **No escalation path** | User stuck in loop | After 3 failed solutions, escalate to human |

### Einstein Trust Layer Considerations

When troubleshooting involves sensitive data (account numbers, payment info), guide the user WITHOUT asking them to share it:

```
❌ Bad: "What's your credit card number so I can check your account?"

✅ Good: "I'll need you to verify your payment method. Can you log into
         your account, go to Settings → Billing, and tell me the last
         4 digits of the card on file?"
```

The Einstein Trust Layer masks PII automatically, but design conversations to avoid soliciting sensitive data in the first place.

---

## Pattern Selection Guide

Use this decision tree to choose the right pattern:

```
START: What does the user want to accomplish?
  │
  ├─ Get factual information
  │    └─ Q&A Pattern
  │
  ├─ Create/update a record
  │    ├─ Single record, 3-8 fields → Information Gathering
  │    └─ Complex, multi-record → Step-by-Step or Handoff
  │
  ├─ Solve a problem
  │    ├─ Known solution (how-to) → Step-by-Step
  │    ├─ Unknown cause (diagnosis needed) → Troubleshooting
  │    └─ Requires human judgment → Handoff
  │
  └─ Talk to a human
       └─ Handoff Pattern
```

---

## Combining Patterns

Real conversations often blend patterns. For example:

**Troubleshooting → Information Gathering → Handoff**
```
1. User reports issue (Troubleshooting)
2. Agent diagnoses problem, but fix requires case creation (Information Gathering)
3. Case created, but issue is complex → escalate to L2 (Handoff)
```

**Q&A → Step-by-Step**
```
1. User asks "How do I reset my password?" (Q&A)
2. Agent provides link, but user says "I can't find it" (Step-by-Step)
3. Agent walks through each step to guide user to reset page
```

When blending patterns, use **topic transitions**:

```
Agent: I found the answer to your question [Q&A Pattern]. Would you like me
       to walk you through the steps to set this up? [Transition to Step-by-Step]
```

---

## Summary: Pattern Comparison

| Pattern | Turns | Complexity | Actions | Best For |
|---------|-------|------------|---------|----------|
| **Q&A** | 1-2 | Low | Knowledge retrieval, data lookup | FAQs, simple queries |
| **Information Gathering** | 3-6 | Medium | Flow with inputs, record creation | Case creation, lead capture |
| **Handoff** | 1-3 | Medium | Omni-Channel routing, context passing | Escalations, human requests |
| **Step-by-Step** | 4-10 | High | Sequential instructions, state tracking | Tutorials, configuration |
| **Troubleshooting** | 4-12 | High | Diagnostic flows, decision trees | Technical support, error resolution |

Choose simplicity first—if Q&A solves the need, don't over-engineer with Step-by-Step.
