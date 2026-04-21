---
name: sf-agentforce-agent-api
description: >
  Agentforce API integration for the REST Agent API, Mobile SDKs, Enhanced Chat
  v2, and Testing API workflows. TRIGGER when the user needs Agent API
  authentication, session lifecycle guidance, agent ID lookup, variable
  handling, token caching, mobile/web chat setup, testing, or troubleshooting.
license: MIT
compatibility: "Requires Agentforce enabled orgs and Salesforce API access"
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
---

# sf-agentforce-agent-api: Agentforce API Integration

Use this skill when integrating Salesforce Agentforce agents into external apps. It covers the Agent API, authentication, Mobile SDKs, Enhanced Chat v2, Testing API, and common pitfalls.

## Quick Start — Minimum Viable Call

Three steps to talk to an agent:

### 1. Get a Token

```
POST https://{MY_DOMAIN}/services/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id={KEY}&client_secret={SECRET}
```

Requires an External Client App with Client Credentials flow. Full setup in [references/auth-setup.md](references/auth-setup.md).

### 2. Start a Session

```
POST https://api.salesforce.com/einstein/ai-agent/v1/agents/{AGENT_ID}/sessions
Authorization: Bearer {TOKEN}
Content-Type: application/json
```

```json
{
  "externalSessionKey": "<uuid>",
  "instanceConfig": { "endpoint": "https://{MY_DOMAIN}" },
  "streamingCapabilities": { "chunkTypes": ["Text"] },
  "bypassUser": true
}
```

### 3. Send a Message

```
POST https://api.salesforce.com/einstein/ai-agent/v1/sessions/{SESSION_ID}/messages
Authorization: Bearer {TOKEN}
Content-Type: application/json
```

```json
{
  "message": { "type": "Text", "text": "Hello!", "sequenceId": 1 }
}
```

Response text is in `messages[].message` (not `.text`). Increment `sequenceId` per turn.

---

## Critical Rules

1. **API host**: Always `api.salesforce.com/einstein/ai-agent/v1` — My Domain goes in the body only
2. **sequenceId**: Must be **inside** the `message` object, not at the root
3. **Response field**: Text lives in `messages[].message`, not `messages[].text`
4. **Run As user**: Must have a full Salesforce license — never use Einstein Agent service users
5. **Token caching**: Mandatory. Salesforce enforces 3,600 logins/user/hour
6. **Env var trimming**: Always `.trim()` — hosting platforms can add trailing `\n`
7. **Agent type**: Agent API is **not supported** for "Agentforce (Default)" agents
8. **Timeout**: 120-second timeout per call; HTTP 500 on timeout

## Session Lifecycle

```
Start Session → Send Messages (sync or stream) → End Session
                     ↓
              Submit Feedback (optional)
```

- **Synchronous**: Full response in one HTTP response
- **Streaming**: SSE events — `ProgressIndicator` → `TextChunk` → `Inform` → `EndOfTurn`
- **End session**: `DELETE /sessions/{SESSION_ID}`
- **Feedback**: `POST /sessions/{SESSION_ID}/feedback` with `feedbackId` from Inform message

Full endpoint reference in [references/api-reference.md](references/api-reference.md).

## Agent Variables

Pass context and custom variables on session start or with messages:

```json
{
  "variables": [
    { "name": "$Context.EndUserLanguage", "value": "en_US" },
    { "name": "team_descriptor", "value": "Sales West" }
  ]
}
```

Key rules:
- Context variables (`$Context.*`) are read-only after session start (except `EndUserLanguage`)
- Custom field variables: omit `__c` suffix (`Conversation_Key__c` → `$Context.Conversation_Key`)
- Must check "Allow value to be set by API" in Builder; `visibility: external` in metadata

Full variable reference in [references/api-reference.md](references/api-reference.md#agent-variables).

## Token Caching (Next.js)

HMR resets module-scoped variables. Use `globalThis` to survive reloads:

```typescript
const g = globalThis as typeof globalThis & {
  __sfToken?: { token: string; expiresAt: number };
};
if (!g.__sfToken) g.__sfToken = { token: '', expiresAt: 0 };
```

- Never retry on rate limit
- Dedup concurrent requests with a shared Promise
- Expire tokens 60 seconds early

Full caching patterns in [references/auth-setup.md](references/auth-setup.md#token-caching).

## React Strict Mode

React 18 dev mode double-mounts. Use `AbortController`, not `useRef` guards:

```typescript
useEffect(() => {
  const controller = new AbortController();
  fetch('/api/session', { method: 'POST', signal: controller.signal })
    .then(r => r.json())
    .then(data => setSessionId(data.sessionId))
    .catch(err => {
      if (err.name === 'AbortError') return;
    });
  return () => controller.abort();
}, []);
```

## Quick Error Reference

| Error | Fix |
|-------|-----|
| `Maximum Logins Exceeded` | Change Run As to admin/Integration User |
| `login rate exceeded` | Wait 15–30 min; implement globalThis caching |
| 404 `URL No Longer Exists` | Use `api.salesforce.com`, not My Domain |
| `Missing required creator property 'sequenceId'` | Move sequenceId inside `message` object |
| `Bad force-config endpoint` | `.trim()` all env vars |
| No text in response | Use `msg.message`, not `msg.text` |
| Session stuck "Connecting..." | Use AbortController pattern (Strict Mode) |
| `EngineConfigLookupException` | Use My Domain URL, not Lightning URL |

Full diagnostic checklist in [references/troubleshooting.md](references/troubleshooting.md).

## Getting the Agent ID

**Legacy Builder**: 18-char ID from URL in Setup → Agentforce Agents.

**New Builder**: Query `SELECT Id FROM BotDefinition WHERE DeveloperName = 'Agent_Name'`.

See [references/api-reference.md](references/api-reference.md#getting-the-agent-id) for the full lookup flow and the official Salesforce doc link.

## Deep References

| Topic | File |
|-------|------|
| Full API endpoints, payloads, variables, citations | [api-reference.md](references/api-reference.md) |
| OAuth setup, ECA creation, token caching patterns | [auth-setup.md](references/auth-setup.md) |
| Error codes, diagnostics, common integration bugs | [troubleshooting.md](references/troubleshooting.md) |
| iOS, Android, React Native Mobile SDKs | [mobile-sdk.md](references/mobile-sdk.md) |
| Testing API, Agentforce DX testing, CI/CD | [testing-api.md](references/testing-api.md) |
| All Agentforce tools, SDKs, and builder comparison | [ecosystem.md](references/ecosystem.md) |
