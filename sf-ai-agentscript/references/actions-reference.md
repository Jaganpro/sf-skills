<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Actions Reference
   2 
   3 > Migrated from the former `sf-ai-agentforce-legacy/references/actions-reference.md` on 2026-02-07.
   4 > For context-aware descriptions, instruction references, and input binding patterns, see [action-patterns.md](action-patterns.md).
   5 > For prompt template actions (`generatePromptResponse://`), see [action-prompt-templates.md](action-prompt-templates.md).
   6 
   7 Complete guide to Agent Actions in Agentforce: Flow, Apex, API actions,
   8 escalation routing, and GenAiFunction metadata.
   9 
  10 ---
  11 
  12 ## Action Properties Reference
  13 
  14 All actions in Agent Script support these properties:
  15 
  16 ### Action Definition Properties
  17 
  18 | Property | Type | Required | Description | TDD |
  19 |----------|------|----------|-------------|-----|
  20 | `target` | String | Yes | Executable target (see Action Target Types below) | v1.3.0 |
  21 | `description` | String | Yes | Explains behavior for LLM decision-making | v1.3.0 |
  22 | `label` | String | No | Display name in UI (valid on action definitions, topics, and I/O fields) | v2.2.0 |
  23 | `inputs` | Object | No | Input parameters and requirements | v1.3.0 |
  24 | `outputs` | Object | No | Return parameters | v1.3.0 |
  25 | `available_when` | Expression | No | Conditional availability for the LLM | v1.3.0 |
  26 | `require_user_confirmation` | Boolean | No | Ask user to confirm before execution (compiles; runtime no-op per Issue 6) | v2.2.0 |
  27 | `include_in_progress_indicator` | Boolean | No | Show progress indicator during execution | v2.2.0 |
  28 | `progress_indicator_message` | String | No | Custom message shown during execution (e.g., "Processing your request...") | v2.2.0 |
  29 
  30 > **Note**: `label`, `require_user_confirmation`, `include_in_progress_indicator`, and `progress_indicator_message` are valid on action definitions with `target:` but NOT on `@utils.transition` utility actions (see Val_Action_Properties vs Val_Action_Meta_Props).
  31 
  32 ### Input Properties (TDD Validated v2.2.0)
  33 
  34 | Property | Type | Description | TDD |
  35 |----------|------|-------------|-----|
  36 | `description` | String | Explains the input parameter to LLM | v1.3.0 |
  37 | `label` | String | Display name in UI | v2.2.0 |
  38 | `is_required` | Boolean | Marks input as mandatory for the LLM | v2.2.0 |
  39 | `is_user_input` | Boolean | LLM extracts value from conversation context | v2.2.0 |
  40 | `complex_data_type_name` | String | Lightning data type mapping | v2.1.0 |
  41 
  42 ### Output Properties (Updated v2.2.0)
  43 
  44 | Property | Type | Description | TDD |
  45 |----------|------|-------------|-----|
  46 | `description` | String | Explains the output parameter | v1.3.0 |
  47 | `label` | String | Display name in UI | v2.2.0 |
  48 | `is_displayable` | Boolean | `False` = hide from user display (standard name for `filter_from_agent`) | v2.2.0 |
  49 | `is_used_by_planner` | Boolean | `True` = LLM can reason about this value for routing decisions | v2.2.0 |
  50 | `filter_from_agent` | Boolean | Alias for `is_displayable: False` — set `True` to hide sensitive data from LLM | v1.3.0 |
  51 | `complex_data_type_name` | String | Lightning data type mapping | v2.1.0 |
  52 
  53 > **`is_displayable` vs `filter_from_agent`**: Both control the same behavior. `is_displayable: False` is the standard property name (used in SKILL.md and zero-hallucination patterns). `filter_from_agent: True` is an older alias that achieves the same result.
  54 
  55 ### Example with All Properties
  56 
  57 ```agentscript
  58 actions:
  59    process_payment:
  60       description: "Processes payment for the order"
  61       require_user_confirmation: True    # Ask user before executing
  62       include_in_progress_indicator: True
  63       inputs:
  64          amount: number
  65             description: "Payment amount"
  66          card_token: string
  67             description: "Tokenized card number"
  68       outputs:
  69          transaction_id: string
  70             description: "Transaction reference"
  71          card_last_four: string
  72             description: "Last 4 digits of card"
  73             filter_from_agent: True     # Hide from LLM context
  74       target: "flow://Process_Payment"
  75       available_when: @variables.cart_total > 0
  76 ```
  77 
  78 ---
  79 
  80 ## Action Target Types (Complete Reference)
  81 
  82 AgentScript supports **22+ action target types**. Use the correct protocol for your integration:
  83 
  84 | Short Name | Long Name | Description | Use Case |
  85 |------------|-----------|-------------|----------|
  86 | `flow` | `flow` | Salesforce Flow | Most common — Autolaunched Flows |
  87 | `apex` | `apex` | Apex Class | Custom business logic |
  88 | `prompt` | `generatePromptResponse` | Prompt Template | AI-generated responses |
  89 | `standardInvocableAction` | `standardInvocableAction` | Built-in Salesforce actions | Send email, create task, etc. |
  90 | `externalService` | `externalService` | External API via OpenAPI schema | External system calls |
  91 | `quickAction` | `quickAction` | Object-specific quick actions | Log call, create related record |
  92 | `api` | `api` | REST API calls | Direct API invocation |
  93 | `apexRest` | `apexRest` | Custom REST endpoints | Custom @RestResource classes |
  94 | `serviceCatalog` | `createCatalogItemRequest` | Service Catalog | Service catalog requests |
  95 | `integrationProcedureAction` | `executeIntegrationProcedure` | OmniStudio Integration | Industry Cloud procedures |
  96 | `expressionSet` | `runExpressionSet` | Expression calculations | Decision matrix, calculations |
  97 | `cdpMlPrediction` | `cdpMlPrediction` | CDP ML predictions | Data Cloud predictions |
  98 | `externalConnector` | `externalConnector` | External system connector | Pre-built connectors |
  99 | `slack` | `slack` | Slack integration | Slack messaging |
 100 | `namedQuery` | `namedQuery` | Predefined queries | Saved SOQL queries |
 101 | `auraEnabled` | `auraEnabled` | Lightning component methods | @AuraEnabled Apex methods |
 102 | `mcpTool` | `mcpTool` | Model Context Protocol | MCP tool integrations |
 103 | `retriever` | `retriever` | Knowledge retrieval | RAG/knowledge base queries |
 104 
 105 **Target Format**: `<type>://<DeveloperName>` (e.g., `flow://Get_Account_Info`, `standardInvocableAction://sendEmail`)
 106 
 107 **Common Examples:**
 108 ```agentscript
 109 # Flow action (most common)
 110 target: "flow://Get_Customer_Orders"
 111 
 112 # Apex action
 113 target: "apex://CustomerServiceController"
 114 
 115 # Prompt template
 116 target: "generatePromptResponse://Email_Draft_Template"
 117 
 118 # Standard invocable action (built-in Salesforce)
 119 target: "standardInvocableAction://sendEmail"
 120 
 121 # External service (API call)
 122 target: "externalService://Stripe_Payment_API"
 123 ```
 124 
 125 **Tip**: Before creating a custom Flow, check if a `standardInvocableAction://` already exists for your use case.
 126 
 127 ---
 128 
 129 ## Action Invocation Methods
 130 
 131 | Method | Syntax | Behavior | AiAuthoringBundle | GenAiPlannerBundle |
 132 |--------|--------|----------|-------------------|-------------------|
 133 | **Actions Block** | `actions:` in `reasoning:` | LLM chooses which to execute | ✅ Works | ✅ Works |
 134 | **Deterministic** | `run @actions.name` | Always executes when code path is reached | ⚠️ Partial (see below) | ✅ Works |
 135 
 136 ### Deployment Method Capabilities
 137 
 138 **`run` keyword IS supported in `reasoning.actions:` post-action blocks and `instructions: ->` blocks (Validated Jan 2026)**
 139 
 140 ```agentscript
 141 # ✅ WORKS — run in reasoning.actions post-action block
 142 create: @actions.create_order
 143    with customer_id = @variables.customer_id
 144    run @actions.send_confirmation     # ✅ Chains after create_order
 145    set @variables.order_id = @outputs.id
 146 
 147 # ✅ WORKS — run in instructions: -> block
 148 reasoning:
 149    instructions: ->
 150       run @actions.load_customer
 151          with id = @variables.customer_id
 152          set @variables.name = @outputs.name
 153 
 154 # ❌ DOES NOT WORK — run in before_reasoning (no LLM context)
 155 before_reasoning:
 156    run @actions.log_turn    # ❌ May not execute as expected
 157 ```
 158 
 159 > **Note**: The Dec 2025 finding that `run` was "NOT supported" has been superseded. As of Jan 2026, `run` works in post-action chains and procedural instruction blocks. It does NOT work reliably in `before_reasoning:`.
 160 
 161 **`{!@actions.name}` interpolation in instructions (Updated Feb 2026)**
 162 
 163 The `{!@actions.action_name}` syntax embeds a reference to the full action definition into reasoning instructions. This gives the LLM richer context about available actions.
 164 
 165 ```agentscript
 166 # ✅ WORKS — reference action in instructions for guided selection
 167 reasoning:
 168    instructions: ->
 169       | To look up an order, use {!@actions.get_order}.
 170       | To check shipping status, use {!@actions.track_shipment}.
 171 ```
 172 
 173 > **Note**: The Dec 2025 finding that this was broken has been superseded. See [action-patterns.md](action-patterns.md#2-instruction-action-references) for detailed usage patterns and examples.
 174 
 175 ### Correct Approach: Use `reasoning.actions` Block
 176 
 177 The LLM automatically selects appropriate actions from those defined in the `reasoning.actions` block:
 178 
 179 ```agentscript
 180 topic order_management:
 181    description: "Handles order inquiries"
 182 
 183    actions:
 184       get_order:
 185          description: "Retrieves order information"
 186          inputs:
 187             order_id: string
 188                description: "The order ID"
 189          outputs:
 190             status: string
 191                description: "Order status"
 192          target: "flow://Get_Order_Details"
 193 
 194    reasoning:
 195       instructions: ->
 196          | Help the customer with their order.
 197          | When they ask about an order, look it up.
 198       actions:
 199          # LLM automatically selects this when appropriate
 200          lookup: @actions.get_order
 201             with order_id=...
 202             set @variables.order_status = @outputs.status
 203 ```
 204 
 205 ---
 206 
 207 ## Action Type 1: Flow Actions
 208 
 209 ### When to Use
 210 
 211 - Standard Salesforce data operations (CRUD)
 212 - Business logic that can be expressed in Flow
 213 - Screen flows for guided user experiences
 214 - Approval processes
 215 
 216 ### Implementation
 217 
 218 ```yaml
 219 actions:
 220   create_case:
 221     description: "Creates a new support case for the customer"
 222     inputs:
 223       subject:
 224         type: string
 225         description: "Case subject line"
 226       description:
 227         type: string
 228         description: "Detailed case description"
 229       priority:
 230         type: string
 231         description: "Case priority (Low, Medium, High, Urgent)"
 232     outputs:
 233       caseNumber:
 234         type: string
 235         description: "Created case number"
 236       caseId:
 237         type: string
 238         description: "Case record ID"
 239     target: "flow://Create_Support_Case"
 240 ```
 241 
 242 ### Flow Requirements
 243 
 244 For an action to work with agents, the Flow must:
 245 
 246 1. **Be Autolaunched** — `processType: AutoLaunchedFlow`
 247 2. **Have Input Variables** — Marked as `isInput: true`
 248 3. **Have Output Variables** — Marked as `isOutput: true`
 249 4. **Be Active** — `status: Active`
 250 
 251 **Flow Variable Example:**
 252 ```xml
 253 <variables>
 254     <name>subject</name>
 255     <dataType>String</dataType>
 256     <isCollection>false</isCollection>
 257     <isInput>true</isInput>
 258     <isOutput>false</isOutput>
 259 </variables>
 260 ```
 261 
 262 ### Best Practices
 263 
 264 | Practice | Description |
 265 |----------|-------------|
 266 | Descriptive names | Use clear Flow API names that describe the action |
 267 | Error handling | Include fault paths in your Flow |
 268 | Bulkification | Design Flows to handle multiple records |
 269 | Governor limits | Avoid SOQL/DML in loops |
 270 
 271 ---
 272 
 273 ## Action Type 2: Apex Actions
 274 
 275 ### When to Use
 276 
 277 - Complex calculations or algorithms
 278 - Custom integrations requiring Apex
 279 - Operations not possible in Flow
 280 - Bulk data processing
 281 - When you need full control over execution
 282 
 283 ### Two Deployment Paths (CRITICAL DISTINCTION)
 284 
 285 | Deployment Method | How Apex Actions Work | GenAiFunction Required? |
 286 |-------------------|----------------------|------------------------|
 287 | **AiAuthoringBundle** (.agent file) | `apex://ClassName` target in topic actions block | **NO** |
 288 | **Agent Builder UI** (GenAiPlannerBundle) | GenAiFunction metadata wraps the Apex class | **YES** |
 289 
 290 > ⚠️ **The official [agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) repo uses `apex://ClassName` directly with ZERO GenAiFunction metadata.** GenAiFunction is only needed when configuring agents through the Agent Builder UI or deploying via GenAiPlannerBundle.
 291 
 292 ### Path A: AiAuthoringBundle (Agent Script — RECOMMENDED)
 293 
 294 #### Step 1: Create Apex Class with @InvocableMethod
 295 
 296 ```apex
 297 public with sharing class CalculateDiscountAction {
 298 
 299     public class DiscountRequest {
 300         @InvocableVariable(label='Order Amount' required=true)
 301         public Decimal orderAmount;
 302 
 303         @InvocableVariable(label='Customer Tier' required=true)
 304         public String customerTier;
 305     }
 306 
 307     public class DiscountResult {
 308         @InvocableVariable(label='Discount Percentage')
 309         public Decimal discountPercentage;
 310 
 311         @InvocableVariable(label='Final Amount')
 312         public Decimal finalAmount;
 313     }
 314 
 315     @InvocableMethod(
 316         label='Calculate Discount'
 317         description='Calculates discount based on order amount and customer tier'
 318     )
 319     public static List<DiscountResult> calculateDiscount(List<DiscountRequest> requests) {
 320         List<DiscountResult> results = new List<DiscountResult>();
 321         for (DiscountRequest req : requests) {
 322             DiscountResult result = new DiscountResult();
 323             result.discountPercentage = getTierDiscount(req.customerTier);
 324             result.finalAmount = req.orderAmount * (1 - result.discountPercentage / 100);
 325             results.add(result);
 326         }
 327         return results;
 328     }
 329 
 330     private static Decimal getTierDiscount(String tier) {
 331         Map<String, Decimal> tierDiscounts = new Map<String, Decimal>{
 332             'Bronze' => 5, 'Silver' => 10, 'Gold' => 15, 'Platinum' => 20
 333         };
 334         return tierDiscounts.containsKey(tier) ? tierDiscounts.get(tier) : 0;
 335     }
 336 }
 337 ```
 338 
 339 #### Step 2: Reference DIRECTLY in Agent Script via `apex://`
 340 
 341 ```yaml
 342 topic discount_calculator:
 343    description: "Calculates discount for customer order"
 344 
 345    # Level 1: Action DEFINITION with target
 346    actions:
 347       calculate_discount:
 348          description: "Calculates discount based on order amount and customer tier"
 349          inputs:
 350             orderAmount: number
 351                description: "The total order amount before discount"
 352             customerTier: string
 353                description: "Customer membership tier"
 354          outputs:
 355             discountPercentage: number
 356                description: "Applied discount percentage"
 357             finalAmount: number
 358                description: "Final order amount after discount"
 359          target: "apex://CalculateDiscountAction"   # Direct Apex — NO GenAiFunction needed!
 360 
 361    reasoning:
 362       instructions: |
 363          Help the customer calculate their discount.
 364       # Level 2: Action INVOCATION referencing the Level 1 definition
 365       actions:
 366          calc: @actions.calculate_discount
 367             with orderAmount=...
 368             with customerTier=@variables.tier
 369             set @variables.final_amount = @outputs.finalAmount
 370 ```
 371 
 372 > ✅ **No GenAiFunction, no GenAiPlugin, no metadata deployment beyond the Apex class itself.** The `apex://ClassName` target auto-discovers the `@InvocableMethod` on the class.
 373 
 374 #### I/O Name Matching Rules (TDD Validated v2.1.0)
 375 
 376 Action `inputs:` and `outputs:` names in Agent Script must **exactly match** the `@InvocableVariable` field names in the Apex class:
 377 
 378 | Agent Script I/O Name | Apex @InvocableVariable Field | Result |
 379 |------------------------|-------------------------------|--------|
 380 | `orderAmount` | `public Decimal orderAmount` | ✅ Publishes |
 381 | `order_amount` | `public Decimal orderAmount` | ❌ `invalid input 'order_amount'` |
 382 | `wrong_name` | `public String outputText` | ❌ `invalid output 'wrong_name'` |
 383 | *(subset of outputs)* | *(declares fewer than all)* | ✅ Publishes (partial is valid) |
 384 
 385 > **Partial Output Pattern**: You can declare a **subset** of the target's outputs in your action definition — you don't need to map every output parameter. This is useful when you only need one field from a multi-output action.
 386 
 387 #### Bare @InvocableMethod Pattern (NOT Compatible)
 388 
 389 > ⚠️ **TDD Finding (v2.1.0)**: Apex classes using bare `List<String>` parameters (no `@InvocableVariable` wrapper classes) are **incompatible** with Agent Script actions. The framework cannot discover bindable parameter names without `@InvocableVariable` annotations.
 390 
 391 ```apex
 392 // ❌ INCOMPATIBLE with Agent Script — bare parameters, no wrappers
 393 public class BareAction {
 394     @InvocableMethod(label='Bare Action')
 395     public static List<String> execute(List<String> inputs) {
 396         return inputs;
 397     }
 398 }
 399 
 400 // ✅ COMPATIBLE — wrapper classes with @InvocableVariable
 401 public class WrappedAction {
 402     public class Request {
 403         @InvocableVariable(label='Input Text' required=true)
 404         public String inputText;  // ← This field name becomes the I/O name
 405     }
 406     public class Response {
 407         @InvocableVariable(label='Output Text')
 408         public String outputText;  // ← This field name becomes the I/O name
 409     }
 410     @InvocableMethod(label='Wrapped Action')
 411     public static List<Response> execute(List<Request> requests) { ... }
 412 }
 413 ```
 414 
 415 **Rule**: Always use `@InvocableVariable` wrapper classes when your Apex action will be called from Agent Script.
 416 
 417 > ⚠️ **Namespace Warning (Unresolved)**: In namespaced packages, `apex://ClassName` may fail at publish time with "invocable action does not exist," even when the Apex class is confirmed deployed via SOQL. It is unclear whether namespace prefix syntax is required (e.g., `apex://ns__ClassName`). If you encounter this in a namespaced org, try: (1) `apex://ns__ClassName` format, (2) wrapping the Apex in a Flow and using `flow://` instead. See [known-issues.md](known-issues.md#issue-2-sf-agent-publish-fails-with-namespace-prefix-on-apex-targets) for tracking.
 418 
 419 ### Path B: Agent Builder UI (GenAiPlannerBundle — Legacy)
 420 
 421 If you're NOT using Agent Script and are building agents through the Agent Builder UI, you need GenAiFunction metadata to wrap the Apex class. See the `assets/metadata/genai-function-apex.xml` template for the XML format.
 422 
 423 > **Note**: GenAiFunction XML (API v65.0) only supports these elements: `masterLabel`, `description`, `invocationTarget`, `invocationTargetType`, `isConfirmationRequired`. Input/output schemas are defined via `input/schema.json` and `output/schema.json` bundle files, NOT inline XML elements.
 424 
 425 ---
 426 
 427 ## Action Type 3: API Actions (External System Integration)
 428 
 429 ### Architecture
 430 
 431 ```
 432 ┌─────────────────────────────────────────────────────────────┐
 433 │                  API ACTION ARCHITECTURE                      │
 434 ├─────────────────────────────────────────────────────────────┤
 435 │  Agent Script                                                │
 436 │       │                                                      │
 437 │       ▼                                                      │
 438 │  flow://HTTP_Callout_Flow                                    │
 439 │       │                                                      │
 440 │       ▼                                                      │
 441 │  HTTP Callout Action (in Flow)                               │
 442 │       │                                                      │
 443 │       ▼                                                      │
 444 │  Named Credential (Authentication)                           │
 445 │       │                                                      │
 446 │       ▼                                                      │
 447 │  External API                                                │
 448 └─────────────────────────────────────────────────────────────┘
 449 ```
 450 
 451 ### Implementation Steps
 452 
 453 1. **Create Named Credential** (via sf-integration skill)
 454 2. **Create HTTP Callout Flow** wrapping the external call
 455 3. **Reference Flow in Agent Script** with `flow://` target
 456 
 457 ### Security Considerations
 458 
 459 | Consideration | Implementation |
 460 |---------------|----------------|
 461 | Authentication | Always use Named Credentials (never hardcode secrets) |
 462 | Permissions | Use Permission Sets to grant Named Principal access |
 463 | Error handling | Implement fault paths in Flow |
 464 | Logging | Log callout details for debugging |
 465 | Timeouts | Set appropriate timeout values |
 466 
 467 ---
 468 
 469 ## Connection Block (Escalation Routing)
 470 
 471 The `connection` block enables escalation to human agents via Omni-Channel. Both singular (`connection`) and plural (`connections`) forms are supported.
 472 
 473 ### Basic Syntax
 474 
 475 ```agentscript
 476 # Messaging channel (most common)
 477 connection messaging:
 478    outbound_route_type: "OmniChannelFlow"
 479    outbound_route_name: "Support_Queue_Flow"
 480    escalation_message: "Transferring you to a human agent..."
 481    adaptive_response_allowed: True
 482 ```
 483 
 484 ### Multiple Channels
 485 
 486 ```agentscript
 487 # Use plural form for multiple channels
 488 connections:
 489    messaging:
 490       escalation_message: "Transferring to messaging agent..."
 491       outbound_route_type: "OmniChannelFlow"
 492       outbound_route_name: "agent_support_flow"
 493       adaptive_response_allowed: True
 494    telephony:
 495       escalation_message: "Routing to technical support..."
 496       outbound_route_type: "OmniChannelFlow"
 497       outbound_route_name: "technical_support_flow"
 498       adaptive_response_allowed: False
 499 ```
 500 
 501 ### Connection Block Properties
 502 
 503 | Property | Type | Required | Description |
 504 |----------|------|----------|-------------|
 505 | `outbound_route_type` | String | Yes | **`"OmniChannelFlow"` is the only TDD-validated value.** SKILL.md mentions `"Queue"` and `"Skill"` but the `connections:` block itself is not GA (see known-issues.md Issue 16). |
 506 | `outbound_route_name` | String | Yes | API name of Omni-Channel Flow (must exist in org) |
 507 | `escalation_message` | String | Yes | Message shown to user during transfer |
 508 | `adaptive_response_allowed` | Boolean | No | Allow agent to adapt responses during escalation (default: False) |
 509 
 510 ### Supported Channels
 511 
 512 | Channel | Description | Use Case |
 513 |---------|-------------|----------|
 514 | `messaging` | Chat/messaging channels | Enhanced Chat, Web Chat, In-App |
 515 | `telephony` | Voice/phone channels | Service Cloud Voice, phone support |
 516 
 517 **CRITICAL**: Values like `"queue"`, `"skill"`, `"agent"` for `outbound_route_type` cause validation errors!
 518 
 519 ### Escalation Action
 520 
 521 ```agentscript
 522 # AiAuthoringBundle - basic escalation
 523 actions:
 524    transfer_to_human: @utils.escalate
 525       description: "Transfer to human agent"
 526 
 527 # GenAiPlannerBundle - with reason parameter
 528 actions:
 529    transfer_to_human: @utils.escalate with reason="Customer requested"
 530 ```
 531 
 532 ### Prerequisites for Escalation
 533 
 534 1. Omni-Channel configured in Salesforce
 535 2. Omni-Channel Flow created and deployed
 536 3. Connection block in agent script
 537 4. Messaging channel active (Enhanced Chat, etc.)
 538 
 539 ---
 540 
 541 ## GenAiFunction Metadata Summary (Agent Builder UI / GenAiPlannerBundle ONLY)
 542 
 543 > ⚠️ **NOT needed for AiAuthoringBundle (Agent Script)**. If you're writing `.agent` files, use `target: "apex://ClassName"` or `target: "flow://FlowName"` directly. See Action Type 2 above.
 544 
 545 `GenAiFunction` wraps Apex, Flows, or Prompts as Agent Actions **for the Agent Builder UI path**.
 546 
 547 ```xml
 548 <!-- Minimal valid GenAiFunction XML (API v65.0) -->
 549 <GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
 550     <description>What this action does</description>
 551     <invocationTarget>FlowOrApexName</invocationTarget>
 552     <invocationTargetType>flow|apex|prompt</invocationTargetType>
 553     <isConfirmationRequired>false</isConfirmationRequired>
 554     <masterLabel>Display Name</masterLabel>
 555 </GenAiFunction>
 556 ```
 557 
 558 **Input/Output Schemas**: Use `input/schema.json` and `output/schema.json` files in the GenAiFunction bundle directory. Do NOT use inline XML elements like `<genAiFunctionInputs>`, `<genAiFunctionOutputs>`, `<genAiFunctionParameters>`, or `<capability>` — these are NOT valid in the Metadata API XML schema (API v65.0).
 559 
 560 ### Prompt Template Types
 561 
 562 | Type | Use Case |
 563 |------|----------|
 564 | `flexPrompt` | General purpose, maximum flexibility |
 565 | `salesGeneration` | Sales content (emails, proposals) |
 566 | `fieldCompletion` | Suggest field values |
 567 | `recordSummary` | Summarize record data |
 568 
 569 ### Template Variable Types
 570 
 571 | Variable Type | Description |
 572 |---------------|-------------|
 573 | `freeText` | User-provided text input |
 574 | `recordField` | Bound to specific record field |
 575 | `relatedList` | Data from related records |
 576 | `resource` | Static resource content |
 577 
 578 ---
 579 
 580 ## Cross-Skill Integration
 581 
 582 ### Orchestration Order for API Actions
 583 
 584 When building agents with external API integrations, follow this order:
 585 
 586 ```
 587 ┌─────────────────────────────────────────────────────────────┐
 588 │  INTEGRATION + AGENTFORCE ORCHESTRATION ORDER                │
 589 ├─────────────────────────────────────────────────────────────┤
 590 │  1. sf-connected-apps  → Connected App (if OAuth needed)     │
 591 │  2. sf-integration     → Named Credential + External Service │
 592 │  3. sf-apex            → @InvocableMethod (if custom logic)  │
 593 │  4. sf-flow            → Flow wrapper (HTTP Callout / Apex)  │
 594 │  5. sf-deploy          → Deploy all metadata to org          │
 595 │  6. sf-ai-agentscript  → Agent with flow:// target           │
 596 │  7. sf-deploy          → Publish (sf agent publish            │
 597 │                           authoring-bundle)                   │
 598 └─────────────────────────────────────────────────────────────┘
 599 ```
 600 
 601 ---
 602 
 603 ## Troubleshooting
 604 
 605 | Issue | Cause | Solution |
 606 |-------|-------|----------|
 607 | `Tool target 'X' is not an action definition` | Action not defined in topic `actions:` block, or target doesn't exist in org | Define action with `target:` in topic-level `actions:` block; ensure Apex class/Flow is deployed |
 608 | `invalid input 'X'` or `invalid output 'X'` | I/O name doesn't match `@InvocableVariable` field name in Apex | Use exact field names from the Apex wrapper class (case-sensitive) |
 609 | `Internal Error` with inputs-only action | Action has `inputs:` but no `outputs:` block | Add `outputs:` block — the server-side compiler requires it (see known-issues.md Issue 15) |
 610 | `Internal Error` with bare @InvocableMethod | Apex uses `List<String>` without `@InvocableVariable` wrappers | Refactor Apex to use wrapper classes with `@InvocableVariable` annotations |
 611 | `apex://` target not found | Apex class not deployed or missing `@InvocableMethod` | Deploy class first, ensure it has `@InvocableMethod` annotation |
 612 | Flow action fails | Flow not active or not Autolaunched | Activate the Flow; ensure it's Autolaunched (not Screen) |
 613 | API action timeout | External system slow | Increase timeout, add retry logic |
 614 | Permission denied | Missing Named Principal access | Grant Permission Set |
 615 | Action not appearing in Agent Builder UI | GenAiFunction not deployed (UI path only) | Deploy GenAiFunction metadata (only needed for Agent Builder UI, not Agent Script) |
 616 
 617 ### Debugging Tips
 618 
 619 1. **Check deployment status:** `sf project deploy report`
 620 2. **Verify GenAiFunction deployment:** `sf org list metadata -m GenAiFunction`
 621 3. **Test Flow independently:** Use Flow debugger in Setup with sample inputs
 622 4. **Check agent logs:** Agent Builder → Logs
 623 
 624 ---
 625 
 626 ## Related Documentation
 627 
 628 - [action-patterns.md](action-patterns.md) — Context-aware descriptions, instruction references, binding strategies
 629 - [action-prompt-templates.md](action-prompt-templates.md) — Prompt template invocation (`generatePromptResponse://`)
 630 - [fsm-architecture.md](fsm-architecture.md) — FSM design and node patterns
