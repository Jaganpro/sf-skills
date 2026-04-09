# Agent API Reference

Complete endpoint reference for the Agentforce Agent API.

> Official docs: [Agent API Reference](https://developer.salesforce.com/docs/ai/agentforce/references/agent-api?meta=summary)
> Postman collection: [Agent API Postman](https://www.postman.com/salesforce-developers/salesforce-developers/collection/gwv9bjy/agent-api)

## Base URL

```
https://api.salesforce.com/einstein/ai-agent/v1
```

Your My Domain goes in the request body as `instanceConfig.endpoint`, **not** in the URL.

---

## Endpoints

### Start Session

```
POST /agents/{AGENT_ID}/sessions
Content-Type: application/json
Authorization: Bearer {ACCESS_TOKEN}
```

```json
{
  "externalSessionKey": "<random-uuid>",
  "instanceConfig": {
    "endpoint": "https://{MY_DOMAIN}"
  },
  "streamingCapabilities": {
    "chunkTypes": ["Text"]
  },
  "bypassUser": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `externalSessionKey` | string (UUID) | Client-generated key for tracing in event logs |
| `instanceConfig.endpoint` | string | Your My Domain URL (e.g. `https://myorg.my.salesforce.com`) |
| `streamingCapabilities.chunkTypes` | string[] | Chunk types for streaming. Use `["Text"]` |
| `bypassUser` | boolean | `true` = use agent-assigned user; `false` = use token user |

**Response** (HTTP 200):
```json
{
  "sessionId": "abc123...",
  "_links": {
    "messages": "/sessions/abc123.../messages",
    "stream": "/sessions/abc123.../messages/stream",
    "end": "/sessions/abc123..."
  }
}
```

### Send Synchronous Message

```
POST /sessions/{SESSION_ID}/messages
Content-Type: application/json
Authorization: Bearer {ACCESS_TOKEN}
```

```json
{
  "message": {
    "type": "Text",
    "text": "Hello, agent!",
    "sequenceId": 1
  }
}
```

**Critical**: `sequenceId` goes **inside** the `message` object. Increment for each message in the session.

**Response** (HTTP 200):
```json
{
  "messages": [
    {
      "type": "Inform",
      "message": "The response text is here",
      "id": "msg-id",
      "feedbackId": "feedback-id",
      "isContentSafe": true,
      "citedReferences": []
    }
  ]
}
```

Response text is in `messages[].message`, **not** `messages[].text`.

### Send Streaming Message

```
POST /sessions/{SESSION_ID}/messages/stream
Content-Type: application/json
Accept: text/event-stream
Authorization: Bearer {ACCESS_TOKEN}
```

Same body as synchronous. The `Accept: text/event-stream` header triggers SSE.

**SSE Event Types** (in order):

| Event | Description |
|-------|-------------|
| `ProgressIndicator` | Response is being generated |
| `TextChunk` | Incremental text fragment |
| `Inform` | Complete final message with `citedReferences` |
| `EndOfTurn` | Response is complete |
| `ValidationFailureChunk` | Trust layer validation failed — discard prior chunks, render only new content |

### End Session

```
DELETE /sessions/{SESSION_ID}
Authorization: Bearer {ACCESS_TOKEN}
```

Returns HTTP 200 on success.

### Submit Feedback

```
POST /sessions/{SESSION_ID}/feedback
Content-Type: application/json
Authorization: Bearer {ACCESS_TOKEN}
```

```json
{
  "feedbackId": "feedback-id-from-inform-message",
  "feedback": "GOOD"
}
```

`feedback` values: `"GOOD"` or `"BAD"`. Stored in Data 360.

Returns HTTP 201 on success.

---

## Agent Variables

Pass context and custom variables when starting a session or sending messages.

```json
{
  "message": {
    "type": "Text",
    "text": "Check my records",
    "sequenceId": 2
  },
  "variables": [
    {
      "name": "$Context.EndUserLanguage",
      "value": "en_US"
    },
    {
      "name": "team_descriptor",
      "value": "Sales West"
    },
    {
      "name": "troubleshootingSteps",
      "value": "Rebooted, cleared cache"
    }
  ]
}
```

### Variable Rules

| Rule | Detail |
|------|--------|
| Context variables (`$Context.*`) | Read-only after session start, except `$Context.EndUserLanguage` |
| Custom field variables | Omit `__c` suffix (e.g. `Conversation_Key__c` → `$Context.Conversation_Key`) |
| Editable variables | Can be modified during send message calls |
| Visibility | Must have `visibility: external` in metadata to be API-settable |
| Builder setting | "Allow value to be set by API" must be checked |

### Variable Metadata Fields

Configure via `ConversationVariable` (in BotVersion) or `ConversationContextVariable` (in Bot).

| Field | Description |
|-------|-------------|
| `dataType` | Text, Number, Boolean, Object, Date, DateTime, Currency, Id |
| `description` | Used by the Agentforce planner service |
| `developerName` | Unique name (letter start, no spaces, no trailing/consecutive underscores) |
| `includeInPrompt` | Whether included in LLM prompt. Don't change for Id/EndUserId/EndUserLanguage |
| `label` | Human-readable UI label |
| `visibility` | `internal` (action output only) or `external` (action output + API) |

---

## Cited References

Inform messages may include `citedReferences`:

```json
{
  "type": "Inform",
  "message": "According to our policy...",
  "citedReferences": [
    {
      "title": "Policy Document",
      "url": "https://...",
      "inlineMetadata": {
        "startIndex": 13,
        "endIndex": 23
      }
    }
  ]
}
```

Citations can be end-of-message sources or inline (tied to specific text ranges via `inlineMetadata`).

---

## Getting the Agent ID

The method depends on which builder created the agent:

> Official docs: [Get the Agent ID for an Agent](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-api-agent-id.html)

### What to look up

- **Agent API name**: usually the agent's **DeveloperName**
- **Agent ID**: the 18-character `Id` value used in the API URL

### Legacy Agentforce Builder
1. Setup → Agentforce Agents → select agent
2. Copy the 18-character ID from the URL
3. Example: `https://mydomain.salesforce-setup.com/.../0XxSB000000IPCr0AO/edit` → `0XxSB000000IPCr0AO`
4. The URL ending is the **agent ID**

### New Agentforce Builder
Query the `BotDefinition` standard object using the agent's **DeveloperName**:

```sql
SELECT Id FROM BotDefinition WHERE DeveloperName = 'Your_Agent_Name'
```

The `DeveloperName` is the API name, and the `Id` field in the query result is the agent ID.

---

## Constraints

- **Not supported** for agents of type "Agentforce (Default)"
- **120-second timeout** per API call — HTTP 500 on timeout
- Impacts credit consumption per [Generative AI Usage and Billing](https://help.salesforce.com/s/articleView?id=ai.generative_ai_usage_billing.htm)
- Use My Domain URL (`myorg.my.salesforce.com`), **not** Lightning URL (`myorg.lightning.force.com`)
