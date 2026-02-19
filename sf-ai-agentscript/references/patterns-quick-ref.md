<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Agent Script Patterns Quick Reference
   2 
   3 > Decision trees and cheat sheets for common Agent Script patterns
   4 
   5 ---
   6 
   7 ## Pattern Selection Decision Tree
   8 
   9 ### Which Architecture Pattern?
  10 
  11 ```
  12 What's your agent's purpose?
  13 │
  14 ├─► Multi-purpose (sales, support, orders)?
  15 │   └─► HUB AND SPOKE
  16 │       Central router → Specialized topics
  17 │
  18 ├─► Sequential workflow (onboarding, checkout)?
  19 │   └─► LINEAR FLOW
  20 │       A → B → C pipeline
  21 │
  22 ├─► Tiered support with escalation?
  23 │   └─► ESCALATION CHAIN
  24 │       L1 → L2 → L3 → Human
  25 │
  26 ├─► Sensitive operations (payments, PII)?
  27 │   └─► VERIFICATION GATE
  28 │       Security check → Protected topics
  29 │
  30 └─► Multiple protected topics behind shared auth gate?
  31     └─► STATE GATE (OPEN GATE)
  32         3-variable bypass with deferred routing
  33 ```
  34 
  35 ---
  36 
  37 ## Node Type Decision Tree
  38 
  39 ```
  40 What should this topic do?
  41 │
  42 ├─► Route based on intent?
  43 │   └─► 🔵 ROUTING (Topic Selector)
  44 │
  45 ├─► Security/identity check?
  46 │   └─► 🔵 VERIFICATION
  47 │
  48 ├─► Fetch external data?
  49 │   └─► 🟡 DATA-LOOKUP
  50 │
  51 ├─► Apply business rules?
  52 │   └─► 🟢 PROCESSING
  53 │
  54 └─► Transfer to human?
  55     └─► 🔴 HANDOFF
  56 ```
  57 
  58 ---
  59 
  60 ## Variable Type Decision Tree
  61 
  62 ```
  63 What kind of data is this?
  64 │
  65 ├─► State that changes during conversation?
  66 │   │   (counters, flags, accumulated data)
  67 │   └─► MUTABLE
  68 │       `failed_attempts: mutable number = 0`
  69 │
  70 └─► Data from external source?
  71     │   (session, context, CRM)
  72     └─► LINKED
  73         `customer_id: linked string`
  74         `   source: @session.customerId`
  75 ```
  76 
  77 ---
  78 
  79 ## Action Target Protocol Decision Tree
  80 
  81 ```
  82 Where should this action go?
  83 │
  84 ├─► Data queries, record updates?
  85 │   └─► flow://
  86 │
  87 ├─► Custom calculations, validation?
  88 │   └─► apex://
  89 │
  90 ├─► LLM-generated summaries?
  91 │   └─► generatePromptResponse://
  92 │
  93 ├─► Knowledge search, RAG?
  94 │   └─► retriever://
  95 │
  96 ├─► External REST APIs?
  97 │   └─► externalService://
  98 │
  99 └─► Built-in SF actions (email, tasks)?
 100     └─► standardInvocableAction://
 101 ```
 102 
 103 ---
 104 
 105 ## Deterministic vs Subjective Decision Tree
 106 
 107 ```
 108 Should this be code-enforced or LLM-flexible?
 109 │
 110 ├─► Security/safety requirement?
 111 │   └─► DETERMINISTIC (code)
 112 │
 113 ├─► Financial threshold?
 114 │   └─► DETERMINISTIC (code)
 115 │
 116 ├─► Counter/state management?
 117 │   └─► DETERMINISTIC (code)
 118 │
 119 ├─► Conversational/greeting?
 120 │   └─► SUBJECTIVE (LLM)
 121 │
 122 ├─► Context understanding needed?
 123 │   └─► SUBJECTIVE (LLM)
 124 │
 125 └─► Natural language generation?
 126     └─► SUBJECTIVE (LLM)
 127 ```
 128 
 129 ---
 130 
 131 ## SOMA Pattern Decision Tree
 132 
 133 ```
 134 Does the conversation return to original agent?
 135 │
 136 ├─► Yes, specialist handles sub-task
 137 │   └─► DELEGATION
 138 │       `@topic.specialist` (in reasoning.actions)
 139 │
 140 └─► No, permanent transfer
 141     ├─► To another topic?
 142     │   └─► HANDOFF  `@utils.transition to @topic.X`
 143     │
 144     ├─► To human?
 145     │   └─► `@utils.escalate`
 146     │
 147     └─► To another agent?
 148         └─► `@agent.X` (Connections)
 149 ```
 150 
 151 ---
 152 
 153 ## Transition Type Cheat Sheet
 154 
 155 | Syntax | Type | Control |
 156 |--------|------|---------|
 157 | `@utils.transition to @topic.X` | LLM-chosen | LLM decides when to use |
 158 | `transition to @topic.X` | Deterministic | Always executes when reached |
 159 | `@utils.escalate` | Permanent handoff | Human takeover |
 160 
 161 ---
 162 
 163 ## Instruction Resolution Order
 164 
 165 ```
 166 instructions: ->
 167    # 1. POST-ACTION CHECKS (at TOP - triggers on loop)
 168    if @variables.action_completed == True:
 169       run @actions.follow_up_action
 170       transition to @topic.next_step
 171 
 172    # 2. PRE-LLM DATA LOADING
 173    run @actions.load_required_data
 174       set @variables.data = @outputs.result
 175 
 176    # 3. DYNAMIC INSTRUCTIONS FOR LLM
 177    | Here is the context: {!@variables.data}
 178 
 179    if @variables.condition:
 180       | Do this thing.
 181    else:
 182       | Do that thing.
 183 ```
 184 
 185 **Why this order?**
 186 1. Post-action at TOP → triggers immediately on loop
 187 2. Data loading next → LLM needs current data
 188 3. Instructions last → LLM sees resolved values
 189 
 190 ---
 191 
 192 ## Common Patterns Quick Reference
 193 
 194 ### Security Gate (Early Exit)
 195 
 196 ```yaml
 197 instructions: ->
 198    if @variables.failed_attempts >= 3:
 199       | Account locked due to too many attempts.
 200       transition to @topic.lockout  # LLM never reasons
 201 ```
 202 
 203 ### Guarded Actions
 204 
 205 ```yaml
 206 actions:
 207    process_refund: @actions.process_refund
 208       description: "Issue refund"
 209       available when @variables.customer_verified == True
 210 ```
 211 
 212 ### Post-Action Follow-Up
 213 
 214 ```yaml
 215 instructions: ->
 216    if @variables.refund_status == "Approved":
 217       run @actions.create_crm_case
 218          with customer_id = @variables.customer_id
 219       transition to @topic.success
 220 ```
 221 
 222 ### Data-Dependent Instructions
 223 
 224 ```yaml
 225 instructions: ->
 226    run @actions.get_account_tier
 227       set @variables.tier = @outputs.tier
 228 
 229    if @variables.tier == "Gold":
 230       | VIP treatment - offer 20% discount.
 231    else:
 232       | Standard customer service.
 233 ```
 234 
 235 ### Open Gate (State Gate)
 236 
 237 3-variable state machine that bypasses the LLM topic selector when a gate holds focus and routes users through an auth gate before accessing protected topics.
 238 
 239 ```yaml
 240 # In topic_selector's before_reasoning — zero-credit bypass:
 241 before_reasoning:
 242    if @variables.open_gate == "protected_workflow":
 243       transition to @topic.protected_workflow
 244    if @variables.open_gate == "authentication_gate":
 245       transition to @topic.authentication_gate
 246 
 247 # In protected topic's before_reasoning — auth redirect:
 248 before_reasoning:
 249    if @variables.authenticated == False:
 250       set @variables.next_topic = "protected_workflow"
 251       set @variables.open_gate = "authentication_gate"
 252       transition to @topic.authentication_gate
 253    set @variables.open_gate = "protected_workflow"
 254 
 255 # EXIT_PROTOCOL — release gate when user changes intent:
 256 before_reasoning:
 257    set @variables.open_gate = "null"
 258    set @variables.next_topic = ""
 259    transition to @topic.topic_selector
 260 ```
 261 
 262 > **Template**: [assets/patterns/open-gate-routing.agent](../assets/patterns/open-gate-routing.agent)
 263 
 264 ---
 265 
 266 ## Anti-Patterns to Avoid
 267 
 268 ### ❌ Data Load After LLM Text
 269 
 270 ```yaml
 271 # WRONG - LLM sees empty values
 272 instructions: ->
 273    | Customer name: {!@variables.name}  # empty!
 274    run @actions.load_customer
 275       set @variables.name = @outputs.name
 276 ```
 277 
 278 ### ❌ Post-Action Check at Bottom
 279 
 280 ```yaml
 281 # WRONG - Never triggers
 282 instructions: ->
 283    | Help with refund.
 284    transition to @topic.main  # Exits first!
 285 
 286    if @variables.refund_done:  # Never reached
 287       run @actions.log_refund
 288 ```
 289 
 290 ### ❌ Mixing Tabs and Spaces
 291 
 292 ```yaml
 293 # WRONG - Compilation error
 294 config:
 295    agent_name: "MyAgent"      # 3 spaces
 296         agent_label: "Label"  # 8 spaces - FAILS!
 297 ```
 298 
 299 ### ❌ Lowercase Booleans
 300 
 301 ```yaml
 302 # WRONG - Agent Script uses Python-style
 303 is_verified: mutable boolean = true   # WRONG
 304 is_verified: mutable boolean = True   # CORRECT
 305 ```
 306 
 307 ---
 308 
 309 ## Syntax Quick Reference
 310 
 311 | Pattern | Purpose |
 312 |---------|---------|
 313 | `instructions: ->` | Arrow syntax, enables expressions |
 314 | `instructions: \|` | Pipe syntax, simple multi-line |
 315 | `if @variables.x:` | Conditional (pre-LLM) |
 316 | `run @actions.x` | Execute during resolution |
 317 | `set @var = @outputs.y` | Capture action output |
 318 | Curly-bang: {!@variables.x} | Template injection |
 319 | `available when` | Control action visibility |
 320 | `transition to @topic.x` | Deterministic topic change |
 321 | `@utils.transition to` | LLM-chosen topic change |
 322 | `@utils.escalate` | Human handoff |
 323 
 324 ---
 325 
 326 ## The 6 Deterministic Building Blocks
 327 
 328 | # | Block | Example |
 329 |---|-------|---------|
 330 | 1 | Conditionals | `if @variables.failed_attempts >= 3:` |
 331 | 2 | Topic Filters | `available when @variables.cart_items > 0` |
 332 | 3 | Variable Checks | `if @variables.churn_risk >= 80:` |
 333 | 4 | Inline Actions | `run @actions.load_customer` |
 334 | 5 | Utility Actions | `@utils.transition`, `@utils.escalate` |
 335 | 6 | Variable Injection | Curly-bang: {!@variables.customer_name} |
 336 
 337 ---
 338 
 339 ## Implementation Best Practices
 340 
 341 > Migrated from the former `sf-ai-agentforce-legacy/references/patterns-and-practices.md` on 2026-02-07.
 342 
 343 ### Pattern Details
 344 
 345 #### Lifecycle Events Pattern
 346 
 347 **File**: `assets/patterns/lifecycle-events.agent`
 348 
 349 Execute code automatically before and after every reasoning step.
 350 
 351 > **⚠️ Deployment Note**: The `run` keyword works in `reasoning.actions:` post-action blocks and `instructions: ->` blocks. It does NOT work reliably in `before_reasoning:` / `after_reasoning:` lifecycle blocks.
 352 
 353 ```agentscript
 354 topic conversation:
 355    before_reasoning:
 356       set @variables.turn_count = @variables.turn_count + 1
 357       run @actions.refresh_context                    # ⚠️ GenAiPlannerBundle only
 358          with user_id=@variables.EndUserId
 359          set @variables.context = @outputs.fresh_context
 360 
 361    reasoning:
 362       instructions: ->
 363          | Turn {!@variables.turn_count}: {!@variables.context}
 364 
 365    after_reasoning:
 366       run @actions.log_analytics                      # ⚠️ GenAiPlannerBundle only
 367          with turn=@variables.turn_count
 368 ```
 369 
 370 | ✅ Good Use Case | ❌ Not Ideal For |
 371 |------------------|------------------|
 372 | Track conversation metrics | One-time setup (use conditional) |
 373 | Refresh context every turn | Heavy processing (adds latency) |
 374 | Log analytics after each response | Actions that might fail often |
 375 
 376 #### Action Callbacks Pattern
 377 
 378 **File**: `assets/patterns/action-callbacks.agent`
 379 
 380 Chain deterministic follow-up actions using the `run` keyword.
 381 
 382 > **⚠️ Deployment Note**: The `run` keyword works in `reasoning.actions:` post-action blocks and `instructions: ->` blocks. It does NOT work reliably in `before_reasoning:` / `after_reasoning:` lifecycle blocks.
 383 
 384 ```agentscript
 385 process_order: @actions.create_order
 386    with customer_id=@variables.customer_id
 387    set @variables.order_id = @outputs.order_id
 388    run @actions.send_confirmation                    # ⚠️ GenAiPlannerBundle only
 389       with order_id=@variables.order_id
 390    run @actions.log_activity                         # ⚠️ GenAiPlannerBundle only
 391       with event="ORDER_CREATED"
 392 ```
 393 
 394 | ✅ Good Use Case | ❌ Not Ideal For |
 395 |------------------|------------------|
 396 | Audit logging (must happen) | Optional follow-ups (let LLM decide) |
 397 | Send notification after action | Complex branching logic |
 398 | Chain dependent actions | More than 1 level of nesting |
 399 
 400 **Critical Rule**: Only 1 level of `run` nesting allowed!
 401 
 402 #### Combining Patterns
 403 
 404 Patterns can be combined for complex scenarios:
 405 
 406 ```
 407 ┌─────────────────────────────────────────────────────────────┐
 408 │           LIFECYCLE + CALLBACKS + ROUTING                    │
 409 ├─────────────────────────────────────────────────────────────┤
 410 │                                                              │
 411 │  topic order_hub:                                            │
 412 │     before_reasoning:                        ◄── Lifecycle   │
 413 │        set @variables.turn_count = ... + 1                   │
 414 │                                                              │
 415 │     reasoning:                                               │
 416 │        actions:                                              │
 417 │           process: @actions.create                           │
 418 │              run @actions.notify           ◄── Callback      │
 419 │              run @actions.log                                │
 420 │                                                              │
 421 │           consult: @utils.transition       ◄── Routing       │
 422 │              to @topic.specialist                            │
 423 │                                                              │
 424 │     after_reasoning:                         ◄── Lifecycle   │
 425 │        run @actions.update_metrics                           │
 426 │                                                              │
 427 └─────────────────────────────────────────────────────────────┘
 428 ```
 429 
 430 ---
 431 
 432 ### N-ary Boolean Expressions
 433 
 434 AgentScript supports **3 or more conditions** chained with `and`/`or`:
 435 
 436 ```agentscript
 437 # Three+ conditions with AND
 438 before_reasoning:
 439    if @variables.is_authenticated and @variables.has_permission and @variables.is_active:
 440       transition to @topic.authorized
 441 
 442 # Three+ conditions with OR
 443 before_reasoning:
 444    if @variables.is_admin or @variables.is_moderator or @variables.is_owner:
 445       transition to @topic.elevated_access
 446 
 447 # In available when clauses
 448 reasoning:
 449    actions:
 450       process_return: @actions.handle_return
 451          description: "Process customer return request"
 452          available when @variables.eligible == True and @variables.order_id != None and @variables.tier != "basic"
 453 
 454       premium_action: @actions.premium_feature
 455          description: "Premium tier feature"
 456          available when @variables.tier == "premium" or @variables.tier == "enterprise" or @variables.is_trial_premium == True
 457 ```
 458 
 459 **Key Points:**
 460 - Chain as many conditions as needed with `and` or `or`
 461 - Use `()` grouping for complex expressions: `(a and b) or (c and d)`
 462 - Works in `if` statements and `available when` clauses
 463 
 464 ---
 465 
 466 ### Naming Conventions
 467 
 468 | Element | Convention | Example |
 469 |---------|------------|---------|
 470 | Agent name | PascalCase with underscores | `Customer_Service_Agent` |
 471 | Topic name | snake_case | `order_management` |
 472 | Variable name | snake_case | `user_email` |
 473 | Action name | snake_case | `get_account_details` |
 474 
 475 ---
 476 
 477 ### Variable Management Best Practices
 478 
 479 #### Initialize with Defaults
 480 
 481 ```agentscript
 482 variables:
 483     # ✅ RECOMMENDED - Has default value (clearer intent)
 484     user_name: mutable string = ""
 485         description: "Customer's full name"
 486 
 487     order_count: mutable number = 0
 488         description: "Number of orders in cart"
 489 ```
 490 
 491 > **Note**: Variables without defaults ARE supported. However, providing defaults is recommended for clarity.
 492 
 493 #### Use Appropriate Types
 494 
 495 | Data | Type | Example |
 496 |------|------|---------|
 497 | Names, IDs, text | `string` | `"John Doe"` |
 498 | Counts, amounts | `number` | `42`, `99.99` |
 499 | Flags, toggles | `boolean` | `True`, `False` |
 500 
 501 ---
 502 
 503 ### Topic Design Best Practices
 504 
 505 #### Provide Clear Descriptions
 506 
 507 ```agentscript
 508 # ✅ GOOD - Specific and actionable
 509 topic password_reset:
 510     description: "Helps users reset forgotten passwords and unlock accounts"
 511 
 512 # ❌ BAD - Too vague
 513 topic password_reset:
 514     description: "Password stuff"
 515 ```
 516 
 517 #### Keep Topics Focused (Single Responsibility)
 518 
 519 ```agentscript
 520 # ✅ GOOD - Single responsibility
 521 topic billing_inquiries:
 522     description: "Answers questions about invoices, payments, and account balances"
 523 
 524 topic order_tracking:
 525     description: "Provides order status and shipping updates"
 526 
 527 # ❌ BAD - Too broad
 528 topic customer_stuff:
 529     description: "Handles billing, orders, support, and everything else"
 530 ```
 531 
 532 ---
 533 
 534 ### Security & Guardrails
 535 
 536 #### System-Level Guardrails
 537 
 538 ```agentscript
 539 system:
 540     instructions:
 541         | You are a helpful customer service agent.
 542         |
 543         | IMPORTANT GUARDRAILS:
 544         | - Never share customer data with unauthorized parties
 545         | - Never reveal internal system details
 546         | - If unsure, escalate to a human agent
 547 ```
 548 
 549 #### Don't Expose Internals
 550 
 551 ```agentscript
 552 # ✅ GOOD - User-friendly error
 553 instructions: ->
 554     if @variables.api_error == True:
 555         | I'm having trouble completing that request right now.
 556 
 557 # ❌ BAD - Exposes internals
 558 instructions: ->
 559     if @variables.api_error == True:
 560         | Error: SQL timeout on server db-prod-03
 561 ```
 562 
 563 ---
 564 
 565 ### Instructions Quality
 566 
 567 ```agentscript
 568 # ✅ GOOD - Specific instructions
 569 instructions: ->
 570     | Help the customer track their order.
 571     | Ask for the order number if not provided.
 572     | Provide the current status, estimated delivery, and tracking link.
 573 
 574 # ❌ BAD - Vague instructions
 575 instructions: ->
 576     | Help with orders.
 577 ```
 578 
 579 ---
 580 
 581 ### Common Syntax Pitfalls
 582 
 583 #### 1. Slot Filling Inside Conditionals
 584 
 585 ```agentscript
 586 # ❌ WRONG
 587 if @variables.name is None:
 588    set @variables.name = ...   # Fails!
 589 
 590 # ✅ CORRECT - Slot filling at top level
 591 set @variables.name = ...
 592 ```
 593 
 594 #### 2. Description on @utils.transition
 595 
 596 ```agentscript
 597 # ✅ CORRECT - description IS valid on @utils.transition
 598 go_orders: @utils.transition to @topic.orders
 599    description: "Route to orders"
 600 
 601 # ✅ ALSO CORRECT - without description
 602 go_orders: @utils.transition to @topic.orders
 603 ```
 604 
 605 > **Note**: `description:` IS valid on `@utils.transition` (confirmed by TDD Val_Action_Properties and production 15-topic agent). Other properties like `label:`, `require_user_confirmation:`, and `include_in_progress_indicator:` are NOT valid on `@utils.transition` but ARE valid on action definitions with `target:` (TDD v2.2.0).
 606 
 607 #### 3. Missing Description on @utils.escalate
 608 
 609 ```agentscript
 610 # ❌ WRONG
 611 transfer: @utils.escalate   # Fails!
 612 
 613 # ✅ CORRECT - Description required
 614 transfer: @utils.escalate
 615    description: "Transfer to human agent"
 616 ```
 617 
 618 #### 4. Empty Lifecycle Blocks
 619 
 620 ```agentscript
 621 # ❌ WRONG
 622 before_reasoning:
 623    # Just a comment   # Fails!
 624 
 625 # ✅ CORRECT - Remove empty blocks or add content
 626 ```
 627 
 628 #### 5. Dynamic Action Invocation
 629 
 630 ```agentscript
 631 # ❌ WRONG
 632 invoke: {!@actions.search}   # Fails!
 633 
 634 # ✅ CORRECT - Define multiple actions, LLM auto-selects
 635 search_products: @actions.product_search
 636 search_orders: @actions.order_search
 637 ```
 638 
 639 ---
 640 
 641 ### Validation Scoring Summary
 642 
 643 | Pattern | Points | Key Requirement |
 644 |---------|--------|-----------------|
 645 | Config block | 10 | All 4 required fields |
 646 | Linked variables | 10 | EndUserId, RoutableId, ContactId |
 647 | Topic structure | 10 | label, description, reasoning |
 648 | Language block | 5 | default_locale present |
 649 | Lifecycle blocks | 5 | Proper before/after structure |
 650 | Action callbacks | 5 | No nested run |
 651 | Error handling | 5 | Validation patterns |
 652 | Template expressions | 5 | {!@variables.x} syntax |
 653 
 654 ---
 655 
 656 ### Slot Filling Reliability Patterns
 657 
 658 #### Problem: LLM Fails to Extract Values Correctly
 659 
 660 | Symptom | What Happened | Example |
 661 |---------|---------------|---------|
 662 | Empty JSON `{}` sent to action | LLM couldn't find value in conversation | User said "look up my account" without ID |
 663 | Wrong field names | LLM abbreviated or guessed | `_id` instead of `account_id` |
 664 | Wrong value extracted | LLM picked similar value from context | Picked Contact ID instead of Account ID |
 665 | Retry/crash cycles | No recovery path after failure | Agent keeps trying same extraction |
 666 
 667 **Root Cause:** The `...` syntax is **probabilistic** — the LLM infers what value to use. For critical inputs (IDs, amounts, required fields), this unreliability causes downstream failures.
 668 
 669 #### 5-Pattern Solution for Critical Inputs
 670 
 671 **Pattern 1: First-Interaction Collection** — Tell the LLM its PRIMARY GOAL:
 672 
 673 ```agentscript
 674 reasoning:
 675    instructions: ->
 676       | YOUR PRIMARY GOAL: Collect the account ID from the user.
 677       | Do NOT proceed with any other actions until account_id is captured.
 678       |
 679       if @variables.account_id == "":
 680          | ⚠️ Account ID not yet collected. ASK the user for it.
 681 ```
 682 
 683 **Pattern 2: Variable Setter Action** — Dedicated action to capture and validate:
 684 
 685 ```agentscript
 686 actions:
 687    capture_account_id:
 688       description: "Captures and validates the Salesforce Account ID from user"
 689       inputs:
 690          account_id: string
 691             description: "The 18-character Salesforce Account ID (starts with 001)"
 692             is_required: True
 693       outputs:
 694          validated_id: string
 695             description: "The validated account ID (empty if invalid)"
 696          is_valid: boolean
 697             description: "Whether the ID is valid"
 698       target: "flow://Validate_Account_Id"
 699 ```
 700 
 701 **Pattern 3: Single-Use Guard** — Make setter unavailable after capture:
 702 
 703 ```agentscript
 704 reasoning:
 705    actions:
 706       validate_id: @actions.capture_account_id
 707          with account_id=...
 708          set @variables.account_id = @outputs.validated_id
 709          set @variables.account_id_validated = @outputs.is_valid
 710          available when @variables.account_id == ""
 711 ```
 712 
 713 **Pattern 4: Null Guard Downstream Actions** — Block until validated:
 714 
 715 ```agentscript
 716 reasoning:
 717    actions:
 718       do_research: @actions.research_account
 719          with account_id=@variables.account_id
 720          available when @variables.account_id_validated == True
 721 ```
 722 
 723 **Pattern 5: Explicit Action References** — Guide the LLM:
 724 
 725 ```agentscript
 726 instructions: ->
 727    | To capture the account ID, use {!@actions.capture_account_id}.
 728    | This ensures the ID is validated before proceeding.
 729 ```
 730 
 731 #### When NOT to Use Slot Filling
 732 
 733 | Use Slot Filling (`...`) | Use Variable/Fixed Value |
 734 |--------------------------|--------------------------|
 735 | Optional, non-critical inputs | Critical IDs (account, order, case) |
 736 | User preference inputs | Values that must be validated |
 737 | One-time collection | Values used across multiple actions |
 738 | Simple text descriptions | Values with specific formats (dates, IDs) |
 739 
 740 **Decision Rule:** If invalid input would cause downstream failure, use deterministic collection.
 741 
 742 ---
 743 
 744 ### Pre-Deploy Checklist
 745 
 746 Before deploying an agent, verify:
 747 
 748 - [ ] All topics have clear descriptions
 749 - [ ] All variables have descriptions and defaults
 750 - [ ] All actions have input/output descriptions
 751 - [ ] System guardrails are defined
 752 - [ ] Error handling is in place for critical operations
 753 - [ ] Navigation back to main menu from all topics
 754 - [ ] Template expressions use correct syntax `{!@variables.name}`
 755 - [ ] Consistent indentation (tabs recommended)
