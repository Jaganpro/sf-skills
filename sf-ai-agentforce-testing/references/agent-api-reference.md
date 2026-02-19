<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # Agent Runtime API Reference
   2 
   3 Reference for Salesforce Einstein Agent Runtime API v1 — the REST API used for multi-turn agent testing.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 The Agent Runtime API provides programmatic access to Agentforce agents via REST endpoints. Unlike the CLI-based Agent Testing Center (single-utterance tests), this API supports **multi-turn conversations** with full session lifecycle management.
  10 
  11 > ⚠️ **Agent API is NOT supported for agents of type "Agentforce (Default)".** Only custom agents created via Agentforce Builder are supported.
  12 
  13 | Feature | Agent Testing Center (CLI) | Agent Runtime API |
  14 |---------|---------------------------|-------------------|
  15 | Multi-turn conversations | ❌ No | ✅ Yes |
  16 | Session state management | ❌ No | ✅ Yes |
  17 | Context preservation testing | ❌ No | ✅ Yes |
  18 | Topic re-matching validation | ❌ No | ✅ Yes |
  19 | Requires AiEvaluationDefinition | ✅ Yes | ❌ No |
  20 | Requires Agent Testing Center feature | ✅ Yes | ❌ No |
  21 | Auth mechanism | sf CLI org auth | Client Credentials ECA |
  22 
  23 ---
  24 
  25 ## Base URL
  26 
  27 ```
  28 https://api.salesforce.com/einstein/ai-agent/v1
  29 ```
  30 
  31 > **Note:** This is the global Salesforce API endpoint, NOT your My Domain URL. The My Domain is passed as `instanceConfig.endpoint` within the session creation payload.
  32 
  33 ---
  34 
  35 ## Authentication
  36 
  37 The Agent Runtime API requires an **OAuth 2.0 access token** obtained via **Client Credentials flow** from an External Client App (ECA).
  38 
  39 > **NEVER use `curl` for OAuth token validation.** Domains containing `--` (e.g., `my-org--devint.sandbox.my.salesforce.com`) cause shell expansion failures. The `agent_api_client.py` handles OAuth internally.
  40 
  41 ```bash
  42 # Verify credentials work (credential_manager.py handles OAuth internally)
  43 python3 ~/.claude/skills/sf-ai-agentforce-testing/hooks/scripts/credential_manager.py \
  44   validate --org-alias {org} --eca-name {eca}
  45 
  46 # The agent_api_client.py and multi_turn_test_runner.py handle token acquisition
  47 # automatically — you never need to manually obtain tokens.
  48 ```
  49 
  50 **Required:** An External Client App configured with Client Credentials flow. See [ECA Setup Guide](eca-setup-guide.md).
  51 
  52 ---
  53 
  54 ## Endpoints
  55 
  56 ### 1. Create Session
  57 
  58 Start a new agent conversation session.
  59 
  60 **Request:**
  61 ```
  62 POST /einstein/ai-agent/v1/agents/{agentId}/sessions
  63 ```
  64 
  65 **Headers:**
  66 ```
  67 Authorization: Bearer {access_token}
  68 Content-Type: application/json
  69 ```
  70 
  71 **Body:**
  72 ```json
  73 {
  74   "externalSessionKey": "unique-uuid-per-session",
  75   "instanceConfig": {
  76     "endpoint": "https://your-domain.my.salesforce.com"
  77   },
  78   "streamingCapabilities": {
  79     "chunkTypes": ["Text"]
  80   },
  81   "bypassUser": true
  82 }
  83 ```
  84 
  85 **Parameters:**
  86 
  87 | Field | Type | Required | Description |
  88 |-------|------|----------|-------------|
  89 | `externalSessionKey` | string | ✅ | Unique identifier for this session (UUID recommended) |
  90 | `instanceConfig.endpoint` | string | ✅ | Your Salesforce My Domain URL (https://...) |
  91 | `streamingCapabilities.chunkTypes` | array | ✅ | Response chunk types to receive (`["Text"]`) |
  92 | `bypassUser` | boolean | ❌ | If `true`, use the agent-assigned user. If `false`, use the token user. Set `true` for Client Credentials testing. |
  93 | `variables` | array | ❌ | Agent input variables. Each: `{"name": "$Context.X", "type": "Text", "value": "..."}` |
  94 
  95 **Response (200 OK):**
  96 ```json
  97 {
  98   "sessionId": "8e715939-a121-40ec-80e3-a8d1ac89da33",
  99   "_links": {
 100     "self": null,
 101     "messages": {
 102       "href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/8e715939.../messages/stream"
 103     },
 104     "session": {
 105       "href": "https://api.salesforce.com/einstein/ai-agent/v1/agents/0XxQZ.../sessions"
 106     },
 107     "end": {
 108       "href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/8e715939..."
 109     }
 110   },
 111   "messages": [
 112     {
 113       "type": "Inform",
 114       "id": "8e7cafae-0eb5-44b1-9195-21f1cd6e1f4b",
 115       "feedbackId": "",
 116       "planId": "",
 117       "isContentSafe": true,
 118       "message": "Hi, I'm an AI service assistant. How can I help you?",
 119       "result": [],
 120       "citedReferences": []
 121     }
 122   ]
 123 }
 124 ```
 125 
 126 > **Note:** The session start response includes an initial greeting message from the agent in the `messages` array.
 127 
 128 **Error Responses:**
 129 
 130 | Status | Meaning | Common Cause |
 131 |--------|---------|--------------|
 132 | 400 | Bad Request | Invalid agentId or malformed body |
 133 | 401 | Unauthorized | Invalid or expired token |
 134 | 403 | Forbidden | ECA scopes insufficient |
 135 | 404 | Not Found | Agent not found or not activated |
 136 | 429 | Rate Limited | Too many concurrent sessions |
 137 
 138 ---
 139 
 140 ### 2. Send Message
 141 
 142 Send a user message within an active session.
 143 
 144 **Request:**
 145 ```
 146 POST /einstein/ai-agent/v1/sessions/{sessionId}/messages
 147 ```
 148 
 149 **Headers:**
 150 ```
 151 Authorization: Bearer {access_token}
 152 Content-Type: application/json
 153 ```
 154 
 155 **Body:**
 156 ```json
 157 {
 158   "message": {
 159     "sequenceId": 1,
 160     "type": "Text",
 161     "text": "I need to cancel my appointment"
 162   }
 163 }
 164 ```
 165 
 166 **Parameters:**
 167 
 168 | Field | Type | Required | Description |
 169 |-------|------|----------|-------------|
 170 | `message.sequenceId` | integer | ✅ | Incrementing sequence number (1, 2, 3...) |
 171 | `message.type` | string | ✅ | Message type (always `"Text"`) |
 172 | `message.text` | string | ✅ | The user's message text |
 173 
 174 > **CRITICAL:** `sequenceId` MUST increment by 1 for each message in the session. Reusing or skipping IDs causes errors.
 175 
 176 **Response (200 OK):**
 177 ```json
 178 {
 179   "messages": [
 180     {
 181       "type": "Inform",
 182       "id": "ceb6b5de-6063-4e39-bc02-91e9bf7da867",
 183       "metrics": {},
 184       "feedbackId": "0bc8720e-e010-4129-87bb-70caaa885ee4",
 185       "planId": "0bc8720e-e010-4129-87bb-70caaa885ee4",
 186       "isContentSafe": true,
 187       "message": "I'd be happy to help you cancel your appointment...",
 188       "result": [],
 189       "citedReferences": []
 190     }
 191   ],
 192   "_links": {
 193     "self": null,
 194     "messages": { "href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/{sessionId}/messages" },
 195     "messagesStream": { "href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/{sessionId}/messages/stream" },
 196     "session": { "href": "https://api.salesforce.com/einstein/ai-agent/v1/agents/{agentId}/sessions" },
 197     "end": { "href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/{sessionId}" }
 198   }
 199 }
 200 ```
 201 
 202 **Response Message Fields:**
 203 
 204 | Field | Type | Description |
 205 |-------|------|-------------|
 206 | `type` | string | Message type (see types below) |
 207 | `id` | string | Unique message identifier |
 208 | `message` | string | The agent's text response |
 209 | `feedbackId` | string | ID for submitting feedback on this response |
 210 | `planId` | string | ID of the execution plan |
 211 | `isContentSafe` | boolean | Whether content passed safety checks |
 212 | `result` | array | Action result data (empty if no actions executed) |
 213 | `citedReferences` | array | Cited sources with optional inline metadata |
 214 
 215 **Response Message Types:**
 216 
 217 | Type | Description | When It Appears |
 218 |------|-------------|-----------------|
 219 | `Inform` | Informational response | Standard agent replies |
 220 | `Confirm` | Confirmation request | Before executing an action |
 221 | `Escalation` | Handoff to human | Escalation triggered |
 222 | `SessionEnded` | Session terminated | Agent or system ends conversation |
 223 | `ProgressIndicator` | Processing notification | Streaming: action in progress |
 224 | `TextChunk` | Incremental text | Streaming: partial response |
 225 | `EndOfTurn` | Turn complete | Streaming: response finished |
 226 
 227 ---
 228 
 229 ### 3. End Session
 230 
 231 Terminate an active session and release resources.
 232 
 233 **Request:**
 234 ```
 235 DELETE /einstein/ai-agent/v1/sessions/{sessionId}
 236 ```
 237 
 238 **Headers:**
 239 ```
 240 Authorization: Bearer {access_token}
 241 x-session-end-reason: UserRequest
 242 ```
 243 
 244 > **IMPORTANT:** The `x-session-end-reason` header is required. Use `UserRequest` for normal session termination.
 245 
 246 **Response (200 OK):**
 247 ```json
 248 {
 249   "messages": [
 250     {
 251       "type": "SessionEnded",
 252       "id": "c5692ca0-ee1b-414a-9d96-4e7862456500",
 253       "reason": "ClientRequest",
 254       "feedbackId": ""
 255     }
 256   ],
 257   "_links": { ... }
 258 }
 259 ```
 260 
 261 > **Best Practice:** Always end sessions after testing to avoid resource leaks and rate limit issues.
 262 
 263 ---
 264 
 265 ### 4. Send Agent Variables
 266 
 267 Variables can be passed at session start and (for editable variables) with messages.
 268 
 269 **Session Start with Variables:**
 270 ```json
 271 {
 272   "externalSessionKey": "{UUID}",
 273   "instanceConfig": { "endpoint": "https://{MY_DOMAIN_URL}" },
 274   "streamingCapabilities": { "chunkTypes": ["Text"] },
 275   "bypassUser": true,
 276   "variables": [
 277     { "name": "$Context.EndUserLanguage", "type": "Text", "value": "en_US" },
 278     { "name": "$Context.AccountId", "type": "Id", "value": "001XXXXXXXXXXXX" },
 279     { "name": "team_descriptor", "type": "Text", "value": "Premium Support" }
 280   ]
 281 }
 282 ```
 283 
 284 **Variable Types:**
 285 
 286 | Type | Description |
 287 |------|-------------|
 288 | `Text` | String value |
 289 | `Number` | Numeric value |
 290 | `Boolean` | true/false |
 291 | `Id` | Salesforce record ID |
 292 | `Date` | Date value |
 293 | `DateTime` | DateTime value |
 294 | `Currency` | Currency value |
 295 | `Object` | Complex object |
 296 
 297 **Important Notes:**
 298 - Context variables (`$Context.*`) are **read-only after session start** (except `$Context.EndUserLanguage`)
 299 - Custom variables derived from custom fields: omit the `__c` suffix (e.g., `Conversation_Key__c` → `$Context.Conversation_Key`)
 300 - Variables must have `Allow value to be set by API` checked in Agentforce Builder
 301 - Only editable variables can be modified in a `send message` call
 302 
 303 ---
 304 
 305 ### 5. Submit Feedback
 306 
 307 Submit feedback on an agent's response for Data 360 tracking.
 308 
 309 **Request:**
 310 ```
 311 POST /einstein/ai-agent/v1/sessions/{sessionId}/feedback
 312 ```
 313 
 314 **Body:**
 315 ```json
 316 {
 317   "feedbackId": "0bc8720e-e010-4129-87bb-70caaa885ee4",
 318   "feedback": "GOOD",
 319   "text": "Response was accurate and helpful"
 320 }
 321 ```
 322 
 323 Returns HTTP 201 on success.
 324 
 325 ---
 326 
 327 ## Agent ID Discovery
 328 
 329 Before calling the API, you need the agent's `BotDefinition` ID:
 330 
 331 ```bash
 332 # Query active agents in the org
 333 sf data query --use-tooling-api \
 334   --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition WHERE IsActive=true" \
 335   --result-format json --target-org [alias]
 336 ```
 337 
 338 The `Id` field from the query result is the `{agentId}` used in session creation.
 339 
 340 ---
 341 
 342 ## Complete Multi-Turn Example
 343 
 344 ```bash
 345 #!/bin/bash
 346 # Multi-turn agent conversation test
 347 
 348 SF_MY_DOMAIN="your-domain.my.salesforce.com"
 349 CONSUMER_KEY="your_key"
 350 CONSUMER_SECRET="your_secret"
 351 AGENT_ID="0XxRM0000004ABC"
 352 
 353 # 1. Get access token (use credential_manager.py to validate first)
 354 # python3 ~/.claude/skills/sf-ai-agentforce-testing/hooks/scripts/credential_manager.py \
 355 #   validate --org-alias {org} --eca-name {eca}
 356 # The agent_api_client.py handles token acquisition automatically.
 357 # For manual scripting, source credentials from ~/.sfagent/{org}/{eca}/credentials.env
 358 source ~/.sfagent/${ORG_ALIAS}/${ECA_NAME}/credentials.env
 359 SF_TOKEN=$(python3 -c "
 360 from hooks.scripts.agent_api_client import AgentAPIClient
 361 c = AgentAPIClient()
 362 print(c._get_token())
 363 ")
 364 
 365 # 2. Create session
 366 SESSION_ID=$(curl -s -X POST \
 367   "https://api.salesforce.com/einstein/ai-agent/v1/agents/${AGENT_ID}/sessions" \
 368   -H "Authorization: Bearer ${SF_TOKEN}" \
 369   -H "Content-Type: application/json" \
 370   -d '{
 371     "externalSessionKey":"'"$(uuidgen | tr A-Z a-z)"'",
 372     "instanceConfig":{"endpoint":"https://'"${SF_MY_DOMAIN}"'"},
 373     "streamingCapabilities":{"chunkTypes":["Text"]},
 374     "bypassUser":true
 375   }' | jq -r '.sessionId')
 376 
 377 echo "Session: ${SESSION_ID}"
 378 
 379 # 3. Turn 1: Initial request
 380 R1=$(curl -s -X POST \
 381   "https://api.salesforce.com/einstein/ai-agent/v1/sessions/${SESSION_ID}/messages" \
 382   -H "Authorization: Bearer ${SF_TOKEN}" \
 383   -H "Content-Type: application/json" \
 384   -d '{"message":{"sequenceId":1,"type":"Text","text":"I need to cancel my appointment"}}')
 385 echo "Turn 1 Response: $(echo $R1 | jq -r '.messages[0].message')"
 386 
 387 # 4. Turn 2: Follow-up
 388 R2=$(curl -s -X POST \
 389   "https://api.salesforce.com/einstein/ai-agent/v1/sessions/${SESSION_ID}/messages" \
 390   -H "Authorization: Bearer ${SF_TOKEN}" \
 391   -H "Content-Type: application/json" \
 392   -d '{"message":{"sequenceId":2,"type":"Text","text":"Actually, can I reschedule instead?"}}')
 393 echo "Turn 2 Response: $(echo $R2 | jq -r '.messages[0].message')"
 394 
 395 # 5. Turn 3: Context check
 396 R3=$(curl -s -X POST \
 397   "https://api.salesforce.com/einstein/ai-agent/v1/sessions/${SESSION_ID}/messages" \
 398   -H "Authorization: Bearer ${SF_TOKEN}" \
 399   -H "Content-Type: application/json" \
 400   -d '{"message":{"sequenceId":3,"type":"Text","text":"What was my original request about?"}}')
 401 echo "Turn 3 Response: $(echo $R3 | jq -r '.messages[0].message')"
 402 
 403 # 6. End session
 404 curl -s -X DELETE \
 405   "https://api.salesforce.com/einstein/ai-agent/v1/sessions/${SESSION_ID}" \
 406   -H "Authorization: Bearer ${SF_TOKEN}"
 407 echo "Session ended."
 408 ```
 409 
 410 ---
 411 
 412 ## Response Analysis
 413 
 414 When analyzing multi-turn responses, check these indicators:
 415 
 416 ### Per-Turn Checklist
 417 
 418 | Check | What to Look For | Pass Criteria |
 419 |-------|------------------|---------------|
 420 | **Non-empty** | Response has text content | `messages[0].message` is not empty |
 421 | **Topic match** | Response language matches expected topic | Infer from response content and actions |
 422 | **Action invoked** | Expected actions executed | `result.type` = `ActionResult` present |
 423 | **Context retained** | References to prior turns | Agent acknowledges prior conversation |
 424 | **Error-free** | No error indicators | No `Failure` or `Escalation` types (unless expected) |
 425 
 426 ### Error Indicators in Responses
 427 
 428 | Indicator | Meaning | Action |
 429 |-----------|---------|--------|
 430 | `"type": "Failure"` | Action execution failed | Check Flow/Apex |
 431 | `"type": "Escalation"` | Agent escalated to human | May be expected or failure |
 432 | Empty `messages` array | Agent produced no response | Check agent activation |
 433 | HTTP 500 on message send | Server-side error | Retry or check agent config |
 434 | `"result": null` | No plan executed | Topic may not have matched |
 435 
 436 ---
 437 
 438 ## Rate Limits & Best Practices
 439 
 440 ### Rate Limits
 441 
 442 | Resource | Limit | Notes |
 443 |----------|-------|-------|
 444 | Concurrent sessions per org | 10 | End sessions promptly |
 445 | Messages per session | 50 | Sufficient for testing |
 446 | Requests per minute | 100 | Per connected app |
 447 | Session timeout | 15 min | Inactive sessions auto-close |
 448 
 449 ### Best Practices
 450 
 451 1. **Always end sessions** — Call DELETE after each test scenario
 452 2. **Unique session keys** — Use `uuidgen` for `externalSessionKey`
 453 3. **Increment sequenceId** — Never reuse or skip sequence numbers
 454 4. **Check for empty responses** — Agent may not respond if not activated
 455 5. **Handle rate limits** — Add retry logic with backoff for 429 responses
 456 6. **Keep credentials in memory** — Never write ECA secrets to files
 457 
 458 ---
 459 
 460 ## Troubleshooting
 461 
 462 | Error | Cause | Fix |
 463 |-------|-------|-----|
 464 | 401 on token request | Wrong Consumer Key/Secret | Verify ECA credentials |
 465 | 401 on API call | Token expired | Re-authenticate |
 466 | 404 on session create | Wrong Agent ID | Re-query BotDefinition |
 467 | 400 "Invalid session" | Session already ended | Create new session |
 468 | 400 "Invalid sequenceId" | Wrong sequence number | Ensure incrementing from 1 |
 469 | Empty response | Agent not activated | Activate and publish agent |
 470 | "Rate limit exceeded" | Too many concurrent sessions | End unused sessions first |
 471 
 472 ---
 473 
 474 ## Related Documentation
 475 
 476 | Resource | Link |
 477 |----------|------|
 478 | ECA Setup | [eca-setup-guide.md](eca-setup-guide.md) |
 479 | Multi-Turn Testing Guide | [multi-turn-testing-guide.md](multi-turn-testing-guide.md) |
 480 | Test Patterns | [multi-turn-test-patterns.md](../references/multi-turn-test-patterns.md) |
