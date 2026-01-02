# Actions Implementation Guide

Complete guide to implementing actions in Agentforce agents, including Flow, Apex, external API integrations, and advanced patterns.

## Table of Contents

- [Action Fundamentals](#action-fundamentals)
- [Complete Action Type Reference](#complete-action-type-reference)
- [Flow Actions](#flow-actions)
- [Apex Actions (via Flow Wrapper)](#apex-actions-via-flow-wrapper)
- [Data Type Mappings](#data-type-mappings)
- [Advanced Action Fields](#advanced-action-fields)
- [Action Callbacks](#action-callbacks)
- [Slot Filling Patterns](#slot-filling-patterns)
- [Best Practices](#best-practices)

---

## Action Fundamentals

**Actions** are the executable operations your agent can perform - calling Flows, Apex, external APIs, or generating AI content.

### Action Structure

```agentscript
actions:
   [action_name]:
      description: "What this action does"
      inputs:
         [input_name]: [type]
            description: "Input description"
            is_required: [True/False]
      outputs:
         [output_name]: [type]
            description: "Output description"
            is_used_by_planner: [True/False]
      target: "[protocol]://[TargetName]"
```

---

## Complete Action Type Reference

AgentScript supports 22+ action target types. Use the appropriate protocol prefix:

| Short Name | Long Name (Alias) | Description | Use When |
|------------|-------------------|-------------|----------|
| `flow` | `flow` | Salesforce Flow | **PRIMARY** - Most reliable, recommended for all actions |
| `apex` | `apex` | Apex Class (@InvocableMethod) | Custom server-side logic (use Flow wrapper in AiAuthoringBundle) |
| `prompt` | `generatePromptResponse` | Prompt Template | AI content generation |
| `standardInvocableAction` | `standardInvocableAction` | Built-in Salesforce actions | Standard platform actions (send email, create task) |
| `externalService` | `externalService` | External API via OpenAPI schema | External system calls via External Services |
| `quickAction` | `quickAction` | Object-specific quick actions | Quick actions (log call, create related record) |
| `api` | `api` | REST API calls | Direct Salesforce API calls |
| `apexRest` | `apexRest` | Apex REST endpoints | Custom REST services |
| `serviceCatalog` | `createCatalogItemRequest` | Service Catalog requests | IT service requests, catalog items |
| `integrationProcedureAction` | `executeIntegrationProcedure` | OmniStudio Integration Procedure | OmniStudio/Vlocity integrations |
| `expressionSet` | `runExpressionSet` | Expression Set calculations | Business rule calculations |
| `cdpMlPrediction` | `cdpMlPrediction` | CDP ML predictions | Customer Data Platform ML models |
| `externalConnector` | `externalConnector` | External system connector | Pre-built external connectors |
| `slack` | `slack` | Slack integration | Slack-specific actions |
| `namedQuery` | `namedQuery` | Predefined SOQL queries | Named queries for data retrieval |
| `auraEnabled` | `auraEnabled` | Aura-enabled Apex methods | Lightning component methods |
| `mcpTool` | `mcpTool` | Model Context Protocol tools | MCP tool integrations |
| `retriever` | `retriever` | Knowledge retrieval | Knowledge base searches |

**Target Format**: `<type>://<DeveloperName>` (e.g., `flow://Get_Account_Info`, `standardInvocableAction://sendEmail`)

**0-shot Tip**: If you need a built-in action, check if `standardInvocableAction://` applies before creating a custom Flow.

### Action Targets by Deployment Method

| Target Type | GenAiPlannerBundle | AiAuthoringBundle |
|-------------|-------------------|-------------------|
| `flow://FlowName` | Works | Works (with exact name matching) |
| `apex://ClassName` | Works | Limited (class must exist) |
| `prompt://TemplateName` | Works | Requires asset in org |

---

## Flow Actions

**RECOMMENDED**: Use `flow://` for all actions - it's the most reliable and works in both deployment methods.

### Critical Requirements

**`flow://` actions work in BOTH AiAuthoringBundle and GenAiPlannerBundle**, but require:

1. **EXACT variable name matching** between Agent Script and Flow
2. Flow must be an **Autolaunched Flow** (not Screen Flow)
3. Flow variables must be marked "Available for input" / "Available for output"
4. Flow must be deployed to org **BEFORE** agent publish

**The "Internal Error" occurs when input/output names don't match Flow variables!**

```
ERROR: "property account_id was not found in the available list of
        properties: [inp_AccountId]"

This error appears as generic "Internal Error, try again later" in CLI.
```

### Correct Flow Action Pattern

**Step 1: Create Flow with specific variable names**

```xml
<!-- Get_Account_Info.flow-meta.xml -->
<variables>
    <name>inp_AccountId</name>     <!-- INPUT variable -->
    <dataType>String</dataType>
    <isInput>true</isInput>
    <isOutput>false</isOutput>
</variables>
<variables>
    <name>out_AccountName</name>   <!-- OUTPUT variable -->
    <dataType>String</dataType>
    <isInput>false</isInput>
    <isOutput>true</isOutput>
</variables>
```

**Step 2: Agent Script MUST use EXACT same names**

```agentscript
actions:
   get_account:
      description: "Retrieves account information"
      inputs:
         inp_AccountId: string        # ← MUST match Flow variable name!
            description: "Salesforce Account ID"
      outputs:
         out_AccountName: string      # ← MUST match Flow variable name!
            description: "Account name"
      target: "flow://Get_Account_Info"
```

### Common Mistake (Causes "Internal Error")

```agentscript
# ❌ WRONG - Names don't match Flow variables
actions:
   get_account:
      inputs:
         account_id: string           # Flow expects "inp_AccountId"!
      outputs:
         account_name: string         # Flow expects "out_AccountName"!
      target: "flow://Get_Account_Info"
```

This will fail with "Internal Error, try again later" because the schema validation fails silently.

### Flow Validation Timing

**Flow existence is validated at DEPLOYMENT time, NOT during `sf agent validate`!**

| Command | What It Checks | Flow Validation |
|---------|----------------|-----------------|
| `sf agent validate authoring-bundle` | Syntax only | Does NOT check if flows exist |
| `sf project deploy start` | Full deployment | Validates flow existence |

**This means:**
- An agent can **PASS validation** with `sf agent validate authoring-bundle`
- But **FAIL deployment** if the referenced flow doesn't exist in the org

```bash
# ✅ Passes - only checks Agent Script syntax
sf agent validate authoring-bundle --api-name My_Agent --target-org MyOrg
# Status: COMPLETED, Errors: 0

# ❌ Fails - flow doesn't exist in org
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/My_Agent
# Error: "We couldn't find the flow, prompt, or apex class: flow://Missing_Flow"
```

**Best Practice: Always deploy flows BEFORE deploying agents that reference them.**

### Flow Actions in AiAuthoringBundle

**Flow actions (`flow://`) DO work in AiAuthoringBundle**, but require a specific pattern:

```agentscript
# ✅ CORRECT PATTERN FOR AiAuthoringBundle
# 1. Define actions in topic blocks (NOT start_agent)
# 2. Use simple action definition (no with/set in reasoning.actions)
# 3. Let the LLM decide when to call the action based on description

start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes users to topics"

   # ✅ start_agent should ONLY have @utils.transition actions
   reasoning:
      instructions: ->
         | Route the user to the appropriate topic.
      actions:
         go_to_orders: @utils.transition to @topic.order_lookup

topic order_lookup:
   label: "Order Lookup"
   description: "Looks up order information"

   # ✅ Define flow actions in the topic's actions: block
   actions:
      get_order:
         description: "Retrieves order details by order number"
         inputs:
            inp_OrderNumber: string
               description: "The order number to look up"
         outputs:
            out_OrderStatus: string
               description: "Status of the order"
            out_OrderTotal: number
               description: "Total amount of the order"
         target: "flow://Get_Order_Details"

   # ✅ Simple reasoning - no with/set in reasoning.actions
   reasoning:
      instructions: ->
         | Help the user look up their order.
         | Ask for the order number if not provided.
         | Use the get_order action to retrieve details.
      actions:
         back_to_menu: @utils.transition to @topic.topic_selector
```

**WRONG PATTERN (causes "Internal Error" at publish):**

```agentscript
# ❌ DO NOT put flow actions in start_agent
start_agent topic_selector:
   actions:
      my_flow_action:    # ❌ WRONG - actions in start_agent fail
         target: "flow://..."

# ❌ DO NOT use with/set in reasoning.actions (AiAuthoringBundle only)
reasoning:
   actions:
      lookup: @actions.get_order
         with inp_OrderNumber=...              # ❌ WRONG - causes Internal Error
         set @variables.status = @outputs...   # ❌ WRONG - causes Internal Error
```

**Key Requirements:**
1. **Flow actions in `topic` blocks only** - NOT in `start_agent`
2. **`start_agent` uses only `@utils.transition`** - for routing to topics
3. **No `with`/`set` in `reasoning.actions`** - just define actions, LLM auto-calls
4. **Input/output names must match Flow exactly** - Case-sensitive!

---

## Data Type Mappings

**Confirmed working data types between Agent Script and Flow:**

| Agent Script Type | Flow Data Type | Status | Notes |
|-------------------|----------------|--------|-------|
| `string` | String | Works | Standard text values |
| `number` | Number (scale=0) | Works | Integer values |
| `number` | Number (scale>0) | Works | Decimal values (e.g., 3.14) |
| `boolean` | Boolean | Works | Use `True`/`False` (capitalized) |
| `list[string]` | Text Collection | Works | Collection with `isCollection=true` |
| `string` | Date | Works* | *Use String I/O pattern (see below) |
| `string` | DateTime | Works* | *Use String I/O pattern (see below) |

### Date/DateTime Workaround Pattern

Agent Script does NOT have native `date` or `datetime` types. If you try to connect an Agent Script `string` input to a Flow `Date` or `DateTime` input, it will fail with "Internal Error" because the platform cannot coerce types.

**Solution: Use String I/O pattern**

1. **Flow accepts/returns Strings** (not Date/DateTime)
2. **Flow parses strings internally** using `DATEVALUE()` or `DATETIMEVALUE()`
3. **Flow converts back to string** using `TEXT()` for output

```xml
<!-- Flow with String I/O for Date handling -->
<variables>
    <name>inp_DateString</name>
    <dataType>String</dataType>       <!-- NOT Date -->
    <isInput>true</isInput>
</variables>
<variables>
    <name>out_DateString</name>
    <dataType>String</dataType>       <!-- NOT Date -->
    <isOutput>true</isOutput>
</variables>
<formulas>
    <name>formula_ParseDate</name>
    <dataType>Date</dataType>
    <expression>DATEVALUE({!inp_DateString})</expression>
</formulas>
<formulas>
    <name>formula_DateAsString</name>
    <dataType>String</dataType>
    <expression>TEXT({!formula_ParseDate})</expression>
</formulas>
```

```agentscript
# Agent Script with string type for date
actions:
   process_date:
      inputs:
         inp_DateString: string
            description: "A date value in YYYY-MM-DD format"
      outputs:
         out_DateString: string
            description: "The processed date as string"
      target: "flow://Test_Date_Type_StringIO"
```

### Collection Types (list[string])

`list[string]` maps directly to Flow Text Collection:

```xml
<variables>
    <name>inp_TextList</name>
    <dataType>String</dataType>
    <isCollection>true</isCollection>  <!-- This makes it a list -->
    <isInput>true</isInput>
</variables>
```

```agentscript
actions:
   process_collection:
      inputs:
         inp_TextList: list[string]
            description: "A list of text values"
      target: "flow://Test_Collection_StringIO"
```

### Important: All Flow inputs must be provided!

If Flow defines 6 input variables but Agent Script only provides 4, publish fails with "Internal Error":

```
❌ FAILS - Missing inputs
   Flow inputs:    inp_String, inp_Number, inp_Boolean, inp_Date
   Agent inputs:   inp_String, inp_Number, inp_Boolean
   Result: "Internal Error, try again later"

✅ WORKS - All inputs provided
   Flow inputs:    inp_String, inp_Number, inp_Boolean
   Agent inputs:   inp_String, inp_Number, inp_Boolean
   Result: Success
```

---

## Advanced Action Fields

For fine-grained control over action behavior, use the `object` type with `complex_data_type_name` and advanced field attributes.

> **Note**: The `filter_from_agent` attribute shown below is **GenAiPlannerBundle only**. It causes "Unexpected 'filter_from_agent'" errors in AiAuthoringBundle. Omit this attribute when using `sf agent publish authoring-bundle`.

```agentscript
actions:
   lookup_order:
      description: "Retrieve order details for a given Order Number."
      inputs:
         order_number: object
            description: "The Order Number the user has provided"
            label: "order_number"
            is_required: False
            is_user_input: False
            complex_data_type_name: "lightning__textType"
      outputs:
         order_id: object
            description: "The Record ID of the Order"
            label: "order_id"
            complex_data_type_name: "lightning__textType"
            filter_from_agent: False
            is_used_by_planner: True
            is_displayable: False
         order_is_current: object
            description: "Whether the order is current"
            label: "order_is_current"
            complex_data_type_name: "lightning__booleanType"
            filter_from_agent: False
            is_used_by_planner: True
            is_displayable: False
      target: "flow://lookup_order"
      label: "Lookup Order"
      require_user_confirmation: False
      include_in_progress_indicator: False
```

### Lightning Data Types (`complex_data_type_name`)

| Type | Description |
|------|-------------|
| `lightning__textType` | Text/String values |
| `lightning__numberType` | Numeric values |
| `lightning__booleanType` | Boolean True/False |
| `lightning__dateTimeStringType` | DateTime as string |

### Input Field Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_required` | Boolean | Whether the input must be provided |
| `is_user_input` | Boolean | Whether the LLM should collect from user |
| `label` | String | Display label for the field |
| `complex_data_type_name` | String | Lightning data type mapping |

### Output Field Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `filter_from_agent` | Boolean | Hide output from agent reasoning |
| `is_used_by_planner` | Boolean | Whether planner uses this output |
| `is_displayable` | Boolean | Show output to user |
| `complex_data_type_name` | String | Lightning data type mapping |

### Action-Level Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `label` | String | Display name for the action |
| `require_user_confirmation` | Boolean | Ask user before executing |
| `include_in_progress_indicator` | Boolean | Show progress during execution |

### Minimum Required Attributes

Only `description` and `complex_data_type_name` are required. All other attributes are optional:

```agentscript
# Minimal object type - works!
inputs:
   input_text: object
      description: "Text input"
      complex_data_type_name: "lightning__textType"
```

### Mixing Simple and Object Types

You can mix `string`/`number`/`boolean` with `object` types in the same action:

```agentscript
inputs:
   # Simple type (basic syntax)
   simple_text: string
      description: "A simple text input"
   # Object type (advanced syntax)
   advanced_text: object
      description: "An advanced text input"
      label: "Advanced Text"
      is_required: True
      is_user_input: True
      complex_data_type_name: "lightning__textType"
```

---

## Apex Actions (via Flow Wrapper)

**`apex://` targets work in GenAiPlannerBundle if the Apex class exists:**

```agentscript
# ✅ Works in GenAiPlannerBundle (if class exists in org)
target: "apex://CaseCreationService"
```

**The following do NOT work in either method:**
```agentscript
# ❌ DOES NOT WORK - Invalid format
target: "apex://CaseService.createCase"  # No method name allowed
target: "action://Create_Support_Case"   # action:// not supported
```

### RECOMMENDED: Use Flow Wrapper Pattern

The only reliable way to call Apex from Agent Script is to wrap the Apex in an Autolaunched Flow:

1. **Create Apex class** with `@InvocableMethod` annotation (use sf-apex skill)
2. **Deploy Apex** to org using `sf project deploy start`
3. **Create Autolaunched Flow wrapper** that calls the Apex via Action element:
   ```xml
   <actionCalls>
       <actionName>YourApexClassName</actionName>
       <actionType>apex</actionType>
       <!-- Map input/output variables -->
   </actionCalls>
   ```
4. **Deploy Flow** to org
5. **Reference Flow** in Agent Script:
```agentscript
# ✅ CORRECT - Use flow:// target pointing to Flow wrapper
target: "flow://Create_Support_Case"  # Flow that wraps Apex InvocableMethod
```

### Flow Wrapper Example

```xml
<!-- Create_Support_Case.flow-meta.xml -->
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <actionCalls>
        <name>Call_Apex_Service</name>
        <actionName>CaseCreationService</actionName>
        <actionType>apex</actionType>
        <inputParameters>
            <name>subject</name>
            <value><elementReference>inp_Subject</elementReference></value>
        </inputParameters>
        <outputParameters>
            <assignToReference>var_CaseNumber</assignToReference>
            <name>caseNumber</name>
        </outputParameters>
    </actionCalls>
    <!-- ... variables with isInput=true/isOutput=true ... -->
</Flow>
```

---

## Action Callbacks

**GenAiPlannerBundle only** - Use the `run` keyword to execute actions after another action completes:

```agentscript
# ✅ CORRECT - GenAiPlannerBundle
reasoning:
    actions:
        create_support_case: @actions.create_case
            with inp_CustomerId=@variables.ContactId
            with inp_Subject=...
            set @variables.case_number = @outputs.out_CaseNumber
            run @actions.send_confirmation_email
                with inp_CaseNumber=@variables.case_number
```

**For AiAuthoringBundle**: Define multiple actions separately and let the LLM choose when to call them:

```agentscript
# ✅ CORRECT - AiAuthoringBundle
actions:
   create_case:
      description: "Creates a support case"
      # ... inputs/outputs ...
   send_email:
      description: "Sends confirmation email after case creation"
      # ... inputs/outputs ...

reasoning:
   instructions: ->
      | Create the case first.
      | Then send a confirmation email to the customer.
```

---

## Slot Filling Patterns

**Problem**: LLM slot filling is unreliable - it may send empty JSON, wrong field names, or wrong values.

**Solution**: Use deterministic collection patterns with dedicated setter actions.

### Pattern: Critical Input Collection

```agentscript
variables:
   account_id: mutable string
      description: "The Account ID collected from user"

topic account_lookup:
   label: "Account Lookup"
   description: "Look up account information"

   actions:
      # Dedicated setter action (single-use)
      capture_account_id:
         description: "Capture the Account ID from the user. Ask them for it if not provided. This MUST be called first before any other actions."
         inputs:
            inp_AccountId: string
               description: "The 18-character Salesforce Account ID"
               is_required: True
               is_user_input: True
         target: "flow://Store_Account_ID"
         # Single-use - only available when NOT yet collected
         available when @variables.account_id == ""

      # Main action with null guard
      get_account_details:
         description: "Retrieves full account details using the stored Account ID"
         inputs:
            inp_AccountId: string
               description: "Account ID"
         outputs:
            out_AccountName: string
               description: "Account name"
         target: "flow://Get_Account_Info"
         # Null guard - only available when ID is collected
         available when @variables.account_id != ""

   reasoning:
      instructions: ->
         | FIRST, use {!@actions.capture_account_id} to collect the Account ID.
         | THEN, use {!@actions.get_account_details} to look up the account.
         |
         | if @variables.account_id == "":
         |    | I need your Account ID to proceed.
         | else:
         |    | Looking up account: {!@variables.account_id}
      actions:
         capture_id: @actions.capture_account_id
            set @variables.account_id = @outputs.stored_id
         lookup: @actions.get_account_details
            with inp_AccountId=@variables.account_id
```

**Key Elements:**
1. **Dedicated setter action** - Sole purpose is to collect the critical input
2. **Single-use availability** - `available when @variables.x == ""` prevents re-collection
3. **Null guards on downstream actions** - `available when @variables.x != ""` prevents premature execution
4. **Explicit action references** - `{!@actions.capture_id}` improves LLM reliability
5. **First-interaction instructions** - "FIRST... THEN..." guides LLM execution order

### Pattern: Multi-Step Workflow with Progress Flags

```agentscript
variables:
   step1_done: mutable boolean
      description: "Step 1 completed"
   step2_done: mutable boolean
      description: "Step 2 completed"

actions:
   step1:
      description: "Execute step 1 of the workflow"
      # ... inputs/outputs ...
      target: "flow://Step1"
      available when @variables.step1_done == False

   step2:
      description: "Execute step 2 of the workflow"
      # ... inputs/outputs ...
      target: "flow://Step2"
      available when @variables.step1_done == True
      available when @variables.step2_done == False

reasoning:
   instructions: ->
      | if @variables.step1_done == False:
      |    | Execute step 1 first.
      | if @variables.step1_done == True and @variables.step2_done == False:
      |    | Now execute step 2.
   actions:
      execute_step1: @actions.step1
         set @variables.step1_done = True
      execute_step2: @actions.step2
         set @variables.step2_done = True
```

---

## Best Practices

### Action Design Principles

1. **Clear Descriptions**: LLM uses descriptions to choose actions - be specific
2. **Explicit References**: Use `{!@actions.x}` in instructions to guide LLM
3. **Null Guards**: Use `available when` to prevent execution without required inputs
4. **Single Responsibility**: Each action should do ONE thing
5. **Deterministic Collection**: Don't rely on slot filling for critical inputs

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Action name | snake_case | `get_account_details` |
| Input/output | snake_case with prefix | `inp_AccountId`, `out_AccountName` |
| Flow variables | Prefix with `inp_` or `out_` | `inp_CustomerId`, `out_CaseNumber` |

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Mismatched variable names | Agent Script names MUST match Flow variable API names exactly |
| Missing Flow inputs | Provide ALL inputs that Flow expects |
| Reserved words as inputs | Use alternative names (e.g., `case_description` instead of `description`) |
| Flow not deployed | Deploy flows BEFORE agent publish |
| Relying on slot filling | Use dedicated setter actions for critical inputs |

### Action Requirements Summary

| Requirement | Details |
|-------------|---------|
| **Variable Name Matching** | Agent Script input/output names MUST exactly match Flow variable API names |
| **Flow Type** | Must be **Autolaunched Flow** (not Screen Flow) |
| **Flow Variables** | Mark as "Available for input" / "Available for output" |
| **Deploy Order** | Deploy Flow to org BEFORE publishing agent |
| **API Version** | API v65.0+ required for both AiAuthoringBundle and GenAiPlannerBundle |
| **All Inputs Required** | Agent Script must define ALL inputs that Flow expects (missing inputs = Internal Error) |

---

## References

For additional information, see:
- [../docs/actions-reference.md](../docs/actions-reference.md) - Complete actions reference
- [../docs/patterns-and-practices.md](../docs/patterns-and-practices.md) - Action patterns and best practices
- [agent-script-reference.md](agent-script-reference.md) - Full Agent Script syntax
- [deployment-guide.md](deployment-guide.md) - Deployment workflow and CLI commands
