---
name: sf-integration
description: >
  Creates comprehensive Salesforce integrations with 120-point scoring. Use when
  setting up Named Credentials, External Services, REST/SOAP callouts, Platform
  Events, Change Data Capture, or connecting Salesforce to external systems.
license: MIT
metadata:
  version: "1.2.0"
  author: "Jag Valaiyapathy"
  scoring: "120 points across 6 categories"
---

# sf-integration: Salesforce Integration Patterns Expert

Expert integration architect specializing in secure callout patterns, event-driven architecture, and external service registration for Salesforce.

## Core Responsibilities

1. **Named Credential Generation**: OAuth 2.0, JWT Bearer, Certificate, or Custom authentication
2. **External Credential Generation**: Modern External Credentials (API 61+) with Named Principals
3. **External Service Registration**: Generate ExternalServiceRegistration from OpenAPI/Swagger specs
4. **REST/SOAP Callout Patterns**: Sync and async implementations ([details](resources/callout-patterns.md))
5. **Platform Events & CDC**: Event definitions, publishers, subscribers ([details](resources/event-patterns.md))
6. **Validation & Scoring**: Score integrations against 6 categories (0-120 points)

## Key Insights

| Insight | Details |
|---------|---------|
| **Named Credential Architecture** | Legacy (pre-API 61) vs External Credentials (API 61+) — check org API version first |
| **Callouts in Triggers** | Synchronous callouts NOT allowed — use async (Queueable, @future) |
| **Governor Limits** | 100 callouts per transaction, 120s timeout max — batch callouts, use async |
| **External Services** | Auto-generates Apex from OpenAPI specs — requires Named Credential for auth |

---

## Named Credential Architecture (API 61+)

| Feature | Legacy Named Credential | External Credential (API 61+) |
|---------|------------------------|------------------------------|
| **API Version** | Pre-API 61 | API 61+ (Winter '24+) |
| **Principal Concept** | Single principal | Named + Per-User Principal |
| **OAuth Support** | Basic OAuth 2.0 | Full OAuth 2.0 + PKCE, JWT |
| **Recommendation** | Legacy orgs only | **Use for all new development** |

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use `AskUserQuestion` to gather: integration type (outbound REST/SOAP, inbound, event-driven), auth method (OAuth 2.0, JWT Bearer, Certificate, API Key), external system details (endpoint, rate limits), sync vs async requirements.

### Phase 2: Template Selection

| Integration Need | Template | Location |
|-----------------|----------|----------|
| Named Credentials | `oauth-client-credentials.namedCredential-meta.xml` | `templates/named-credentials/` |
| External Credentials | `oauth-external-credential.externalCredential-meta.xml` | `templates/external-credentials/` |
| External Services | `openapi-registration.externalServiceRegistration-meta.xml` | `templates/external-services/` |
| REST Callouts | `rest-sync-callout.cls`, `rest-queueable-callout.cls` | `templates/callouts/` |
| SOAP Callouts | `soap-callout-service.cls` | `templates/soap/` |
| Platform Events | `platform-event-definition.object-meta.xml` | `templates/platform-events/` |
| CDC Subscribers | `cdc-subscriber-trigger.trigger` | `templates/cdc/` |

### Phase 3: Generation & Validation

```
force-app/main/default/
├── namedCredentials/          # Legacy Named Credentials
├── externalCredentials/       # External Credentials (API 61+)
├── externalServiceRegistrations/
├── classes/                   # Callout services, handlers
├── objects/{{EventName}}__e/  # Platform Events
└── triggers/                  # Event/CDC subscribers
```

### Phase 4: Deployment (CRITICAL ORDER)

1. Named Credentials / External Credentials FIRST
2. External Service Registrations (depends on Named Credentials)
3. Apex classes (callout services, handlers)
4. Platform Events / CDC configuration
5. Triggers (depends on events being deployed)

Use sf-deploy skill: `Skill(skill="sf-deploy")`

### Phase 5: Testing & Verification

1. **Named Credential**: Setup → Named Credentials → Test Connection
2. **External Service**: Invoke generated Apex methods
3. **Callout**: Anonymous Apex or test class with `Test.setMock()`
4. **Events**: Publish and verify subscriber execution

---

## Named Credentials

| Auth Type | Use Case | Template |
|-----------|----------|----------|
| **OAuth 2.0 Client Credentials** | Server-to-server | `oauth-client-credentials.namedCredential-meta.xml` |
| **OAuth 2.0 JWT Bearer** | CI/CD, backend | `oauth-jwt-bearer.namedCredential-meta.xml` |
| **Certificate (Mutual TLS)** | High-security | `certificate-auth.namedCredential-meta.xml` |
| **Custom (API Key/Basic)** | Simple APIs | `custom-auth.namedCredential-meta.xml` |

Templates in `templates/named-credentials/`. **NEVER hardcode credentials.**

---

## External Services (OpenAPI/Swagger)

**Process**: Obtain OpenAPI spec → Create Named Credential → Register External Service → Salesforce auto-generates `ExternalService.{{ServiceName}}` Apex classes.

```apex
ExternalService.Stripe stripe = new ExternalService.Stripe();
ExternalService.Stripe_createCustomer_Request req = new ExternalService.Stripe_createCustomer_Request();
req.email = 'customer@example.com';
ExternalService.Stripe_createCustomer_Response resp = stripe.createCustomer(req);
```

---

## Callout Patterns

> See [resources/callout-patterns.md](resources/callout-patterns.md) for complete REST and SOAP implementations.

| Pattern | Use Case | Template |
|---------|----------|----------|
| **Sync REST** | User-initiated, immediate response | `rest-sync-callout.cls` |
| **Async Queueable** | Triggered from DML, fire-and-forget | `rest-queueable-callout.cls` |
| **Retry Handler** | Transient failures, exponential backoff | `callout-retry-handler.cls` |
| **SOAP (WSDL2Apex)** | WSDL-based services | `soap-callout-service.cls` |

**Key rules**: Use Named Credentials (`callout:{{NC}}/path`), set timeout (`req.setTimeout(120000)`), handle 4xx/5xx status codes.

---

## Event-Driven Patterns

> See [resources/event-patterns.md](resources/event-patterns.md) for complete Platform Event and CDC implementations.

**Platform Events**: Standard Volume (~2K events/hour, 3-day retention) or High Volume (millions/day, 24-hour retention). Publish via `EventBus.publish()`, subscribe via triggers.

**Change Data Capture (CDC)**: Enable via Setup → Integrations → CDC. Channel: `{{Object}}ChangeEvent`. Change types: CREATE, UPDATE, DELETE, UNDELETE.

---

## Scoring System (120 Points)

> See [references/scoring-rubric.md](references/scoring-rubric.md) for the full category breakdown, scoring thresholds, and output format.

**Quick summary:** Security (30), Error Handling (25), Bulkification (20), Architecture (20), Best Practices (15), Documentation (10). Score 108+ = Excellent. Score <54 = BLOCK.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Hardcoded credentials | Security vulnerability | Use Named Credentials |
| Sync callout in trigger | `CalloutException` | Use Queueable |
| No timeout specified | Default 10s too short | `req.setTimeout(120000)` |
| No retry logic | Transient failures | Exponential backoff |
| 100+ callouts per txn | Governor limit | Batch + async |
| No logging | Can't debug production | Log requests/responses |

---

## CLI Commands & Helper Scripts

> See [references/cli-reference.md](references/cli-reference.md) for Named Credential, External Service, Platform Event CLI commands, API request examples, and credential automation scripts.

---

## Cross-Skill Integration

| To Skill | When to Use |
|----------|-------------|
| sf-connected-apps | OAuth Connected App for Named Credential |
| sf-apex | Custom callout service beyond templates |
| sf-metadata | Query existing Named Credentials |
| sf-deploy | Deploy to org |
| sf-ai-agentscript | Agent action using External Service |
| sf-flow | HTTP Callout Flow for agent |

**Agentforce Integration Flow**: sf-integration → Named Credential + External Service → sf-flow → HTTP Callout wrapper → sf-ai-agentscript → `flow://` target → sf-deploy

---

## Additional Resources

- [Callout Patterns](resources/callout-patterns.md) — REST and SOAP implementations
- [Event Patterns](resources/event-patterns.md) — Platform Events and CDC
- [Messaging API v2](docs/messaging-api-v2.md) — MIAW custom client architecture (Agentforce external chat)
- [Scoring Rubric](references/scoring-rubric.md) — 120-point scoring details
- [CLI Reference](references/cli-reference.md) — CLI commands and helper scripts

---

## Notes & Dependencies

- **API Version**: 62.0+ recommended for External Credentials
- **Required Permissions**: API Enabled, External Services access
- **Optional Skills**: sf-connected-apps, sf-apex, sf-deploy
- **Scoring Mode**: Strict (block deployment if score < 54)
