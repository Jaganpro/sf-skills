# Authentication & External Client App Setup

Complete guide for OAuth Client Credentials flow with the Agentforce Agent API.

> Official docs: [Get Started with Agent API](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-api-get-started.html)

## Prerequisites

- Agentforce enabled org with at least one activated agent
- A user with API login access (admin or Integration User)

---

## Step 1: Create External Client App (ECA)

1. Setup → Quick Find → "External Client App" → **External Client Apps Manager**
2. **New External Client App** → provide name and contact email
3. **Enable OAuth** with these scopes:
   - `api` — Manage user data via APIs
   - `refresh_token, offline_access` — Perform requests at any time
   - `chatbot_api` — Access chatbot services
   - `sfap_api` — Access the Salesforce API Platform
4. Check these OAuth settings:
   - **Enable Client Credentials Flow**
   - **Issue JWT-based access tokens for named users**
5. **Uncheck** these:
   - Require secret for Web Server Flow
   - Require secret for Refresh Token Flow
   - Require PKCE for Supported Authorization Flows
6. Save and create

## Step 2: Configure Policy

1. App settings → **Policy** tab → **Edit**
2. Under "OAuth Flows and External Client App Enhancements":
   - Check **Enable Client Credentials Flow**
   - Set **Run As (Username)** to a user with API login access
3. Save

### Run As User — Critical Gotcha

The Run As user **must** have a full Salesforce license with API login capability.

**Do NOT use**:
- Einstein Agent service users (`serviceagentagentforce...@example.com`) — restricted licenses, will return `invalid_grant` / `Maximum Logins Exceeded`
- Users without API permissions

**Use instead**:
- Full Salesforce admin user (dev/testing)
- Salesforce Integration User (production)

## Step 3: Obtain Credentials

1. App settings → **Settings** tab
2. Expand **OAuth Settings**
3. Click **Consumer Key and Secret**
4. Copy both values

---

## Token Request

```
POST https://{MY_DOMAIN}/services/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id={CONSUMER_KEY}&client_secret={CONSUMER_SECRET}
```

**Response:**
```json
{
  "access_token": "00D...",
  "instance_url": "https://myorg.my.salesforce.com",
  "id": "https://login.salesforce.com/id/00D.../005...",
  "token_type": "Bearer",
  "issued_at": "1234567890",
  "signature": "..."
}
```

Use the `access_token` value in the `Authorization: Bearer` header for all Agent API calls.

---

## Token Caching

### Why It Matters

Salesforce enforces a **3,600 logins per user per hour** rolling rate limit. Exceeding it returns `login rate exceeded` and you must wait 15–30 minutes.

### Next.js / HMR Gotcha

In dev mode, Hot Module Replacement resets module-scoped variables on every file save. A naive token cache in module scope triggers a fresh OAuth request each save.

**Fix — use `globalThis`:**

```typescript
const g = globalThis as typeof globalThis & {
  __sfToken?: { token: string; expiresAt: number };
};
if (!g.__sfToken) g.__sfToken = { token: '', expiresAt: 0 };
```

### Caching Rules

1. **Never retry on rate limit** — retrying burns more quota
2. **Dedup concurrent requests** — share a single in-flight Promise:
   ```typescript
   let tokenPromise: Promise<string> | null = null;
   async function getToken() {
     if (g.__sfToken && Date.now() < g.__sfToken.expiresAt) {
       return g.__sfToken.token;
     }
     if (!tokenPromise) {
       tokenPromise = fetchNewToken().finally(() => { tokenPromise = null; });
     }
     return tokenPromise;
   }
   ```
3. **Expire early** — subtract 60 seconds from the token's actual expiry
4. **Trim env vars** — hosting platforms can add trailing `\n`:
   ```typescript
   const domain = process.env.SALESFORCE_MY_DOMAIN?.trim();
   ```

---

## Environment Variables

```env
SALESFORCE_MY_DOMAIN=your-org.my.salesforce.com
SALESFORCE_CONSUMER_KEY=3MVG9...
SALESFORCE_CONSUMER_SECRET=ABC123...
SALESFORCE_AGENT_ID=0XxHu000000XXXXKXX
```

Always normalize the domain:

```typescript
const endpoint = myDomain.startsWith('https://') ? myDomain : `https://${myDomain}`;
```

---

## Alternative Auth Flows

The Client Credentials flow is the most common for server-to-server Agent API integration. Other supported flows include any that produce a JWT-based access token. See [JWT-Based Access Tokens](https://help.salesforce.com/s/articleView?id=xcloud.jwt_access_tokens.htm) for alternatives.
