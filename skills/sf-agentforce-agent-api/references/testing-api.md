# Agentforce Testing API & Agent Testing

Programmatic test automation for Agentforce agents.

> Official docs: [Testing API Developer Guide](https://developer.salesforce.com/docs/ai/agentforce/guide/testing-api.html)

## Testing Methods

| Method | Access | Format | Custom Evaluations | Best For |
|--------|--------|--------|--------------------|----------|
| [Testing Center](https://help.salesforce.com/s/articleView?id=ai.agent_testing_center.htm) | UI | CSV | No | Non-developers, quick manual tests |
| [Agentforce DX](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx-test.html) | CLI | YAML | Yes | Pro-code dev workflows |
| [Testing API](https://developer.salesforce.com/docs/ai/agentforce/guide/testing-api-build-tests.html) | Code | XML | Yes | CI/CD pipelines, automation |

---

## Prerequisites & Limits

- Agentforce enabled with at least one active agent
- **Sandbox only** — agent testing is not available in production
- Running tests consumes Einstein Requests credits (and possibly Data 360 credits)
- Running tests can modify data in your org
- Max **10 concurrent** `IN-PROGRESS` runs
- Max **1,000 test cases** per `AiEvaluationDefinition`
- Test results may change over time due to testing service improvements

---

## Workflow: Create → Deploy → Run → Analyze

### 1. Create Tests

**Metadata API (XML)** — define `AiEvaluationDefinition`:
- [Build Tests in Metadata API](https://developer.salesforce.com/docs/ai/agentforce/guide/testing-api-build-tests.html)

**Agentforce DX (YAML)** — generate test specs:
- [Generate a Test Spec](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx-test-spec.html)

### 2. Deploy Tests

```bash
# Metadata API via CLI
sf project deploy start -m AiEvaluationDefinition:YourTestName

# Or via VS Code Command Palette
SFDX: Deploy This Source to Org
```

Agentforce DX: [Create an Agent Test](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx-test-create.html)

### 3. Run Tests

**Agentforce DX:**
```bash
sf agent test run --agent-api-name Your_Agent_Name --target-org your-sandbox
```

**Connect API:**
```bash
# Start test
sf api request rest /services/data/v63.0/einstein/ai-evaluations/runs \
  --method POST --body '{"aiEvaluationDefinitionName":"YourTestName"}'

# Poll status (replace {runId})
sf api request rest /services/data/v63.0/einstein/ai-evaluations/runs/{runId}

# Get results
sf api request rest /services/data/v63.0/einstein/ai-evaluations/runs/{runId}/results
```

### 4. Analyze Results

See [Use Test Results to Improve Your Agent](https://developer.salesforce.com/docs/ai/agentforce/guide/testing-api-use-results.html).

---

## Building Tests with Metadata API

The `AiEvaluationDefinition` metadata type contains test cases. Each test case has inputs (utterance + optional context) and expectations.

### Test Case Inputs

| Input Type | Description |
|------------|-------------|
| Utterance | The primary user message to send to the agent |
| Context variables | `$Context.*` variables for scenario simulation. Immutable after session start except `EndUserLanguage` |
| Conversation history | Prior messages for multi-turn testing (role, text, topic, index) |

### Conversation History (Multi-Turn)

Add `conversationHistory` to inputs for multi-turn context:

```xml
<inputs>
  <utterance>What about the second item?</utterance>
  <conversationHistory>
    <role>user</role>
    <messageText>Show me my open cases</messageText>
    <messageIndex>0</messageIndex>
  </conversationHistory>
  <conversationHistory>
    <role>agent</role>
    <messageText>Here are your 3 open cases...</messageText>
    <topicName>CaseManagement</topicName>
    <messageIndex>1</messageIndex>
  </conversationHistory>
</inputs>
```

### Sample Test Definition (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiEvaluationDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
  <name>MyAgentTests</name>
  <subjectName>Your_Agent_Name</subjectName>
  <subjectType>AGENT</subjectType>
  <testCases>
    <testCase>
      <number>1</number>
      <inputs>
        <utterance>Summarize the Global Media account</utterance>
      </inputs>
      <expectations>
        <expectation>
          <name>topic_sequence_match</name>
          <expectedValue>OOTBSingleRecordSummary</expectedValue>
        </expectation>
        <expectation>
          <name>action_sequence_match</name>
          <expectedValue>IdentifyRecordByName</expectedValue>
        </expectation>
        <expectation>
          <name>bot_response_rating</name>
          <expectedValue>Contains account summary</expectedValue>
        </expectation>
        <expectation>
          <name>conciseness</name>
        </expectation>
      </expectations>
    </testCase>
  </testCases>
</AiEvaluationDefinition>
```

---

## Expectation Types (Standard)

| Expectation Name | What It Tests | `expectedValue` Required | `metricScore` |
|-----------------|---------------|--------------------------|---------------|
| `topic_sequence_match` | Agent used the expected topic | Yes — topic name | PASS / FAILED |
| `action_sequence_match` | Agent used the expected action(s) | Yes — action name | PASS / FAILED |
| `bot_response_rating` | Semantic comparison of response vs expected (meaning, not exact text) | Yes — expected response text | PASS / FAILED |
| `coherence` | Response is understandable, no grammar errors | No | PASS / FAILED |
| `completeness` | Response includes all essential information | No | PASS / FAILED |
| `conciseness` | Response is brief but comprehensive | No | PASS / FAILED |
| `output_latency_milliseconds` | Latency from request to response (ms) | No | Numeric value |
| `instruction_adherence` | How well response follows topic instructions | No | HIGH / LOW / UNCERTAIN |

### Reading Failed Results

- **Topic fail**: Compare `expectedValue` (in test def) vs actual topic the agent routed to
- **Action fail**: Compare `expectedValue` vs actual action sequence
- **Response fail**: Check if the meaning diverged significantly
- **Instruction adherence**: `generatedData` = raw LLM response; `actualValue` = final agent response

Use the Agent Builder conversation preview to test utterances interactively and fine-tune instructions, actions, or topics.

---

## Custom Evaluation Criteria

> [Custom Evaluation Criteria docs](https://developer.salesforce.com/docs/ai/agentforce/guide/testing-api-custom-evaluation-criteria.html)

Available in Testing API and Agentforce DX only (not Testing Center). Test for specific strings or numbers in agent responses.

### Custom Evaluation Types

| Type | API Name | Use Case |
|------|----------|----------|
| String comparison | `string_comparison` | Check for specific text in responses |
| Numeric comparison | `numeric_comparison` | Check latency, counts, numeric outputs |

### String Comparison Operators

| Operator | Behavior | Case Sensitive |
|----------|----------|----------------|
| `equals` | Exact match | Yes |
| `contains` | Substring check | Yes |
| `startswith` | Prefix check | Yes |
| `endswith` | Suffix check | Yes |

### Numeric Comparison Operators

| Operator | Behavior |
|----------|----------|
| `equals` | `actual == expected` |
| `greater_than` | `actual > expected` |
| `greater_than_or_equal` | `actual >= expected` |
| `less_than` | `actual < expected` |
| `less_than_or_equal` | `actual <= expected` |

### Custom Evaluation XML Structure

Each parameter has `name`, `value`, and `isReference` fields:

```xml
<expectation>
  <name>string_comparison</name>
  <expectedValues>
    <parameter>
      <name>actual</name>
      <value>$.actions[?(@.action=='namespace_actionName')].inputs.query</value>
      <isReference>true</isReference>
    </parameter>
    <parameter>
      <name>expected</name>
      <value>John Smith</value>
      <isReference>false</isReference>
    </parameter>
    <parameter>
      <name>operator</name>
      <value>contains</value>
      <isReference>false</isReference>
    </parameter>
  </expectedValues>
</expectation>
```

### JSONPath for `actual` Values

The `actual` parameter uses JSONPath to reference data from `generatedData` in test results. `isReference` must be `true`.

Common patterns:

```
# Action input
$.actions[?(@.action=='namespace_actionName')].inputs.query

# Action output
$.actions[?(@.action=='namespace_actionName')].outputs.result

# Additional context value (first item)
$.actions[?(@.action=='namespace_actionName')].additionalContext[0].value
```

**Tip**: Use `sf agent test run --verbose` to see the generated JSON data and construct JSONPath expressions.

Each parameter `value` field is limited to **100 characters**.

---

## Connect API Endpoints

Auth setup is identical to Agent API — create an External Client App with Client Credentials flow. Required scopes: `chatter_api`, `api`, `web`, `refresh_token`/`offline_access`.

| Endpoint | Method | Path |
|----------|--------|------|
| Start Test | POST | `/services/data/v63.0/einstein/ai-evaluations/runs` |
| Get Test Status | GET | `/services/data/v63.0/einstein/ai-evaluations/runs/{runId}` |
| Get Test Results | GET | `/services/data/v63.0/einstein/ai-evaluations/runs/{runId}/results` |

### Start Test

```bash
curl -X POST "https://{INSTANCE}/services/data/v63.0/einstein/ai-evaluations/runs" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"aiEvaluationDefinitionName":"YourTestName"}'
```

Returns `runId` for polling.

### Get Status (Poll)

```bash
curl "https://{INSTANCE}/services/data/v63.0/einstein/ai-evaluations/runs/{runId}" \
  -H "Authorization: Bearer {TOKEN}"
```

Poll until status is no longer `IN-PROGRESS`.

### Get Results

```bash
curl "https://{INSTANCE}/services/data/v63.0/einstein/ai-evaluations/runs/{runId}/results" \
  -H "Authorization: Bearer {TOKEN}"
```

Results include `metricScore` per expectation and `errorMessage` for failures.

---

## Agentforce DX Testing Commands

```bash
# Generate a test spec (YAML)
sf agent test spec generate

# Create/deploy a test to org
sf agent test create

# Run tests
sf agent test run --agent-api-name Agent_Name --target-org sandbox-alias

# Run with verbose output (shows generatedData JSON)
sf agent test run --verbose

# Preview agent interactively (manual testing)
sf agent preview
```

See [Test an Agent with Agentforce DX](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx-test.html) for full CLI reference.

---

## Related Metadata Types

- [AiEvaluationDefinition](https://developer.salesforce.com/docs/ai/agentforce/references/testing-api-metadata)
- [Bot](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_bot.htm)
- [BotVersion](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_botversion.htm)
- [BotTemplate](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_bottemplate.htm)
- [Agentforce Metadata Types](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-metadata.html)
