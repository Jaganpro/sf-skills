<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # CLI Commands Reference
   2 
   3 Complete reference for SF CLI commands related to Agentforce testing.
   4 
   5 ---
   6 
   7 ## ⚠️ CRITICAL: Agent Testing Center Required
   8 
   9 **All `sf agent test` commands require Agent Testing Center feature enabled in your org.**
  10 
  11 ```bash
  12 # Check if Agent Testing Center is enabled
  13 sf agent test list --target-org [alias]
  14 
  15 # If you get these errors, Agent Testing Center is NOT enabled:
  16 # ❌ "Not available for deploy for this organization"
  17 # ❌ "INVALID_TYPE: Cannot use: AiEvaluationDefinition in this organization"
  18 ```
  19 
  20 See [SKILL.md](../SKILL.md#-critical-org-requirements-agent-testing-center) for enabling this feature.
  21 
  22 ---
  23 
  24 ## Command Overview
  25 
  26 ```
  27 sf agent test
  28 ├── create          Create agent test in org from spec (requires Agent Testing Center)
  29 ├── list            List available test definitions (requires Agent Testing Center)
  30 ├── run             Start agent test execution (requires Agent Testing Center)
  31 ├── results         Get completed test results
  32 └── resume          Resume incomplete test run
  33 
  34 sf agent
  35 ├── preview         Interactive agent testing (works without Agent Testing Center)
  36 ├── generate
  37 │   └── test-spec   Generate test specification YAML (interactive only - no --api-name flag)
  38 └── (other agent commands in sf-ai-agentscript)
  39 ```
  40 
  41 **Note:** `sf agent preview` works WITHOUT Agent Testing Center - useful for manual testing when automated tests are unavailable.
  42 
  43 ---
  44 
  45 ## Test Specification Generation
  46 
  47 ### sf agent generate test-spec
  48 
  49 Generate a YAML test specification **interactively** (no batch/scripted mode available).
  50 
  51 ```bash
  52 sf agent generate test-spec [--output-file <path>]
  53 ```
  54 
  55 **⚠️ Important:** This command is **interactive only**. There is no `--api-name` flag to auto-generate from an existing agent. You must manually input test cases through the prompts.
  56 
  57 **Flags:**
  58 
  59 | Flag | Description |
  60 |------|-------------|
  61 | `--output-file` | Path for generated YAML (default: `specs/agentTestSpec.yaml`) |
  62 | `--api-version` | Override API version |
  63 
  64 **⛔ Non-existent flags (DO NOT USE):**
  65 - `--api-name` - Does NOT exist (common misconception)
  66 - `--agent-name` - Does NOT exist
  67 - `--from-agent` - Does NOT exist
  68 
  69 **Interactive Prompts:**
  70 
  71 The command interactively prompts for:
  72 1. **Utterance** - Test input (user message)
  73 2. **Expected topic** - Which topic should be selected
  74 3. **Expected actions** - Which actions should be invoked
  75 4. **Expected outcome** - Response validation rules
  76 5. **Custom evaluations** - JSONPath expressions for complex validation
  77 6. **Add another?** - Continue adding test cases
  78 
  79 **Example:**
  80 
  81 ```bash
  82 sf agent generate test-spec --output-file ./tests/support-agent-tests.yaml
  83 
  84 # Interactive session:
  85 # > Enter utterance: Where is my order?
  86 # > Expected topic: order_lookup
  87 # > Expected actions (comma-separated): get_order_status
  88 # > Expected outcome: action_invoked
  89 # > Add another test case? (y/n): y
  90 ```
  91 
  92 ---
  93 
  94 ## Test Creation
  95 
  96 ### sf agent test create
  97 
  98 Create an agent test in the org from a YAML specification.
  99 
 100 ```bash
 101 sf agent test create --spec <file> --target-org <alias> [--api-name <name>] [--force-overwrite]
 102 ```
 103 
 104 **Required Flags:**
 105 
 106 | Flag | Description |
 107 |------|-------------|
 108 | `-s, --spec` | Path to test spec YAML file |
 109 | `-o, --target-org` | Target org alias or username |
 110 
 111 **Optional Flags:**
 112 
 113 | Flag | Description |
 114 |------|-------------|
 115 | `-n, --api-name` | API name for the test (auto-generated if omitted) |
 116 | `--force-overwrite` | Skip confirmation if test exists |
 117 | `--preview` | Dry-run - view metadata without deploying |
 118 
 119 **Example:**
 120 
 121 ```bash
 122 # Create test from spec
 123 sf agent test create --spec ./tests/support-agent-tests.yaml --target-org dev
 124 
 125 # Force overwrite existing test
 126 sf agent test create --spec ./tests/updated-spec.yaml --api-name MyAgentTest --force-overwrite --target-org dev
 127 
 128 # Preview without deploying
 129 sf agent test create --spec ./tests/spec.yaml --preview --target-org dev
 130 ```
 131 
 132 **Output:**
 133 
 134 Creates `AiEvaluationDefinition` metadata in the org at:
 135 ```
 136 force-app/main/default/aiEvaluationDefinitions/[TestName].aiEvaluationDefinition-meta.xml
 137 ```
 138 
 139 ---
 140 
 141 ## Test Execution
 142 
 143 ### sf agent test run
 144 
 145 Execute agent tests asynchronously.
 146 
 147 ```bash
 148 sf agent test run --api-name <name> --target-org <alias> [--wait <minutes>]
 149 ```
 150 
 151 **Required Flags:**
 152 
 153 | Flag | Description |
 154 |------|-------------|
 155 | `-n, --api-name` | Test API name (created via `test create`) |
 156 | `-o, --target-org` | Target org alias or username |
 157 
 158 **Optional Flags:**
 159 
 160 | Flag | Description |
 161 |------|-------------|
 162 | `-w, --wait` | Minutes to wait for completion (default: async) |
 163 | `-r, --result-format` | Output format: `human` (default), `json`, `junit`, `tap` |
 164 | `-d, --output-dir` | Directory to save results |
 165 | `--verbose` | Include detailed action data |
 166 
 167 **Example:**
 168 
 169 ```bash
 170 # Run test and wait up to 10 minutes
 171 sf agent test run --api-name CustomerSupportTests --wait 10 --target-org dev
 172 
 173 # Run async (returns job ID immediately)
 174 sf agent test run --api-name MyAgentTest --target-org dev
 175 
 176 # Run with JSON output for CI/CD
 177 sf agent test run --api-name MyAgentTest --wait 15 --result-format json --output-dir ./results --target-org dev
 178 
 179 # Run with verbose output
 180 sf agent test run --api-name MyAgentTest --wait 10 --verbose --target-org dev
 181 ```
 182 
 183 ### Verbose Output (`--verbose`)
 184 
 185 The `--verbose` flag adds detailed `generatedData` to test results, including action invocations with inputs/outputs, raw agent response text, and test session IDs.
 186 
 187 **Additional fields in `generatedData` with `--verbose`:**
 188 
 189 | Field | Type | Description |
 190 |-------|------|-------------|
 191 | `invokedActions` | stringified JSON | All action invocations per turn — inputs, outputs, latency |
 192 | `generatedResponse` | string | Raw agent response text (pre-formatting) |
 193 | `sessionId` | string | Test session UUID |
 194 
 195 **Example `generatedData` with `--verbose`:**
 196 
 197 ```json
 198 "generatedData": {
 199   "topic": "p_16jPl000000GwEX_Field_Support_Routing_16j8eeef13560aa",
 200   "actionsSequence": "['Field_Support_Updating_Messaging_Session_179c7c824b693d7']",
 201   "generatedResponse": "Looks like you're wanting assistance...",
 202   "invokedActions": "[[{\"function\":{\"name\":\"Field_Support_Updating_Messaging_Session_179c7c824b693d7\",\"input\":{\"deviceType\":\"Unknown\",\"recordId\":\"0Mwbb000007MGoTCAW\",\"supportPath\":\"Field Support\"},\"output\":{\"caseId\":null}},\"executionLatency\":3553}]]",
 203   "outcome": "Looks like you're wanting assistance...",
 204   "sessionId": "019c435a-be34-7ed5-bb1e-081a6e3be446"
 205 }
 206 ```
 207 
 208 > **Important:** `invokedActions` is a **stringified JSON** — the value is `"[[{...}]]"` (a string), NOT a parsed array. Parse it with `JSON.parse()` or `jq 'fromjson'` before traversing.
 209 
 210 **Using `--verbose` to build JSONPath for custom evaluations:**
 211 
 212 1. Run: `sf agent test run --api-name Test --wait 10 --verbose --result-format json --json --target-org dev`
 213 2. Extract action data: `jq '.result.testCases[0].generatedData.invokedActions | fromjson'`
 214 3. Build JSONPath: `$.generatedData.invokedActions[0][0].function.input.[fieldName]`
 215 
 216 **Async Behavior:**
 217 
 218 Without `--wait`, the command:
 219 1. Starts the test
 220 2. Returns a job ID
 221 3. Exits immediately
 222 
 223 Use `sf agent test results --job-id <id>` to retrieve results later.
 224 
 225 ---
 226 
 227 ## Test Results
 228 
 229 ### sf agent test results
 230 
 231 Retrieve results from a completed test run.
 232 
 233 ```bash
 234 sf agent test results --job-id <id> --target-org <alias> [--result-format <format>]
 235 ```
 236 
 237 **⚠️ CRITICAL BUG:** The `--use-most-recent` flag is documented in `--help` but **NOT IMPLEMENTED**. You will get "Nonexistent flag" error. **ALWAYS use `--job-id` explicitly.**
 238 
 239 **Flags:**
 240 
 241 | Flag | Description |
 242 |------|-------------|
 243 | `-i, --job-id` | **(REQUIRED)** Job ID from `test run` command |
 244 | `-o, --target-org` | Target org alias or username |
 245 | `-r, --result-format` | Output format: `human`, `json`, `junit`, `tap` |
 246 | `-d, --output-dir` | Directory to save results |
 247 | `--verbose` | Include generated data (actions, objects touched) |
 248 
 249 **⛔ Non-working flags (DO NOT USE):**
 250 - `--use-most-recent` - Documented but NOT implemented as of Jan 2026
 251 
 252 **Example:**
 253 
 254 ```bash
 255 # Get results from specific job (REQUIRED - must use job-id)
 256 sf agent test results --job-id 4KBak0000001btZGAQ --result-format json --target-org dev
 257 
 258 # Save results to file
 259 sf agent test results --job-id 4KBak0000001btZGAQ --output-dir ./results --target-org dev
 260 
 261 # With verbose output to see action details
 262 sf agent test results --job-id 4KBak0000001btZGAQ --verbose --target-org dev
 263 ```
 264 
 265 **Getting the Job ID:**
 266 The `sf agent test run` command outputs the job ID when it starts:
 267 ```
 268 Job ID: 4KBak0000001btZGAQ
 269 ```
 270 Save this ID to retrieve results later.
 271 
 272 ---
 273 
 274 ## Test Resume
 275 
 276 ### sf agent test resume
 277 
 278 Resume or retrieve results from an incomplete test.
 279 
 280 ```bash
 281 sf agent test resume --job-id <id> --target-org <alias> [--wait <minutes>]
 282 ```
 283 
 284 **Flags:**
 285 
 286 | Flag | Description |
 287 |------|-------------|
 288 | `-i, --job-id` | Job ID to resume |
 289 | `-o, --target-org` | Target org alias or username |
 290 | `-w, --wait` | Minutes to wait for completion |
 291 | `--result-format` | Output format |
 292 | `--output-dir` | Directory to save results |
 293 
 294 **Example:**
 295 
 296 ```bash
 297 # Resume specific job
 298 sf agent test resume --job-id 0Ah7X0000000001 --wait 5 --target-org dev
 299 ```
 300 
 301 ---
 302 
 303 ## Context Variables
 304 
 305 Context variables inject session-level data (record IDs, user info) into CLI test cases, enabling action flows to receive real record IDs instead of the topic's internal name.
 306 
 307 ### YAML Syntax
 308 
 309 ```yaml
 310 testCases:
 311   - utterance: "I need help with my device"
 312     expectedTopic: Field_Support_Routing
 313     expectedActions:
 314       - Field_Support_Updating_Messaging_Session_179c7c824b693d7
 315     contextVariables:
 316       - name: RoutableId            # NOT $Context.RoutableId — bare name only
 317         value: "0Mwbb000007MGoTCAW"
 318       - name: CaseId
 319         value: "500XX0000000001"
 320 ```
 321 
 322 **Key Rules:**
 323 - `name` uses the **bare variable name** (e.g., `RoutableId`), NOT `$Context.RoutableId`
 324 - The CLI framework adds the `$Context.` prefix automatically during XML generation
 325 - Maps to `<contextVariable><variableName>` / `<variableValue>` in metadata XML
 326 
 327 **Common Variables:**
 328 
 329 | Variable | Purpose | Discovery Query |
 330 |----------|---------|-----------------|
 331 | `RoutableId` | MessagingSession ID for action flows | `SELECT Id FROM MessagingSession WHERE Status='Active' LIMIT 1` |
 332 | `CaseId` | Case record ID | `SELECT Id FROM Case ORDER BY CreatedDate DESC LIMIT 1` |
 333 | `EndUserId` | End user contact/person ID | `SELECT Id FROM Contact LIMIT 1` |
 334 | `ContactId` | Contact record ID | `SELECT Id FROM Contact LIMIT 1` |
 335 
 336 **Effect of `RoutableId`:**
 337 - **Without RoutableId:** Action flows receive the topic's internal name (e.g., `p_16jPl000000GwEX_Field_Support_Routing_16j8eeef13560aa`) as `recordId`
 338 - **With RoutableId:** Action flows receive a real MessagingSession ID (e.g., `0Mwbb000007MGoTCAW`) as `recordId`
 339 
 340 > **Note:** Standard context variables (`RoutableId`, `CaseId`) do NOT unlock authentication-gated topics. Injecting them does not satisfy `User_Authentication` flows. However, **custom boolean auth-state variables** (e.g., `Verified_Check`) CAN bypass the authentication flow for testing post-auth business topics — inject the boolean variable as `true` via `contextVariables` to unlock gated topics directly.
 341 
 342 ---
 343 
 344 ## Custom Evaluations
 345 
 346 Custom evaluations allow JSONPath-based assertions on action inputs and outputs, enabling precise validation of what data an action received or returned.
 347 
 348 > **⚠️ SPRING '26 PLATFORM BUG:** Custom evaluations with `isReference: true` (JSONPath) are currently **BLOCKED** by a server-side bug. See [Known Issues](#critical-custom-evaluations-retry-bug-spring-26) below.
 349 
 350 ### YAML Syntax
 351 
 352 ```yaml
 353 testCases:
 354   - utterance: "My doorbell camera isn't working"
 355     expectedTopic: p_16jPl000000GwEX_Field_Support_Routing_16j8eeef13560aa
 356     expectedActions:
 357       - Field_Support_Updating_Messaging_Session_179c7c824b693d7
 358     contextVariables:
 359       - name: RoutableId
 360         value: "0Mwbb000007MGoTCAW"
 361     customEvaluations:
 362       - label: "supportPath is Field Support"
 363         name: string_comparison
 364         parameters:
 365           - name: operator
 366             value: equals
 367             isReference: false
 368           - name: actual
 369             value: "$.generatedData.invokedActions[0][0].function.input.supportPath"
 370             isReference: true       # JSONPath resolved against generatedData
 371           - name: expected
 372             value: "Field Support"
 373             isReference: false
 374 ```
 375 
 376 ### Evaluation Types
 377 
 378 **`string_comparison`** operators: `equals`, `contains`, `startswith`, `endswith`
 379 
 380 **`numeric_comparison`** operators: `equals`, `greater_than`, `less_than`, `greater_than_or_equal`, `less_than_or_equal`
 381 
 382 ### JSONPath Patterns
 383 
 384 Common JSONPath expressions for `invokedActions` (use `--verbose` to discover structure):
 385 
 386 | Path | What It Returns |
 387 |------|-----------------|
 388 | `$.generatedData.invokedActions[0][0].function.name` | Action name |
 389 | `$.generatedData.invokedActions[0][0].function.input.[field]` | Action input field value |
 390 | `$.generatedData.invokedActions[0][0].function.output.[field]` | Action output field value |
 391 | `$.generatedData.invokedActions[0][0].executionLatency` | Action execution latency (ms) |
 392 
 393 ### Workflow
 394 
 395 1. **Run with `--verbose`** to see `generatedData.invokedActions` structure
 396 2. **Parse the stringified JSON** to identify field names and values
 397 3. **Build JSONPath expressions** targeting specific input/output fields
 398 4. **Add `customEvaluations`** to your YAML test spec
 399 5. **Deploy and run** — ⚠️ results may only be viewable in Testing Center UI due to Spring '26 bug
 400 
 401 ---
 402 
 403 ## Metrics
 404 
 405 Metrics add platform quality scoring to test cases. They evaluate the agent's response quality using LLM-based grading or raw performance measurements.
 406 
 407 ### YAML Syntax
 408 
 409 ```yaml
 410 testCases:
 411   - utterance: "I need help troubleshooting my thermostat"
 412     expectedTopic: Field_Support_Routing
 413     expectedOutcome: "Agent should offer troubleshooting assistance"
 414     metrics:
 415       - coherence
 416       - instruction_following
 417       - output_latency_milliseconds
 418     # Skip: conciseness (broken), completeness (misleading for routing agents)
 419 ```
 420 
 421 ### Available Metrics
 422 
 423 | Metric | Score Range | Status | Description |
 424 |--------|-------------|--------|-------------|
 425 | `coherence` | 1-5 | ✅ Works (caveat) | Response clarity, grammar, and logical flow. Typically scores 4-5 for clear responses. **⚠️ Scores deflection agents poorly** (2-3) because it evaluates whether the response "answers" the user's literal question, not whether the agent behaved correctly. For deflection/guardrail tests, use `expectedOutcome` instead. |
 426 | `completeness` | 1-5 | ⚠️ Misleading | How fully the response addresses the query. **Penalizes triage/routing agents** for transferring instead of "solving." |
 427 | `conciseness` | 1-5 | 🔴 Broken | **Returns score=0** with empty `metricExplainability` on most tests. Platform bug. |
 428 | `instruction_following` | 0-1 | ⚠️ Two bugs | Whether agent follows instructions. **Bug 1:** Labels "FAILURE" even at score=1 — check score value, ignore label. **Bug 2:** Crashes Testing Center UI — `No enum constant AiEvaluationMetricType.INSTRUCTION_FOLLOWING_EVALUATION`. Remove from metrics if users need UI. |
 429 | `output_latency_milliseconds` | Raw ms | ✅ Works | Raw response latency. No pass/fail grading — useful for performance baselining. |
 430 
 431 ### Recommendations
 432 
 433 - **Use:** `coherence` + `output_latency_milliseconds` for baseline quality scoring
 434 - **Skip:** `conciseness` (broken) and `completeness` (misleading for routing agents)
 435 - **Caution:** `instruction_following` — rely on the numeric score, not the PASS/FAILURE label
 436 
 437 ---
 438 
 439 ## Test Listing
 440 
 441 ### sf agent test list
 442 
 443 List all agent test runs in the org.
 444 
 445 ```bash
 446 sf agent test list --target-org <alias>
 447 ```
 448 
 449 **Example:**
 450 
 451 ```bash
 452 sf agent test list --target-org dev
 453 ```
 454 
 455 **Output:**
 456 
 457 ```
 458 Test Name                  Status      Created
 459 ─────────────────────────────────────────────────
 460 CustomerSupportTests       Completed   2025-01-01
 461 OrderAgentTests           Running     2025-01-01
 462 FAQAgentTests             Failed      2024-12-30
 463 ```
 464 
 465 ---
 466 
 467 ## Interactive Preview
 468 
 469 ### sf agent preview
 470 
 471 Test agent interactively via conversation.
 472 
 473 ```bash
 474 sf agent preview --api-name <name> --target-org <alias> [options]
 475 ```
 476 
 477 **Required Flags:**
 478 
 479 | Flag | Description |
 480 |------|-------------|
 481 | `-n, --api-name` | Agent API name |
 482 | `-o, --target-org` | Target org alias or username |
 483 
 484 **Optional Flags:**
 485 
 486 | Flag | Description |
 487 |------|-------------|
 488 | `--use-live-actions` | Execute real Flows/Apex (vs simulated) |
 489 | `--authoring-bundle` | Specific authoring bundle to preview |
 490 | `-d, --output-dir` | Directory to save transcripts |
 491 | `-x, --apex-debug` | Capture Apex debug logs |
 492 
 493 **Modes:**
 494 
 495 | Mode | Command | Description |
 496 |------|---------|-------------|
 497 | **Simulated** | `sf agent preview --api-name Agent` | LLM simulates action results |
 498 | **Live** | `sf agent preview --api-name Agent --use-live-actions` | Real Flows/Apex execute |
 499 
 500 > **v2.121.7+**: When `--api-name` is omitted, the interactive agent selection now shows **(Published)** and **(Agent Script)** labels next to agent names to help distinguish agent types.
 501 
 502 **Example:**
 503 
 504 ```bash
 505 # Simulated preview (default - safe for testing)
 506 sf agent preview --api-name Customer_Support_Agent --target-org dev
 507 
 508 # Save transcripts
 509 sf agent preview --api-name Customer_Support_Agent --output-dir ./logs --target-org dev
 510 
 511 # Live preview with real actions
 512 sf agent preview --api-name Customer_Support_Agent --use-live-actions --target-org dev
 513 
 514 # Live preview with debug logs
 515 sf agent preview --api-name Customer_Support_Agent --use-live-actions --apex-debug --output-dir ./logs --target-org dev
 516 ```
 517 
 518 **Interactive Session:**
 519 
 520 ```
 521 > Hello, how can I help you today?
 522 
 523 You: Where is my order?
 524 
 525 Agent: I'd be happy to help you check your order status. Let me look that up...
 526 [Action: get_order_status invoked]
 527 Your order #12345 is currently in transit and expected to arrive tomorrow.
 528 
 529 You: [ESC to exit]
 530 
 531 Save transcript? (y/n): y
 532 Saved to: ./logs/transcript.json
 533 ```
 534 
 535 **Output Files:**
 536 
 537 When using `--output-dir`:
 538 - `transcript.json` - Conversation record
 539 - `responses.json` - Full API messages with internal details
 540 - `apex-debug.log` - Debug logs (if `--apex-debug`)
 541 
 542 ---
 543 
 544 ## Result Formats
 545 
 546 ### Human (Default)
 547 
 548 Formatted for terminal display with colors and tables.
 549 
 550 ```bash
 551 sf agent test run --api-name Test --result-format human --target-org dev
 552 ```
 553 
 554 ### JSON
 555 
 556 Machine-parseable for CI/CD pipelines.
 557 
 558 ```bash
 559 sf agent test run --api-name Test --result-format json --target-org dev
 560 ```
 561 
 562 **JSON Structure (actual format from `--result-format json --json`):**
 563 
 564 ```json
 565 {
 566   "result": {
 567     "runId": "4KBbb...",
 568     "testCases": [
 569       {
 570         "testNumber": 1,
 571         "inputs": {
 572           "utterance": "Where is my order?"
 573         },
 574         "generatedData": {
 575           "topic": "p_16jPl000000GwEX_Order_Lookup_16j8eeef13560aa",
 576           "actionsSequence": "['get_order_status']",
 577           "outcome": "I can help you track your order...",
 578           "sessionId": "uuid-string"
 579         },
 580         "testResults": [
 581           {
 582             "name": "topic_assertion",
 583             "expectedValue": "order_lookup",
 584             "actualValue": "p_16jPl000000GwEX_Order_Lookup_16j8eeef13560aa",
 585             "result": "PASS",
 586             "score": 1
 587           },
 588           {
 589             "name": "actions_assertion",
 590             "expectedValue": "['get_order_status']",
 591             "actualValue": "['get_order_status', 'summarize_record']",
 592             "result": "PASS",
 593             "score": 1
 594           },
 595           {
 596             "name": "output_validation",
 597             "expectedValue": "",
 598             "actualValue": "I can help you track your order...",
 599             "result": "FAILURE",
 600             "errorMessage": "Skip metric result due to missing expected input"
 601           }
 602         ]
 603       }
 604     ]
 605   }
 606 }
 607 ```
 608 
 609 > **Note:** `output_validation` shows `FAILURE` when `expectedOutcome` is omitted — this is **harmless**. The `topic_assertion` and `actions_assertion` results are the primary pass/fail indicators.
 610 ```
 611 
 612 ### JUnit
 613 
 614 XML format for test reporting tools.
 615 
 616 ```bash
 617 sf agent test run --api-name Test --result-format junit --output-dir ./results --target-org dev
 618 ```
 619 
 620 **JUnit Structure:**
 621 
 622 ```xml
 623 <?xml version="1.0" encoding="UTF-8"?>
 624 <testsuite name="CustomerSupportTests" tests="20" failures="2" time="45.2">
 625   <testcase name="route_to_order_lookup" classname="topic_routing" time="2.1"/>
 626   <testcase name="action_invocation_test" classname="action_invocation" time="3.2">
 627     <failure type="ACTION_NOT_INVOKED">Expected action get_order_status was not invoked</failure>
 628   </testcase>
 629 </testsuite>
 630 ```
 631 
 632 ### TAP (Test Anything Protocol)
 633 
 634 Simple text format for basic parsing.
 635 
 636 ```bash
 637 sf agent test run --api-name Test --result-format tap --target-org dev
 638 ```
 639 
 640 **TAP Output:**
 641 
 642 ```
 643 TAP version 13
 644 1..20
 645 ok 1 route_to_order_lookup
 646 ok 2 action_output_validation
 647 not ok 3 complex_order_inquiry
 648   ---
 649   message: Expected get_order_status invoked 2 times, actual 1
 650   category: ACTION_INVOCATION_COUNT_MISMATCH
 651   ...
 652 ```
 653 
 654 ---
 655 
 656 ## Common Workflows
 657 
 658 ### Workflow 1: First-Time Test Setup
 659 
 660 ```bash
 661 # 1. Generate test spec
 662 sf agent generate test-spec --output-file ./tests/my-agent-tests.yaml
 663 
 664 # 2. Edit YAML to add test cases (manual step)
 665 
 666 # 3. Create test in org
 667 sf agent test create --spec ./tests/my-agent-tests.yaml --api-name MyAgentTests --target-org dev
 668 
 669 # 4. Run tests
 670 sf agent test run --api-name MyAgentTests --wait 10 --target-org dev
 671 ```
 672 
 673 ### Workflow 2: CI/CD Pipeline
 674 
 675 ```bash
 676 # Run tests with JSON output
 677 sf agent test run --api-name MyAgentTests --wait 15 --result-format junit --output-dir ./results --target-org dev
 678 
 679 # Check exit code
 680 if [ $? -ne 0 ]; then
 681   echo "Agent tests failed"
 682   exit 1
 683 fi
 684 ```
 685 
 686 ### Workflow 3: Debug Failing Agent
 687 
 688 ```bash
 689 # 1. Run preview with debug logs
 690 sf agent preview --api-name MyAgent --use-live-actions --apex-debug --output-dir ./debug --target-org dev
 691 
 692 # 2. Analyze transcripts
 693 cat ./debug/responses.json | jq '.messages'
 694 
 695 # 3. Check debug logs
 696 cat ./debug/apex-debug.log | grep ERROR
 697 ```
 698 
 699 ---
 700 
 701 ## Error Troubleshooting
 702 
 703 | Error | Cause | Solution |
 704 |-------|-------|----------|
 705 | "Agent not found" | Agent not published | Run `sf agent publish authoring-bundle` |
 706 | "Test not found" | Test not created | Run `sf agent test create` first |
 707 | "401 Unauthorized" | Org auth expired | Re-authenticate: `sf org login web` |
 708 | "Job ID not found" | Test timed out | Use `sf agent test resume` |
 709 | "No results" | Test still running | Wait longer or use `--wait` |
 710 | **"Nonexistent flag: --use-most-recent"** | CLI bug | Use `--job-id` explicitly instead |
 711 | **Topic assertion fails** | Expected topic doesn't match actual | Standard copilots use `MigrationDefaultTopic` - update test expectations |
 712 | **"No matching records"** | Test data doesn't exist | Verify utterances reference actual org data |
 713 | **Test exists confirmation hangs** | Interactive prompt in script | Use `echo "y" \| sf agent test create...` |
 714 | **"RETRY" / "INTERNAL_SERVER_ERROR"** | Custom eval platform bug (Spring '26) | Skip custom evaluations or use Testing Center UI. See [Known Issues](#critical-custom-evaluations-retry-bug-spring-26) |
 715 | **Metric score=0 on conciseness** | `conciseness` metric broken | Skip `conciseness` metric until platform patch |
 716 | **"No enum constant AiEvaluationMetricType.INSTRUCTION_FOLLOWING_EVALUATION"** | Testing Center UI crashes when test suite includes `instruction_following` metric | Remove `- instruction_following` from YAML metrics and redeploy. CLI execution is unaffected. |
 717 
 718 ---
 719 
 720 ## ⚠️ Common Pitfalls (Lessons Learned)
 721 
 722 ### 1. Action Matching Uses Superset Logic
 723 
 724 Action assertions use **flexible superset matching**:
 725 - Expected: `[IdentifyRecordByName]`
 726 - Actual: `[IdentifyRecordByName, SummarizeRecord]`
 727 - Result: ✅ **PASS** (actual contains expected)
 728 
 729 This means tests pass if the agent invokes *at least* the expected actions, even if it invokes additional ones.
 730 
 731 ### 2. Topic Names Vary by Agent Type
 732 
 733 | Agent Type | Typical Topic Names |
 734 |------------|---------------------|
 735 | Standard Salesforce Copilot | `MigrationDefaultTopic` |
 736 | Custom Agent | Custom names you define |
 737 | Agentforce for Service | `GeneralCRM`, `OOTBSingleRecordSummary` |
 738 
 739 **Best Practice:** Run one test first, check actual topic names in results, then update expectations.
 740 
 741 ### 3. Test Data Must Exist
 742 
 743 Tests referencing specific records will fail if:
 744 - The record doesn't exist (e.g., "Acme" account)
 745 - The record name doesn't match exactly (case-sensitive)
 746 
 747 **Best Practice:** Query org for actual data before writing tests:
 748 ```bash
 749 sf data query --query "SELECT Name FROM Account LIMIT 5" --target-org dev
 750 ```
 751 
 752 ### 4. Two Fix Strategies Exist
 753 
 754 | Agent Type | Fix Strategy |
 755 |------------|--------------|
 756 | Custom Agent (you control) | Fix agent via sf-ai-agentforce |
 757 | Managed/Standard Agent | Fix test expectations in YAML |
 758 
 759 ---
 760 
 761 ## Topic Name Resolution in CLI Tests
 762 
 763 When writing `expectedTopic` in YAML specs, the format depends on the topic type:
 764 
 765 | Topic Type | YAML Value | Example |
 766 |------------|-----------|---------|
 767 | **Standard** (Escalation, Off_Topic, etc.) | `localDeveloperName` | `Escalation` |
 768 | **Promoted** (p_16j... prefix) | Full runtime `developerName` with hash | `p_16jPl000000GwEX_Topic_16j8eeef13560aa` |
 769 
 770 ### Standard Topics
 771 
 772 Standard topics like `Escalation`, `Off_Topic`, and `Inappropriate_Content` can use their short `localDeveloperName`. The CLI framework resolves these to the full hash-suffixed runtime name automatically.
 773 
 774 ```yaml
 775 # ✅ Works — framework resolves to Escalation_16j9d687a53f890
 776 - utterance: "I want to talk to a human"
 777   expectedTopic: Escalation
 778 ```
 779 
 780 ### Promoted Topics
 781 
 782 Promoted topics (custom topics created in Setup UI) have an org-specific `p_16j...` prefix and a hash suffix. You MUST use the full runtime `developerName`:
 783 
 784 ```yaml
 785 # ✅ Works — exact runtime developerName
 786 - utterance: "My doorbell camera is offline"
 787   expectedTopic: p_16jPl000000GwEX_Field_Support_Routing_16j8eeef13560aa
 788 
 789 # ❌ FAILS — localDeveloperName doesn't resolve for promoted topics
 790 - utterance: "My doorbell camera is offline"
 791   expectedTopic: Field_Support_Routing
 792 ```
 793 
 794 ### Discovery Workflow
 795 
 796 To discover actual runtime topic names:
 797 
 798 1. Run a test with best-guess topic names
 799 2. Get results: `sf agent test results --job-id <ID> --result-format json --json`
 800 3. Extract actual names: `jq '.result.testCases[].generatedData.topic'`
 801 4. Update YAML spec with actual runtime names
 802 5. Re-deploy with `--force-overwrite` and re-run
 803 
 804 See [topic-name-resolution.md](topic-name-resolution.md) for the complete guide.
 805 
 806 ---
 807 
 808 ## YAML Spec Gotchas
 809 
 810 ### `name:` Field is MANDATORY
 811 
 812 The `name:` field (becomes MasterLabel in metadata) is **required**. Without it, deploy fails:
 813 
 814 ```
 815 Error: Required fields are missing: [MasterLabel]
 816 ```
 817 
 818 ```yaml
 819 # ✅ Correct
 820 name: "My Agent Tests"
 821 subjectType: AGENT
 822 subjectName: My_Agent
 823 
 824 # ❌ Wrong — missing name: field
 825 subjectType: AGENT
 826 subjectName: My_Agent
 827 ```
 828 
 829 ### `expectedActions` is a Flat String List
 830 
 831 Action names are simple strings, NOT objects with `name`/`invoked`/`outputs`:
 832 
 833 ```yaml
 834 # ✅ Correct — flat string list
 835 expectedActions:
 836   - get_order_status
 837   - create_support_case
 838 
 839 # ❌ Wrong — object format is NOT recognized
 840 expectedActions:
 841   - name: get_order_status
 842     invoked: true
 843     outputs:
 844       - field: out_Status
 845         notNull: true
 846 ```
 847 
 848 ### Empty `expectedActions: []` Means "Not Testing"
 849 
 850 An empty list or omitted `expectedActions` means "I'm not testing action invocation for this test case" — it will PASS even if the agent invokes actions.
 851 
 852 ### Missing `expectedOutcome` Causes Harmless ERROR
 853 
 854 Omitting `expectedOutcome` causes `output_validation` to report `ERROR` status with:
 855 > "Skip metric result due to missing expected input"
 856 
 857 This is **harmless** — `topic_assertion` and `actions_assertion` still run and report correctly.
 858 
 859 ### CLI Tests Have No MessagingSession Context
 860 
 861 The CLI test framework runs without a MessagingSession. Flows that need `recordId` (e.g., from `$Context.RoutableId`) will error at runtime. The agent typically handles this gracefully by asking for the information instead.
 862 
 863 ### Do NOT Add Fabricated Fields
 864 
 865 These fields are NOT part of the CLI YAML schema and will be silently ignored or cause errors:
 866 - `apiVersion`, `kind` — not recognized
 867 - `metadata.name`, `metadata.agent` — use top-level `name:` and `subjectName:` instead
 868 - `settings.timeout`, `settings.retryCount` — not recognized
 869 - `category`, `description`, `expectedBehavior`, `expectedResponse` — not recognized by CLI
 870 
 871 ---
 872 
 873 ## Known Issues
 874 
 875 ### CRITICAL: Custom Evaluations RETRY Bug (Spring '26)
 876 
 877 **Status**: 🔴 PLATFORM BUG — Blocks all `string_comparison` / `numeric_comparison` evaluations with JSONPath
 878 
 879 **Error**: `INTERNAL_SERVER_ERROR: The specified enum type has no constant with the specified name: RETRY`
 880 
 881 **Scope**:
 882 - Server returns "RETRY" status for test cases with custom evaluations using `isReference: true`
 883 - Results API endpoint crashes with HTTP 500 when fetching results
 884 - Both filter expressions `[?(@.field == 'value')]` AND direct indexing `[0][0]` trigger the bug
 885 - Tests WITHOUT custom evaluations on the same run complete normally
 886 
 887 **Confirmed**: Direct `curl` to REST endpoint returns same 500 — NOT a CLI parsing issue
 888 
 889 **Workaround**:
 890 1. Use Testing Center UI (Setup → Agent Testing) — may display results
 891 2. Skip custom evaluations until platform patch
 892 3. Use `expectedOutcome` (LLM-as-judge) for response validation instead
 893 
 894 **Tracking**: Discovered 2026-02-09 on DevInt sandbox (Spring '26). TODO: Retest after platform patch.
 895 
 896 ### MEDIUM: `conciseness` Metric Returns Score=0
 897 
 898 **Status**: 🟡 Platform bug — metric evaluation appears non-functional
 899 
 900 **Workaround**: Skip `conciseness` in metrics lists until platform patch.
 901 
 902 ### LOW: `instruction_following` FAILURE at Score=1
 903 
 904 **Status**: 🟡 Threshold mismatch — score and label disagree
 905 
 906 **Workaround**: Use the numeric `score` value (0 or 1) for evaluation. Ignore the PASS/FAILURE label.
 907 
 908 ### HIGH: `instruction_following` Crashes Testing Center UI
 909 
 910 **Status**: 🔴 Blocks Testing Center UI entirely
 911 
 912 **Error**: `No enum constant einstein.gpt.shared.testingcenter.enums.AiEvaluationMetricType.INSTRUCTION_FOLLOWING_EVALUATION`
 913 
 914 **Scope**: Testing Center UI (Setup → Agent Testing) throws a Java exception when opening any test suite with `instruction_following` metric. CLI execution is unaffected.
 915 
 916 **Workaround**: Remove `- instruction_following` from YAML metrics, redeploy via `sf agent test create --force-overwrite`.
 917 
 918 **Discovered**: 2026-02-11.
 919 
 920 ---
 921 
 922 ## Related Commands
 923 
 924 | Command | Skill | Purpose |
 925 |---------|-------|---------|
 926 | `sf agent publish authoring-bundle` | sf-ai-agentscript | Publish agent before testing |
 927 | `sf agent validate authoring-bundle` | sf-ai-agentscript | Validate agent syntax |
 928 | `sf agent activate` | sf-ai-agentscript | Activate for preview |
 929 | `sf org login web` | - | OAuth for live preview |
