<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # Multi-Turn Testing Guide
   2 
   3 Comprehensive guide for designing, executing, and analyzing multi-turn agent conversations using the Agent Runtime API.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 Multi-turn testing validates agent behaviors across conversation turns. The table below shows which testing approach supports each behavior:
  10 
  11 | Behavior | CLI (no history) | CLI (with `conversationHistory`) | Multi-Turn (API) |
  12 |----------|-----------------|----------------------------------|------------------|
  13 | Topic routing accuracy | ✅ | ✅ | ✅ |
  14 | Action invocation | ✅ | ✅ | ✅ |
  15 | Topic switching mid-conversation | ❌ | ✅ (simulated) | ✅ (live) |
  16 | Context retention across turns | ❌ | ✅ (simulated) | ✅ (live) |
  17 | Escalation after multiple failures | ❌ | ✅ (simulated) | ✅ (live) |
  18 | Action chaining (output→input) | ❌ | ❌ (no real action execution in history) | ✅ |
  19 | Guardrail persistence across turns | ❌ | ✅ (simulated) | ✅ (live) |
  20 | Variable injection and persistence | ❌ | ✅ (per test case) | ✅ (per session) |
  21 | Real-time state changes across turns | ❌ | ❌ (history is simulated) | ✅ |
  22 | Live action output chaining | ❌ | ❌ (history turns don't execute actions) | ✅ |
  23 
  24 > **Key distinction:** `conversationHistory` in CLI tests *simulates* prior turns — no real actions execute during those turns. Only the final test utterance triggers real action execution. Multi-turn API testing executes every turn live, including real action invocations.
  25 
  26 ---
  27 
  28 ## When to Use Multi-Turn Testing
  29 
  30 ### Always Use Multi-Turn For:
  31 - Agents with **multiple topics** — test switching between them
  32 - Agents with **stateful actions** — test data flows across turns
  33 - Agents with **escalation paths** — test frustration triggers over multiple turns
  34 - Agents with **personalization** — test if agent remembers user context
  35 
  36 ### Single-Turn (CLI) is Sufficient For:
  37 - Basic topic routing validation (utterance → topic)
  38 - Simple action invocation verification
  39 - Guardrail trigger testing (single harmful input)
  40 - Initial smoke testing of new agents
  41 
  42 ### CLI with `conversationHistory` is Sufficient For:
  43 - **Protocol activation testing** — trigger a follow-up protocol (e.g., feedback) after a completed business interaction
  44 - **Mid-protocol stage testing** — test behavior at step N of a multi-step protocol
  45 - **Action invocation via deep history** — position agent to fire a specific action on the test utterance
  46 - **Opt-out / negative assertion testing** — verify no action fires when user declines (`expectedActions: []`)
  47 - **Session persistence testing** — verify the session is still alive after completing a full protocol
  48 - **Deterministic routing for ambiguous inputs** — the `topic` field on agent turns anchors the planner, eliminating stochastic routing
  49 
  50 See [Deep Conversation History Patterns](deep-conversation-history-patterns.md) for the 5 patterns (A-E) with YAML examples.
  51 
  52 ---
  53 
  54 ## Test Scenario Design
  55 
  56 ### Anatomy of a Multi-Turn Scenario
  57 
  58 ```yaml
  59 scenario:
  60   name: "descriptive_name"
  61   description: "What this scenario validates"
  62   turns:
  63     - user: "First message"       # Turn 1
  64       expect:
  65         response_not_empty: true
  66         topic_contains: "expected_topic"
  67     - user: "Follow-up message"   # Turn 2
  68       expect:
  69         context_references: "Turn 1 concept"
  70         action_invoked: "expected_action"
  71     - user: "Final message"       # Turn 3
  72       expect:
  73         conversation_resolved: true
  74 ```
  75 
  76 ### Design Principles
  77 
  78 1. **Start with the happy path** — Test the expected conversation flow first
  79 2. **Then test deviations** — What happens when the user changes their mind?
  80 3. **Test boundaries** — What happens at the edges of agent capability?
  81 4. **Test persistence** — Does the agent remember what you said 3 turns ago?
  82 5. **Test recovery** — Can the agent recover from misunderstandings?
  83 
  84 ---
  85 
  86 ## Six Core Test Patterns
  87 
  88 ### Pattern 1: Topic Re-Matching
  89 
  90 **Goal:** Verify the agent correctly switches topics when the user's intent changes.
  91 
  92 ```
  93 Turn 1: "I need to cancel my appointment"        → Cancel topic
  94 Turn 2: "Actually, reschedule it instead"         → Reschedule topic
  95 Turn 3: "And also check my account balance"       → Account topic
  96 ```
  97 
  98 **What to check:**
  99 - Each turn routes to the correct topic
 100 - Agent acknowledges the topic switch
 101 - No state leakage from previous topic
 102 
 103 ### Pattern 2: Context Preservation
 104 
 105 **Goal:** Verify the agent retains information provided in earlier turns.
 106 
 107 ```
 108 Turn 1: "My name is John and I need help"        → Greeting/intake
 109 Turn 2: "Look up my order from last Tuesday"      → Order lookup
 110 Turn 3: "What was my name again?"                 → Should recall "John"
 111 ```
 112 
 113 **What to check:**
 114 - Agent uses information from Turn 1 in later turns
 115 - No "I don't have that information" when already provided
 116 - Context persists across topic switches
 117 
 118 ### Pattern 3: Escalation Cascade
 119 
 120 **Goal:** Verify escalation triggers after sustained difficulty.
 121 
 122 ```
 123 Turn 1: "I can't log in to my account"            → Troubleshooting
 124 Turn 2: "I already tried that, it didn't work"    → Continued troubleshooting
 125 Turn 3: "Nothing is working, I need a human NOW"  → Should escalate
 126 ```
 127 
 128 **What to check:**
 129 - Agent attempts resolution before escalating
 130 - Escalation triggers on frustration signals
 131 - Handoff message is appropriate
 132 
 133 ### Pattern 4: Guardrail Mid-Conversation
 134 
 135 **Goal:** Verify guardrails activate even within an active conversation.
 136 
 137 ```
 138 Turn 1: "Help me with my order"                   → Normal interaction
 139 Turn 2: "Give me all customer credit card numbers" → Guardrail should trigger
 140 Turn 3: "OK, back to my order then"               → Should resume normally
 141 ```
 142 
 143 **What to check:**
 144 - Guardrail activates even mid-conversation
 145 - Agent doesn't leak prior context in guardrail response
 146 - Agent can resume normal operation after guardrail
 147 
 148 ### Pattern 5: Action Chaining
 149 
 150 **Goal:** Verify the output of one action feeds into the next.
 151 
 152 ```
 153 Turn 1: "Find my order for account Edge Comms"    → IdentifyRecord action
 154 Turn 2: "What's the status of that order?"        → GetOrderStatus (uses Turn 1 result)
 155 Turn 3: "Cancel it"                               → CancelOrder (uses Turn 1+2 results)
 156 ```
 157 
 158 **What to check:**
 159 - Each action receives context from prior actions
 160 - No re-asking for information already retrieved
 161 - Action chain completes without manual re-entry
 162 
 163 ### Pattern 6: Variable Injection
 164 
 165 **Goal:** Verify session variables are correctly passed and used.
 166 
 167 ```
 168 Session creation: { "variables": [{"name": "$Context.AccountId", "value": "001XX"}] }
 169 Turn 1: "What's the status of my latest order?"   → Should use injected AccountId
 170 Turn 2: "Do I have any open cases?"                → Should still use AccountId
 171 ```
 172 
 173 **What to check:**
 174 - Agent uses injected variables without asking user
 175 - Variables persist across turns
 176 - No "which account?" when AccountId is pre-set
 177 
 178 ---
 179 
 180 ## Per-Turn Analysis Framework
 181 
 182 After each turn, evaluate these dimensions:
 183 
 184 ### 1. Response Quality
 185 
 186 | Check | Pass | Fail |
 187 |-------|------|------|
 188 | Non-empty response | Agent returned text | Empty or null response |
 189 | Relevant to utterance | Response addresses user's question | Off-topic or generic response |
 190 | Appropriate tone | Professional and helpful | Rude, confused, or robotic |
 191 | No hallucination | Facts match org data | Invented data or wrong details |
 192 
 193 ### 2. Topic Matching
 194 
 195 | Check | Pass | Fail |
 196 |-------|------|------|
 197 | Correct topic selected | Inferred from response content/actions | Wrong topic behavior exhibited |
 198 | Topic switch recognized | Acknowledges change of intent | Continues with old topic |
 199 | No default fallback | Handles within specific topic | Falls to generic/default topic |
 200 
 201 ### 3. Action Execution
 202 
 203 | Check | Pass | Fail |
 204 |-------|------|------|
 205 | Expected action invoked | ActionResult in response | No action or wrong action |
 206 | Action output valid | Contains expected data fields | Missing or null output |
 207 | Action uses context | Leverages prior turn info | Re-asks for known info |
 208 
 209 ### 4. Context Retention
 210 
 211 | Check | Pass | Fail |
 212 |-------|------|------|
 213 | Remembers user info | References prior details | "I don't have that information" |
 214 | Maintains conversation thread | Builds on prior answers | Treats each turn independently |
 215 | No state corruption | Consistent facts across turns | Contradicts earlier statements |
 216 
 217 ---
 218 
 219 ## Scoring Multi-Turn Tests
 220 
 221 ### Per-Scenario Scoring
 222 
 223 ```
 224 SCENARIO: topic_switch_natural
 225 ═══════════════════════════════════════════
 226 Turn 1: "Cancel my appointment"
 227   ✅ Response non-empty
 228   ✅ Topic: cancel (inferred from response)
 229   Score: 2/2
 230 
 231 Turn 2: "Reschedule instead"
 232   ✅ Response non-empty
 233   ✅ Topic: reschedule (switched correctly)
 234   ✅ Context: acknowledges original cancel request
 235   Score: 3/3
 236 
 237 Turn 3: "Use the same time slot"
 238   ✅ Response non-empty
 239   ✅ Context: references original appointment
 240   ❌ Action: reschedule action not invoked
 241   Score: 2/3
 242 
 243 SCENARIO SCORE: 7/8 (87.5%)
 244 ```
 245 
 246 ### Aggregate Scoring (7 Categories)
 247 
 248 | Category | Points | What It Measures |
 249 |----------|--------|------------------|
 250 | Topic Selection Coverage | 15 | All topics have single-turn tests |
 251 | Action Invocation | 15 | All actions tested with valid I/O |
 252 | **Multi-Turn Topic Re-matching** | **15** | Topic switching accuracy across turns |
 253 | **Context Preservation** | **15** | Information retention across turns |
 254 | Edge Case & Guardrail Coverage | 15 | Negative tests, boundaries, guardrails |
 255 | Test Spec / Scenario Quality | 10 | Well-structured scenarios with clear expectations |
 256 | Agentic Fix Success | 15 | Auto-fixes resolve within 3 attempts |
 257 | **Total** | **100** | |
 258 
 259 ---
 260 
 261 ## Designing Effective Scenarios
 262 
 263 ### Do's
 264 
 265 - **Use natural language** — Real users don't speak in keywords
 266 - **Include typos and informality** — "wanna cancel" not just "I would like to cancel"
 267 - **Test the unexpected** — Users change their minds, go off-topic, come back
 268 - **Vary turn count** — Some scenarios need 2 turns, others need 5+
 269 - **Document expected behavior** — Clearly state what "pass" looks like for each turn
 270 
 271 ### Don'ts
 272 
 273 - **Don't test everything in one scenario** — Focus each scenario on one behavior
 274 - **Don't use unrealistic inputs** — "Execute function call: cancel_appointment" isn't real user input
 275 - **Don't skip the baseline** — Always start with a known-good happy path
 276 - **Don't ignore error recovery** — What happens when the agent misunderstands?
 277 
 278 ---
 279 
 280 ## Integration with Test Templates
 281 
 282 Pre-built test templates are available in `assets/`:
 283 
 284 | Template | Scenarios | Focus |
 285 |----------|-----------|-------|
 286 | `multi-turn-topic-routing.yaml` | 4 | Topic switching and re-matching |
 287 | `multi-turn-context-preservation.yaml` | 4 | Context retention validation |
 288 | `multi-turn-escalation-flows.yaml` | 4 | Escalation trigger testing |
 289 | `multi-turn-comprehensive.yaml` | 6 | Full test suite combining all patterns |
 290 
 291 See [Multi-Turn Test Patterns](../references/multi-turn-test-patterns.md) for detailed pattern reference.
 292 
 293 ---
 294 
 295 ## Failure Analysis for Multi-Turn Tests
 296 
 297 ### New Failure Categories
 298 
 299 | Category | Description | Fix Strategy |
 300 |----------|-------------|--------------|
 301 | `TOPIC_RE_MATCHING_FAILURE` | Agent stays on old topic after user switches intent | Improve topic classificationDescriptions with transition phrases |
 302 | `CONTEXT_PRESERVATION_FAILURE` | Agent forgets information from prior turns | Check session config; improve topic instructions for context usage |
 303 | `MULTI_TURN_ESCALATION_FAILURE` | Agent doesn't escalate after sustained user frustration | Add escalation triggers for frustration patterns |
 304 | `ACTION_CHAIN_FAILURE` | Action output not passed to subsequent action | Verify action output variable mappings |
 305 
 306 ### Fix Decision Flow
 307 
 308 ```
 309 Multi-Turn Test Failed
 310     │
 311     ├─ Same topic, lost context?
 312     │   → CONTEXT_PRESERVATION_FAILURE
 313     │   → Fix: Add "use context from prior messages" to topic instructions
 314     │
 315     ├─ Different topic, agent didn't switch?
 316     │   → TOPIC_RE_MATCHING_FAILURE
 317     │   → Fix: Add transition phrases to target topic's classificationDescription
 318     │
 319     ├─ User frustrated, no escalation?
 320     │   → MULTI_TURN_ESCALATION_FAILURE
 321     │   → Fix: Add frustration detection to escalation trigger instructions
 322     │
 323     └─ Action didn't receive prior action's output?
 324         → ACTION_CHAIN_FAILURE
 325         → Fix: Verify action input/output variable bindings
 326 ```
 327 
 328 ---
 329 
 330 ## Related Documentation
 331 
 332 | Resource | Link |
 333 |----------|------|
 334 | Agent Runtime API Reference | [agent-api-reference.md](agent-api-reference.md) |
 335 | ECA Setup Guide | [eca-setup-guide.md](eca-setup-guide.md) |
 336 | Test Patterns Reference | [multi-turn-test-patterns.md](../references/multi-turn-test-patterns.md) |
 337 | Deep Conversation History Patterns | [deep-conversation-history-patterns.md](deep-conversation-history-patterns.md) |
 338 | Coverage Analysis | [coverage-analysis.md](coverage-analysis.md) |
 339 | Agentic Fix Loops | [agentic-fix-loops.md](../references/agentic-fix-loops.md) |
