# Salesforce ERD Template

Entity Relationship Diagram template for visualizing Salesforce data models.

## When to Use
- Documenting object relationships
- Planning data model changes
- Understanding existing schema
- Design reviews and architecture discussions

## sf-metadata Integration

When connected to an org, query object definitions:

```
Skill(skill="sf-metadata")
Request: "Describe objects: Account, Contact, Opportunity, Case"
```

This returns:
- Field names and types
- Lookup/Master-Detail relationships
- Required fields
- External IDs

## Mermaid Template - Standard Sales Cloud

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#00A1E0',
  'primaryTextColor': '#032D60',
  'lineColor': '#706E6B',
  'tertiaryColor': '#f0f0f0'
}}}%%
erDiagram
    Account ||--o{ Contact : "has many"
    Account ||--o{ Opportunity : "has many"
    Account ||--o{ Case : "has many"
    Account ||--o{ Account : "parent of"

    Account {
        Id Id PK "18-char Salesforce ID"
        Text Name "Required, max 255"
        Lookup ParentId FK "Account (Self)"
        Lookup OwnerId FK "User"
        Picklist Industry
        Picklist Type
        Currency AnnualRevenue
        Phone Phone
        Text BillingCity
        Text BillingState
        Text BillingCountry
        DateTime CreatedDate
        DateTime LastModifiedDate
    }

    Contact {
        Id Id PK
        Lookup AccountId FK "Account"
        Lookup OwnerId FK "User"
        Lookup ReportsToId FK "Contact (Self)"
        Text FirstName
        Text LastName "Required"
        Email Email
        Phone Phone
        Phone MobilePhone
        Text Title
        Date Birthdate
        DateTime CreatedDate
    }

    Opportunity ||--o{ OpportunityLineItem : "contains"
    Opportunity ||--o{ OpportunityContactRole : "involves"
    Contact ||--o{ OpportunityContactRole : "plays role"

    Opportunity {
        Id Id PK
        Lookup AccountId FK "Account"
        Lookup OwnerId FK "User"
        Text Name "Required"
        Picklist StageName "Required"
        Date CloseDate "Required"
        Currency Amount
        Number Probability
        Picklist LeadSource
        Picklist Type
        Text NextStep
        DateTime CreatedDate
    }

    OpportunityContactRole {
        Id Id PK
        MasterDetail OpportunityId FK "Opportunity"
        Lookup ContactId FK "Contact"
        Picklist Role
        Checkbox IsPrimary
    }

    Product2 ||--o{ PricebookEntry : "priced in"
    Pricebook2 ||--o{ PricebookEntry : "contains"
    PricebookEntry ||--o{ OpportunityLineItem : "used in"

    Product2 {
        Id Id PK
        Text Name "Required"
        Text ProductCode
        Text Description
        Checkbox IsActive "Required"
        Text Family
    }

    Pricebook2 {
        Id Id PK
        Text Name "Required"
        Checkbox IsActive
        Checkbox IsStandard
    }

    PricebookEntry {
        Id Id PK
        Lookup Product2Id FK "Product2"
        Lookup Pricebook2Id FK "Pricebook2"
        Currency UnitPrice "Required"
        Checkbox IsActive
    }

    OpportunityLineItem {
        Id Id PK
        MasterDetail OpportunityId FK "Opportunity"
        Lookup PricebookEntryId FK "PricebookEntry"
        Number Quantity "Required"
        Currency UnitPrice
        Currency TotalPrice
        Text Description
    }

    Case {
        Id Id PK
        Lookup AccountId FK "Account"
        Lookup ContactId FK "Contact"
        Lookup OwnerId FK "User, Queue"
        Lookup ParentId FK "Case (Self)"
        Text Subject
        TextArea Description
        Picklist Status "Required"
        Picklist Priority
        Picklist Origin
        Picklist Type
        Checkbox IsClosed
        DateTime ClosedDate
    }

    User ||--o{ Account : "owns"
    User ||--o{ Contact : "owns"
    User ||--o{ Opportunity : "owns"
    User ||--o{ Case : "owns/assigned"

    User {
        Id Id PK
        Text Username "Required, Unique"
        Text FirstName
        Text LastName "Required"
        Email Email "Required"
        Checkbox IsActive
        Lookup ProfileId FK "Profile"
        Lookup UserRoleId FK "UserRole"
    }
```

## ASCII Fallback Template

```
┌─────────────────────────────┐
│          ACCOUNT            │
├─────────────────────────────┤
│ Id (PK)                     │
│ Name (Required)             │
│ ParentId (FK → Account)     │──────────────────┐
│ OwnerId (FK → User)         │                  │
│ Industry                    │                  │
│ Type                        │                  │
│ AnnualRevenue               │                  │
└─────────────┬───────────────┘                  │
              │                                   │
              │ 1:N                               │
              ▼                                   │
┌─────────────────────────────┐                  │
│          CONTACT            │                  │
├─────────────────────────────┤                  │
│ Id (PK)                     │                  │
│ AccountId (FK → Account) ───│──────────────────┘
│ OwnerId (FK → User)         │
│ ReportsToId (FK → Contact)  │───┐
│ FirstName                   │   │
│ LastName (Required)         │   │ Self-reference
│ Email                       │<──┘
│ Phone                       │
└─────────────────────────────┘

              │
              │ N:M (via junction)
              ▼

┌─────────────────────────────┐     ┌─────────────────────────────┐
│  OPPORTUNITY_CONTACT_ROLE   │     │        OPPORTUNITY          │
├─────────────────────────────┤     ├─────────────────────────────┤
│ Id (PK)                     │     │ Id (PK)                     │
│ OpportunityId (FK) ─────────│────>│ AccountId (FK → Account)    │
│ ContactId (FK → Contact)    │     │ OwnerId (FK → User)         │
│ Role                        │     │ Name (Required)             │
│ IsPrimary                   │     │ StageName (Required)        │
└─────────────────────────────┘     │ CloseDate (Required)        │
                                    │ Amount                      │
                                    └─────────────┬───────────────┘
                                                  │
                                                  │ 1:N
                                                  ▼
                                    ┌─────────────────────────────┐
                                    │    OPPORTUNITY_LINE_ITEM    │
                                    ├─────────────────────────────┤
                                    │ Id (PK)                     │
                                    │ OpportunityId (FK)          │
                                    │ PricebookEntryId (FK)       │
                                    │ Quantity (Required)         │
                                    │ UnitPrice                   │
                                    │ TotalPrice                  │
                                    └─────────────────────────────┘
```

## Cardinality Notation

| Symbol | Meaning | Salesforce Equivalent |
|--------|---------|----------------------|
| `\|\|` | Exactly one | Required Lookup |
| `\|o` | Zero or one | Optional Lookup |
| `o{` | Zero or many | Child objects |
| `\|{` | One or many | Required children |

## Relationship Types

```mermaid
erDiagram
    %% Master-Detail (cascade delete)
    Parent ||--o{ Child_MasterDetail : "owns (MD)"

    %% Lookup (no cascade)
    Parent ||--o{ Child_Lookup : "references (LK)"

    %% Self-Referential
    Employee ||--o{ Employee : "manages"

    %% Junction Object (Many-to-Many)
    TableA ||--o{ Junction : "linked via"
    TableB ||--o{ Junction : "linked via"
```

## Salesforce Field Type Mapping

| Salesforce Type | ERD Type | Example |
|-----------------|----------|---------|
| Id | Id | `Id Id PK` |
| Text | Text | `Text Name` |
| Text Area | TextArea | `TextArea Description` |
| Number | Number | `Number Quantity` |
| Currency | Currency | `Currency Amount` |
| Percent | Percent | `Percent Probability` |
| Checkbox | Checkbox | `Checkbox IsActive` |
| Date | Date | `Date CloseDate` |
| DateTime | DateTime | `DateTime CreatedDate` |
| Picklist | Picklist | `Picklist Status` |
| Multi-Picklist | MultiPicklist | `MultiPicklist Industries` |
| Email | Email | `Email Email` |
| Phone | Phone | `Phone Phone` |
| URL | URL | `URL Website` |
| Lookup | Lookup | `Lookup AccountId FK "Account"` |
| Master-Detail | MasterDetail | `MasterDetail AccountId FK "Account"` |
| Formula | Formula | `Formula FullName` |
| Roll-Up Summary | RollUp | `RollUp TotalAmount` |

## Custom Object Example

```mermaid
erDiagram
    Account ||--o{ Invoice__c : "has many"
    Invoice__c ||--o{ Invoice_Line_Item__c : "contains"
    Product2 ||--o{ Invoice_Line_Item__c : "sold as"

    Invoice__c {
        Id Id PK
        Text Name "Auto-Number"
        MasterDetail Account__c FK "Account"
        Lookup Contact__c FK "Contact"
        Date Invoice_Date__c "Required"
        Date Due_Date__c
        Picklist Status__c "Draft/Sent/Paid"
        Currency Total_Amount__c "Roll-Up"
        Currency Paid_Amount__c
        Formula Amount_Due__c "Total - Paid"
        Text External_Id__c UK "Integration Key"
    }

    Invoice_Line_Item__c {
        Id Id PK
        Text Name "Auto-Number"
        MasterDetail Invoice__c FK "Invoice__c"
        Lookup Product__c FK "Product2"
        Number Quantity__c "Required"
        Currency Unit_Price__c
        Formula Line_Total__c "Qty * Price"
        Text Description__c
    }
```

## Best Practices

1. **Use API Names** - Show `Account__c` not "Custom Account"
2. **Mark Required Fields** - Add "Required" notation
3. **Show Relationship Type** - MD vs Lookup distinction matters
4. **Include Key Fields Only** - Don't overcrowd; focus on relationships
5. **Group Related Objects** - Use visual proximity

## Generating from sf-metadata

When sf-metadata returns object info, map to ERD:

```javascript
// Example mapping
{
  "name": "Account",
  "fields": [
    { "name": "Id", "type": "id" },
    { "name": "Name", "type": "string", "nillable": false },
    { "name": "ParentId", "type": "reference", "referenceTo": ["Account"] }
  ]
}

// Becomes:
// Account {
//     Id Id PK
//     Text Name "Required"
//     Lookup ParentId FK "Account"
// }
```

## Customization Points

- Add custom objects by following the pattern
- Include only relevant fields (not all 200+ standard fields)
- Use comments `%% Comment` for notes
- Adjust layout by reordering entities
