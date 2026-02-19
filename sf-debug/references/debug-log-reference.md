<!-- Parent: sf-debug/SKILL.md -->
   1 # Salesforce Debug Log Reference
   2 
   3 ## Log Structure
   4 
   5 Debug logs follow a consistent format:
   6 ```
   7 TIMESTAMP|EVENT_IDENTIFIER|[PARAMS]|DETAILS
   8 ```
   9 
  10 Example:
  11 ```
  12 14:32:54.123 (123456789)|SOQL_EXECUTE_BEGIN|[45]|SELECT Id FROM Account
  13 ```
  14 
  15 ---
  16 
  17 ## Event Categories
  18 
  19 ### Execution Events
  20 
  21 | Event | Description | Analysis Notes |
  22 |-------|-------------|----------------|
  23 | `EXECUTION_STARTED` | Transaction begins | Identifies transaction type |
  24 | `EXECUTION_FINISHED` | Transaction ends | Total execution time |
  25 | `CODE_UNIT_STARTED` | Method/trigger entry | Call stack tracing |
  26 | `CODE_UNIT_FINISHED` | Method/trigger exit | Method duration |
  27 
  28 ### SOQL Events
  29 
  30 | Event | Description | Key Fields |
  31 |-------|-------------|------------|
  32 | `SOQL_EXECUTE_BEGIN` | Query starts | Line number, Query text |
  33 | `SOQL_EXECUTE_END` | Query ends | Rows returned |
  34 
  35 **Analysis Pattern:**
  36 ```
  37 |SOQL_EXECUTE_BEGIN|[45]|SELECT Id, Name FROM Account WHERE...
  38 |SOQL_EXECUTE_END|[3 rows]
  39 ```
  40 - Line 45 in source code
  41 - Query returned 3 rows
  42 
  43 **Warning Signs:**
  44 - Same query appearing multiple times → SOQL in loop
  45 - `[100000 rows]` → Non-selective query
  46 - Query without WHERE clause → Full table scan
  47 
  48 ### DML Events
  49 
  50 | Event | Description | Key Fields |
  51 |-------|-------------|------------|
  52 | `DML_BEGIN` | DML starts | Line number, Operation type, Object |
  53 | `DML_END` | DML ends | Rows affected |
  54 
  55 **Analysis Pattern:**
  56 ```
  57 |DML_BEGIN|[78]|Op:Insert|Type:Contact|
  58 |DML_END|[200 rows]
  59 ```
  60 - Line 78: INSERT operation
  61 - 200 Contact records inserted
  62 
  63 **Warning Signs:**
  64 - Same DML operation appearing multiple times → DML in loop
  65 - DML after each SOQL → Likely unbulkified code
  66 
  67 ### Limit Events
  68 
  69 | Event | Description | Format |
  70 |-------|-------------|--------|
  71 | `LIMIT_USAGE` | Current limit usage | `LIMIT_NAME|used|max` |
  72 | `LIMIT_USAGE_FOR_NS` | Per-namespace limits | `LIMIT_NAME|used|max|namespace` |
  73 | `CUMULATIVE_LIMIT_USAGE` | End of transaction | Summary of all limits |
  74 
  75 **Example:**
  76 ```
  77 |LIMIT_USAGE|SOQL_QUERIES|25|100
  78 |LIMIT_USAGE|DML_STATEMENTS|45|150
  79 |LIMIT_USAGE|CPU_TIME|3500|10000
  80 |LIMIT_USAGE|HEAP_SIZE|2500000|6000000
  81 ```
  82 
  83 ### Exception Events
  84 
  85 | Event | Description | Format |
  86 |-------|-------------|--------|
  87 | `EXCEPTION_THROWN` | Exception occurs | `[line]|ExceptionType|Message` |
  88 | `FATAL_ERROR` | Unhandled exception | Full stack trace |
  89 
  90 **Analysis Pattern:**
  91 ```
  92 |EXCEPTION_THROWN|[67]|System.NullPointerException|Attempt to de-reference a null object
  93 |FATAL_ERROR|System.NullPointerException: Attempt to de-reference a null object
  94   Class.ContactService.processContacts: line 67, column 1
  95   Class.AccountTriggerHandler.afterUpdate: line 34, column 1
  96   Trigger.AccountTrigger: line 5, column 1
  97 ```
  98 
  99 ### Method Events
 100 
 101 | Event | Description | Use Case |
 102 |-------|-------------|----------|
 103 | `METHOD_ENTRY` | Method called | Call hierarchy |
 104 | `METHOD_EXIT` | Method returns | Method duration |
 105 | `CONSTRUCTOR_ENTRY` | Constructor called | Object creation |
 106 | `CONSTRUCTOR_EXIT` | Constructor returns | |
 107 
 108 ### Loop Events
 109 
 110 | Event | Description | Important For |
 111 |-------|-------------|---------------|
 112 | `LOOP_BEGIN` | Loop starts | SOQL/DML in loop detection |
 113 | `LOOP_END` | Loop ends | |
 114 | `ITERATION_BEGIN` | Loop iteration | Iteration count |
 115 | `ITERATION_END` | Iteration ends | |
 116 
 117 **Detection Pattern for SOQL in Loop:**
 118 ```
 119 |LOOP_BEGIN|
 120   |ITERATION_BEGIN|
 121     |SOQL_EXECUTE_BEGIN|[45]|SELECT...
 122     |SOQL_EXECUTE_END|[1 rows]
 123   |ITERATION_END|
 124   |ITERATION_BEGIN|
 125     |SOQL_EXECUTE_BEGIN|[45]|SELECT...  ← Same query repeating!
 126     |SOQL_EXECUTE_END|[1 rows]
 127   |ITERATION_END|
 128 |LOOP_END|
 129 ```
 130 
 131 ### Callout Events
 132 
 133 | Event | Description | Key Fields |
 134 |-------|-------------|------------|
 135 | `CALLOUT_EXTERNAL_ENTRY` | HTTP callout starts | Endpoint URL |
 136 | `CALLOUT_EXTERNAL_EXIT` | HTTP callout ends | Status code, Duration |
 137 
 138 **Example:**
 139 ```
 140 |CALLOUT_EXTERNAL_ENTRY|[89]|https://api.example.com/endpoint
 141 |CALLOUT_EXTERNAL_EXIT|[200]|[1500ms]
 142 ```
 143 
 144 ### Heap Events
 145 
 146 | Event | Description | Importance |
 147 |-------|-------------|------------|
 148 | `HEAP_ALLOCATE` | Heap allocation | Track large allocations |
 149 | `HEAP_DEALLOCATE` | Heap freed | Garbage collection |
 150 
 151 ---
 152 
 153 ## Log Levels
 154 
 155 ### Categories and Levels
 156 
 157 | Category | What It Controls |
 158 |----------|------------------|
 159 | Database | SOQL, SOSL, DML |
 160 | Workflow | Workflow rules, Process Builder |
 161 | Validation | Validation rules |
 162 | Callout | HTTP callouts |
 163 | Apex Code | Apex execution |
 164 | Apex Profiling | Method timing |
 165 | Visualforce | VF page execution |
 166 | System | System operations |
 167 
 168 ### Level Values
 169 
 170 | Level | Amount of Detail | Use Case |
 171 |-------|------------------|----------|
 172 | NONE | Nothing | Disable category |
 173 | ERROR | Errors only | Production monitoring |
 174 | WARN | Warnings + errors | |
 175 | INFO | General info | Default |
 176 | DEBUG | Detailed debug | Development |
 177 | FINE | Very detailed | Deep debugging |
 178 | FINER | Method entry/exit | Performance analysis |
 179 | FINEST | Everything | Complete trace |
 180 
 181 ### Recommended Debug Level Settings
 182 
 183 **For Performance Issues:**
 184 ```
 185 Apex Code: FINE
 186 Apex Profiling: FINEST
 187 Database: FINE
 188 System: DEBUG
 189 ```
 190 
 191 **For Exception Debugging:**
 192 ```
 193 Apex Code: DEBUG
 194 Apex Profiling: FINE
 195 Database: INFO
 196 System: DEBUG
 197 ```
 198 
 199 **For Callout Issues:**
 200 ```
 201 Apex Code: DEBUG
 202 Callout: FINEST
 203 System: DEBUG
 204 ```
 205 
 206 ---
 207 
 208 ## Governor Limits Reference
 209 
 210 ### Synchronous Limits
 211 
 212 | Limit | Value | Log Event |
 213 |-------|-------|-----------|
 214 | SOQL Queries | 100 | `SOQL_QUERIES` |
 215 | SOQL Rows | 50,000 | `SOQL_ROWS` |
 216 | DML Statements | 150 | `DML_STATEMENTS` |
 217 | DML Rows | 10,000 | `DML_ROWS` |
 218 | CPU Time | 10,000 ms | `CPU_TIME` |
 219 | Heap Size | 6 MB | `HEAP_SIZE` |
 220 | Callouts | 100 | `CALLOUTS` |
 221 | Future Calls | 50 | `FUTURE_CALLS` |
 222 
 223 ### Asynchronous Limits
 224 
 225 | Limit | Value | Applies To |
 226 |-------|-------|------------|
 227 | CPU Time | 60,000 ms | @future, Batch, Queueable |
 228 | Heap Size | 12 MB | @future, Batch, Queueable |
 229 
 230 ### Warning Thresholds
 231 
 232 | Limit | Warning (80%) | Critical (95%) |
 233 |-------|---------------|----------------|
 234 | SOQL Queries | 80 | 95 |
 235 | DML Statements | 120 | 143 |
 236 | CPU Time | 8,000 ms | 9,500 ms |
 237 | Heap Size | 4.8 MB | 5.7 MB |
 238 
 239 ---
 240 
 241 ## Common Log Patterns
 242 
 243 ### Pattern 1: SOQL in Loop
 244 
 245 ```
 246 |LOOP_BEGIN|
 247 |ITERATION_BEGIN|
 248 |SOQL_EXECUTE_BEGIN|[45]|SELECT Id FROM Contact WHERE AccountId = '001xxx'
 249 |SOQL_EXECUTE_END|[1 rows]
 250 |ITERATION_END|
 251 |ITERATION_BEGIN|
 252 |SOQL_EXECUTE_BEGIN|[45]|SELECT Id FROM Contact WHERE AccountId = '001yyy'
 253 |SOQL_EXECUTE_END|[1 rows]
 254 |ITERATION_END|
 255 ... (repeats 100 times)
 256 |LIMIT_USAGE|SOQL_QUERIES|100|100  ← LIMIT HIT!
 257 |FATAL_ERROR|System.LimitException: Too many SOQL queries: 101
 258 ```
 259 
 260 ### Pattern 2: DML in Loop
 261 
 262 ```
 263 |LOOP_BEGIN|
 264 |ITERATION_BEGIN|
 265 |DML_BEGIN|[78]|Op:Insert|Type:Contact|
 266 |DML_END|[1 rows]
 267 |ITERATION_END|
 268 ... (repeats 150 times)
 269 |LIMIT_USAGE|DML_STATEMENTS|150|150  ← LIMIT HIT!
 270 |FATAL_ERROR|System.LimitException: Too many DML statements: 151
 271 ```
 272 
 273 ### Pattern 3: Non-Selective Query
 274 
 275 ```
 276 |SOQL_EXECUTE_BEGIN|[23]|SELECT Id FROM Lead WHERE Status = 'Open'
 277 |SOQL_EXECUTE_END|[250000 rows]  ← Large result set!
 278 ```
 279 
 280 ### Pattern 4: CPU Limit Approaching
 281 
 282 ```
 283 |CUMULATIVE_LIMIT_USAGE|
 284 |CPU_TIME|9500|10000  ← 95% used!
 285 ```
 286 
 287 ### Pattern 5: Null Pointer Exception
 288 
 289 ```
 290 |SOQL_EXECUTE_BEGIN|[45]|SELECT Id FROM Account WHERE Id = '001xxx'
 291 |SOQL_EXECUTE_END|[0 rows]  ← No results!
 292 |METHOD_EXIT|getAccount|
 293 |EXCEPTION_THROWN|[47]|System.NullPointerException|Attempt to de-reference a null object
 294 ```
 295 
 296 ---
 297 
 298 ## Log Analysis Checklist
 299 
 300 ### Quick Scan
 301 
 302 1. **Search for `FATAL_ERROR`** - Find the exception
 303 2. **Search for `LIMIT_USAGE`** - Check governor limits
 304 3. **Search for `SOQL_EXECUTE_BEGIN`** - Count queries
 305 4. **Search for `DML_BEGIN`** - Count DML operations
 306 5. **Search for `LOOP_BEGIN`** - Check for operations in loops
 307 
 308 ### Deep Analysis
 309 
 310 1. **Trace the call stack** - Use `CODE_UNIT_STARTED` events
 311 2. **Find the hotspot** - Use `Apex Profiling: FINEST` for method timing
 312 3. **Identify large queries** - Look for `[N rows]` in SOQL_EXECUTE_END
 313 4. **Check callout timing** - Look for slow `CALLOUT_EXTERNAL_EXIT`
 314 5. **Monitor heap growth** - Track `HEAP_ALLOCATE` events
 315 
 316 ---
 317 
 318 ## Related Commands
 319 
 320 | Command | Purpose |
 321 |---------|---------|
 322 | `sf apex list log` | List available logs |
 323 | `sf apex get log --log-id XXX` | Download specific log |
 324 | `sf apex tail log` | Stream logs real-time |
 325 | `sf data delete record --sobject ApexLog --record-id <id>` | Delete individual log record |
 326 
 327 See [cli-commands.md](./cli-commands.md) for detailed command reference.
