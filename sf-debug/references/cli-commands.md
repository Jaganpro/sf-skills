<!-- Parent: sf-debug/SKILL.md -->
   1 # Salesforce CLI Debug Commands Reference
   2 
   3 ## Quick Reference
   4 
   5 | Task | Command |
   6 |------|---------|
   7 | List recent logs | `sf apex list log --target-org my-org` |
   8 | Get specific log | `sf apex get log --log-id 07Lxx0000000000` |
   9 | Stream real-time | `sf apex tail log --target-org my-org` |
  10 | Delete log | `sf data delete record --sobject ApexLog --record-id <id> --target-org my-org` |
  11 
  12 ---
  13 
  14 ## Log Retrieval
  15 
  16 ### List Available Logs
  17 
  18 ```bash
  19 # List all logs for current user
  20 sf apex list log --target-org my-org
  21 
  22 # JSON output for parsing
  23 sf apex list log --target-org my-org --json
  24 ```
  25 
  26 **Output Fields:**
  27 - `Id` - Log ID for retrieval
  28 - `LogUser.Name` - Who generated the log
  29 - `Operation` - What triggered the log
  30 - `Status` - Success/Failure
  31 - `LogLength` - Size in bytes
  32 - `StartTime` - When it was generated
  33 
  34 ### Get Specific Log
  35 
  36 ```bash
  37 # Download log by ID
  38 sf apex get log \
  39   --log-id 07Lxx0000000000AAA \
  40   --target-org my-org
  41 
  42 # Save to file
  43 sf apex get log \
  44   --log-id 07Lxx0000000000AAA \
  45   --target-org my-org \
  46   --output-dir ./logs
  47 
  48 # Get most recent log
  49 sf apex list log --target-org my-org --json | \
  50   jq -r '.result[0].Id' | \
  51   xargs -I {} sf apex get log --log-id {} --target-org my-org
  52 ```
  53 
  54 ### Stream Logs Real-Time
  55 
  56 ```bash
  57 # Tail logs with color highlighting
  58 sf apex tail log --target-org my-org --color
  59 
  60 # Tail with color highlighting
  61 sf apex tail log \
  62   --target-org my-org \
  63   --color
  64 # Note: Debug levels are configured via TraceFlag records in Setup, not CLI flags
  65 
  66 # Tail with skip flag (don't show historical logs)
  67 sf apex tail log --target-org my-org --skip-trace-flag
  68 ```
  69 
  70 ---
  71 
  72 ## Log Management
  73 
  74 ### Delete Logs
  75 
  76 > **Note**: `sf apex log delete` does not exist in sf CLI v2. Use `sf data delete record` instead.
  77 
  78 ```bash
  79 # Delete specific log
  80 sf data delete record \
  81   --sobject ApexLog \
  82   --record-id 07Lxx0000000000AAA \
  83   --target-org my-org
  84 ```
  85 
  86 ---
  87 
  88 ## Debug Level Configuration
  89 
  90 ### Using Trace Flags
  91 
  92 Trace flags control what gets logged and for which users.
  93 
  94 ```bash
  95 # Create trace flag for specific user
  96 sf data create record \
  97   --sobject TraceFlag \
  98   --values "TracedEntityId='005xx0000001234' LogType='USER_DEBUG' DebugLevelId='7dlxx0000000000' StartDate='2025-01-01T00:00:00Z' ExpirationDate='2025-01-02T00:00:00Z'" \
  99   --target-org my-org
 100 
 101 # Query existing trace flags
 102 sf data query \
 103   --query "SELECT Id, TracedEntityId, DebugLevel.MasterLabel, ExpirationDate FROM TraceFlag" \
 104   --target-org my-org
 105 
 106 # Delete trace flag
 107 sf data delete record \
 108   --sobject TraceFlag \
 109   --record-id 7tfxx0000000000AAA \
 110   --target-org my-org
 111 ```
 112 
 113 ### Debug Levels
 114 
 115 ```bash
 116 # List available debug levels
 117 sf data query \
 118   --query "SELECT Id, MasterLabel, ApexCode, ApexProfiling, Callout, Database, System, Workflow FROM DebugLevel" \
 119   --target-org my-org
 120 
 121 # Create custom debug level
 122 sf data create record \
 123   --sobject DebugLevel \
 124   --values "MasterLabel='PerformanceDebug' DeveloperName='PerformanceDebug' ApexCode='FINE' ApexProfiling='FINEST' Database='FINE' System='DEBUG'" \
 125   --target-org my-org
 126 ```
 127 
 128 ---
 129 
 130 ## Advanced Usage
 131 
 132 ### Execute Anonymous with Logging
 133 
 134 ```bash
 135 # Run anonymous Apex and capture log
 136 echo "System.debug('Test'); Account a = [SELECT Id FROM Account LIMIT 1];" | \
 137   sf apex run --target-org my-org
 138 
 139 # Run from file
 140 sf apex run \
 141   --file ./scripts/debug-script.apex \
 142   --target-org my-org
 143 
 144 # Get the log from that execution
 145 sf apex list log --target-org my-org --json | \
 146   jq -r '.result[0].Id' | \
 147   xargs -I {} sf apex get log --log-id {} --target-org my-org
 148 ```
 149 
 150 ### Query Plan Analysis
 151 
 152 ```bash
 153 # Analyze query plan using Tooling API
 154 sf data query \
 155   --query "SELECT Id FROM Account WHERE Name = 'Test'" \
 156   --target-org my-org \
 157   --use-tooling-api
 158 # Note: --explain does not exist. Use REST API for query plans:
 159 # GET /services/data/v62.0/query/?explain=SELECT+Id+FROM+Account+WHERE+Name='Test'
 160 ```
 161 
 162 ### Log Analysis with grep
 163 
 164 ```bash
 165 # Find SOQL queries in log
 166 sf apex get log --log-id 07Lxx0000000000 --target-org my-org | \
 167   rg "SOQL_EXECUTE"
 168 
 169 # Count SOQL queries
 170 sf apex get log --log-id 07Lxx0000000000 --target-org my-org | \
 171   rg -c "SOQL_EXECUTE_BEGIN"
 172 
 173 # Find exceptions
 174 sf apex get log --log-id 07Lxx0000000000 --target-org my-org | \
 175   rg "EXCEPTION_THROWN|FATAL_ERROR"
 176 
 177 # Find limit usage
 178 sf apex get log --log-id 07Lxx0000000000 --target-org my-org | \
 179   rg "LIMIT_USAGE"
 180 
 181 # Find slow operations (method timing)
 182 sf apex get log --log-id 07Lxx0000000000 --target-org my-org | \
 183   rg "METHOD_EXIT.*\|([0-9]{4,})\|"
 184 ```
 185 
 186 ---
 187 
 188 ## Automation Scripts
 189 
 190 ### Save and Analyze Latest Log
 191 
 192 ```bash
 193 #!/bin/bash
 194 # save-latest-log.sh
 195 
 196 ORG_ALIAS=${1:-"my-org"}
 197 OUTPUT_DIR=${2:-"./logs"}
 198 
 199 mkdir -p $OUTPUT_DIR
 200 
 201 # Get latest log ID
 202 LOG_ID=$(sf apex list log --target-org $ORG_ALIAS --json | jq -r '.result[0].Id')
 203 
 204 if [ "$LOG_ID" == "null" ]; then
 205     echo "No logs found"
 206     exit 1
 207 fi
 208 
 209 # Save log
 210 FILENAME="$OUTPUT_DIR/$(date +%Y%m%d_%H%M%S)_$LOG_ID.log"
 211 sf apex get log --log-id $LOG_ID --target-org $ORG_ALIAS > $FILENAME
 212 
 213 echo "Log saved to: $FILENAME"
 214 
 215 # Quick analysis
 216 echo ""
 217 echo "=== QUICK ANALYSIS ==="
 218 echo "SOQL Queries: $(rg -c 'SOQL_EXECUTE_BEGIN' $FILENAME || echo 0)"
 219 echo "DML Statements: $(rg -c 'DML_BEGIN' $FILENAME || echo 0)"
 220 echo "Exceptions: $(rg -c 'EXCEPTION_THROWN|FATAL_ERROR' $FILENAME || echo 0)"
 221 ```
 222 
 223 ### Monitor for Errors
 224 
 225 ```bash
 226 #!/bin/bash
 227 # monitor-errors.sh
 228 
 229 ORG_ALIAS=${1:-"my-org"}
 230 
 231 echo "Monitoring $ORG_ALIAS for errors..."
 232 echo "Press Ctrl+C to stop"
 233 
 234 sf apex tail log --target-org $ORG_ALIAS --color 2>&1 | \
 235   while read line; do
 236     if echo "$line" | rg -q "EXCEPTION|FATAL_ERROR|LimitException"; then
 237       echo "🔴 ERROR DETECTED: $line"
 238       # Optional: Send alert
 239       # osascript -e 'display notification "Error in Salesforce" with title "sf-debug"'
 240     fi
 241   done
 242 ```
 243 
 244 ### Bulk Log Cleanup
 245 
 246 ```bash
 247 #!/bin/bash
 248 # cleanup-logs.sh
 249 
 250 ORG_ALIAS=${1:-"my-org"}
 251 DAYS_OLD=${2:-7}
 252 
 253 echo "Deleting logs older than $DAYS_OLD days from $ORG_ALIAS..."
 254 
 255 # Get old log IDs
 256 OLD_LOGS=$(sf data query \
 257   --query "SELECT Id FROM ApexLog WHERE StartTime < LAST_N_DAYS:$DAYS_OLD" \
 258   --target-org $ORG_ALIAS \
 259   --json | jq -r '.result.records[].Id')
 260 
 261 COUNT=0
 262 for LOG_ID in $OLD_LOGS; do
 263     sf data delete record --sobject ApexLog --record-id $LOG_ID --target-org $ORG_ALIAS --json > /dev/null
 264     ((COUNT++))
 265 done
 266 
 267 echo "Deleted $COUNT logs"
 268 ```
 269 
 270 ---
 271 
 272 ## Troubleshooting
 273 
 274 ### No Logs Appearing
 275 
 276 1. **Check trace flags exist:**
 277    ```bash
 278    sf data query \
 279      --query "SELECT Id, TracedEntityId, ExpirationDate FROM TraceFlag WHERE ExpirationDate > TODAY" \
 280      --target-org my-org
 281    ```
 282 
 283 2. **Check log retention:**
 284    ```bash
 285    sf data query \
 286      --query "SELECT Id, StartTime FROM ApexLog ORDER BY StartTime DESC LIMIT 5" \
 287      --target-org my-org
 288    ```
 289 
 290 3. **Verify user has API access:**
 291    - User must have "API Enabled" permission
 292    - User must have "Author Apex" for trace flags
 293 
 294 ### Log Too Large
 295 
 296 Logs over 2MB are truncated. Solutions:
 297 
 298 1. **Reduce debug level:**
 299    ```
 300    ApexCode: DEBUG → INFO
 301    ApexProfiling: FINEST → FINE
 302    ```
 303 
 304 2. **Focus on specific operation:**
 305    - Create trace flag just before the operation
 306    - Delete after capturing
 307 
 308 3. **Use targeted logging:**
 309    - Add `System.debug()` only where needed
 310    - Use `LoggingLevel.ERROR` for critical info
 311 
 312 ### Logs Not Persisting
 313 
 314 Default log retention is 24 hours. To keep logs longer:
 315 
 316 ```bash
 317 # Export log to file immediately
 318 sf apex get log --log-id 07Lxx0000000000 --target-org my-org > ./saved-log.txt
 319 ```
 320 
 321 ---
 322 
 323 ## Integration with sf-debug Skill
 324 
 325 The sf-debug skill automatically:
 326 
 327 1. **Fetches logs** when you run `sf apex get log` or `sf apex tail log`
 328 2. **Parses content** for SOQL in loops, DML in loops, exceptions
 329 3. **Displays analysis** with governor limit usage
 330 4. **Suggests fixes** using sf-apex skill integration
 331 
 332 Example workflow:
 333 ```bash
 334 # Run a test that generates a log
 335 sf apex run test --class-names MyTestClass --target-org my-org
 336 
 337 # Get the log (sf-debug hook auto-analyzes)
 338 sf apex list log --target-org my-org --json | \
 339   jq -r '.result[0].Id' | \
 340   xargs -I {} sf apex get log --log-id {} --target-org my-org
 341 ```
 342 
 343 The hook will output analysis like:
 344 ```
 345 ============================================================
 346 🔍 DEBUG LOG ANALYSIS
 347 ============================================================
 348 
 349 🔴 CRITICAL ISSUES
 350 ------------------------------------------------------------
 351    • SOQL in loop detected: 50 queries executed inside loops
 352    • CPU limit critical: 9500/10000ms (95.0%)
 353 
 354 📊 GOVERNOR LIMIT USAGE
 355 ------------------------------------------------------------
 356    ✅ SOQL Queries: 50/100 (50.0%)
 357    ✅ DML Statements: 25/150 (16.7%)
 358    🔴 CPU Time (ms): 9500/10000 (95.0%)
 359 
 360 🤖 AGENTIC FIX RECOMMENDATIONS
 361 ============================================================
 362 
 363 For SOQL in loop:
 364    1. Move query BEFORE the loop
 365    2. Store results in Map<Id, SObject>
 366    3. Access from Map inside loop
 367 ```
