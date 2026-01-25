<!-- TIER: 3 | DETAILED REFERENCE -->
<!-- Read after: SKILL.md, agent-script-reference.md -->
<!-- Purpose: PromptTemplate metadata and generatePromptResponse:// actions -->

# Prompt Templates

> Complete guide to creating PromptTemplate metadata for Salesforce Einstein and Agentforce

## Overview

`PromptTemplate` is the metadata type for creating reusable AI prompts in Salesforce. Templates can be used by Einstein features, Agentforce agents, and custom Apex code.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROMPT TEMPLATE ECOSYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PromptTemplate  ──────►  Einstein Prompt Builder (UI)                      │
│                  ──────►  GenAiFunction (Agent Actions)                     │
│                  ──────►  ConnectApi.Einstein.evaluatePrompt() (Apex)       │
│                  ──────►  Flow Prompt Template Action                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Template Types

| Type | Use Case | Example |
|------|----------|---------|
| `flexPrompt` | General purpose, maximum flexibility | Custom AI tasks |
| `salesGeneration` | Sales content creation | Email drafts, proposals |
| `fieldCompletion` | Suggest field values | Auto-populate fields |
| `recordSummary` | Summarize record data | Case summaries, account briefs |

---

## Metadata Structure

### Full Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <!-- Required: API name -->
    <fullName>{{TemplateName}}</fullName>

    <!-- Required: Display name -->
    <masterLabel>{{Template Display Label}}</masterLabel>

    <!-- Required: Description -->
    <description>{{What this template does}}</description>

    <!-- Required: Template type -->
    <type>{{flexPrompt|salesGeneration|fieldCompletion|recordSummary}}</type>

    <!-- Required: Active status -->
    <isActive>true</isActive>

    <!-- Optional: Primary object (for record-bound templates) -->
    <objectType>{{ObjectApiName}}</objectType>

    <!-- Required: The prompt content -->
    <promptContent>
        {{Your prompt with {!variable} placeholders}}
    </promptContent>

    <!-- Variable definitions (0 or more) -->
    <promptTemplateVariables>
        <developerName>{{variableName}}</developerName>
        <promptTemplateVariableType>{{freeText|recordField|relatedList|resource}}</promptTemplateVariableType>
        <isRequired>{{true|false}}</isRequired>
        <!-- For recordField type -->
        <objectType>{{ObjectApiName}}</objectType>
        <fieldName>{{FieldApiName}}</fieldName>
    </promptTemplateVariables>
</PromptTemplate>
```

---

## Variable Types

### freeText

User-provided text input at runtime.

```xml
<promptTemplateVariables>
    <developerName>customerQuestion</developerName>
    <promptTemplateVariableType>freeText</promptTemplateVariableType>
    <isRequired>true</isRequired>
</promptTemplateVariables>
```

**Usage in prompt:**
```
Customer Question: {!customerQuestion}
```

### recordField

Binds to a specific field on a Salesforce record.

```xml
<promptTemplateVariables>
    <developerName>accountName</developerName>
    <promptTemplateVariableType>recordField</promptTemplateVariableType>
    <objectType>Account</objectType>
    <fieldName>Name</fieldName>
    <isRequired>true</isRequired>
</promptTemplateVariables>
```

**Relationship traversal:**
```xml
<promptTemplateVariables>
    <developerName>ownerEmail</developerName>
    <promptTemplateVariableType>recordField</promptTemplateVariableType>
    <objectType>Case</objectType>
    <fieldName>Owner.Email</fieldName>
    <isRequired>false</isRequired>
</promptTemplateVariables>
```

### relatedList

Data from related records.

```xml
<promptTemplateVariables>
    <developerName>recentCases</developerName>
    <promptTemplateVariableType>relatedList</promptTemplateVariableType>
    <objectType>Account</objectType>
    <fieldName>Cases</fieldName>
    <isRequired>false</isRequired>
</promptTemplateVariables>
```

### resource

Content from a Static Resource.

```xml
<promptTemplateVariables>
    <developerName>brandGuidelines</developerName>
    <promptTemplateVariableType>resource</promptTemplateVariableType>
    <resourceName>Brand_Voice_Guidelines</resourceName>
    <isRequired>false</isRequired>
</promptTemplateVariables>
```

---

## Complete Examples

### Example 1: Flex Prompt (General Purpose)

**Use Case:** Answer questions using knowledge base context.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Knowledge_Assistant</fullName>
    <masterLabel>Knowledge Assistant</masterLabel>
    <description>Answers questions using knowledge article context</description>

    <type>flexPrompt</type>
    <isActive>true</isActive>

    <promptContent>
You are a helpful customer support assistant for {{CompanyName}}.

Use the following knowledge base context to answer the customer's question:

--- KNOWLEDGE CONTEXT ---
{!knowledgeContext}
--- END CONTEXT ---

Customer Question:
{!customerQuestion}

Instructions:
1. Answer based ONLY on the provided context
2. If the context doesn't contain the answer, say "I don't have that information"
3. Be concise but complete
4. Use a friendly, professional tone
5. Include relevant article references when applicable

Response:
    </promptContent>

    <promptTemplateVariables>
        <developerName>knowledgeContext</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>customerQuestion</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>true</isRequired>
    </promptTemplateVariables>
</PromptTemplate>
```

**File Location:**
```
force-app/main/default/promptTemplates/Knowledge_Assistant.promptTemplate-meta.xml
```

---

### Example 2: Record Summary

**Use Case:** Generate executive summary for Opportunity records.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Opportunity_Executive_Summary</fullName>
    <masterLabel>Opportunity Executive Summary</masterLabel>
    <description>Generates executive briefing for opportunity reviews</description>

    <type>recordSummary</type>
    <isActive>true</isActive>
    <objectType>Opportunity</objectType>

    <promptContent>
Generate an executive summary for the following sales opportunity:

OPPORTUNITY DETAILS
═══════════════════════════════════════════════════════════════════
Name: {!opportunityName}
Account: {!accountName}
Amount: ${!amount}
Stage: {!stageName}
Close Date: {!closeDate}
Probability: {!probability}%
Owner: {!ownerName}

Description:
{!description}

Next Steps:
{!nextStep}

Competitor Information:
{!competitorInfo}
═══════════════════════════════════════════════════════════════════

Create an executive summary (150 words max) that includes:

1. **Deal Overview**: One sentence on what we're selling and to whom
2. **Current Status**: Where we are in the sales cycle
3. **Key Risks**: Top 2-3 risks to closing
4. **Recommended Actions**: Priority actions for the sales team
5. **Win Probability Assessment**: Your assessment of likelihood to close

Format the output with clear section headers.
    </promptContent>

    <!-- Core opportunity fields -->
    <promptTemplateVariables>
        <developerName>opportunityName</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Opportunity</objectType>
        <fieldName>Name</fieldName>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>accountName</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Opportunity</objectType>
        <fieldName>Account.Name</fieldName>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>amount</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Opportunity</objectType>
        <fieldName>Amount</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>stageName</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Opportunity</objectType>
        <fieldName>StageName</fieldName>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>closeDate</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Opportunity</objectType>
        <fieldName>CloseDate</fieldName>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>probability</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Opportunity</objectType>
        <fieldName>Probability</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>ownerName</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Opportunity</objectType>
        <fieldName>Owner.Name</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>description</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Opportunity</objectType>
        <fieldName>Description</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>nextStep</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Opportunity</objectType>
        <fieldName>NextStep</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>competitorInfo</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>false</isRequired>
    </promptTemplateVariables>
</PromptTemplate>
```

---

### Example 3: Sales Generation (Email Draft)

**Use Case:** Generate follow-up email after a sales call.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Sales_Follow_Up_Email</fullName>
    <masterLabel>Sales Follow-Up Email Generator</masterLabel>
    <description>Generates personalized follow-up emails after sales meetings</description>

    <type>salesGeneration</type>
    <isActive>true</isActive>
    <objectType>Contact</objectType>

    <promptContent>
Generate a professional follow-up email after a sales meeting.

RECIPIENT INFORMATION
─────────────────────────────────────────────────────────────────
Contact Name: {!contactName}
Title: {!contactTitle}
Company: {!accountName}
Industry: {!accountIndustry}

MEETING CONTEXT
─────────────────────────────────────────────────────────────────
Meeting Date: {!meetingDate}
Discussion Topics: {!discussionTopics}
Key Pain Points: {!painPoints}
Next Steps Agreed: {!nextSteps}

SENDER INFORMATION
─────────────────────────────────────────────────────────────────
Sender Name: {!senderName}
Sender Title: {!senderTitle}

TONE PREFERENCE
─────────────────────────────────────────────────────────────────
{!tonePreference}

Generate a follow-up email that:
1. Thanks them for their time
2. Summarizes key discussion points (2-3 bullets)
3. Reiterates agreed next steps
4. Proposes a specific follow-up action
5. Ends with a professional sign-off

Keep the email under 200 words. Match the specified tone.
    </promptContent>

    <!-- Contact fields -->
    <promptTemplateVariables>
        <developerName>contactName</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Contact</objectType>
        <fieldName>Name</fieldName>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>contactTitle</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Contact</objectType>
        <fieldName>Title</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>accountName</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Contact</objectType>
        <fieldName>Account.Name</fieldName>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>accountIndustry</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Contact</objectType>
        <fieldName>Account.Industry</fieldName>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <!-- Runtime inputs -->
    <promptTemplateVariables>
        <developerName>meetingDate</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>discussionTopics</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>painPoints</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>nextSteps</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>senderName</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>senderTitle</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>tonePreference</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>false</isRequired>
    </promptTemplateVariables>
</PromptTemplate>
```

---

### Example 4: Field Completion

**Use Case:** Suggest case resolution notes based on case history.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Case_Resolution_Suggestion</fullName>
    <masterLabel>Case Resolution Suggestion</masterLabel>
    <description>Suggests resolution notes for cases based on history</description>

    <type>fieldCompletion</type>
    <isActive>true</isActive>
    <objectType>Case</objectType>

    <promptContent>
Based on the following case information, suggest appropriate resolution notes:

CASE INFORMATION
═══════════════════════════════════════════════════════════════════
Case Number: {!caseNumber}
Subject: {!subject}
Type: {!caseType}
Priority: {!priority}

Original Description:
{!description}

Comments/Activities:
{!caseComments}

Resolution Category: {!resolutionCategory}
═══════════════════════════════════════════════════════════════════

Generate resolution notes that:
1. Summarize the issue (1 sentence)
2. Describe the resolution steps taken (2-3 bullets)
3. Note any follow-up actions or recommendations
4. Include relevant KB article references if applicable

Keep the resolution notes under 150 words.
Maintain a professional, factual tone.
    </promptContent>

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
        <developerName>caseType</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Case</objectType>
        <fieldName>Type</fieldName>
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
        <developerName>description</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Case</objectType>
        <fieldName>Description</fieldName>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>caseComments</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>false</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>resolutionCategory</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>false</isRequired>
    </promptTemplateVariables>
</PromptTemplate>
```

---

## Using Prompt Templates

### In Agentforce (via GenAiFunction)

```xml
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Generate Opportunity Summary</masterLabel>
    <developerName>Generate_Opp_Summary</developerName>
    <description>Generates executive summary for an opportunity</description>

    <invocationTarget>Opportunity_Executive_Summary</invocationTarget>
    <invocationTargetType>prompt</invocationTargetType>

    <capability>
        Generate executive summaries for sales opportunities.
    </capability>

    <genAiFunctionInputs>
        <developerName>recordId</developerName>
        <description>Opportunity record ID</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>
</GenAiFunction>
```

### In Agent Script (Direct Invocation)

**NEW - December 2025**: You can invoke PromptTemplates directly from Agent Script without creating a separate GenAiFunction wrapper.

```agentscript
topic content_generation:
    description: "Generates personalized content using AI"

    actions:
        # Prompt Template Action - direct invocation
        Generate_Personalized_Schedule:
            description: "Generate a personalized schedule with a prompt template."
            inputs:
                # CRITICAL: Input names MUST use "Input:" prefix
                "Input:email": string
                    description: "User's email address to look up preferences"
                    is_required: True
                "Input:timezone": string
                    description: "User's timezone for schedule formatting"
                    is_required: False
            outputs:
                # Standard output field name for prompt responses
                promptResponse: string
                    description: "The AI-generated schedule content"
                    is_used_by_planner: True
                    is_displayable: True
            # Target uses generatePromptResponse:// protocol
            target: "generatePromptResponse://Generate_Personalized_Schedule"

    reasoning:
        instructions: ->
            | Help the user create a personalized schedule.
            | Ask for their email and timezone preference.
        actions:
            create_schedule: @actions.Generate_Personalized_Schedule
                with "Input:email"=...
                with "Input:timezone"=...
                set @variables.generated_content = @outputs.promptResponse
```

**Key Syntax Points:**

| Element | Requirement | Example |
|---------|-------------|---------|
| Target protocol | `generatePromptResponse://` | `target: "generatePromptResponse://My_Template"` |
| Input naming | Must have `"Input:"` prefix | `"Input:customerName": string` |
| Output field | Use `promptResponse` | `promptResponse: string` |
| Template name | Must match PromptTemplate API name | Template file: `My_Template.promptTemplate-meta.xml` |

**Mapping Template Variables:**

The `"Input:variableName"` in Agent Script maps to `{!variableName}` in your PromptTemplate:

```
Agent Script Input          →  PromptTemplate Variable
────────────────────────────────────────────────────────
"Input:email"              →  {!email}
"Input:customerQuestion"   →  {!customerQuestion}
"Input:context"            →  {!context}
```

**Complete Example Workflow:**

1. **Create PromptTemplate** (`force-app/main/default/promptTemplates/Generate_Personalized_Schedule.promptTemplate-meta.xml`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Generate_Personalized_Schedule</fullName>
    <masterLabel>Generate Personalized Schedule</masterLabel>
    <description>Creates personalized schedules based on user preferences</description>
    <type>flexPrompt</type>
    <isActive>true</isActive>

    <promptContent>
Create a personalized daily schedule for the user.

User Email: {!email}
Timezone: {!timezone}

Generate a structured schedule that includes:
1. Morning routine
2. Work blocks with breaks
3. Lunch break
4. Afternoon focus time
5. Evening wind-down

Format as a clean, readable schedule.
    </promptContent>

    <promptTemplateVariables>
        <developerName>email</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>true</isRequired>
    </promptTemplateVariables>

    <promptTemplateVariables>
        <developerName>timezone</developerName>
        <promptTemplateVariableType>freeText</promptTemplateVariableType>
        <isRequired>false</isRequired>
    </promptTemplateVariables>
</PromptTemplate>
```

2. **Deploy the PromptTemplate first:**

```bash
sf project deploy start -m "PromptTemplate:Generate_Personalized_Schedule"
```

3. **Then publish the agent** that references it.

> ⚠️ **Deployment Order Matters**: The PromptTemplate must exist in the org before publishing an agent that references it via `generatePromptResponse://`.

### In Apex

```apex
public class PromptTemplateService {

    public static String generateSummary(Id recordId, String templateName) {
        // Build input map
        Map<String, String> inputMap = new Map<String, String>();
        inputMap.put('recordId', recordId);

        // Build prompt input
        ConnectApi.EinsteinPromptTemplateGenerationsInput input =
            new ConnectApi.EinsteinPromptTemplateGenerationsInput();
        input.isPreview = false;
        input.inputParams = inputMap;

        // Evaluate prompt
        ConnectApi.EinsteinPromptTemplateGenerationsRepresentation result =
            ConnectApi.EinsteinLlm.generateMessagesForPromptTemplate(
                templateName,
                input
            );

        // Return generated text
        return result.generations[0].text;
    }
}
```

### In Flow

1. Add "Prompt Template" action element
2. Select your PromptTemplate
3. Map input variables
4. Store output to a text variable

---

## Data Cloud Grounding

For enhanced context using Data Cloud:

```xml
<PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <!-- ... standard elements ... -->

    <dataCloudConfig>
        <dataCloudObjectName>Customer_Profile__dlm</dataCloudObjectName>
        <retrievalStrategy>semantic</retrievalStrategy>
    </dataCloudConfig>
</PromptTemplate>
```

### Retrieval Strategies

| Strategy | Description |
|----------|-------------|
| `semantic` | Vector-based semantic search |
| `keyword` | Traditional keyword matching |
| `hybrid` | Combination of semantic + keyword |

---

## Deployment

### package.xml Entry

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>PromptTemplate</name>
    </types>
    <version>65.0</version>
</Package>
```

### Deploy Command

```bash
# Deploy specific template
sf project deploy start -m "PromptTemplate:Knowledge_Assistant"

# Deploy all templates
sf project deploy start -m "PromptTemplate:*"
```

---

## Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROMPT TEMPLATE BEST PRACTICES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PROMPT DESIGN                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ✅ Be specific about output format                                         │
│  ✅ Include examples when helpful                                           │
│  ✅ Set clear constraints (word limits, tone)                               │
│  ✅ Use structured sections with headers                                    │
│  ❌ Don't be vague or overly general                                        │
│                                                                             │
│  VARIABLES                                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ✅ Use recordField for data from records                                   │
│  ✅ Use freeText for runtime context                                        │
│  ✅ Mark optional variables as isRequired=false                             │
│  ❌ Don't hardcode values that should be dynamic                            │
│                                                                             │
│  SECURITY                                                                   │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ✅ Consider field-level security                                           │
│  ✅ Respect sharing rules                                                   │
│  ✅ Don't expose sensitive data                                             │
│  ❌ Don't include PII in prompt instructions                                │
│                                                                             │
│  MAINTENANCE                                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ✅ Version your templates logically                                        │
│  ✅ Document template purpose                                               │
│  ✅ Test with various input combinations                                    │
│  ❌ Don't create one-off templates for each use case                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Variable not replaced | Typo in {!name} | Check variable developerName exactly matches |
| "Field not accessible" | FLS issue | Check profile/permission set |
| Empty output | Required field is null | Make variable optional or add fallback |
| Unexpected format | Model interpretation | Be more specific in instructions |

---

## Related Documentation

- [Actions Reference](actions-reference.md) - Action configuration and metadata
- [Agent Script Reference](agent-script-reference.md) - Complete syntax guide
- [Einstein Prompt Builder (Salesforce Help)](https://help.salesforce.com/s/articleView?id=sf.prompt_builder.htm)
