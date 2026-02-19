<!-- Parent: sf-metadata/SKILL.md -->
   1 # Salesforce CLI Commands Reference
   2 
   3 ## Overview
   4 
   5 This guide covers sf CLI v2 commands for metadata operations, org queries, and deployment tasks.
   6 
   7 ---
   8 
   9 ## Authentication
  10 
  11 ### Authorize an Org
  12 ```bash
  13 # Web login (interactive)
  14 sf org login web --alias myorg
  15 
  16 # JWT flow (CI/CD)
  17 sf org login jwt \
  18   --client-id <client_id> \
  19   --jwt-key-file server.key \
  20   --username user@example.com \
  21   --alias myorg
  22 
  23 # SFDX Auth URL (from file)
  24 sf org login sfdx-url --sfdx-url-file authFile.txt --alias myorg
  25 ```
  26 
  27 ### List Connected Orgs
  28 ```bash
  29 sf org list
  30 
  31 # With details
  32 sf org list --verbose
  33 ```
  34 
  35 ### Display Org Info
  36 ```bash
  37 sf org display --target-org myorg
  38 
  39 # JSON output
  40 sf org display --target-org myorg --json
  41 ```
  42 
  43 ---
  44 
  45 ## Object & Field Queries
  46 
  47 ### Describe an Object
  48 ```bash
  49 # Standard or custom object
  50 sf sobject describe --sobject Account --target-org myorg
  51 
  52 # JSON output (for parsing)
  53 sf sobject describe --sobject Account --target-org myorg --json
  54 
  55 # Tooling API object
  56 sf sobject describe --sobject ApexClass --target-org myorg --use-tooling-api
  57 ```
  58 
  59 ### List Objects
  60 ```bash
  61 # All objects
  62 sf sobject list --target-org myorg --sobject all
  63 
  64 # Custom objects only
  65 sf sobject list --target-org myorg --sobject custom
  66 
  67 # Standard objects only
  68 sf sobject list --target-org myorg --sobject standard
  69 ```
  70 
  71 ### Parse Object Fields (with jq)
  72 ```bash
  73 # List all field names
  74 sf sobject describe --sobject Account --target-org myorg --json | \
  75   jq -r '.result.fields[].name'
  76 
  77 # List custom fields only
  78 sf sobject describe --sobject Account --target-org myorg --json | \
  79   jq -r '.result.fields[] | select(.custom == true) | .name'
  80 
  81 # Get field details
  82 sf sobject describe --sobject Account --target-org myorg --json | \
  83   jq '.result.fields[] | {name, type, length, label}'
  84 ```
  85 
  86 ---
  87 
  88 ## Metadata Operations
  89 
  90 ### List Metadata Types
  91 ```bash
  92 # All available metadata types
  93 sf org list metadata-types --target-org myorg
  94 
  95 # JSON output
  96 sf org list metadata-types --target-org myorg --json
  97 ```
  98 
  99 ### List Metadata of a Type
 100 ```bash
 101 # Custom Objects
 102 sf org list metadata --metadata-type CustomObject --target-org myorg
 103 
 104 # Custom Fields (specify folder/object)
 105 sf org list metadata --metadata-type CustomField --folder Account --target-org myorg
 106 
 107 # Profiles
 108 sf org list metadata --metadata-type Profile --target-org myorg
 109 
 110 # Permission Sets
 111 sf org list metadata --metadata-type PermissionSet --target-org myorg
 112 
 113 # Flows
 114 sf org list metadata --metadata-type Flow --target-org myorg
 115 
 116 # Apex Classes
 117 sf org list metadata --metadata-type ApexClass --target-org myorg
 118 ```
 119 
 120 ---
 121 
 122 ## Retrieve Metadata
 123 
 124 ### Retrieve by Metadata Type
 125 ```bash
 126 # Single type
 127 sf project retrieve start --metadata CustomObject:Account --target-org myorg
 128 
 129 # Multiple items
 130 sf project retrieve start \
 131   --metadata CustomObject:Account \
 132   --metadata CustomObject:Contact \
 133   --target-org myorg
 134 
 135 # Wildcard (all of type)
 136 sf project retrieve start --metadata "CustomObject:*" --target-org myorg
 137 ```
 138 
 139 ### Retrieve from Manifest (package.xml)
 140 ```bash
 141 sf project retrieve start --manifest manifest/package.xml --target-org myorg
 142 ```
 143 
 144 ### Retrieve to Specific Directory
 145 ```bash
 146 sf project retrieve start \
 147   --metadata CustomObject:Account \
 148   --target-org myorg \
 149   --output-dir ./retrieved
 150 ```
 151 
 152 ---
 153 
 154 ## Deploy Metadata
 155 
 156 ### Deploy Source Directory
 157 ```bash
 158 # Deploy all source
 159 sf project deploy start --source-dir force-app --target-org myorg
 160 
 161 # Dry run (validation only)
 162 sf project deploy start --source-dir force-app --target-org myorg --dry-run
 163 
 164 # With specific test level
 165 sf project deploy start \
 166   --source-dir force-app \
 167   --target-org myorg \
 168   --test-level RunLocalTests
 169 ```
 170 
 171 ### Deploy Specific Metadata
 172 ```bash
 173 sf project deploy start \
 174   --metadata CustomObject:Invoice__c \
 175   --target-org myorg
 176 ```
 177 
 178 ### Deploy from Manifest
 179 ```bash
 180 sf project deploy start --manifest manifest/package.xml --target-org myorg
 181 ```
 182 
 183 ### Check Deploy Status
 184 ```bash
 185 # Poll for status
 186 sf project deploy report --job-id <jobId>
 187 
 188 # Resume watching
 189 sf project deploy resume --job-id <jobId>
 190 ```
 191 
 192 ### Test Levels
 193 | Level | Description |
 194 |-------|-------------|
 195 | `NoTestRun` | No tests (sandbox only) |
 196 | `RunSpecifiedTests` | Run specific tests |
 197 | `RunLocalTests` | Run org tests (non-managed) |
 198 | `RunAllTestsInOrg` | Run all tests |
 199 
 200 ---
 201 
 202 ## Generate Metadata
 203 
 204 ### Generate Custom Object
 205 ```bash
 206 sf schema generate sobject --label "My Object"
 207 ```
 208 
 209 ### Generate Custom Field
 210 ```bash
 211 sf schema generate field --label "My Field" --object Account
 212 ```
 213 
 214 ### Generate Package.xml
 215 ```bash
 216 # From source directory
 217 sf project generate manifest --source-dir force-app --name package.xml
 218 
 219 # From org metadata
 220 sf project generate manifest \
 221   --from-org myorg \
 222   --metadata-type CustomObject \
 223   --name package.xml
 224 ```
 225 
 226 ---
 227 
 228 ## Data Operations
 229 
 230 ### Query Records (SOQL)
 231 ```bash
 232 # Simple query
 233 sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org myorg
 234 
 235 # Export to CSV
 236 sf data query \
 237   --query "SELECT Id, Name FROM Account" \
 238   --target-org myorg \
 239   --result-format csv > accounts.csv
 240 
 241 # Bulk export (large data, > 2,000 records)
 242 sf data export bulk \
 243   --query "SELECT Id, Name FROM Account" \
 244   --target-org myorg \
 245   --output-file accounts.csv
 246 ```
 247 
 248 ### Import/Export Records
 249 ```bash
 250 # Export to JSON
 251 sf data export tree \
 252   --query "SELECT Id, Name, Industry FROM Account WHERE Industry != null" \
 253   --target-org myorg \
 254   --output-dir ./data
 255 
 256 # Import from JSON
 257 sf data import tree --files data/Account.json --target-org myorg
 258 ```
 259 
 260 ---
 261 
 262 ## Apex Operations
 263 
 264 ### Execute Anonymous Apex
 265 ```bash
 266 # From command line
 267 sf apex run --target-org myorg --file scripts/anonymous.apex
 268 
 269 # Interactive
 270 sf apex run --target-org myorg
 271 ```
 272 
 273 ### Run Tests
 274 ```bash
 275 # All local tests
 276 sf apex test run --target-org myorg --test-level RunLocalTests
 277 
 278 # Specific test class
 279 sf apex test run --target-org myorg --tests MyTestClass
 280 
 281 # Specific test method
 282 sf apex test run --target-org myorg --tests MyTestClass.testMethod
 283 
 284 # With code coverage
 285 sf apex test run --target-org myorg --code-coverage --test-level RunLocalTests
 286 ```
 287 
 288 ---
 289 
 290 ## Useful Patterns
 291 
 292 ### Check Object Exists
 293 ```bash
 294 sf sobject describe --sobject MyObject__c --target-org myorg --json | \
 295   jq -r '.status'
 296 # Returns 0 if exists, 1 if not
 297 ```
 298 
 299 ### Get Field API Names
 300 ```bash
 301 sf sobject describe --sobject Account --target-org myorg --json | \
 302   jq -r '.result.fields[].name' | sort
 303 ```
 304 
 305 ### Get Custom Field Count
 306 ```bash
 307 sf sobject describe --sobject Account --target-org myorg --json | \
 308   jq '[.result.fields[] | select(.custom == true)] | length'
 309 ```
 310 
 311 ### List All Custom Objects
 312 ```bash
 313 sf org list metadata --metadata-type CustomObject --target-org myorg --json | \
 314   jq -r '.result[].fullName' | grep '__c$'
 315 ```
 316 
 317 ### Validate Deployment
 318 ```bash
 319 sf project deploy start \
 320   --source-dir force-app \
 321   --target-org myorg \
 322   --dry-run \
 323   --test-level RunLocalTests \
 324   --json | jq '.result.status'
 325 ```
 326 
 327 ---
 328 
 329 ## Environment Variables
 330 
 331 | Variable | Purpose |
 332 |----------|---------|
 333 | `SF_TARGET_ORG` | Default target org |
 334 | `SF_ACCESS_TOKEN` | Auth token |
 335 | `SF_INSTANCE_URL` | Instance URL |
 336 | `SF_API_VERSION` | API version |
 337 
 338 ---
 339 
 340 ## Common Flags
 341 
 342 | Flag | Short | Description |
 343 |------|-------|-------------|
 344 | `--target-org` | `-o` | Target org alias |
 345 | `--json` | | JSON output |
 346 | `--wait` | `-w` | Wait time (minutes) |
 347 | `--verbose` | | Verbose output |
 348 | `--help` | `-h` | Show help |
 349 
 350 ---
 351 
 352 ## Quick Reference
 353 
 354 ### Daily Operations
 355 ```bash
 356 # Check org
 357 sf org display -o myorg
 358 
 359 # Deploy changes
 360 sf project deploy start -d force-app -o myorg
 361 
 362 # Run tests
 363 sf apex test run -o myorg -l RunLocalTests -c
 364 
 365 # Query data
 366 sf data query -q "SELECT Id FROM Account LIMIT 1" -o myorg
 367 ```
 368 
 369 ### Metadata Discovery
 370 ```bash
 371 # What's in the org?
 372 sf org list metadata-types -o myorg
 373 
 374 # What objects exist?
 375 sf sobject list -o myorg --sobject all
 376 
 377 # Describe an object
 378 sf sobject describe -s Account -o myorg
 379 ```
 380 
 381 ### CI/CD Pipeline
 382 ```bash
 383 # Authenticate
 384 sf org login jwt ...
 385 
 386 # Validate
 387 sf project deploy start -d force-app -o myorg --dry-run -l RunLocalTests
 388 
 389 # Deploy
 390 sf project deploy start -d force-app -o myorg -l RunLocalTests
 391 
 392 # Run additional tests
 393 sf apex test run -o myorg -l RunLocalTests -c -r human
 394 ```
