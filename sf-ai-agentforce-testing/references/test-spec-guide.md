<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # Test Specification Guide
   2 
   3 Complete reference for creating YAML test specifications for Agentforce agents using `sf agent test create`.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 Test specifications define expected agent behavior using YAML format. When you run `sf agent test create`, the `@salesforce/agents` CLI plugin parses the YAML and deploys `AiEvaluationDefinition` metadata to the org.
  10 
  11 > **Important:** The YAML format is defined by the `@salesforce/agents` TypeScript source — NOT a generic `AiEvaluationDefinition` XML format. Only the fields documented below are recognized.
  12 
  13 ---
  14 
  15 ## File Structure
  16 
  17 ```yaml
  18 # Description: [Brief description of what this test suite validates]
  19 
  20 # Required: Display name (becomes MasterLabel in metadata)
  21 name: "My Agent Tests"
  22 
  23 # Required: Must be AGENT
  24 subjectType: AGENT
  25 
  26 # Required: Agent BotDefinition DeveloperName (API name)
  27 subjectName: My_Agent_Name
  28 
  29 testCases:
  30   - utterance: "User message to test"
  31     expectedTopic: topic_name
  32     expectedActions:
  33       - action_name
  34     expectedOutcome: "Natural language description of expected response"
  35 ```
  36 
  37 ### Required Top-Level Fields
  38 
  39 | Field | Type | Description |
  40 |-------|------|-------------|
  41 | `name` | string | Display name for the test (MasterLabel). **Deploy FAILS without this.** |
  42 | `subjectType` | string | Must be `AGENT` |
  43 | `subjectName` | string | Agent BotDefinition DeveloperName (API name) |
  44 | `testCases` | array | List of test case objects |
  45 
  46 > **Do NOT add** `apiVersion`, `kind`, `metadata`, or `settings` — these are not part of the CLI YAML schema and will be silently ignored or cause errors.
  47 
  48 ---
  49 
  50 ## Test Case Fields
  51 
  52 Each test case supports these fields:
  53 
  54 | Field | Type | Required | Description |
  55 |-------|------|----------|-------------|
  56 | `utterance` | string | **Yes** | User input message to test |
  57 | `expectedTopic` | string | No | Expected topic the agent should route to |
  58 | `expectedActions` | string[] | No | Flat list of action name strings expected to be invoked |
  59 | `expectedOutcome` | string | No | Natural language description of expected agent response |
  60 | `contextVariables` | array | No | Variables to inject into the test session |
  61 | `conversationHistory` | array | No | Prior conversation turns for multi-turn context |
  62 
  63 ### What the CLI Actually Validates
  64 
  65 The CLI runs three assertions per test case:
  66 
  67 | Assertion | Based On | Behavior |
  68 |-----------|----------|----------|
  69 | `topic_assertion` | `expectedTopic` | Exact match against runtime topic `developerName` |
  70 | `actions_assertion` | `expectedActions` | **Superset matching** — passes if agent invoked at least the expected actions |
  71 | `output_validation` | `expectedOutcome` | LLM-as-judge evaluates if agent response satisfies the description |
  72 
  73 ---
  74 
  75 ## Topic Routing Tests
  76 
  77 Verify the agent routes to the correct topic.
  78 
  79 ```yaml
  80 testCases:
  81   - utterance: "Where is my order?"
  82     expectedTopic: order_lookup
  83 
  84   - utterance: "What are your business hours?"
  85     expectedTopic: faq
  86 
  87   - utterance: "I have a problem with my product"
  88     expectedTopic: support_case
  89 ```
  90 
  91 ### Topic Name Resolution
  92 
  93 The `expectedTopic` value depends on the topic type:
  94 
  95 | Topic Type | Format | Example |
  96 |------------|--------|---------|
  97 | Standard (Escalation, Off_Topic) | `localDeveloperName` | `Escalation` |
  98 | Promoted (p_16j... prefix) | Full runtime `developerName` with hash | `p_16jPl000000GwEX_Topic_16j8eeef13560aa` |
  99 
 100 See [topic-name-resolution.md](topic-name-resolution.md) for the complete guide, including the discovery workflow for promoted topics.
 101 
 102 ### Multiple Phrasings
 103 
 104 Test the same topic with different phrasings to ensure robust routing:
 105 
 106 ```yaml
 107 testCases:
 108   - utterance: "Where is my order?"
 109     expectedTopic: order_lookup
 110 
 111   - utterance: "Track my package"
 112     expectedTopic: order_lookup
 113 
 114   - utterance: "When will my stuff arrive?"
 115     expectedTopic: order_lookup
 116 ```
 117 
 118 ---
 119 
 120 ## Action Invocation Tests
 121 
 122 Verify actions are invoked. `expectedActions` is a **flat list of action name strings**.
 123 
 124 ### Basic Action Test
 125 
 126 ```yaml
 127 testCases:
 128   - utterance: "What's the status of order 12345?"
 129     expectedTopic: order_lookup
 130     expectedActions:
 131       - get_order_status
 132 ```
 133 
 134 ### Multiple Actions
 135 
 136 ```yaml
 137 testCases:
 138   - utterance: "Look up my order and create a case for it"
 139     expectedTopic: order_lookup
 140     expectedActions:
 141       - get_order_status
 142       - create_support_case
 143 ```
 144 
 145 ### Superset Matching
 146 
 147 Action assertions use **superset matching**:
 148 - Expected: `[get_order_status]` / Actual: `[get_order_status, summarize_record]` → **PASS**
 149 - The agent can invoke additional actions beyond what's expected and the test still passes.
 150 
 151 ### Empty Actions
 152 
 153 | Pattern | Meaning | Current Behavior |
 154 |---------|---------|------------------|
 155 | `expectedActions:` omitted | "Not testing actions" | PASS regardless of what fires |
 156 | `expectedActions: []` | "Testing that NO actions fire" | Currently same behavior (PASS regardless), but documents intent |
 157 
 158 **Best practice:** Use `expectedActions: []` explicitly for opt-out tests to document your intent that no action should fire, even though the CLI currently treats it the same as omitted. This makes the test self-documenting and future-proofs against framework changes.
 159 
 160 ```yaml
 161 # Omitted — "I'm not testing actions for this test case"
 162 - utterance: "Hello"
 163   expectedTopic: greeting
 164   # (expectedActions omitted entirely)
 165 
 166 # Empty list — DELIBERATE assertion: "NO action should fire"
 167 - utterance: "No thanks, I'm all set"
 168   expectedTopic: feedback_collection
 169   expectedActions: []    # Documents intent: opt-out should NOT trigger feedback action
 170   expectedOutcome: "Agent gracefully accepts the opt-out without pushing for feedback"
 171 ```
 172 
 173 ### Action Name Discovery for GenAiPlannerBundle Agents
 174 
 175 For GenAiPlannerBundle agents, action names in test results include a hash suffix (e.g., `Store_Feedback_179a9701f17c194`). Short name **prefix matching** works — you can use the prefix in `expectedActions` and the CLI will match.
 176 
 177 **Discovery workflow:**
 178 ```bash
 179 # Run with --verbose to see full action names
 180 sf agent test run --api-name Discovery --wait 10 --verbose --result-format json --json --target-org [alias]
 181 
 182 # Extract action names from results
 183 jq '.result.testCases[].generatedData | {topic, actionsSequence}' results.json
 184 
 185 # For detailed action input/output inspection
 186 jq '.result.testCases[].generatedData.invokedActions | fromjson | .[0][0].function' results.json
 187 ```
 188 
 189 > **Note:** The multi-turn API may report `has_action_result: false` for actions that actually fired. CLI `--verbose` output is authoritative for action verification.
 190 
 191 ---
 192 
 193 ## Outcome Validation Tests
 194 
 195 Verify the agent's response content using natural language descriptions.
 196 
 197 ```yaml
 198 testCases:
 199   - utterance: "What are your business hours?"
 200     expectedTopic: faq
 201     expectedOutcome: "Agent should provide specific business hours including days and times"
 202 
 203   - utterance: "How do I return an item?"
 204     expectedTopic: returns
 205     expectedOutcome: "Agent should explain the return process with step-by-step instructions"
 206 ```
 207 
 208 The CLI uses an LLM-as-judge to evaluate whether the agent's actual response satisfies the `expectedOutcome` description.
 209 
 210 > **Gotcha:** Omitting `expectedOutcome` causes `output_validation` to report `ERROR` status with "Skip metric result due to missing expected input". This is **harmless** — `topic_assertion` and `actions_assertion` still run normally.
 211 
 212 > **Important: `output_validation` judges TEXT, not actions.** The LLM-as-judge evaluates the agent's **text response** only — it does NOT inspect action results, sObject writes, or internal state changes. Write `expectedOutcome` about what the agent *says*, not what it *does* internally.
 213 >
 214 > ```yaml
 215 > # ❌ WRONG — references internal action behavior
 216 > expectedOutcome: "Agent should create a Survey_Result__c record with rating=4"
 217 >
 218 > # ❌ WRONG — references sObject changes
 219 > expectedOutcome: "Agent should update the MessagingSession.Bot_Support_Path__c field"
 220 >
 221 > # ✅ RIGHT — describes what the agent SAYS
 222 > expectedOutcome: "Agent acknowledges the rating and thanks the user for feedback"
 223 >
 224 > # ✅ RIGHT — describes observable text behavior
 225 > expectedOutcome: "Agent confirms the payment is being processed and provides next steps"
 226 > ```
 227 
 228 ---
 229 
 230 ## Multi-Turn Conversation Tests
 231 
 232 Provide conversation history to test context retention.
 233 
 234 ```yaml
 235 testCases:
 236   - utterance: "When will it arrive?"
 237     expectedTopic: order_lookup
 238     conversationHistory:
 239       - role: user
 240         message: "I want to check on order 12345"
 241       - role: agent
 242         topic: order_lookup
 243         message: "I'd be happy to help you check on order 12345. Let me look that up."
 244 
 245   - utterance: "Yes, please create one"
 246     expectedTopic: support_case
 247     expectedActions:
 248       - create_support_case
 249     conversationHistory:
 250       - role: user
 251         message: "My product is broken"
 252       - role: agent
 253         topic: support_case
 254         message: "I'm sorry to hear that. Would you like me to create a support case?"
 255 ```
 256 
 257 ### Conversation History Format
 258 
 259 | Field | Required | Description |
 260 |-------|----------|-------------|
 261 | `role` | Yes | `user` or `agent` (NOT `assistant`) |
 262 | `message` | Yes | The message content |
 263 | `topic` | Agent only | Topic name for agent turns |
 264 
 265 ### Deep Conversation History for Protocol Stage Testing
 266 
 267 By providing 4-8 turns of `conversationHistory`, you can position the agent at a specific point in a multi-step protocol and test its behavior at that exact stage. The `topic` field on agent turns **anchors the planner** to the correct topic context, making ambiguous utterances (like "thanks" or "I'm done") route deterministically.
 268 
 269 ```yaml
 270 # Without history: "Thanks for the help" routes stochastically (greeting? escalation? feedback?)
 271 # With history: anchored to feedback_collection after completed business interaction
 272 - utterance: "Thanks for the help"
 273   expectedTopic: feedback_collection
 274   conversationHistory:
 275     - role: user
 276       message: "I need to check my account status"
 277     - role: agent
 278       topic: account_support          # Local developer name — no hash suffix needed
 279       message: "I found your account. Everything looks good — your balance is current."
 280     - role: user
 281       message: "Great, that answers my question"
 282     - role: agent
 283       topic: account_support
 284       message: "Glad I could help! Is there anything else you need?"
 285 ```
 286 
 287 > **Key detail:** The `topic` field in `conversationHistory` resolves **local developer names** (e.g., `account_support`, `feedback_collection`). You do NOT need the hash-suffixed runtime `developerName` in history — only in `expectedTopic` for promoted topics.
 288 
 289 See [Deep Conversation History Patterns](deep-conversation-history-patterns.md) for 5 patterns: protocol activation, mid-protocol stage, action invocation, opt-out assertion, and session persistence.
 290 
 291 ---
 292 
 293 ## Context Variables
 294 
 295 Inject session context variables for testing.
 296 
 297 ```yaml
 298 testCases:
 299   - utterance: "What's the status of my account?"
 300     expectedTopic: account_lookup
 301     contextVariables:
 302       - name: "$Context.RoutableId"    # Prefixed format (recommended) — bare RoutableId also works
 303         value: "0Mw8X000000XXXXX"
 304       - name: CaseId
 305         value: "5008X000000XXXXX"
 306 ```
 307 
 308 > **Important:** Agents with authentication flows (e.g., `User_Authentication` topic) typically require `RoutableId` and `CaseId` context variables. Without them, the authentication flow fails and the agent escalates on Turn 1. Both prefixed names (`$Context.RoutableId`) and bare names (`RoutableId`) work — the runtime resolves both formats. The `$Context.` prefix is recommended as it matches the Merge Field syntax used in Flow Builder.
 309 
 310 ---
 311 
 312 ## Escalation Tests
 313 
 314 Standard `Escalation` topic uses `localDeveloperName`:
 315 
 316 ```yaml
 317 testCases:
 318   - utterance: "I need to speak to a manager about my billing issue"
 319     expectedTopic: Escalation
 320 
 321   - utterance: "This is too complicated, I need a human"
 322     expectedTopic: Escalation
 323 ```
 324 
 325 ---
 326 
 327 ## Complete Example
 328 
 329 ```yaml
 330 name: "Customer Support Agent Tests"
 331 subjectType: AGENT
 332 subjectName: Customer_Support_Agent
 333 
 334 testCases:
 335   # ═══ TOPIC ROUTING ═══
 336   - utterance: "Where is my order?"
 337     expectedTopic: order_lookup
 338 
 339   - utterance: "Track my package"
 340     expectedTopic: order_lookup
 341 
 342   - utterance: "What are your business hours?"
 343     expectedTopic: faq
 344 
 345   - utterance: "I have a problem with my product"
 346     expectedTopic: support_case
 347 
 348   # ═══ ACTION TESTS ═══
 349   - utterance: "What's the status of order 12345?"
 350     expectedTopic: order_lookup
 351     expectedActions:
 352       - get_order_status
 353 
 354   - utterance: "Create a support case for my broken item"
 355     expectedTopic: support_case
 356     expectedActions:
 357       - create_support_case
 358 
 359   # ═══ OUTCOME TESTS ═══
 360   - utterance: "How do I return an item?"
 361     expectedTopic: returns
 362     expectedOutcome: "Agent should explain the return process and any time limits"
 363 
 364   # ═══ ESCALATION ═══
 365   - utterance: "I need to speak with a manager"
 366     expectedTopic: Escalation
 367 
 368   # ═══ MULTI-TURN ═══
 369   - utterance: "Can you create a case for this?"
 370     expectedTopic: support_case
 371     expectedActions:
 372       - create_support_case
 373     conversationHistory:
 374       - role: user
 375         message: "My product arrived damaged"
 376       - role: agent
 377         topic: support_case
 378         message: "I'm sorry to hear that. I can help you create a support case."
 379 ```
 380 
 381 ---
 382 
 383 ## Agent Script Agents (AiAuthoringBundle)
 384 
 385 Agent Script agents (`.agent` files) have unique testing requirements due to their two-level action system and `start_agent` routing.
 386 
 387 ### Key Differences from GenAiPlannerBundle Agents
 388 
 389 | Aspect | Agent Script | GenAiPlannerBundle |
 390 |--------|-------------|-------------------|
 391 | Single-utterance test | Captures transition action only | May capture business action |
 392 | Action names in results | Level 1 definition name | GenAiFunction name |
 393 | `subjectName` source | `config.developer_name` in `.agent` | Directory name of bundle |
 394 | Action test approach | Use `conversationHistory` for `apex://` | Standard single-utterance |
 395 
 396 ### Routing Test (Transition Action)
 397 
 398 ```yaml
 399 testCases:
 400   - utterance: "I want to check my order status"
 401     expectedTopic: order_status
 402     expectedActions:
 403       - go_order_status    # Transition action from start_agent
 404 ```
 405 
 406 ### Action Test (with conversationHistory)
 407 
 408 ```yaml
 409 testCases:
 410   - utterance: "The order ID is 801ak00001g59JlAAI"
 411     conversationHistory:
 412       - role: "user"
 413         message: "I want to check my order status"
 414       - role: "agent"
 415         topic: "order_status"
 416         message: "Could you provide the Order ID?"
 417     expectedTopic: order_status
 418     expectedActions:
 419       - get_order_status    # Level 1 definition name, NOT check_status
 420 ```
 421 
 422 ### Permission Pre-Check
 423 
 424 If the Apex class uses `WITH USER_MODE`, the Einstein Agent User (`default_agent_user` in `.agent` config) must have read permissions on queried objects. Missing permissions cause **silent failures** (0 rows returned, no error).
 425 
 426 See [agentscript-testing-patterns.md](agentscript-testing-patterns.md) for 5 detailed test patterns and the permission pre-check workflow.
 427 
 428 ---
 429 
 430 ## Best Practices
 431 
 432 ### Test Coverage
 433 
 434 | Aspect | Recommendation |
 435 |--------|----------------|
 436 | Topics | Test every topic with 3+ phrasings |
 437 | Actions | Test every action at least once |
 438 | Escalation | Test trigger and non-trigger scenarios |
 439 | Edge cases | Test typos, gibberish, long inputs |
 440 
 441 ### Organization
 442 
 443 Group test cases by category using comments:
 444 
 445 ```yaml
 446 testCases:
 447   # ═══ TOPIC ROUTING ═══
 448   - utterance: "..."
 449   - utterance: "..."
 450 
 451   # ═══ ACTION TESTS ═══
 452   - utterance: "..."
 453   - utterance: "..."
 454 ```
 455 
 456 ### Ambiguous Routing
 457 
 458 When multiple topics are acceptable destinations for an utterance, **omit `expectedTopic`** and use `expectedOutcome` for behavioral validation instead. This prevents false failures from non-deterministic routing.
 459 
 460 ```yaml
 461 testCases:
 462   # ❌ FRAGILE — fails if planner picks Off_Topic instead of Escalation
 463   - utterance: "What is the meaning of life?"
 464     expectedTopic: Escalation
 465 
 466   # ✅ ROBUST — validates behavior regardless of which topic fires
 467   - utterance: "What is the meaning of life?"
 468     expectedOutcome: "Agent deflects gracefully. Does NOT crash. Does NOT attempt to answer."
 469 ```
 470 
 471 ### Auth Gate Verification
 472 
 473 For agents with authentication flows, include tests confirming that business-domain requests route to the auth topic first — not to a broad catch-all:
 474 
 475 ```yaml
 476 testCases:
 477   - utterance: "I need to check my order status"
 478     expectedTopic: User_Authentication0
 479 
 480   - utterance: "Can I update my billing information?"
 481     expectedTopic: User_Authentication0
 482 
 483   - utterance: "I want to return a product"
 484     expectedTopic: User_Authentication0
 485 ```
 486 
 487 If any of these route to a non-auth topic (e.g., Escalation), the catch-all topic's description is likely too broad and absorbing business intents.
 488 
 489 ### Description Convention
 490 
 491 Since `AiEvaluationDefinition` metadata has no XML `<description>` element, document each test suite's purpose using a YAML comment at the top of the spec file:
 492 
 493 ```yaml
 494 # Description: Validates auth-first routing for all greeting patterns
 495 name: "VVS Greeting Auth Tests"
 496 subjectType: AGENT
 497 subjectName: Product_Troubleshooting2
 498 ```
 499 
 500 This convention helps teams understand the intent of each test suite at a glance.
 501 
 502 ### Parallel Test Suites
 503 
 504 For agents with 20+ test cases, split into category-based YAML specs for parallel execution:
 505 
 506 ```
 507 tests/
 508 ├── agent-routing-tests.yaml      # Topic routing (8 tests)
 509 ├── agent-guardrail-tests.yaml    # Guardrails and deflection (10 tests)
 510 ├── agent-auth-tests.yaml         # Auth gate verification (5 tests)
 511 └── agent-session-tests.yaml      # Session/context tests (3 tests)
 512 ```
 513 
 514 Each spec is deployed independently via `sf agent test create`, then executed in parallel via separate `sf agent test run` commands. This reduces total wall-clock time and makes failures easier to categorize.
 515 
 516 ---
 517 
 518 ## Known Gotchas
 519 
 520 | Issue | Detail |
 521 |-------|--------|
 522 | **`name:` is mandatory** | Deploy fails with "Required fields are missing: [MasterLabel]" if omitted |
 523 | **`expectedActions` is a flat string list** | NOT objects with `name`/`invoked`/`outputs` — those are fabricated fields |
 524 | **Empty `expectedActions: []` means "not testing"** | Will PASS even if actions are invoked |
 525 | **Missing `expectedOutcome` causes harmless ERROR** | `output_validation` reports ERROR but topic/action assertions still work |
 526 | **CLI has NO MessagingSession context** | Flows that need `recordId` will error at runtime (agent handles gracefully) |
 527 | **`--use-most-recent` flag is broken** | Always use `--job-id` explicitly for `sf agent test results` |
 528 | **Promoted topics need full runtime name** | `localDeveloperName` only resolves for standard topics |
 529 | **`instruction_following` crashes Testing Center UI** | `No enum constant AiEvaluationMetricType.INSTRUCTION_FOLLOWING_EVALUATION` — CLI works fine but UI breaks. Remove this metric if users need Testing Center UI access. |
 530 | **Standard platform topics intercept before custom routing** | `Inappropriate_Content`, `Prompt_Injection`, `Reverse_Engineering` fire BEFORE the custom planner. Don't use custom topic names for these guardrail tests. See [topic-name-resolution.md](topic-name-resolution.md#standard-platform-topics-intercept-before-custom-routing). |
 531 | **`coherence` misleading for deflection agents** | Evaluates whether the response "answers" the user's question — scores 2-3 for correct deflections. Use `expectedOutcome` for guardrail/deflection tests instead. |
 532 
 533 ---
 534 
 535 ## Troubleshooting
 536 
 537 | Issue | Cause | Solution |
 538 |-------|-------|----------|
 539 | "Required fields are missing: [MasterLabel]" | Missing `name:` field | Add `name:` to top of YAML |
 540 | Topic assertion fails | Wrong topic name format | See [topic-name-resolution.md](topic-name-resolution.md) |
 541 | Action assertion unexpected PASS | Superset matching | Expected is subset of actual — this is correct behavior |
 542 | `output_validation` shows ERROR | No `expectedOutcome` provided | Add `expectedOutcome` or ignore — harmless |
 543 | "Agent not found" | Wrong `subjectName` | Verify agent DeveloperName in org |
