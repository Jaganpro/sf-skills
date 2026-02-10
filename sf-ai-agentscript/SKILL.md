---
name: sf-ai-agentscript
description: >
  Agent Script DSL development skill for Salesforce Agentforce.
  Enables writing deterministic agents in a single .agent file with
  FSM architecture, instruction resolution, and hybrid reasoning.
  Covers syntax, debugging, testing, and CLI deployment.
license: MIT
compatibility: "Requires Agentforce license, API v65.0+, Einstein Agent User"
metadata:
  version: "1.7.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 6 categories"
  validated: "0-shot generation tested (Pet_Adoption_Advisor, TechCorp_IT_Agent, Quiz_Master, Expense_Calculator, Order_Processor)"
  # Validation Framework
  last_validated: "2026-01-20"
  validation_status: "PASS"
  validation_agents: 13
  validate_by: "2026-02-19"  # 30 days from last validation
  validation_org: "R6-Agentforce-SandboxFull"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/agentscript-syntax-validator.py"
          timeout: 10000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-ai-agentscript"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-ai-agentscript"
      timeout: 5000
---

# SF-AI-AgentScript Skill

> **"Prompt engineering is like writing laws in poetry - beautiful, but not enforceable."**

Agent Script transforms agent development from prompt-based suggestions to **code-enforced guarantees**. This skill guides you through writing, debugging, testing, and deploying Agentforce agents using the Agent Script DSL.

---

## ⚠️ CRITICAL WARNINGS

### API & Version Requirements
| Requirement | Value | Notes |
|-------------|-------|-------|
| **API Version** | 65.0+ | Required for Agent Script support |
| **License** | Agentforce | Required for agent authoring |
| **Einstein Agent User** | Required | Must exist in org for `default_agent_user` |
| **File Extension** | `.agent` | Single file contains entire agent definition |

### MANDATORY Pre-Deployment Checks
1. **`default_agent_user` MUST be valid** - Query: `SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true`
2. **No mixed tabs/spaces** - Use consistent indentation (2-space, 3-space, or tabs - never mix)
3. **Booleans are capitalized** - Use `True`/`False`, not `true`/`false`
4. **Exactly one `start_agent` block** - Multiple entry points cause compilation failure

### ⛔ SYNTAX CONSTRAINTS (Validated via Testing + Official Spec)

| Constraint | ❌ WRONG | ✅ CORRECT |
|------------|----------|-----------|
| **No nested if statements** | `if x:` then `if y:` (nested) | `if x and y:` (compound) OR flatten to sequential ifs |
| **No top-level `actions:` block** | `actions:` at root level | Actions only inside `topic.reasoning.actions:` |
| **No `inputs:`/`outputs:` in actions** | `inputs:` block inside action | Use `with` for inputs, `set` for outputs |
| **One `available when` per action** | Two `available when` clauses | `available when A and B` |
| **Avoid reserved action names** | `escalate: @utils.escalate` | `escalate_now: @utils.escalate` |
| **`...` is slot-filling only** | `my_var: mutable string = ...` | `my_var: mutable string = ""` |
| **No defaults on linked vars** | `id: linked string = ""` | `id: linked string` + `source:` |
| **Linked vars: no object/list** | `data: linked object` | Use `linked string` or parse in Flow |
| **Post-action only on @actions** | `@utils.X` with `set`/`run` | Only `@actions.X` supports post-action |
| **agent_name must match folder** | Folder: `MyAgent`, config: `my_agent` | Both must be identical (case-sensitive) |
| **Reserved field names** | `description: string`, `label: string` | Use `descriptions`, `label_text`, or suffix with `_field` |

### 🔴 Reserved Field Names (Breaking in Recent Releases)

Common field names that cause parse errors:
```
❌ RESERVED (cannot use as variable/field names):
description, label, is_required, is_displayable, is_used_by_planner

✅ WORKAROUNDS:
description  → descriptions, description_text, desc_field
label        → label_text, display_label, label_field
```

### 🔴 Features NOT Valid in Current Release (TDD Validated 2026-01-20)

> **These features appear in documentation or recipes but do NOT compile in Winter '26.**

| Feature | Where Mentioned | Error | Status |
|---------|-----------------|-------|--------|
| `label:` on topics | agentforce.guide | `Unexpected 'label'` | ❌ NOT valid anywhere |
| `label:` on actions | agentforce.guide | `Unexpected 'label'` | ❌ NOT valid anywhere |
| `always_expect_input:` | Some docs | `Unexpected 'always_expect_input'` | ❌ NOT implemented |
| `require_user_confirmation:` on transitions | Recipes | `Unexpected 'require_user_confirmation'` | ❌ NOT valid on `@utils.transition` |
| `include_in_progress_indicator:` on transitions | Recipes | `Unexpected 'include_in_progress_indicator'` | ❌ NOT valid on `@utils.transition` |
| `output_instructions:` on transitions | Recipes | `Unexpected 'output_instructions'` | ❌ NOT valid on `@utils.transition` |
| `progress_indicator_message:` on transitions | Recipes | `Unexpected 'progress_indicator_message'` | ❌ May only work on `flow://` targets |

**What DOES work on `@utils.transition` actions:**
```yaml
actions:
   go_next: @utils.transition to @topic.next
      description: "Navigate to next topic"   # ✅ ONLY this works
```

> **Note**: Some of these may work on `flow://` action targets (not validated). The `@utils.transition` utility action has limited property support.

### 🔴 `complex_data_type_name` Mapping Table (Critical for Actions)

> **"#1 source of compile errors"** - Use this table when defining action inputs/outputs in Agentforce Assets.

| Data Type | `complex_data_type_name` Value | Notes |
|-----------|-------------------------------|-------|
| `string` | *(none needed)* | Primitive type |
| `number` | *(none needed)* | Primitive type |
| `boolean` | *(none needed)* | Primitive type |
| `object` (SObject) | `lightning__recordInfoType` | Use for Account, Contact, etc. |
| `list[string]` | `lightning__textType` | Collection of text values |
| `list[object]` | `lightning__textType` | Serialized as JSON text |
| Apex Inner Class | `@apexClassType/NamespacedClass__InnerClass` | Namespace required |
| Custom LWC Type | `lightning__c__CustomTypeName` | Custom component types |
| Currency field | `lightning__currencyType` | For monetary values |

**Pro Tip**: Don't manually edit `complex_data_type_name` - use the UI dropdown in **Agentforce Assets > Action Definition**, then export/import the action definition.

### ⚠️ Canvas View Corruption Bugs

> **CRITICAL**: Canvas view can silently corrupt Agent Script syntax. Make complex edits in **Script view**.

| Original Syntax | Canvas Corrupts To | Impact |
|-----------------|-------------------|--------|
| `==` | `{! OPERATOR.EQUAL }` | Breaks conditionals |
| `if condition:` | `if condition` (missing colon) | Parse error |
| `with email =` | `with @inputs.email =` | Invalid syntax |
| 4-space indent | De-indented (breaks nesting) | Structure lost |
| `@topic.X` (supervision) | `@utils.transition to @topic.X` (handoff) | Changes return behavior |
| `A and B` | `A {! and } B` | Breaks compound conditions |

**Safe Workflow**:
1. Use **Script view** for all structural edits (conditionals, actions, transitions)
2. Use Canvas only for visual validation and simple text changes
3. **Always review in Script view** after any Canvas edit

### ⚠️ Preview Mode Critical Bugs

> **CRITICAL REFRESH BUG**: Browser refresh required after **every** Agent Script save before preview works properly.

| Issue | Error Message | Workaround |
|-------|---------------|------------|
| Linked vars in context, not state | `"Cannot access 'X': Not a declared field in dict"` | Convert to mutable + hardcode for testing |
| Output property access fails | Silent failure, no error | Assign to variable first, then use in conditional |
| Simulate vs Live behavior differs | Works in Simulate, fails in Live | Test in **BOTH** modes before committing |

**Pattern for Testing Linked Variables:**
```yaml
# ❌ DOESN'T WORK IN PREVIEW (linked var from session):
RoutableId: linked string
   source: @MessagingSession.Id

# ✅ WORKAROUND FOR TESTING (hardcode value):
RoutableId: mutable string = "test-session-123"
   description: "MessagingSession Id (hardcoded for testing)"

# After testing, switch back to linked for production
```

**Output Property Access Pattern:**
```yaml
# ❌ DOESN'T WORK IN PREVIEW (direct output access):
if @actions.check_status.result == "approved":
   | Approved!

# ✅ CORRECT (assign to variable first):
set @variables.status = @outputs.result
if @variables.status == "approved":
   | Approved!
```

#### No Nested `if` - Two Valid Approaches
```yaml
# ❌ WRONG - Nested if (causes SyntaxError)
if @variables.software_cost > 0:
   if @variables.software_cost <= 500:
      | Auto-approve this software request.

# ✅ CORRECT Approach 1 - Compound condition (when logic allows)
if @variables.software_cost > 0 and @variables.software_cost <= 500:
   | Auto-approve this software request.

# ✅ CORRECT Approach 2 - Flatten to sequential ifs (for separate messages)
if @variables.order_verified == False or @variables.payment_confirmed == False:
   | ❌ **PROCESSING BLOCKED**
   | Missing requirements:

if @variables.order_verified == False:
   | - Order verification pending

if @variables.payment_confirmed == False:
   | - Payment confirmation pending
```
> **When to use each**: Use compound conditions when logic permits (single condition block). Use flattening when you need separate conditional outputs that can't be combined.

#### `...` is Slot-Filling Syntax (LLM Extracts from Conversation)
```yaml
# ❌ WRONG - Using ... as default value
order_id: mutable string = ...

# ✅ CORRECT - Use ... only in action parameter binding
reasoning:
   actions:
      search: @actions.search_products
         with query=...           # LLM extracts from user message
         with category=...        # LLM decides based on context
         with limit=10            # Fixed value
```

#### Post-Action Directives: Only on `@actions.*`
```yaml
# ❌ WRONG - @utils does NOT support set/run/if
go_next: @utils.transition to @topic.main
   set @variables.visited = True   # ERROR!

# ✅ CORRECT - Only @actions.* supports post-action
process: @actions.process_order
   with order_id=@variables.order_id
   set @variables.status = @outputs.status        # ✅ Works
   run @actions.send_notification                 # ✅ Works
   if @outputs.needs_review:                      # ✅ Works
      transition to @topic.review
```

#### Helper Topic Pattern (For Demo Agents Without Flows/Apex)
When you need to set variables without backend actions, use dedicated "helper topics":
```yaml
# Main topic offers LLM-selectable action
topic verify_employee:
   reasoning:
      actions:
         complete_verification: @utils.transition to @topic.verification_success
            description: "Mark employee as verified"
            available when @variables.employee_verified == False

# Helper topic sets variables in instructions, then returns
topic verification_success:
   description: "Set verified state and return"
   reasoning:
      instructions: ->
         set @variables.employee_verified = True
         set @variables.employee_name = "Demo Employee"
         | ✓ Identity verified!
         transition to @topic.verify_employee  # Return to parent
```
> **Why this works**: `set` statements ARE valid inside `instructions: ->` blocks. The topic loop pattern lets you change state without Flows/Apex.

---

## 💰 PRODUCTION GOTCHAS: Billing, Determinism & Performance

### Credit Consumption Table

> **Key insight**: Framework operations are FREE. Only actions that invoke external services consume credits.

| Operation | Credits | Notes |
|-----------|---------|-------|
| `@utils.transition` | FREE | Framework navigation |
| `@utils.setVariables` | FREE | Framework state management |
| `@utils.escalate` | FREE | Framework escalation |
| `if`/`else` control flow | FREE | Deterministic resolution |
| `before_reasoning` | FREE | Deterministic pre-processing (see note below) |
| `after_reasoning` | FREE | Deterministic post-processing (see note below) |
| `reasoning` (LLM turn) | FREE | LLM reasoning itself is not billed |
| Prompt Templates | 2-16 | Per invocation (varies by complexity) |
| Flow actions | 20 | Per action execution |
| Apex actions | 20 | Per action execution |
| Any other action | 20 | Per action execution |

> **✅ Lifecycle Hooks Validated (v1.3.0)**: The `before_reasoning:` and `after_reasoning:` lifecycle hooks are now TDD-validated. Content goes **directly** under the block (no `instructions:` wrapper). See "Lifecycle Hooks" section below for correct syntax.

**Cost Optimization Pattern**: Fetch data once in `before_reasoning:`, cache in variables, reuse across topics.

### Lifecycle Hooks: `before_reasoning:` and `after_reasoning:`

> **TDD Validated (2026-01-20)**: These hooks enable deterministic pre/post-processing around LLM reasoning.

```yaml
topic main:
   description: "Topic with lifecycle hooks"

   # BEFORE: Runs deterministically BEFORE LLM sees instructions
   before_reasoning:
      # Content goes DIRECTLY here (NO instructions: wrapper!)
      set @variables.pre_processed = True
      set @variables.customer_tier = "gold"

   # LLM reasoning phase
   reasoning:
      instructions: ->
         | Customer tier: {!@variables.customer_tier}
         | How can I help you today?

   # AFTER: Runs deterministically AFTER LLM finishes reasoning
   after_reasoning:
      # Content goes DIRECTLY here (NO instructions: wrapper!)
      set @variables.interaction_logged = True
      if @variables.needs_audit == True:
         set @variables.audit_flag = True
```

**Key Points:**
- Content goes **directly** under `before_reasoning:` / `after_reasoning:` (NO `instructions:` wrapper)
- Supports `set`, `if`, `run` statements (same as procedural `instructions: ->`)
- `before_reasoning:` is FREE (no credit cost) - use for data prep
- `after_reasoning:` is FREE (no credit cost) - use for logging, cleanup

**❌ WRONG Syntax (causes compile error):**
```yaml
before_reasoning:
   instructions: ->      # ❌ NO! Don't wrap with instructions:
      set @variables.x = True
```

**✅ CORRECT Syntax:**
```yaml
before_reasoning:
   set @variables.x = True   # ✅ Direct content under the block
```

### Supervision vs Handoff (Clarified Terminology)

| Term | Syntax | Behavior | Use When |
|------|--------|----------|----------|
| **Handoff** | `@utils.transition to @topic.X` | Control transfers completely, child generates final response | Checkout, escalation, terminal states |
| **Supervision** | `@topic.X` (as action reference) | Parent orchestrates, child returns, parent synthesizes | Expert consultation, sub-tasks |

```yaml
# HANDOFF - child topic takes over completely:
checkout: @utils.transition to @topic.order_checkout
   description: "Proceed to checkout"
# → @topic.order_checkout generates the user-facing response

# SUPERVISION - parent remains in control:
get_advice: @topic.product_expert
   description: "Consult product expert"
# → @topic.product_expert returns, parent topic synthesizes final response
```

**KNOWN BUG**: Adding ANY new action in Canvas view may inadvertently change Supervision references to Handoff transitions.

### Action Output Flags for Zero-Hallucination Routing

> **Key Pattern for Determinism**: Control what the LLM can see and say.

When defining actions in Agentforce Assets, use these output flags:

| Flag | Effect | Use When |
|------|--------|----------|
| `is_displayable: False` | LLM **cannot** show this value to user | Preventing hallucinated responses |
| `is_used_by_planner: True` | LLM **can** reason about this value | Decision-making, routing |

**Zero-Hallucination Intent Classification Pattern:**
```yaml
# In Agentforce Assets - Action Definition outputs:
outputs:
   intent_classification: string
      is_displayable: False       # LLM cannot show this to user
      is_used_by_planner: True    # LLM can use for routing decisions

# In Agent Script - LLM routes but cannot hallucinate:
topic intent_router:
   reasoning:
      instructions: ->
         run @actions.classify_intent
         set @variables.intent = @outputs.intent_classification

         if @variables.intent == "refund":
            transition to @topic.refunds
         if @variables.intent == "order_status":
            transition to @topic.orders
```

### Action Chaining with `run` Keyword

> **Known quirk**: Parent action may complain about inputs needed by chained action - this is expected.

```yaml
# Chained action execution:
process_order: @actions.create_order
   with customer_id = @variables.customer_id
   run @actions.send_confirmation        # Chains after create_order completes
   set @variables.order_id = @outputs.id
```

**KNOWN BUG**: Chained actions with Prompt Templates don't properly map inputs using `Input:Query` format:
```yaml
# ❌ MAY NOT WORK with Prompt Templates:
run @actions.transform_recommendation
   with "Input:Reco_Input" = @variables.ProductReco

# ⚠️ TRY THIS (may still have issues):
run @actions.transform_recommendation
   with Reco_Input = @variables.ProductReco
```

> **📖 For prompt template action definitions, input binding syntax, and grounded data patterns**, see [resources/action-prompt-templates.md](resources/action-prompt-templates.md). For context-aware descriptions, instruction references (`{!@actions.X}`), and advanced binding strategies, see [resources/action-patterns.md](resources/action-patterns.md).

### Latch Variable Pattern for Topic Re-entry

> **Problem**: Topic selector doesn't properly re-evaluate after user provides missing input.

**Solution**: Use a "latch" variable to force re-entry:

```yaml
variables:
   verification_in_progress: mutable boolean = False

start_agent topic_selector:
   reasoning:
      instructions: ->
         # LATCH CHECK - force re-entry if verification was started
         if @variables.verification_in_progress == True:
            transition to @topic.verification

         | How can I help you today?
      actions:
         start_verify: @topic.verification
            description: "Start identity verification"
            # Set latch when user chooses this action
            set @variables.verification_in_progress = True

topic verification:
   reasoning:
      instructions: ->
         | Please provide your email to verify your identity.
      actions:
         verify: @actions.verify_identity
            with email = ...
            set @variables.verified = @outputs.success
            # Clear latch when verification completes
            set @variables.verification_in_progress = False
```

### Loop Protection Guardrail

> Agent Scripts have a built-in guardrail that limits iterations to approximately **3-4 loops** before breaking out and returning to the Topic Selector.

**Best Practice**: Map out your execution paths - particularly topic transitions. Ensure testing covers all paths and specifically check for unintended circular references between topics.

### Token & Size Limits

| Limit Type | Value | Notes |
|------------|-------|-------|
| Max response size | 1,048,576 bytes (1MB) | Per agent response |
| Plan trace limit (Frontend) | 1M characters | For debugging UI |
| Transformed plan trace (Backend) | 32k tokens | Internal processing |
| Active/Committed Agents per org | 100 max | Org limit |

### Progress Indicators

Add user feedback during long-running actions:

```yaml
actions:
   fetch_data: @actions.get_customer_data
      description: "Fetch customer information"
      include_in_progress_indicator: True
      progress_indicator_message: "Fetching your account details..."
```

### VS Code Pull/Push NOT Supported

```bash
# ❌ ERROR when using source tracking:
Failed to retrieve components using source tracking:
[SfError [UnsupportedBundleTypeError]: Unsupported Bundle Type: AiAuthoringBundle

# ✅ WORKAROUND - Use CLI directly:
sf project retrieve start -m AiAuthoringBundle:MyAgent
sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG
```

### Language Block Quirks

- Hebrew and Indonesian appear **twice** in the language dropdown
- Selecting from the second set causes save errors
- Use `adaptive_response_allowed: True` for automatic language adaptation

```yaml
language:
   locale: en_US
   adaptive_response_allowed: True  # Allow language adaptation
```

---

### Cross-Skill Orchestration

| Direction | Pattern | Priority |
|-----------|---------|----------|
| **Before Agent Script** | `/sf-flow` - Create Flows for `flow://` action targets | ⚠️ REQUIRED |
| **After Agent Script** | `/sf-ai-agentforce-testing` - Test topic routing and actions | ✅ RECOMMENDED |
| **For Deployment** | `/sf-deploy` - Publish agent with `sf agent publish authoring-bundle` | ⚠️ REQUIRED |

> **Tip**: Open Agentforce Studio list view with `sf org open authoring-bundle -o TARGET_ORG` (v2.121.7+). Open a specific agent with `sf org open agent --api-name MyAgent -o TARGET_ORG`.

---

## 📋 QUICK REFERENCE: Agent Script Syntax

### Block Structure (CORRECTED Order per Official Spec)
```yaml
config:        # 1. Required: Agent metadata (developer_name, agent_type, default_agent_user)
variables:     # 2. Optional: State management (mutable/linked)
system:        # 3. Required: Global messages and instructions
connections:   # 4. Optional: Escalation routing (Service Agents ONLY)
knowledge:     # 5. Optional: Knowledge base config
language:      # 6. Optional: Locale settings
start_agent:   # 7. Required: Entry point (exactly one)
topic:         # 8. Required: Conversation topics (one or more)
```

### Config Block Field Names (CRITICAL)

> ⚠️ **Common Error**: Using incorrect field names from outdated documentation.

| Documented Field (Wrong) | Actual Field (Correct) | Notes |
|--------------------------|------------------------|-------|
| `agent_name` | `developer_name` | Must match folder name (case-sensitive) |
| `description` | `agent_description` | Agent's purpose description |
| `agent_label` | *(not used)* | Remove from examples |
| `default_agent_user` | `default_agent_user` | ✓ Correct |
| *(missing)* | `agent_type` | **Required**: `AgentforceServiceAgent` or `AgentforceEmployeeAgent` |

```yaml
# ✅ CORRECT config block:
config:
  developer_name: "my_agent"
  agent_description: "Handles customer support inquiries"
  agent_type: "AgentforceServiceAgent"
  default_agent_user: "agent_user@00dxx000001234.ext"
```

### Naming Rules (All Identifiers)
- Only letters, numbers, underscores
- Must begin with a letter
- No spaces, no consecutive underscores, cannot end with underscore
- **Maximum 80 characters**

### Instruction Syntax Patterns
| Pattern | Purpose | Example |
|---------|---------|---------|
| `instructions: \|` | Literal multi-line (no expressions) | `instructions: \| Help the user.` |
| `instructions: ->` | Procedural (enables expressions) | `instructions: -> if @variables.x:` |
| `\| text` | Literal text for LLM prompt | `\| Hello` + variable injection |
| `if @variables.x:` | Conditional (resolves before LLM) | `if @variables.verified == True:` |
| `run @actions.x` | Execute action during resolution | `run @actions.load_customer` |
| `set @var = @outputs.y` | Capture action output | `set @variables.risk = @outputs.score` |
| `set @var = value` | Set variable in instructions | `set @variables.count = 0` |
| `{!@variables.x}` | Variable injection in text | `Risk score: {!@variables.risk}` |
| `{!expr if cond else alt}` | Conditional interpolation | `{!@variables.status if @variables.status else "pending"}` |
| `available when` | Control action visibility to LLM | `available when @variables.verified == True` |
| `with param=...` | LLM slot-filling (extracts from conversation) | `with query=...` |
| `with param=value` | Fixed parameter value | `with limit=10` |

### Transition vs Delegation (CRITICAL DISTINCTION)
| Syntax | Behavior | Returns? | Use When |
|--------|----------|----------|----------|
| `@utils.transition to @topic.X` | Permanent handoff | ❌ No | Checkout, escalation, final states |
| `@topic.X` (in reasoning.actions) | Delegation | ✅ Yes | Get expert advice, sub-tasks |
| `transition to @topic.X` (inline) | Deterministic jump | ❌ No | Post-action routing, gates |

```yaml
# Delegation - returns to current topic after specialist finishes
consulting: @topic.expert_topic
   description: "Get expert advice"

# Transition - permanent handoff, no return
checkout: @utils.transition to @topic.checkout
   description: "Proceed to purchase"
```

### Expression Operators (Safe Subset)
| Category | Operators | NOT Supported |
|----------|-----------|---------------|
| Comparison | `==`, `<>` (not-equal), `<`, `<=`, `>`, `>=`, `is`, `is not` | |
| Logical | `and`, `or`, `not` | |
| Arithmetic | `+`, `-` | ❌ `*`, `/`, `%` |
| Access | `.` (property), `[]` (index) | |
| Conditional | `x if condition else y` | |

### Variable Types
| Modifier | Behavior | Supported Types | Default Required? |
|----------|----------|-----------------|-------------------|
| `mutable` | Read/write state | `string`, `number`, `boolean`, `object`, `date`, `timestamp`, `currency`, `id`, `list[T]` | ✅ Yes |
| `linked` | Read-only from source | `string`, `number`, `boolean`, `date`, `timestamp`, `currency`, `id` | ❌ No (has `source:`) |

> ⚠️ **Linked variables CANNOT use `object` or `list` types**

### Linked Variable Sources by Agent Type

> ⚠️ **CRITICAL**: Not all source bindings work for all agent types.

| Source Pattern | Service Agent | Employee Agent |
|----------------|---------------|----------------|
| `@MessagingSession.Id` | ✅ Works | ❌ Not available |
| `@MessagingSession.RoutableId` | ✅ Works | ❌ Not available |
| `@Record.Id` | ❓ Untested | ❌ Does not work |
| `@context.recordId` | ❓ Untested | ❌ Does not work |

**Workaround for Employee Agents**:
Employee Agents in the Copilot panel don't automatically receive record context. Use a mutable variable and have the Flow action look up the current record.

```yaml
# ❌ DOESN'T WORK for Employee Agents:
case_id: linked string
   source: @Record.Id

# ✅ WORKAROUND - use mutable variable:
case_id: mutable string = ""
   description: "Case ID - enter or will be looked up by Flow"
```

### Variable vs Action I/O Type Matrix
> **Critical distinction**: Some types are valid ONLY for action inputs/outputs, NOT for Agent Script variables.

| Type | Variables | Action I/O | Notes |
|------|-----------|------------|-------|
| `string` | ✅ | ✅ | Universal |
| `number` | ✅ | ✅ | Universal |
| `boolean` | ✅ | ✅ | Universal |
| `date` | ✅ | ✅ | Universal |
| `currency` | ✅ | ✅ | Universal |
| `id` | ✅ | ✅ | Salesforce IDs |
| `list` | ✅ (mutable only) | ✅ | Collections |
| `object` | ✅ (mutable only) | ✅ | ⚠️ Not for linked vars |
| `datetime` | ❌ | ✅ | **Actions only** |
| `time` | ❌ | ✅ | **Actions only** |
| `integer` | ❌ | ✅ | **Actions only** |
| `long` | ❌ | ✅ | **Actions only** |

> **Source**: AGENT_SCRIPT.md rules document from trailheadapps/agent-script-recipes

### Action Target Protocols
| Short | Long Form | Use When | Validated? |
|-------|-----------|----------|------------|
| `flow` | `flow://` | Data operations, business logic | ✅ TDD |
| `apex` | `apex://` | Custom calculations, validation | ✅ TDD |
| `prompt` | `generatePromptResponse://` | Grounded LLM responses | ✅ TDD |
| `api` | `api://` | REST API calls | ✅ TDD |
| `retriever` | `retriever://` | RAG knowledge search | ✅ TDD |
| `externalService` | `externalService://` | Third-party APIs via Named Credentials | ✅ TDD |
| `standardInvocableAction` | `standardInvocableAction://` | Built-in SF actions (email, tasks) | ✅ TDD |
| `datacloudDataGraphAction` | `datacloudDataGraphAction://` | Data Cloud graph queries | 📋 Spec |
| `datacloudSegmentAction` | `datacloudSegmentAction://` | Data Cloud segment operations | 📋 Spec |
| `triggerByKnowledgeSource` | `triggerByKnowledgeSource://` | Knowledge article triggers | 📋 Spec |
| `contextGrounding` | `contextGrounding://` | Context grounding for LLM | 📋 Spec |
| `predictiveAI` | `predictiveAI://` | Einstein prediction models | 📋 Spec |
| `runAction` | `runAction://` | Execute sub-actions | 📋 Spec |
| `external` | `external://` | External service calls | 📋 Spec |
| `copilotAction` | `copilotAction://` | Salesforce Copilot actions | 📋 Spec |
| `@topic.X` | (inline) | Topic delegation (returns to parent) | ✅ TDD |

> **Legend**: ✅ TDD = Validated via deployment testing | 📋 Spec = Documented in AGENT_SCRIPT.md spec (requires specific org setup to test)

### Using Flow and Apex Actions in Agent Script

> **For AiAuthoringBundle (Agent Script)**: `flow://` and `apex://` targets work **directly** — no GenAiFunction registration needed. The target just needs to exist in the org (active Flow or deployed Apex class with `@InvocableMethod`).

**Two-Level Action System (CRITICAL to understand):**

```
Level 1: ACTION DEFINITION (in topic's `actions:` block)
   → Has `target:`, `inputs:`, `outputs:`, `description:`
   → Specifies WHAT to call (e.g., "apex://OrderService")

Level 2: ACTION INVOCATION (in `reasoning.actions:` block)
   → References Level 1 via `@actions.name`
   → Specifies HOW to call it (with/set clauses)
```

**Complete Example:**
```yaml
topic order_status:
   description: "Look up order details"

   # Level 1: DEFINE the action with a target
   actions:
      get_case_details:
         description: "Fetch case information by ID"
         inputs:
            case_id: string
               description: "The Case record ID"
         outputs:
            subject: string
               description: "Case subject line"
         target: "flow://Get_Case_Details"   # Flow must exist and be active

   reasoning:
      instructions: |
         Help the customer check their case status.
      # Level 2: INVOKE the action defined above
      actions:
         lookup_case: @actions.get_case_details
            with case_id = @variables.case_id
            set @variables.case_subject = @outputs.subject
```

> ⚠️ **Common Error**: `ValidationError: Tool target 'X' is not an action definition` — This means either:
> 1. The action is referenced in `reasoning.actions:` via `@actions.X` but `X` is not defined in the topic's `actions:` block, OR
> 2. The `target:` value points to a Flow/Apex class that doesn't exist in the org
>
> **Fix**: Ensure you have BOTH levels: action definition (with `target:`) AND action invocation (with `@actions.name`).

**Agent Builder UI Path (GenAiPlannerBundle — different workflow):**
If building agents through the Agent Builder UI (not Agent Script), you DO need GenAiFunction metadata. See `resources/actions-reference.md` for details.

### Connection Block (Full Escalation Pattern)

> ⚠️ **Service Agents Only**: The `connections:` block is only valid for `agent_type: "AgentforceServiceAgent"`. Employee Agents will fail with `Unexpected 'connections' block` error. Employee Agents do not support channel-based escalation routing.

```yaml
connections:
   # Messaging channel escalation
   connection messaging:
      escalation_message: "One moment, I'm transferring our conversation to get you more help."
      outbound_route_type: "OmniChannelFlow"
      outbound_route_name: "<flow://Escalate_Messaging_To_Live_Agent>"
      adaptive_response_allowed: False

   # Voice channel escalation
   connection voice:
      escalation_message: "Please hold while I transfer you to a specialist."
      outbound_route_type: "Queue"
      outbound_route_name: "Support_Queue"
      adaptive_response_allowed: True

   # Web chat escalation
   connection web:
      escalation_message: "Connecting you with a live agent now."
      outbound_route_type: "OmniChannelFlow"
      outbound_route_name: "<flow://Web_Chat_Escalation>"
```

**Key Properties:**
| Property | Required | Description |
|----------|----------|-------------|
| `escalation_message` | ✅ | Message shown to user during handoff |
| `outbound_route_type` | ✅ | `OmniChannelFlow`, `Queue`, or `Skill` |
| `outbound_route_name` | ✅ | Flow API name or Queue name |
| `adaptive_response_allowed` | ❌ | Allow LLM to adapt escalation message |

---

## 🔄 WORKFLOW: Agent Development Lifecycle

### Phase 1: Requirements & Design
1. **Identify deterministic vs. subjective logic**
   - Deterministic: Security checks, financial thresholds, data lookups, counters
   - Subjective: Greetings, context understanding, natural language generation
2. **Design FSM architecture** - Map topics as states, transitions as edges
3. **Define variables** - Mutable for state tracking, linked for session context

### Phase 2: Agent Script Authoring
1. **Create `.agent` file** with required blocks
2. **Write topics** with instruction resolution pattern:
   - Post-action checks at TOP (triggers on loop)
   - Pre-LLM data loading
   - Dynamic instructions for LLM
3. **Configure actions** with appropriate target protocols
4. **Add `available when` guards** to enforce security

### Phase 3: Validation (LSP + CLI)

> **AUTOMATIC**: LSP validation runs on every Write/Edit to `.agent` files. Errors are reported with line numbers and autofix suggestions.

#### LSP Validation Loop (Find Error → Autofix)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Write/Edit  │ ──▶ │ LSP Analyze │ ──▶ │ Report      │
│ .agent file │     │ (automatic) │     │ Errors      │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
      ┌────────────────────────────────────────┘
      ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Claude      │ ──▶ │ Apply Fix   │ ──▶ │ Re-validate │
│ Suggests Fix│     │ (Edit tool) │     │ (loop)      │
└─────────────┘     └─────────────┘     └─────────────┘
```

#### LSP Checks (Automatic)
| Check | Severity | Autofix |
|-------|----------|---------|
| Mixed tabs/spaces | ❌ Error | Convert to consistent spacing |
| Lowercase booleans (`true`/`false`) | ❌ Error | Capitalize to `True`/`False` |
| Missing required blocks | ❌ Error | Add missing block template |
| Missing `default_agent_user` | ❌ Error | Add placeholder with comment |
| Mutable + linked conflict | ❌ Error | Remove conflicting modifier |
| Undefined topic references | ⚠️ Warning | Create topic stub |
| Post-action check position | ⚠️ Warning | Move to top of instructions |

#### CLI Validation (Before Deploy)
```bash
# Validate authoring bundle syntax
sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG
```

#### Manual Checks
- `default_agent_user` exists and is active Einstein Agent User
- All topic references resolve to existing topics
- Action targets (`flow://`, `apex://`, etc.) exist in org

### Phase 4: Testing (Delegate to `/sf-ai-agentforce-testing`)
1. **Batch testing** - Run up to 100 test cases simultaneously
2. **Quality metrics** - Completeness, Coherence, Topic/Action Assertions
3. **LLM-as-Judge** - Automated scoring against golden responses

### Phase 5: Deployment

> ⚠️ **CRITICAL**: Use `sf agent publish authoring-bundle`, NOT `sf project deploy start`

1. **Create bundle directory**: `force-app/main/default/aiAuthoringBundles/AgentName/`
2. **Add files**:
   - `AgentName.agent` - Your Agent Script
   - `AgentName.bundle-meta.xml` - Metadata XML (NOT `.aiAuthoringBundle-meta.xml`)
3. **Publish**: `sf agent publish authoring-bundle --api-name AgentName -o TARGET_ORG`
4. **Monitor** - Use trace debugging for production issues

### Phase 5.5: API Channel Enablement (For Agent Runtime API Testing)

> ⚠️ **Without these steps, Agent Runtime API calls return `500 Internal Server Error`.**

After publishing an Agent Script agent, the following metadata must be configured for API access:

**1. GenAiPlannerBundle — Add `plannerSurfaces` block:**

When deploying via the `Agent` pseudo metadata type, retrieve and verify the `GenAiPlannerBundle` XML includes:
```xml
<GenAiPlannerBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <!-- ... existing elements ... -->
    <plannerSurfaces>
        <plannerSurface>
            <surfaceType>EinsteinAgentApiChannel</surfaceType>
        </plannerSurface>
    </plannerSurfaces>
</GenAiPlannerBundle>
```

If missing, add it and redeploy:
```bash
sf project deploy start --metadata GenAiPlannerBundle:AgentName_Planner -o TARGET_ORG
```

**2. BotVersion — Set `surfacesEnabled` to `true`:**

The `BotVersion` metadata defaults `surfacesEnabled` to `false`. Update:
```xml
<BotVersion xmlns="http://soap.sforce.com/2006/04/metadata">
    <!-- ... existing elements ... -->
    <surfacesEnabled>true</surfacesEnabled>
</BotVersion>
```

```bash
sf project deploy start --metadata BotVersion:AgentName.v1 -o TARGET_ORG
```

**3. External Client App (ECA) — Required for Client Credentials flow:**

The Agent Runtime API requires OAuth with `chatbot_api`, `sfap_api`, and `api` scopes. See `/sf-connected-apps` for ECA creation.

> **Note:** If you only need interactive testing via `sf agent preview`, skip ECA setup — preview uses standard org auth (`sf org login web`, v2.121.7+).

**Validation — Confirm API access works:**
```bash
# Acquire token
curl -X POST "https://YOUR_DOMAIN.my.salesforce.com/services/oauth2/token" \
  -d "grant_type=client_credentials&client_id=KEY&client_secret=SECRET"

# Create agent session
curl -X POST "https://YOUR_DOMAIN.my.salesforce.com/einstein/ai-agent/v1" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agentDefinitionId":"0XxXXXXXXXXXXXXXXX"}'
```

> **Symptom**: 500 error with `"errorCode": "UNKNOWN_EXCEPTION"` → Missing `plannerSurfaces` or `surfacesEnabled=false`.

### Phase 6: CLI Operations
```bash
# Retrieve from org
sf agent retrieve --name MyAgent --target-org sandbox

# Validate syntax
sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG

# Publish to org (NOT sf project deploy!)
sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG

# Generate authoring bundle scaffolding
sf agent generate authoring-bundle --api-name MyAgent -o TARGET_ORG

# Generate without retrieving from org (useful for CI/CD)
sf agent generate authoring-bundle --api-name MyAgent --skip-retrieve -o TARGET_ORG
```

### Bundle Structure (CRITICAL)
```
force-app/main/default/aiAuthoringBundles/
└── MyAgent/
    ├── MyAgent.agent              # Agent Script file
    └── MyAgent.bundle-meta.xml    # NOT .aiAuthoringBundle-meta.xml!
```

**bundle-meta.xml content:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

---

## 📊 SCORING SYSTEM (100 Points)

### Categories

| Category | Points | Key Criteria |
|----------|--------|--------------|
| **Structure & Syntax** | 20 | Block ordering, indentation consistency, required fields present |
| **Deterministic Logic** | 25 | Security via `available when`, post-action checks, proper conditionals |
| **Instruction Resolution** | 20 | Correct use of `->` vs `\|`, template injection, action execution |
| **FSM Architecture** | 15 | Clear topic separation, explicit transitions, state management |
| **Action Configuration** | 10 | Correct protocols, input/output mapping, error handling |
| **Deployment Readiness** | 10 | Valid `default_agent_user`, no compilation errors, metadata complete |

### Scoring Rubric Details

#### Structure & Syntax (20 points)
| Points | Criteria |
|--------|----------|
| 20 | All required blocks present, consistent indentation, valid identifiers |
| 15 | Minor issues (e.g., inconsistent spacing within tolerance) |
| 10 | Missing optional blocks that would improve clarity |
| 5 | Block ordering issues or mixed indentation |
| 0 | Missing required blocks or compilation failures |

#### Deterministic Logic (25 points)
| Points | Criteria |
|--------|----------|
| 25 | All security actions guarded with `available when`, post-action patterns used |
| 20 | Most guards present, minor gaps in deterministic enforcement |
| 15 | Some security logic relies on prompts instead of guards |
| 10 | Critical actions lack `available when` guards |
| 0 | Security logic entirely prompt-based (LLM can bypass) |

#### Instruction Resolution (20 points)
| Points | Criteria |
|--------|----------|
| 20 | Arrow syntax for complex logic, proper template injection, correct action execution |
| 15 | Mostly correct, minor syntax issues |
| 10 | Uses pipe syntax where arrow needed, template injection errors |
| 5 | Incorrect phase ordering (data loads after LLM sees instructions) |
| 0 | Fundamental misunderstanding of resolution order |

#### FSM Architecture (15 points)
| Points | Criteria |
|--------|----------|
| 15 | Clear topic boundaries, explicit transitions, appropriate escalation paths |
| 12 | Good structure with minor redundancy |
| 9 | Topics too broad or transitions unclear |
| 5 | Monolithic topic handling multiple concerns |
| 0 | No topic separation, all logic in start_agent |

#### Action Configuration (10 points)
| Points | Criteria |
|--------|----------|
| 10 | Correct protocols, proper I/O mapping, descriptions present |
| 8 | Minor issues (missing descriptions) |
| 5 | Wrong protocol for use case |
| 2 | Input/output mapping errors |
| 0 | Actions don't compile |

#### Deployment Readiness (10 points)
| Points | Criteria |
|--------|----------|
| 10 | Valid user, clean validation, metadata complete |
| 8 | Minor warnings |
| 5 | Validation errors that need fixing |
| 2 | Missing metadata files |
| 0 | Cannot deploy |

### Score Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | ⭐⭐⭐⭐⭐ Excellent | Deploy with confidence |
| 80-89 | ⭐⭐⭐⭐ Very Good | Minor improvements recommended |
| 70-79 | ⭐⭐⭐ Good | Review flagged issues before deploy |
| 60-69 | ⭐⭐ Needs Work | Address issues before deploy |
| <60 | ⭐ Critical | **BLOCK** - Fix critical issues |

### Score Report Format
```
📊 AGENT SCRIPT SCORE REPORT
════════════════════════════════════════

Score: 85/100 ⭐⭐⭐⭐ Very Good
├─ Structure & Syntax:    18/20 (90%)
├─ Deterministic Logic:   22/25 (88%)
├─ Instruction Resolution: 16/20 (80%)
├─ FSM Architecture:      12/15 (80%)
├─ Action Configuration:   9/10 (90%)
└─ Deployment Readiness:   8/10 (80%)

Issues:
⚠️ [Deterministic] Missing `available when` on process_refund action
⚠️ [Resolution] Post-action check should be at TOP of instructions
✓ All Structure & Syntax checks passed
✓ All Action Configuration checks passed
```

---

## 🔧 THE 6 DETERMINISTIC BUILDING BLOCKS

These execute as **code**, not suggestions. The LLM cannot override them.

| # | Block | Description | Example |
|---|-------|-------------|---------|
| 1 | **Conditionals** | if/else resolves before LLM | `if @variables.attempts >= 3:` |
| 2 | **Topic Filters** | Control action visibility | `available when @variables.verified == True` |
| 3 | **Variable Checks** | Numeric/boolean comparisons | `if @variables.churn_risk >= 80:` |
| 4 | **Inline Actions** | Immediate execution | `run @actions.load_customer` |
| 5 | **Utility Actions** | Built-in helpers | `@utils.transition`, `@utils.escalate` |
| 6 | **Variable Injection** | Template values | `{!@variables.customer_name}` |

---

## 📐 ARCHITECTURE PATTERNS

### Pattern 1: Hub and Spoke
Central router (hub) to specialized topics (spokes). Use for multi-purpose agents.
```
       ┌─────────────┐
       │ topic_sel   │
       │   (hub)     │
       └──────┬──────┘
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│refunds │ │ orders │ │support │
└────────┘ └────────┘ └────────┘
```

### Pattern 2: Verification Gate
Security gate before protected topics. Mandatory for sensitive data.
```
┌─────────┐     ┌──────────┐     ┌───────────┐
│  entry  │ ──▶ │ VERIFY   │ ──▶ │ protected │
└─────────┘     │  (GATE)  │     │  topics   │
                └────┬─────┘     └───────────┘
                     │ 3 fails
                     ▼
                ┌──────────┐
                │ lockout  │
                └──────────┘
```

### Pattern 3: Post-Action Loop
Topic re-resolves after action completes - put checks at TOP.
```yaml
topic refund:
  reasoning:
    instructions: ->
      # POST-ACTION CHECK (at TOP - triggers on next loop)
      if @variables.refund_status == "Approved":
        run @actions.create_crm_case
        transition to @topic.success

      # PRE-LLM DATA LOADING
      run @actions.check_churn_risk
      set @variables.risk = @outputs.score

      # DYNAMIC INSTRUCTIONS FOR LLM
      if @variables.risk >= 80:
        | Offer full refund to retain customer.
      else:
        | Offer $10 credit instead.
```

---

## 🐛 DEBUGGING: Trace Analysis

### The 6 Span Types
| Span | Description |
|------|-------------|
| ➡️ `topic_enter` | Execution enters a topic |
| ▶ `before_reasoning` | Deterministic pre-processing |
| 🧠 `reasoning` | LLM processes instructions |
| ⚡ `action_call` | Action invoked |
| → `transition` | Topic navigation |
| ✓ `after_reasoning` | Deterministic post-processing |

### Debugging Workflow
1. **Interaction Details** - Quick understanding of what happened
2. **Trace Waterfall** - Technical view with exact prompts, latencies
3. **Variable State** - Entry vs Exit values reveal when state was ignored
4. **Script View** - Red squiggles show syntax errors

### Common Debug Patterns
| Symptom | Check | Fix |
|---------|-------|-----|
| Wrong policy applied | Variable Entry values | Change `mutable` to `linked` with `source:` |
| Action executed without auth | `available when` presence | Add guard clause |
| LLM ignores variable | Instruction resolution order | Move data load before LLM text |
| Infinite loop | Transition conditions | Add exit condition |

---

## ⚠️ COMMON ISSUES & FIXES

| Issue | Symptom | Fix |
|-------|---------|-----|
| `Internal Error, try again later` | Invalid `default_agent_user` | Query: `sf data query -q "SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User'" -o TARGET_ORG` |
| `Default agent user X could not be found` | User doesn't exist in target org | Query the **specific target org** (user formats vary: some use `user@orgid.ext`) |
| `No .agent file found in directory` | `agent_name` doesn't match folder | Make `agent_name` identical to folder name (case-sensitive) |
| `SyntaxError: cannot mix spaces and tabs` | Mixed indentation | Use consistent spacing throughout |
| `SyntaxError: Unexpected 'if'` | Nested if statements | Use compound condition: `if A and B:` or flatten to sequential ifs |
| `SyntaxError: Unexpected 'actions'` | Top-level actions block | Move actions inside `topic.reasoning.actions:` |
| `SyntaxError: Unexpected 'inputs'` | `inputs:` block in action | Use `with param=value` syntax instead |
| `SyntaxError: Unexpected 'outputs'` | `outputs:` block in action | Use `set @variables.x = @outputs.y` instead |
| `SyntaxError: Unexpected 'set'` | `set` after `@utils.setVariables` | Use Helper Topic Pattern (set in `instructions: ->`) |
| `Duplicate 'available when' clause` | Multiple guards on action | Combine: `available when A and B` |
| `Unexpected 'escalate'` | Reserved action name | Rename to `escalate_now` or `escalate_to_human` |
| `Transition to undefined topic` | Typo in topic reference | Check spelling, ensure topic exists |
| `Variables cannot be both mutable AND linked` | Conflicting modifiers | Choose one: mutable for state, linked for external |
| `Required fields missing: [BundleType]` | Using wrong deploy command | Use `sf agent publish authoring-bundle`, NOT `sf project deploy start` |
| `Cannot find a bundle-meta.xml file` | Wrong file naming | Rename to `AgentName.bundle-meta.xml`, NOT `.aiAuthoringBundle-meta.xml` |
| `ValidationError: Tool target 'X' is not an action definition` | Action not defined in topic `actions:` block with `target:`, OR target doesn't exist in org | Define action in topic-level `actions:` block with valid `target:` (e.g., `apex://ClassName`), then reference via `@actions.name` in `reasoning.actions:` |
| LLM bypasses security check | Using prompts for security | Use `available when` guards instead |
| Post-action logic doesn't run | Check not at TOP | Move post-action check to first lines |
| Wrong data retrieved | Missing filter | Wrap retriever in Flow with filter inputs |
| Variables don't change | Using `@utils.setVariables` with `set` | Post-action `set` only works on `@actions.*`, use Helper Topics |
| Wrong target protocol | `flows://` instead of `flow://` | Remove trailing `s`: `flow://FlowName` |
| Prompt template input not mapped | Unquoted `Input:` parameter | Quote it: `with "Input:email"=...` |
| Missing type on action input | `email:` with no type in definition | Add type: `email: string` |

### Deployment Gotchas (Validated by Testing)

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| `AgentName.aiAuthoringBundle-meta.xml` | `AgentName.bundle-meta.xml` |
| `sf project deploy start` | `sf agent publish authoring-bundle` |
| `sf agent validate --source-dir` | `sf agent validate authoring-bundle --source-dir` |
| Query user from wrong org | Query **target org** specifically with `-o` flag |

### Einstein Agent User Format (Org-Specific)

Einstein Agent User formats vary between orgs:
- **Production/Partner orgs**: Often use `username@orgid.ext` format (e.g., `resort_manager@00dak00000gdgwu480119933.ext`)
- **Dev orgs**: May use `username.suffix@orgfarm.salesforce.com` format

**MANDATORY: Ask user to confirm which Einstein Agent User to use when creating a new agent.**

**Always query the specific target org:**
```bash
# Query target org specifically
sf data query -q "SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true" -o YOUR_TARGET_ORG
```

Present the results to the user and ask them to select which user to use for `default_agent_user`.

> ⚠️ A user existing in one org does NOT mean it exists in another. Always verify in the deployment target.

---

## 📚 DOCUMENT MAP (Progressive Disclosure)

### Tier 2: Resource Guides (Comprehensive)
| Need | Document | Description |
|------|----------|-------------|
| Syntax reference | [resources/syntax-reference.md](resources/syntax-reference.md) | Complete block & expression syntax |
| FSM design | [resources/fsm-architecture.md](resources/fsm-architecture.md) | State machine patterns & examples |
| Instruction resolution | [resources/instruction-resolution.md](resources/instruction-resolution.md) | Three-phase execution model |
| Data & multi-agent | [resources/grounding-multiagent.md](resources/grounding-multiagent.md) | Retriever actions & SOMA patterns |
| Debugging | [resources/debugging-guide.md](resources/debugging-guide.md) | Trace analysis & forensics |
| Testing | [resources/testing-guide.md](resources/testing-guide.md) | Batch testing & quality metrics |
| Prompt template actions | [resources/action-prompt-templates.md](resources/action-prompt-templates.md) | `generatePromptResponse://` input binding, grounded data, `run` limitation |
| Advanced action patterns | [resources/action-patterns.md](resources/action-patterns.md) | Context-aware descriptions, `{!@actions.X}` instruction refs, binding matrix |
| Actions reference | [resources/actions-reference.md](resources/actions-reference.md) | Complete action types, GenAiFunction metadata, escalation routing, Flow/Apex/API patterns |

### Tier 3: Quick References (Docs)
| Need | Document | Description |
|------|----------|-------------|
| CLI commands | [docs/cli-guide.md](docs/cli-guide.md) | sf agent retrieve/validate/deploy |
| Patterns | [docs/patterns-quick-ref.md](docs/patterns-quick-ref.md) | Decision tree for pattern selection |

### Tier 4: Templates
| Category | Directory | Contents |
|----------|-----------|----------|
| Root templates | [templates/](templates/) | 7 .agent templates (minimal-starter, hub-and-spoke, etc.) |
| Complete agents | [templates/agents/](templates/agents/) | 4 full agent examples (hello-world, simple-qa, multi-topic, production-faq) |
| Components | [templates/components/](templates/components/) | 6 component fragments (apex-action, error-handling, escalation, flow-action, n-ary-conditions, topic-with-actions) |
| Advanced patterns | [templates/patterns/](templates/patterns/) | 11 pattern templates (action-callbacks, bidirectional-routing, delegation, lifecycle-events, etc.) |
| Metadata XML | [templates/metadata/](templates/metadata/) | 6 XML templates (GenAiFunction, GenAiPlugin, PromptTemplate, Flow) |
| Apex | [templates/apex/](templates/apex/) | Models API queueable class |

---

## 🔗 CROSS-SKILL INTEGRATION

### MANDATORY Delegations
| Task | Delegate To | Reason |
|------|-------------|--------|
| Create Flows for `flow://` targets | `/sf-flow` | Flows must exist before agent uses them |
| Test agent routing & actions | `/sf-ai-agentforce-testing` | Specialized testing patterns |
| Deploy agent to org | `/sf-deploy` | Proper deployment validation |

### Integration Patterns
| From | To | Pattern |
|------|-----|---------|
| `/sf-ai-agentscript` | `/sf-flow` | Create Flow, then reference in agent |
| `/sf-ai-agentscript` | `/sf-apex` | Create Apex class with `@InvocableMethod`, then use `apex://ClassName` target directly (NO GenAiFunction needed) |
| `/sf-ai-agentscript` | `/sf-integration` | Set up Named Credentials for `externalService://` |

---

## ✅ DEPLOYMENT CHECKLIST

### Configuration
- [ ] `default_agent_user` is valid Einstein Agent User
- [ ] `agent_name` uses snake_case (no spaces)

### Syntax
- [ ] No mixed tabs/spaces
- [ ] Booleans use `True`/`False`
- [ ] Variable names use snake_case

### Structure
- [ ] Exactly one `start_agent` block
- [ ] At least one `topic` block
- [ ] All transitions reference existing topics

### Security
- [ ] Critical actions have `available when` guards
- [ ] Session data uses `linked` variables (not `mutable`)

### Testing
- [ ] `sf agent validate --source-dir ./my-agent` passes
- [ ] Preview mode tested before activation

---

## 🚀 MINIMAL WORKING EXAMPLE

```yaml
config:
  developer_name: "simple_agent"
  agent_description: "A minimal working agent example"
  agent_type: "AgentforceServiceAgent"  # or "AgentforceEmployeeAgent"
  default_agent_user: "agent_user@yourorg.com"

system:
  messages:
    welcome: "Hello! How can I help you today?"
    error: "Sorry, something went wrong."
  instructions: "You are a helpful customer service agent."

variables:
  customer_verified: mutable boolean = False

topic main:
  description: "Main conversation handler"
  reasoning:
    instructions: ->
      if @variables.customer_verified == True:
        | You are speaking with a verified customer.
        | Help them with their request.
      else:
        | Please verify the customer's identity first.
    actions:
      verify: @actions.verify_customer
        description: "Verify customer identity"
        set @variables.customer_verified = @outputs.verified

start_agent entry:
  description: "Entry point for all conversations"
  reasoning:
    instructions: |
      Greet the customer and route to the main topic.
    actions:
      go_main: @utils.transition to @topic.main
        description: "Navigate to main conversation"
```

---

## 📖 OFFICIAL RESOURCES

- [Agent Script Documentation](https://developer.salesforce.com/docs/einstein/genai/guide/agent-script.html)
- [Agentforce Builder Guide](https://help.salesforce.com/s/articleView?id=sf.copilot_builder_overview.htm)
- [Atlas Reasoning Engine](https://developer.salesforce.com/docs/einstein/genai/guide/atlas-reasoning-engine.html)

---

## 📚 SOURCES & ACKNOWLEDGMENTS

This skill draws from multiple authoritative sources:

| Source | Contribution |
|--------|--------------|
| [trailheadapps/agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) | 20 reference recipes across 4 categories, AGENT_SCRIPT.md rules document, variable patterns, action target catalog |
| Salesforce Official Documentation | Core syntax, API references, deployment guides |
| TDD Validation (this skill) | 13 validation agents confirming current-release syntax compatibility |
| Tribal knowledge interviews | Canvas View bugs, VS Code limitations, credit consumption patterns |
| [agentforce.guide](https://agentforce.guide/) | Unofficial but useful examples (note: some patterns don't compile in current release) |
| @kunello ([PR #20](https://github.com/Jaganpro/sf-skills/pull/20)) | Prompt template `"Input:fieldName"` binding syntax, context-aware description overrides, `{!@actions.X}` instruction reference patterns, callback behavior notes, error pattern catalog |

> **⚠️ Note on Feature Validation**: Some patterns from external sources (e.g., `always_expect_input:`, `label:` property, certain action properties on transitions) do NOT compile in Winter '26. The `before_reasoning:`/`after_reasoning:` lifecycle hooks ARE valid but require **direct content** (no `instructions:` wrapper) - see the Lifecycle Hooks section for correct syntax. This skill documents only patterns that pass TDD validation.

---

## 🏷️ VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.7.0 | 2026-02-09 | **CRITICAL FIX: apex:// works directly, GenAiFunction NOT needed for Agent Script**. Removed false "Known Issue" claiming `apex://ClassName` doesn't work (actions-reference.md line 393). Rewrote "Action Type 2: Apex Actions" section to document two deployment paths (AiAuthoringBundle uses `apex://` directly; Agent Builder UI needs GenAiFunction). Added "Two-Level Action System" explanation (topic `actions:` block defines with `target:`, `reasoning.actions:` invokes via `@actions.name`). Fixed GenAiFunction XML templates to use correct API v65.0 schema (removed invalid `<capability>`, `<genAiFunctionParameters>`, `<genAiFunctionInputs>`, `<genAiFunctionOutputs>` elements; added `input/schema.json` + `output/schema.json` bundle pattern). Fixed `apex-action.agent` template to use `apex://ClassName` (not `ClassName.MethodName`). Fixed `topic-with-actions.agent` to remove incorrect "with/set not supported in AiAuthoringBundle" warning. Fixed troubleshooting table entries. Updated SKILL.md "Registering Flow Actions" section to clarify AiAuthoringBundle vs Agent Builder UI paths. Confirmed against `trailheadapps/agent-script-recipes` (zero GenAiFunction/GenAiPlugin in official recipes). |
| 1.6.0 | 2026-02-07 | **Content migration from former sf-ai-agentforce-legacy**: Migrated 28 template files across 5 categories (agents/, components/, patterns/, metadata/, apex/) from the former legacy skill (now `sf-ai-agentforce`). Created `resources/actions-reference.md` (602 lines) with exhaustive action type reference, GenAiFunction metadata, escalation routing, and Flow/Apex/API patterns. Merged topic design patterns into `resources/fsm-architecture.md`. Merged advanced decision trees into `docs/patterns-quick-ref.md`. Added Tier 4 Templates section to Document Map. The former legacy skill directory is now `sf-ai-agentforce` — repurposed for standard Agentforce platform content (Agent Builder, PromptTemplate, Models API). |
| 1.5.0 | 2026-02-06 | **Action patterns & prompt template docs** (from @kunello PR #20): Added `resources/action-prompt-templates.md` documenting `generatePromptResponse://` input binding syntax (`"Input:fieldName"`), grounded data integration, output handling, and `run` keyword limitation workaround. Added `resources/action-patterns.md` covering context-aware action description overrides (beginner/advanced mode), `{!@actions.X}` instruction references for guided LLM action selection, input binding decision matrix, callback success-only behavior, and additional error patterns. Updated Common Issues table with 3 new error entries (wrong protocol, unquoted Input: params, missing type annotations). Added Document Map entries and cross-reference after Action Chaining section. Content consolidated from @kunello's 8-file contribution against Agent Script Recipes. |
| 1.3.0 | 2026-01-20 | **Lifecycle hooks validated**: Added full documentation for `before_reasoning:` and `after_reasoning:` with CORRECT syntax (content directly under block, NO `instructions:` wrapper). Added "Features NOT Valid in Current Release" section documenting 7 features that appear in docs/recipes but don't compile (label on topics/actions, always_expect_input, action properties on transitions). Updated validation_agents count to 13. Confirmed `@utils.transition` only supports `description:` property. |
| 1.2.0 | 2026-01-20 | **Gap analysis vs agent-script-recipes**: Expanded Action Target Protocols from 7 to 16 (with validation status indicators), added Variable vs Action I/O Type Matrix, added lifecycle hooks note with TDD validation caveat, added Sources & Acknowledgments section, documented future/planned features notice. TDD validation confirmed `label:` IS reserved (SKILL.md was correct), `before_reasoning:`/`after_reasoning:` syntax from recipes does NOT compile in current release |
| 1.1.0 | 2026-01-20 | **"Ultimate Guide" tribal knowledge integration**: Added `complex_data_type_name` mapping table, Canvas View corruption bugs, Reserved field names, Preview mode workarounds, Credit consumption table, Supervision vs Handoff clarification, Action output flags for zero-hallucination routing, Latch variable pattern, Loop protection guardrails, Token/size limits, Progress indicators, Connection block escalation patterns, VS Code limitations, Language block quirks. Added 4 new templates: flow-action-lookup, prompt-rag-search, deterministic-routing, escalation-pattern |
| 1.0.4 | 2026-01-19 | **Progressive testing validation** (Quiz_Master, Expense_Calculator, Order_Processor): Added constraints for no top-level `actions:` block, no `inputs:`/`outputs:` in reasoning.actions, expanded nested-if guidance with flattening approach, added new SyntaxError entries to common issues |
| 1.0.3 | 2026-01-19 | Added Einstein Agent User interview requirement - mandatory user confirmation when creating new agents |
| 1.0.2 | 2026-01-19 | **Major corrections from GitHub reference**: Fixed block order (config→system), added Helper Topic Pattern, transition vs delegation, expression operators (+/- only), naming rules (80 char max), slot-filling `...` syntax, post-action directives (@actions.* only) |
| 1.0.1 | 2026-01-19 | Added syntax constraints from 0-shot testing: no nested if, one available when per action, reserved action names |
| 1.0.0 | 2026-01 | Initial release with 8-module coverage |
