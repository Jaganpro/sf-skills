# Actions Reference

> Migrated from the former `sf-ai-agentforce-legacy/docs/actions-reference.md` on 2026-02-07.
> For context-aware descriptions, instruction references, and input binding patterns, see [action-patterns.md](action-patterns.md).
> For prompt template actions (`generatePromptResponse://`), see [action-prompt-templates.md](action-prompt-templates.md).

Complete guide to Agent Actions in Agentforce: Flow, Apex, API actions,
escalation routing, and GenAiFunction metadata.

---

## Action Properties Reference

All actions in Agent Script support these properties:

### Action Definition Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `target` | String | Yes | Executable target (see Action Target Types below) |
| `description` | String | Yes | Explains behavior for LLM decision-making |
| `inputs` | Object | No | Input parameters and requirements |
| `outputs` | Object | No | Return parameters |
| `label` | String | No | Display name (auto-generated if omitted) |
| `available_when` | Expression | No | Conditional availability for the LLM |
| `require_user_confirmation` | Boolean | No | Ask user to confirm before execution |
| `include_in_progress_indicator` | Boolean | No | Show progress indicator during execution |
| `progress_indicator_message` | String | No | Custom message shown during execution (e.g., "Processing your request...") |

### Output Properties

| Property | Type | Description |
|----------|------|-------------|
| `description` | String | Explains the output parameter |
| `filter_from_agent` | Boolean | Set `True` to hide sensitive data from LLM |
| `complex_data_type_name` | String | Lightning data type mapping |

### Example with All Properties

```agentscript
actions:
   process_payment:
      description: "Processes payment for the order"
      label: "Process Payment"
      require_user_confirmation: True    # Ask user before executing
      include_in_progress_indicator: True
      inputs:
         amount: number
            description: "Payment amount"
         card_token: string
            description: "Tokenized card number"
      outputs:
         transaction_id: string
            description: "Transaction reference"
         card_last_four: string
            description: "Last 4 digits of card"
            filter_from_agent: True     # Hide from LLM context
      target: "flow://Process_Payment"
      available_when: @variables.cart_total > 0
```

---

## Action Target Types (Complete Reference)

AgentScript supports **22+ action target types**. Use the correct protocol for your integration:

| Short Name | Long Name | Description | Use Case |
|------------|-----------|-------------|----------|
| `flow` | `flow` | Salesforce Flow | Most common — Autolaunched Flows |
| `apex` | `apex` | Apex Class | Custom business logic |
| `prompt` | `generatePromptResponse` | Prompt Template | AI-generated responses |
| `standardInvocableAction` | `standardInvocableAction` | Built-in Salesforce actions | Send email, create task, etc. |
| `externalService` | `externalService` | External API via OpenAPI schema | External system calls |
| `quickAction` | `quickAction` | Object-specific quick actions | Log call, create related record |
| `api` | `api` | REST API calls | Direct API invocation |
| `apexRest` | `apexRest` | Custom REST endpoints | Custom @RestResource classes |
| `serviceCatalog` | `createCatalogItemRequest` | Service Catalog | Service catalog requests |
| `integrationProcedureAction` | `executeIntegrationProcedure` | OmniStudio Integration | Industry Cloud procedures |
| `expressionSet` | `runExpressionSet` | Expression calculations | Decision matrix, calculations |
| `cdpMlPrediction` | `cdpMlPrediction` | CDP ML predictions | Data Cloud predictions |
| `externalConnector` | `externalConnector` | External system connector | Pre-built connectors |
| `slack` | `slack` | Slack integration | Slack messaging |
| `namedQuery` | `namedQuery` | Predefined queries | Saved SOQL queries |
| `auraEnabled` | `auraEnabled` | Lightning component methods | @AuraEnabled Apex methods |
| `mcpTool` | `mcpTool` | Model Context Protocol | MCP tool integrations |
| `retriever` | `retriever` | Knowledge retrieval | RAG/knowledge base queries |

**Target Format**: `<type>://<DeveloperName>` (e.g., `flow://Get_Account_Info`, `standardInvocableAction://sendEmail`)

**Common Examples:**
```agentscript
# Flow action (most common)
target: "flow://Get_Customer_Orders"

# Apex action
target: "apex://CustomerServiceController"

# Prompt template
target: "generatePromptResponse://Email_Draft_Template"

# Standard invocable action (built-in Salesforce)
target: "standardInvocableAction://sendEmail"

# External service (API call)
target: "externalService://Stripe_Payment_API"
```

**Tip**: Before creating a custom Flow, check if a `standardInvocableAction://` already exists for your use case.

---

## Action Invocation Methods

| Method | Syntax | Behavior | AiAuthoringBundle | GenAiPlannerBundle |
|--------|--------|----------|-------------------|-------------------|
| **Actions Block** | `actions:` in `reasoning:` | LLM chooses which to execute | ✅ Works | ✅ Works |
| **Deterministic** | `run @actions.name` | Always executes when code path is reached | ❌ NOT Supported | ✅ Works |

### CRITICAL: Deployment Method Limitations

**`run` keyword is NOT supported in AiAuthoringBundle (Tested Dec 2025)**

```agentscript
# ❌ FAILS in AiAuthoringBundle - SyntaxError: Unexpected 'run'
before_reasoning:
   run @actions.log_turn    # NOT SUPPORTED!

create: @actions.create_order
   run @actions.send_email  # NOT SUPPORTED!
```

**`{!@actions.name}` interpolation does NOT work (Tested Dec 2025)**

```agentscript
# ❌ FAILS - SyntaxError: Unexpected '{'
reasoning:
   instructions: ->
      | Use {!@actions.get_order} to look up order details.  # BROKEN!
```

### Correct Approach: Use `reasoning.actions` Block

The LLM automatically selects appropriate actions from those defined in the `reasoning.actions` block:

```agentscript
topic order_management:
   label: "Order Management"
   description: "Handles order inquiries"

   actions:
      get_order:
         description: "Retrieves order information"
         inputs:
            order_id: string
               description: "The order ID"
         outputs:
            status: string
               description: "Order status"
         target: "flow://Get_Order_Details"

   reasoning:
      instructions: ->
         | Help the customer with their order.
         | When they ask about an order, look it up.
      actions:
         # LLM automatically selects this when appropriate
         lookup: @actions.get_order
            with order_id=...
            set @variables.order_status = @outputs.status
```

---

## Action Type 1: Flow Actions

### When to Use

- Standard Salesforce data operations (CRUD)
- Business logic that can be expressed in Flow
- Screen flows for guided user experiences
- Approval processes

### Implementation

```yaml
actions:
  create_case:
    description: "Creates a new support case for the customer"
    inputs:
      subject:
        type: string
        description: "Case subject line"
      description:
        type: string
        description: "Detailed case description"
      priority:
        type: string
        description: "Case priority (Low, Medium, High, Urgent)"
    outputs:
      caseNumber:
        type: string
        description: "Created case number"
      caseId:
        type: string
        description: "Case record ID"
    target: "flow://Create_Support_Case"
```

### Flow Requirements

For an action to work with agents, the Flow must:

1. **Be Autolaunched** — `processType: AutoLaunchedFlow`
2. **Have Input Variables** — Marked as `isInput: true`
3. **Have Output Variables** — Marked as `isOutput: true`
4. **Be Active** — `status: Active`

**Flow Variable Example:**
```xml
<variables>
    <name>subject</name>
    <dataType>String</dataType>
    <isCollection>false</isCollection>
    <isInput>true</isInput>
    <isOutput>false</isOutput>
</variables>
```

### Best Practices

| Practice | Description |
|----------|-------------|
| Descriptive names | Use clear Flow API names that describe the action |
| Error handling | Include fault paths in your Flow |
| Bulkification | Design Flows to handle multiple records |
| Governor limits | Avoid SOQL/DML in loops |

---

## Action Type 2: Apex Actions

### When to Use

- Complex calculations or algorithms
- Custom integrations requiring Apex
- Operations not possible in Flow
- Bulk data processing
- When you need full control over execution

### Two Deployment Paths (CRITICAL DISTINCTION)

| Deployment Method | How Apex Actions Work | GenAiFunction Required? |
|-------------------|----------------------|------------------------|
| **AiAuthoringBundle** (.agent file) | `apex://ClassName` target in topic actions block | **NO** |
| **Agent Builder UI** (GenAiPlannerBundle) | GenAiFunction metadata wraps the Apex class | **YES** |

> ⚠️ **The official [agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) repo uses `apex://ClassName` directly with ZERO GenAiFunction metadata.** GenAiFunction is only needed when configuring agents through the Agent Builder UI or deploying via GenAiPlannerBundle.

### Path A: AiAuthoringBundle (Agent Script — RECOMMENDED)

#### Step 1: Create Apex Class with @InvocableMethod

```apex
public with sharing class CalculateDiscountAction {

    public class DiscountRequest {
        @InvocableVariable(label='Order Amount' required=true)
        public Decimal orderAmount;

        @InvocableVariable(label='Customer Tier' required=true)
        public String customerTier;
    }

    public class DiscountResult {
        @InvocableVariable(label='Discount Percentage')
        public Decimal discountPercentage;

        @InvocableVariable(label='Final Amount')
        public Decimal finalAmount;
    }

    @InvocableMethod(
        label='Calculate Discount'
        description='Calculates discount based on order amount and customer tier'
    )
    public static List<DiscountResult> calculateDiscount(List<DiscountRequest> requests) {
        List<DiscountResult> results = new List<DiscountResult>();
        for (DiscountRequest req : requests) {
            DiscountResult result = new DiscountResult();
            result.discountPercentage = getTierDiscount(req.customerTier);
            result.finalAmount = req.orderAmount * (1 - result.discountPercentage / 100);
            results.add(result);
        }
        return results;
    }

    private static Decimal getTierDiscount(String tier) {
        Map<String, Decimal> tierDiscounts = new Map<String, Decimal>{
            'Bronze' => 5, 'Silver' => 10, 'Gold' => 15, 'Platinum' => 20
        };
        return tierDiscounts.containsKey(tier) ? tierDiscounts.get(tier) : 0;
    }
}
```

#### Step 2: Reference DIRECTLY in Agent Script via `apex://`

```yaml
topic discount_calculator:
   description: "Calculates discount for customer order"

   # Level 1: Action DEFINITION with target
   actions:
      calculate_discount:
         description: "Calculates discount based on order amount and customer tier"
         inputs:
            orderAmount: number
               description: "The total order amount before discount"
            customerTier: string
               description: "Customer membership tier"
         outputs:
            discountPercentage: number
               description: "Applied discount percentage"
            finalAmount: number
               description: "Final order amount after discount"
         target: "apex://CalculateDiscountAction"   # Direct Apex — NO GenAiFunction needed!

   reasoning:
      instructions: |
         Help the customer calculate their discount.
      # Level 2: Action INVOCATION referencing the Level 1 definition
      actions:
         calc: @actions.calculate_discount
            with orderAmount=...
            with customerTier=@variables.tier
            set @variables.final_amount = @outputs.finalAmount
```

> ✅ **No GenAiFunction, no GenAiPlugin, no metadata deployment beyond the Apex class itself.** The `apex://ClassName` target auto-discovers the `@InvocableMethod` on the class.

### Path B: Agent Builder UI (GenAiPlannerBundle — Legacy)

If you're NOT using Agent Script and are building agents through the Agent Builder UI, you need GenAiFunction metadata to wrap the Apex class. See the `templates/metadata/genai-function-apex.xml` template for the XML format.

> **Note**: GenAiFunction XML (API v65.0) only supports these elements: `masterLabel`, `description`, `invocationTarget`, `invocationTargetType`, `isConfirmationRequired`. Input/output schemas are defined via `input/schema.json` and `output/schema.json` bundle files, NOT inline XML elements.

---

## Action Type 3: API Actions (External System Integration)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  API ACTION ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│  Agent Script                                                │
│       │                                                      │
│       ▼                                                      │
│  flow://HTTP_Callout_Flow                                    │
│       │                                                      │
│       ▼                                                      │
│  HTTP Callout Action (in Flow)                               │
│       │                                                      │
│       ▼                                                      │
│  Named Credential (Authentication)                           │
│       │                                                      │
│       ▼                                                      │
│  External API                                                │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Steps

1. **Create Named Credential** (via sf-integration skill)
2. **Create HTTP Callout Flow** wrapping the external call
3. **Reference Flow in Agent Script** with `flow://` target

### Security Considerations

| Consideration | Implementation |
|---------------|----------------|
| Authentication | Always use Named Credentials (never hardcode secrets) |
| Permissions | Use Permission Sets to grant Named Principal access |
| Error handling | Implement fault paths in Flow |
| Logging | Log callout details for debugging |
| Timeouts | Set appropriate timeout values |

---

## Connection Block (Escalation Routing)

The `connection` block enables escalation to human agents via Omni-Channel. Both singular (`connection`) and plural (`connections`) forms are supported.

### Basic Syntax

```agentscript
# Messaging channel (most common)
connection messaging:
   outbound_route_type: "OmniChannelFlow"
   outbound_route_name: "Support_Queue_Flow"
   escalation_message: "Transferring you to a human agent..."
   adaptive_response_allowed: True
```

### Multiple Channels

```agentscript
# Use plural form for multiple channels
connections:
   messaging:
      escalation_message: "Transferring to messaging agent..."
      outbound_route_type: "OmniChannelFlow"
      outbound_route_name: "agent_support_flow"
      adaptive_response_allowed: True
   telephony:
      escalation_message: "Routing to technical support..."
      outbound_route_type: "OmniChannelFlow"
      outbound_route_name: "technical_support_flow"
      adaptive_response_allowed: False
```

### Connection Block Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `outbound_route_type` | String | Yes | **MUST be `"OmniChannelFlow"`** — only valid value |
| `outbound_route_name` | String | Yes | API name of Omni-Channel Flow (must exist in org) |
| `escalation_message` | String | Yes | Message shown to user during transfer |
| `adaptive_response_allowed` | Boolean | No | Allow agent to adapt responses during escalation (default: False) |

### Supported Channels

| Channel | Description | Use Case |
|---------|-------------|----------|
| `messaging` | Chat/messaging channels | Enhanced Chat, Web Chat, In-App |
| `telephony` | Voice/phone channels | Service Cloud Voice, phone support |

**CRITICAL**: Values like `"queue"`, `"skill"`, `"agent"` for `outbound_route_type` cause validation errors!

### Escalation Action

```agentscript
# AiAuthoringBundle - basic escalation
actions:
   transfer_to_human: @utils.escalate
      description: "Transfer to human agent"

# GenAiPlannerBundle - with reason parameter
actions:
   transfer_to_human: @utils.escalate with reason="Customer requested"
```

### Prerequisites for Escalation

1. Omni-Channel configured in Salesforce
2. Omni-Channel Flow created and deployed
3. Connection block in agent script
4. Messaging channel active (Enhanced Chat, etc.)

---

## GenAiFunction Metadata Summary (Agent Builder UI / GenAiPlannerBundle ONLY)

> ⚠️ **NOT needed for AiAuthoringBundle (Agent Script)**. If you're writing `.agent` files, use `target: "apex://ClassName"` or `target: "flow://FlowName"` directly. See Action Type 2 above.

`GenAiFunction` wraps Apex, Flows, or Prompts as Agent Actions **for the Agent Builder UI path**.

```xml
<!-- Minimal valid GenAiFunction XML (API v65.0) -->
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>What this action does</description>
    <invocationTarget>FlowOrApexName</invocationTarget>
    <invocationTargetType>flow|apex|prompt</invocationTargetType>
    <isConfirmationRequired>false</isConfirmationRequired>
    <masterLabel>Display Name</masterLabel>
</GenAiFunction>
```

**Input/Output Schemas**: Use `input/schema.json` and `output/schema.json` files in the GenAiFunction bundle directory. Do NOT use inline XML elements like `<genAiFunctionInputs>`, `<genAiFunctionOutputs>`, `<genAiFunctionParameters>`, or `<capability>` — these are NOT valid in the Metadata API XML schema (API v65.0).

### Prompt Template Types

| Type | Use Case |
|------|----------|
| `flexPrompt` | General purpose, maximum flexibility |
| `salesGeneration` | Sales content (emails, proposals) |
| `fieldCompletion` | Suggest field values |
| `recordSummary` | Summarize record data |

### Template Variable Types

| Variable Type | Description |
|---------------|-------------|
| `freeText` | User-provided text input |
| `recordField` | Bound to specific record field |
| `relatedList` | Data from related records |
| `resource` | Static resource content |

---

## Cross-Skill Integration

### Orchestration Order for API Actions

When building agents with external API integrations, follow this order:

```
┌─────────────────────────────────────────────────────────────┐
│  INTEGRATION + AGENTFORCE ORCHESTRATION ORDER                │
├─────────────────────────────────────────────────────────────┤
│  1. sf-connected-apps  → Connected App (if OAuth needed)     │
│  2. sf-integration     → Named Credential + External Service │
│  3. sf-apex            → @InvocableMethod (if custom logic)  │
│  4. sf-flow            → Flow wrapper (HTTP Callout / Apex)  │
│  5. sf-deploy          → Deploy all metadata to org          │
│  6. sf-ai-agentscript  → Agent with flow:// target           │
│  7. sf-deploy          → Publish (sf agent publish            │
│                           authoring-bundle)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Tool target 'X' is not an action definition` | Action not defined in topic `actions:` block, or target doesn't exist in org | Define action with `target:` in topic-level `actions:` block; ensure Apex class/Flow is deployed |
| `apex://` target not found | Apex class not deployed or missing `@InvocableMethod` | Deploy class first, ensure it has `@InvocableMethod` annotation |
| Flow action fails | Flow not active or not Autolaunched | Activate the Flow; ensure it's Autolaunched (not Screen) |
| API action timeout | External system slow | Increase timeout, add retry logic |
| Permission denied | Missing Named Principal access | Grant Permission Set |
| Action not appearing in Agent Builder UI | GenAiFunction not deployed (UI path only) | Deploy GenAiFunction metadata (only needed for Agent Builder UI, not Agent Script) |

### Debugging Tips

1. **Check deployment status:** `sf project deploy report`
2. **Verify GenAiFunction deployment:** `sf org list metadata -m GenAiFunction`
3. **Test Flow independently:** Use Flow debugger in Setup with sample inputs
4. **Check agent logs:** Agent Builder → Logs

---

## Related Documentation

- [action-patterns.md](action-patterns.md) — Context-aware descriptions, instruction references, binding strategies
- [action-prompt-templates.md](action-prompt-templates.md) — Prompt template invocation (`generatePromptResponse://`)
- [fsm-architecture.md](fsm-architecture.md) — FSM design and node patterns
