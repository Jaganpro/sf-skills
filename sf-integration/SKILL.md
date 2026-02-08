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
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: Write
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/suggest_credential_setup.py"
          timeout: 5000
        - type: command
          command: "python3 ${SKILL_HOOKS}/validate_integration.py"
          timeout: 10000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-integration"
          timeout: 5000
    - matcher: Edit
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/suggest_credential_setup.py"
          timeout: 5000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-integration"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-integration"
      timeout: 5000
---

# sf-integration: Salesforce Integration Patterns Expert

Expert integration architect specializing in secure callout patterns, event-driven architecture, and external service registration for Salesforce.

## Core Responsibilities

1. **Named Credential Generation**: Create Named Credentials with OAuth 2.0, JWT Bearer, Certificate, or Custom authentication
2. **External Credential Generation**: Create modern External Credentials (API 61+) with Named Principals
3. **External Service Registration**: Generate ExternalServiceRegistration metadata from OpenAPI/Swagger specs
4. **REST Callout Patterns**: Synchronous and asynchronous HTTP callout implementations ([details](resources/callout-patterns.md#rest-callout-patterns))
5. **SOAP Callout Patterns**: WSDL2Apex guidance and WebServiceCallout patterns ([details](resources/callout-patterns.md#soap-callout-patterns))
6. **Platform Events**: Event definitions, publishers, and subscriber triggers ([details](resources/event-patterns.md#platform-events))
7. **Change Data Capture**: CDC enablement and subscriber patterns ([details](resources/event-patterns.md#change-data-capture-cdc))
8. **Validation & Scoring**: Score integrations against 6 categories (0-120 points)

## Key Insights

| Insight | Details | Action |
|---------|---------|--------|
| **Named Credential Architecture** | Legacy (pre-API 61) vs External Credentials (API 61+) | Check org API version first |
| **Callouts in Triggers** | Synchronous callouts NOT allowed in triggers | Always use async (Queueable, @future) |
| **Governor Limits** | 100 callouts per transaction, 120s timeout max | Batch callouts, use async patterns |
| **External Services** | Auto-generates Apex from OpenAPI specs | Requires Named Credential for auth |

---

## ⚠️ CRITICAL: Named Credential Architecture (API 61+)

### Legacy Named Credentials vs External Credentials

| Feature | Legacy Named Credential | External Credential (API 61+) |
|---------|------------------------|------------------------------|
| **API Version** | Pre-API 61 | API 61+ (Winter '24+) |
| **Principal Concept** | Single principal per credential | Named Principal + Per-User Principal |
| **OAuth Support** | Basic OAuth 2.0 | Full OAuth 2.0 + PKCE, JWT |
| **Permissions** | Profile-based | Permission Set + Named Principal |
| **Recommendation** | Legacy orgs only | **Use for all new development** |

### Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WHEN TO USE WHICH CREDENTIAL TYPE                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Use LEGACY Named Credential if:                                            │
│  • Org API version < 61                                                     │
│  • Migrating existing integrations (maintain compatibility)                 │
│  • Simple API key / Basic Auth (quick setup)                               │
│                                                                             │
│  Use EXTERNAL Credential (API 61+) if:                                      │
│  • New development (recommended)                                            │
│  • OAuth 2.0 with PKCE required                                            │
│  • Per-user authentication needed                                           │
│  • Fine-grained permission control required                                 │
│  • JWT Bearer flow for server-to-server                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use `AskUserQuestion` to gather:

1. **Integration Type**: Outbound REST/SOAP, Inbound REST, Event-driven (Platform Events, CDC)
2. **Authentication Method**: OAuth 2.0 (Client Credentials, JWT Bearer, Authorization Code), Certificate-based, API Key/Basic Auth
3. **External System Details**: Base endpoint URL, API version, rate limits, required headers
4. **Sync vs Async Requirements**: Real-time response needed → Sync | Fire-and-forget or DML-triggered → Async (Queueable)

### Phase 2: Template Selection

| Integration Need | Template | Location |
|-----------------|----------|----------|
| **Named Credentials** | `oauth-client-credentials.namedCredential-meta.xml` | `templates/named-credentials/` |
| **External Credentials** | `oauth-external-credential.externalCredential-meta.xml` | `templates/external-credentials/` |
| **External Services** | `openapi-registration.externalServiceRegistration-meta.xml` | `templates/external-services/` |
| **REST Callouts** | `rest-sync-callout.cls`, `rest-queueable-callout.cls` | `templates/callouts/` |
| **SOAP Callouts** | `soap-callout-service.cls` | `templates/soap/` |
| **Platform Events** | `platform-event-definition.object-meta.xml` | `templates/platform-events/` |
| **CDC Subscribers** | `cdc-subscriber-trigger.trigger` | `templates/cdc/` |

### Phase 3: Generation & Validation

**File Locations**:
```
force-app/main/default/
├── namedCredentials/          # Legacy Named Credentials
├── externalCredentials/       # External Credentials (API 61+)
├── externalServiceRegistrations/
├── classes/                   # Callout services, handlers
├── objects/{{EventName}}__e/  # Platform Events
└── triggers/                  # Event/CDC subscribers
```

**Validate using scoring system** (see [Scoring System](#scoring-system-120-points) below)

### Phase 4: Deployment

**Deployment Order** (CRITICAL):
```
1. Named Credentials / External Credentials FIRST
2. External Service Registrations (depends on Named Credentials)
3. Apex classes (callout services, handlers)
4. Platform Events / CDC configuration
5. Triggers (depends on events being deployed)
```

**Use sf-deploy skill**: `Skill(skill="sf-deploy")`

**CLI Commands**: See [CLI Commands Reference](#cli-commands-reference)

### Phase 5: Testing & Verification

1. **Test Named Credential**: Setup → Named Credentials → Test Connection
2. **Test External Service**: Invoke generated Apex methods
3. **Test Callout**: Anonymous Apex or test class with `Test.setMock()`
4. **Test Events**: Publish and verify subscriber execution

---

## Named Credentials

| Auth Type | Use Case | Template | Key Config |
|-----------|----------|----------|------------|
| **OAuth 2.0 Client Credentials** | Server-to-server, no user context | `oauth-client-credentials.namedCredential-meta.xml` | scope, tokenEndpoint |
| **OAuth 2.0 JWT Bearer** | CI/CD, backend services | `oauth-jwt-bearer.namedCredential-meta.xml` | Certificate + Connected App |
| **Certificate (Mutual TLS)** | High-security integrations | `certificate-auth.namedCredential-meta.xml` | Client cert required |
| **Custom (API Key/Basic)** | Simple APIs | `custom-auth.namedCredential-meta.xml` | username/password |

Templates in `templates/named-credentials/`. ⚠️ **NEVER hardcode credentials** - always use Named Credentials!

---

## External Credentials (API 61+)

**Use Case**: Modern OAuth 2.0 with per-user or named principal authentication

**Template**: `templates/external-credentials/oauth-external-credential.externalCredential-meta.xml`

**Key Features**:
- Named Principal vs Per-User Principal support
- OAuth 2.0 with PKCE
- JWT Bearer flow
- Permission Set-based access control

**Quick Start**:
```xml
<ExternalCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>{{CredentialLabel}}</label>
    <authenticationProtocol>Oauth</authenticationProtocol>
    <principals>
        <principalName>{{PrincipalName}}</principalName>
        <principalType>NamedPrincipal</principalType>
    </principals>
</ExternalCredential>
```

---

## External Services (OpenAPI/Swagger)

**Process**:
1. Obtain OpenAPI 2.0 (Swagger) or 3.0 spec from external API
2. Create Named Credential for authentication
3. Register External Service in Salesforce (Setup → External Services OR via metadata)
4. Salesforce auto-generates Apex classes: `ExternalService.{{ServiceName}}`

**Template**: `templates/external-services/openapi-registration.externalServiceRegistration-meta.xml`

**CLI Alternative**:
```bash
sf api request rest /services/data/v62.0/externalServiceRegistrations \
  --method POST \
  --body '{"label":"{{Label}}","namedCredential":"{{NC}}","schemaUrl":"{{URL}}"}'
```

**Usage Example**:
```apex
ExternalService.Stripe stripe = new ExternalService.Stripe();
ExternalService.Stripe_createCustomer_Request req = new ExternalService.Stripe_createCustomer_Request();
req.email = 'customer@example.com';
ExternalService.Stripe_createCustomer_Response resp = stripe.createCustomer(req);
```

---

## Callout Patterns

### REST Callouts

**For detailed REST callout patterns, see [resources/callout-patterns.md](resources/callout-patterns.md)**

#### Quick Reference

| Pattern | Use Case | Template |
|---------|----------|----------|
| **Synchronous** | User-initiated, need immediate response | `rest-sync-callout.cls` |
| **Asynchronous (Queueable)** | Triggered from DML (triggers), fire-and-forget | `rest-queueable-callout.cls` |
| **Retry Handler** | Handle transient failures with exponential backoff | `callout-retry-handler.cls` |

**Key Points**:
- Use Named Credentials: `req.setEndpoint('callout:{{NamedCredentialName}}/{{path}}')`
- Set timeout: `req.setTimeout(120000)` (120s max)
- Handle status codes: 2xx success, 4xx client error (don't retry), 5xx server error (retry)

**Detailed Examples**:
- [Synchronous REST Callout](resources/callout-patterns.md#synchronous-rest-callout)
- [Asynchronous Queueable Callout](resources/callout-patterns.md#asynchronous-rest-callout-queueable)
- [Retry Handler with Exponential Backoff](resources/callout-patterns.md#retry-handler-with-exponential-backoff)

### SOAP Callouts

**For detailed SOAP callout patterns, see [resources/callout-patterns.md#soap-callout-patterns](resources/callout-patterns.md#soap-callout-patterns)**

#### Quick Reference

**WSDL2Apex Process**:
1. Setup → Apex Classes → Generate from WSDL
2. Upload WSDL file
3. Salesforce generates stub classes

**Usage**:
```apex
{{WsdlGeneratedClass}}.{{PortType}} stub = new {{WsdlGeneratedClass}}.{{PortType}}();
stub.endpoint_x = 'callout:{{NamedCredentialName}}';
stub.timeout_x = 120000;
return stub.{{OperationName}}(request);
```

**Detailed Examples**:
- [WSDL2Apex Process](resources/callout-patterns.md#wsdl2apex-process)
- [SOAP Service Implementation](resources/callout-patterns.md#soap-service-implementation)

---

## Event-Driven Patterns

### Platform Events

**For detailed Platform Event patterns, see [resources/event-patterns.md#platform-events](resources/event-patterns.md#platform-events)**

#### Quick Reference

**Event Types**:
- **Standard Volume**: ~2,000 events/hour, 3-day retention
- **High Volume**: Millions/day, 24-hour retention, at-least-once delivery

**Templates**:
- Event Definition: `templates/platform-events/platform-event-definition.object-meta.xml`
- Publisher: `templates/platform-events/event-publisher.cls`
- Subscriber: `templates/platform-events/event-subscriber-trigger.trigger`

**Publishing**:
```apex
List<Database.SaveResult> results = EventBus.publish(events);
```

**Subscribing**:
```apex
trigger {{EventName}}Subscriber on {{EventName}}__e (after insert) {
    for ({{EventName}}__e event : Trigger.new) {
        {{EventName}}Handler.processEvent(event);
    }
}
```

**Detailed Examples**:
- [Platform Event Definition](resources/event-patterns.md#platform-event-definition)
- [Event Publisher](resources/event-patterns.md#event-publisher)
- [Event Subscriber Trigger](resources/event-patterns.md#event-subscriber-trigger)

### Change Data Capture (CDC)

**For detailed CDC patterns, see [resources/event-patterns.md#change-data-capture-cdc](resources/event-patterns.md#change-data-capture-cdc)**

#### Quick Reference

**Enablement**: Setup → Integrations → Change Data Capture

**Channel Naming**: `{{ObjectAPIName}}ChangeEvent` (e.g., `AccountChangeEvent`)

**Subscriber Template**:
```apex
trigger {{ObjectName}}CDCSubscriber on {{ObjectName}}ChangeEvent (after insert) {
    for ({{ObjectName}}ChangeEvent event : Trigger.new) {
        EventBus.ChangeEventHeader header = event.ChangeEventHeader;
        String changeType = header.getChangeType(); // CREATE, UPDATE, DELETE, UNDELETE
        List<String> changedFields = header.getChangedFields();
        String recordId = header.getRecordIds()[0];

        switch on changeType {
            when 'CREATE' { {{ObjectName}}CDCHandler.handleCreate(event); }
            when 'UPDATE' { {{ObjectName}}CDCHandler.handleUpdate(event, changedFields); }
            when 'DELETE' { {{ObjectName}}CDCHandler.handleDelete(recordId); }
            when 'UNDELETE' { {{ObjectName}}CDCHandler.handleUndelete(event); }
        }
    }
}
```

**Detailed Examples**:
- [CDC Enablement](resources/event-patterns.md#cdc-enablement)
- [CDC Subscriber Trigger](resources/event-patterns.md#cdc-subscriber-trigger)
- [CDC Handler Service](resources/event-patterns.md#cdc-handler-service)

---

## Scoring System (120 Points)

### Category Breakdown

| Category | Points | Evaluation Criteria |
|----------|--------|---------------------|
| **Security** | 30 | Named Credentials used (no hardcoded secrets), OAuth scopes minimized, certificate auth where applicable |
| **Error Handling** | 25 | Retry logic present, timeout handling (120s max), specific exception types, logging implemented |
| **Bulkification** | 20 | Batch callouts considered, CDC bulk handling, event batching for Platform Events |
| **Architecture** | 20 | Async patterns for DML-triggered callouts, proper service layer separation, single responsibility |
| **Best Practices** | 15 | Governor limit awareness, proper HTTP methods, idempotency for retries |
| **Documentation** | 10 | Clear intent documented, endpoint versioning noted, API contract documented |

### Scoring Thresholds

```
Score: XX/120 Rating
├─ ⭐⭐⭐⭐⭐ Excellent (108-120): Production-ready, follows all best practices
├─ ⭐⭐⭐⭐ Very Good (90-107): Minor improvements suggested
├─ ⭐⭐⭐ Good (72-89): Acceptable with noted improvements
├─ ⭐⭐ Needs Work (54-71): Address issues before deployment
└─ ⭐ Block (<54): CRITICAL issues, do not deploy
```

### Scoring Output Format

```
📊 INTEGRATION SCORE: XX/120 ⭐⭐⭐⭐ Rating
════════════════════════════════════════════════════

🔐 Security           XX/30  ████████░░ XX%
├─ Named Credentials used: ✅
├─ No hardcoded secrets: ✅
└─ OAuth scopes minimal: ✅

⚠️ Error Handling     XX/25  ████████░░ XX%
├─ Retry logic: ✅
├─ Timeout handling: ✅
└─ Logging: ✅

📦 Bulkification      XX/20  ████████░░ XX%
├─ Batch callouts: ✅
└─ Event batching: ✅

🏗️ Architecture       XX/20  ████████░░ XX%
├─ Async patterns: ✅
└─ Service separation: ✅

✅ Best Practices     XX/15  ████████░░ XX%
├─ Governor limits: ✅
└─ Idempotency: ✅

📝 Documentation      XX/10  ████████░░ XX%
├─ Clear intent: ✅
└─ API versioning: ✅

════════════════════════════════════════════════════
```

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

### Agentforce Integration Flow

`sf-integration` → Named Credential + External Service → `sf-flow` → HTTP Callout wrapper → `sf-ai-agentscript` → Agent with `flow://` target → `sf-deploy` → Deploy all

---

## CLI Commands Reference

### Named Credentials

```bash
# List Named Credentials
sf org list metadata --metadata-type NamedCredential --target-org {{alias}}

# Deploy Named Credential
sf project deploy start --metadata NamedCredential:{{Name}} --target-org {{alias}}

# Retrieve Named Credential
sf project retrieve start --metadata NamedCredential:{{Name}} --target-org {{alias}}
```

### External Services

```bash
# List External Service Registrations
sf org list metadata --metadata-type ExternalServiceRegistration --target-org {{alias}}

# Deploy External Service
sf project deploy start --metadata ExternalServiceRegistration:{{Name}} --target-org {{alias}}
```

### Platform Events

```bash
# List Platform Events
sf org list metadata --metadata-type CustomObject --target-org {{alias}} | grep "__e"

# Deploy Platform Event
sf project deploy start --metadata CustomObject:{{EventName}}__e --target-org {{alias}}
```

### API Requests (Beta)

Execute REST and GraphQL API calls directly via `sf` CLI, without `curl`:

```bash
# REST API request
sf api request rest /services/data/v62.0/sobjects/Account/describe --target-org {{alias}}

# REST with POST body
sf api request rest /services/data/v62.0/sobjects/Account --method POST \
  --body '{"Name":"Test Account"}' --target-org {{alias}}

# GraphQL query
sf api request graphql --body '{"query":"{ uiapi { query { Account { edges { node { Name { value } } } } } } }"}' --target-org {{alias}}
```

> **[Beta]** These commands simplify API exploration. For production integration code, use Named Credentials and Apex callouts.

---

## 🔧 Helper Scripts

sf-integration includes automation scripts to configure credentials without manual UI steps.

### Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `configure-named-credential.sh` | Set API keys via ConnectApi (Enhanced NC) | `./scripts/configure-named-credential.sh <org-alias>` |
| `set-api-credential.sh` | Store keys in Custom Settings (legacy) | `./scripts/set-api-credential.sh <name> - <org-alias>` |

### Auto-Run Behavior

When you create credential metadata files, Claude automatically suggests running the appropriate script:

| File Pattern | Suggested Action |
|--------------|------------------|
| `*.namedCredential-meta.xml` | Run `configure-named-credential.sh` |
| `*.externalCredential-meta.xml` | Run `configure-named-credential.sh` |
| `*.cspTrustedSite-meta.xml` | Deploy endpoint security |

### Example Workflow

```bash
# 1. Claude generates credential metadata files
# 2. Hook detects and suggests next steps
# 3. Deploy metadata first
sf project deploy start --metadata ExternalCredential:WeatherAPI \
  --metadata NamedCredential:WeatherAPI \
  --target-org MyOrg

# 4. Run automation script
./scripts/configure-named-credential.sh MyOrg
# Enter API key when prompted (secure, hidden input)
```

### Prerequisites

- **Salesforce CLI v2+**: `sf` command available
- **Authenticated org**: `sf org login web -a <alias>`
- **Deployed metadata**: External Credential and Named Credential deployed

📚 **Documentation**: See [docs/named-credentials-automation.md](docs/named-credentials-automation.md) for complete guide.

---

## Anti-Patterns

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| Hardcoded credentials | Security vulnerability, credential rotation nightmare | Use Named Credentials |
| Sync callout in trigger | `CalloutException: Uncommitted work pending` | Use Queueable with `Database.AllowsCallouts` |
| No timeout specified | Default 10s may be too short | Set `req.setTimeout(120000)` (max 120s) |
| No retry logic | Transient failures cause data loss | Implement exponential backoff |
| Ignoring status codes | Silent failures | Check `statusCode` and handle 4xx/5xx |
| 100+ callouts per transaction | Governor limit exceeded | Batch callouts, use async |
| No logging | Can't debug production issues | Log all callout requests/responses |
| Exposing API errors to users | Security risk, poor UX | Catch and wrap in user-friendly messages |

---

## Additional Resources

📚 **Detailed Documentation**:
- [Callout Patterns](resources/callout-patterns.md) - REST and SOAP callout implementations
- [Event Patterns](resources/event-patterns.md) - Platform Events and Change Data Capture
- [Messaging API v2](docs/messaging-api-v2.md) - **NEW**: MIAW custom client architecture (Agentforce external chat)

📁 **Templates**:
- `templates/named-credentials/` - Authentication templates
- `templates/external-credentials/` - External Credential templates (API 61+)
- `templates/external-services/` - OpenAPI registration templates
- `templates/callouts/` - REST/SOAP callout patterns
- `templates/platform-events/` - Event definitions and publishers
- `templates/cdc/` - Change Data Capture triggers

---

## Notes & Dependencies

- **API Version**: 62.0+ (Winter '25) recommended for External Credentials
- **Required Permissions**: API Enabled, External Services access
- **Optional Skills**: sf-connected-apps (OAuth setup), sf-apex (custom callout code), sf-deploy (deployment)
- **Scoring Mode**: Strict (block deployment if score < 54)

---

## License

MIT License - See LICENSE file for details.
