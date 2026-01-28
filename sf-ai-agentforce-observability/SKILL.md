---
name: sf-ai-agentforce-observability
description: >
  Extract and analyze Agentforce session tracing data from Salesforce Data Cloud.
  Supports high-volume extraction (1-10M records/day), Polars-based analysis,
  and debugging workflows for agent sessions.
license: MIT
compatibility: "Requires Data Cloud enabled org with Agentforce Session Tracing"
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
  data_model: "Session Tracing Data Model (STDM)"
  storage_format: "Parquet (via PyArrow)"
  analysis_library: "Polars"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/validate-extraction.py"
          timeout: 10000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-ai-agentforce-observability"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-ai-agentforce-observability"
      timeout: 5000
---

<!-- TIER: 1 | ENTRY POINT -->
<!-- This is the starting document - read this FIRST -->
<!-- Pattern: Follows sf-data for Python extraction scripts -->

# sf-ai-agentforce-observability: Agentforce Session Tracing Extraction & Analysis

Expert in extracting and analyzing Agentforce session tracing data from Salesforce Data Cloud. Supports high-volume data extraction (1-10M records/day), Parquet storage, and Polars-based analysis for debugging agent behavior.

## Core Responsibilities

1. **Session Extraction**: Extract STDM (Session Tracing Data Model) data via Data Cloud Query API
2. **Data Storage**: Write to Parquet format with PyArrow for efficient storage
3. **Analysis**: Polars-based lazy evaluation for memory-efficient analysis
4. **Debugging**: Session timeline reconstruction for troubleshooting agent issues
5. **Cross-Skill Integration**: Works with sf-connected-apps for auth, sf-ai-agentscript for fixes

## Document Map

| Need | Document | Description |
|------|----------|-------------|
| **Quick start** | [README.md](README.md) | Installation & basic usage |
| **Data model** | [resources/data-model-reference.md](resources/data-model-reference.md) | Full STDM schema documentation |
| **Query patterns** | [resources/query-patterns.md](resources/query-patterns.md) | Data Cloud SQL examples |
| **Analysis recipes** | [resources/analysis-cookbook.md](resources/analysis-cookbook.md) | Common Polars patterns |
| **CLI reference** | [docs/cli-reference.md](docs/cli-reference.md) | Complete command documentation |
| **Auth setup** | [docs/auth-setup.md](docs/auth-setup.md) | JWT Bearer configuration |
| **Troubleshooting** | [resources/troubleshooting.md](resources/troubleshooting.md) | Common issues & fixes |

**Quick Links:**
- [Data Model Overview](#session-tracing-data-model-stdm)
- [CLI Quick Reference](#cli-quick-reference)
- [Analysis Examples](#analysis-examples)
- [Cross-Skill Integration](#cross-skill-integration)

---

## CRITICAL: Prerequisites Checklist

Before extracting session data, verify:

| Check | How to Verify | Why |
|-------|---------------|-----|
| **Data Cloud enabled** | Setup → Data Cloud | Required for Query API |
| **Agentforce activated** | Setup → Agentforce | Generates session data |
| **Session Tracing enabled** | Agent Settings | Must be ON to collect data |
| **JWT Auth configured** | Use `sf-connected-apps` | Required for Data Cloud API |

### Auth Setup (via sf-connected-apps)

```bash
# 1. Generate certificate
openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 \
  -keyout ~/.sf/jwt/myorg.key \
  -out ~/.sf/jwt/myorg.crt \
  -subj "/CN=DataCloudAuth"

# 2. Create External Client App (use sf-connected-apps skill)
Skill(skill="sf-connected-apps", args="Create ECA with JWT Bearer for Data Cloud")

# Required scopes: cdp_query_api, cdp_profile_api
```

See [docs/auth-setup.md](docs/auth-setup.md) for detailed instructions.

---

## Session Tracing Data Model (STDM)

The STDM consists of 4 Data Model Objects (DMOs) in a hierarchical structure:

```
ssot__AIAgentSession__dlm (SESSION)
├── ssot__Id__c                          # Session ID
├── ssot__AIAgentApiName__c              # Agent API name
├── ssot__StartTimestamp__c              # Session start
├── ssot__EndTimestamp__c                # Session end
├── ssot__AIAgentSessionEndType__c       # End type (Completed, Abandoned, etc.)
├── ssot__RelatedMessagingSessionId__c   # Linked messaging session
└── ssot__OrganizationId__c              # Org ID

    └── ssot__AIAgentInteraction__dlm (TURN/SESSION_END)  [1:N]
        ├── ssot__Id__c                          # Interaction ID
        ├── ssot__aiAgentSessionId__c            # FK to Session
        ├── ssot__InteractionType__c             # TURN or SESSION_END
        ├── ssot__TopicApiName__c                # Topic that handled this turn
        ├── ssot__StartTimestamp__c              # Turn start
        └── ssot__EndTimestamp__c                # Turn end

            ├── ssot__AIAgentInteractionStep__dlm (STEP)  [1:N]
            │   ├── ssot__Id__c                          # Step ID
            │   ├── ssot__AIAgentInteractionId__c        # FK to Interaction
            │   ├── ssot__AIAgentInteractionStepType__c  # LLM_STEP or ACTION_STEP
            │   ├── ssot__Name__c                        # Action/step name
            │   ├── ssot__InputValueText__c              # Input to step
            │   ├── ssot__OutputValueText__c             # Output from step
            │   ├── ssot__PreStepVariableText__c         # Variables before
            │   ├── ssot__PostStepVariableText__c        # Variables after
            │   └── ssot__GenerationId__c                # LLM generation ID

            └── ssot__AIAgentMoment__dlm (MESSAGE)  [1:N]
                ├── ssot__Id__c                              # Message ID
                ├── ssot__AIAgentInteractionId__c            # FK to Interaction
                ├── ssot__ContentText__c                     # Message content
                ├── ssot__AIAgentInteractionMessageType__c   # INPUT or OUTPUT
                └── ssot__MessageSentTimestamp__c            # Timestamp
```

See [resources/data-model-reference.md](resources/data-model-reference.md) for full field documentation.

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:

| # | Question | Options |
|---|----------|---------|
| 1 | Target org | Org alias from `sf org list` |
| 2 | Time range | Last N days / Date range |
| 3 | Agent filter | All agents / Specific API names |
| 4 | Output format | Parquet (default) / CSV |
| 5 | Analysis type | Summary / Debug session / Full extraction |

### Phase 2: Auth Configuration

Verify JWT auth is configured:

```python
from scripts.auth import DataCloudAuth

auth = DataCloudAuth(
    org_alias="myorg",
    consumer_key="YOUR_CONSUMER_KEY"
)

# Test authentication
token = auth.get_token()
print(f"Auth successful: {token[:20]}...")
```

If auth fails, invoke:
```
Skill(skill="sf-connected-apps", args="Setup JWT Bearer for Data Cloud")
```

### Phase 3: Extraction

**Basic Extraction (last 7 days):**
```bash
python3 scripts/cli.py extract \
  --org prod \
  --days 7 \
  --output ./stdm_data
```

**Filtered Extraction:**
```bash
python3 scripts/cli.py extract \
  --org prod \
  --since 2026-01-01 \
  --until 2026-01-28 \
  --agent Customer_Support_Agent \
  --output ./stdm_data
```

**Session Tree (specific session):**
```bash
python3 scripts/cli.py extract-tree \
  --org prod \
  --session-id "a0x..." \
  --output ./debug_session
```

### Phase 4: Analysis

**Session Summary:**
```python
from scripts.analyzer import STDMAnalyzer
from pathlib import Path

analyzer = STDMAnalyzer(Path("./stdm_data"))

# High-level summary
summary = analyzer.session_summary()
print(summary)

# Step distribution by agent
steps = analyzer.step_distribution(agent_name="Customer_Support_Agent")
print(steps)

# Topic routing analysis
topics = analyzer.topic_analysis()
print(topics)
```

**Debug Specific Session:**
```bash
python3 scripts/cli.py debug-session \
  --data-dir ./stdm_data \
  --session-id "a0x..."
```

### Phase 5: Integration & Next Steps

Based on analysis findings:

| Finding | Next Step | Skill |
|---------|-----------|-------|
| Topic mismatch | Improve topic descriptions | `sf-ai-agentscript` |
| Action failures | Debug Flow/Apex | `sf-flow`, `sf-debug` |
| Slow responses | Optimize actions | `sf-apex` |
| Missing coverage | Add test cases | `sf-ai-agentforce-testing` |

---

## CLI Quick Reference

### Extraction Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `extract` | Extract session data | `extract --org prod --days 7` |
| `extract-tree` | Extract full session tree | `extract-tree --org prod --session-id "a0x..."` |
| `extract-incremental` | Resume from last run | `extract-incremental --org prod` |

### Analysis Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `analyze` | Generate summary stats | `analyze --data-dir ./stdm_data` |
| `debug-session` | Timeline view | `debug-session --session-id "a0x..."` |
| `topics` | Topic analysis | `topics --data-dir ./stdm_data` |

### Common Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--org` | Target org alias | Required |
| `--days` | Last N days | 7 |
| `--since` | Start date (YYYY-MM-DD) | - |
| `--until` | End date (YYYY-MM-DD) | Today |
| `--agent` | Filter by agent API name | All |
| `--output` | Output directory | `./stdm_data` |
| `--verbose` | Detailed logging | False |
| `--format` | Output format (table/json/csv) | table |

See [docs/cli-reference.md](docs/cli-reference.md) for complete documentation.

---

## Analysis Examples

### Session Summary

```
📊 SESSION SUMMARY
════════════════════════════════════════════════════════════════

Period: 2026-01-21 to 2026-01-28
Total Sessions: 15,234
Unique Agents: 3

SESSIONS BY AGENT
────────────────────────────────────────────────────────────────
Agent                          │ Sessions │ Avg Turns │ Avg Duration
───────────────────────────────┼──────────┼───────────┼─────────────
Customer_Support_Agent         │   8,502  │    4.2    │     3m 15s
Order_Tracking_Agent           │   4,128  │    2.8    │     1m 45s
Product_FAQ_Agent              │   2,604  │    1.9    │       45s

END TYPE DISTRIBUTION
────────────────────────────────────────────────────────────────
✅ Completed:    12,890 (84.6%)
🔄 Escalated:     1,523 (10.0%)
❌ Abandoned:       821 (5.4%)
```

### Debug Session Timeline

```
🔍 SESSION DEBUG: a0x1234567890ABC
════════════════════════════════════════════════════════════════

Agent: Customer_Support_Agent
Started: 2026-01-28 10:15:23 UTC
Duration: 4m 32s
End Type: Completed
Turns: 5

TIMELINE
────────────────────────────────────────────────────────────────
10:15:23 │ [INPUT]  "I need help with my order #12345"
10:15:24 │ [TOPIC]  → Order_Tracking (confidence: 0.95)
10:15:24 │ [STEP]   LLM_STEP: Identify intent
10:15:25 │ [STEP]   ACTION_STEP: Get_Order_Status
         │          Input: {"orderId": "12345"}
         │          Output: {"status": "Shipped", "eta": "2026-01-30"}
10:15:26 │ [OUTPUT] "Your order #12345 has shipped and will arrive by Jan 30."

10:16:01 │ [INPUT]  "Can I change the delivery address?"
10:16:02 │ [TOPIC]  → Order_Tracking (same topic)
10:16:02 │ [STEP]   LLM_STEP: Clarify request
10:16:03 │ [STEP]   ACTION_STEP: Check_Modification_Eligibility
         │          Input: {"orderId": "12345", "type": "address_change"}
         │          Output: {"eligible": false, "reason": "Already shipped"}
10:16:04 │ [OUTPUT] "I'm sorry, the order has already shipped..."
```

---

## Cross-Skill Integration

### Prerequisite Skills

| Skill | When | How to Invoke |
|-------|------|---------------|
| `sf-connected-apps` | Auth setup | `Skill(skill="sf-connected-apps", args="JWT Bearer for Data Cloud")` |

### Follow-up Skills

| Finding | Skill | How to Invoke |
|---------|-------|---------------|
| Topic routing issues | `sf-ai-agentscript` | `Skill(skill="sf-ai-agentscript", args="Fix topic: [issue]")` |
| Action failures | `sf-flow` / `sf-debug` | `Skill(skill="sf-debug", args="Analyze agent action failure")` |
| Test coverage gaps | `sf-ai-agentforce-testing` | `Skill(skill="sf-ai-agentforce-testing", args="Add test cases")` |

### Commonly Used With

| Skill | Use Case | Confidence |
|-------|----------|------------|
| `sf-ai-agentscript` | Fix agent based on trace analysis | ⭐⭐⭐ Required |
| `sf-ai-agentforce-testing` | Create test cases from observed patterns | ⭐⭐ Recommended |
| `sf-debug` | Deep-dive into action failures | ⭐⭐ Recommended |

---

## Key Insights

| Insight | Description | Action |
|---------|-------------|--------|
| **STDM is read-only** | Data Cloud stores traces; cannot modify | Use for analysis only |
| **Session lag** | Data may lag 5-15 minutes | Don't expect real-time |
| **Volume limits** | Query API: 10M records/day | Use incremental extraction |
| **Parquet efficiency** | 10x smaller than JSON | Always use Parquet for storage |
| **Lazy evaluation** | Polars scans without loading | Handles 100M+ rows |

---

## Common Issues & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | JWT auth expired/invalid | Refresh token or reconfigure ECA |
| `No session data` | Tracing not enabled | Enable Session Tracing in Agent Settings |
| `Query timeout` | Too much data | Add date filters, use incremental |
| `Memory error` | Loading all data | Use Polars lazy frames |
| `Missing DMO` | Wrong API version | Use API v60.0+ |

See [resources/troubleshooting.md](resources/troubleshooting.md) for detailed solutions.

---

## Output Directory Structure

After extraction:

```
stdm_data/
├── sessions/
│   └── date=2026-01-28/
│       └── part-0000.parquet
├── interactions/
│   └── date=2026-01-28/
│       └── part-0000.parquet
├── steps/
│   └── date=2026-01-28/
│       └── part-0000.parquet
├── messages/
│   └── date=2026-01-28/
│       └── part-0000.parquet
└── metadata/
    ├── extraction.json      # Extraction parameters
    └── watermark.json       # For incremental extraction
```

---

## Dependencies

**Python 3.10+** with:

```
polars>=1.0.0           # DataFrame library (lazy evaluation)
pyarrow>=15.0.0         # Parquet support
pyjwt>=2.8.0            # JWT generation
cryptography>=42.0.0    # Certificate handling
httpx>=0.27.0           # HTTP client
rich>=13.0.0            # CLI progress bars
click>=8.1.0            # CLI framework
pydantic>=2.6.0         # Data validation
```

Install: `pip install -r requirements.txt`

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
