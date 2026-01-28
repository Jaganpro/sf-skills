# sf-ai-agentforce-observability

Extract and analyze Agentforce session tracing data from Salesforce Data Cloud.

## Features

- **High-Volume Extraction**: Handle 1-10M records/day via Data Cloud Query API
- **Parquet Storage**: Efficient columnar storage (10x smaller than JSON)
- **Polars Analysis**: Lazy evaluation for memory-efficient analysis of 100M+ rows
- **Session Debugging**: Reconstruct session timelines for troubleshooting
- **Incremental Sync**: Watermark-based extraction for continuous monitoring

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

# Extract for specific agent
python3 scripts/cli.py extract --org myorg --agent Customer_Support_Agent
```

### 4. Analyze Data

```bash
# Session summary
python3 scripts/cli.py analyze --data-dir ./data

# Debug specific session
python3 scripts/cli.py debug-session --data-dir ./data --session-id "a0x..."

# Topic analysis
python3 scripts/cli.py topics --data-dir ./data
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

The Session Tracing Data Model (STDM) consists of 4 DMOs:

```
AIAgentSession (Session)
└── AIAgentInteraction (Turn)
    ├── AIAgentInteractionStep (LLM/Action Step)
    └── AIAgentMoment (Message)
```

See [resources/data-model-reference.md](resources/data-model-reference.md) for full schema.

## Output Format

Data is stored in Parquet format with date partitioning:

```
stdm_data/
├── sessions/date=YYYY-MM-DD/*.parquet
├── interactions/date=YYYY-MM-DD/*.parquet
├── steps/date=YYYY-MM-DD/*.parquet
└── messages/date=YYYY-MM-DD/*.parquet
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `extract` | Extract session data for time range |
| `extract-tree` | Extract full tree for specific session |
| `extract-incremental` | Continue from last extraction |
| `analyze` | Generate summary statistics |
| `debug-session` | Show session timeline |
| `topics` | Topic routing analysis |

See [docs/cli-reference.md](docs/cli-reference.md) for all options.

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

## License

MIT License - See [LICENSE](LICENSE) file.

## Author

Jag Valaiyapathy
