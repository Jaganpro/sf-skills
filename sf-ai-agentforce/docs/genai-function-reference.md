# GenAiFunction Metadata Reference

> Complete reference for GenAiFunction metadata structure in Salesforce Agentforce

## Overview

`GenAiFunction` is the metadata type that exposes capabilities (Apex, Flows, Prompts) as Agent Actions. It's the bridge between your business logic and Agentforce agents.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      GenAiFunction PURPOSE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  @InvocableMethod    ─────►  GenAiFunction  ─────►  Agent Action            │
│  Flow                ─────►  GenAiFunction  ─────►  Agent Action            │
│  PromptTemplate      ─────►  GenAiFunction  ─────►  Agent Action            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Metadata Structure

### Full Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <!-- Required: Display name in Agent Builder -->
    <masterLabel>{{Display Label}}</masterLabel>

    <!-- Required: API name -->
    <developerName>{{API_Name}}</developerName>

    <!-- Required: Description shown in Agent Builder -->
    <description>{{Description of what this function does}}</description>

    <!-- Required: What to invoke -->
    <invocationTarget>{{ClassName|FlowAPIName|PromptTemplateName}}</invocationTarget>

    <!-- Required: Type of target -->
    <invocationTargetType>{{apex|flow|prompt}}</invocationTargetType>

    <!-- Optional: Require user confirmation before execution -->
    <isConfirmationRequired>{{true|false}}</isConfirmationRequired>

    <!-- Optional: Natural language description for the AI -->
    <capability>{{Detailed capability description for the agent}}</capability>

    <!-- Input parameters (0 or more) -->
    <genAiFunctionInputs>
        <developerName>{{paramName}}</developerName>
        <description>{{Parameter description}}</description>
        <dataType>{{Text|Number|Boolean|Date|DateTime}}</dataType>
        <isRequired>{{true|false}}</isRequired>
    </genAiFunctionInputs>

    <!-- Output parameters (0 or more) -->
    <genAiFunctionOutputs>
        <developerName>{{outputName}}</developerName>
        <description>{{Output description}}</description>
        <dataType>{{Text|Number|Boolean|Date|DateTime}}</dataType>
    </genAiFunctionOutputs>
</GenAiFunction>
```

---

## Element Reference

### Root Element: GenAiFunction

| Element | Required | Description |
|---------|----------|-------------|
| `masterLabel` | Yes | Display name in Agent Builder UI |
| `developerName` | Yes | API name (unique identifier) |
| `description` | Yes | Brief description of the function |
| `invocationTarget` | Yes | Name of Apex class, Flow, or PromptTemplate |
| `invocationTargetType` | Yes | Type: `apex`, `flow`, or `prompt` |
| `isConfirmationRequired` | No | If `true`, agent asks user to confirm |
| `capability` | No | Natural language description for AI reasoning |

### invocationTargetType Values

| Value | Target | Example |
|-------|--------|---------|
| `apex` | @InvocableMethod class | `CalculateDiscountAction` |
| `flow` | Autolaunched Flow | `Create_Support_Case` |
| `prompt` | PromptTemplate | `Case_Summary_Generator` |

### genAiFunctionInputs

| Element | Required | Description |
|---------|----------|-------------|
| `developerName` | Yes | Parameter API name |
| `description` | Yes | Description for AI understanding |
| `dataType` | Yes | Data type of the parameter |
| `isRequired` | Yes | Whether parameter is required |

### genAiFunctionOutputs

| Element | Required | Description |
|---------|----------|-------------|
| `developerName` | Yes | Output API name |
| `description` | Yes | Description of the output |
| `dataType` | Yes | Data type of the output |

### Supported Data Types

| Data Type | Apex Equivalent | Description |
|-----------|-----------------|-------------|
| `Text` | `String` | Text/string values |
| `Number` | `Decimal`, `Integer` | Numeric values |
| `Boolean` | `Boolean` | True/false |
| `Date` | `Date` | Date without time |
| `DateTime` | `DateTime` | Date with time |

---

## Complete Examples

### Example 1: Apex Action

**Use Case:** Calculate shipping costs based on weight, destination, and service level.

**Apex Class:**
```apex
public with sharing class CalculateShippingAction {

    public class ShippingRequest {
        @InvocableVariable(label='Weight in Pounds' required=true)
        public Decimal weightLbs;

        @InvocableVariable(label='Destination Zip Code' required=true)
        public String destinationZip;

        @InvocableVariable(label='Service Level' required=true)
        public String serviceLevel; // Standard, Express, Overnight
    }

    public class ShippingResult {
        @InvocableVariable(label='Shipping Cost')
        public Decimal cost;

        @InvocableVariable(label='Estimated Days')
        public Integer estimatedDays;

        @InvocableVariable(label='Carrier')
        public String carrier;
    }

    @InvocableMethod(
        label='Calculate Shipping Cost'
        description='Calculates shipping cost based on weight, destination, and service level'
    )
    public static List<ShippingResult> calculate(List<ShippingRequest> requests) {
        List<ShippingResult> results = new List<ShippingResult>();

        for (ShippingRequest req : requests) {
            ShippingResult result = new ShippingResult();

            // Calculate based on service level
            if (req.serviceLevel == 'Overnight') {
                result.cost = req.weightLbs * 5.99;
                result.estimatedDays = 1;
                result.carrier = 'FedEx';
            } else if (req.serviceLevel == 'Express') {
                result.cost = req.weightLbs * 3.49;
                result.estimatedDays = 2;
                result.carrier = 'UPS';
            } else {
                result.cost = req.weightLbs * 1.99;
                result.estimatedDays = 5;
                result.carrier = 'USPS';
            }

            results.add(result);
        }

        return results;
    }
}
```

**GenAiFunction Metadata:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Calculate Shipping Cost</masterLabel>
    <developerName>Calculate_Shipping_Cost</developerName>
    <description>Calculates shipping cost based on package weight, destination, and service level</description>

    <invocationTarget>CalculateShippingAction</invocationTarget>
    <invocationTargetType>apex</invocationTargetType>

    <isConfirmationRequired>false</isConfirmationRequired>

    <capability>
        Calculate shipping costs for packages. Supports three service levels:
        - Standard: 5-day delivery via USPS
        - Express: 2-day delivery via UPS
        - Overnight: Next-day delivery via FedEx

        Ask for weight in pounds, destination zip code, and preferred service level.
    </capability>

    <genAiFunctionInputs>
        <developerName>weightLbs</developerName>
        <description>Package weight in pounds</description>
        <dataType>Number</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionInputs>
        <developerName>destinationZip</developerName>
        <description>Destination zip code (5 digits)</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionInputs>
        <developerName>serviceLevel</developerName>
        <description>Shipping speed: Standard, Express, or Overnight</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionOutputs>
        <developerName>cost</developerName>
        <description>Calculated shipping cost in dollars</description>
        <dataType>Number</dataType>
    </genAiFunctionOutputs>

    <genAiFunctionOutputs>
        <developerName>estimatedDays</developerName>
        <description>Estimated delivery time in days</description>
        <dataType>Number</dataType>
    </genAiFunctionOutputs>

    <genAiFunctionOutputs>
        <developerName>carrier</developerName>
        <description>Shipping carrier name</description>
        <dataType>Text</dataType>
    </genAiFunctionOutputs>
</GenAiFunction>
```

**File Location:**
```
force-app/main/default/genAiFunctions/Calculate_Shipping_Cost.genAiFunction-meta.xml
```

---

### Example 2: Flow Action

**Use Case:** Create a support case and send notification.

**GenAiFunction Metadata:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Create Support Case</masterLabel>
    <developerName>Create_Support_Case</developerName>
    <description>Creates a new support case and notifies the support team</description>

    <invocationTarget>Create_Support_Case_Flow</invocationTarget>
    <invocationTargetType>flow</invocationTargetType>

    <isConfirmationRequired>true</isConfirmationRequired>

    <capability>
        Create support cases for customers. Collects subject, description,
        priority, and contact information. Automatically assigns to the
        appropriate queue based on case type.
    </capability>

    <genAiFunctionInputs>
        <developerName>subject</developerName>
        <description>Brief summary of the issue</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionInputs>
        <developerName>description</developerName>
        <description>Detailed description of the problem</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionInputs>
        <developerName>priority</developerName>
        <description>Case priority: Low, Medium, High, or Urgent</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionInputs>
        <developerName>contactEmail</developerName>
        <description>Contact email for follow-up</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionOutputs>
        <developerName>caseNumber</developerName>
        <description>Assigned case number</description>
        <dataType>Text</dataType>
    </genAiFunctionOutputs>

    <genAiFunctionOutputs>
        <developerName>caseId</developerName>
        <description>Salesforce record ID</description>
        <dataType>Text</dataType>
    </genAiFunctionOutputs>
</GenAiFunction>
```

---

### Example 3: Prompt Template Action

**Use Case:** Generate email response draft.

**GenAiFunction Metadata:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Draft Email Response</masterLabel>
    <developerName>Draft_Email_Response</developerName>
    <description>Generates a professional email response draft</description>

    <invocationTarget>Email_Response_Generator</invocationTarget>
    <invocationTargetType>prompt</invocationTargetType>

    <isConfirmationRequired>false</isConfirmationRequired>

    <capability>
        Draft professional email responses based on incoming email content
        and case context. Maintains brand voice and addresses customer
        concerns appropriately.
    </capability>

    <genAiFunctionInputs>
        <developerName>caseId</developerName>
        <description>The Case record ID for context</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionInputs>
        <developerName>tone</developerName>
        <description>Desired tone: Professional, Friendly, or Empathetic</description>
        <dataType>Text</dataType>
        <isRequired>false</isRequired>
    </genAiFunctionInputs>

    <genAiFunctionOutputs>
        <developerName>emailDraft</developerName>
        <description>Generated email draft</description>
        <dataType>Text</dataType>
    </genAiFunctionOutputs>
</GenAiFunction>
```

---

## GenAiPlugin (Topic Container)

`GenAiPlugin` groups related `GenAiFunction` entries into a topic.

### Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiPlugin xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>{{Plugin Display Name}}</masterLabel>
    <developerName>{{Plugin_API_Name}}</developerName>
    <description>{{Plugin description}}</description>

    <pluginType>Standard</pluginType>

    <pluginInstructions>
        {{Natural language instructions for using functions in this plugin}}
    </pluginInstructions>

    <genAiFunctions>
        <function>{{GenAiFunction1_DeveloperName}}</function>
    </genAiFunctions>
    <genAiFunctions>
        <function>{{GenAiFunction2_DeveloperName}}</function>
    </genAiFunctions>
</GenAiPlugin>
```

### Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiPlugin xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Order Management</masterLabel>
    <developerName>Order_Management_Plugin</developerName>
    <description>Functions for managing customer orders</description>

    <pluginType>Standard</pluginType>

    <pluginInstructions>
        Use these functions to help customers with order-related requests.
        Always verify the customer's identity before providing order details.
        For order modifications, confirm changes before executing.
        Escalate to a human agent if the customer is dissatisfied.
    </pluginInstructions>

    <genAiFunctions>
        <function>Get_Order_Status</function>
    </genAiFunctions>
    <genAiFunctions>
        <function>Update_Shipping_Address</function>
    </genAiFunctions>
    <genAiFunctions>
        <function>Cancel_Order</function>
    </genAiFunctions>
    <genAiFunctions>
        <function>Request_Refund</function>
    </genAiFunctions>
</GenAiPlugin>
```

**File Location:**
```
force-app/main/default/genAiPlugins/Order_Management_Plugin.genAiPlugin-meta.xml
```

---

## Deployment

### package.xml Entry

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>GenAiFunction</name>
    </types>
    <types>
        <members>*</members>
        <name>GenAiPlugin</name>
    </types>
    <version>62.0</version>
</Package>
```

### Deploy Command

```bash
# Deploy specific function
sf project deploy start -m "GenAiFunction:Calculate_Shipping_Cost"

# Deploy all functions
sf project deploy start -m "GenAiFunction:*"

# Deploy plugin with functions
sf project deploy start -m "GenAiFunction:*" -m "GenAiPlugin:*"
```

### Retrieve Command

```bash
# Retrieve all GenAiFunctions
sf project retrieve start -m "GenAiFunction:*"

# Retrieve specific function
sf project retrieve start -m "GenAiFunction:Calculate_Shipping_Cost"
```

---

## Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GenAiFunction BEST PRACTICES                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NAMING                                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ✅ Use verb_noun pattern: Calculate_Shipping, Create_Case                  │
│  ✅ Match developerName to invocationTarget where possible                  │
│  ❌ Avoid abbreviations: Calc_Ship, Crt_Cs                                  │
│                                                                             │
│  CAPABILITY DESCRIPTION                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ✅ Write natural language the AI can understand                            │
│  ✅ Include edge cases and constraints                                      │
│  ✅ Specify valid parameter values                                          │
│  ❌ Don't be too brief or technical                                         │
│                                                                             │
│  INPUTS/OUTPUTS                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ✅ Use descriptive parameter names                                         │
│  ✅ Provide clear descriptions for AI reasoning                             │
│  ✅ Mark truly required params as required                                  │
│  ❌ Don't require optional parameters                                       │
│                                                                             │
│  CONFIRMATION                                                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ✅ Use isConfirmationRequired=true for destructive actions                 │
│  ✅ Confirm: delete, cancel, refund, update sensitive data                  │
│  ❌ Don't require confirmation for read-only operations                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Function not in Agent Builder | Not deployed | Run `sf project deploy start` |
| "Invocation target not found" | Apex/Flow doesn't exist | Deploy target first |
| Inputs not mapping | Name mismatch | Match developerName to @InvocableVariable name |
| Function fails silently | Apex exception | Add error handling, check debug logs |

---

## Related Documentation

- [Agent Actions Guide](./agent-actions-guide.md)
- [Prompt Template Guide](./prompt-template-guide.md)
- [sf-apex Skill](../../sf-apex/skills/sf-apex/SKILL.md)
