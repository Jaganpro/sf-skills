<!-- TIER: 3 | DETAILED REFERENCE -->
<!-- Read after: SKILL.md, agent-script-reference.md -->
<!-- Purpose: Complete guide to actions, escalation, and GenAiFunction metadata -->

# Actions Reference

Complete guide to Agent Actions in Agentforce: Flow, Apex, API, Prompt actions,
escalation routing, and GenAiFunction metadata.

## Overview

Agent Actions are the executable capabilities that Agentforce agents can perform. This guide covers all four action types and how to implement them effectively.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT ACTION TYPES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Action Type      │ Target Syntax         │ Use Case                       │
│───────────────────┼───────────────────────┼────────────────────────────────│
│  Flow Action      │ flow://FlowAPIName    │ Standard business logic        │
│  Apex Action      │ GenAiFunction         │ Complex logic, callouts        │
│  API Action       │ flow:// + HTTP Callout│ External system integration    │
│  Prompt Action    │ PromptTemplate        │ AI-generated content           │
└─────────────────────────────────────────────────────────────────────────────┘
```

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

### Action Target Types (Complete Reference)

AgentScript supports **22+ action target types**. Use the correct protocol for your integration:

| Short Name | Long Name | Description | Use Case |
|------------|-----------|-------------|----------|
| `flow` | `flow` | Salesforce Flow | Most common - Autolaunched Flows |
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

**⚠️ 0-shot Tip**: Before creating a custom Flow, check if a `standardInvocableAction://` already exists for your use case.

### Action Invocation Methods

Agent Script supports these invocation styles:

| Method | Syntax | Behavior | AiAuthoringBundle | GenAiPlannerBundle |
|--------|--------|----------|-------------------|-------------------|
| **Actions Block** | `actions:` in `reasoning:` | LLM chooses which to execute | ✅ Works | ✅ Works |
| **Deterministic** | `run @actions.name` | Always executes when code path is reached | ❌ NOT Supported | ✅ Works |

### ⚠️ CRITICAL: Deployment Method Limitations

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

### ✅ Correct Approach: Use `reasoning.actions` Block

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

**How it works**: The LLM reads action descriptions and selects the appropriate one based on conversation context. No need for `{!@actions.x}` syntax - just define actions with clear descriptions.

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

## Action Type 1: Flow Actions

### Overview

Flow Actions are the most straightforward action type. They use the `flow://` target syntax directly in Agent Script.

### When to Use

- Standard Salesforce data operations (CRUD)
- Business logic that can be expressed in Flow
- Screen flows for guided user experiences
- Approval processes

### Implementation

**Agent Script Syntax:**
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

1. **Be Autolaunched** - `processType: AutoLaunchedFlow`
2. **Have Input Variables** - Marked as `isInput: true`
3. **Have Output Variables** - Marked as `isOutput: true`
4. **Be Active** - `status: Active`

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

## Action Type 2: Apex Actions (via GenAiFunction)

### Overview

Apex Actions provide the most flexibility for complex business logic. They use `GenAiFunction` metadata to expose `@InvocableMethod` Apex to agents.

### When to Use

- Complex calculations or algorithms
- Custom integrations requiring Apex
- Operations not possible in Flow
- Bulk data processing
- When you need full control over execution

### Implementation Steps

#### Step 1: Create Apex Class with @InvocableMethod

```apex
/**
 * Apex class for agent action: Calculate discount
 * Exposed via GenAiFunction metadata
 */
public with sharing class CalculateDiscountAction {

    public class DiscountRequest {
        @InvocableVariable(label='Order Amount' required=true)
        public Decimal orderAmount;

        @InvocableVariable(label='Customer Tier' required=true)
        public String customerTier;

        @InvocableVariable(label='Promo Code')
        public String promoCode;
    }

    public class DiscountResult {
        @InvocableVariable(label='Discount Percentage')
        public Decimal discountPercentage;

        @InvocableVariable(label='Discount Amount')
        public Decimal discountAmount;

        @InvocableVariable(label='Final Amount')
        public Decimal finalAmount;

        @InvocableVariable(label='Applied Rules')
        public String appliedRules;
    }

    @InvocableMethod(
        label='Calculate Discount'
        description='Calculates discount based on order amount, customer tier, and promo code'
    )
    public static List<DiscountResult> calculateDiscount(List<DiscountRequest> requests) {
        List<DiscountResult> results = new List<DiscountResult>();

        for (DiscountRequest req : requests) {
            DiscountResult result = new DiscountResult();

            // Calculate tier discount
            Decimal tierDiscount = getTierDiscount(req.customerTier);

            // Calculate promo discount
            Decimal promoDiscount = getPromoDiscount(req.promoCode);

            // Apply higher discount
            result.discountPercentage = Math.max(tierDiscount, promoDiscount);
            result.discountAmount = req.orderAmount * (result.discountPercentage / 100);
            result.finalAmount = req.orderAmount - result.discountAmount;
            result.appliedRules = buildAppliedRules(tierDiscount, promoDiscount);

            results.add(result);
        }

        return results;
    }

    private static Decimal getTierDiscount(String tier) {
        Map<String, Decimal> tierDiscounts = new Map<String, Decimal>{
            'Bronze' => 5,
            'Silver' => 10,
            'Gold' => 15,
            'Platinum' => 20
        };
        return tierDiscounts.containsKey(tier) ? tierDiscounts.get(tier) : 0;
    }

    private static Decimal getPromoDiscount(String promoCode) {
        if (String.isBlank(promoCode)) return 0;
        // Query promo code records for discount percentage
        // Simplified for example
        return promoCode == 'SAVE20' ? 20 : 0;
    }

    private static String buildAppliedRules(Decimal tierDiscount, Decimal promoDiscount) {
        List<String> rules = new List<String>();
        if (tierDiscount > 0) rules.add('Tier discount: ' + tierDiscount + '%');
        if (promoDiscount > 0) rules.add('Promo discount: ' + promoDiscount + '%');
        return String.join(rules, '; ');
    }
}
```

#### Step 2: Create GenAiFunction Metadata

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Calculate Discount</masterLabel>
    <description>Calculates customer discount based on tier and promo codes</description>
    <developerName>Calculate_Discount_Action</developerName>

    <invocationTarget>CalculateDiscountAction</invocationTarget>
    <invocationTargetType>apex</invocationTargetType>

    <isConfirmationRequired>false</isConfirmationRequired>

    <capability>
        Calculate customer discounts considering their membership tier and any
        promotional codes. Returns the discount percentage, discount amount,
        and final order amount.
    </capability>

    <genAiFunctionInputs>
        <developerName>orderAmount</developerName>
        <description>The total order amount before discount</description>
        <dataType>Number</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionInputs>
        <developerName>customerTier</developerName>
        <description>Customer membership tier: Bronze, Silver, Gold, or Platinum</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionInputs>
        <developerName>promoCode</developerName>
        <description>Optional promotional code</description>
        <dataType>Text</dataType>
        <isRequired>false</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionOutputs>
        <developerName>discountPercentage</developerName>
        <description>Applied discount percentage</description>
        <dataType>Number</dataType>
    </genAiFunctionOutputs>

    <genAiFunctionOutputs>
        <developerName>discountAmount</developerName>
        <description>Dollar amount of discount</description>
        <dataType>Number</dataType>
    </genAiFunctionOutputs>

    <genAiFunctionOutputs>
        <developerName>finalAmount</developerName>
        <description>Final order amount after discount</description>
        <dataType>Number</dataType>
    </genAiFunctionOutputs>
</GenAiFunction>
```

#### Step 3: Reference in Agent Topic (Agent Builder UI)

After deploying the GenAiFunction, it appears in Agent Builder under available actions. Add it to your topic.

### Important: Agent Script apex:// Limitation

> ⚠️ **Known Issue**: The `apex://ClassName` syntax in Agent Script does not work reliably. Always use GenAiFunction metadata for Apex actions.

**❌ Does NOT Work:**
```yaml
actions:
  calculate_discount:
    target: "apex://CalculateDiscountAction"  # BROKEN
```

**✅ Works:**
Deploy GenAiFunction metadata and add to topic via Agent Builder UI.

---

## Action Type 3: API Actions (External System Integration)

### Overview

API Actions enable agents to call external systems. They require a combination of sf-integration skill components and Flow wrappers.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      API ACTION ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Agent Script                                                               │
│       │                                                                     │
│       ▼                                                                     │
│  flow://HTTP_Callout_Flow                                                   │
│       │                                                                     │
│       ▼                                                                     │
│  HTTP Callout Action (in Flow)                                              │
│       │                                                                     │
│       ▼                                                                     │
│  Named Credential (Authentication)                                          │
│       │                                                                     │
│       ▼                                                                     │
│  External API                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step 1: Create Named Credential (via sf-integration)

Ask Claude to use the sf-integration skill:

```
"Create a Named Credential for the Stripe API using OAuth client credentials"
```

This generates:
- Named Credential metadata
- External Credential (if using API 61+)
- Permission Set for Named Principal access

#### Step 2: Create HTTP Callout Flow

**Flow Metadata (simplified):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Stripe_Create_Customer</fullName>
    <label>Stripe Create Customer</label>
    <processType>AutoLaunchedFlow</processType>
    <apiVersion>65.0</apiVersion>
    <status>Active</status>

    <!-- Input Variables -->
    <variables>
        <name>customerEmail</name>
        <dataType>String</dataType>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>

    <variables>
        <name>customerName</name>
        <dataType>String</dataType>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>

    <!-- Output Variables -->
    <variables>
        <name>stripeCustomerId</name>
        <dataType>String</dataType>
        <isInput>false</isInput>
        <isOutput>true</isOutput>
    </variables>

    <variables>
        <name>status</name>
        <dataType>String</dataType>
        <isInput>false</isInput>
        <isOutput>true</isOutput>
    </variables>

    <!-- HTTP Callout Action -->
    <actionCalls>
        <name>Create_Stripe_Customer</name>
        <actionType>httpCallout</actionType>
        <actionName>callout:Stripe_API</actionName>

        <inputParameters>
            <name>method</name>
            <value><stringValue>POST</stringValue></value>
        </inputParameters>

        <inputParameters>
            <name>url</name>
            <value><stringValue>/v1/customers</stringValue></value>
        </inputParameters>

        <inputParameters>
            <name>body</name>
            <value><elementReference>RequestBody</elementReference></value>
        </inputParameters>

        <outputParameters>
            <assignToReference>ResponseBody</assignToReference>
            <name>responseBody</name>
        </outputParameters>
    </actionCalls>

    <!-- Start element -->
    <start>
        <connector>
            <targetReference>Create_Stripe_Customer</targetReference>
        </connector>
    </start>
</Flow>
```

#### Step 3: Reference Flow in Agent Script

```yaml
agent:
  name: "Payment_Agent"
  description: "Handles payment operations with external payment processors"

topics:
  customer_management:
    description: "Manages customer records in payment system"
    instructions: |
      Help users create and manage customer records in our payment system.
      Always collect required information (email, name) before creating customers.

actions:
  create_payment_customer:
    description: "Creates a new customer in the payment processor"
    inputs:
      email:
        type: string
        description: "Customer email address"
      name:
        type: string
        description: "Customer full name"
    outputs:
      customerId:
        type: string
        description: "Payment processor customer ID"
      status:
        type: string
        description: "Operation status"
    target: "flow://Stripe_Create_Customer"
```

### Security Considerations

| Consideration | Implementation |
|---------------|----------------|
| Authentication | Always use Named Credentials (never hardcode secrets) |
| Permissions | Use Permission Sets to grant Named Principal access |
| Error handling | Implement fault paths in Flow |
| Logging | Log callout details for debugging |
| Timeouts | Set appropriate timeout values |

---

## Action Type 4: Prompt Template Actions

### Overview

Prompt Template Actions use Einstein's AI to generate content based on templates. They're ideal for summarization, content generation, and AI-assisted responses.

### When to Use

- Email or message drafting
- Record summarization
- Content recommendations
- AI-powered field suggestions
- Knowledge article generation

### Implementation

#### Step 1: Create PromptTemplate Metadata

**Basic Prompt Template:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Case_Summary_Generator</fullName>
    <masterLabel>Case Summary Generator</masterLabel>
    <description>Generates executive summaries for support cases</description>

    <type>recordSummary</type>
    <isActive>true</isActive>
    <objectType>Case</objectType>

    <promptContent>
You are a customer support analyst creating an executive summary.

Case Information:
- Case Number: {!caseNumber}
- Subject: {!subject}
- Status: {!status}
- Priority: {!priority}
- Account: {!accountName}
- Created: {!createdDate}

Case Description:
{!description}

Recent Activities:
{!recentActivities}

Generate a concise executive summary (under 150 words) that includes:
1. Issue overview
2. Current status and any blockers
3. Recommended next steps
4. Risk assessment (if applicable)

Focus on actionable insights for leadership.
    </promptContent>

    <!-- Record field bindings -->
    <promptTemplateVariables>
        <developerName>caseNumber</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Case</objectType>
        <fieldName>CaseNumber</fieldName>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>subject</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Case</objectType>
        <fieldName>Subject</fieldName>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>status</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Case</objectType>
        <fieldName>Status</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>priority</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Case</objectType>
        <fieldName>Priority</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>accountName</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Case</objectType>
        <fieldName>Account.Name</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>createdDate</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Case</objectType>
        <fieldName>CreatedDate</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>description</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Case</objectType>
        <fieldName>Description</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>recentActivities</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>false</isRequired>
    </promptTemplateVariables>
</PromptTemplate>
```

#### Step 2: Create GenAiFunction for Prompt Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Generate Case Summary</masterLabel>
    <description>Generates an executive summary for a support case</description>
    <developerName>Generate_Case_Summary</developerName>

    <invocationTarget>Case_Summary_Generator</invocationTarget>
    <invocationTargetType>prompt</invocationTargetType>

    <capability>
        Generate executive summaries for support cases. Provides concise
        overviews with status, blockers, and recommended next steps.
    </capability>

    <genAiFunctionInputs>
        <developerName>recordId</developerName>
        <description>The Case record ID to summarize</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionOutputs>
        <developerName>summary</developerName>
        <description>Generated executive summary</description>
        <dataType>Text</dataType>
    </genAiFunctionOutputs>
</GenAiFunction>
```

### Direct Agent Script Invocation (NEW - December 2025)

**You can invoke Prompt Templates directly in Agent Script using the `generatePromptResponse://` target syntax.** This is simpler than creating GenAiFunction metadata.

```agentscript
topic schedule_assistant:
   label: "Schedule Assistant"
   description: "Helps users create personalized schedules"

   actions:
      Generate_Personalized_Schedule:
         description: "Generate a personalized schedule with a prompt template."
         inputs:
            "Input:email": string
               description: "User's email address"
               is_required: True
            "Input:preferences": string
               description: "User's scheduling preferences"
               is_required: False
         outputs:
            promptResponse: string
               description: "The prompt response generated by the action"
               is_used_by_planner: True
               is_displayable: True
         target: "generatePromptResponse://Generate_Personalized_Schedule"

   reasoning:
      instructions: ->
         | Help the user create a personalized schedule.
         | 1. Ask for their email address
         | 2. Ask about their preferences
         | 3. Generate the schedule using the template
      actions:
         schedule: @actions.Generate_Personalized_Schedule
            with "Input:email"=...
            with "Input:preferences"=...
            set @variables.generated_schedule = @outputs.promptResponse
```

**Key Syntax Notes:**

| Element | Syntax | Notes |
|---------|--------|-------|
| Target | `generatePromptResponse://TemplateDeveloperName` | Uses the PromptTemplate's API name |
| Input naming | `"Input:fieldApiName"` | **Must** use `"Input:"` prefix with quotes |
| Output field | `promptResponse` | Standard field name for template response |
| Output flags | `is_used_by_planner: True`, `is_displayable: True` | Required for LLM to use response |

**Input Naming Convention:**

The `"Input:"` prefix is **required** to match PromptTemplate variable references:

```agentscript
# PromptTemplate has variable: customerEmail
# Agent Script input MUST be: "Input:customerEmail"

inputs:
   "Input:customerEmail": string     # ← Quotes required due to colon
      description: "Customer's email address"
```

**Complete Example - Email Generation Agent:**

```agentscript
system:
   instructions: "You help users draft professional emails."
   messages:
      welcome: "I can help you draft emails!"
      error: "Sorry, something went wrong."

config:
   agent_name: "Email_Drafter"
   default_agent_user: "agent@company.com"
   agent_label: "Email Drafter"
   description: "Drafts professional emails using AI"

variables:
   recipient: mutable string
      description: "Email recipient"
   subject: mutable string
      description: "Email subject"
   draft: mutable string
      description: "Generated email draft"

language:
   default_locale: "en_US"
   additional_locales: ""
   all_additional_locales: False

start_agent topic_selector:
   label: "Email Drafter"
   description: "Draft professional emails"

   actions:
      draft_email:
         description: "Generate a professional email draft"
         inputs:
            "Input:recipient": string
               description: "Who the email is for"
               is_required: True
            "Input:subject": string
               description: "Email subject"
               is_required: True
            "Input:tone": string
               description: "Desired tone (formal, friendly, urgent)"
               is_required: False
         outputs:
            promptResponse: string
               description: "Generated email draft"
               is_used_by_planner: True
               is_displayable: True
         target: "generatePromptResponse://Professional_Email_Template"

   reasoning:
      instructions: ->
         | Help the user draft a professional email.
         | Ask for: recipient, subject, and preferred tone.
         | Use the draft_email action to generate the content.
      actions:
         generate: @actions.draft_email
            with "Input:recipient"=...
            with "Input:subject"=...
            with "Input:tone"=...
            set @variables.draft = @outputs.promptResponse
```

**When to Use Each Approach:**

| Approach | Use When |
|----------|----------|
| `generatePromptResponse://` in Agent Script | Simple template invocation, quick setup |
| GenAiFunction + `prompt://` | Complex scenarios, reusable across agents, need more control |

### Template Types

| Type | Use Case |
|------|----------|
| `flexPrompt` | General purpose, maximum flexibility |
| `salesGeneration` | Sales content (emails, proposals) |
| `fieldCompletion` | Suggest field values |
| `recordSummary` | Summarize record data |

### Variable Types

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
┌─────────────────────────────────────────────────────────────────────────────┐
│  INTEGRATION + AGENTFORCE ORCHESTRATION ORDER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. sf-connected-apps  → Create Connected App (if OAuth needed)             │
│  2. sf-integration     → Create Named Credential + External Service         │
│  3. sf-apex            → Create @InvocableMethod (if custom logic needed)   │
│  4. sf-flow            → Create Flow wrapper (HTTP Callout or Apex wrapper) │
│  5. sf-deploy          → Deploy all metadata to org                         │
│  6. sf-ai-agentforce   → Create agent with flow:// target                   │
│  7. sf-deploy          → Publish agent (sf agent publish)                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Skill Invocation Examples

**For External API Action:**
```
"Create an agent that can check inventory in our warehouse system via REST API"

Skills invoked:
1. sf-integration → Named Credential, HTTP Callout Flow
2. sf-ai-agentforce → Agent Script with flow:// action
3. sf-deploy → Deploy and publish
```

**For Complex Apex Action:**
```
"Create an agent action that calculates shipping costs based on complex rules"

Skills invoked:
1. sf-apex → @InvocableMethod class
2. sf-ai-agentforce → GenAiFunction metadata
3. sf-deploy → Deploy
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Action not appearing | GenAiFunction not deployed | Deploy metadata with sf-deploy |
| `apex://` not working | Known limitation | Use GenAiFunction metadata instead |
| Flow action fails | Flow not active | Activate the Flow |
| API action timeout | External system slow | Increase timeout, add retry logic |
| Permission denied | Missing Named Principal access | Grant Permission Set |

### Debugging Tips

1. **Check deployment status:**
   ```bash
   sf project deploy report
   ```

2. **Verify GenAiFunction deployment:**
   ```bash
   sf org list metadata -m GenAiFunction
   ```

3. **Test Flow independently:**
   - Use Flow debugger in Setup
   - Test with sample inputs

4. **Check agent logs:**
   - Agent Builder → Logs
   - Einstein Activity Capture

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
| `outbound_route_type` | String | Yes | **MUST be `"OmniChannelFlow"`** - only valid value |
| `outbound_route_name` | String | Yes | API name of Omni-Channel Flow (must exist in org) |
| `escalation_message` | String | Yes | Message shown to user during transfer |
| `adaptive_response_allowed` | Boolean | No | Allow agent to adapt responses during escalation (default: False) |

### Supported Channels

| Channel | Description | Use Case |
|---------|-------------|----------|
| `messaging` | Chat/messaging channels | Enhanced Chat, Web Chat, In-App |
| `telephony` | Voice/phone channels | Service Cloud Voice, phone support |

**⚠️ CRITICAL**: Values like `"queue"`, `"skill"`, `"agent"` for `outbound_route_type` cause validation errors!

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

## GenAiFunction Metadata (Summary)

`GenAiFunction` wraps Apex, Flows, or Prompts as Agent Actions. See `templates/metadata/` for XML templates.

```xml
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Display Name</masterLabel>
    <developerName>API_Name</developerName>
    <description>What this action does</description>
    <invocationTarget>FlowOrApexName</invocationTarget>
    <invocationTargetType>flow|apex|prompt</invocationTargetType>
</GenAiFunction>
```

**Templates available**: `templates/metadata/genai-function-apex.xml`, `templates/metadata/genai-function-flow.xml`

---

## Best Practices Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BEST PRACTICES CHECKLIST                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ☐ Use descriptive action names and descriptions                            │
│  ☐ Always handle errors gracefully                                          │
│  ☐ Use Named Credentials for all external callouts                          │
│  ☐ Test actions independently before adding to agent                        │
│  ☐ Document input/output parameters clearly                                 │
│  ☐ Consider governor limits in Apex actions                                 │
│  ☐ Use confirmation for destructive actions                                 │
│  ☐ Implement proper logging for debugging                                   │
│  ☐ Follow bulkification patterns                                            │
│  ☐ Keep prompt templates focused and specific                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [Agent Script Reference](agent-script-reference.md) - Complete syntax guide
- [Prompt Templates](prompt-templates.md) - PromptTemplate metadata
- [Patterns & Practices](patterns-and-practices.md) - Best practices
- [CLI Guide](cli-guide.md) - Deployment commands
