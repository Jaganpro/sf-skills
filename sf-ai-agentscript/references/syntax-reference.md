<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Agent Script Syntax Reference
   2 
   3 > Complete syntax guide for the Agent Script DSL. Your entire agent in one `.agent` file.
   4 
   5 ---
   6 
   7 ## Design Principles
   8 
   9 | Principle | Description |
  10 |-----------|-------------|
  11 | **Declarative Over Imperative** | Describe WHAT the agent should do, not HOW step-by-step |
  12 | **Human-Readable by Design** | Syntax resembles structured English - non-engineers can read it |
  13 | **Single File Portability** | Entire agent definition in one `.agent` file - copy/paste ready |
  14 | **Version Control Friendly** | Plain text works with Git - diff, review, rollback |
  15 
  16 ---
  17 
  18 ## Block Structure
  19 
  20 ### Required Block Order
  21 
  22 ```
  23 system → config → variables → language → connections → topic → start_agent
  24 ```
  25 
  26 | Block | Required | Purpose |
  27 |-------|----------|---------|
  28 | `system:` | ✅ Yes | Global messages and instructions |
  29 | `config:` | ✅ Yes | Agent metadata and identification |
  30 | `variables:` | Optional | State management (mutable/linked) |
  31 | `language:` | Optional | Supported languages |
  32 | `connections:` | Optional | External system integrations |
  33 | `topic:` | ✅ Yes | Conversation topics (one or more) |
  34 | `start_agent:` | ✅ Yes | Entry point (exactly one) |
  35 
  36 > ✅ **Validated Finding**: Documentation implies strict ordering, but both config-first and system-first orderings compile. Pick one convention and be consistent.
  37 
  38 ---
  39 
  40 ## Block Definitions
  41 
  42 ### 1. system: Block (Required)
  43 
  44 ```yaml
  45 system:
  46   messages:
  47     welcome: "Hello! How can I help?"
  48     error: "Sorry, something went wrong."
  49   instructions: "You are a helpful assistant."
  50 ```
  51 
  52 | Field | Purpose |
  53 |-------|---------|
  54 | `messages.welcome` | Initial greeting message |
  55 | `messages.error` | Fallback error message |
  56 | `instructions` | Global system prompt for the agent |
  57 
  58 ---
  59 
  60 ### 2. config: Block (Required)
  61 
  62 ```yaml
  63 config:
  64   developer_name: "refund_agent"
  65   agent_description: "Handles refund requests"
  66   agent_type: "AgentforceServiceAgent"
  67   default_agent_user: "admin@yourorg.com"
  68 ```
  69 
  70 | Field | Required | Purpose |
  71 |-------|----------|---------|
  72 | `developer_name` | ✅ Yes | Internal identifier (must match folder name, case-sensitive) |
  73 | `agent_description` | ✅ Yes | Agent's purpose description |
  74 | `agent_type` | ✅ Yes | `AgentforceServiceAgent` or `AgentforceEmployeeAgent` |
  75 | `default_agent_user` | ⚠️ **REQUIRED** | Must be valid Einstein Agent User |
  76 
  77 > ⚠️ **Critical**: `default_agent_user` must exist in the org with the "Einstein Agent User" profile. Query: `SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true`
  78 
  79 ---
  80 
  81 ### 3. variables: Block (Optional)
  82 
  83 ```yaml
  84 variables:
  85   # Mutable: State we track and modify
  86   failed_attempts: mutable number = 0
  87   customer_verified: mutable boolean = False
  88   order_ids: mutable list[string] = []
  89 
  90   # Linked: Read-only from external sources
  91   session_id: linked string
  92     source: @session.sessionID
  93     description: "Current session identifier"
  94   customer_id: linked string
  95     source: @context.customerId
  96     description: "Customer ID from context"
  97 ```
  98 
  99 #### Variable Types
 100 
 101 | Type | Description | Example |
 102 |------|-------------|---------|
 103 | `string` | Text values | `name: mutable string = ""` |
 104 | `number` | Numeric values | `count: mutable number = 0` |
 105 | `boolean` | True/false flags | `verified: mutable boolean = False` |
 106 | `object` | Structured data | `data: mutable object = {}` |
 107 | `date` | Calendar dates | `created: mutable date` |
 108 | `timestamp` | Date and time | `updated: mutable timestamp` |
 109 | `currency` | Money values | `amount: mutable currency` |
 110 | `id` | Unique identifiers | `record_id: mutable id` |
 111 | `list[T]` | Arrays of type T | `items: mutable list[string] = []` |
 112 
 113 #### Variable Modifiers
 114 
 115 | Modifier | Behavior | Use Case |
 116 |----------|----------|----------|
 117 | `mutable` | Read/write - can be changed during conversation | Counters, flags, accumulated state |
 118 | `linked` | Read-only - populated from external source | Session IDs, user profiles, context data |
 119 
 120 > ⚠️ **Booleans are capitalized**: Use `True`/`False`, not `true`/`false`
 121 
 122 ---
 123 
 124 ### 4. language: Block (Optional)
 125 
 126 ```yaml
 127 language:
 128   default: "en_US"
 129   supported: ["en_US", "es_ES", "fr_FR"]
 130 ```
 131 
 132 ---
 133 
 134 ### 5. connections: Block (Optional)
 135 
 136 ```yaml
 137 connections:
 138   crm_system:
 139     type: "http"
 140     credential: "CRM_Named_Credential"
 141     base_url: "https://api.example.com/v1"
 142 ```
 143 
 144 #### Connection Types
 145 
 146 | Type | Label | Purpose |
 147 |------|-------|---------|
 148 | `http` | API | External REST/SOAP services via Named Credentials |
 149 | `dataCloud` | DATACLOUD | Customer 360 data for personalization |
 150 | `mulesoft` | MULESOFT | Enterprise integrations and API orchestration |
 151 | `flow` | FLOW | Salesforce automation and internal data |
 152 
 153 ---
 154 
 155 ### 6. topic: Block (Required - one or more)
 156 
 157 ```yaml
 158 topic main:
 159   description: "Main conversation handler"
 160   reasoning:
 161     instructions: |
 162       Help the user with their request.
 163     actions:
 164       do_something: @actions.my_action
 165         description: "Action description"
 166 ```
 167 
 168 | Field | Purpose |
 169 |-------|---------|
 170 | `description` | Helps LLM understand topic purpose |
 171 | `reasoning.instructions` | Instructions for this topic |
 172 | `reasoning.actions` | Available actions in this topic |
 173 
 174 ---
 175 
 176 ### 7. start_agent: Block (Required - exactly one)
 177 
 178 ```yaml
 179 start_agent entry:
 180   description: "Entry point for conversations"
 181   reasoning:
 182     instructions: |
 183       Greet the user and route appropriately.
 184     actions:
 185       go_main: @utils.transition to @topic.main
 186         description: "Navigate to main topic"
 187 ```
 188 
 189 > 💡 The name can be anything - "main", "entry", "topic_selector" - just be consistent.
 190 
 191 ---
 192 
 193 ## Instruction Syntax
 194 
 195 ### Pipe vs Arrow Syntax
 196 
 197 | Syntax | Use When | Example |
 198 |--------|----------|---------|
 199 | `instructions: \|` | Simple multi-line text (no expressions) | `instructions: \| Help the user.` |
 200 | `instructions: ->` | Complex logic with conditionals/actions | `instructions: -> if @variables.x:` |
 201 
 202 ### Arrow Syntax (`->`) Patterns
 203 
 204 ```yaml
 205 reasoning:
 206   instructions: ->
 207     # Conditional (resolves BEFORE LLM)
 208     if @variables.customer_verified == True:
 209       | Welcome back, verified customer!
 210     else:
 211       | Please verify your identity first.
 212 
 213     # Inline action execution
 214     run @actions.load_customer
 215       with customer_id = @variables.customer_id
 216       set @variables.customer_data = @outputs.data
 217 
 218     # Variable injection in text
 219     | Customer name: {!@variables.customer_name}
 220 
 221     # Deterministic transition
 222     if @variables.failed_attempts >= 3:
 223       transition to @topic.escalation
 224 ```
 225 
 226 ### Instruction Syntax Elements
 227 
 228 | Element | Syntax | Purpose |
 229 |---------|--------|---------|
 230 | Literal text | `\| text` | Text that becomes part of LLM prompt |
 231 | Conditional | `if @variables.x:` | Resolves before LLM sees instructions |
 232 | Else clause | `else:` | Alternative path |
 233 | Inline action | `run @actions.x` | Execute action during resolution |
 234 | Set variable | `set @var = @outputs.y` | Capture action output |
 235 | Template injection | Curly-bang syntax: {!@variables.x} | Insert variable value into text |
 236 | Deterministic transition | `transition to @topic.x` | Change topic without LLM |
 237 
 238 ---
 239 
 240 ## Action Configuration
 241 
 242 ### Action Declaration
 243 
 244 ```yaml
 245 actions:
 246   action_name: @actions.my_action
 247     description: "What this action does"
 248     with input_param = @variables.some_value
 249     set @variables.result = @outputs.output_field
 250     available when @variables.is_authorized == True
 251 ```
 252 
 253 ### Action Metadata Properties (TDD Validated v2.2.0)
 254 
 255 Action definitions with `target:` support the following metadata properties. These are NOT valid on `@utils.transition` utility actions.
 256 
 257 **Action-Level:**
 258 
 259 | Property | Type | Context | Notes |
 260 |----------|------|---------|-------|
 261 | `label` | String | Action def, topic, I/O | Display name in UI |
 262 | `description` | String | Action def, I/O | LLM decision-making context |
 263 | `require_user_confirmation` | Boolean | Action def | Compiles; runtime no-op (Issue 6) |
 264 | `include_in_progress_indicator` | Boolean | Action def | Shows spinner during execution |
 265 | `progress_indicator_message` | String | Action def | Custom spinner text |
 266 
 267 **Input-Level:**
 268 
 269 | Property | Type | Notes |
 270 |----------|------|-------|
 271 | `is_required` | Boolean | Marks input as mandatory |
 272 | `is_user_input` | Boolean | LLM extracts from conversation |
 273 | `label` | String | Display name |
 274 | `description` | String | LLM context |
 275 | `complex_data_type_name` | String | Lightning type mapping |
 276 
 277 **Output-Level:**
 278 
 279 | Property | Type | Notes |
 280 |----------|------|-------|
 281 | `is_displayable` | Boolean | `False` = hide from user (alias: `filter_from_agent`) |
 282 | `is_used_by_planner` | Boolean | `True` = LLM can reason about value |
 283 | `label` | String | Display name |
 284 | `description` | String | LLM context |
 285 | `complex_data_type_name` | String | Lightning type mapping |
 286 
 287 ---
 288 
 289 ### Two-Level Action System
 290 
 291 Agent Script uses a two-level system for actions. Understanding this distinction is critical:
 292 
 293 ```
 294 Level 1: ACTION DEFINITION (in topic's `actions:` block)
 295    → Has `target:`, `inputs:`, `outputs:`, `description:`
 296    → Specifies WHAT to call (e.g., "flow://GetOrderStatus")
 297 
 298 Level 2: ACTION INVOCATION (in `reasoning.actions:` block)
 299    → References Level 1 via `@actions.name`
 300    → Specifies HOW to call it (`with`, `set` clauses)
 301    → Does NOT use `inputs:`/`outputs:` (use `with`/`set` instead)
 302 ```
 303 
 304 **Complete Example:**
 305 ```yaml
 306 topic order_lookup:
 307    description: "Look up order details"
 308 
 309    # Level 1: DEFINE the action (with target + I/O schemas)
 310    actions:
 311       get_order:
 312          description: "Retrieves order information by ID"
 313          inputs:
 314             order_id: string
 315                description: "Customer's order number"
 316          outputs:
 317             status: string
 318                description: "Current order status"
 319          target: "flow://Get_Order_Details"
 320 
 321    reasoning:
 322       instructions: |
 323          Help the customer check their order status.
 324       # Level 2: INVOKE the action (with/set, NOT inputs/outputs)
 325       actions:
 326          lookup: @actions.get_order
 327             with order_id = ...
 328             set @variables.order_status = @outputs.status
 329 ```
 330 
 331 > ⚠️ **I/O schemas are REQUIRED for publish**: Action definitions with only `description:` and `target:` (no `inputs:`/`outputs:`) will PASS LSP and CLI validation but FAIL server-side compilation with "Internal Error." Always include complete I/O schemas in Level 1 definitions.
 332 
 333 ---
 334 
 335 ### Lifecycle Hooks: `before_reasoning:` and `after_reasoning:`
 336 
 337 Lifecycle hooks enable deterministic pre/post-processing around LLM reasoning. They are FREE (no credit cost).
 338 
 339 ```yaml
 340 topic main:
 341    description: "Topic with lifecycle hooks"
 342 
 343    # BEFORE: Runs deterministically BEFORE LLM sees instructions
 344    before_reasoning:
 345       # Content goes DIRECTLY here (NO instructions: wrapper!)
 346       set @variables.turn_count = @variables.turn_count + 1
 347       if @variables.needs_redirect == True:
 348          transition to @topic.redirect
 349 
 350    # LLM reasoning phase
 351    reasoning:
 352       instructions: ->
 353          | Turn {!@variables.turn_count}: How can I help?
 354 
 355    # AFTER: Runs deterministically AFTER LLM finishes reasoning
 356    after_reasoning:
 357       # Content goes DIRECTLY here (NO instructions: wrapper!)
 358       set @variables.interaction_logged = True
 359 ```
 360 
 361 **Key Rules:**
 362 - Content goes **directly** under the block (NO `instructions:` wrapper)
 363 - Supports `set`, `if`, `transition` statements
 364 - `run` does NOT work reliably in lifecycle blocks (use it in `reasoning.actions:` or `instructions: ->` instead)
 365 - Both hooks are FREE (no credit cost) — use for data prep, logging, cleanup
 366 
 367 ---
 368 
 369 ### Action Target Protocols
 370 
 371 **Core Targets (Validated)**
 372 
 373 | Protocol | Use When | Status |
 374 |----------|----------|--------|
 375 | `flow://` | Data operations, business logic | ✅ Validated |
 376 | `apex://` | Custom calculations, validation | ✅ Validated |
 377 | `generatePromptResponse://` | Grounded LLM responses | ✅ Validated |
 378 | `api://` | REST API callouts | ✅ Validated |
 379 | `retriever://` | RAG knowledge search | ✅ Validated |
 380 | `externalService://` | Third-party APIs via Named Credential | ✅ Validated |
 381 | `standardInvocableAction://` | Built-in SF actions | ✅ Validated |
 382 
 383 **Additional Targets (From agent-script-recipes)**
 384 
 385 | Protocol | Use When | Status |
 386 |----------|----------|--------|
 387 | `datacloudDataGraphAction://` | Data Cloud graph queries | ⚠️ Untested |
 388 | `datacloudSegmentAction://` | Data Cloud segment operations | ⚠️ Untested |
 389 | `triggerByKnowledgeSource://` | Knowledge-triggered actions | ⚠️ Untested |
 390 | `contextGrounding://` | Context grounding operations | ⚠️ Untested |
 391 | `predictiveAI://` | Einstein predictions | ⚠️ Untested |
 392 | `runAction://` | Sub-action execution | ⚠️ Untested |
 393 | `external://` | External services | ⚠️ Untested |
 394 | `copilotAction://` | Copilot actions | ⚠️ Untested |
 395 | `@topic.X` | Topic delegation (supervision) | ✅ Validated |
 396 
 397 > **Note**: Untested targets are documented in the official AGENT_SCRIPT.md rules. They may require specific licenses, org configurations, or future API versions.
 398 
 399 ### Utility Actions
 400 
 401 | Action | Purpose | Example |
 402 |--------|---------|---------|
 403 | `@utils.transition to @topic.x` | LLM-chosen topic navigation | `go_main: @utils.transition to @topic.main` |
 404 | `@utils.escalate` | Hand off to human agent | `escalate: @utils.escalate` |
 405 | `@utils.setVariables` | Set multiple variables | `set_vars: @utils.setVariables` |
 406 
 407 ---
 408 
 409 ## Resource References
 410 
 411 | Syntax | Purpose | Example |
 412 |--------|---------|---------|
 413 | `@variables.x` | Reference a variable | `@variables.customer_id` |
 414 | `@actions.x` | Reference an action | `@actions.process_refund` |
 415 | `@topic.x` | Reference a topic | `@topic.escalation` |
 416 | `@outputs.x` | Reference action output | `@outputs.status` |
 417 | `@session.x` | Reference session data | `@session.sessionID` |
 418 | `@context.x` | Reference context data | `@context.userProfile` |
 419 
 420 ---
 421 
 422 ## Whitespace Rules
 423 
 424 ### Indentation
 425 
 426 | ✅ CORRECT | ❌ INCORRECT |
 427 |------------|-------------|
 428 | 2-space consistent | Mixed tabs and spaces |
 429 | 3-space consistent | Inconsistent spacing |
 430 | Tabs consistent | Tab in one block, spaces in another |
 431 
 432 > **CRITICAL**: Never mix tabs and spaces in the same file. This causes compilation errors.
 433 
 434 ### Boolean Values
 435 
 436 | ✅ CORRECT | ❌ INCORRECT |
 437 |------------|-------------|
 438 | `True` | `true` |
 439 | `False` | `false` |
 440 
 441 ---
 442 
 443 ## Complete Example
 444 
 445 ```yaml
 446 system:
 447   messages:
 448     welcome: "Welcome to Pronto Support!"
 449     error: "Sorry, something went wrong. Let me connect you with a human."
 450   instructions: "You are a helpful customer service agent for Pronto Delivery."
 451 
 452 config:
 453   developer_name: "pronto_refund_agent"
 454   agent_description: "Handles customer refund requests with churn risk assessment"
 455   agent_type: "AgentforceServiceAgent"
 456   default_agent_user: "agent_user@myorg.com"
 457 
 458 variables:
 459   # Mutable state
 460   customer_verified: mutable boolean = False
 461   failed_attempts: mutable number = 0
 462   churn_risk_score: mutable number = 0
 463   refund_status: mutable string = ""
 464 
 465   # Linked from session
 466   customer_id: linked string
 467     source: @session.customerId
 468     description: "Customer ID from messaging session"
 469 
 470 topic identity_verification:
 471   description: "Verify customer identity before refund processing"
 472   reasoning:
 473     instructions: ->
 474       if @variables.failed_attempts >= 3:
 475         | Too many failed attempts. Escalating to human agent.
 476         transition to @topic.escalation
 477 
 478       if @variables.customer_verified == True:
 479         | Identity verified. Proceeding to refund assessment.
 480         transition to @topic.refund_processor
 481 
 482       | Please verify your identity by providing your email address.
 483     actions:
 484       verify: @actions.verify_customer
 485         description: "Verify customer by email"
 486         set @variables.customer_verified = @outputs.verified
 487 
 488 topic refund_processor:
 489   description: "Process refund based on churn risk assessment"
 490   reasoning:
 491     instructions: ->
 492       # Post-action check (triggers on loop after refund)
 493       if @variables.refund_status == "Approved":
 494         run @actions.create_crm_case
 495           with customer_id = @variables.customer_id
 496         transition to @topic.success
 497 
 498       # Pre-LLM: Load churn data
 499       run @actions.get_churn_score
 500         with customer_id = @variables.customer_id
 501         set @variables.churn_risk_score = @outputs.score
 502 
 503       # Dynamic instructions based on score
 504       | Customer churn risk: {!@variables.churn_risk_score}%
 505 
 506       if @variables.churn_risk_score >= 80:
 507         | HIGH RISK - Offer full cash refund to retain customer.
 508       else:
 509         | LOW RISK - Offer $10 store credit as goodwill.
 510     actions:
 511       process_refund: @actions.process_refund
 512         description: "Issue the refund"
 513         available when @variables.customer_verified == True
 514         set @variables.refund_status = @outputs.status
 515 
 516 topic escalation:
 517   description: "Escalate to human agent"
 518   reasoning:
 519     instructions: |
 520       Apologize for the inconvenience and transfer to a human agent.
 521     actions:
 522       handoff: @utils.escalate
 523         description: "Transfer to live support"
 524 
 525 topic success:
 526   description: "Successful refund confirmation"
 527   reasoning:
 528     instructions: |
 529       Thank the customer and confirm their refund has been processed.
 530 
 531 start_agent topic_selector:
 532   description: "Entry point - route to identity verification"
 533   reasoning:
 534     instructions: |
 535       Greet the customer and begin identity verification.
 536     actions:
 537       start: @utils.transition to @topic.identity_verification
 538         description: "Begin refund process"
 539 ```
 540 
 541 ---
 542 
 543 ## Expression Operators
 544 
 545 ### Comparison Operators
 546 
 547 | Operator | Description | Example |
 548 |----------|-------------|---------|
 549 | `==` | Equal to | `if @variables.status == "active":` |
 550 | `!=` | Not equal to | `if @variables.status != "closed":` |
 551 | `<` | Less than | `if @variables.count < 10:` |
 552 | `<=` | Less than or equal | `if @variables.count <= 5:` |
 553 | `>` | Greater than | `if @variables.risk > 80:` |
 554 | `>=` | Greater than or equal | `if @variables.attempts >= 3:` |
 555 | `is` | Identity check | `if @variables.data is None:` |
 556 | `is not` | Negated identity check | `if @variables.data is not None:` |
 557 
 558 > **Note**: Use `!=` for not-equal comparisons. The `<>` operator does NOT compile (TDD validated v1.9.0).
 559 
 560 ### Logical Operators
 561 
 562 | Operator | Description | Example |
 563 |----------|-------------|---------|
 564 | `and` | Logical AND | `if @variables.verified == True and @variables.active == True:` |
 565 | `or` | Logical OR | `if @variables.status == "open" or @variables.status == "pending":` |
 566 | `not` | Logical NOT | `if not @variables.blocked:` |
 567 
 568 ### Arithmetic Operators
 569 
 570 | Operator | Description | Example |
 571 |----------|-------------|---------|
 572 | `+` | Addition | `set @variables.count = @variables.count + 1` |
 573 | `-` | Subtraction | `set @variables.remaining = @variables.total - @variables.used` |
 574 
 575 > ⚠️ **NOT supported**: `*` (multiplication), `/` (division), `%` (modulo). For complex arithmetic, use a Flow or Apex action.
 576 
 577 ### Access Operators
 578 
 579 | Operator | Description | Example |
 580 |----------|-------------|---------|
 581 | `.` | Property access | `@outputs.result.status` |
 582 | `[]` | Index access | `@variables.items[0]` |
 583 
 584 ### Conditional Expression (Ternary-like)
 585 
 586 ```yaml
 587 | Status: {!@variables.status if @variables.status else "pending"}
 588 ```
 589 
 590 ### Expression Limitations (Sandboxed Python AST Subset)
 591 
 592 Agent Script expressions use a sandboxed subset of Python. Not all Python operations are available.
 593 
 594 **Supported:**
 595 
 596 | Category | Operations |
 597 |----------|-----------|
 598 | Arithmetic | `+`, `-` |
 599 | Comparison | `==`, `!=`, `<`, `<=`, `>`, `>=`, `is`, `is not` |
 600 | Logical | `and`, `or`, `not` |
 601 | Ternary | `x if condition else y` |
 602 | Built-in functions | `len()`, `max()`, `min()` |
 603 | Attribute access | `@outputs.result.field` |
 604 | Index access | `@variables.items[0]` |
 605 | String methods | `contains`, `startswith`, `endswith` |
 606 
 607 **NOT Supported:**
 608 
 609 | Operation | Workaround |
 610 |-----------|-----------|
 611 | Multiplication (`*`) | Use Flow/Apex action |
 612 | Division (`/`) | Use Flow/Apex action |
 613 | Modulo (`%`) | Use Flow/Apex action |
 614 | String concatenation (`+` on strings) | Use `{!var1}{!var2}` template injection |
 615 | List slicing (`items[1:3]`) | Use Flow to extract sublist |
 616 | List comprehensions (`[x for x in ...]`) | Use Flow/Apex for list transformation |
 617 | Lambda expressions | Use Flow/Apex action |
 618 | `for`/`while` loops | Use topic loop pattern (re-entry) |
 619 | `import` statements | Not available (security sandbox) |
 620 
 621 ### Apex Complex Type Notation
 622 
 623 When action inputs or outputs reference Apex inner classes, use the `@apexClassType` notation:
 624 
 625 ```
 626 @apexClassType/c__OuterClass$InnerClass
 627 ```
 628 
 629 | Component | Description | Example |
 630 |-----------|-------------|---------|
 631 | `@apexClassType/` | Required prefix | — |
 632 | `c__` | Default namespace (or your package namespace) | `c__`, `myns__` |
 633 | `OuterClass` | The containing Apex class | `OrderService` |
 634 | `$` | Inner class separator | — |
 635 | `InnerClass` | The inner class name | `LineItem` |
 636 
 637 **Example:**
 638 ```yaml
 639 actions:
 640    process_order:
 641       inputs:
 642          line_items: list[object]
 643             complex_data_type_name: "@apexClassType/c__OrderService$LineItem"
 644       target: "apex://OrderService"
 645 ```
 646 
 647 > **Note**: This notation is used in the `complex_data_type_name` field of action input/output definitions in Agentforce Assets, not in the `.agent` file directly.
 648 
 649 ---
 650 
 651 ## Common Pitfalls
 652 
 653 | Pitfall | Symptom | Fix |
 654 |---------|---------|-----|
 655 | Mixed tabs/spaces | `SyntaxError: cannot mix` | Use consistent indentation |
 656 | Invalid boolean | Type mismatch | Use `True`/`False` (capitalized) |
 657 | Spaces in variable names | Parse error | Use `snake_case` |
 658 | Mutable + linked | Conflicting modifiers | Choose one modifier |
 659 | Missing `source:` for linked | Variable empty | Add `source: @session.X` |
 660 | Missing `default_agent_user` | Internal error on deploy | Add valid Einstein Agent User |
