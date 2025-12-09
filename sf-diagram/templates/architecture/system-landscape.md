# System Landscape Diagram Template

Flowchart template for visualizing high-level Salesforce system architecture.

## When to Use
- Architecture overview presentations
- Integration landscape documentation
- System inventory
- Stakeholder communication

## Mermaid Template - Sales Cloud Integration Landscape

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#00A1E0',
  'primaryTextColor': '#ffffff',
  'primaryBorderColor': '#032D60',
  'lineColor': '#706E6B',
  'secondaryColor': '#FF6D00',
  'tertiaryColor': '#04844B'
}}}%%
flowchart TB
    subgraph users[👥 Users]
        direction LR
        U1[Sales Reps<br/>📱 Mobile]
        U2[Managers<br/>💻 Desktop]
        U3[Partners<br/>🌐 Portal]
    end

    subgraph salesforce[☁️ Salesforce Platform]
        direction TB

        subgraph core[Core CRM]
            SF1[(Sales Cloud)]
            SF2[(Service Cloud)]
            SF3[(Experience Cloud)]
        end

        subgraph automation[Automation]
            FL[Flows]
            AP[Apex]
            PE[Platform Events]
        end

        subgraph ai[AI & Analytics]
            EIN[Einstein]
            TB[Tableau]
            CRM[CRM Analytics]
        end
    end

    subgraph integration[🔄 Integration Layer]
        direction LR
        MW[MuleSoft<br/>Anypoint]
        API[API Gateway]
    end

    subgraph external[🏢 External Systems]
        direction TB

        subgraph erp[ERP]
            SAP[SAP S/4HANA]
            NET[NetSuite]
        end

        subgraph marketing[Marketing]
            MC[Marketing Cloud]
            PAR[Pardot]
        end

        subgraph data[Data & Storage]
            DW[Data Warehouse<br/>Snowflake]
            S3[AWS S3]
        end
    end

    %% User connections
    U1 -->|Salesforce Mobile| SF1
    U2 -->|Lightning| SF1
    U2 -->|Lightning| SF2
    U3 -->|Portal| SF3

    %% Internal SF connections
    SF1 <--> FL
    SF2 <--> FL
    FL <--> AP
    AP <--> PE

    SF1 --> EIN
    SF1 --> TB
    SF2 --> CRM

    %% Integration connections
    PE --> MW
    AP <--> API
    MW <--> API

    %% External connections
    API <-->|REST/SOAP| SAP
    API <-->|REST| NET
    MW <-->|CDC| MC
    MW --> PAR
    MW -->|ETL| DW
    API -->|Files| S3

    %% Styling
    classDef salesforce fill:#00A1E0,color:#fff,stroke:#032D60
    classDef external fill:#04844B,color:#fff,stroke:#032D60
    classDef integration fill:#FF6D00,color:#fff,stroke:#032D60
    classDef user fill:#9050E9,color:#fff,stroke:#032D60

    class SF1,SF2,SF3,FL,AP,PE,EIN,TB,CRM salesforce
    class SAP,NET,MC,PAR,DW,S3 external
    class MW,API integration
    class U1,U2,U3 user
```

## Mermaid Template - Agentforce Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#00A1E0'
}}}%%
flowchart TB
    subgraph channels[📱 Channels]
        WEB[Web Chat]
        SMS[SMS]
        WHATS[WhatsApp]
        SLACK[Slack]
    end

    subgraph agentforce[🤖 Agentforce]
        direction TB

        subgraph agents[AI Agents]
            SA[Service Agent]
            SDA[SDR Agent]
            COACH[Sales Coach]
        end

        subgraph topics[Topics & Actions]
            T1[Order Status]
            T2[Return Request]
            T3[Lead Qualify]
            A1[Apex Actions]
            A2[Flow Actions]
        end

        subgraph foundation[Foundation]
            DM[Data Cloud]
            TRUST[Trust Layer]
            PROMPT[Prompt Builder]
        end
    end

    subgraph backend[⚙️ Backend]
        APEX[Apex Services]
        FLOW[Flow Orchestration]
        INT[Integrations]
    end

    subgraph data[💾 Data Sources]
        CRM[(CRM Data)]
        EXT[(External Data)]
        KB[(Knowledge Base)]
    end

    %% Channel to Agent
    WEB --> SA
    SMS --> SA
    WHATS --> SA
    SLACK --> SDA
    SLACK --> COACH

    %% Agent to Topics
    SA --> T1
    SA --> T2
    SDA --> T3

    %% Topics to Actions
    T1 --> A1
    T2 --> A2
    T3 --> A1

    %% Foundation connections
    agents --> DM
    agents --> TRUST
    topics --> PROMPT

    %% Backend connections
    A1 --> APEX
    A2 --> FLOW
    APEX --> INT

    %% Data connections
    DM --> CRM
    DM --> EXT
    TRUST --> KB
```

## ASCII Fallback Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM LANDSCAPE                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  👥 USERS                                                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│  │  Sales Reps   │  │   Managers    │  │   Partners    │                   │
│  │  (Mobile)     │  │  (Desktop)    │  │   (Portal)    │                   │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘                   │
└──────────│──────────────────│──────────────────│────────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ☁️ SALESFORCE PLATFORM                                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  CORE CRM                                                              │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │ │
│  │  │ Sales Cloud │  │Service Cloud│  │ Experience  │                    │ │
│  │  │             │  │             │  │   Cloud     │                    │ │
│  │  └──────┬──────┘  └──────┬──────┘  └─────────────┘                    │ │
│  └─────────│────────────────│────────────────────────────────────────────┘ │
│            │                │                                               │
│  ┌─────────▼────────────────▼────────────────────────────────────────────┐ │
│  │  AUTOMATION                                                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │ │
│  │  │    Flows    │──│    Apex     │──│  Platform   │                    │ │
│  │  │             │  │             │  │   Events    │                    │ │
│  │  └─────────────┘  └──────┬──────┘  └──────┬──────┘                    │ │
│  └──────────────────────────│────────────────│───────────────────────────┘ │
└─────────────────────────────│────────────────│──────────────────────────────┘
                              │                │
                              ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔄 INTEGRATION LAYER                                                       │
│  ┌─────────────────────────┐  ┌─────────────────────────┐                  │
│  │       MuleSoft          │  │      API Gateway        │                  │
│  │      Anypoint           │──│                         │                  │
│  └───────────┬─────────────┘  └───────────┬─────────────┘                  │
└──────────────│────────────────────────────│─────────────────────────────────┘
               │                            │
               ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏢 EXTERNAL SYSTEMS                                                        │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │        ERP          │  │      Marketing      │  │    Data Storage     │ │
│  │  ┌───────┬───────┐  │  │  ┌───────┬───────┐  │  │  ┌───────┬───────┐  │ │
│  │  │  SAP  │NetSuit│  │  │  │  MC   │Pardot │  │  │  │Snowflk│  S3   │  │ │
│  │  └───────┴───────┘  │  │  └───────┴───────┘  │  │  └───────┴───────┘  │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Types

| Category | Examples | Icon |
|----------|----------|------|
| Users | Sales, Service, Partners | 👥 |
| Salesforce Clouds | Sales, Service, Marketing | ☁️ |
| Automation | Flow, Apex, Events | ⚡ |
| AI/Analytics | Einstein, Tableau, CRM Analytics | 🧠 |
| Integration | MuleSoft, API Gateway | 🔄 |
| External Systems | ERP, Marketing, Data | 🏢 |
| Storage | Database, Data Lake, Files | 💾 |

## Connection Types

| Pattern | Description | Arrow |
|---------|-------------|-------|
| Sync Request/Response | REST API call | `<-->` |
| Async (Event-based) | Platform Events, CDC | `-->` |
| Batch/ETL | Scheduled data load | `-->` (dashed) |
| Real-time streaming | CometD, Pub/Sub | `==>` |

## Customization Points

- Replace example systems with actual integrations
- Add or remove clouds based on implementation
- Include specific API names and versions
- Show data flow direction and volumes
