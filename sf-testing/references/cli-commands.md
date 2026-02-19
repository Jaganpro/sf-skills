<!-- Parent: sf-testing/SKILL.md -->
   1 # Salesforce CLI Test Commands Reference
   2 
   3 ## Quick Reference
   4 
   5 | Task | Command |
   6 |------|---------|
   7 | Run single test class | `sf apex run test --class-names MyTest` |
   8 | Run all local tests | `sf apex run test --test-level RunLocalTests` |
   9 | Run with coverage | `sf apex run test --class-names MyTest --code-coverage` |
  10 | Get JSON output | `sf apex run test --class-names MyTest --result-format json` |
  11 | Run specific methods | `sf apex run test --tests MyTest.method1 --tests MyTest.method2` |
  12 
  13 ## Test Execution
  14 
  15 ### Run Single Test Class
  16 
  17 ```bash
  18 sf apex run test \
  19   --class-names AccountServiceTest \
  20   --target-org my-sandbox \
  21   --code-coverage \
  22   --result-format human
  23 ```
  24 
  25 ### Run Multiple Test Classes
  26 
  27 ```bash
  28 sf apex run test \
  29   --class-names AccountServiceTest \
  30   --class-names ContactServiceTest \
  31   --class-names LeadServiceTest \
  32   --target-org my-sandbox \
  33   --code-coverage
  34 ```
  35 
  36 ### Run Specific Test Methods
  37 
  38 ```bash
  39 sf apex run test \
  40   --tests AccountServiceTest.testCreate \
  41   --tests AccountServiceTest.testUpdate \
  42   --target-org my-sandbox
  43 ```
  44 
  45 ### Run All Local Tests
  46 
  47 ```bash
  48 sf apex run test \
  49   --test-level RunLocalTests \
  50   --target-org my-sandbox \
  51   --code-coverage \
  52   --output-dir test-results
  53 ```
  54 
  55 ### Run Test Suite
  56 
  57 ```bash
  58 sf apex run test \
  59   --suite-names RegressionSuite \
  60   --target-org my-sandbox \
  61   --code-coverage
  62 ```
  63 
  64 ## Test Levels
  65 
  66 | Level | Description |
  67 |-------|-------------|
  68 | `RunSpecifiedTests` | Only specified tests (default when using --class-names) |
  69 | `RunLocalTests` | All tests except managed packages |
  70 | `RunAllTestsInOrg` | All tests including managed packages |
  71 
  72 ## Output Formats
  73 
  74 ### Human Readable (Default)
  75 
  76 ```bash
  77 sf apex run test --class-names MyTest --result-format human
  78 ```
  79 
  80 ### JSON (For Parsing)
  81 
  82 ```bash
  83 sf apex run test --class-names MyTest --result-format json
  84 ```
  85 
  86 ### JUnit XML (For CI/CD)
  87 
  88 ```bash
  89 sf apex run test --class-names MyTest --result-format junit
  90 ```
  91 
  92 ### TAP (Test Anything Protocol)
  93 
  94 ```bash
  95 sf apex run test --class-names MyTest --result-format tap
  96 ```
  97 
  98 ## Code Coverage
  99 
 100 ### Basic Coverage
 101 
 102 ```bash
 103 sf apex run test \
 104   --class-names MyTest \
 105   --code-coverage \
 106   --target-org my-sandbox
 107 ```
 108 
 109 ### Detailed Line-by-Line Coverage
 110 
 111 ```bash
 112 sf apex run test \
 113   --class-names MyTest \
 114   --code-coverage \
 115   --detailed-coverage \
 116   --target-org my-sandbox
 117 ```
 118 
 119 ### Save Results to Directory
 120 
 121 ```bash
 122 sf apex run test \
 123   --class-names MyTest \
 124   --code-coverage \
 125   --output-dir ./test-results \
 126   --target-org my-sandbox
 127 ```
 128 
 129 Output files:
 130 - `test-run-id.json` - Test results
 131 - `test-run-id-codecoverage.json` - Coverage data
 132 
 133 ## Async Test Execution
 134 
 135 ### Run Tests Asynchronously
 136 
 137 ```bash
 138 sf apex run test \
 139   --test-level RunLocalTests \
 140   --target-org my-sandbox \
 141   --async
 142 ```
 143 
 144 Returns a test run ID for checking status later.
 145 
 146 ### Check Async Test Status
 147 
 148 ```bash
 149 sf apex get test \
 150   --test-run-id 707xx0000000000AAA \
 151   --target-org my-sandbox
 152 ```
 153 
 154 ### Wait for Test Completion
 155 
 156 ```bash
 157 sf apex run test \
 158   --test-level RunLocalTests \
 159   --target-org my-sandbox \
 160   --wait 10  # Wait up to 10 minutes
 161 ```
 162 
 163 ## Debug Logs During Tests
 164 
 165 ### Enable Debug Logs
 166 
 167 ```bash
 168 # List current log levels
 169 sf apex list log --target-org my-sandbox
 170 
 171 # Tail logs in real-time
 172 sf apex tail log --target-org my-sandbox --color
 173 ```
 174 
 175 ### Get Specific Log
 176 
 177 ```bash
 178 sf apex get log \
 179   --log-id 07Lxx0000000000AAA \
 180   --target-org my-sandbox
 181 ```
 182 
 183 ## Useful Flags
 184 
 185 | Flag | Description |
 186 |------|-------------|
 187 | `--code-coverage` | Include coverage in results |
 188 | `--detailed-coverage` | Line-by-line coverage (slower) |
 189 | `--result-format` | Output format (human, json, junit, tap) |
 190 | `--output-dir` | Save results to directory |
 191 | `--synchronous` | Wait for completion (default) |
 192 | `--wait` | Max minutes to wait |
 193 | `--async` | Return immediately with run ID |
 194 | `--verbose` | Show additional details |
 195 | `--concise` | Suppress passing test details (show only failures) |
 196 | `--poll-interval <seconds>` | Customize polling interval (v2.116.6+) |
 197 
 198 ## Common Patterns
 199 
 200 ### Full Test Run with Coverage Report
 201 
 202 ```bash
 203 sf apex run test \
 204   --test-level RunLocalTests \
 205   --code-coverage \
 206   --result-format json \
 207   --output-dir ./test-results \
 208   --target-org my-sandbox \
 209   --wait 30
 210 ```
 211 
 212 ### Quick Validation (Single Test)
 213 
 214 ```bash
 215 sf apex run test \
 216   --tests AccountServiceTest.testCreate \
 217   --target-org my-sandbox
 218 ```
 219 
 220 ### CI/CD Pipeline Pattern
 221 
 222 ```bash
 223 # Run tests with JUnit output for CI tools
 224 sf apex run test \
 225   --test-level RunLocalTests \
 226   --result-format junit \
 227   --output-dir ./test-results \
 228   --code-coverage \
 229   --target-org ci-sandbox \
 230   --wait 60
 231 
 232 # Check exit code
 233 if [ $? -ne 0 ]; then
 234   echo "Tests failed!"
 235   exit 1
 236 fi
 237 ```
 238 
 239 ### Coverage Validation
 240 
 241 ```bash
 242 # Run tests and check minimum coverage
 243 sf apex run test \
 244   --test-level RunLocalTests \
 245   --code-coverage \
 246   --result-format json \
 247   --output-dir ./test-results \
 248   --target-org my-sandbox
 249 
 250 # Parse coverage from JSON (requires jq)
 251 coverage=$(jq '.result.summary.orgWideCoverage' ./test-results/*.json | tr -d '"' | tr -d '%')
 252 if [ "$coverage" -lt 75 ]; then
 253   echo "Coverage $coverage% is below 75% threshold!"
 254   exit 1
 255 fi
 256 ```
 257 
 258 ## Troubleshooting
 259 
 260 ### Test Timeout
 261 
 262 ```bash
 263 # Increase wait time for long-running tests
 264 sf apex run test \
 265   --test-level RunAllTestsInOrg \
 266   --wait 120 \
 267   --target-org my-sandbox
 268 ```
 269 
 270 ### No Test Results
 271 
 272 Check if tests exist:
 273 ```bash
 274 sf apex list test --target-org my-sandbox
 275 ```
 276 
 277 ### Permission Errors
 278 
 279 Ensure user has "Author Apex" permission and API access.
 280 
 281 ### Async Test Not Completing
 282 
 283 Check system status:
 284 ```bash
 285 sf apex get test \
 286   --test-run-id 707xx0000000000AAA \
 287   --target-org my-sandbox
 288 ```
