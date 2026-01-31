# sf-ai-agentforce-observability

![Status: GA](https://img.shields.io/badge/Status-GA-brightgreen)
![Tests: 233 Passed](https://img.shields.io/badge/Tests-233%20Passed-success)
![Validation: Live API Tested](https://img.shields.io/badge/Validation-Live%20API%20Tested-blue)

Extract and analyze Agentforce session tracing data from Salesforce Data Cloud (Data 360).

## Status: General Availability (GA)

This skill has been validated against live Salesforce orgs and is production-ready.

| Metric | Value |
|--------|-------|
| **Test Coverage** | 233 tests across 6 tiers |
| **Live API Validation** | All SQL patterns tested against Data Cloud |
| **Schema Accuracy** | Verified column names match actual API |
| **Last Validated** | January 2026 (Vivint-DevInt) |

## Features

- **High-Volume Extraction**: Handle 1-10M records/day via Data Cloud Query API
- **Parquet Storage**: Efficient columnar storage (10x smaller than JSON)
- **Polars Analysis**: Lazy evaluation for memory-efficient analysis of 100M+ rows
- **Session Debugging**: Reconstruct session timelines for troubleshooting
- **Incremental Sync**: Watermark-based extraction for continuous monitoring
- **GenAI Quality Analysis**: Extract Trust Layer metrics (toxicity, adherence, resolution)

## Quick Start

### 1. Prerequisites

```bash
# Install Python dependencies
pip install polars pyarrow pyjwt cryptography httpx rich click pydantic

# Verify Data Cloud access
sf org display --target-org myorg
```

### 2. Configure Authentication

Session tracing extraction requires JWT Bearer auth to the Data Cloud Query API.

```bash
# Generate certificate
openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 \
  -keyout ~/.sf/jwt/myorg.key \
  -out ~/.sf/jwt/myorg.crt \
  -subj "/CN=DataCloudAuth"

# Create External Client App (via sf-connected-apps skill)
# Required scopes: cdp_query_api, cdp_profile_api
```

See [docs/auth-setup.md](docs/auth-setup.md) for detailed instructions.

### 3. Extract Session Data

```bash
# Extract last 7 days
python3 scripts/cli.py extract --org myorg --days 7 --output ./data

# Extract specific date range
python3 scripts/cli.py extract --org myorg --since 2026-01-01 --until 2026-01-15

# Extract complete session tree for debugging
python3 scripts/cli.py extract-tree --org myorg --session-id "a0x..."
```

### 4. Analyze Data

```bash
# Session summary
python3 scripts/cli.py analyze --data-dir ./data

# Debug specific session
python3 scripts/cli.py debug-session --data-dir ./data --session-id "a0x..."

# Topic analysis
python3 scripts/cli.py topics --data-dir ./data

# Extract GenAI quality metrics
python3 scripts/cli.py extract-quality --data-dir ./data
```

### 5. Use with Python

```python
from scripts.analyzer import STDMAnalyzer
from pathlib import Path

analyzer = STDMAnalyzer(Path("./data"))

# Session summary
print(analyzer.session_summary())

# Step distribution
print(analyzer.step_distribution())

# Message timeline for debugging
print(analyzer.message_timeline("a0x..."))
```

## Data Model

The Session Tracing Data Model (STDM) consists of 4 core DMOs plus GenAI quality DMOs:

```
AIAgentSession (Session)
├── AIAgentSessionParticipant (Participants)
├── AIAgentInteraction (Turn)
│   ├── AIAgentInteractionStep (LLM/Action Step)
│   │   └── → GenAIGeneration (LLM Output)
│   │       └── GenAIContentQuality (Trust Layer)
│   │           └── GenAIContentCategory (Toxicity/Adherence/Resolution)
│   └── AIAgentInteractionMessage (Raw Messages)
└── AIAgentMoment (Summaries)
```

**Important**: Data Cloud uses `AiAgent` (lowercase 'i') in column names, not `AIAgent`.

See [resources/data-model-reference.md](resources/data-model-reference.md) for full schema.

## Output Format

Data is stored in Parquet format:

```
stdm_data/
├── sessions/data.parquet
├── interactions/data.parquet
├── steps/data.parquet
├── messages/data.parquet
├── generations/data.parquet        # GenAI quality
├── content_quality/data.parquet    # Trust Layer
├── content_categories/data.parquet # Toxicity/Adherence
└── metadata/
    ├── extraction.json
    └── watermark.json
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `extract` | Extract session data for time range |
| `extract-tree` | Extract full tree for specific session |
| `extract-incremental` | Continue from last extraction |
| `extract-quality` | Extract GenAI Trust Layer metrics |
| `analyze` | Generate summary statistics |
| `debug-session` | Show session timeline |
| `topics` | Topic routing analysis |
| `count` | Count records per DMO |

See [docs/cli-reference.md](docs/cli-reference.md) for all options.

## Validation

This skill includes comprehensive validation testing:

| Tier | Category | Tests | Description |
|------|----------|-------|-------------|
| T1 | Auth & Connectivity | 5 | JWT auth, API access, DMO existence |
| T2 | Extraction Commands | 35 | CLI extract, tree, incremental |
| T3 | Analysis Commands | 46 | Analyze, debug-session, topics |
| T4 | Schema/Documentation | 96 | Field validation, query patterns |
| T5 | Negative Cases | 12 | Error handling, invalid args |
| T6 | **Live SQL Execution** | 39 | All SQL patterns against live API |

**Total: 233 tests | 100% pass rate**

Run validation:
```bash
cd validation
source .venv/bin/activate
pytest scenarios/ -v --org YourOrgAlias
```

## Integration with Other Skills

| Skill | Use Case |
|-------|----------|
| `sf-connected-apps` | Set up JWT Bearer auth |
| `sf-ai-agentscript` | Fix agents based on trace analysis |
| `sf-ai-agentforce-testing` | Create tests from observed patterns |
| `sf-debug` | Deep-dive into action failures |

## Requirements

- Python 3.10+
- Salesforce org with Data Cloud and Agentforce enabled
- Session Tracing enabled in Agentforce settings
- JWT Bearer auth configured (via External Client App)
- Salesforce Standard Data Model v1.124+

## Resources

- [Data Model Reference](resources/data-model-reference.md) - Full STDM schema
- [Query Patterns](resources/query-patterns.md) - SQL examples for Data Cloud
- [Analysis Cookbook](resources/analysis-cookbook.md) - Polars analysis patterns
- [Polars Cheatsheet](docs/polars-cheatsheet.md) - Quick reference

## License

MIT License - See [LICENSE](LICENSE) file.

## Author

Jag Valaiyapathy

---

*Last updated: January 2026 | Validated against: Vivint-DevInt*
