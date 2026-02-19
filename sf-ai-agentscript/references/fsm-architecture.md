<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # FSM Architecture Guide
   2 
   3 > Design agent behavior as a finite state machine with deterministic nodes and explicit transitions.
   4 
   5 ---
   6 
   7 ## Why FSM Architecture?
   8 
   9 ### The Problem with Prompt-Only Agents
  10 
  11 | Anti-Pattern | Description |
  12 |--------------|-------------|
  13 | **ReAct Pattern** | Agents get stuck in reasoning loops without guardrails |
  14 | **Doom-Prompting** | Prompts grow exponentially to handle edge cases |
  15 | **Goal Drift** | Agents forget original intent after several turns |
  16 
  17 > **KEY INSIGHT**: "LLMs are non-deterministic by design. Without structured control flow, enterprise agents become unpredictable, expensive, and impossible to debug."
  18 
  19 ### The FSM Solution
  20 
  21 | FSM Concept | Traffic Light Example | Agent Benefit |
  22 |-------------|----------------------|---------------|
  23 | **States** | Red, Green, Yellow | Agent always knows exactly what it's doing |
  24 | **Transitions** | Timer expires | No ambiguity about what happens next |
  25 | **Determinism** | Red → Green (guaranteed) | Auditable, testable, trustworthy |
  26 
  27 ---
  28 
  29 ## The Three FSM Pillars
  30 
  31 | Pillar | Definition | Agent Benefit |
  32 |--------|------------|---------------|
  33 | **States** | Distinct "modes" the system can be in | Clear context at any moment |
  34 | **Transitions** | Explicit rules for moving between states | Defined paths, no surprises |
  35 | **Determinism** | Same input → same output | Auditable and testable |
  36 
  37 ---
  38 
  39 ## The 5 Node Patterns
  40 
  41 ### Pattern Overview
  42 
  43 | Pattern | Color | Purpose |
  44 |---------|-------|---------|
  45 | 🔵 **ROUTING** | Blue | Routes based on intent |
  46 | 🔵 **VERIFICATION** | Light Blue | Security checks |
  47 | 🟡 **DATA-LOOKUP** | Yellow | External data fetch |
  48 | 🟢 **PROCESSING** | Green | Business logic |
  49 | 🔴 **HANDOFF** | Red | Human escalation |
  50 
  51 ---
  52 
  53 ### Pattern 1: ROUTING (Topic Selector)
  54 
  55 **Purpose**: Routes conversations based on detected intent
  56 
  57 ```yaml
  58 start_agent topic_selector:
  59   description: "Route to appropriate topic based on intent"
  60   reasoning:
  61     instructions: ->
  62       | You are the support agent.
  63         Classify the customer's intent and route:
  64         - Refund requests go to identity verification
  65         - General inquiries are handled directly
  66     actions:
  67       start_refund: @utils.transition to @topic.identity_verification
  68         description: "Customer wants a refund"
  69       handle_inquiry: @utils.transition to @topic.general_support
  70         description: "General question or inquiry"
  71 ```
  72 
  73 **When to Use**: Entry point for multi-purpose agents
  74 
  75 ---
  76 
  77 ### Pattern 2: VERIFICATION (Identity Gate)
  78 
  79 **Purpose**: Enforces security checks before proceeding
  80 
  81 ```yaml
  82 topic identity_verification:
  83   description: "Verify customer identity before refund"
  84   reasoning:
  85     instructions: ->
  86       if @variables.failed_attempts >= 3:
  87         | Too many failed attempts. Escalating to human agent.
  88       if @variables.email_verified == True:
  89         | Identity verified. Proceed to risk assessment.
  90       else:
  91         | Ask customer to verify their email address.
  92     actions:
  93       verify_email: @actions.verify_email
  94         description: "Verify customer email"
  95         with email = @variables.customer_email
  96         set @variables.email_verified = @outputs.verified
  97       proceed: @utils.transition to @topic.risk_assessment
  98         description: "Continue to risk assessment"
  99         available when @variables.email_verified == True
 100       escalate: @utils.escalate
 101         description: "Transfer to human agent"
 102         available when @variables.failed_attempts >= 3
 103 ```
 104 
 105 **When to Use**: Before accessing sensitive data or actions
 106 
 107 ---
 108 
 109 ### Pattern 3: DATA-LOOKUP (Risk Assessment)
 110 
 111 **Purpose**: Fetches data from external sources
 112 
 113 ```yaml
 114 topic risk_assessment:
 115   description: "Fetch customer data and assess churn risk"
 116   reasoning:
 117     instructions: ->
 118       | Fetch customer profile using the action.
 119         Once loaded, review:
 120         - Churn Risk: {!@variables.churn_risk_score}%
 121         - Lifetime Value: {!@variables.lifetime_value}
 122     actions:
 123       get_profile: @actions.get_customer_profile
 124         description: "Load customer data from CRM"
 125         with customer_id = @variables.customer_id
 126         set @variables.churn_risk_score = @outputs.churn_risk
 127         set @variables.lifetime_value = @outputs.ltv
 128       process_refund: @utils.transition to @topic.refund_processor
 129         description: "Continue to refund processing"
 130 ```
 131 
 132 **When to Use**: When decisions require external data
 133 
 134 ---
 135 
 136 ### Pattern 4: PROCESSING (Refund Processor)
 137 
 138 **Purpose**: Applies business logic based on conditions
 139 
 140 ```yaml
 141 topic refund_processor:
 142   description: "Process refund based on churn risk"
 143   reasoning:
 144     instructions: ->
 145       if @variables.churn_risk_score >= 80:
 146         | HIGH CHURN RISK - Approve full refund.
 147       if @variables.churn_risk_score < 80:
 148         | LOW CHURN RISK - Offer partial credit.
 149     actions:
 150       approve_full: @actions.process_refund
 151         available when @variables.churn_risk_score >= 80
 152         with amount = @variables.order_total
 153         with type = "full"
 154       offer_credit: @actions.issue_credit
 155         available when @variables.churn_risk_score < 80
 156         with amount = 10
 157 ```
 158 
 159 **When to Use**: Applying business rules to data
 160 
 161 ---
 162 
 163 ### Pattern 5: HANDOFF (Escalation)
 164 
 165 **Purpose**: Transfers conversation to human agent
 166 
 167 ```yaml
 168 topic escalation:
 169   description: "Escalate to human agent"
 170   reasoning:
 171     instructions: ->
 172       | Customer has failed verification 3 times.
 173         Escalating to a human agent for assistance.
 174     actions:
 175       handoff: @utils.escalate
 176         description: "Transfer to human agent"
 177 ```
 178 
 179 **When to Use**: Failed verification, complex issues, customer request
 180 
 181 ---
 182 
 183 ## Architecture Patterns
 184 
 185 ### Pattern 1: Hub and Spoke
 186 
 187 Central router to specialized topics.
 188 
 189 ```
 190        ┌─────────────┐
 191        │ topic_sel   │
 192        │   (hub)     │
 193        └──────┬──────┘
 194     ┌─────────┼─────────┐
 195     ▼         ▼         ▼
 196 ┌────────┐ ┌────────┐ ┌────────┐
 197 │refunds │ │ orders │ │support │
 198 │(spoke) │ │(spoke) │ │(spoke) │
 199 └────────┘ └────────┘ └────────┘
 200 ```
 201 
 202 **When to Use**: Multi-purpose agents with distinct request types
 203 
 204 ---
 205 
 206 ### Pattern 2: Linear Flow
 207 
 208 Sequential A → B → C pipeline.
 209 
 210 ```
 211 ┌───────┐    ┌────────┐    ┌─────────┐    ┌─────────┐
 212 │ entry │ → │ verify │ → │ process │ → │ confirm │
 213 └───────┘    └────────┘    └─────────┘    └─────────┘
 214 ```
 215 
 216 **When to Use**: Mandatory steps (onboarding, checkout, compliance)
 217 
 218 ---
 219 
 220 ### Pattern 3: Escalation Chain
 221 
 222 Tiered support with complexity-based routing.
 223 
 224 ```
 225 ┌───────┐    ┌───────┐    ┌──────────┐    ┌─────────┐
 226 │  L1   │ → │  L2   │ → │    L3    │ → │  human  │
 227 │(basic)│    │ (adv) │    │ (expert) │    │  agent  │
 228 └───┬───┘    └───┬───┘    └────┬─────┘    └─────────┘
 229     ▼            ▼             ▼
 230 [resolved]  [resolved]    [resolved]
 231 ```
 232 
 233 **When to Use**: Support workflows with complexity levels
 234 
 235 ---
 236 
 237 ### Pattern 4: Verification Gate
 238 
 239 Security gate before protected topics.
 240 
 241 ```
 242               ┌───────────┐
 243               │   entry   │
 244               └─────┬─────┘
 245                     ▼
 246               ┌───────────┐◄─────────────┐
 247               │  VERIFY   │              │
 248               │  (GATE)   │              │
 249               └─────┬─────┘              │
 250           ┌─────────┴─────────┐          │
 251           ▼                   ▼          │
 252     [verified=True]    [verified=False]──┘
 253           │
 254     ┌─────┴─────────────┐
 255     ▼         ▼         ▼
 256 ┌─────────┐┌─────────┐┌──────────┐
 257 │ account ││payments ││ settings │
 258 │(protect)││(protect)││(protected)│
 259 └─────────┘└─────────┘└──────────┘
 260 ```
 261 
 262 **When to Use**: Sensitive data, payments, PII access
 263 
 264 ---
 265 
 266 ### Pattern 5: State Gate (Open Gate)
 267 
 268 3-variable state machine that bypasses the LLM topic selector when a gate holds focus, redirects unauthenticated users to an auth gate, and automatically returns them to their original intended topic after authentication.
 269 
 270 ```
 271                       ┌─────────────────────┐
 272                       │   topic_selector    │
 273                       │   (start_agent)     │
 274                       │                     │
 275                       │ before_reasoning:   │
 276                       │ if open_gate <> null│
 277                       │   → bypass LLM     │
 278                       └──────────┬──────────┘
 279              ┌───────────────────┼───────────────────┐
 280              ▼                   ▼                   ▼
 281   ┌──────────────────┐ ┌────────────────┐ ┌─────────────────┐
 282   │ protected_topic_A│ │protected_top_B│ │ general_inquiry  │
 283   │ (auth required)  │ │(auth required)│ │ (no auth needed) │
 284   │                  │ │               │ │                  │
 285   │ if !auth → gate  │ │ if !auth→gate │ │ (no gate logic)  │
 286   │ if auth → lock   │ │ if auth→lock  │ │                  │
 287   └────────┬─────────┘ └───────┬───────┘ └─────────────────┘
 288            │ set next_topic    │ set next_topic
 289            ▼                   ▼
 290   ┌──────────────────────────────────────┐
 291   │         authentication_gate          │
 292   │                                      │
 293   │ after_reasoning:                     │
 294   │   if auth → route via next_topic     │
 295   └──────────────────────────────────────┘
 296 ```
 297 
 298 **The 3 Variables:**
 299 
 300 | Variable | Type | Purpose |
 301 |----------|------|---------|
 302 | `open_gate` | string | Which topic holds focus (`"null"` = LLM decides) |
 303 | `next_topic` | string | Deferred destination after auth completes |
 304 | `authenticated` | boolean | Whether user has passed authentication |
 305 
 306 **When to Use**: Multiple protected topics behind a shared auth gate, especially when you want zero-credit LLM bypass while the gate holds focus.
 307 
 308 **Key Difference from Verification Gate (Pattern 4)**: The Verification Gate is a linear, one-time gate — once verified, the user proceeds and never returns. The State Gate supports **deferred routing** (remembers where the user wanted to go), **N protected topics** behind a single gate, and an **EXIT_PROTOCOL** to release the gate when the user changes intent.
 309 
 310 > **Template**: See [assets/patterns/open-gate-routing.agent](../assets/patterns/open-gate-routing.agent) for the complete implementation with walkthrough.
 311 
 312 ---
 313 
 314 ## Deterministic vs. Subjective Classification
 315 
 316 ### Classification Framework
 317 
 318 | Put in Deterministic Nodes if... | Put in Subjective Reasoning if... |
 319 |----------------------------------|-----------------------------------|
 320 | Security/safety requirement | Conversational/greeting |
 321 | Financial threshold | Context understanding needed |
 322 | Data fetch required | Natural language generation |
 323 | Counter/state management | Flexible interpretation needed |
 324 | Hard cutoff rule | Response explanation |
 325 
 326 ### Examples
 327 
 328 | Requirement | Classification | Reasoning |
 329 |-------------|----------------|-----------|
 330 | "ALWAYS verify identity before refund" | **Deterministic** | Security - must be code-enforced |
 331 | "Start with a friendly greeting" | **Subjective** | Conversational - LLM flexibility |
 332 | "IF churn > 80, full refund" | **Deterministic** | Financial threshold - no exceptions |
 333 | "Explain the refund status" | **Subjective** | Natural language generation |
 334 | "Count failed verification attempts" | **Deterministic** | Counter logic - must be accurate |
 335 | "Redirect off-topic questions" | **Subjective** | Context understanding required |
 336 
 337 ---
 338 
 339 ## State Machine Example: Pronto Refund Agent
 340 
 341 ```
 342                               ┌────────────────────┐
 343                               │ Identity           │  verified
 344                  refund       │ Verification       │─────────────┐
 345                  intent       │ (VERIFICATION)     │             │
 346 ┌────────────────┐           └─────────┬──────────┘             ▼
 347 │ Topic Selector │──────────▶          │              ┌─────────────────┐
 348 │   (ROUTING)    │                     │ failed 3x    │ Risk Assessment │
 349 └────────────────┘                     │              │ (DATA-LOOKUP)   │
 350                                        │              └────────┬────────┘
 351                                        ▼                       │ score loaded
 352                               ┌────────────────┐               ▼
 353                               │  Escalation    │      ┌─────────────────┐
 354                               │  (HANDOFF)     │      │ Refund Processor│
 355                               └────────────────┘      │  (PROCESSING)   │
 356                                                       └─────────────────┘
 357 ```
 358 
 359 ### State Definitions
 360 
 361 | State | Type | Entry Condition | Exit Conditions |
 362 |-------|------|-----------------|-----------------|
 363 | Topic Selector | ROUTING | Conversation start | Intent detected |
 364 | Identity Verification | VERIFICATION | Refund intent | Verified OR 3 failures |
 365 | Risk Assessment | DATA-LOOKUP | Identity verified | Score loaded |
 366 | Refund Processor | PROCESSING | Score loaded | Refund complete |
 367 | Escalation | HANDOFF | 3 failures | Human takeover |
 368 
 369 ---
 370 
 371 ## Best Practices
 372 
 373 ### 1. Single Responsibility per Topic
 374 Each topic should handle ONE concern. If a topic does verification AND processing, split it.
 375 
 376 ### 2. Explicit Transitions
 377 Always define how to enter AND exit each state. No dead ends.
 378 
 379 ### 3. Guard Sensitive Transitions
 380 Use `available when` to make actions invisible when conditions aren't met.
 381 
 382 ```yaml
 383 actions:
 384   process_payment: @actions.charge_card
 385     available when @variables.customer_verified == True
 386     # LLM literally cannot see this action if not verified
 387 ```
 388 
 389 ### 4. Design for the Happy Path First
 390 Map the success flow, then add failure states.
 391 
 392 ### 5. Use Escalation as a Safety Net
 393 When in doubt, escalate to human. It's better than a bad automated decision.
 394 
 395 ---
 396 
 397 ## Topic Design Patterns
 398 
 399 > Migrated from the former `sf-ai-agentforce-legacy/references/topics-guide.md` on 2026-02-07.
 400 
 401 ### Topic Fundamentals
 402 
 403 **Topics** are conversation modes that group related actions and reasoning logic. Think of them as "skill areas" or "conversation contexts" for your agent.
 404 
 405 | Benefit | Description |
 406 |---------|-------------|
 407 | **Separation of Concerns** | Group related functionality (e.g., "Order Management", "Support") |
 408 | **Focused Instructions** | Each topic has its own reasoning instructions |
 409 | **Action Scoping** | Actions defined in a topic are available only in that topic |
 410 | **Persona Switching** | Topics can override system instructions for different modes |
 411 
 412 ### Topic Structure
 413 
 414 #### Required Fields
 415 
 416 Every topic MUST have:
 417 - `description:` - What the topic does (used by LLM for routing decisions)
 418 
 419 > **`label:` is valid on topics** (TDD v2.2.0). Use `label:` for display names and `description:` to convey the topic's purpose to the LLM.
 420 
 421 ```agentscript
 422 topic order_lookup:
 423    description: "Helps customers look up their order status and details"
 424 
 425    reasoning:
 426       instructions: ->
 427          | Help the user find their order.
 428 ```
 429 
 430 #### Optional Blocks
 431 
 432 | Block | Purpose | Example |
 433 |-------|---------|---------|
 434 | `system:` | Override global system instructions | Persona switching |
 435 | `actions:` | Define topic-specific actions | Flow/Apex actions |
 436 | `reasoning:` | Topic reasoning logic | Instructions + action invocations |
 437 
 438 ---
 439 
 440 ### Topic Transition Mechanics
 441 
 442 #### `@utils.transition to @topic.[name]`
 443 
 444 Permanently move to another topic. The user CANNOT return to the previous topic without explicit routing.
 445 
 446 ```agentscript
 447 start_agent topic_selector:
 448    description: "Routes users to topics"
 449 
 450    reasoning:
 451       instructions: ->
 452          | What would you like to do?
 453          | 1. Check order status
 454          | 2. Get support
 455       actions:
 456          go_orders: @utils.transition to @topic.order_lookup
 457          go_support: @utils.transition to @topic.support
 458 ```
 459 
 460 **When to Use:**
 461 - **Permanent mode switches** (e.g., "I want to check my order" → order_lookup)
 462 - **One-way transitions** where user won't return to previous topic
 463 - **Entry point routing** (start_agent → specific topics)
 464 
 465 ---
 466 
 467 ### Topic Delegation vs Transition
 468 
 469 There are TWO ways to reference other topics:
 470 
 471 #### 1. `@utils.transition to @topic.[name]` — Permanent Transition
 472 
 473 **Behavior:**
 474 - Permanently moves to the target topic
 475 - User CANNOT automatically return
 476 - Current topic is abandoned
 477 - Target topic becomes the active context
 478 
 479 **Use Cases:**
 480 - Main menu routing (start_agent → feature topics)
 481 - Mode switches (FAQ → Support)
 482 - One-way workflows
 483 
 484 ```agentscript
 485 # Permanent transition
 486 actions:
 487    go_to_orders: @utils.transition to @topic.order_management
 488 ```
 489 
 490 #### 2. `@topic.[name]` — Topic Delegation (Sub-Agent Pattern)
 491 
 492 **Behavior:**
 493 - Temporarily delegates to target topic
 494 - Target topic can "return" control to caller
 495 - Original topic resumes after delegation completes
 496 - Like calling a subroutine
 497 
 498 **Use Cases:**
 499 - Specialist consultation (Main Agent → Tax Expert → Main Agent)
 500 - Reusable sub-workflows (Address Collection)
 501 - Modular agent design
 502 
 503 ```agentscript
 504 # Topic delegation (can return)
 505 actions:
 506    consult_specialist: @topic.tax_specialist
 507 ```
 508 
 509 **Key Difference:**
 510 
 511 | Pattern | Control Flow | Returns? |
 512 |---------|--------------|----------|
 513 | `@utils.transition to @topic.x` | Permanent move | No |
 514 | `@topic.x` | Temporary delegation | Yes (if target topic transitions back) |
 515 
 516 ---
 517 
 518 ### Routing Pattern Examples
 519 
 520 #### Hub-and-Spoke (with Back Navigation)
 521 
 522 ```agentscript
 523 start_agent topic_selector:
 524    description: "Main menu / router"
 525 
 526    reasoning:
 527       instructions: ->
 528          | What can I help you with?
 529       actions:
 530          go_orders: @utils.transition to @topic.order_management
 531          go_support: @utils.transition to @topic.support
 532          go_faq: @utils.transition to @topic.faq
 533 
 534 topic order_management:
 535    description: "Order lookup and tracking"
 536 
 537    reasoning:
 538       instructions: ->
 539          | Help with orders.
 540       actions:
 541          back: @utils.transition to @topic.topic_selector
 542 
 543 topic support:
 544    description: "Customer support"
 545 
 546    reasoning:
 547       instructions: ->
 548          | Provide support.
 549       actions:
 550          back: @utils.transition to @topic.topic_selector
 551 ```
 552 
 553 **Benefits:** Clear entry point, easy to add new topics, users can always go back to menu.
 554 
 555 #### Linear Workflow
 556 
 557 ```agentscript
 558 start_agent onboarding:
 559    description: "Collect user information"
 560 
 561    reasoning:
 562       instructions: ->
 563          | Welcome! Let's get started.
 564       actions:
 565          next: @utils.transition to @topic.collect_address
 566 
 567 topic collect_address:
 568    description: "Get shipping address"
 569 
 570    reasoning:
 571       instructions: ->
 572          | What's your address?
 573       actions:
 574          next: @utils.transition to @topic.confirm_details
 575 
 576 topic confirm_details:
 577    description: "Review and confirm"
 578 
 579    reasoning:
 580       instructions: ->
 581          | Please confirm your information.
 582 ```
 583 
 584 **Benefits:** Guided, step-by-step experience. Prevents users from skipping steps.
 585 
 586 #### Contextual Routing (Data-Driven)
 587 
 588 ```agentscript
 589 topic order_lookup:
 590    description: "Look up order by number"
 591 
 592    reasoning:
 593       instructions: ->
 594          | if @variables.order_found == False:
 595          |    | I couldn't find that order.
 596       actions:
 597          lookup: @actions.get_order
 598          # Conditional routing based on outcome
 599          go_support: @utils.transition to @topic.support
 600             available when @variables.order_found == False
 601          back: @utils.transition to @topic.topic_selector
 602             available when @variables.order_found == True
 603 ```
 604 
 605 **Benefits:** Dynamic routing based on data, handles error cases gracefully.
 606 
 607 ---
 608 
 609 ### Multi-Topic Agent Design
 610 
 611 #### When to Use Multiple Topics
 612 
 613 | Scenario | Topics Needed |
 614 |----------|---------------|
 615 | **Multi-feature agent** | 1 topic per feature + 1 router topic |
 616 | **Workflow with steps** | 1 topic per step + 1 entry topic |
 617 | **Persona switching** | 1 topic per persona + 1 selector |
 618 | **Specialist delegation** | 1 main topic + N specialist topics |
 619 
 620 ---
 621 
 622 ### Bidirectional Routing (Specialist Consultation)
 623 
 624 ```agentscript
 625 topic main_agent:
 626    description: "General assistant that can consult specialists"
 627 
 628    reasoning:
 629       instructions: ->
 630          | I can help with most questions.
 631          | For specialized topics, I'll consult our experts.
 632       actions:
 633          # Delegation - specialist can return control
 634          consult_tax: @topic.tax_specialist
 635          consult_legal: @topic.legal_specialist
 636 
 637 topic tax_specialist:
 638    description: "Expert on tax questions"
 639 
 640    reasoning:
 641       instructions: ->
 642          | [Tax Specialist Mode]
 643          | Provide detailed tax guidance.
 644       actions:
 645          # Return to main agent when done
 646          return_to_main: @utils.transition to @topic.main_agent
 647 
 648 topic legal_specialist:
 649    description: "Expert on legal questions"
 650 
 651    reasoning:
 652       instructions: ->
 653          | [Legal Specialist Mode]
 654          | Provide legal information.
 655       actions:
 656          return_to_main: @utils.transition to @topic.main_agent
 657 ```
 658 
 659 **Benefits:** Main agent stays in control, specialists provide focused expertise, clean separation of concerns, reusable specialist topics.
 660 
 661 ---
 662 
 663 ### Topic Naming Conventions
 664 
 665 | Element | Convention | Example |
 666 |---------|------------|---------|
 667 | Topic name | snake_case | `order_management` |
 668 | Action name | snake_case | `get_order_status` |
 669 
 670 ### Common Topic Design Mistakes
 671 
 672 | Mistake | Fix |
 673 |---------|-----|
 674 | Missing `description` | Add `description:` to every topic (required for LLM routing) |
 675 | Orphaned topics (unreachable) | Ensure all topics have incoming transitions |
 676 | No way to go back | Add transition to topic_selector or escalation |
 677 | Too many topics | Combine related functionality |
 678 | Too few topics | Split complex topics into focused ones |
 679 
 680 ### Topic Transitions Checklist
 681 
 682 - [ ] `start_agent` transitions to at least one topic
 683 - [ ] All topics are reachable from `start_agent` (directly or indirectly)
 684 - [ ] Each topic has at least one outbound transition (or escalation)
 685 - [ ] Users can navigate back to main menu or exit
 686 - [ ] Topic descriptions are clear and detailed for LLM routing
