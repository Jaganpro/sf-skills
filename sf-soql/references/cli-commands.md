<!-- Parent: sf-soql/SKILL.md -->
   1 # Salesforce CLI SOQL Commands
   2 
   3 ## Quick Reference
   4 
   5 | Task | Command |
   6 |------|---------|
   7 | Run query | `sf data query --query "SELECT..."` |
   8 | JSON output | `sf data query --query "..." --json` |
   9 | CSV output | `sf data query --query "..." --result-format csv` |
  10 | Bulk export | `sf data export bulk --query "SELECT..." --target-org alias` |
  11 | Query plan | `sf data query --query "..." --use-tooling-api --plan` |
  12 
  13 ---
  14 
  15 ## Basic Queries
  16 
  17 ### Run a Query
  18 
  19 ```bash
  20 sf data query \
  21   --query "SELECT Id, Name, Industry FROM Account LIMIT 10" \
  22   --target-org my-sandbox
  23 ```
  24 
  25 ### Query with Filters
  26 
  27 ```bash
  28 sf data query \
  29   --query "SELECT Id, Name FROM Account WHERE Industry = 'Technology'" \
  30   --target-org my-sandbox
  31 ```
  32 
  33 ### Query Relationships
  34 
  35 ```bash
  36 # Child-to-parent
  37 sf data query \
  38   --query "SELECT Id, Name, Account.Name FROM Contact LIMIT 10" \
  39   --target-org my-sandbox
  40 
  41 # Parent-to-child
  42 sf data query \
  43   --query "SELECT Id, Name, (SELECT Id, Name FROM Contacts) FROM Account LIMIT 5" \
  44   --target-org my-sandbox
  45 ```
  46 
  47 ---
  48 
  49 ## Output Formats
  50 
  51 ### Human-Readable (Default)
  52 
  53 ```bash
  54 sf data query \
  55   --query "SELECT Id, Name FROM Account LIMIT 5" \
  56   --target-org my-sandbox
  57 ```
  58 
  59 ### JSON
  60 
  61 ```bash
  62 sf data query \
  63   --query "SELECT Id, Name FROM Account LIMIT 5" \
  64   --target-org my-sandbox \
  65   --json
  66 ```
  67 
  68 ### CSV
  69 
  70 ```bash
  71 sf data query \
  72   --query "SELECT Id, Name, Industry FROM Account" \
  73   --target-org my-sandbox \
  74   --result-format csv > accounts.csv
  75 ```
  76 
  77 ### Direct to File
  78 
  79 ```bash
  80 sf data query \
  81   --query "SELECT Id, Name, Industry FROM Account" \
  82   --target-org my-sandbox \
  83   --result-format csv \
  84   --output-file accounts.csv
  85 ```
  86 
  87 ---
  88 
  89 ## Bulk Data Export
  90 
  91 For large result sets (> 2,000 records), use the dedicated bulk export command:
  92 
  93 ```bash
  94 # Export to CSV (default)
  95 sf data export bulk \
  96   --query "SELECT Id, Name FROM Account" \
  97   --target-org my-sandbox \
  98   --output-file accounts.csv
  99 
 100 # Export as JSON
 101 sf data export bulk \
 102   --query "SELECT Id, Name FROM Account" \
 103   --target-org my-sandbox \
 104   --output-file accounts.json \
 105   --result-format json
 106 ```
 107 
 108 > **Note**: `--bulk` and `--wait` flags on `sf data query` were removed in v2.87.7. Use `sf data export bulk` instead.
 109 
 110 ---
 111 
 112 ## Query Plan Analysis
 113 
 114 Analyze query performance before running:
 115 
 116 ```bash
 117 sf data query \
 118   --query "SELECT Id FROM Account WHERE Name = 'Acme'" \
 119   --target-org my-sandbox \
 120   --use-tooling-api \
 121   --plan
 122 ```
 123 
 124 ### Understanding Query Plan Output
 125 
 126 ```json
 127 {
 128   "plans": [{
 129     "cardinality": 50,           // Estimated rows returned
 130     "fields": ["Name"],          // Fields used for filtering
 131     "leadingOperationType": "Index",  // Index = good, TableScan = bad
 132     "relativeCost": 0.1,         // Lower is better
 133     "sobjectCardinality": 10000, // Total records in object
 134     "sobjectType": "Account"
 135   }]
 136 }
 137 ```
 138 
 139 **Key Indicators:**
 140 - `leadingOperationType: "Index"` = Query uses index (good)
 141 - `leadingOperationType: "TableScan"` = Full table scan (bad for large tables)
 142 - `relativeCost < 1` = Efficient query
 143 - `cardinality` = Expected number of results
 144 
 145 ---
 146 
 147 ## Tooling API Queries
 148 
 149 Query metadata objects:
 150 
 151 ```bash
 152 # Query ApexClass
 153 sf data query \
 154   --query "SELECT Id, Name, Body FROM ApexClass WHERE Name = 'MyController'" \
 155   --target-org my-sandbox \
 156   --use-tooling-api
 157 
 158 # Query CustomField
 159 sf data query \
 160   --query "SELECT Id, DeveloperName, TableEnumOrId FROM CustomField WHERE TableEnumOrId = 'Account'" \
 161   --target-org my-sandbox \
 162   --use-tooling-api
 163 ```
 164 
 165 ---
 166 
 167 ## Query from File
 168 
 169 Store query in file and execute:
 170 
 171 ```bash
 172 # Create query file
 173 echo "SELECT Id, Name FROM Account WHERE Industry = 'Technology'" > query.soql
 174 
 175 # Execute from file
 176 sf data query \
 177   --file query.soql \
 178   --target-org my-sandbox
 179 ```
 180 
 181 ---
 182 
 183 ## Useful Patterns
 184 
 185 ### Get Record Count
 186 
 187 ```bash
 188 sf data query \
 189   --query "SELECT COUNT() FROM Account" \
 190   --target-org my-sandbox
 191 ```
 192 
 193 ### Export to File
 194 
 195 ```bash
 196 # CSV export
 197 sf data query \
 198   --query "SELECT Id, Name, Industry, Phone FROM Account" \
 199   --target-org my-sandbox \
 200   --result-format csv > accounts.csv
 201 
 202 # JSON export
 203 sf data query \
 204   --query "SELECT Id, Name, Industry FROM Account" \
 205   --target-org my-sandbox \
 206   --json > accounts.json
 207 ```
 208 
 209 ### Query with jq Processing
 210 
 211 ```bash
 212 # Get just the names
 213 sf data query \
 214   --query "SELECT Name FROM Account LIMIT 10" \
 215   --target-org my-sandbox \
 216   --json | jq -r '.result.records[].Name'
 217 
 218 # Count records
 219 sf data query \
 220   --query "SELECT Id FROM Account" \
 221   --target-org my-sandbox \
 222   --json | jq '.result.totalSize'
 223 
 224 # Filter in shell
 225 sf data query \
 226   --query "SELECT Id, Name, Industry FROM Account" \
 227   --target-org my-sandbox \
 228   --json | jq '.result.records[] | select(.Industry == "Technology")'
 229 ```
 230 
 231 ### Query with Dates
 232 
 233 ```bash
 234 # Records created today
 235 sf data query \
 236   --query "SELECT Id, Name FROM Account WHERE CreatedDate = TODAY" \
 237   --target-org my-sandbox
 238 
 239 # Records from last 30 days
 240 sf data query \
 241   --query "SELECT Id, Name FROM Account WHERE CreatedDate = LAST_N_DAYS:30" \
 242   --target-org my-sandbox
 243 ```
 244 
 245 ### Aggregate Queries
 246 
 247 ```bash
 248 # Count by industry
 249 sf data query \
 250   --query "SELECT Industry, COUNT(Id) FROM Account GROUP BY Industry" \
 251   --target-org my-sandbox
 252 
 253 # Sum of amounts
 254 sf data query \
 255   --query "SELECT SUM(Amount) FROM Opportunity WHERE StageName = 'Closed Won'" \
 256   --target-org my-sandbox
 257 ```
 258 
 259 ---
 260 
 261 ## Troubleshooting
 262 
 263 ### Query Timeout
 264 
 265 For long-running queries, export via bulk API:
 266 
 267 ```bash
 268 sf data export bulk \
 269   --query "SELECT Id, Name FROM Account" \
 270   --target-org my-sandbox \
 271   --output-file results.csv
 272 ```
 273 
 274 ### Too Many Results
 275 
 276 Add LIMIT or filter:
 277 
 278 ```bash
 279 # With limit
 280 sf data query \
 281   --query "SELECT Id, Name FROM Account LIMIT 1000" \
 282   --target-org my-sandbox
 283 
 284 # With filter
 285 sf data query \
 286   --query "SELECT Id, Name FROM Account WHERE CreatedDate = THIS_YEAR" \
 287   --target-org my-sandbox
 288 ```
 289 
 290 ### Non-Selective Query Error
 291 
 292 Add indexed field to WHERE:
 293 
 294 ```bash
 295 # Add CreatedDate filter (indexed)
 296 sf data query \
 297   --query "SELECT Id FROM Lead WHERE Status = 'Open' AND CreatedDate = LAST_N_DAYS:90" \
 298   --target-org my-sandbox
 299 ```
 300 
 301 ### Permission Errors
 302 
 303 Check field-level security:
 304 
 305 ```bash
 306 # Query accessible fields only
 307 sf data query \
 308   --query "SELECT Id, Name FROM Account" \
 309   --target-org my-sandbox
 310 ```
 311 
 312 ---
 313 
 314 ## Integration with Other Tools
 315 
 316 ### Pipe to File
 317 
 318 ```bash
 319 sf data query \
 320   --query "SELECT Id, Name FROM Account" \
 321   --target-org my-sandbox \
 322   --result-format csv | tee accounts.csv
 323 ```
 324 
 325 ### Use in Scripts
 326 
 327 ```bash
 328 #!/bin/bash
 329 
 330 ORG=${1:-"my-sandbox"}
 331 
 332 # Get count
 333 COUNT=$(sf data query \
 334   --query "SELECT COUNT() FROM Account" \
 335   --target-org $ORG \
 336   --json | jq -r '.result.totalSize')
 337 
 338 echo "Total accounts: $COUNT"
 339 
 340 # Get top accounts
 341 sf data query \
 342   --query "SELECT Name, AnnualRevenue FROM Account ORDER BY AnnualRevenue DESC LIMIT 10" \
 343   --target-org $ORG
 344 ```
 345 
 346 ### Compare Orgs
 347 
 348 ```bash
 349 #!/bin/bash
 350 
 351 PROD_COUNT=$(sf data query --query "SELECT COUNT() FROM Account" --target-org prod --json | jq '.result.totalSize')
 352 SANDBOX_COUNT=$(sf data query --query "SELECT COUNT() FROM Account" --target-org sandbox --json | jq '.result.totalSize')
 353 
 354 echo "Production accounts: $PROD_COUNT"
 355 echo "Sandbox accounts: $SANDBOX_COUNT"
 356 echo "Difference: $((PROD_COUNT - SANDBOX_COUNT))"
 357 ```
