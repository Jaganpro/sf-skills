<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Basic Extraction Examples
   2 
   3 Simple examples to get started with STDM extraction.
   4 
   5 ## Prerequisites
   6 
   7 1. JWT authentication configured (see [Auth Setup](../references/auth-setup.md))
   8 2. Consumer key set: `export SF_CONSUMER_KEY="3MVG9..."`
   9 3. Org alias available in `sf org list`
  10 
  11 ---
  12 
  13 ## Example 1: Extract Last 7 Days
  14 
  15 The simplest extraction - all sessions from the last 7 days:
  16 
  17 ```bash
  18 stdm-extract extract --org prod
  19 ```
  20 
  21 **Output structure:**
  22 ```
  23 ./stdm_data/
  24 ├── sessions/
  25 │   └── data.parquet
  26 ├── interactions/
  27 │   └── data.parquet
  28 ├── steps/
  29 │   └── data.parquet
  30 └── messages/
  31     └── data.parquet
  32 ```
  33 
  34 ---
  35 
  36 ## Example 2: Extract Last 24 Hours
  37 
  38 ```bash
  39 stdm-extract extract --org prod --days 1
  40 ```
  41 
  42 ---
  43 
  44 ## Example 3: Custom Output Directory
  45 
  46 ```bash
  47 stdm-extract extract --org prod --output /data/agentforce/prod
  48 ```
  49 
  50 ---
  51 
  52 ## Example 4: Verbose Mode
  53 
  54 See detailed progress and timing:
  55 
  56 ```bash
  57 stdm-extract extract --org prod --verbose
  58 ```
  59 
  60 **Sample output:**
  61 ```
  62 🔐 Authenticating to Data Cloud...
  63    Instance URL: https://myorg.my.salesforce.com
  64 
  65 📊 Extracting sessions...
  66    Query: SELECT ... FROM ssot__AIAgentSession__dlm WHERE ...
  67    Records: 1,234 (2.3s)
  68 
  69 📊 Extracting interactions...
  70    Records: 5,678 (4.1s)
  71 
  72 📊 Extracting steps...
  73    Records: 12,345 (8.7s)
  74 
  75 📊 Extracting messages...
  76    Records: 9,876 (5.2s)
  77 
  78 ✅ Extraction complete!
  79    Total records: 29,133
  80    Duration: 20.3s
  81    Output: ./stdm_data/
  82 ```
  83 
  84 ---
  85 
  86 ## Example 5: Test Authentication First
  87 
  88 Before extracting, verify your setup:
  89 
  90 ```bash
  91 stdm-extract test-auth --org prod
  92 ```
  93 
  94 **Success:**
  95 ```
  96 ✅ Authentication successful
  97    Instance URL: https://myorg.my.salesforce.com
  98    Token valid for: 3599 seconds
  99 ```
 100 
 101 **Failure:**
 102 ```
 103 ❌ Authentication failed
 104    Error: invalid_grant
 105    Hint: Check certificate expiration with:
 106          openssl x509 -enddate -noout -in ~/.sf/jwt/prod.key
 107 ```
 108 
 109 ---
 110 
 111 ## Example 6: Count Records Before Extraction
 112 
 113 Check how much data exists without downloading:
 114 
 115 ```bash
 116 stdm-extract count --org prod --dmo sessions
 117 ```
 118 
 119 **Output:**
 120 ```
 121 📊 Record counts for prod:
 122    Sessions: 12,345
 123 ```
 124 
 125 ---
 126 
 127 ## Example 7: Extract from Sandbox
 128 
 129 Works the same as production - just use the sandbox alias:
 130 
 131 ```bash
 132 # List your orgs
 133 sf org list
 134 
 135 # Extract from sandbox
 136 stdm-extract extract --org mysandbox --days 3
 137 ```
 138 
 139 ---
 140 
 141 ## What's Next?
 142 
 143 - [Filtered Extraction](filtered-extraction.md) - Filter by agent, date range
 144 - [Analysis Examples](analysis-examples.md) - Analyze extracted data
 145 - [Debugging Sessions](debugging-sessions.md) - Debug specific sessions
 146 
 147 ---
 148 
 149 ## Quick Reference
 150 
 151 | Task | Command |
 152 |------|---------|
 153 | Last 7 days | `stdm-extract extract --org prod` |
 154 | Last N days | `stdm-extract extract --org prod --days N` |
 155 | Test auth | `stdm-extract test-auth --org prod` |
 156 | Check counts | `stdm-extract count --org prod` |
 157 | Verbose mode | Add `--verbose` to any command |
