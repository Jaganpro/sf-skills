# Troubleshooting & Error Reference

> Official docs: [Agent API Troubleshooting](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-api-troubleshooting.html)

## HTTP Error Codes

### HTTP 400 — Bad Request

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `{VALUE} is not a valid agent ID` | Wrong agent ID in URL | Verify agent ID — see [api-reference.md](api-reference.md) "Getting the Agent ID" |
| `Missing required creator property 'sequenceId'` | `sequenceId` placed at message root | Move `sequenceId` **inside** the `message` object |

### HTTP 401 — Unauthorized

| Symptom | Cause | Fix |
|---------|-------|-----|
| `invalid_grant` | Service user as Run As, or bad credentials | Use admin/Integration User. Verify consumer key/secret |
| `Maximum Logins Exceeded` | Einstein Agent service user | Change Run As to a full-license user |
| `login rate exceeded` | Too many OAuth requests | Wait 15–30 min. Implement `globalThis` caching — see [auth-setup.md](auth-setup.md) |
| Token expired | Token not refreshed | Implement token caching with early expiry |

### HTTP 404 — Not Found

| Symptom | Cause | Fix |
|---------|-------|-----|
| `URL No Longer Exists` | My Domain used as API host | Use `api.salesforce.com/einstein/ai-agent/v1` as base URL |
| Resource not found | Wrong session ID | Verify `sessionId` from start session response |

### HTTP 500 — Server Error

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Unsupported Media Type` | Wrong Content-Type header | Use `Content-Type: application/json` |
| `EngineConfigLookupException` | Wrong domain in endpoint | Use **My Domain** URL (`myorg.my.salesforce.com`), not Lightning URL |
| `HttpServerErrorException` | Wrong agent ID | Verify agent ID per the correct builder method |
| Timeout (120s) | Agent response took too long | Simplify agent logic; consider streaming endpoint |

---

## Common Integration Issues

### No Text in Response

**Symptom**: Parsing `msg.text` returns undefined.
**Fix**: Response text is in `messages[].message`, not `messages[].text`.

### Session Stuck on "Connecting..."

**Symptom**: React app never shows agent response.
**Cause**: `useRef` guard with React 18 Strict Mode double-mount.
**Fix**: Use `AbortController` pattern:

```typescript
useEffect(() => {
  const controller = new AbortController();
  async function init() {
    const res = await fetch('/api/session', {
      method: 'POST',
      signal: controller.signal,
    });
    const data = await res.json();
    setSessionId(data.sessionId);
  }
  init().catch(err => {
    if (err instanceof DOMException && err.name === 'AbortError') return;
  });
  return () => controller.abort();
}, []);
```

### `Bad force-config endpoint`

**Cause**: Trailing `\n` in environment variable (common on Vercel, Heroku, etc.).
**Fix**: `.trim()` all env vars before use.

### Streaming ValidationFailureChunk

**Symptom**: Streaming response contains `ValidationFailureChunk` event.
**Cause**: Agentforce trust layer rejected the response.
**Fix**: Discard all previously rendered chunks. Display only new streamed content after the validation event.

### Domain Confusion

| URL Type | Example | Use For |
|----------|---------|---------|
| My Domain | `myorg.my.salesforce.com` | Token requests + `instanceConfig.endpoint` |
| Lightning | `myorg.lightning.force.com` | **Never** — not valid for API |
| Agent API | `api.salesforce.com` | All Agent API calls |

---

## Diagnostic Checklist

When debugging Agent API integration:

1. **Auth**: Is the token valid and not expired? Is the Run As user correct?
2. **Endpoint**: Using `api.salesforce.com` for Agent API, My Domain for OAuth?
3. **Agent ID**: Correct ID from the right builder? 18-character format?
4. **Headers**: `Content-Type: application/json`? `Accept: text/event-stream` for streaming?
5. **Body**: `sequenceId` inside `message` object? `instanceConfig.endpoint` set?
6. **Env vars**: All trimmed? Domain normalized with `https://`?
7. **Rate limits**: Token being cached? Not retrying on `login rate exceeded`?
