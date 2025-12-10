---
name: sf-integration
description: Creates comprehensive Salesforce integrations including Named Credentials, External Services, REST/SOAP callouts, Platform Events, and Change Data Capture. 120-point scoring across 6 categories. Use this skill when the user needs to connect Salesforce to external systems.
---

# sf-integration: Salesforce Integration Patterns Expert

Expert integration architect specializing in secure callout patterns, event-driven architecture, and external service registration for Salesforce.

## Core Responsibilities

1. **Named Credential Generation**: Create Named Credentials with OAuth 2.0, JWT Bearer, Certificate, or Custom authentication
2. **External Credential Generation**: Create modern External Credentials (API 61+) with Named Principals
3. **External Service Registration**: Generate ExternalServiceRegistration metadata from OpenAPI/Swagger specs
4. **REST Callout Patterns**: Synchronous and asynchronous HTTP callout implementations
5. **SOAP Callout Patterns**: WSDL2Apex guidance and WebServiceCallout patterns
6. **Platform Events**: Event definitions, publishers, and subscriber triggers
7. **Change Data Capture**: CDC enablement and subscriber patterns
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

1. **Integration Type**:
   - Outbound REST (Salesforce → External API)
   - Outbound SOAP (Salesforce → External SOAP Service)
   - Inbound REST (External → Salesforce REST API)
   - Event-driven (Platform Events, CDC)

2. **Authentication Method**:
   - OAuth 2.0 Client Credentials
   - OAuth 2.0 JWT Bearer
   - OAuth 2.0 Authorization Code
   - Certificate-based (Mutual TLS)
   - API Key / Basic Auth

3. **External System Details**:
   - Base endpoint URL
   - API version
   - Rate limits
   - Required headers

4. **Sync vs Async Requirements**:
   - Real-time response needed? → Sync
   - Fire-and-forget? → Async (@future, Queueable)
   - Triggered from DML? → MUST be async

### Phase 2: Template Selection

| Integration Need | Template | Location |
|-----------------|----------|----------|
| OAuth 2.0 Client Credentials | `oauth-client-credentials.namedCredential-meta.xml` | `templates/named-credentials/` |
| OAuth 2.0 JWT Bearer | `oauth-jwt-bearer.namedCredential-meta.xml` | `templates/named-credentials/` |
| Certificate Auth | `certificate-auth.namedCredential-meta.xml` | `templates/named-credentials/` |
| API Key / Basic Auth | `custom-auth.namedCredential-meta.xml` | `templates/named-credentials/` |
| External Credential (OAuth) | `oauth-external-credential.externalCredential-meta.xml` | `templates/external-credentials/` |
| External Service (OpenAPI) | `openapi-registration.externalServiceRegistration-meta.xml` | `templates/external-services/` |
| REST Callout (Sync) | `rest-sync-callout.cls` | `templates/callouts/` |
| REST Callout (Async) | `rest-queueable-callout.cls` | `templates/callouts/` |
| Retry Handler | `callout-retry-handler.cls` | `templates/callouts/` |
| SOAP Callout | `soap-callout-service.cls` | `templates/soap/` |
| Platform Event | `platform-event-definition.object-meta.xml` | `templates/platform-events/` |
| Event Publisher | `event-publisher.cls` | `templates/platform-events/` |
| Event Subscriber | `event-subscriber-trigger.trigger` | `templates/platform-events/` |
| CDC Subscriber | `cdc-subscriber-trigger.trigger` | `templates/cdc/` |

### Phase 3: Generation & Validation

**File Locations**:
```
force-app/main/default/
├── namedCredentials/
│   └── {{CredentialName}}.namedCredential-meta.xml
├── externalCredentials/
│   └── {{CredentialName}}.externalCredential-meta.xml
├── externalServiceRegistrations/
│   └── {{ServiceName}}.externalServiceRegistration-meta.xml
├── classes/
│   ├── {{ServiceName}}Callout.cls
│   ├── {{ServiceName}}Callout.cls-meta.xml
│   └── ...
├── objects/
│   └── {{EventName}}__e/
│       └── {{EventName}}__e.object-meta.xml
└── triggers/
    ├── {{EventName}}Subscriber.trigger
    └── {{EventName}}Subscriber.trigger-meta.xml
```

**Validate using scoring system** (see Scoring System section)

### Phase 4: Deployment

**Deployment Order** (CRITICAL):
```
1. Deploy Named Credentials / External Credentials FIRST
2. Deploy External Service Registrations (depends on Named Credentials)
3. Deploy Apex classes (callout services, handlers)
4. Deploy Platform Events / CDC configuration
5. Deploy Triggers (depends on events being deployed)
```

**Use sf-deploy skill**:
```
Skill(skill="sf-deploy")
Request: "Deploy Named Credential {{Name}} with dry-run first"
```

**CLI Commands**:
```bash
# Deploy Named Credential
sf project deploy start --metadata NamedCredential:{{Name}} --target-org {{alias}}

# Deploy External Service
sf project deploy start --metadata ExternalServiceRegistration:{{Name}} --target-org {{alias}}

# Deploy all integration components
sf project deploy start --source-dir force-app/main/default/namedCredentials,force-app/main/default/externalServiceRegistrations --target-org {{alias}}
```

### Phase 5: Testing & Verification

1. **Test Named Credential** in Setup → Named Credentials → Test Connection
2. **Test External Service** by invoking generated Apex methods
3. **Test Callout** using Anonymous Apex or test class
4. **Test Events** by publishing and verifying subscriber execution

---

## Named Credentials

### OAuth 2.0 Client Credentials

**Use Case**: Server-to-server integration without user context

**Template**: `templates/named-credentials/oauth-client-credentials.namedCredential-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{{CredentialName}}</fullName>
    <label>{{CredentialLabel}}</label>
    <endpoint>{{BaseEndpoint}}</endpoint>
    <principalType>NamedUser</principalType>
    <protocol>Oauth</protocol>
    <oauthScope>{{Scopes}}</oauthScope>
    <oauthTokenEndpoint>{{TokenEndpoint}}</oauthTokenEndpoint>
    <generateAuthorizationHeader>true</generateAuthorizationHeader>
    <allowMergeFieldsInBody>true</allowMergeFieldsInBody>
    <allowMergeFieldsInHeader>true</allowMergeFieldsInHeader>
</NamedCredential>
```

### OAuth 2.0 JWT Bearer

**Use Case**: Server-to-server with certificate-based authentication (CI/CD, backend services)

**Template**: `templates/named-credentials/oauth-jwt-bearer.namedCredential-meta.xml`

**Requirements**:
- Certificate uploaded to Salesforce (Setup → Certificate and Key Management)
- Connected App configured for JWT Bearer flow
- Certificate registered with external system

### Certificate-Based Authentication (Mutual TLS)

**Use Case**: High-security integrations requiring client certificate

**Template**: `templates/named-credentials/certificate-auth.namedCredential-meta.xml`

### Custom Authentication (API Key / Basic Auth)

**Use Case**: Simple APIs with API key or username/password

**Template**: `templates/named-credentials/custom-auth.namedCredential-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{{CredentialName}}</fullName>
    <label>{{CredentialLabel}}</label>
    <endpoint>{{BaseEndpoint}}</endpoint>
    <principalType>NamedUser</principalType>
    <protocol>Password</protocol>
    <username>{{Username}}</username>
    <generateAuthorizationHeader>true</generateAuthorizationHeader>
    <allowMergeFieldsInBody>true</allowMergeFieldsInBody>
    <allowMergeFieldsInHeader>true</allowMergeFieldsInHeader>
</NamedCredential>
```

**⚠️ CRITICAL**: Password is stored in Named Credential, NOT in code. Never hardcode credentials!

---

## External Credentials (API 61+)

### OAuth External Credential

**Use Case**: Modern OAuth 2.0 with per-user or named principal authentication

**Template**: `templates/external-credentials/oauth-external-credential.externalCredential-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExternalCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>{{CredentialLabel}}</label>
    <authenticationProtocol>Oauth</authenticationProtocol>
    <externalCredentialParameters>
        <parameterName>clientId</parameterName>
        <parameterType>AuthProviderClientId</parameterType>
        <parameterValue>{{ClientId}}</parameterValue>
    </externalCredentialParameters>
    <externalCredentialParameters>
        <parameterName>clientSecret</parameterName>
        <parameterType>AuthProviderClientSecret</parameterType>
        <parameterValue>{{ClientSecret}}</parameterValue>
    </externalCredentialParameters>
    <principals>
        <principalName>{{PrincipalName}}</principalName>
        <principalType>NamedPrincipal</principalType>
        <sequenceNumber>1</sequenceNumber>
    </principals>
</ExternalCredential>
```

---

## External Services (OpenAPI/Swagger)

### Generating from OpenAPI Spec

**Process**:
1. Obtain OpenAPI 2.0 (Swagger) or 3.0 spec from external API
2. Create Named Credential for authentication
3. Register External Service in Salesforce
4. Salesforce auto-generates Apex classes

**Template**: `templates/external-services/openapi-registration.externalServiceRegistration-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExternalServiceRegistration xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>{{ServiceLabel}}</label>
    <namedCredential>{{NamedCredentialName}}</namedCredential>
    <schema>{{OpenAPISchemaContent}}</schema>
    <schemaType>OpenApi3</schemaType>
    <serviceBinding>{{ServiceBindingName}}</serviceBinding>
    <status>Complete</status>
</ExternalServiceRegistration>
```

**CLI Alternative**:
```bash
# Register External Service from URL
sf api request rest /services/data/v62.0/externalServiceRegistrations \
  --method POST \
  --body '{"label":"{{Label}}","namedCredential":"{{NC}}","schemaUrl":"{{URL}}"}'
```

### Using Auto-Generated Apex

External Services generate Apex classes like:
- `ExternalService.{{ServiceName}}`
- `ExternalService.{{ServiceName}}_{{OperationName}}`

**Example Usage**:
```apex
// Auto-generated class usage
ExternalService.Stripe stripe = new ExternalService.Stripe();
ExternalService.Stripe_createCustomer_Request req = new ExternalService.Stripe_createCustomer_Request();
req.email = 'customer@example.com';
ExternalService.Stripe_createCustomer_Response resp = stripe.createCustomer(req);
```

---

## REST Callout Patterns

### Synchronous REST Callout

**Use Case**: Need immediate response, NOT triggered from DML

**Template**: `templates/callouts/rest-sync-callout.cls`

```apex
public with sharing class {{ServiceName}}Callout {

    private static final String NAMED_CREDENTIAL = 'callout:{{NamedCredentialName}}';

    public static HttpResponse makeRequest(String method, String endpoint, String body) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(NAMED_CREDENTIAL + endpoint);
        req.setMethod(method);
        req.setHeader('Content-Type', 'application/json');
        req.setTimeout(120000); // 120 seconds max

        if (String.isNotBlank(body)) {
            req.setBody(body);
        }

        Http http = new Http();
        return http.send(req);
    }

    public static Map<String, Object> get(String endpoint) {
        HttpResponse res = makeRequest('GET', endpoint, null);
        return handleResponse(res);
    }

    public static Map<String, Object> post(String endpoint, Map<String, Object> payload) {
        HttpResponse res = makeRequest('POST', endpoint, JSON.serialize(payload));
        return handleResponse(res);
    }

    private static Map<String, Object> handleResponse(HttpResponse res) {
        Integer statusCode = res.getStatusCode();

        if (statusCode >= 200 && statusCode < 300) {
            return (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        } else if (statusCode >= 400 && statusCode < 500) {
            throw new CalloutException('Client Error: ' + statusCode + ' - ' + res.getBody());
        } else if (statusCode >= 500) {
            throw new CalloutException('Server Error: ' + statusCode + ' - ' + res.getBody());
        }

        return null;
    }
}
```

### Asynchronous REST Callout (Queueable)

**Use Case**: Callouts triggered from DML (triggers, Process Builder)

**Template**: `templates/callouts/rest-queueable-callout.cls`

```apex
public with sharing class {{ServiceName}}QueueableCallout implements Queueable, Database.AllowsCallouts {

    private List<Id> recordIds;
    private String operation;

    public {{ServiceName}}QueueableCallout(List<Id> recordIds, String operation) {
        this.recordIds = recordIds;
        this.operation = operation;
    }

    public void execute(QueueableContext context) {
        if (recordIds == null || recordIds.isEmpty()) {
            return;
        }

        try {
            // Query records
            List<{{ObjectName}}> records = [
                SELECT Id, Name, {{FieldsToSend}}
                FROM {{ObjectName}}
                WHERE Id IN :recordIds
                WITH USER_MODE
            ];

            // Make callout for each record (consider batching)
            for ({{ObjectName}} record : records) {
                makeCallout(record);
            }

        } catch (CalloutException e) {
            // Log callout errors
            System.debug(LoggingLevel.ERROR, 'Callout failed: ' + e.getMessage());
            // Consider: Create error log record, retry logic, notification
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, 'Error: ' + e.getMessage());
        }
    }

    private void makeCallout({{ObjectName}} record) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:{{NamedCredentialName}}/{{Endpoint}}');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');
        req.setTimeout(120000);

        Map<String, Object> payload = new Map<String, Object>{
            'id' => record.Id,
            'name' => record.Name
            // Add more fields
        };
        req.setBody(JSON.serialize(payload));

        Http http = new Http();
        HttpResponse res = http.send(req);

        if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
            // Success - update record status if needed
        } else {
            // Handle error
            throw new CalloutException('API Error: ' + res.getStatusCode());
        }
    }
}
```

### Retry Handler with Exponential Backoff

**Use Case**: Handle transient failures with intelligent retry

**Template**: `templates/callouts/callout-retry-handler.cls`

```apex
public with sharing class CalloutRetryHandler {

    private static final Integer MAX_RETRIES = 3;
    private static final Integer BASE_DELAY_MS = 1000; // 1 second

    public static HttpResponse executeWithRetry(HttpRequest request) {
        Integer retryCount = 0;
        HttpResponse response;

        while (retryCount < MAX_RETRIES) {
            try {
                Http http = new Http();
                response = http.send(request);

                // Success or client error (4xx) - don't retry
                if (response.getStatusCode() < 500) {
                    return response;
                }

                // Server error (5xx) - retry with backoff
                retryCount++;
                if (retryCount < MAX_RETRIES) {
                    // Exponential backoff: 1s, 2s, 4s
                    Integer delayMs = BASE_DELAY_MS * (Integer) Math.pow(2, retryCount - 1);
                    // Note: Apex doesn't have sleep(), so we schedule retry via Queueable
                    throw new RetryableException('Server error, retry ' + retryCount);
                }

            } catch (CalloutException e) {
                retryCount++;
                if (retryCount >= MAX_RETRIES) {
                    throw e;
                }
            }
        }

        return response;
    }

    public class RetryableException extends Exception {}
}
```

---

## SOAP Callout Patterns

### WSDL2Apex Process

**Step 1**: Generate Apex from WSDL
1. Setup → Apex Classes → Generate from WSDL
2. Upload WSDL file
3. Salesforce generates Apex classes

**Step 2**: Configure Remote Site Setting or Named Credential

**Step 3**: Use generated classes in Apex

**Template**: `templates/soap/soap-callout-service.cls`

```apex
public with sharing class {{ServiceName}}SoapService {

    public static {{ResponseType}} callService({{RequestType}} request) {
        try {
            // Generated stub class
            {{WsdlGeneratedClass}}.{{PortType}} stub = new {{WsdlGeneratedClass}}.{{PortType}}();

            // Set endpoint (use Named Credential if possible)
            stub.endpoint_x = 'callout:{{NamedCredentialName}}';

            // Set timeout
            stub.timeout_x = 120000;

            // Make the call
            return stub.{{OperationName}}(request);

        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, 'SOAP Callout Error: ' + e.getMessage());
            throw new CalloutException('SOAP service error: ' + e.getMessage());
        }
    }
}
```

---

## Platform Events

### Platform Event Definition

**Use Case**: Asynchronous, event-driven communication

**Template**: `templates/platform-events/platform-event-definition.object-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <deploymentStatus>Deployed</deploymentStatus>
    <eventType>HighVolume</eventType>
    <label>{{EventLabel}}</label>
    <pluralLabel>{{EventPluralLabel}}</pluralLabel>
    <publishBehavior>PublishAfterCommit</publishBehavior>
    <fields>
        <fullName>{{FieldName}}__c</fullName>
        <label>{{FieldLabel}}</label>
        <type>Text</type>
        <length>255</length>
    </fields>
    <!-- Add more fields as needed -->
</CustomObject>
```

**Event Types**:
- `StandardVolume`: ~2,000 events/hour, standard delivery
- `HighVolume`: Millions/day, at-least-once delivery, 24-hour retention

### Event Publisher

**Template**: `templates/platform-events/event-publisher.cls`

```apex
public with sharing class {{EventName}}Publisher {

    public static void publishEvents(List<{{EventName}}__e> events) {
        if (events == null || events.isEmpty()) {
            return;
        }

        List<Database.SaveResult> results = EventBus.publish(events);

        for (Integer i = 0; i < results.size(); i++) {
            Database.SaveResult sr = results[i];
            if (!sr.isSuccess()) {
                for (Database.Error err : sr.getErrors()) {
                    System.debug(LoggingLevel.ERROR,
                        'Event publish error: ' + err.getStatusCode() + ' - ' + err.getMessage());
                }
            }
        }
    }

    public static void publishSingleEvent(Map<String, Object> eventData) {
        {{EventName}}__e event = new {{EventName}}__e();
        // Map fields from eventData
        event.{{FieldName}}__c = (String) eventData.get('{{fieldKey}}');

        Database.SaveResult sr = EventBus.publish(event);
        if (!sr.isSuccess()) {
            throw new EventPublishException('Failed to publish event: ' + sr.getErrors());
        }
    }

    public class EventPublishException extends Exception {}
}
```

### Event Subscriber Trigger

**Template**: `templates/platform-events/event-subscriber-trigger.trigger`

```apex
trigger {{EventName}}Subscriber on {{EventName}}__e (after insert) {
    // Get replay ID for resumption
    String lastReplayId = '';

    for ({{EventName}}__e event : Trigger.new) {
        // Store replay ID for potential resume
        lastReplayId = event.ReplayId;

        try {
            // Process event
            {{EventName}}Handler.processEvent(event);
        } catch (Exception e) {
            // Log error but don't throw - allow other events to process
            System.debug(LoggingLevel.ERROR,
                'Event processing error: ' + e.getMessage() +
                ' ReplayId: ' + event.ReplayId);
        }
    }

    // Set resume checkpoint (for high-volume events)
    EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastReplayId);
}
```

---

## Change Data Capture (CDC)

### CDC Enablement

Enable CDC via Setup → Integrations → Change Data Capture, or via metadata:

**Objects supporting CDC**: Standard objects, Custom objects

**Channel Format**: `{{ObjectAPIName}}ChangeEvent` (e.g., `AccountChangeEvent`, `Order__ChangeEvent`)

### CDC Subscriber Trigger

**Template**: `templates/cdc/cdc-subscriber-trigger.trigger`

```apex
trigger {{ObjectName}}CDCSubscriber on {{ObjectName}}ChangeEvent (after insert) {

    for ({{ObjectName}}ChangeEvent event : Trigger.new) {
        // Get change event header
        EventBus.ChangeEventHeader header = event.ChangeEventHeader;

        String changeType = header.getChangeType();
        List<String> changedFields = header.getChangedFields();
        String recordId = header.getRecordIds()[0]; // First record ID

        System.debug('CDC Event - Type: ' + changeType +
                     ', RecordId: ' + recordId +
                     ', Changed Fields: ' + changedFields);

        // Route based on change type
        switch on changeType {
            when 'CREATE' {
                // Handle new record
                {{ObjectName}}CDCHandler.handleCreate(event);
            }
            when 'UPDATE' {
                // Handle update
                {{ObjectName}}CDCHandler.handleUpdate(event, changedFields);
            }
            when 'DELETE' {
                // Handle delete
                {{ObjectName}}CDCHandler.handleDelete(recordId);
            }
            when 'UNDELETE' {
                // Handle undelete
                {{ObjectName}}CDCHandler.handleUndelete(event);
            }
        }
    }
}
```

### CDC Handler Service

**Template**: `templates/cdc/cdc-handler.cls`

```apex
public with sharing class {{ObjectName}}CDCHandler {

    public static void handleCreate({{ObjectName}}ChangeEvent event) {
        // Sync to external system on create
        Map<String, Object> payload = buildPayload(event);
        System.enqueueJob(new ExternalSystemSyncQueueable(payload, 'CREATE'));
    }

    public static void handleUpdate({{ObjectName}}ChangeEvent event, List<String> changedFields) {
        // Only sync if relevant fields changed
        Set<String> fieldsToWatch = new Set<String>{'Name', 'Status__c', 'Amount__c'};

        Boolean relevantChange = false;
        for (String field : changedFields) {
            if (fieldsToWatch.contains(field)) {
                relevantChange = true;
                break;
            }
        }

        if (relevantChange) {
            Map<String, Object> payload = buildPayload(event);
            payload.put('changedFields', changedFields);
            System.enqueueJob(new ExternalSystemSyncQueueable(payload, 'UPDATE'));
        }
    }

    public static void handleDelete(String recordId) {
        Map<String, Object> payload = new Map<String, Object>{'recordId' => recordId};
        System.enqueueJob(new ExternalSystemSyncQueueable(payload, 'DELETE'));
    }

    public static void handleUndelete({{ObjectName}}ChangeEvent event) {
        handleCreate(event); // Treat undelete like create
    }

    private static Map<String, Object> buildPayload({{ObjectName}}ChangeEvent event) {
        return new Map<String, Object>{
            'recordId' => event.ChangeEventHeader.getRecordIds()[0],
            'commitTimestamp' => event.ChangeEventHeader.getCommitTimestamp(),
            // Add event field values
            'name' => event.Name
            // Add more fields
        };
    }
}
```

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

| To Skill | When to Use | Example Invocation |
|----------|-------------|-------------------|
| sf-connected-apps | Need OAuth Connected App for Named Credential | `Skill(skill="sf-connected-apps")` → "Create Connected App for API integration" |
| sf-apex | Need custom callout service beyond templates | `Skill(skill="sf-apex")` → "Create Queueable callout service" |
| sf-metadata | Query existing Named Credentials or objects | `Skill(skill="sf-metadata")` → "List Named Credentials in org" |
| sf-deploy | Deploy integration components | `Skill(skill="sf-deploy")` → "Deploy Named Credential with dry-run" |
| sf-ai-agentforce | Create agent action using External Service | `Skill(skill="sf-ai-agentforce")` → "Create agent with API action" |
| sf-flow | Create HTTP Callout Flow for agent | `Skill(skill="sf-flow")` → "Create Autolaunched HTTP Callout Flow" |
| sf-data | Test integration with sample data | `Skill(skill="sf-data")` → "Create test Account for callout testing" |

### Integration with sf-ai-agentforce

When creating agents that need external API access:

1. **sf-integration creates**: Named Credential + External Service
2. **sf-flow creates**: HTTP Callout Flow wrapper
3. **sf-ai-agentforce creates**: Agent with `flow://` action targeting the callout flow

**Workflow**:
```
User: "Create agent that checks order status from external API"
                    ↓
sf-ai-agentforce detects API need → calls sf-integration
                    ↓
sf-integration creates Named Credential + External Service
                    ↓
sf-flow creates HTTP Callout Flow
                    ↓
sf-ai-agentforce creates agent with flow:// target
                    ↓
sf-deploy deploys all components
```

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

## Notes & Dependencies

- **API Version**: 62.0+ (Winter '25) recommended for External Credentials
- **Required Permissions**: API Enabled, External Services access
- **Optional Skills**: sf-connected-apps (OAuth setup), sf-apex (custom callout code), sf-deploy (deployment)
- **Scoring Mode**: Strict (block deployment if score < 54)

---

## License

MIT License - See LICENSE file for details.
