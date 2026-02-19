<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # CLI Reference
   2 
   3 Complete command reference for the `stdm-extract` CLI tool.
   4 
   5 ## Global Options
   6 
   7 | Option | Description |
   8 |--------|-------------|
   9 | `--help` | Show help message and exit |
  10 | `--version` | Show version number |
  11 
  12 ---
  13 
  14 ## Commands
  15 
  16 ### `extract`
  17 
  18 Extract session tracing data for a date range.
  19 
  20 ```bash
  21 stdm-extract extract --org <alias> [options]
  22 ```
  23 
  24 **Options:**
  25 
  26 | Option | Type | Default | Description |
  27 |--------|------|---------|-------------|
  28 | `--org` | String | Required | Salesforce org alias (from `sf org list`) |
  29 | `--consumer-key` | String | `$SF_CONSUMER_KEY` | ECA consumer key |
  30 | `--days` | Integer | 7 | Extract last N days |
  31 | `--since` | DateTime | None | Start date (ISO format) |
  32 | `--until` | DateTime | Now | End date (ISO format) |
  33 | `--agent` | String | None | Filter by agent API name (repeatable) |
  34 | `--output` | Path | `./stdm_data` | Output directory |
  35 | `--verbose` | Flag | False | Enable verbose logging |
  36 
  37 **Examples:**
  38 
  39 ```bash
  40 # Last 7 days for all agents
  41 stdm-extract extract --org prod
  42 
  43 # Specific date range
  44 stdm-extract extract --org prod --since 2026-01-01 --until 2026-01-15
  45 
  46 # Filter by agent
  47 stdm-extract extract --org prod --agent Customer_Support_Agent
  48 
  49 # Multiple agents
  50 stdm-extract extract --org prod --agent Agent1 --agent Agent2
  51 ```
  52 
  53 ---
  54 
  55 ### `extract-tree`
  56 
  57 Extract complete session tree for specific session IDs.
  58 
  59 ```bash
  60 stdm-extract extract-tree --org <alias> --session-ids <ids> [options]
  61 ```
  62 
  63 **Options:**
  64 
  65 | Option | Type | Default | Description |
  66 |--------|------|---------|-------------|
  67 | `--org` | String | Required | Salesforce org alias |
  68 | `--consumer-key` | String | `$SF_CONSUMER_KEY` | ECA consumer key |
  69 | `--session-ids` | String | Required | Comma-separated session IDs |
  70 | `--output` | Path | `./stdm_data` | Output directory |
  71 | `--verbose` | Flag | False | Enable verbose logging |
  72 
  73 **Example:**
  74 
  75 ```bash
  76 stdm-extract extract-tree --org prod --session-ids "a0x001,a0x002,a0x003"
  77 ```
  78 
  79 ---
  80 
  81 ### `extract-incremental`
  82 
  83 Incremental extraction based on last run timestamp.
  84 
  85 ```bash
  86 stdm-extract extract-incremental --org <alias> [options]
  87 ```
  88 
  89 **Options:**
  90 
  91 | Option | Type | Default | Description |
  92 |--------|------|---------|-------------|
  93 | `--org` | String | Required | Salesforce org alias |
  94 | `--consumer-key` | String | `$SF_CONSUMER_KEY` | ECA consumer key |
  95 | `--output` | Path | `./stdm_data` | Output directory |
  96 | `--verbose` | Flag | False | Enable verbose logging |
  97 
  98 **Notes:**
  99 - Watermark stored at `~/.sf/observability/{org}/watermark.json`
 100 - First run extracts last 24 hours
 101 - Subsequent runs extract since last watermark
 102 
 103 **Example:**
 104 
 105 ```bash
 106 # First run: extracts last 24 hours
 107 stdm-extract extract-incremental --org prod
 108 
 109 # Subsequent runs: extracts only new data
 110 stdm-extract extract-incremental --org prod
 111 ```
 112 
 113 ---
 114 
 115 ### `analyze`
 116 
 117 Generate summary statistics from extracted data.
 118 
 119 ```bash
 120 stdm-extract analyze --data-dir <path> [options]
 121 ```
 122 
 123 **Options:**
 124 
 125 | Option | Type | Default | Description |
 126 |--------|------|---------|-------------|
 127 | `--data-dir` | Path | Required | Directory containing Parquet files |
 128 | `--format` | Choice | `table` | Output format: `table`, `json`, `csv` |
 129 
 130 **Example:**
 131 
 132 ```bash
 133 stdm-extract analyze --data-dir ./stdm_data --format table
 134 ```
 135 
 136 ---
 137 
 138 ### `debug-session`
 139 
 140 Debug a specific session with full message timeline.
 141 
 142 ```bash
 143 stdm-extract debug-session --data-dir <path> --session-id <id> [options]
 144 ```
 145 
 146 **Options:**
 147 
 148 | Option | Type | Default | Description |
 149 |--------|------|---------|-------------|
 150 | `--data-dir` | Path | Required | Directory containing Parquet files |
 151 | `--session-id` | String | Required | Session ID to debug |
 152 | `--verbose` | Flag | False | Show step details (LLM, actions) |
 153 | `--output` | Path | None | Export timeline to JSON |
 154 
 155 **Example:**
 156 
 157 ```bash
 158 # View timeline in terminal
 159 stdm-extract debug-session --data-dir ./stdm_data --session-id "a0x123"
 160 
 161 # Export to JSON with full details
 162 stdm-extract debug-session --data-dir ./stdm_data --session-id "a0x123" \
 163     --verbose --output ./debug/session.json
 164 ```
 165 
 166 ---
 167 
 168 ### `topics`
 169 
 170 Analyze topic routing patterns.
 171 
 172 ```bash
 173 stdm-extract topics --data-dir <path> [options]
 174 ```
 175 
 176 **Options:**
 177 
 178 | Option | Type | Default | Description |
 179 |--------|------|---------|-------------|
 180 | `--data-dir` | Path | Required | Directory containing Parquet files |
 181 | `--format` | Choice | `table` | Output format: `table`, `json` |
 182 
 183 **Example:**
 184 
 185 ```bash
 186 stdm-extract topics --data-dir ./stdm_data
 187 ```
 188 
 189 ---
 190 
 191 ### `actions`
 192 
 193 Analyze action invocation patterns.
 194 
 195 ```bash
 196 stdm-extract actions --data-dir <path> [options]
 197 ```
 198 
 199 **Options:**
 200 
 201 | Option | Type | Default | Description |
 202 |--------|------|---------|-------------|
 203 | `--data-dir` | Path | Required | Directory containing Parquet files |
 204 | `--agent` | String | None | Filter by agent API name |
 205 | `--format` | Choice | `table` | Output format: `table`, `json` |
 206 
 207 **Example:**
 208 
 209 ```bash
 210 stdm-extract actions --data-dir ./stdm_data --agent Customer_Support_Agent
 211 ```
 212 
 213 ---
 214 
 215 ### `count`
 216 
 217 Count records in Data Cloud (quick check without extraction).
 218 
 219 ```bash
 220 stdm-extract count --org <alias> [options]
 221 ```
 222 
 223 **Options:**
 224 
 225 | Option | Type | Default | Description |
 226 |--------|------|---------|-------------|
 227 | `--org` | String | Required | Salesforce org alias |
 228 | `--consumer-key` | String | `$SF_CONSUMER_KEY` | ECA consumer key |
 229 | `--dmo` | Choice | `sessions` | DMO to count |
 230 
 231 **Example:**
 232 
 233 ```bash
 234 stdm-extract count --org prod --dmo sessions
 235 ```
 236 
 237 ---
 238 
 239 ### `test-auth`
 240 
 241 Test authentication to Data Cloud.
 242 
 243 ```bash
 244 stdm-extract test-auth --org <alias> [options]
 245 ```
 246 
 247 **Options:**
 248 
 249 | Option | Type | Default | Description |
 250 |--------|------|---------|-------------|
 251 | `--org` | String | Required | Salesforce org alias |
 252 | `--consumer-key` | String | `$SF_CONSUMER_KEY` | ECA consumer key |
 253 
 254 **Example:**
 255 
 256 ```bash
 257 stdm-extract test-auth --org prod
 258 ```
 259 
 260 ---
 261 
 262 ## Environment Variables
 263 
 264 | Variable | Description |
 265 |----------|-------------|
 266 | `SF_CONSUMER_KEY` | Default consumer key for ECA |
 267 | `SF_JWT_KEY_PATH` | Override JWT private key location (default: `~/.sf/jwt/{org}.key`) |
 268 
 269 ---
 270 
 271 ## Exit Codes
 272 
 273 | Code | Meaning |
 274 |------|---------|
 275 | 0 | Success |
 276 | 1 | General error |
 277 | 2 | Authentication failed |
 278 | 3 | Data not found |
 279 | 4 | Invalid arguments |
 280 
 281 ---
 282 
 283 ## See Also
 284 
 285 - [Auth Setup](auth-setup.md) - Setting up JWT authentication
 286 - [Polars Cheatsheet](polars-cheatsheet.md) - Quick analysis commands
 287 - [Troubleshooting](../references/troubleshooting.md) - Common issues
