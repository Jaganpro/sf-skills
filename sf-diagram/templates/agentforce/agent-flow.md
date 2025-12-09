# Agentforce Flow Diagram Template

Flowchart template for visualizing Agentforce agent architecture and conversation flows.

## When to Use
- Documenting Agentforce agent structure
- Planning agent topics and actions
- Visualizing conversation flows
- Architecture reviews

## Mermaid Template - Agent Structure

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#00A1E0',
  'primaryTextColor': '#ffffff',
  'primaryBorderColor': '#032D60',
  'lineColor': '#706E6B'
}}}%%
flowchart TB
    subgraph agent[🤖 Service Agent]
        direction TB

        DESC[/"Agent Description:<br/>AI-powered customer service<br/>assistant for order management"/]

        subgraph topics[📋 Topics]
            direction LR
            T1[Order Status]
            T2[Return Request]
            T3[Product Info]
            T4[Escalation]
        end

        subgraph instructions[📝 Instructions]
            I1[Greet professionally]
            I2[Verify customer identity]
            I3[Use knowledge base first]
            I4[Escalate if frustrated]
        end
    end

    subgraph topic_order[📦 Topic: Order Status]
        direction TB
        TO_DESC[/"Help customers check<br/>order and shipping status"/]
        TO_SCOPE[Scope: Order tracking,<br/>delivery estimates]

        subgraph to_actions[Actions]
            TO_A1[Get Order Details<br/>⚡ Apex]
            TO_A2[Check Shipping<br/>🔄 Flow]
        end
    end

    subgraph topic_return[🔄 Topic: Return Request]
        direction TB
        TR_DESC[/"Process return and<br/>refund requests"/]
        TR_SCOPE[Scope: Returns, refunds,<br/>exchanges]

        subgraph tr_actions[Actions]
            TR_A1[Create Case<br/>🔄 Flow]
            TR_A2[Generate Label<br/>⚡ Apex]
            TR_A3[Process Refund<br/>⚡ Apex]
        end
    end

    %% Connections
    T1 --> topic_order
    T2 --> topic_return

    TO_A1 --> ORDER_SVC[Order Service]
    TO_A2 --> SHIP_API[Shipping API]

    TR_A1 --> CASE_OBJ[(Case Object)]
    TR_A2 --> SHIP_API
    TR_A3 --> PAY_API[Payment API]

    %% Styling
    classDef topic fill:#9050E9,color:#fff,stroke:#032D60
    classDef action fill:#04844B,color:#fff,stroke:#032D60
    classDef external fill:#FF6D00,color:#fff,stroke:#032D60

    class T1,T2,T3,T4 topic
    class TO_A1,TO_A2,TR_A1,TR_A2,TR_A3 action
    class ORDER_SVC,SHIP_API,PAY_API,CASE_OBJ external
```

## Mermaid Template - Conversation Flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#00A1E0'
}}}%%
flowchart TD
    START([🟢 Conversation Start])

    START --> GREET[Greet Customer]
    GREET --> CLASSIFY{Classify Intent}

    CLASSIFY -->|Order Related| ORDER_TOPIC
    CLASSIFY -->|Return Related| RETURN_TOPIC
    CLASSIFY -->|General Question| KB_SEARCH
    CLASSIFY -->|Unknown| CLARIFY

    subgraph ORDER_TOPIC[📦 Order Status Topic]
        ORD_1[Ask for Order Number]
        ORD_2[Retrieve Order Details<br/>⚡ GetOrderDetails Action]
        ORD_3{Order Found?}
        ORD_4[Display Status]
        ORD_5[Offer Additional Help]

        ORD_1 --> ORD_2 --> ORD_3
        ORD_3 -->|Yes| ORD_4 --> ORD_5
        ORD_3 -->|No| ORD_1
    end

    subgraph RETURN_TOPIC[🔄 Return Request Topic]
        RET_1[Verify Order Eligible]
        RET_2{Eligible for Return?}
        RET_3[Create Return Case<br/>🔄 CreateReturnCase Action]
        RET_4[Generate Return Label<br/>⚡ GenerateLabel Action]
        RET_5[Provide Instructions]
        RET_6[Explain Policy]

        RET_1 --> RET_2
        RET_2 -->|Yes| RET_3 --> RET_4 --> RET_5
        RET_2 -->|No| RET_6
    end

    KB_SEARCH[Search Knowledge Base<br/>📚 Knowledge Action]
    KB_SEARCH --> KB_RESULT{Found Answer?}
    KB_RESULT -->|Yes| PROVIDE_ANSWER[Provide Answer]
    KB_RESULT -->|No| ESCALATE

    CLARIFY[Ask Clarifying Question]
    CLARIFY --> CLASSIFY

    ESCALATE[Escalate to Human<br/>👤 Transfer Action]

    ORD_5 --> SATISFIED{Customer Satisfied?}
    RET_5 --> SATISFIED
    PROVIDE_ANSWER --> SATISFIED

    SATISFIED -->|Yes| END_SUCCESS([🟢 End - Resolved])
    SATISFIED -->|No| ESCALATE

    ESCALATE --> END_TRANSFER([🟡 End - Transferred])

    %% Styling
    classDef start fill:#2E844A,color:#fff
    classDef end_good fill:#2E844A,color:#fff
    classDef end_transfer fill:#FE9339,color:#fff
    classDef decision fill:#9050E9,color:#fff
    classDef action fill:#00A1E0,color:#fff

    class START start
    class END_SUCCESS end_good
    class END_TRANSFER end_transfer
    class CLASSIFY,ORD_3,RET_2,KB_RESULT,SATISFIED decision
```

## ASCII Fallback Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🤖 SERVICE AGENT STRUCTURE                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: Customer Service Bot                                                │
│  ─────────────────────────────                                              │
│  Description: AI-powered assistant for order and return inquiries           │
│                                                                             │
│  Instructions:                                                              │
│  • Greet customers professionally                                           │
│  • Verify identity before sharing order details                             │
│  • Search knowledge base before escalating                                  │
│  • Escalate if customer expresses frustration                               │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  📋 TOPICS                                                                  │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐       │
│  │  📦 Order Status  │  │ 🔄 Return Request │  │  ❓ General Help  │       │
│  │                   │  │                   │  │                   │       │
│  │  Scope:           │  │  Scope:           │  │  Scope:           │       │
│  │  - Track orders   │  │  - Process return │  │  - FAQ answers    │       │
│  │  - Delivery ETA   │  │  - Generate label │  │  - Knowledge base │       │
│  │  - Order history  │  │  - Refund status  │  │  - Escalation     │       │
│  └─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘       │
└────────────│──────────────────────│──────────────────────│──────────────────┘
             │                      │                      │
             ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚡ ACTIONS                                                                 │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐       │
│  │ GetOrderDetails   │  │ CreateReturnCase  │  │ SearchKnowledge   │       │
│  │ [Apex Invocable]  │  │ [Flow]            │  │ [Standard Action] │       │
│  ├───────────────────┤  ├───────────────────┤  ├───────────────────┤       │
│  │ Input:            │  │ Input:            │  │ Input:            │       │
│  │ - orderNumber     │  │ - orderId         │  │ - query           │       │
│  │ - customerId      │  │ - reason          │  │ - language        │       │
│  │                   │  │ - quantity        │  │                   │       │
│  │ Output:           │  │ Output:           │  │ Output:           │       │
│  │ - status          │  │ - caseId          │  │ - articles[]      │       │
│  │ - items[]         │  │ - returnLabel     │  │ - confidence      │       │
│  │ - trackingUrl     │  │ - instructions    │  │                   │       │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
             │                      │                      │
             ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔗 INTEGRATIONS                                                            │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐       │
│  │   Order Service   │  │   Shipping API    │  │  Knowledge Base   │       │
│  │   (Salesforce)    │  │   (FedEx/UPS)     │  │   (Salesforce)    │       │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Agent Components

| Component | Description | Example |
|-----------|-------------|---------|
| Agent | The AI assistant container | Service Agent, SDR Agent |
| Topic | Conversation category | Order Status, Returns |
| Action | Executable capability | Apex method, Flow |
| Instruction | Behavioral guideline | "Always verify identity" |
| Scope | Topic boundaries | What's in/out of scope |

## Action Types

| Type | Icon | Use Case |
|------|------|----------|
| Apex Invocable | ⚡ | Complex logic, callouts |
| Flow | 🔄 | Record creation, updates |
| Standard | 📚 | Knowledge search, case creation |
| Prompt Template | 💬 | Dynamic response generation |

## Conversation Flow Patterns

### 1. Linear Flow
```
Start → Topic → Action → Response → End
```

### 2. Branching Flow
```
Start → Classify → [Topic A | Topic B | Escalate]
```

### 3. Loop Back
```
Start → Topic → Action → Validate → [Success | Retry]
```

## Best Practices

1. **Clear topic boundaries** - Don't overlap scope
2. **Minimal actions per topic** - 3-5 max
3. **Always have escalation path** - Human handoff
4. **Use knowledge base first** - Before custom actions
5. **Verify before acting** - Confirm understanding

## Customization Points

- Replace example topics with actual use cases
- Add specific action inputs/outputs
- Include actual integration endpoints
- Show conversation sample flows
