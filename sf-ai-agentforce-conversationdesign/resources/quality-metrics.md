# Quality Metrics for Agentforce Conversation Design

This guide defines key performance indicators (KPIs), benchmarks, and improvement strategies for evaluating Agentforce agent quality. Use these metrics to measure success and identify areas for optimization.

---

## Core Metrics Framework

Agentforce quality should be measured across four dimensions:

1. **Resolution** — Did the agent solve the customer's problem?
2. **Accuracy** — Did the agent route correctly and provide correct information?
3. **Efficiency** — Did the agent resolve the issue quickly?
4. **Satisfaction** — Is the customer happy with the experience?

---

## Metric 1: Resolution Rate

**Definition:** Percentage of conversations resolved without escalation to a human agent.

**Formula:**
```
Resolution Rate = (Conversations Resolved by AI / Total Conversations) × 100
```

**Target Benchmark:** >70%

**Grade Scale:**
- **Excellent:** >80%
- **Good:** 70-80%
- **Fair:** 60-70%
- **Poor:** <60%

### How to Measure

**Method 1: Escalation Tracking (Proxy)**
```
Resolution Rate ≈ 100% - Escalation Rate
```

If 25% of conversations escalate, resolution rate ≈ 75%.

**Method 2: Post-Conversation Survey**
```
Survey Question: "Was your issue resolved?"
  - Yes (resolved)
  - Partially (some help, but not fully resolved)
  - No (not resolved)

Resolution Rate = % who answered "Yes"
```

**Method 3: AgentWork Analysis**
```
Query AgentWork records:
  - Total conversations: COUNT(*)
  - Escalations: COUNT(*) WHERE WorkItemType = 'Escalation'
  - Resolution Rate = 100% - (Escalations / Total)
```

### Interpretation

| Resolution Rate | What It Means | Action |
|-----------------|---------------|--------|
| **>85%** | AI is highly effective | Maintain current design, look for edge case improvements |
| **70-85%** | AI is performing well | Identify top escalation reasons and address |
| **60-70%** | AI is struggling | Major redesign needed—check topic scope, instructions, actions |
| **<60%** | AI is not adding value | Consider if the use case is suitable for AI |

### Improvement Strategies

**If Resolution Rate is Low:**

1. **Analyze Escalation Reasons:**
   ```
   Top Escalation Reasons:
     - 35%: Complexity (multi-issue conversations)
     - 25%: Customer request for human
     - 20%: Repeated failures (same action fails 2+ times)
     - 10%: Frustration
     - 10%: Policy exceptions
   ```

   **Action:** Focus on the top 1-2 reasons. If "Complexity" is #1, add actions or split topics.

2. **Add Missing Actions:**
   - If customers escalate because "I can't find X", add a Search Knowledge action for X
   - If customers escalate for "Change Y", add an Update Y action

3. **Improve Instructions:**
   - Review conversations where agent gave incorrect info → update instructions
   - Review conversations where agent asked redundant questions → improve context handling

4. **Expand Topic Coverage:**
   - If 20% of escalations are "Out of Scope", consider adding a topic for that domain

---

## Metric 2: Topic Classification Accuracy

**Definition:** Percentage of conversations correctly routed to the right topic on first intent.

**Formula:**
```
Classification Accuracy = (Correct Topic Matches / Total Conversations) × 100
```

**Target Benchmark:** >90%

**Grade Scale:**
- **Excellent:** >95%
- **Good:** 90-95%
- **Fair:** 85-90%
- **Poor:** <85%

### How to Measure

**Method 1: Manual Review (Gold Standard)**

Sample 100 conversations. For each, answer:
- Did the agent route to the correct topic on the first message?
- If topic switched mid-conversation, was it appropriate?

```
Example:
  User: "I want to return my order"
  Agent: [Routes to "Returns & Refunds" topic] ✅ Correct

  User: "I forgot my password"
  Agent: [Routes to "Product Help" topic] ❌ Incorrect (should be "Account Settings")
```

**Method 2: Topic Switch Rate (Proxy)**

If the agent frequently switches topics mid-conversation, it suggests initial classification was wrong.

```
Topic Switch Rate = (Conversations with Topic Switch / Total) × 100

Target: <10% (most conversations should stay in one topic)
```

**Method 3: Fallback Topic Rate**

If >15% of conversations land in the Fallback/Out-of-Scope topic, classification is failing.

```
Fallback Rate = (Fallback Topic Conversations / Total) × 100

Target: <15%
```

### Interpretation

| Classification Accuracy | What It Means | Action |
|-------------------------|---------------|--------|
| **>95%** | Topic descriptions are clear and well-differentiated | Maintain current design |
| **90-95%** | Generally good, minor ambiguities | Review top misclassification pairs |
| **85-90%** | Significant ambiguity | Rewrite overlapping topic descriptions |
| **<85%** | Topics are poorly defined | Major topic architecture redesign |

### Improvement Strategies

**If Classification Accuracy is Low:**

1. **Identify Ambiguous Topic Pairs:**
   ```
   Misclassification Analysis:
     - 40% of "Technical Support" conversations misclassified as "Product Help"
     - 30% of "Account Settings" misclassified as "Order Management"
   ```

   **Action:** Disambiguate the overlapping topics:
   ```yaml
   # Before (Ambiguous)
   Topic A: Technical Support
   Description: Customer has problems with the product or needs help.

   Topic B: Product Help
   Description: Customer needs help with the product or has questions.

   # After (Clear)
   Topic A: Technical Support
   Description: Customer reports an error, crash, bug, or unexpected behavior—
                something that should work but doesn't. Keywords: "error",
                "crash", "broken", "not working", "stopped working".

   Topic B: Product Help
   Description: Customer asks how to use a feature, configure settings, or
                accomplish a task. Keywords: "how do I", "where is", "show me".
   ```

2. **Add Keyword Indicators:**
   - Include explicit keywords in classification descriptions
   - Example: "Includes phrases like 'I want to return', 'start a return', 'return policy'"

3. **Test with Real User Queries:**
   - Use historical conversation data to test topic classification
   - For each query, predict which topic should match, then validate

4. **Split Overly Broad Topics:**
   - If one topic handles 50%+ of conversations, it's too broad
   - Example: Split "Customer Service" into "Order Support", "Returns", "Account Settings"

---

## Metric 3: Average Turns to Resolution

**Definition:** Average number of back-and-forth messages (turns) from start to resolution.

**Formula:**
```
Avg Turns to Resolution = Total Message Count / Total Resolved Conversations
```

**Target Benchmark:** <6 turns

**Grade Scale:**
- **Excellent:** <4 turns (efficient, concise)
- **Good:** 4-6 turns (acceptable for most use cases)
- **Fair:** 6-8 turns (slow, needs optimization)
- **Poor:** >8 turns (inefficient, frustrating)

### How to Measure

**Method 1: Conversation Message Count**

Query conversation records:
```sql
SELECT AVG(MessageCount)
FROM Conversation
WHERE Status = 'Resolved'
AND EscalatedToHuman__c = FALSE
```

**Method 2: By Topic**

Compare turn counts across topics to identify inefficiencies:
```
Topic                  | Avg Turns | Status
-------------------------------------------------
Order Status           | 2.3       | ✅ Excellent
Returns & Refunds      | 5.1       | ✅ Good
Technical Support      | 8.7       | ❌ Poor (needs optimization)
Account Settings       | 4.2       | ✅ Good
```

### Interpretation

| Avg Turns | What It Means | Action |
|-----------|---------------|--------|
| **<4** | Highly efficient (likely simple Q&A) | Maintain efficiency |
| **4-6** | Normal for multi-step workflows | Acceptable, monitor for increases |
| **6-8** | Agent is slow or inefficient | Optimize instructions, reduce redundant questions |
| **>8** | Major inefficiency, customer frustration | Immediate redesign needed |

### Improvement Strategies

**If Turn Count is High:**

1. **Reduce Redundant Questions:**
   ```yaml
   # Before (Redundant)
   Agent: What's your order number?
   User: 12345678
   Agent: Thanks. And what's your email?
   User: john@example.com
   Agent: And your phone number?

   # After (Batch Questions)
   Agent: To look up your order, I'll need your order number and the email
          address you used for the purchase. What are those?
   User: Order 12345678, email john@example.com
   Agent: Got it! Let me pull that up...
   ```

2. **Use Smarter Actions:**
   - Instead of asking for email separately, look up order by order number and auto-retrieve email
   - Use Flow Get Records to pre-fetch data

3. **Eliminate Unnecessary Confirmations:**
   ```yaml
   # Before (Excessive Confirmation)
   Agent: I'll check your order status now. Is that okay?
   User: Yes.
   Agent: [Retrieves order]

   # After (Just Act)
   Agent: Let me check your order status...
   Agent: [Retrieves order immediately]
   ```

4. **Parallelize Data Collection:**
   ```yaml
   # Before (Sequential)
   Turn 1: Agent asks for order number
   Turn 2: User provides
   Turn 3: Agent asks for reason for return
   Turn 4: User provides
   Turn 5: Agent asks for preferred refund method
   Turn 6: User provides

   # After (Combined)
   Turn 1: Agent asks for order number and reason in one question
   Turn 2: User provides both
   Turn 3: Agent asks for refund method
   Turn 4: User provides
   ```

---

## Metric 4: Customer Satisfaction (CSAT)

**Definition:** Percentage of customers who rate their experience positively.

**Formula:**
```
CSAT = (Positive Ratings / Total Ratings) × 100
```

**Target Benchmark:** >80% (4+ out of 5 stars)

**Grade Scale:**
- **Excellent:** >90%
- **Good:** 80-90%
- **Fair:** 70-80%
- **Poor:** <70%

### How to Measure

**Method 1: Post-Conversation Survey**

After conversation ends, trigger a survey:
```
Survey Question: "How satisfied were you with this conversation?"
  ⭐ ⭐ ⭐ ⭐ ⭐ (5 stars)

Positive = 4-5 stars
Neutral = 3 stars
Negative = 1-2 stars

CSAT = (4-5 star ratings / Total ratings) × 100
```

**Method 2: Thumbs Up/Down**

Simpler binary feedback:
```
Survey Question: "Was this conversation helpful?"
  👍 Helpful  |  👎 Not Helpful

CSAT = (Thumbs Up / Total) × 100
```

**Method 3: Net Promoter Score (NPS)**

For deeper loyalty measurement:
```
Survey Question: "How likely are you to recommend our support to a friend?"
  0 (Not Likely) ... 10 (Very Likely)

Promoters (9-10): Highly satisfied
Passives (7-8): Neutral
Detractors (0-6): Dissatisfied

NPS = % Promoters - % Detractors
```

### Interpretation

| CSAT Score | What It Means | Action |
|------------|---------------|--------|
| **>90%** | Customers are very happy | Maintain quality, scale to more use cases |
| **80-90%** | Generally satisfied | Identify and fix pain points |
| **70-80%** | Mixed feedback | Major improvements needed |
| **<70%** | Customers are unhappy | Urgent redesign or consider removing AI |

### Improvement Strategies

**If CSAT is Low:**

1. **Analyze Low-Rating Conversations:**
   - Review 1-2 star ratings to find patterns
   - Common themes: "Agent didn't understand me", "Too slow", "Didn't solve my problem"

2. **Improve Empathy and Tone:**
   ```yaml
   # Before (Robotic)
   Agent: Your request has been processed. Reference number: 12345.

   # After (Empathetic)
   Agent: All set! I've processed your request and you should receive confirmation
          shortly. Your reference number is 12345 if you need to follow up.
          Is there anything else I can help with?
   ```

3. **Set Expectations:**
   - If an action takes time, tell the customer: "This will take about 10 seconds..."
   - If escalating, say: "You'll be connected in 2-3 minutes"

4. **Follow Up After Resolution:**
   - End every conversation with: "Did that solve your issue? Is there anything else?"
   - This ensures the customer feels heard

---

## Metric 5: Escalation Rate

**Definition:** Percentage of conversations that escalate to a human agent.

**Formula:**
```
Escalation Rate = (Escalations / Total Conversations) × 100
```

**Target Benchmark:** 15-30%

**Grade Scale:**
- **Excellent:** 10-20% (AI handling most, escalating when needed)
- **Good:** 20-30% (healthy balance)
- **Fair:** 30-40% (over-escalating, AI not confident)
- **Poor:** >40% (AI not adding value)

**Note:** <10% is also concerning — may indicate under-escalation (customers frustrated but not escalating).

### How to Measure

```sql
SELECT COUNT(*) AS Total,
       SUM(CASE WHEN Escalated__c = TRUE THEN 1 ELSE 0 END) AS Escalations,
       (SUM(CASE WHEN Escalated__c = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS EscalationRate
FROM Conversation
```

**Breakdown by Reason:**
```sql
SELECT EscalationReason__c, COUNT(*) AS Count
FROM Conversation
WHERE Escalated__c = TRUE
GROUP BY EscalationReason__c
ORDER BY Count DESC
```

### Interpretation

| Escalation Rate | What It Means | Action |
|-----------------|---------------|--------|
| **<10%** | Under-escalating (customers giving up?) | Review CSAT—are customers frustrated? |
| **10-30%** | Healthy (AI handles most, escalates when needed) | Maintain and optimize |
| **30-50%** | Over-escalating (AI not confident) | Improve topic classification, add actions |
| **>50%** | AI is barely helping | Major redesign or consider removing AI |

### Improvement Strategies

**If Escalation Rate is High:**

1. **Analyze Top Escalation Reasons:**
   ```
   Top Reasons:
     - 40%: Complexity (multi-issue conversations)
     - 30%: Customer request for human
     - 20%: Repeated failures
     - 10%: Out of scope
   ```

   **Action:** Address the top reason first.

2. **Reduce "Complexity" Escalations:**
   - Add more actions (e.g., if customers escalate for "Can't modify order", add a Modify Order action)
   - Improve multi-turn workflows (reduce turn count)

3. **Reduce "Customer Request" Escalations:**
   - Some customers prefer humans — this is acceptable (target: <10%)
   - If >15%, customers may not trust AI — improve transparency and empathy

4. **Reduce "Repeated Failures" Escalations:**
   - If actions fail frequently (API errors, timeouts), fix underlying systems
   - If solutions don't work, improve troubleshooting logic

---

## Metric 6: Containment Rate

**Definition:** Percentage of conversations that stay within the AI agent (inverse of escalation rate).

**Formula:**
```
Containment Rate = 100% - Escalation Rate
```

**Target Benchmark:** >70%

**Grade Scale:**
- **Excellent:** >80%
- **Good:** 70-80%
- **Fair:** 60-70%
- **Poor:** <60%

**Note:** Containment Rate and Resolution Rate are related but not identical:
- **Containment Rate:** Did the conversation stay in AI? (No escalation)
- **Resolution Rate:** Did the AI resolve the issue? (Successful outcome)

Example:
- Conversation stays in AI but doesn't resolve issue → High containment, low resolution (bad)
- Conversation escalates after AI partially helps → Low containment, medium resolution (acceptable)

---

## Metric 7: First Contact Resolution (FCR)

**Definition:** Percentage of issues resolved in the first conversation session (no follow-up needed).

**Formula:**
```
FCR = (Single-Session Resolutions / Total Resolved) × 100
```

**Target Benchmark:** >60%

**Grade Scale:**
- **Excellent:** >75%
- **Good:** 60-75%
- **Fair:** 50-60%
- **Poor:** <50%

### How to Measure

**Method 1: Track Repeat Conversations**

If a customer returns within 24 hours with the same issue, FCR failed.

```sql
SELECT ContactId, COUNT(*) AS ConversationCount
FROM Conversation
WHERE CreatedDate >= LAST_N_DAYS:7
GROUP BY ContactId
HAVING COUNT(*) > 1
```

**Method 2: Post-Conversation Survey**

```
Survey Question: "Did we fully resolve your issue today?"
  - Yes, completely resolved
  - Partially resolved
  - Not resolved

FCR = % who answered "Yes"
```

### Improvement Strategies

**If FCR is Low:**

1. **Check for Incomplete Resolutions:**
   - Review conversations where customers return within 24 hours
   - Common issue: Agent said "issue resolved" but customer didn't confirm

2. **Improve Confirmation:**
   ```yaml
   # Before (No Confirmation)
   Agent: I've reset your password. The reset link has been sent.

   # After (Confirmation)
   Agent: I've sent the reset link to your email. Let me know when you've
          received it and successfully reset your password so I can confirm
          everything is working.
   ```

3. **Offer Follow-Up:**
   ```
   Agent: Your order has been canceled and you'll receive a refund in 5-7 days.
          If you don't see the refund by [date], reach out and I'll escalate it.
          Does that work for you?
   ```

---

## Metric 8: Error Recovery Rate

**Definition:** Percentage of errors (misunderstandings, failed actions, wrong topic routing) that are gracefully recovered without escalation.

**Formula:**
```
Error Recovery Rate = (Errors Recovered / Total Errors) × 100
```

**Target Benchmark:** >70%

**Grade Scale:**
- **Excellent:** >85%
- **Good:** 70-85%
- **Fair:** 60-70%
- **Poor:** <60%

### How to Measure

**Method 1: Manual Review**

Sample 100 conversations with errors:
- Misclassification (wrong topic)
- Failed action (API error, timeout)
- Misunderstanding (agent gives wrong answer)

For each error, did the agent recover?
```
Example 1 (Recovered):
  Agent: [Routes to wrong topic]
  User: "No, I need help with X"
  Agent: "Got it, let me switch to [correct topic]"
  [Conversation continues successfully]

Example 2 (Not Recovered):
  Agent: [Routes to wrong topic]
  User: "No, I need help with X"
  Agent: [Still in wrong topic, doesn't switch]
  User: "Forget it, get me a human"
```

**Method 2: Track Topic Switches**

If the agent switches topics mid-conversation, it suggests initial classification was wrong. Did it recover?

```
Topic Switch + Resolution = Error Recovered ✅
Topic Switch + Escalation = Error Not Recovered ❌
```

### Improvement Strategies

**If Error Recovery Rate is Low:**

1. **Improve Fallback Responses:**
   ```yaml
   Fallback Topic Instructions:
   If you don't understand the customer's request, offer choices:
   "I'm not sure I understood that. Are you looking for help with:
    • Order status
    • Returns
    • Technical support
    Which is closest to what you need?"
   ```

2. **Add Error Handling to Actions:**
   ```yaml
   Action: Get Order Status
   Action-Level Instructions:
   If this action fails (order not found, API error), apologize and offer
   alternatives:
   "I'm having trouble looking up that order. Let's try this:
    • Double-check the order number (it's 8 digits)
    • Or, I can look it up by your email address instead
    Which would you prefer?"
   ```

3. **Train on Edge Cases:**
   - Add conversation examples (training data) for common errors
   - Example: "User says 'no' after agent proposes solution → agent asks clarifying question"

---

## Metric 9: Conversation Duration

**Definition:** Average time (in seconds) from first message to resolution or escalation.

**Formula:**
```
Avg Duration = SUM(ConversationDuration) / Total Conversations
```

**Target Benchmark:** <5 minutes (300 seconds)

**Grade Scale:**
- **Excellent:** <3 minutes
- **Good:** 3-5 minutes
- **Fair:** 5-7 minutes
- **Poor:** >7 minutes

### Interpretation

| Duration | What It Means | Action |
|----------|---------------|--------|
| **<3 min** | Efficient (likely Q&A or simple workflows) | Maintain efficiency |
| **3-5 min** | Normal for multi-turn workflows | Acceptable |
| **5-7 min** | Slow, customer may be frustrated | Optimize for speed |
| **>7 min** | Too slow, high abandonment risk | Immediate optimization |

**Note:** Duration is affected by:
- User response time (not in agent's control)
- Action execution time (API latency, Flow complexity)
- Agent turn count (more turns = longer duration)

### Improvement Strategies

**If Duration is High:**

1. **Optimize Action Performance:**
   - Review Flow execution times (Setup → Flow → Execution History)
   - Optimize SOQL queries (add indexes, reduce record counts)
   - Cache frequently-accessed data (Knowledge articles, picklist values)

2. **Reduce Turn Count:** See Metric 3 (Avg Turns to Resolution)

3. **Set Expectations for Slow Actions:**
   ```
   Agent: Let me run a credit check—this will take about 15 seconds...
   ```

---

## Metric 10: Abandonment Rate

**Definition:** Percentage of conversations where the customer stops responding before resolution.

**Formula:**
```
Abandonment Rate = (Abandoned Conversations / Total Conversations) × 100
```

**Target Benchmark:** <20%

**Grade Scale:**
- **Excellent:** <10%
- **Good:** 10-20%
- **Fair:** 20-30%
- **Poor:** >30%

### How to Measure

**Definition of Abandonment:**
- Agent sends a message, customer doesn't respond within 5 minutes
- Conversation ends without resolution or escalation

```sql
SELECT COUNT(*) AS Abandoned
FROM Conversation
WHERE Status = 'Abandoned'
AND LastMessageSender = 'Agent'
AND TimeSinceLastMessage > 5 minutes
```

### Interpretation

| Abandonment Rate | What It Means | Action |
|------------------|---------------|--------|
| **<10%** | Customers are engaged | Maintain quality |
| **10-20%** | Acceptable (some drop-off is normal) | Monitor for increases |
| **20-30%** | High abandonment, customers giving up | Immediate investigation |
| **>30%** | Major UX problem | Urgent redesign |

### Improvement Strategies

**If Abandonment Rate is High:**

1. **Analyze When Abandonment Happens:**
   ```
   Turn Abandonment Rate:
     - Turn 1: 5% (normal, user may have changed mind)
     - Turn 3: 10%
     - Turn 5: 25% ← Peak abandonment (investigate)
     - Turn 7: 15%
   ```

   **Action:** Review what happens at Turn 5. Is the agent asking a confusing question? Is an action failing?

2. **Reduce Friction:**
   - If customers abandon after "What's your order number?", they may not have it handy
   - Offer alternative: "If you don't have your order number, I can look it up by email address"

3. **Improve Engagement:**
   ```yaml
   # Before (Dry)
   Agent: What's your order number?

   # After (Engaging)
   Agent: I can check your order status! What's your order number? (It's usually
          in your confirmation email.)
   ```

---

## Summary: Metrics Dashboard

Track these 10 metrics in a Salesforce Dashboard:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Resolution Rate** | >70% | 78% | ✅ Good |
| **Classification Accuracy** | >90% | 92% | ✅ Good |
| **Avg Turns to Resolution** | <6 | 5.2 | ✅ Good |
| **Customer Satisfaction (CSAT)** | >80% | 85% | ✅ Good |
| **Escalation Rate** | 15-30% | 22% | ✅ Good |
| **Containment Rate** | >70% | 78% | ✅ Good |
| **First Contact Resolution (FCR)** | >60% | 68% | ✅ Good |
| **Error Recovery Rate** | >70% | 74% | ✅ Good |
| **Avg Duration** | <5 min | 4.2 min | ✅ Good |
| **Abandonment Rate** | <20% | 12% | ✅ Good |

**Overall Agent Health:** 🟢 Healthy

---

## Continuous Improvement Process

### Step 1: Monitor Weekly
- Review top 3 metrics: Resolution Rate, CSAT, Escalation Rate
- Flag any metric that drops >5% week-over-week

### Step 2: Investigate Monthly
- Deep-dive into failing conversations (low CSAT, high turns, abandonment)
- Identify patterns (specific topics, specific actions, specific times of day)

### Step 3: Optimize Quarterly
- Implement fixes for top 3 pain points
- A/B test instruction changes (old vs. new instructions)
- Measure impact of changes

### Step 4: Benchmark Annually
- Compare year-over-year metrics
- Adjust targets based on industry benchmarks and business goals
- Celebrate wins and share learnings across teams

---

## Final Checklist: Is My Agent High-Quality?

- [ ] Resolution Rate >70%
- [ ] Classification Accuracy >90%
- [ ] CSAT >80%
- [ ] Escalation Rate 15-30%
- [ ] FCR >60%
- [ ] Error Recovery Rate >70%
- [ ] Avg Duration <5 min
- [ ] Abandonment Rate <20%

If you check 7+ boxes, your agent is high-quality. If <5, focus on improvement areas.
