# OAuth 2.0 Flows Reference

Complete guide to OAuth flows supported by Salesforce Connected Apps and External Client Apps.

## Flow Decision Matrix

| Use Case | Recommended Flow | PKCE | Refresh Token | Secret Required |
|----------|-----------------|------|---------------|-----------------|
| Web Server (backend) | Authorization Code | Optional | Yes | Yes |
| Single Page App (SPA) | Authorization Code | **Required** | Yes (rotate) | No |
| Mobile Native App | Authorization Code | **Required** | Yes (rotate) | No |
| Server-to-Server | JWT Bearer | N/A | No | Certificate |
| CI/CD Pipeline | JWT Bearer | N/A | No | Certificate |
| IoT/Device | Device Authorization | N/A | Yes | No |
| CLI Tool | Device Authorization | N/A | Yes | No |
| Legacy (avoid) | Username-Password | N/A | Yes | Yes |

---

## Authorization Code Flow

**Best for**: Web applications, Mobile apps, SPAs

### Flow Diagram
```
┌──────────┐      ┌───────────────┐      ┌────────────────┐
│  User    │      │  Application  │      │   Salesforce   │
└────┬─────┘      └───────┬───────┘      └───────┬────────┘
     │                    │                      │
     │  1. Click Login    │                      │
     │───────────────────>│                      │
     │                    │                      │
     │                    │  2. Redirect to      │
     │                    │     /authorize       │
     │<───────────────────┼─────────────────────>│
     │                    │                      │
     │  3. Login & Consent│                      │
     │─────────────────────────────────────────>│
     │                    │                      │
     │                    │  4. Redirect with    │
     │<───────────────────┼──────code───────────│
     │                    │                      │
     │                    │  5. Exchange code    │
     │                    │     for tokens       │
     │                    │─────────────────────>│
     │                    │                      │
     │                    │  6. Access Token +   │
     │                    │     Refresh Token    │
     │                    │<─────────────────────│
     │                    │                      │
     │  7. Authenticated  │                      │
     │<───────────────────│                      │
```

### Authorization URL
```
https://login.salesforce.com/services/oauth2/authorize
  ?response_type=code
  &client_id=<CONSUMER_KEY>
  &redirect_uri=<CALLBACK_URL>
  &scope=api refresh_token
  &state=<CSRF_TOKEN>
  &code_challenge=<PKCE_CHALLENGE>        # For PKCE
  &code_challenge_method=S256              # For PKCE
```

### Token Exchange
```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=authorization_code" \
  -d "code=<AUTH_CODE>" \
  -d "client_id=<CONSUMER_KEY>" \
  -d "client_secret=<CONSUMER_SECRET>" \
  -d "redirect_uri=<CALLBACK_URL>" \
  -d "code_verifier=<PKCE_VERIFIER>"      # For PKCE
```

---

## JWT Bearer Flow

**Best for**: Server-to-server integrations, CI/CD, Headless automation

### Prerequisites
1. X.509 Certificate uploaded to Salesforce
2. Connected App with certificate configured
3. Pre-authorized user via Permission Set

### Flow Diagram
```
┌─────────────────┐                 ┌────────────────┐
│  Server/CI/CD   │                 │   Salesforce   │
└────────┬────────┘                 └───────┬────────┘
         │                                  │
         │  1. Create JWT with claims       │
         │     - iss: consumer_key          │
         │     - sub: username              │
         │     - aud: login.salesforce.com  │
         │     - exp: expiration            │
         │                                  │
         │  2. Sign JWT with private key    │
         │                                  │
         │  3. POST to /token               │
         │─────────────────────────────────>│
         │                                  │
         │  4. Validate signature with      │
         │     uploaded certificate         │
         │                                  │
         │  5. Access Token                 │
         │<─────────────────────────────────│
```

### JWT Structure
```json
// Header
{
  "alg": "RS256"
}

// Payload
{
  "iss": "<CONSUMER_KEY>",
  "sub": "user@company.com",
  "aud": "https://login.salesforce.com",
  "exp": 1234567890
}
```

### Token Request
```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
  -d "assertion=<SIGNED_JWT>"
```

---

## Client Credentials Flow

**Best for**: Service accounts, Background processes

### Configuration
- Enable `isClientCredentialsEnabled` in ECA OAuth Settings
- Assign execution user via Permission Set

### Token Request
```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=client_credentials" \
  -d "client_id=<CONSUMER_KEY>" \
  -d "client_secret=<CONSUMER_SECRET>"
```

### Agent Runtime API — Required Scopes

When creating an ECA for Agentforce Agent Runtime API testing (`/einstein/ai-agent/v1`), the following OAuth scopes are **required**:

| Scope | Purpose |
|-------|---------|
| `api` | Base REST API access |
| `chatbot_api` | Agent Runtime API conversation endpoints |
| `sfap_api` | Einstein platform services |

**ECA Configuration for Agent API Testing:**
```xml
<!-- In ecaOauth-meta.xml -->
<ExtlClntAppOauthSettings>
    <oauthScopes>Api</oauthScopes>
    <oauthScopes>ChatbotApi</oauthScopes>
    <oauthScopes>SfapApi</oauthScopes>
    <isClientCredentialsEnabled>true</isClientCredentialsEnabled>
    <!-- ... -->
</ExtlClntAppOauthSettings>
```

**Post-Deploy Steps:**
1. In Setup, navigate to the ECA → **Manage** → **Edit Policies**
2. Set **"Run As"** to an active Einstein Agent User
3. Verify the agent's `GenAiPlannerBundle` has `plannerSurfaces` with `EinsteinAgentApiChannel`
4. Verify the agent's `BotVersion` has `surfacesEnabled=true`

> See `/sf-ai-agentforce-testing` and `/sf-ai-agentscript` for full Agent Runtime API testing workflow.

---

## Device Authorization Flow

**Best for**: CLI tools, Smart TVs, IoT devices without browsers

### Flow Diagram
```
┌─────────────┐         ┌───────────────┐         ┌────────────────┐
│   Device    │         │     User      │         │   Salesforce   │
└──────┬──────┘         └───────┬───────┘         └───────┬────────┘
       │                        │                         │
       │  1. Request device code│                         │
       │─────────────────────────────────────────────────>│
       │                        │                         │
       │  2. device_code + user_code + verification_uri  │
       │<─────────────────────────────────────────────────│
       │                        │                         │
       │  3. Display code       │                         │
       │───────────────────────>│                         │
       │                        │                         │
       │                        │  4. Visit URL & enter   │
       │                        │     user_code           │
       │                        │────────────────────────>│
       │                        │                         │
       │  5. Poll for token     │                         │
       │─────────────────────────────────────────────────>│
       │                        │                         │
       │  6. Access Token (when authorized)               │
       │<─────────────────────────────────────────────────│
```

### Device Code Request
```bash
curl -X POST https://login.salesforce.com/services/oauth2/device/code \
  -d "client_id=<CONSUMER_KEY>" \
  -d "scope=api refresh_token"
```

### Poll for Token
```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=device" \
  -d "client_id=<CONSUMER_KEY>" \
  -d "code=<DEVICE_CODE>"
```

---

## Refresh Token Flow

**Use**: Exchange refresh token for new access token

```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=refresh_token" \
  -d "client_id=<CONSUMER_KEY>" \
  -d "client_secret=<CONSUMER_SECRET>" \
  -d "refresh_token=<REFRESH_TOKEN>"
```

---

## PKCE (Proof Key for Code Exchange)

**Required for**: Mobile apps, SPAs, Public clients

### Generate Code Verifier & Challenge

```javascript
// Generate random code verifier (43-128 chars)
const codeVerifier = base64URLEncode(crypto.randomBytes(32));

// Create code challenge
const codeChallenge = base64URLEncode(
  crypto.createHash('sha256').update(codeVerifier).digest()
);
```

### Use in Authorization
```
/authorize?...&code_challenge=<CHALLENGE>&code_challenge_method=S256
```

### Use in Token Exchange
```
grant_type=authorization_code&...&code_verifier=<VERIFIER>
```

---

## Token Introspection

**Use**: Validate token status and metadata

```bash
curl -X POST https://login.salesforce.com/services/oauth2/introspect \
  -d "token=<ACCESS_TOKEN>" \
  -d "client_id=<CONSUMER_KEY>" \
  -d "client_secret=<CONSUMER_SECRET>" \
  -d "token_type_hint=access_token"
```

---

## Token Revocation

**Use**: Invalidate tokens on logout

```bash
curl -X POST https://login.salesforce.com/services/oauth2/revoke \
  -d "token=<TOKEN>"
```

---

## Best Practices

1. **Always use HTTPS** for callback URLs in production
2. **Enable PKCE** for all public clients (mobile, SPA)
3. **Use short-lived access tokens** with refresh token rotation
4. **Store secrets securely** - never in client-side code
5. **Implement state parameter** to prevent CSRF
6. **Validate tokens** before trusting claims
7. **Use JWT Bearer** for server-to-server instead of username-password
