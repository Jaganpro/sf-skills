<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Migration Guide: Agentforce Builder UI → Agent Script DSL
   2 
   3 > This guide maps every concept from the Agentforce Builder UI (Setup > Agents) to its Agent Script DSL equivalent. Use it when converting existing agents from the visual builder to code.
   4 
   5 ---
   6 
   7 ## Builder UI → Agent Script Mapping
   8 
   9 | # | Builder UI Concept | Agent Script Equivalent | Notes |
  10 |---|-------------------|------------------------|-------|
  11 | 1 | Topic name | `topic my_topic_name:` | Must use snake_case, max 80 chars |
  12 | 2 | Classification description | `description: "..."` on topic | Helps LLM decide when to enter topic |
  13 | 3 | Scope / "What this topic can do" | `reasoning.instructions` + available `actions` | Combined: instructions tell LLM what to do, actions tell it what tools are available |
  14 | 4 | Instructions (numbered text boxes) | `reasoning: instructions:` | Use `->` for logic/expressions, `\|` for literal text |
  15 | 5 | Flow actions | `target: flow://FlowName` | Flow must be Autolaunched and Active |
  16 | 6 | Apex actions | `target: apex://ClassName` | Class must have `@InvocableMethod` |
  17 | 7 | Prompt Template actions | `target: generatePromptResponse://TemplateName` | Template must exist in org |
  18 | 8 | "Collect from user" input | Slot-fill `...` operator | `with query = ...` — LLM extracts from conversation |
  19 | 9 | "Show/Hide in conversation" toggle | `filter_from_agent: True` | On action output definitions |
  20 | 10 | "Require Confirmation" toggle | `require_user_confirmation: True` | On action definitions |
  21 | 11 | Guard Conditions | `available when` clause | `available when @variables.verified == True` |
  22 
  23 ---
  24 
  25 ## What's New in Agent Script (No Builder UI Equivalent)
  26 
  27 These capabilities exist ONLY in Agent Script — they cannot be configured through the Builder UI:
  28 
  29 | # | Feature | Description | Example |
  30 |---|---------|-------------|---------|
  31 | 1 | `before_reasoning:` hook | Deterministic pre-processing before LLM sees instructions | Set variables, load data, enforce gates |
  32 | 2 | `after_reasoning:` hook | Deterministic post-processing after LLM finishes | Logging, cleanup, audit flags |
  33 | 3 | Linked variables | Read-only variables bound to session/context sources | `source: @MessagingSession.Id` |
  34 | 4 | Per-topic `system.instructions` override | Different system prompts for different topics | Customize LLM persona per topic |
  35 | 5 | Topic delegation (supervision) | Call a topic as a function — it returns to caller | `@topic.expert` in `reasoning.actions` |
  36 | 6 | Conditional transitions with `if/else` | Deterministic routing based on variable state | `if @variables.risk >= 80: transition to @topic.escalation` |
  37 | 7 | Template arithmetic | Expression evaluation in text templates | `{!@variables.x + 1}` |
  38 | 8 | Post-action loop pattern | Topic re-resolves after action, enabling check-at-top pattern | Deterministic post-action routing |
  39 | 9 | Latch variables | Force topic re-entry after user provides input | Workaround for topic selector limitations |
  40 | 10 | Connection block | Multi-channel escalation routing (messaging, voice) | Service Agent channel-specific escalation |
  41 
  42 ---
  43 
  44 ## Side-by-Side: Simple Topic
  45 
  46 ### Builder UI Configuration
  47 
  48 ```
  49 Topic Name: Order Lookup
  50 Classification: Handles customer order status inquiries
  51 
  52 Instructions:
  53   1. Ask the customer for their order number
  54   2. Look up the order using the Get Order Details action
  55   3. Share the order status with the customer
  56 
  57 Actions:
  58   - Get Order Details (Flow: Get_Order_Details)
  59     Input: order_id (Collect from user)
  60     Output: status, estimated_delivery
  61 ```
  62 
  63 ### Agent Script Equivalent
  64 
  65 ```yaml
  66 topic order_lookup:
  67    description: "Handles customer order status inquiries"
  68 
  69    actions:
  70       get_order_details:
  71          description: "Retrieves order information by order ID"
  72          inputs:
  73             order_id: string
  74                description: "Customer's order number"
  75          outputs:
  76             status: string
  77                description: "Current order status"
  78             estimated_delivery: string
  79                description: "Estimated delivery date"
  80          target: "flow://Get_Order_Details"
  81 
  82    reasoning:
  83       instructions: ->
  84          # Post-action check (if order was already looked up)
  85          if @variables.order_status != "":
  86             | Your order status is: {!@variables.order_status}
  87             | Estimated delivery: {!@variables.estimated_delivery}
  88 
  89          | I can help you check your order status.
  90          | Please provide your order number.
  91       actions:
  92          lookup: @actions.get_order_details
  93             with order_id = ...
  94             set @variables.order_status = @outputs.status
  95             set @variables.estimated_delivery = @outputs.estimated_delivery
  96 ```
  97 
  98 **Key differences in the Agent Script version:**
  99 - Explicit action definition with typed inputs/outputs and target
 100 - Post-action check pattern (at TOP of instructions) enables deterministic routing after the action completes
 101 - Variable injection (`{!@variables.X}`) for dynamic text
 102 - Slot-fill (`...`) replaces "Collect from user"
 103 
 104 ---
 105 
 106 ## Side-by-Side: Verification Gate
 107 
 108 ### Builder UI Configuration
 109 
 110 ```
 111 Topic Name: Identity Verification
 112 Classification: Verifies customer identity before accessing account
 113 
 114 Instructions:
 115   1. Ask the customer for their email address
 116   2. Use the Verify Identity action to check their email
 117   3. If verified, route to the Account Management topic
 118   4. After 3 failed attempts, escalate to a human agent
 119 
 120 Actions:
 121   - Verify Identity (Apex: VerifyIdentityAction)
 122     Input: email (Collect from user)
 123     Output: verified (boolean)
 124   - Go to Account Management (Topic Transition)
 125   - Escalate (Escalate to Agent)
 126 ```
 127 
 128 ### Agent Script Equivalent
 129 
 130 ```yaml
 131 variables:
 132    customer_verified: mutable boolean = False
 133    failed_attempts: mutable number = 0
 134 
 135 topic identity_verification:
 136    description: "Verifies customer identity before accessing account"
 137 
 138    actions:
 139       verify_identity:
 140          description: "Checks customer identity by email"
 141          inputs:
 142             email: string
 143                description: "Customer email address"
 144          outputs:
 145             verified: boolean
 146                description: "Whether identity was verified"
 147          target: "apex://VerifyIdentityAction"
 148 
 149    reasoning:
 150       instructions: ->
 151          # Gate: Too many failures → escalate
 152          if @variables.failed_attempts >= 3:
 153             | Too many failed attempts. Connecting you with a human agent.
 154             transition to @topic.escalation
 155 
 156          # Gate: Already verified → proceed
 157          if @variables.customer_verified == True:
 158             transition to @topic.account_management
 159 
 160          | Please provide your email address to verify your identity.
 161       actions:
 162          verify: @actions.verify_identity
 163             with email = ...
 164             set @variables.customer_verified = @outputs.verified
 165             if @outputs.verified == False:
 166                set @variables.failed_attempts = @variables.failed_attempts + 1
 167          go_account: @utils.transition to @topic.account_management
 168             description: "Proceed to account management"
 169             available when @variables.customer_verified == True
 170          escalate_now: @utils.escalate
 171             description: "Transfer to human agent"
 172 ```
 173 
 174 **Key differences in the Agent Script version:**
 175 - Deterministic gates at top of instructions (cannot be bypassed by LLM)
 176 - Explicit failure counter with arithmetic
 177 - `available when` guard ensures the "proceed" action is invisible until verified
 178 - `@utils.escalate` replaces the UI "Escalate to Agent" button
 179 
 180 ---
 181 
 182 ## Migration Checklist
 183 
 184 When converting a Builder UI agent to Agent Script:
 185 
 186 - [ ] **Export current config**: Document all topics, instructions, and actions from the UI
 187 - [ ] **Map each topic**: Use the mapping table above to translate concepts
 188 - [ ] **Identify implicit logic**: Builder UI often has implicit routing — make it explicit with `if/else`
 189 - [ ] **Add deterministic gates**: Convert any "instruction-based" security to `available when` guards
 190 - [ ] **Define variables**: Builder UI hides state management — declare all needed variables explicitly
 191 - [ ] **Set action targets**: Ensure all Flows/Apex classes are deployed with correct API names
 192 - [ ] **Test incrementally**: Validate each topic independently before combining
 193 - [ ] **Verify `default_agent_user`**: Must be a valid Einstein Agent User in the target org
 194 
 195 ---
 196 
 197 ## Common Migration Pitfalls
 198 
 199 | Pitfall | Description | Fix |
 200 |---------|-------------|-----|
 201 | Missing deterministic logic | Builder UI relies on LLM to follow instructions; Agent Script should enforce with code | Add `if/else` gates and `available when` guards |
 202 | Implicit routing | Builder UI auto-routes between topics; Agent Script needs explicit transitions | Add `@utils.transition` actions for each topic change |
 203 | Action naming conflicts | Builder UI action names may conflict with reserved words | Rename to avoid `description`, `label`, `escalate` |
 204 | Missing variable declarations | Builder UI manages state implicitly | Declare all mutable/linked variables explicitly |
 205 | Wrong instruction syntax | Builder UI text → `\|` (pipe) syntax; conditional logic → `->` (arrow) syntax | Use arrow when you need `if`, `run`, `set`, or `transition` |
 206 
 207 ---
 208 
 209 *Last updated: 2026-02-12*
