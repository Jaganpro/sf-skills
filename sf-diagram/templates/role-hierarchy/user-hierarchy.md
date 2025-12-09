# Role Hierarchy Diagram Template

Flowchart template for visualizing Salesforce role hierarchies and permission structures.

## When to Use
- Documenting org security model
- Planning role hierarchy changes
- Explaining data access patterns
- Security review presentations

## Mermaid Template - Sales Role Hierarchy

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#00A1E0',
  'primaryTextColor': '#ffffff',
  'primaryBorderColor': '#032D60',
  'lineColor': '#706E6B'
}}}%%
flowchart TB
    subgraph legend[📋 Legend]
        direction LR
        L1[Role]
        L2([Profile])
        L3{{Permission Set}}
    end

    CEO[CEO]

    subgraph sales[Sales Organization]
        direction TB
        VP_SALES[VP of Sales]

        subgraph regions[Regional Directors]
            direction LR
            DIR_WEST[Director - West]
            DIR_EAST[Director - East]
            DIR_CENTRAL[Director - Central]
        end

        subgraph managers[Sales Managers]
            direction LR
            MGR_W1[Manager - SF]
            MGR_W2[Manager - LA]
            MGR_E1[Manager - NYC]
            MGR_E2[Manager - Boston]
            MGR_C1[Manager - Chicago]
            MGR_C2[Manager - Dallas]
        end

        subgraph reps[Sales Representatives]
            direction LR
            REP_W[West Reps<br/>12 users]
            REP_E[East Reps<br/>15 users]
            REP_C[Central Reps<br/>10 users]
        end
    end

    subgraph service[Service Organization]
        direction TB
        VP_SVC[VP of Service]

        SVC_MGR[Service Manager]

        subgraph agents[Service Agents]
            direction LR
            AGENT_T1[Tier 1 Support<br/>20 users]
            AGENT_T2[Tier 2 Support<br/>8 users]
        end
    end

    %% Hierarchy connections
    CEO --> VP_SALES
    CEO --> VP_SVC

    VP_SALES --> DIR_WEST
    VP_SALES --> DIR_EAST
    VP_SALES --> DIR_CENTRAL

    DIR_WEST --> MGR_W1
    DIR_WEST --> MGR_W2
    DIR_EAST --> MGR_E1
    DIR_EAST --> MGR_E2
    DIR_CENTRAL --> MGR_C1
    DIR_CENTRAL --> MGR_C2

    MGR_W1 --> REP_W
    MGR_W2 --> REP_W
    MGR_E1 --> REP_E
    MGR_E2 --> REP_E
    MGR_C1 --> REP_C
    MGR_C2 --> REP_C

    VP_SVC --> SVC_MGR
    SVC_MGR --> AGENT_T1
    SVC_MGR --> AGENT_T2

    %% Styling
    classDef exec fill:#032D60,color:#fff,stroke:#032D60
    classDef director fill:#0176D3,color:#fff,stroke:#032D60
    classDef manager fill:#00A1E0,color:#fff,stroke:#032D60
    classDef rep fill:#1B96FF,color:#fff,stroke:#032D60

    class CEO exec
    class VP_SALES,VP_SVC,DIR_WEST,DIR_EAST,DIR_CENTRAL director
    class MGR_W1,MGR_W2,MGR_E1,MGR_E2,MGR_C1,MGR_C2,SVC_MGR manager
    class REP_W,REP_E,REP_C,AGENT_T1,AGENT_T2 rep
```

## Mermaid Template - Profile & Permission Set Structure

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#00A1E0'
}}}%%
flowchart TB
    subgraph profiles[📋 Profiles - Base Access]
        direction LR
        P_ADMIN([System Admin])
        P_SALES([Sales User])
        P_SVC([Service User])
        P_MKTG([Marketing User])
        P_PARTNER([Partner Community])
    end

    subgraph psets[🔐 Permission Sets - Additive]
        direction TB

        subgraph functional[Functional Permissions]
            PS_API{{API Access}}
            PS_REPORTS{{Advanced Reports}}
            PS_FLOW{{Flow Admin}}
        end

        subgraph feature[Feature Permissions]
            PS_CPQ{{CPQ User}}
            PS_EINSTEIN{{Einstein Analytics}}
            PS_INBOX{{Sales Engagement}}
        end

        subgraph object[Object Permissions]
            PS_INVOICE{{Invoice Manager}}
            PS_CONTRACT{{Contract Editor}}
            PS_PRODUCT{{Product Admin}}
        end
    end

    subgraph groups[👥 Permission Set Groups]
        direction LR
        PSG_SALES_FULL{{Sales Full Access}}
        PSG_SVC_FULL{{Service Full Access}}
    end

    %% Profile assignments
    P_SALES --> PSG_SALES_FULL
    P_SVC --> PSG_SVC_FULL

    %% Group composition
    PS_API --> PSG_SALES_FULL
    PS_CPQ --> PSG_SALES_FULL
    PS_EINSTEIN --> PSG_SALES_FULL
    PS_INBOX --> PSG_SALES_FULL

    PS_API --> PSG_SVC_FULL
    PS_REPORTS --> PSG_SVC_FULL

    %% Styling
    classDef profile fill:#9050E9,color:#fff
    classDef pset fill:#04844B,color:#fff
    classDef group fill:#FF6D00,color:#fff

    class P_ADMIN,P_SALES,P_SVC,P_MKTG,P_PARTNER profile
    class PS_API,PS_REPORTS,PS_FLOW,PS_CPQ,PS_EINSTEIN,PS_INBOX,PS_INVOICE,PS_CONTRACT,PS_PRODUCT pset
    class PSG_SALES_FULL,PSG_SVC_FULL group
```

## ASCII Fallback Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ROLE HIERARCHY                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                                   ┌─────────┐
                                   │   CEO   │
                                   └────┬────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
             ┌──────▼──────┐                        ┌──────▼──────┐
             │ VP of Sales │                        │ VP of Svc   │
             └──────┬──────┘                        └──────┬──────┘
                    │                                      │
     ┌──────────────┼──────────────┐              ┌────────▼────────┐
     │              │              │              │ Service Manager │
     ▼              ▼              ▼              └────────┬────────┘
┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│Director │  │Director │  │Director │          ┌──────────┼──────────┐
│  West   │  │  East   │  │ Central │          ▼          ▼          │
└────┬────┘  └────┬────┘  └────┬────┘    ┌─────────┐ ┌─────────┐    │
     │            │            │         │ Tier 1  │ │ Tier 2  │    │
     ▼            ▼            ▼         │ Support │ │ Support │    │
┌─────────┐ ┌─────────┐ ┌─────────┐      │ (20)    │ │  (8)    │    │
│Manager  │ │Manager  │ │Manager  │      └─────────┘ └─────────┘    │
│SF | LA  │ │NYC|BOS  │ │CHI|DAL  │                                 │
└────┬────┘ └────┬────┘ └────┬────┘                                 │
     │           │           │                                       │
     ▼           ▼           ▼                                       │
┌─────────┐ ┌─────────┐ ┌─────────┐                                 │
│ West    │ │ East    │ │ Central │                                 │
│ Reps    │ │ Reps    │ │ Reps    │                                 │
│  (12)   │ │  (15)   │ │  (10)   │                                 │
└─────────┘ └─────────┘ └─────────┘                                 │

┌─────────────────────────────────────────────────────────────────────────────┐
│  DATA ACCESS FLOW                                                           │
│  ─────────────────                                                          │
│  • Roles ABOVE can see records owned by roles BELOW                         │
│  • CEO sees ALL sales and service data                                      │
│  • VP Sales sees all sales data, NOT service data                           │
│  • Managers see only their team's records                                   │
│  • Reps see only their own records                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Security Components

| Component | Purpose | Shape |
|-----------|---------|-------|
| Role | Data visibility hierarchy | Rectangle |
| Profile | Base object/field access | Rounded |
| Permission Set | Additive permissions | Hexagon |
| Permission Set Group | Bundle of perm sets | Hexagon (orange) |

## Data Access Patterns

### OWD (Organization-Wide Defaults)

| Setting | Meaning |
|---------|---------|
| Private | Owner + hierarchy above |
| Public Read Only | All can view |
| Public Read/Write | All can edit |
| Controlled by Parent | Inherits from master |

### Sharing Rules

```mermaid
flowchart LR
    OWD[OWD: Private]
    SHARE[Sharing Rule]
    APEX[Apex Sharing]

    OWD --> SHARE --> APEX

    subgraph access[Access Expansion]
        ROLE[Role-based]
        CRITERIA[Criteria-based]
        MANUAL[Manual]
    end

    SHARE --> access
```

## Best Practices

1. **Minimize role levels** - 3-5 levels max
2. **Use Permission Set Groups** - Easier to manage
3. **Document exceptions** - Note any sharing rules
4. **Show user counts** - Understand scale
5. **Include profiles** - Show base access

## Customization Points

- Replace example roles with actual org structure
- Add specific user counts
- Include custom permission sets
- Show sharing rule exceptions
