<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Filtered Extraction Examples
   2 
   3 Examples for extracting specific subsets of session tracing data.
   4 
   5 ---
   6 
   7 ## Filter by Agent
   8 
   9 ### Single Agent
  10 
  11 Extract only sessions handled by a specific agent:
  12 
  13 ```bash
  14 stdm-extract extract --org prod --agent Customer_Support_Agent
  15 ```
  16 
  17 ### Multiple Agents
  18 
  19 Extract sessions from multiple agents:
  20 
  21 ```bash
  22 stdm-extract extract --org prod \
  23     --agent Customer_Support_Agent \
  24     --agent Order_Tracking_Agent \
  25     --agent FAQ_Agent
  26 ```
  27 
  28 **Note:** Agent names are the **API Name** (e.g., `My_Agent`), not the label.
  29 
  30 ---
  31 
  32 ## Filter by Date Range
  33 
  34 ### Specific Start Date
  35 
  36 Extract from a specific date to now:
  37 
  38 ```bash
  39 stdm-extract extract --org prod --since 2026-01-15
  40 ```
  41 
  42 ### Date Range
  43 
  44 Extract a specific window:
  45 
  46 ```bash
  47 stdm-extract extract --org prod \
  48     --since 2026-01-01 \
  49     --until 2026-01-15
  50 ```
  51 
  52 ### ISO DateTime Format
  53 
  54 For precise timestamps:
  55 
  56 ```bash
  57 stdm-extract extract --org prod \
  58     --since "2026-01-15T00:00:00" \
  59     --until "2026-01-15T23:59:59"
  60 ```
  61 
  62 ---
  63 
  64 ## Combine Filters
  65 
  66 ### Agent + Date Range
  67 
  68 ```bash
  69 stdm-extract extract --org prod \
  70     --agent Customer_Support_Agent \
  71     --since 2026-01-01 \
  72     --until 2026-01-15 \
  73     --output ./data/jan-first-half
  74 ```
  75 
  76 ---
  77 
  78 ## Extract Specific Sessions
  79 
  80 ### Known Session IDs
  81 
  82 When you have specific session IDs to investigate:
  83 
  84 ```bash
  85 stdm-extract extract-tree --org prod \
  86     --session-ids "a0x001,a0x002,a0x003"
  87 ```
  88 
  89 This extracts the **complete tree** for each session:
  90 - Session record
  91 - All interactions (turns)
  92 - All steps (LLM and actions)
  93 - All messages
  94 
  95 ### From a File
  96 
  97 If you have session IDs in a file:
  98 
  99 ```bash
 100 # Session IDs file (one per line)
 101 cat session_ids.txt
 102 a0x001
 103 a0x002
 104 a0x003
 105 
 106 # Extract using command substitution
 107 stdm-extract extract-tree --org prod \
 108     --session-ids "$(cat session_ids.txt | tr '\n' ',')"
 109 ```
 110 
 111 ---
 112 
 113 ## Incremental Extraction
 114 
 115 ### First Run
 116 
 117 Extracts last 24 hours and saves watermark:
 118 
 119 ```bash
 120 stdm-extract extract-incremental --org prod
 121 ```
 122 
 123 **Creates:**
 124 - `~/.sf/observability/prod/watermark.json`
 125 - `./stdm_data/` (with 24h of data)
 126 
 127 ### Subsequent Runs
 128 
 129 Extracts only new data since last run:
 130 
 131 ```bash
 132 stdm-extract extract-incremental --org prod
 133 ```
 134 
 135 **Watermark file:**
 136 ```json
 137 {
 138   "last_run": "2026-01-28T10:15:23.000Z",
 139   "sessions_extracted": 1234
 140 }
 141 ```
 142 
 143 ### Force Full Re-extraction
 144 
 145 Delete the watermark to reset:
 146 
 147 ```bash
 148 rm ~/.sf/observability/prod/watermark.json
 149 stdm-extract extract-incremental --org prod  # Now extracts last 24h
 150 ```
 151 
 152 ---
 153 
 154 ## Production Workflow
 155 
 156 ### Daily Extraction Job
 157 
 158 ```bash
 159 #!/bin/bash
 160 # daily-extract.sh
 161 
 162 ORG="prod"
 163 OUTPUT_BASE="/data/agentforce"
 164 DATE=$(date +%Y-%m-%d)
 165 
 166 # Extract yesterday's data
 167 stdm-extract extract --org $ORG \
 168     --since "$(date -d 'yesterday' +%Y-%m-%d)" \
 169     --until "$DATE" \
 170     --output "$OUTPUT_BASE/$DATE" \
 171     --verbose 2>&1 | tee "$OUTPUT_BASE/logs/$DATE.log"
 172 ```
 173 
 174 ### Scheduled Incremental (Cron)
 175 
 176 ```bash
 177 # Run every hour, extract only new data
 178 0 * * * * /usr/local/bin/stdm-extract extract-incremental --org prod >> /var/log/stdm.log 2>&1
 179 ```
 180 
 181 ---
 182 
 183 ## Finding Agent Names
 184 
 185 If you're not sure of the exact agent API names:
 186 
 187 ### Option 1: Extract First, Then Filter
 188 
 189 ```bash
 190 # Extract all
 191 stdm-extract extract --org prod --days 1
 192 
 193 # Check agent names
 194 python3 -c "
 195 import polars as pl
 196 print(pl.read_parquet('./stdm_data/sessions/data.parquet')
 197     .select('ssot__AiAgentApiName__c')
 198     .unique()
 199 )
 200 "
 201 ```
 202 
 203 ### Option 2: Check in Salesforce
 204 
 205 1. **Setup** → **Agents**
 206 2. Click agent → **Details** tab
 207 3. Copy **API Name**
 208 
 209 ---
 210 
 211 ## Tips
 212 
 213 1. **Start small**: Test with `--days 1` before large extractions
 214 2. **Use incremental**: For ongoing monitoring, use `extract-incremental`
 215 3. **Separate outputs**: Use `--output` to organize by date or environment
 216 4. **Check counts first**: Use `count` command to estimate extraction size
 217 
 218 ---
 219 
 220 ## See Also
 221 
 222 - [Basic Extraction](basic-extraction.md) - Simple examples
 223 - [Analysis Examples](analysis-examples.md) - Analyze filtered data
 224 - [CLI Reference](../references/cli-reference.md) - All command options
