# sf-diagram Usage Examples

Real-world examples of using the sf-diagram skill.

---

## Example 1: OAuth Flow Diagram

### Request
```
"Create a JWT Bearer OAuth flow diagram for our CI/CD pipeline integration"
```

### Generated Output

#### Mermaid Diagram
```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'actorBkg': '#00A1E0',
  'actorTextColor': '#ffffff',
  'signalColor': '#032D60'
}}}%%
sequenceDiagram
    autonumber

    box rgb(240,240,255) CI/CD Pipeline
        participant GH as 🔧 GitHub Actions
        participant K as 🔐 Secrets Manager
    end

    box rgb(255,240,230) Salesforce
        participant SF as ☁️ Salesforce
    end

    Note over GH,SF: JWT Bearer Flow for CI/CD

    GH->>K: 1. Retrieve private key
    K->>GH: 2. Return encrypted key

    GH->>GH: 3. Create JWT
    Note over GH: iss: consumer_key<br/>sub: deploy@company.com<br/>aud: login.salesforce.com

    GH->>GH: 4. Sign with private key

    GH->>SF: 5. POST /token (JWT assertion)

    SF->>SF: 6. Verify signature
    SF->>SF: 7. Validate claims

    SF->>GH: 8. Access token

    GH->>SF: 9. sf deploy start
    SF->>GH: 10. Deployment result
```

#### ASCII Fallback
```
┌───────────────────────┐     ┌────────────────────┐
│   GitHub Actions      │     │     Salesforce     │
│   (Private Key)       │     │   (Certificate)    │
└───────────┬───────────┘     └─────────┬──────────┘
            │                           │
            │  1. Create JWT            │
            │  2. Sign with key         │
            │                           │
            │  3. POST /token           │
            │──────────────────────────>│
            │                           │
            │  4. Verify signature      │
            │  5. Return access_token   │
            │<──────────────────────────│
            │                           │
            │  6. sf deploy start       │
            │──────────────────────────>│
```

### Score
```
Score: 72/80 ⭐⭐⭐⭐⭐ Excellent
├─ Accuracy: 20/20     ✓ All JWT Bearer steps correct
├─ Clarity: 18/20      ✓ Clear labels, good flow
├─ Completeness: 14/15 ✓ Includes CI/CD context
├─ Styling: 12/15      ✓ Proper theming
└─ Best Practices: 8/10 ✓ Good annotations
```

---

## Example 2: Data Model ERD

### Request
```
"Create an ERD for our custom Invoice system with Invoice__c, Invoice_Line_Item__c, and relationships to Account and Product"
```

### Generated Output

#### Mermaid Diagram
```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#00A1E0',
  'lineColor': '#706E6B'
}}}%%
erDiagram
    Account ||--o{ Invoice__c : "billed to"
    Account ||--o{ Contact : "has"
    Invoice__c ||--|{ Invoice_Line_Item__c : "contains"
    Product2 ||--o{ Invoice_Line_Item__c : "included in"

    Account {
        Id Id PK
        Text Name "Required"
        Text BillingStreet
        Text BillingCity
        Text BillingState
        Text BillingPostalCode
    }

    Contact {
        Id Id PK
        Lookup AccountId FK "Account"
        Text FirstName
        Text LastName "Required"
        Email Email
    }

    Invoice__c {
        Id Id PK
        AutoNumber Name "INV-00001"
        MasterDetail Account__c FK "Account"
        Lookup Billing_Contact__c FK "Contact"
        Date Invoice_Date__c "Required"
        Date Due_Date__c "Required"
        Picklist Status__c "Draft, Sent, Paid, Overdue"
        Currency Total_Amount__c "Roll-Up SUM"
        Currency Paid_Amount__c
        Formula Amount_Due__c "Total - Paid"
        Text External_Id__c UK "Integration Key"
    }

    Invoice_Line_Item__c {
        Id Id PK
        AutoNumber Name "LI-00001"
        MasterDetail Invoice__c FK "Invoice__c"
        Lookup Product__c FK "Product2"
        Number Quantity__c "Required"
        Currency Unit_Price__c "Required"
        Formula Line_Total__c "Qty × Price"
        TextArea Description__c
    }

    Product2 {
        Id Id PK
        Text Name "Required"
        Text ProductCode
        Currency UnitPrice
        Checkbox IsActive
    }
```

#### ASCII Fallback
```
┌─────────────────────────┐       ┌─────────────────────────┐
│        ACCOUNT          │       │        CONTACT          │
├─────────────────────────┤       ├─────────────────────────┤
│ Id (PK)                 │       │ Id (PK)                 │
│ Name (Required)         │──┐    │ AccountId (FK) ─────────│───┐
│ BillingStreet           │  │    │ FirstName               │   │
│ BillingCity             │  │    │ LastName (Required)     │   │
│ BillingState            │  │    │ Email                   │   │
│ BillingPostalCode       │  │    └─────────────────────────┘   │
└─────────────────────────┘  │                                  │
              │               │                                  │
              │ 1:N           └──────────────────────────────────┘
              ▼
┌─────────────────────────┐
│      INVOICE__C         │
├─────────────────────────┤
│ Id (PK)                 │
│ Name (Auto: INV-00001)  │
│ Account__c (MD)         │
│ Billing_Contact__c (LK) │
│ Invoice_Date__c (Req)   │
│ Due_Date__c (Req)       │
│ Status__c (Picklist)    │
│ Total_Amount__c (Roll)  │
│ Amount_Due__c (Formula) │
│ External_Id__c (UK)     │
└─────────────┬───────────┘
              │
              │ 1:N (Master-Detail)
              ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│  INVOICE_LINE_ITEM__C   │       │       PRODUCT2          │
├─────────────────────────┤       ├─────────────────────────┤
│ Id (PK)                 │       │ Id (PK)                 │
│ Name (Auto: LI-00001)   │       │ Name (Required)         │
│ Invoice__c (MD) ────────│──┘    │ ProductCode             │
│ Product__c (LK) ────────│──────>│ UnitPrice               │
│ Quantity__c (Req)       │       │ IsActive                │
│ Unit_Price__c (Req)     │       └─────────────────────────┘
│ Line_Total__c (Formula) │
│ Description__c          │
└─────────────────────────┘
```

### Score
```
Score: 74/80 ⭐⭐⭐⭐⭐ Excellent
├─ Accuracy: 20/20     ✓ All relationships correct
├─ Clarity: 19/20      ✓ Clear field annotations
├─ Completeness: 15/15 ✓ All objects included
├─ Styling: 13/15      ✓ Good layout
└─ Best Practices: 7/10  ⚠ Could add more field comments
```

---

## Example 3: Integration Sequence

### Request
```
"Diagram our real-time Order sync from Salesforce to SAP using Platform Events"
```

### Generated Output

#### Mermaid Diagram
```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'actorBkg': '#00A1E0',
  'actorTextColor': '#ffffff',
  'signalColor': '#032D60'
}}}%%
sequenceDiagram
    autonumber

    box rgb(255,240,230) Salesforce
        participant T as 🔄 Order Trigger
        participant PE as 📢 Order_Sync__e
    end

    box rgb(230,247,255) Integration
        participant MW as 🔄 MuleSoft
    end

    box rgb(240,255,240) SAP
        participant SAP as 🏭 SAP S/4HANA
    end

    Note over T,SAP: Real-time Order Sync (Platform Events)

    T->>T: 1. Order record saved
    Note over T: Status changed to 'Approved'

    T->>PE: 2. Publish Platform Event
    Note over T,PE: EventBus.publish(<br/>  new Order_Sync__e(<br/>    Order_Id__c,<br/>    Action__c='CREATE'<br/>  )<br/>)

    PE-)MW: 3. Event delivered (CometD)
    Note over PE,MW: /event/Order_Sync__e

    activate MW

    MW->>MW: 4. Transform to SAP format
    Note over MW: Map SF Order → SAP Sales Order

    MW->>SAP: 5. POST /sap/api/salesorders
    Note over MW,SAP: IDOC or REST API

    alt Success
        SAP->>MW: 6a. 201 Created
        Note over SAP,MW: SAP Order #: 4500012345

        MW->>PE: 7a. Publish confirmation
        Note over MW,PE: Order_Sync_Status__e<br/>Status='SUCCESS'

    else Validation Error
        SAP->>MW: 6b. 400 Bad Request
        Note over SAP,MW: Missing required field

        MW->>PE: 7b. Publish error
        Note over MW,PE: Order_Sync_Status__e<br/>Status='ERROR'
    end

    deactivate MW

    Note over T: Flow updates Order<br/>with SAP reference
```

### Score
```
Score: 70/80 ⭐⭐⭐⭐ Very Good
├─ Accuracy: 19/20     ✓ Platform Event pattern correct
├─ Clarity: 18/20      ✓ Good error handling shown
├─ Completeness: 13/15 ✓ Main paths covered
├─ Styling: 12/15      ✓ Good use of boxes
└─ Best Practices: 8/10 ✓ Shows async pattern
```

---

## Example 4: Combined Request

### Request
```
"I need to document our partner portal authentication.
Create: 1) The OAuth flow for partner login, 2) The data model showing Partner Account, Portal User, and Opportunities they can see"
```

### Generated Output

The skill generates two diagrams:

1. **OAuth Authorization Code + PKCE Flow** (for the portal)
2. **ERD showing Partner Access Model**

Both with Mermaid and ASCII versions.

---

## Tips for Best Results

1. **Be specific** - "JWT Bearer for CI/CD" is better than just "OAuth"
2. **Name your systems** - "Salesforce to SAP" produces clearer diagrams
3. **Mention custom objects** - Include `__c` suffix so we know they're custom
4. **Request both formats** - If you need ASCII fallback, mention it explicitly
