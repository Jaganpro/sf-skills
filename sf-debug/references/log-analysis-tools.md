<!-- Parent: sf-debug/SKILL.md -->
   1 # Log Analysis Tools
   2 
   3 This guide covers tools for analyzing Salesforce debug logs, with a focus on performance profiling and bottleneck identification.
   4 
   5 ---
   6 
   7 ## Recommended: Apex Log Analyzer (VS Code)
   8 
   9 The **Apex Log Analyzer** is a free VS Code extension that provides visual analysis of Apex debug logs.
  10 
  11 ### Installation
  12 
  13 ```
  14 1. Open VS Code
  15 2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
  16 3. Search "Apex Log Analyzer"
  17 4. Install "Apex Log Analyzer" by FinancialForce
  18 ```
  19 
  20 Or install via command line:
  21 ```bash
  22 code --install-extension FinancialForce.lana
  23 ```
  24 
  25 ### Key Features
  26 
  27 | Feature | Description | Use Case |
  28 |---------|-------------|----------|
  29 | **Flame Charts** | Visual execution timeline | Find slow methods at a glance |
  30 | **Call Tree** | Hierarchical method calls | Trace execution paths |
  31 | **Database Analysis** | SOQL/DML highlighting | Find query hotspots |
  32 | **Timeline View** | Execution over time | See parallel operations |
  33 | **Limit Summary** | Governor limit usage | Quick health check |
  34 
  35 ### How to Use
  36 
  37 1. **Get a debug log**:
  38    ```bash
  39    sf apex get log --log-id 07Lxx0000000000 --target-org my-sandbox -o debug.log
  40    ```
  41 
  42 2. **Open in VS Code**:
  43    - Open the `.log` file
  44    - Click "Analyze Log" button in the editor toolbar
  45    - Or use Command Palette: "Apex Log: Analyze Log"
  46 
  47 3. **Navigate the visualization**:
  48    - **Flame Chart**: Wider bars = more time spent
  49    - **Click methods** to see details
  50    - **Hover** for exact timing
  51    - **Filter** to focus on specific operations
  52 
  53 ### Reading Flame Charts
  54 
  55 ```
  56 ┌─────────────────────────────────────────────────────────────┐
  57 │ FLAME CHART INTERPRETATION                                   │
  58 ├─────────────────────────────────────────────────────────────┤
  59 │                                                              │
  60 │  ████████████████████████████████████  AccountTrigger       │
  61 │    ██████████████████  AccountService.processAccounts       │
  62 │      ██████████  ← BOTTLENECK: Wide bar = slow operation    │
  63 │        ████  SOQL query                                      │
  64 │      ████████████  Another slow method                       │
  65 │                                                              │
  66 │  Time flows left → right                                     │
  67 │  Width = execution time                                      │
  68 │  Stack depth = call hierarchy                                │
  69 │                                                              │
  70 └─────────────────────────────────────────────────────────────┘
  71 ```
  72 
  73 **Bottleneck Indicators**:
  74 - Wide bars at lower levels (deep in call stack)
  75 - Multiple identical bars (repeated operations)
  76 - SOQL/DML bars inside loop patterns
  77 
  78 ---
  79 
  80 ## SF CLI Debug Commands
  81 
  82 ### List Available Logs
  83 
  84 ```bash
  85 # List recent logs
  86 sf apex list log --target-org my-sandbox --json
  87 
  88 # Output includes:
  89 # - Log ID
  90 # - Start time
  91 # - Operation type
  92 # - User
  93 # - Size
  94 ```
  95 
  96 ### Download Logs
  97 
  98 ```bash
  99 # Download specific log
 100 sf apex get log --log-id 07Lxx0000000000 --target-org my-sandbox
 101 
 102 # Save to file
 103 sf apex get log --log-id 07Lxx0000000000 --target-org my-sandbox > debug.log
 104 
 105 # Download with number
 106 sf apex get log --number 1 --target-org my-sandbox  # Most recent
 107 ```
 108 
 109 ### Real-Time Log Streaming
 110 
 111 ```bash
 112 # Tail logs in real-time (like `tail -f`)
 113 sf apex tail log --target-org my-sandbox
 114 
 115 # With color highlighting
 116 sf apex tail log --target-org my-sandbox --color
 117 
 118 # Note: --debug-level flag does not exist on sf apex tail log
 119 # Debug levels are configured via TraceFlag records in Setup
 120 sf apex tail log --target-org my-sandbox --skip-trace-flag
 121 ```
 122 
 123 ### Set Debug Level
 124 
 125 ```bash
 126 # Create trace flag via SFDX
 127 sf data create record \
 128   --sobject TraceFlag \
 129   --values "TracedEntityId='005xx...' LogType='USER_DEBUG' StartDate='2024-01-01T00:00:00' ExpirationDate='2024-01-02T00:00:00'" \
 130   --target-org my-sandbox
 131 ```
 132 
 133 ---
 134 
 135 ## Manual Log Analysis (grep/ripgrep)
 136 
 137 When you need quick analysis without visual tools:
 138 
 139 ### Find All SOQL Queries
 140 
 141 ```bash
 142 # Count SOQL queries
 143 rg "SOQL_EXECUTE_BEGIN" debug.log | wc -l
 144 
 145 # See query text
 146 rg "SOQL_EXECUTE_BEGIN" debug.log
 147 
 148 # Find SOQL in loops (query appears multiple times on same line)
 149 rg "SOQL_EXECUTE_BEGIN" debug.log | sort | uniq -c | sort -rn | head -10
 150 ```
 151 
 152 ### Find Large Result Sets
 153 
 154 ```bash
 155 # Find queries returning many rows
 156 rg "SOQL_EXECUTE_END.*\[\d{4,} rows\]" debug.log
 157 ```
 158 
 159 ### Check Governor Limits
 160 
 161 ```bash
 162 # Find limit snapshots
 163 rg "LIMIT_USAGE" debug.log | tail -20
 164 
 165 # Find approaching limits (>80%)
 166 rg "CPU_TIME" debug.log | tail -5
 167 rg "HEAP_SIZE" debug.log | tail -5
 168 ```
 169 
 170 ### Find Exceptions
 171 
 172 ```bash
 173 # Find all exceptions
 174 rg "EXCEPTION_THROWN|FATAL_ERROR" debug.log
 175 
 176 # Get stack traces
 177 rg -A 10 "FATAL_ERROR" debug.log
 178 ```
 179 
 180 ### Find Slow Operations
 181 
 182 ```bash
 183 # Extract all timing info
 184 rg "\[\d+\]ms" debug.log | sort -t'[' -k2 -rn | head -20
 185 ```
 186 
 187 ---
 188 
 189 ## Developer Console Analysis
 190 
 191 For quick checks directly in Salesforce:
 192 
 193 ### Query Plan Tool
 194 
 195 1. Open Developer Console
 196 2. Query Editor tab
 197 3. Click "Query Plan" checkbox
 198 4. Run your query
 199 5. Review selectivity and cost
 200 
 201 ### Log Inspector
 202 
 203 1. Open Developer Console
 204 2. Debug → Open Execute Anonymous Window
 205 3. Run code to generate log
 206 4. Select log in "Logs" tab
 207 5. Debug → View Log Panels
 208 
 209 **Useful Panels**:
 210 - **Execution Overview**: Summary of operations
 211 - **Timeline**: Visual execution flow
 212 - **Stack Tree**: Call hierarchy
 213 - **Database**: SOQL/DML details
 214 
 215 ---
 216 
 217 ## Quick Reference: What to Look For
 218 
 219 | Problem | What to Search | Pattern |
 220 |---------|----------------|---------|
 221 | SOQL in Loop | `SOQL_EXECUTE_BEGIN` | Same query repeated many times |
 222 | DML in Loop | `DML_BEGIN` | Same DML repeated many times |
 223 | Slow Query | `SOQL_EXECUTE_END` | Large row count |
 224 | CPU Issue | `CPU_TIME` | Approaching 10,000ms |
 225 | Heap Issue | `HEAP_SIZE` | Approaching 6,000,000 |
 226 | Exception | `EXCEPTION_THROWN` | Stack trace |
 227 
 228 ---
 229 
 230 ## Comparison: Analysis Tools
 231 
 232 | Tool | Pros | Cons | Best For |
 233 |------|------|------|----------|
 234 | **Apex Log Analyzer** | Visual, free, flame charts | Requires VS Code | Deep performance analysis |
 235 | **Developer Console** | Built-in, no install | Limited visualization | Quick checks |
 236 | **SF CLI + grep** | Scriptable, fast | No visualization | CI/CD, automation |
 237 | **Salesforce Inspector** | Browser-based | Limited log analysis | Quick org exploration |
 238 
 239 ---
 240 
 241 ## Related Resources
 242 
 243 - [debug-log-reference.md](./debug-log-reference.md) - Log event types
 244 - [benchmarking-guide.md](./benchmarking-guide.md) - Performance testing
 245 - [cli-commands.md](./cli-commands.md) - SF CLI reference
