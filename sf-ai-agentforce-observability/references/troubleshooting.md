<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Troubleshooting Guide
   2 
   3 Common issues and solutions for Agentforce session tracing extraction.
   4 
   5 ## Authentication Issues
   6 
   7 ### 401 Unauthorized
   8 
   9 **Symptom:**
  10 ```
  11 RuntimeError: Token exchange failed: invalid_grant
  12 ```
  13 
  14 **Causes & Solutions:**
  15 
  16 | Cause | Solution |
  17 |-------|----------|
  18 | Expired JWT | Check certificate expiration with `openssl x509 -enddate -noout -in cert.crt` |
  19 | Wrong consumer key | Verify consumer key matches External Client App |
  20 | Certificate mismatch | Re-upload certificate to Salesforce |
  21 | User not authorized | Assign user to Connected App / Permission Set |
  22 
  23 **Debug Steps:**
  24 ```bash
  25 # Test JWT generation
  26 python3 -c "
  27 from scripts.auth import DataCloudAuth
  28 auth = DataCloudAuth('myorg', 'CONSUMER_KEY')
  29 print(auth.get_token()[:50])
  30 "
  31 
  32 # Verify org connection
  33 sf org display --target-org myorg --json
  34 ```
  35 
  36 ### 403 Forbidden
  37 
  38 **Symptom:**
  39 ```
  40 RuntimeError: Access denied: Ensure ECA has cdp_query_api scope
  41 ```
  42 
  43 **Solutions:**
  44 
  45 1. **Add Required Scopes** to External Client App:
  46    - `cdp_query_api`
  47    - `cdp_profile_api`
  48 
  49 2. **Assign Data 360 Permissions** to user:
  50    - Setup → Permission Sets → Data 360 permissions
  51 
  52 3. **Enable Data 360** in org:
  53    - Setup → Data 360 → Enable
  54 
  55 ---
  56 
  57 ## Data Issues
  58 
  59 ### No Session Data Found
  60 
  61 **Symptom:**
  62 ```
  63 Extracted 0 sessions
  64 ```
  65 
  66 **Causes & Solutions:**
  67 
  68 | Cause | Solution |
  69 |-------|----------|
  70 | Session tracing not enabled | Setup → Agentforce → Enable Session Tracing |
  71 | Wrong date range | Data typically lags 5-15 minutes |
  72 | Wrong agent name | Check exact API name with `sf agent list` |
  73 | Sandbox without data | Session tracing may not be enabled in sandbox |
  74 
  75 **Debug:**
  76 ```python
  77 # Check if DMO exists and has data
  78 from scripts.datacloud_client import Data360Client
  79 
  80 client = Data360Client(auth)
  81 count = client.count("ssot__AIAgentSession__dlm")
  82 print(f"Total sessions in Data 360: {count}")
  83 ```
  84 
  85 ### Query Timeout
  86 
  87 **Symptom:**
  88 ```
  89 RuntimeError: Request timed out after 3 retries
  90 ```
  91 
  92 **Solutions:**
  93 
  94 1. **Add date filters** to reduce data volume:
  95    ```python
  96    extractor.extract_sessions(
  97        since=datetime.now() - timedelta(days=1),  # Shorter range
  98    )
  99    ```
 100 
 101 2. **Use incremental extraction**:
 102    ```bash
 103    python3 scripts/cli.py extract-incremental --org prod
 104    ```
 105 
 106 3. **Increase timeout**:
 107    ```python
 108    client = DataCloudClient(auth, timeout=300.0)  # 5 minutes
 109    ```
 110 
 111 ### Memory Error
 112 
 113 **Symptom:**
 114 ```
 115 MemoryError: Unable to allocate array
 116 ```
 117 
 118 **Solutions:**
 119 
 120 1. **Use lazy evaluation**:
 121    ```python
 122    # Good
 123    sessions = pl.scan_parquet(path)
 124    result = sessions.filter(...).collect()
 125 
 126    # Bad
 127    sessions = pl.read_parquet(path)  # Loads everything
 128    ```
 129 
 130 2. **Stream to Parquet** instead of loading:
 131    ```python
 132    client.query_to_parquet(sql, output_path)  # Streams, doesn't load all
 133    ```
 134 
 135 3. **Process in batches**:
 136    ```python
 137    for i in range(0, total_sessions, 1000):
 138        batch_ids = session_ids[i:i+1000]
 139        # Process batch
 140    ```
 141 
 142 ---
 143 
 144 ## Extraction Issues
 145 
 146 ### Missing Child Records
 147 
 148 **Symptom:**
 149 ```
 150 Sessions: 1000
 151 Interactions: 0
 152 Steps: 0
 153 ```
 154 
 155 **Cause:** Session IDs not matching in child queries.
 156 
 157 **Solution:**
 158 ```python
 159 # Verify session IDs are valid
 160 sessions_df = pl.read_parquet(data_dir / "sessions" / "data.parquet")
 161 print(sessions_df.head())  # Check ssot__Id__c values
 162 
 163 # Check if interactions exist for these sessions
 164 interaction_query = f"""
 165 SELECT COUNT(*) FROM ssot__AIAgentInteraction__dlm
 166 WHERE ssot__AiAgentSessionId__c IN ('{session_ids[0]}')
 167 """
 168 ```
 169 
 170 ### Parquet Write Failure
 171 
 172 **Symptom:**
 173 ```
 174 ArrowInvalid: Could not convert X with type Y
 175 ```
 176 
 177 **Solutions:**
 178 
 179 1. **Check for nested/complex types**:
 180    ```python
 181    # Complex types are serialized to JSON strings
 182    if isinstance(value, (dict, list)):
 183        value = json.dumps(value)
 184    ```
 185 
 186 2. **Use explicit schema**:
 187    ```python
 188    from scripts.models import SCHEMAS
 189    client.query_to_parquet(sql, path, schema=SCHEMAS["sessions"])
 190    ```
 191 
 192 ---
 193 
 194 ## Analysis Issues
 195 
 196 ### Polars Import Error
 197 
 198 **Symptom:**
 199 ```
 200 ImportError: No module named 'polars'
 201 ```
 202 
 203 **Solution:**
 204 ```bash
 205 pip install polars pyarrow
 206 ```
 207 
 208 ### Empty DataFrame
 209 
 210 **Symptom:**
 211 ```python
 212 analyzer.session_summary()  # Returns empty DataFrame
 213 ```
 214 
 215 **Debug:**
 216 ```python
 217 # Check if files exist
 218 from pathlib import Path
 219 data_dir = Path("./stdm_data")
 220 print(list(data_dir.glob("**/*.parquet")))
 221 
 222 # Check if files have data
 223 import pyarrow.parquet as pq
 224 pf = pq.ParquetFile(data_dir / "sessions" / "data.parquet")
 225 print(f"Rows: {pf.metadata.num_rows}")
 226 ```
 227 
 228 ### Column Not Found
 229 
 230 **Symptom:**
 231 ```
 232 SchemaError: column 'ssot__Id__c' not found
 233 ```
 234 
 235 **Cause:** Parquet file has different column names.
 236 
 237 **Debug:**
 238 ```python
 239 # Check actual column names
 240 import pyarrow.parquet as pq
 241 pf = pq.ParquetFile("path/to/file.parquet")
 242 print(pf.schema_arrow)
 243 ```
 244 
 245 ---
 246 
 247 ## CLI Issues
 248 
 249 ### Command Not Found
 250 
 251 **Symptom:**
 252 ```
 253 bash: stdm-extract: command not found
 254 ```
 255 
 256 **Solution:**
 257 ```bash
 258 # Run directly
 259 python3 scripts/cli.py extract --help
 260 
 261 # Or install as package (if setup.py exists)
 262 pip install -e .
 263 ```
 264 
 265 ### Environment Variable Not Set
 266 
 267 **Symptom:**
 268 ```
 269 ValueError: Consumer key not found. Set SF_CONSUMER_KEY
 270 ```
 271 
 272 **Solutions:**
 273 
 274 1. **Set environment variable**:
 275    ```bash
 276    export SF_CONSUMER_KEY="3MVG9..."
 277    ```
 278 
 279 2. **Pass via command line**:
 280    ```bash
 281    python3 scripts/cli.py extract --org prod --consumer-key "3MVG9..."
 282    ```
 283 
 284 3. **Create `.env` file** (if using python-dotenv):
 285    ```
 286    SF_CONSUMER_KEY=3MVG9...
 287    ```
 288 
 289 ---
 290 
 291 ## Data 360 Specific Issues
 292 
 293 ### DMO Not Found
 294 
 295 **Symptom:**
 296 ```
 297 Error: Object ssot__AIAgentSession__dlm not found
 298 ```
 299 
 300 **Causes:**
 301 
 302 1. **Session tracing not enabled** - Enable in Agentforce settings
 303 2. **Wrong API version** - Use v65.0 or higher
 304 3. **Permission issue** - User needs Data 360 access
 305 
 306 ### Query Syntax Error
 307 
 308 **Symptom:**
 309 ```
 310 Error: Unexpected token at position X
 311 ```
 312 
 313 **Common fixes:**
 314 
 315 | Issue | Fix |
 316 |-------|-----|
 317 | Single quotes in values | Escape: `'O''Brien'` |
 318 | Reserved words | Use backticks: `` `Order` `` |
 319 | Date format | Use ISO: `'2026-01-28T00:00:00.000Z'` |
 320 
 321 ---
 322 
 323 ## Lessons Learned (Live Deployment - Jan 2026)
 324 
 325 Critical discoveries from live testing against Vivint-DevInt org.
 326 
 327 ### API Version: v65.0 Recommended
 328 
 329 **Problem:** Documentation referenced v60.0, but Data 360 Query SQL API requires v64.0+. We recommend v65.0 (Winter '26).
 330 
 331 **Fix:**
 332 ```python
 333 # Wrong (v60.0)
 334 url = f"{instance_url}/services/data/v60.0/ssot/querybuilder/execute"
 335 
 336 # Correct (v65.0)
 337 url = f"{instance_url}/services/data/v65.0/ssot/query-sql"
 338 ```
 339 
 340 ### Field Naming: AiAgent (lowercase 'i')
 341 
 342 **Problem:** Documentation shows `AIAgent` but actual schema uses `AiAgent`.
 343 
 344 **Wrong:**
 345 ```sql
 346 SELECT ssot__AIAgentSessionId__c FROM ssot__AIAgentInteraction__dlm
 347 ```
 348 
 349 **Correct:**
 350 ```sql
 351 SELECT ssot__AiAgentSessionId__c FROM ssot__AIAgentInteraction__dlm
 352 ```
 353 
 354 **Affected fields:** All FK references in Interaction, Step, and Moment DMOs.
 355 
 356 ### AIAgentMoment Links to Sessions, Not Interactions
 357 
 358 **Problem:** Documentation implied Moments link to Interactions via `AIAgentInteractionId__c`.
 359 
 360 **Reality:** AIAgentMoment links directly to Sessions via `ssot__AiAgentSessionId__c`.
 361 
 362 **Correct Schema:**
 363 ```
 364 AIAgentSession → AIAgentInteraction → AIAgentInteractionStep
 365        ↓
 366 AIAgentMoment (links to session, not interaction)
 367 ```
 368 
 369 ### Response Format: Array of Arrays
 370 
 371 **Problem:** Expected array of objects, but v64.0+ returns array of arrays.
 372 
 373 **v65.0 Response:**
 374 ```json
 375 {
 376   "metadata": [{"name": "ssot__Id__c"}, {"name": "ssot__Name__c"}],
 377   "data": [
 378     ["019abc...", "Session 1"],
 379     ["019def...", "Session 2"]
 380   ]
 381 }
 382 ```
 383 
 384 **Fix:** Convert using metadata column names:
 385 ```python
 386 column_names = [col["name"] for col in metadata]
 387 records = [dict(zip(column_names, row)) for row in data]
 388 ```
 389 
 390 ### External Client App Setup URL
 391 
 392 **Problem:** Documentation had wrong Setup URL.
 393 
 394 **Wrong:** `/lightning/setup/ExternalClientAppManager/home`
 395 **Correct:** `/lightning/setup/ManageExternalClientApplication/home`
 396 
 397 ### Incremental Extraction Overwrites Data
 398 
 399 **Problem:** `extract-incremental` was overwriting Parquet files instead of appending.
 400 
 401 **Symptoms:**
 402 - Running incremental after full extract → lost all historical data
 403 - Session count dropped from 447 to 17
 404 
 405 **Fix:** Added `append` + `dedupe_key` parameters to `query_to_parquet()`:
 406 ```python
 407 # Now correctly reads existing, appends new, dedupes by ID
 408 result = client.query_to_parquet(
 409     sql, output_path,
 410     append=True,
 411     dedupe_key="ssot__Id__c"
 412 )
 413 ```
 414 
 415 ### Session End Types All NOT_SET
 416 
 417 **Observation:** 100% of sessions had `ssot__AiAgentSessionEndType__c = 'NOT_SET'`.
 418 
 419 **Possible causes:**
 420 - Sessions not explicitly closed
 421 - Agent Builder sessions don't track end types
 422 - Potential data quality issue in source org
 423 
 424 **Recommendation:** Investigate session closure patterns in agent configuration.
 425 
 426 ---
 427 
 428 ## Getting Help
 429 
 430 ### Debug Mode
 431 
 432 ```bash
 433 # Enable verbose logging
 434 python3 scripts/cli.py extract --org prod --verbose 2>&1 | tee debug.log
 435 ```
 436 
 437 ### Check Data 360 Status
 438 
 439 ```bash
 440 # List available DMOs
 441 python3 -c "
 442 from scripts.auth import Data360Auth
 443 from scripts.datacloud_client import Data360Client
 444 
 445 auth = Data360Auth('prod', 'KEY')
 446 client = Data360Client(auth)
 447 dmos = client.list_dmos()
 448 for dmo in dmos:
 449     print(dmo.get('name'))
 450 "
 451 ```
 452 
 453 ### Report Issues
 454 
 455 If you encounter issues not covered here:
 456 
 457 1. Enable verbose mode and capture logs
 458 2. Note the error message and stack trace
 459 3. Check Data 360 health status
 460 4. Contact Salesforce support for API issues
