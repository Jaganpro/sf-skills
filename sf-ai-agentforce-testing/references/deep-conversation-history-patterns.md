<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # Deep Conversation History Patterns
   2 
   3 Testing specific protocol stages in CLI tests using 4-8 turn `conversationHistory`.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 CLI tests are often described as "single-utterance" — but this is only half the story. By providing deep `conversationHistory` (4-8 turns of prior conversation), you can position the agent at a specific point in a multi-step protocol and test its behavior at that exact stage.
  10 
  11 This transforms CLI tests from simple "utterance → topic" checks into precise protocol-stage validators:
  12 
  13 | Without History | With Deep History |
  14 |----------------|-------------------|
  15 | Tests routing only (utterance → topic) | Tests behavior at any protocol stage |
  16 | Stochastic routing for ambiguous inputs | Deterministic routing anchored by history |
  17 | Cannot test mid-protocol actions | Can trigger specific actions at specific steps |
  18 | Cannot test opt-out or exit paths | Can validate graceful opt-out handling |
  19 | Cannot test session persistence | Can verify session stays alive after protocol |
  20 
  21 ---
  22 
  23 ## Why Deep History Eliminates Stochastic Routing
  24 
  25 When a user sends an ambiguous utterance like "Thanks for the help" to an agent with multiple topics, the planner must decide between several valid destinations. Without history, this decision is non-deterministic — the same utterance may route to different topics on repeated runs.
  26 
  27 **The `topic` field anchors routing.** In `conversationHistory`, agent turns include a `topic` field that tells the planner which topic was active. When the planner sees a history of turns within a specific topic, it biases routing toward that topic's continuation or natural follow-ups.
  28 
  29 ```yaml
  30 # ❌ STOCHASTIC — "Thanks for the help" could route anywhere
  31 - utterance: "Thanks for the help"
  32   expectedTopic: feedback_collection
  33 
  34 # ✅ DETERMINISTIC — history anchors to account_support → feedback naturally follows
  35 - utterance: "Thanks for the help"
  36   expectedTopic: feedback_collection
  37   conversationHistory:
  38     - role: user
  39       message: "I need help with my account"
  40     - role: agent
  41       topic: account_support
  42       message: "I'd be happy to help! I found your account. What do you need?"
  43     - role: user
  44       message: "Can you check my recent activity?"
  45     - role: agent
  46       topic: account_support
  47       message: "Here's your recent activity. Your last transaction was on Feb 10."
  48 ```
  49 
  50 **Key detail:** The `topic` field in `conversationHistory` resolves **local developer names** (e.g., `account_support`, `feedback_collection`). You do NOT need the hash-suffixed runtime `developerName` in history — only in `expectedTopic` for promoted topics.
  51 
  52 ---
  53 
  54 ## Pattern A: Protocol Activation
  55 
  56 **Goal:** Trigger a secondary protocol (e.g., feedback collection, survey, follow-up) after a completed business interaction.
  57 
  58 **History depth:** 4 turns (2 user + 2 agent)
  59 
  60 **Why it works:** The history establishes that a business interaction just completed, creating the natural entry point for a follow-up protocol.
  61 
  62 ```yaml
  63 testCases:
  64   # After a completed business interaction, trigger feedback collection
  65   - utterance: "Thanks for the help"
  66     expectedTopic: [feedback_topic]
  67     expectedActions:
  68       - [feedback_action]
  69     conversationHistory:
  70       - role: user
  71         message: "I need to check my account status"
  72       - role: agent
  73         topic: [business_topic]
  74         message: "I found your account. Everything looks good — your balance is current."
  75       - role: user
  76         message: "Great, that answers my question"
  77       - role: agent
  78         topic: [business_topic]
  79         message: "Glad I could help! Is there anything else you need?"
  80 ```
  81 
  82 **Without this history**, "Thanks for the help" would stochastically route to greeting, escalation, or off-topic — depending on the planner's confidence scores.
  83 
  84 ---
  85 
  86 ## Pattern B: Mid-Protocol Stage
  87 
  88 **Goal:** Test agent behavior at step N of a multi-step protocol (e.g., after collecting a rating but before collecting detailed feedback).
  89 
  90 **History depth:** 4-6 turns
  91 
  92 **Why it works:** The history positions the agent mid-protocol, so the test utterance exercises the specific step you want to validate.
  93 
  94 ```yaml
  95 testCases:
  96   # Agent has already asked for a rating — now test the follow-up question
  97   - utterance: "I'd give it a 4 out of 5"
  98     expectedTopic: [feedback_topic]
  99     expectedActions:
 100       - [store_feedback_action]
 101     expectedOutcome: "Agent acknowledges the rating and asks a follow-up question about what could be improved"
 102     conversationHistory:
 103       - role: user
 104         message: "I need help checking my order"
 105       - role: agent
 106         topic: [order_topic]
 107         message: "Your order #12345 is scheduled for delivery tomorrow."
 108       - role: user
 109         message: "Thanks, that's helpful"
 110       - role: agent
 111         topic: [feedback_topic]
 112         message: "Glad I could help! On a scale of 1-5, how would you rate your experience today?"
 113 ```
 114 
 115 ---
 116 
 117 ## Pattern C: Action Invocation via Deep History
 118 
 119 **Goal:** Position the agent at the exact point where it needs to fire a specific action on the next utterance.
 120 
 121 **History depth:** 6 turns
 122 
 123 **Why it works:** The history completes all prerequisite steps (authentication, data collection) so the test utterance triggers the action directly.
 124 
 125 ```yaml
 126 testCases:
 127   # Agent has verified identity and collected payment info — now trigger payment action
 128   - utterance: "Yes, please process the payment"
 129     expectedTopic: [payment_topic]
 130     expectedActions:
 131       - [process_payment_action]
 132     expectedOutcome: "Agent confirms the payment is being processed"
 133     conversationHistory:
 134       - role: user
 135         message: "I'd like to make a payment"
 136       - role: agent
 137         topic: [auth_topic]
 138         message: "I can help with that. For security, can you verify your name on the account?"
 139       - role: user
 140         message: "John Smith"
 141       - role: agent
 142         topic: [payment_topic]
 143         message: "Thanks, John. I found your account. Your current balance is $150. Would you like to pay the full amount?"
 144       - role: user
 145         message: "Yes, full amount"
 146       - role: agent
 147         topic: [payment_topic]
 148         message: "I'll process a payment of $150. Should I proceed?"
 149 ```
 150 
 151 > **Note:** Actions fire during CLI test execution for the final utterance — but the *history turns* are simulated (no real actions execute during those turns). Only the test utterance triggers real action execution.
 152 
 153 ---
 154 
 155 ## Pattern D: Opt-Out / Negative Assertion
 156 
 157 **Goal:** Verify the agent handles opt-out gracefully — no action should fire, and the agent should acknowledge the user's choice.
 158 
 159 **History depth:** 4-6 turns
 160 
 161 **Key technique:** Use `expectedActions: []` as a **deliberate negative assertion** — this documents the intent that NO action should fire. Combine with `expectedOutcome` to verify the agent's graceful response.
 162 
 163 ```yaml
 164 testCases:
 165   # User declines feedback — agent should NOT invoke feedback action
 166   - utterance: "No thanks, I'm all set"
 167     expectedTopic: [feedback_topic]
 168     expectedActions: []    # ← DELIBERATE: documents intent that NO action fires
 169     expectedOutcome: "Agent gracefully accepts the opt-out without pushing for feedback"
 170     conversationHistory:
 171       - role: user
 172         message: "I need to check my account"
 173       - role: agent
 174         topic: [account_topic]
 175         message: "Your account looks good. Balance is current."
 176       - role: user
 177         message: "Great, thanks"
 178       - role: agent
 179         topic: [feedback_topic]
 180         message: "Glad I could help! Would you like to share feedback about your experience?"
 181 ```
 182 
 183 ### `expectedActions: []` vs Omitted
 184 
 185 | Pattern | Meaning | Behavior |
 186 |---------|---------|----------|
 187 | `expectedActions:` omitted | "Not testing actions" | PASS regardless of what fires |
 188 | `expectedActions: []` | "Testing that NO actions fire" | Currently same behavior (PASS regardless), but documents intent |
 189 
 190 > **Best practice:** Use `expectedActions: []` explicitly for opt-out tests to document your intent, even though the CLI currently treats it the same as omitted. This makes the test self-documenting and future-proofs against framework changes.
 191 
 192 ---
 193 
 194 ## Pattern E: Session Persistence
 195 
 196 **Goal:** After completing a full protocol (including all steps), verify the session is still alive by starting a new business interaction.
 197 
 198 **History depth:** 8 turns (full protocol + new question)
 199 
 200 **Why it works:** If the agent's session terminated during the protocol, the new utterance would fail or produce a generic greeting. A successful business-topic response proves the session survived.
 201 
 202 ```yaml
 203 testCases:
 204   # After completing full feedback flow, start new business request
 205   - utterance: "Actually, can you also check on my recent order?"
 206     expectedTopic: [order_topic]
 207     expectedActions:
 208       - [order_lookup_action]
 209     expectedOutcome: "Agent acknowledges the new request and begins order lookup"
 210     conversationHistory:
 211       - role: user
 212         message: "I need help with my account"
 213       - role: agent
 214         topic: [account_topic]
 215         message: "I found your account. Everything looks good."
 216       - role: user
 217         message: "Thanks!"
 218       - role: agent
 219         topic: [feedback_topic]
 220         message: "Glad to help! Would you rate your experience 1-5?"
 221       - role: user
 222         message: "4 out of 5"
 223       - role: agent
 224         topic: [feedback_topic]
 225         message: "Thanks for the feedback! Is there anything else I can help with?"
 226       - role: user
 227         message: "No, that's all for feedback"
 228       - role: agent
 229         topic: [feedback_topic]
 230         message: "Got it! Let me know if you need anything else."
 231 ```
 232 
 233 ---
 234 
 235 ## expectedOutcome Gotcha: Judges TEXT, Not Actions
 236 
 237 The `output_validation` assertion evaluates the agent's **text response** — it does NOT inspect action results, sObject writes, or internal state changes.
 238 
 239 ```yaml
 240 # ❌ WRONG — references internal action behavior
 241 expectedOutcome: "Agent should create a Survey_Result__c record with rating=4"
 242 
 243 # ❌ WRONG — references sObject changes
 244 expectedOutcome: "Agent should update the MessagingSession.Bot_Support_Path__c field"
 245 
 246 # ✅ RIGHT — describes what the agent SAYS
 247 expectedOutcome: "Agent acknowledges the rating and thanks the user for feedback"
 248 
 249 # ✅ RIGHT — describes observable text behavior
 250 expectedOutcome: "Agent confirms the payment is being processed and provides a confirmation number"
 251 ```
 252 
 253 **Rule of thumb:** If you can't verify it by reading the agent's chat response, don't put it in `expectedOutcome`. Use `expectedActions` for action verification and `--verbose` output for action input/output inspection.
 254 
 255 ---
 256 
 257 ## History Length Guide
 258 
 259 | Test Goal | Recommended Turns | Pattern |
 260 |-----------|-------------------|---------|
 261 | Simple topic anchoring | 2 (1 user + 1 agent) | Basic routing |
 262 | Protocol activation | 4 (2 user + 2 agent) | Pattern A |
 263 | Mid-protocol stage | 4-6 | Pattern B |
 264 | Action invocation | 6 | Pattern C |
 265 | Opt-out / negative assertion | 4-6 | Pattern D |
 266 | Session persistence | 8 | Pattern E |
 267 
 268 > **Diminishing returns:** Beyond 8 turns, the history becomes expensive to maintain and may hit token limits. If you need deeper history, consider splitting into separate test cases or using the multi-turn API (Phase A) instead.
 269 
 270 ---
 271 
 272 ## Related Documentation
 273 
 274 | Resource | Link |
 275 |----------|------|
 276 | Test Spec Guide | [test-spec-guide.md](test-spec-guide.md) |
 277 | Test Spec Reference | [test-spec-reference.md](../references/test-spec-reference.md) |
 278 | Multi-Turn Testing Guide | [multi-turn-testing-guide.md](multi-turn-testing-guide.md) |
 279 | CLI Deep History Template | [cli-deep-history-tests.yaml](../assets/cli-deep-history-tests.yaml) |
 280 | Topic Name Resolution | [topic-name-resolution.md](topic-name-resolution.md) |
