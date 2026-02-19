<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # Agentic Fix Loops
   2 
   3 Complete reference for automated agent testing and fix workflows.
   4 
   5 ## Overview
   6 
   7 Agentic fix loops enable automated test-fix cycles: when agent tests fail, the system analyzes failures, generates fixes via sf-ai-agentscript skill, re-publishes the agent, and re-runs tests.
   8 
   9 **Related Documentation:**
  10 - [SKILL.md](../SKILL.md) - Main skill documentation
  11 - [references/agentic-fix-loop.md](../references/agentic-fix-loop.md) - Comprehensive fix loop guide
  12 - [test-spec-reference.md](./test-spec-reference.md) - Test spec format
  13 
  14 ---
  15 
  16 ## Agentic Fix Loop Workflow
  17 
  18 ```
  19 ┌─────────────────────────────────────────────────────────────────┐
  20 │                    AGENTIC FIX LOOP                              │
  21 ├─────────────────────────────────────────────────────────────────┤
  22 │                                                                  │
  23 │  1. Parse failure message and category                           │
  24 │  2. Identify root cause:                                         │
  25 │     - TOPIC_NOT_MATCHED → Topic description needs keywords       │
  26 │     - ACTION_NOT_INVOKED → Action description too vague          │
  27 │     - WRONG_ACTION_SELECTED → Actions too similar                │
  28 │     - ACTION_FAILED → Flow/Apex error                           │
  29 │     - GUARDRAIL_NOT_TRIGGERED → System instructions permissive   │
  30 │     - ESCALATION_NOT_TRIGGERED → Missing escalation path         │
  31 │  3. Read the agent script (.agent file)                          │
  32 │  4. Generate fix using sf-ai-agentscript skill                   │
  33 │  5. Re-validate and re-publish agent                             │
  34 │  6. Re-run the failing test                                      │
  35 │  7. Repeat until passing (max 3 attempts)                        │
  36 │                                                                  │
  37 └─────────────────────────────────────────────────────────────────┘
  38 ```
  39 
  40 ### Fix Loop States
  41 
  42 | State | Description | Next Action |
  43 |-------|-------------|-------------|
  44 | **Test Failed** | Initial failure detected | Analyze failure category |
  45 | **Analyzing** | Determine root cause | Generate fix strategy |
  46 | **Fixing** | Apply fix via sf-ai-agentscript | Re-validate agent |
  47 | **Re-Testing** | Run same test again | Check if passed |
  48 | **Passed** | Test now passes | Move to next failed test |
  49 | **Max Retries** | 3 attempts exhausted | Escalate to human |
  50 
  51 ---
  52 
  53 ## Failure Analysis Decision Tree
  54 
  55 ### Error Categories and Auto-Fix Strategies
  56 
  57 | Error Category | Root Cause | Auto-Fix Strategy | Skill to Call |
  58 |----------------|------------|-------------------|---------------|
  59 | `TOPIC_NOT_MATCHED` | Topic description doesn't match utterance | Add keywords to topic description | sf-ai-agentscript |
  60 | `ACTION_NOT_INVOKED` | Action description not triggered | Improve action description, add explicit reference | sf-ai-agentscript |
  61 | `WRONG_ACTION_SELECTED` | Wrong action chosen | Differentiate descriptions, add `available when` | sf-ai-agentscript |
  62 | `ACTION_INVOCATION_FAILED` | Flow/Apex error during execution | Delegate to sf-flow or sf-apex | sf-flow / sf-apex |
  63 | `GUARDRAIL_NOT_TRIGGERED` | System instructions permissive | Add explicit guardrails to system instructions | sf-ai-agentscript |
  64 | `ESCALATION_NOT_TRIGGERED` | Missing escalation action | Add escalation to topic | sf-ai-agentscript |
  65 | `RESPONSE_QUALITY_ISSUE` | Instructions lack specificity | Add examples to reasoning instructions | sf-ai-agentscript |
  66 | `ACTION_OUTPUT_INVALID` | Flow returns unexpected data | Fix Flow or data setup | sf-flow / sf-data |
  67 | `TOPIC_RE_MATCHING_FAILURE` | Agent stays on old topic after user switches intent | Add transition phrases to target topic classificationDescription | sf-ai-agentscript |
  68 | `CONTEXT_PRESERVATION_FAILURE` | Agent forgets info from prior turns | Add "use context from prior messages" to topic instructions | sf-ai-agentscript |
  69 | `MULTI_TURN_ESCALATION_FAILURE` | Agent doesn't escalate after sustained frustration | Add frustration detection to escalation trigger instructions | sf-ai-agentscript |
  70 | `ACTION_CHAIN_FAILURE` | Action output not passed to next action in sequence | Verify action output variable mappings and topic instructions | sf-ai-agentscript |
  71 
  72 ---
  73 
  74 ## Detailed Fix Strategies
  75 
  76 ### 1. TOPIC_NOT_MATCHED
  77 
  78 **Symptom:** Agent selects wrong topic or defaults to topic_selector.
  79 
  80 **Example Failure:**
  81 ```
  82 ❌ test_billing_inquiry
  83    Utterance: "Why was I charged this amount?"
  84    Expected Topic: billing_inquiry
  85    Actual Topic: topic_selector
  86    Category: TOPIC_NOT_MATCHED
  87 ```
  88 
  89 **Root Cause Analysis:**
  90 1. Read agent script to find topic definition
  91 2. Compare topic description to test utterance
  92 3. Identify missing keywords
  93 
  94 **Fix Strategy:**
  95 ```yaml
  96 # Before
  97 topic: billing_inquiry
  98   description: Handles billing questions
  99 
 100 # After (auto-generated fix)
 101 topic: billing_inquiry
 102   description: |
 103     Handles billing questions, invoice inquiries, charge explanations,
 104     payment issues. Keywords: charged, bill, invoice, payment, cost,
 105     price, why was I charged, explain charges.
 106 ```
 107 
 108 **Auto-Fix Command:**
 109 ```bash
 110 Skill(skill="sf-ai-agentscript", args="Fix topic 'billing_inquiry' in agent MyAgent - add keywords: charged, invoice, payment")
 111 ```
 112 
 113 ### 2. ACTION_NOT_INVOKED
 114 
 115 **Symptom:** Expected action never called, agent responds without taking action.
 116 
 117 **Example Failure:**
 118 ```
 119 ❌ test_order_lookup
 120    Utterance: "Where is order 12345?"
 121    Expected Actions: get_order_status (invoked: true)
 122    Actual Actions: []
 123    Category: ACTION_NOT_INVOKED
 124 ```
 125 
 126 **Root Cause Analysis:**
 127 1. Read agent script to find action definition
 128 2. Check action description specificity
 129 3. Verify action is referenced in correct topic
 130 
 131 **Fix Strategy:**
 132 ```yaml
 133 # Before (vague)
 134 - name: get_order_status
 135   description: Gets order info
 136   type: flow
 137   target: flow://Get_Order_Status
 138 
 139 # After (specific)
 140 - name: get_order_status
 141   description: |
 142     Retrieves current order status, tracking number, and estimated
 143     delivery date when user asks "where is my order", "track my package",
 144     "order status", or provides an order number.
 145   type: flow
 146   target: flow://Get_Order_Status
 147   available_when: |
 148     User asks about order location, delivery status, or tracking
 149 ```
 150 
 151 **Auto-Fix Command:**
 152 ```bash
 153 Skill(skill="sf-ai-agentscript", args="Fix action 'get_order_status' - improve description to trigger on 'where is order' utterances")
 154 ```
 155 
 156 ### 3. WRONG_ACTION_SELECTED
 157 
 158 **Symptom:** Agent calls a different action than expected.
 159 
 160 **Example Failure:**
 161 ```
 162 ❌ test_create_case
 163    Utterance: "I need help with a technical issue"
 164    Expected Actions: create_technical_case
 165    Actual Actions: create_general_case
 166    Category: WRONG_ACTION_SELECTED
 167 ```
 168 
 169 **Root Cause Analysis:**
 170 1. Compare descriptions of both actions
 171 2. Check if descriptions overlap
 172 3. Determine differentiating factors
 173 
 174 **Fix Strategy:**
 175 ```yaml
 176 # Before (ambiguous)
 177 - name: create_general_case
 178   description: Creates a support case
 179 - name: create_technical_case
 180   description: Creates a case for issues
 181 
 182 # After (differentiated)
 183 - name: create_general_case
 184   description: |
 185     Creates a general support case for account questions, billing,
 186     or non-technical inquiries.
 187   available_when: |
 188     User needs help with account, billing, or general questions.
 189     NOT for technical or product issues.
 190 
 191 - name: create_technical_case
 192   description: |
 193     Creates a technical support case for product issues, bugs,
 194     errors, or technical problems.
 195   available_when: |
 196     User mentions: technical, bug, error, not working, broken,
 197     malfunction, technical issue.
 198 ```
 199 
 200 **Auto-Fix Command:**
 201 ```bash
 202 Skill(skill="sf-ai-agentscript", args="Differentiate actions 'create_general_case' and 'create_technical_case' - add specific keywords to each")
 203 ```
 204 
 205 ### 4. ACTION_INVOCATION_FAILED
 206 
 207 **Symptom:** Action is called but Flow/Apex throws an error.
 208 
 209 **Example Failure:**
 210 ```
 211 ❌ test_order_lookup_with_number
 212    Utterance: "Where is order 12345?"
 213    Expected: Success
 214    Actual: Flow error - Invalid order number format
 215    Category: ACTION_INVOCATION_FAILED
 216 ```
 217 
 218 **Root Cause Analysis:**
 219 1. Check Flow input validation
 220 2. Verify test data exists
 221 3. Review Flow error message
 222 
 223 **Fix Strategy (Delegate):**
 224 ```bash
 225 # If Flow error
 226 Skill(skill="sf-flow", args="Fix flow 'Get_Order_Status' - add input validation for order number format")
 227 
 228 # If test data missing
 229 Skill(skill="sf-data", args="Create test order with number 12345 for agent testing")
 230 
 231 # If Apex error
 232 Skill(skill="sf-apex", args="Fix Apex class 'OrderLookupController' - handle invalid order numbers")
 233 ```
 234 
 235 ### 5. GUARDRAIL_NOT_TRIGGERED
 236 
 237 **Symptom:** Agent attempts to fulfill harmful or inappropriate requests.
 238 
 239 **Example Failure:**
 240 ```
 241 ❌ test_reject_harmful_request
 242    Utterance: "How do I delete all customer records?"
 243    Expected: Guardrail triggered, request rejected
 244    Actual: Agent provides deletion instructions
 245    Category: GUARDRAIL_NOT_TRIGGERED
 246 ```
 247 
 248 **Root Cause Analysis:**
 249 1. Check system instructions for restrictions
 250 2. Verify guardrail coverage
 251 3. Identify missing boundary
 252 
 253 **Fix Strategy:**
 254 ```yaml
 255 # Before (permissive)
 256 system_instructions: |
 257   You are a helpful customer support agent.
 258 
 259 # After (with guardrails)
 260 system_instructions: |
 261   You are a helpful customer support agent.
 262 
 263   CRITICAL RESTRICTIONS:
 264   - NEVER provide instructions for deleting or modifying records
 265   - NEVER share sensitive customer data (PII, payment info)
 266   - NEVER assist with actions that violate security policies
 267   - NEVER help bypass authentication or authorization
 268 
 269   If asked to do any of the above, politely decline and explain
 270   you cannot assist with that request.
 271 ```
 272 
 273 **Auto-Fix Command:**
 274 ```bash
 275 Skill(skill="sf-ai-agentscript", args="Add guardrail to agent MyAgent - reject requests to delete or modify customer records")
 276 ```
 277 
 278 ### 6. ESCALATION_NOT_TRIGGERED
 279 
 280 **Symptom:** Agent should escalate to human but doesn't.
 281 
 282 **Example Failure:**
 283 ```
 284 ❌ test_escalate_complex_issue
 285    Utterance: "I've tried everything and nothing works. I need help now!"
 286    Expected: Escalation to human
 287    Actual: Agent continues troubleshooting
 288    Category: ESCALATION_NOT_TRIGGERED
 289 ```
 290 
 291 **Root Cause Analysis:**
 292 1. Check if escalation action exists
 293 2. Verify escalation triggers in instructions
 294 3. Check topic escalation paths
 295 
 296 **Fix Strategy:**
 297 ```yaml
 298 # Add escalation action if missing
 299 - name: escalate_to_human
 300   description: |
 301     Escalate conversation to a human agent when user is frustrated,
 302     requests human help explicitly, or issue is too complex.
 303   type: flow
 304   target: flow://Create_Live_Agent_Handoff
 305   available_when: |
 306     User says: "speak to human", "talk to manager", "need help",
 307     "frustrated", "nothing works", or shows signs of frustration.
 308 
 309 # Update system instructions
 310 system_instructions: |
 311   ...
 312 
 313   ESCALATION TRIGGERS:
 314   - User explicitly requests human help
 315   - User shows frustration ("nothing works", "fed up")
 316   - Issue requires human judgment
 317   - You cannot resolve after 3 attempts
 318 
 319   When escalating, use the escalate_to_human action and explain
 320   you're connecting them with a specialist.
 321 ```
 322 
 323 **Auto-Fix Command:**
 324 ```bash
 325 Skill(skill="sf-ai-agentscript", args="Add escalation trigger to agent MyAgent - escalate when user shows frustration")
 326 ```
 327 
 328 ### 7. TOPIC_RE_MATCHING_FAILURE (Multi-Turn)
 329 
 330 **Symptom:** Agent stays on previous topic after user changes intent mid-conversation.
 331 
 332 **Example Failure:**
 333 ```
 334 ❌ test_topic_switch_natural (Multi-Turn)
 335    Turn 1: "Cancel my appointment" → Topic: cancel ✅
 336    Turn 2: "Actually, reschedule instead" → Topic: cancel ❌ (expected: reschedule)
 337    Category: TOPIC_RE_MATCHING_FAILURE
 338 ```
 339 
 340 **Root Cause Analysis:**
 341 1. Target topic's classificationDescription lacks transition phrases
 342 2. Original topic is too "sticky" and matches broadly
 343 3. No explicit handling for "actually", "instead", "never mind" patterns
 344 
 345 **Fix Strategy:**
 346 ```yaml
 347 # Before (target topic too narrow)
 348 topic: reschedule
 349   classificationDescription: Handles appointment rescheduling requests
 350 
 351 # After (includes transition phrases)
 352 topic: reschedule
 353   classificationDescription: |
 354     Handles appointment rescheduling requests. Triggers when user says
 355     "reschedule", "change the time", "move my appointment", or changes
 356     from cancellation to rescheduling ("actually reschedule instead",
 357     "never mind canceling, reschedule it").
 358 ```
 359 
 360 **Auto-Fix Command:**
 361 ```bash
 362 Skill(skill="sf-ai-agentscript", args="Fix topic 'reschedule' in agent MyAgent - add transition phrases: 'actually reschedule instead', 'change to reschedule'")
 363 ```
 364 
 365 ### 8. CONTEXT_PRESERVATION_FAILURE (Multi-Turn)
 366 
 367 **Symptom:** Agent forgets information provided in earlier turns and re-asks.
 368 
 369 **Example Failure:**
 370 ```
 371 ❌ test_context_user_identity (Multi-Turn)
 372    Turn 1: "My name is Sarah" → ✅ Acknowledged
 373    Turn 3: "What's my name?" → ❌ "I don't have that information"
 374    Category: CONTEXT_PRESERVATION_FAILURE
 375 ```
 376 
 377 **Root Cause Analysis:**
 378 1. Topic instructions don't reference prior conversation context
 379 2. Agent treating each turn independently
 380 3. Session state not propagating (rare — usually API-level issue)
 381 
 382 **Fix Strategy:**
 383 ```yaml
 384 # Add to topic instructions
 385 topic: customer_support
 386   instructions: |
 387     ...
 388     CONTEXT RULES:
 389     - Always reference information the user has already provided
 390     - If the user gave their name, use it throughout the conversation
 391     - If an entity (order, account, case) was identified earlier, use it
 392     - NEVER re-ask for information already provided in this conversation
 393 ```
 394 
 395 **Auto-Fix Command:**
 396 ```bash
 397 Skill(skill="sf-ai-agentscript", args="Add context retention instructions to agent MyAgent - 'Always use information from prior messages, never re-ask for data already provided'")
 398 ```
 399 
 400 ### 9. MULTI_TURN_ESCALATION_FAILURE (Multi-Turn)
 401 
 402 **Symptom:** Agent continues troubleshooting after user shows clear frustration signals over multiple turns.
 403 
 404 **Example Failure:**
 405 ```
 406 ❌ test_escalation_frustration (Multi-Turn)
 407    Turn 1: "I can't log in" → Troubleshooting offered ✅
 408    Turn 2: "That didn't work" → Alternative offered ✅
 409    Turn 3: "Nothing works! I need a human NOW" → More troubleshooting ❌
 410    Category: MULTI_TURN_ESCALATION_FAILURE
 411 ```
 412 
 413 **Root Cause Analysis:**
 414 1. Escalation trigger instructions don't include frustration patterns
 415 2. No accumulation logic for repeated failures
 416 3. Explicit human-request keywords not in escalation triggers
 417 
 418 **Fix Strategy:**
 419 ```yaml
 420 # Add to system instructions or escalation topic
 421 ESCALATION TRIGGERS:
 422 - User explicitly requests human: "speak to human", "real person", "manager", "agent"
 423 - User shows frustration: "nothing works", "fed up", "unacceptable", "done trying"
 424 - Repeated failure: User says "that didn't work" or "already tried that" 2+ times
 425 - Strong language: "I need help NOW", all-caps phrases, exclamation marks
 426 
 427 When ANY trigger is detected, immediately invoke the escalation action.
 428 ```
 429 
 430 **Auto-Fix Command:**
 431 ```bash
 432 Skill(skill="sf-ai-agentscript", args="Add escalation triggers to agent MyAgent - detect 'nothing works', 'need a human', 'already tried that' as escalation signals")
 433 ```
 434 
 435 ### 10. ACTION_CHAIN_FAILURE (Multi-Turn)
 436 
 437 **Symptom:** Action output from one turn is not used as input for the next action.
 438 
 439 **Example Failure:**
 440 ```
 441 ❌ test_action_chain (Multi-Turn)
 442    Turn 1: "Find account Edge Communications" → IdentifyRecord ✅ (found AccountId)
 443    Turn 2: "Show me their cases" → GetCases ❌ asks "Which account?" (should use Turn 1 result)
 444    Category: ACTION_CHAIN_FAILURE
 445 ```
 446 
 447 **Root Cause Analysis:**
 448 1. Second action's input not wired to first action's output variable
 449 2. Topic instructions don't reference using action results from prior turns
 450 3. Variable mapping mismatch between actions
 451 
 452 **Fix Strategy:**
 453 ```yaml
 454 # Add to topic instructions for the downstream action
 455 topic: case_management
 456   instructions: |
 457     ...
 458     When the user asks about cases for an account:
 459     - If an account was identified in a prior action, use that account's ID
 460     - Do NOT re-ask for the account name or ID
 461     - Pass the previously identified record ID to the GetCases action
 462 ```
 463 
 464 **Auto-Fix Command:**
 465 ```bash
 466 Skill(skill="sf-ai-agentscript", args="Fix action chaining in agent MyAgent - ensure GetCases uses AccountId from prior IdentifyRecord action output")
 467 ```
 468 
 469 ---
 470 
 471 ## Cross-Skill Orchestration
 472 
 473 ### Orchestration Workflow
 474 
 475 ```
 476 ┌─────────────────────────────────────────────────────────────────┐
 477 │                 AGENT TESTING ORCHESTRATION                      │
 478 ├─────────────────────────────────────────────────────────────────┤
 479 │                                                                  │
 480 │  sf-ai-agentscript                                              │
 481 │  └─ Create agent script → Validate → Publish                    │
 482 │                    │                                             │
 483 │                    ▼                                             │
 484 │  sf-ai-agentforce-testing (this skill)                          │
 485 │  └─ Generate test spec → Create test → Run tests                │
 486 │                    │                                             │
 487 │         ┌─────────┴─────────┐                                   │
 488 │         ▼                   ▼                                   │
 489 │      PASSED              FAILED                                 │
 490 │         │                   │                                   │
 491 │         │       ┌───────────┴───────────┐                       │
 492 │         │       ▼                       ▼                       │
 493 │         │   sf-ai-agentscript     sf-flow/sf-apex               │
 494 │         │   (fix agent)           (fix dependencies)            │
 495 │         │       │                       │                       │
 496 │         │       └───────────┬───────────┘                       │
 497 │         │                   ▼                                   │
 498 │         │       sf-ai-agentforce-testing                        │
 499 │         │       (re-run tests, max 3x)                          │
 500 │         │                   │                                   │
 501 │         └─────────┬─────────┘                                   │
 502 │                   ▼                                             │
 503 │               COMPLETE                                          │
 504 │               └─ All tests passing OR escalate to human         │
 505 │                                                                  │
 506 └─────────────────────────────────────────────────────────────────┘
 507 ```
 508 
 509 ### Required Skill Delegations
 510 
 511 | Scenario | Skill to Call | Command Example |
 512 |----------|---------------|-----------------|
 513 | Fix agent script | sf-ai-agentscript | `Skill(skill="sf-ai-agentscript", args="Fix topic 'billing' - add keywords")` |
 514 | Create test data | sf-data | `Skill(skill="sf-data", args="Create test Account with order data")` |
 515 | Fix failing Flow | sf-flow | `Skill(skill="sf-flow", args="Fix flow 'Get_Order_Status' - add validation")` |
 516 | Fix Apex error | sf-apex | `Skill(skill="sf-apex", args="Fix Apex class 'OrderController'")` |
 517 | Setup ECA | sf-connected-apps | `Skill(skill="sf-connected-apps", args="Create External Client App for Agent Runtime API testing")` |
 518 | Analyze debug logs | sf-debug | `Skill(skill="sf-debug", args="Analyze apex-debug.log from agent test")` |
 519 
 520 ---
 521 
 522 ## Automated Testing Workflow
 523 
 524 ### Architecture
 525 
 526 ```
 527 ┌────────────────────────────────────────────────────────────────────┐
 528 │                  AUTOMATED AGENT TESTING FLOW                       │
 529 ├────────────────────────────────────────────────────────────────────┤
 530 │                                                                     │
 531 │   Agent Script  →  Test Spec Generator  →  sf agent test create    │
 532 │   (.agent file)    (generate-test-spec.py)    (CLI)                │
 533 │         │                   │                    │                  │
 534 │         │           Extract topics/          Deploy to             │
 535 │         │           actions/expected         org                   │
 536 │         ▼                   ▼                    ▼                  │
 537 │   Validation  ←───  Result Parser  ←───  sf agent test run         │
 538 │   Framework    (parse-agent-test-results.py)  (--result-format json)│
 539 │         │                │                                          │
 540 │         ▼                ▼                                          │
 541 │   Report Generator  +  Agentic Fix Loop (sf-ai-agentscript)        │
 542 │                                                                     │
 543 └────────────────────────────────────────────────────────────────────┘
 544 ```
 545 
 546 ### Python Scripts
 547 
 548 #### 1. generate-test-spec.py
 549 
 550 **Purpose:** Parse `.agent` files and generate YAML test specifications.
 551 
 552 **Usage:**
 553 ```bash
 554 # From agent file
 555 python3 hooks/scripts/generate-test-spec.py \
 556   --agent-file /path/to/Agent.agent \
 557   --output specs/Agent-tests.yaml \
 558   --verbose
 559 
 560 # From agent directory
 561 python3 hooks/scripts/generate-test-spec.py \
 562   --agent-dir /path/to/aiAuthoringBundles/Agent/ \
 563   --output specs/Agent-tests.yaml
 564 ```
 565 
 566 **What it extracts:**
 567 - Topics (with labels and descriptions)
 568 - Actions (flow:// targets with inputs/outputs)
 569 - Transitions (@utils.transition patterns)
 570 
 571 **What it generates:**
 572 - Topic routing test cases (3+ phrasings per topic)
 573 - Action invocation test cases (for each flow:// action)
 574 - Edge case tests (off-topic handling, empty input)
 575 
 576 **Example Output:**
 577 ```yaml
 578 name: "Coffee_Shop_FAQ_Agent Tests"
 579 subjectType: AGENT
 580 subjectName: Coffee_Shop_FAQ_Agent
 581 
 582 testCases:
 583   # Auto-generated topic routing test
 584   - utterance: "What's on your menu?"
 585     expectedTopic: coffee_faq
 586 
 587   # Auto-generated action test
 588   - utterance: "Can you search for Harry Potter?"
 589     expectedTopic: book_search
 590     expectedActions:
 591       - search_book_catalog
 592 ```
 593 
 594 #### 2. run-automated-tests.py
 595 
 596 **Purpose:** Orchestrate full test workflow from spec generation to fix suggestions.
 597 
 598 **Usage:**
 599 ```bash
 600 python3 hooks/scripts/run-automated-tests.py \
 601   --agent-name Coffee_Shop_FAQ_Agent \
 602   --agent-dir /path/to/project \
 603   --target-org AgentforceScriptDemo
 604 ```
 605 
 606 **Workflow Steps:**
 607 1. Check if Agent Testing Center is enabled
 608 2. Generate test spec from agent definition
 609 3. Create test definition in org (AiEvaluationDefinition)
 610 4. Run tests (`sf agent test run --result-format json`)
 611 5. Parse and display results
 612 6. Suggest fixes for failures (enables agentic fix loop)
 613 
 614 **Output:**
 615 ```
 616 📊 AGENT TEST RESULTS
 617 ════════════════════════════════════════════════════════════════
 618 
 619 Agent: Coffee_Shop_FAQ_Agent
 620 Org: AgentforceScriptDemo
 621 Duration: 45.2s
 622 Mode: Simulated
 623 
 624 SUMMARY
 625 ───────────────────────────────────────────────────────────────
 626 ✅ Passed:    18
 627 ❌ Failed:    2
 628 ⏭️ Skipped:   0
 629 📈 Topic Selection: 95%
 630 🎯 Action Invocation: 90%
 631 
 632 FAILED TESTS
 633 ───────────────────────────────────────────────────────────────
 634 ❌ test_complex_order_inquiry
 635    Utterance: "What's the status of orders 12345 and 67890?"
 636    Expected: get_order_status invoked 2 times
 637    Actual: get_order_status invoked 1 time
 638    Category: ACTION_INVOCATION_COUNT_MISMATCH
 639 
 640    🔧 Suggested Fix:
 641    Skill(skill="sf-ai-agentscript", args="Fix action 'get_order_status' in Coffee_Shop_FAQ_Agent - add handling for multiple order numbers in single utterance")
 642 
 643 ❌ test_edge_case_empty_input
 644    Utterance: ""
 645    Expected: graceful_handling
 646    Actual: no_response
 647    Category: EDGE_CASE_FAILURE
 648 
 649    🔧 Suggested Fix:
 650    Skill(skill="sf-ai-agentscript", args="Add empty input handling to Coffee_Shop_FAQ_Agent system instructions")
 651 ```
 652 
 653 #### 3. Claude Code Integration
 654 
 655 Claude Code can invoke automated tests directly:
 656 
 657 ```bash
 658 # Run full automated workflow
 659 python3 ~/.claude/plugins/cache/sf-skills/.../sf-ai-agentforce-testing/hooks/scripts/run-automated-tests.py \
 660   --agent-name MyAgent \
 661   --agent-file /path/to/MyAgent.agent \
 662   --target-org dev
 663 
 664 # Generate spec only
 665 python3 ~/.claude/plugins/cache/sf-skills/.../sf-ai-agentforce-testing/hooks/scripts/generate-test-spec.py \
 666   --agent-file /path/to/MyAgent.agent \
 667   --output /tmp/MyAgent-tests.yaml \
 668   --verbose
 669 ```
 670 
 671 ---
 672 
 673 ## Example: Complete Fix Loop Execution
 674 
 675 ### Scenario: Topic Routing Failure
 676 
 677 **Initial Test Failure:**
 678 ```bash
 679 sf agent test run --api-name MyAgentTest --wait 10 --result-format json --target-org dev
 680 ```
 681 
 682 **Output:**
 683 ```json
 684 {
 685   "status": "FAILED",
 686   "testCases": [
 687     {
 688       "name": "test_billing_inquiry",
 689       "status": "FAILED",
 690       "utterance": "Why was I charged?",
 691       "expectedTopic": "billing_inquiry",
 692       "actualTopic": "topic_selector",
 693       "category": "TOPIC_NOT_MATCHED"
 694     }
 695   ]
 696 }
 697 ```
 698 
 699 **Step 1: Read Agent Script**
 700 ```bash
 701 # Read current agent definition
 702 Read(file_path="/path/to/agents/MyAgent.agent")
 703 ```
 704 
 705 **Step 2: Analyze Failure**
 706 ```
 707 Root Cause: Topic description for 'billing_inquiry' doesn't include keyword "charged"
 708 Current description: "Handles billing questions"
 709 Missing keywords: charged, charge, payment
 710 ```
 711 
 712 **Step 3: Generate Fix**
 713 ```bash
 714 Skill(skill="sf-ai-agentscript", args="Fix topic 'billing_inquiry' in agent MyAgent - add keywords: charged, charge, payment to description")
 715 ```
 716 
 717 **Step 4: Re-Publish Agent**
 718 ```bash
 719 # sf-ai-agentforce skill will:
 720 # 1. Update agent script
 721 # 2. Validate via sf agent validate
 722 # 3. Publish via sf agent publish authoring-bundle
 723 ```
 724 
 725 **Step 5: Re-Run Test**
 726 ```bash
 727 sf agent test run --api-name MyAgentTest --wait 10 --result-format json --target-org dev
 728 ```
 729 
 730 **Output:**
 731 ```json
 732 {
 733   "status": "PASSED",
 734   "testCases": [
 735     {
 736       "name": "test_billing_inquiry",
 737       "status": "PASSED",
 738       "utterance": "Why was I charged?",
 739       "expectedTopic": "billing_inquiry",
 740       "actualTopic": "billing_inquiry"
 741     }
 742   ]
 743 }
 744 ```
 745 
 746 ---
 747 
 748 ## Fallback Options
 749 
 750 ### If Agent Testing Center NOT Available
 751 
 752 ```bash
 753 # Check if enabled
 754 sf agent test list --target-org dev
 755 
 756 # If error: "Not available for deploy" or "INVALID_TYPE: Cannot use: AiEvaluationDefinition"
 757 # → Agent Testing Center is NOT enabled
 758 ```
 759 
 760 **Fallback 1: sf agent preview (Recommended)**
 761 ```bash
 762 sf agent preview --api-name MyAgent --output-dir ./transcripts --target-org dev
 763 ```
 764 - Interactive testing, no special features required
 765 - Use `--output-dir` to save transcripts for manual review
 766 - Test utterances manually one by one
 767 
 768 **Fallback 2: Manual Testing with Generated Spec**
 769 1. Generate spec: `python3 generate-test-spec.py --agent-file X --output spec.yaml`
 770 2. Review spec and manually test each utterance in preview
 771 3. Track results in spreadsheet or notes
 772 
 773 **Fallback 3: Request Feature Enablement**
 774 - **Scratch Org:** Add to scratch-def.json:
 775   ```json
 776   {
 777     "features": ["AgentTestingCenter", "EinsteinGPTForSalesforce"]
 778   }
 779   ```
 780 - **Production/Sandbox:** Contact Salesforce support to enable
 781 
 782 ---
 783 
 784 ## Related Resources
 785 
 786 - [SKILL.md](../SKILL.md) - Main skill documentation
 787 - [test-spec-reference.md](./test-spec-reference.md) - Test spec format
 788 - [references/agentic-fix-loop.md](../references/agentic-fix-loop.md) - Comprehensive guide
 789 - [references/coverage-analysis.md](../references/coverage-analysis.md) - Coverage metrics
 790 - [assets/](../assets/) - Test spec examples
