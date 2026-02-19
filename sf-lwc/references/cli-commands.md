<!-- Parent: sf-lwc/SKILL.md -->
   1 # Salesforce CLI Commands for LWC Development
   2 
   3 ## Quick Reference
   4 
   5 | Task | Command |
   6 |------|---------|
   7 | Create component | `sf lightning generate component --name myComp --type lwc` |
   8 | Run all tests | `sf lightning lwc test run` |
   9 | Deploy component | `sf project deploy start --source-dir force-app/.../lwc/myComp` |
  10 | Create message channel | Manual XML: `force-app/.../messageChannels/MyChannel.messageChannel-meta.xml` |
  11 
  12 ---
  13 
  14 ## Component Generation
  15 
  16 ### Create New LWC
  17 
  18 ```bash
  19 # Basic component
  20 sf lightning generate component \
  21   --name accountList \
  22   --type lwc \
  23   --output-dir force-app/main/default/lwc
  24 
  25 # Creates:
  26 # force-app/main/default/lwc/accountList/
  27 # ├── accountList.js
  28 # ├── accountList.html
  29 # └── accountList.js-meta.xml
  30 ```
  31 
  32 ### Generate with Jest Test
  33 
  34 ```bash
  35 # The test file must be created manually in __tests__ folder
  36 mkdir -p force-app/main/default/lwc/accountList/__tests__
  37 touch force-app/main/default/lwc/accountList/__tests__/accountList.test.js
  38 ```
  39 
  40 ---
  41 
  42 ## Testing
  43 
  44 ### Run All Jest Tests
  45 
  46 ```bash
  47 sf lightning lwc test run
  48 ```
  49 
  50 ### Run Specific Test File
  51 
  52 ```bash
  53 sf lightning lwc test run \
  54   --spec force-app/main/default/lwc/accountList/__tests__/accountList.test.js
  55 ```
  56 
  57 ### Watch Mode (Development)
  58 
  59 ```bash
  60 # Re-runs tests when files change
  61 sf lightning lwc test run --watch
  62 ```
  63 
  64 ### Coverage Report
  65 
  66 ```bash
  67 # Generate HTML coverage report
  68 sf lightning lwc test run --coverage
  69 # Report at: coverage/lcov-report/index.html
  70 ```
  71 
  72 ### Debug Tests
  73 
  74 ```bash
  75 # Run with Node debugger
  76 sf lightning lwc test run --debug
  77 
  78 # Then in Chrome: chrome://inspect
  79 ```
  80 
  81 ### Update Snapshots
  82 
  83 ```bash
  84 sf lightning lwc test run --update-snapshot
  85 ```
  86 
  87 ---
  88 
  89 ## Linting
  90 
  91 ### Run ESLint
  92 
  93 > **Note**: `sf lightning lint` does not exist. Use `npx eslint` directly or `sf code-analyzer run`.
  94 
  95 ```bash
  96 # Lint LWC files with ESLint (requires @salesforce/eslint-config-lwc)
  97 npx eslint force-app/main/default/lwc
  98 
  99 # Lint specific component
 100 npx eslint force-app/main/default/lwc/accountList
 101 
 102 # Auto-fix issues
 103 npx eslint force-app/main/default/lwc --fix
 104 
 105 # Or use Code Analyzer (includes ESLint + PMD + RetireJS)
 106 sf code-analyzer run --workspace force-app/main/default/lwc
 107 ```
 108 
 109 ---
 110 
 111 ## Deployment
 112 
 113 ### Deploy Single Component
 114 
 115 ```bash
 116 sf project deploy start \
 117   --source-dir force-app/main/default/lwc/accountList \
 118   --target-org my-sandbox
 119 ```
 120 
 121 ### Deploy Multiple Components
 122 
 123 ```bash
 124 sf project deploy start \
 125   --source-dir force-app/main/default/lwc/accountList \
 126   --source-dir force-app/main/default/lwc/accountForm \
 127   --target-org my-sandbox
 128 ```
 129 
 130 ### Deploy with Related Apex
 131 
 132 ```bash
 133 sf project deploy start \
 134   --source-dir force-app/main/default/lwc/accountList \
 135   --source-dir force-app/main/default/classes/AccountController.cls \
 136   --target-org my-sandbox
 137 ```
 138 
 139 ### Validate Without Deploying
 140 
 141 ```bash
 142 sf project deploy start \
 143   --source-dir force-app/main/default/lwc \
 144   --target-org my-sandbox \
 145   --dry-run
 146 ```
 147 
 148 ---
 149 
 150 ## Retrieval
 151 
 152 ### Retrieve Component from Org
 153 
 154 ```bash
 155 sf project retrieve start \
 156   --metadata LightningComponentBundle:accountList \
 157   --target-org my-sandbox \
 158   --output-dir force-app/main/default
 159 ```
 160 
 161 ### Retrieve All LWC
 162 
 163 ```bash
 164 sf project retrieve start \
 165   --metadata LightningComponentBundle \
 166   --target-org my-sandbox
 167 ```
 168 
 169 ---
 170 
 171 ## Local Development
 172 
 173 ### Preview Components Locally
 174 
 175 > **Note**: `sf lightning dev-server` was deprecated. Local Dev is now built into sf CLI.
 176 
 177 ```bash
 178 # Open component preview in browser (built into sf CLI, no plugin needed)
 179 sf org open --source-file force-app/main/default/lwc/myComp/myComp.js --target-org my-sandbox
 180 
 181 # Open specific Lightning page for testing
 182 sf org open --target-org my-sandbox --path /lightning/setup/FlexiPageList/home
 183 ```
 184 
 185 ---
 186 
 187 ## Message Channels
 188 
 189 ### Create Message Channel
 190 
 191 > **Note**: There is no `sf lightning generate messageChannel` command. Message Channels are created as metadata XML files manually.
 192 
 193 ```bash
 194 # Create the directory if it doesn't exist
 195 mkdir -p force-app/main/default/messageChannels
 196 
 197 # Create the XML file manually:
 198 # force-app/main/default/messageChannels/RecordSelected.messageChannel-meta.xml
 199 ```
 200 
 201 ### Deploy Message Channel
 202 
 203 ```bash
 204 sf project deploy start \
 205   --metadata LightningMessageChannel:RecordSelected__c \
 206   --target-org my-sandbox
 207 ```
 208 
 209 ---
 210 
 211 ## Debugging
 212 
 213 ### Open Component in Browser
 214 
 215 ```bash
 216 # Open Lightning App Builder
 217 sf org open --target-org my-sandbox --path /lightning/setup/FlexiPageList/home
 218 ```
 219 
 220 ### View Debug Logs
 221 
 222 ```bash
 223 # Tail logs while testing
 224 sf apex tail log --target-org my-sandbox --color
 225 ```
 226 
 227 ### Check Deployment Errors
 228 
 229 ```bash
 230 # If deployment fails, check status
 231 sf project deploy report --job-id <job-id>
 232 ```
 233 
 234 ---
 235 
 236 ## Package Development
 237 
 238 ### Create Unlocked Package
 239 
 240 ```bash
 241 # Create package
 242 sf package create \
 243   --name "My LWC Package" \
 244   --package-type Unlocked \
 245   --path force-app
 246 
 247 # Create version
 248 sf package version create \
 249   --package "My LWC Package" \
 250   --installation-key test1234 \
 251   --wait 10
 252 ```
 253 
 254 ---
 255 
 256 ## Jest Configuration
 257 
 258 ### Setup Jest (if not already configured)
 259 
 260 ```bash
 261 # Install Jest dependencies
 262 npm install @salesforce/sfdx-lwc-jest --save-dev
 263 
 264 # Add to package.json scripts
 265 {
 266   "scripts": {
 267     "test:unit": "sfdx-lwc-jest",
 268     "test:unit:watch": "sfdx-lwc-jest --watch",
 269     "test:unit:debug": "sfdx-lwc-jest --debug",
 270     "test:unit:coverage": "sfdx-lwc-jest --coverage"
 271   }
 272 }
 273 ```
 274 
 275 ### Jest Config (jest.config.js)
 276 
 277 ```javascript
 278 const { jestConfig } = require('@salesforce/sfdx-lwc-jest/config');
 279 
 280 module.exports = {
 281     ...jestConfig,
 282     modulePathIgnorePatterns: ['<rootDir>/.localdevserver'],
 283     testTimeout: 10000
 284 };
 285 ```
 286 
 287 ---
 288 
 289 ## Useful Patterns
 290 
 291 ### Deploy and Test Flow
 292 
 293 ```bash
 294 # 1. Run local tests
 295 sf lightning lwc test run
 296 
 297 # 2. Deploy to sandbox
 298 sf project deploy start \
 299   --source-dir force-app/main/default/lwc/myComponent \
 300   --target-org my-sandbox
 301 
 302 # 3. Open org to test
 303 sf org open --target-org my-sandbox
 304 ```
 305 
 306 ### CI/CD Pipeline Pattern
 307 
 308 ```bash
 309 #!/bin/bash
 310 
 311 # Lint
 312 npx eslint ./force-app/main/default/lwc || exit 1
 313 
 314 # Test
 315 sf lightning lwc test run --coverage || exit 1
 316 
 317 # Validate deployment
 318 sf project deploy start \
 319   --source-dir force-app/main/default/lwc \
 320   --target-org ci-sandbox \
 321   --dry-run || exit 1
 322 
 323 # Deploy if validation passes
 324 sf project deploy start \
 325   --source-dir force-app/main/default/lwc \
 326   --target-org ci-sandbox
 327 ```
 328 
 329 ### Watch and Auto-Deploy
 330 
 331 ```bash
 332 # Using nodemon or similar
 333 npx nodemon \
 334   --watch "force-app/main/default/lwc/**/*" \
 335   --exec "sf project deploy start --source-dir force-app/main/default/lwc --target-org my-sandbox"
 336 ```
 337 
 338 ---
 339 
 340 ## Troubleshooting
 341 
 342 ### Component Not Visible in App Builder
 343 
 344 1. Check `isExposed` is `true` in meta.xml
 345 2. Check `targets` include the desired location
 346 3. Verify deployment was successful
 347 
 348 ```bash
 349 # Re-deploy with verbose output
 350 sf project deploy start \
 351   --source-dir force-app/main/default/lwc/myComponent \
 352   --target-org my-sandbox \
 353   --verbose
 354 ```
 355 
 356 ### Jest Tests Not Finding Component
 357 
 358 ```bash
 359 # Clear Jest cache
 360 npx jest --clearCache
 361 
 362 # Re-run tests
 363 sf lightning lwc test run
 364 ```
 365 
 366 ### Wire Service Not Working
 367 
 368 1. Verify `cacheable=true` on Apex method
 369 2. Check reactive parameter has `$` prefix
 370 3. Verify Apex method is accessible
 371 
 372 ```bash
 373 # Test Apex method directly
 374 sf apex run --target-org my-sandbox <<< "System.debug(MyController.getRecords());"
 375 ```
 376 
 377 ### Deployment Conflicts
 378 
 379 ```bash
 380 # Check what's different
 381 sf project retrieve start \
 382   --metadata LightningComponentBundle:myComponent \
 383   --target-org my-sandbox \
 384   --output-dir temp-retrieve
 385 
 386 # Compare and resolve
 387 diff -r force-app/main/default/lwc/myComponent temp-retrieve/force-app/.../myComponent
 388 ```
 389 
 390 ---
 391 
 392 ## Static Analysis (Code Analyzer v5)
 393 
 394 ### Salesforce Code Analyzer
 395 
 396 Code Analyzer v5 (`@salesforce/plugin-code-analyzer`) validates LWC files for SLDS 2 compliance, accessibility, and security.
 397 
 398 ```bash
 399 # Install Code Analyzer v5 plugin
 400 sf plugins install @salesforce/plugin-code-analyzer
 401 
 402 # Run scan on LWC components
 403 sf code-analyzer run \
 404   --workspace force-app/main/default/lwc \
 405   --output-format html \
 406   --output-file lwc-scan-results.html
 407 
 408 # Run with specific rules
 409 sf code-analyzer run \
 410   --workspace force-app/main/default/lwc \
 411   --rule-selector "Category:Best Practices,Security"
 412 ```
 413 
 414 > **Migration from sfdx-scanner**: v5 uses `--workspace` instead of `--target`, `--output-format` instead of `--format`, `--output-file` instead of `--outfile`, and `--rule-selector` instead of `--engine`/`--category`.
 415 
 416 ### SLDS 2 Compliance Checks
 417 
 418 ```bash
 419 # Check for hardcoded colors (breaks dark mode)
 420 rg -n '#[0-9A-Fa-f]{3,8}' force-app/main/default/lwc/**/*.css
 421 
 422 # Find deprecated SLDS 1 tokens
 423 rg -n '\-\-lwc\-' force-app/main/default/lwc/**/*.css
 424 
 425 # Find missing alternative-text on icons
 426 rg -n '<lightning-icon' force-app/main/default/lwc/**/*.html | \
 427   rg -v 'alternative-text'
 428 
 429 # Check for !important overrides
 430 rg -n '!important' force-app/main/default/lwc/**/*.css
 431 ```
 432 
 433 ### Dark Mode Validation
 434 
 435 ```bash
 436 # Find all hardcoded colors that may break dark mode
 437 rg -n 'rgb\(|rgba\(|#[0-9A-Fa-f]{3,8}' \
 438   force-app/main/default/lwc/**/*.css \
 439   --glob '!**/node_modules/**'
 440 
 441 # Verify CSS variables usage (SLDS 2 global hooks)
 442 rg -n '\-\-slds-g-color' force-app/main/default/lwc/**/*.css
 443 ```
 444 
 445 ---
 446 
 447 ## GraphQL Debugging
 448 
 449 ### GraphQL Wire Service
 450 
 451 ```bash
 452 # View GraphQL queries in debug mode (enable in Setup → Debug Logs)
 453 sf apex tail log --target-org my-sandbox --color
 454 # Note: Debug levels are configured via TraceFlag records in Setup, not CLI flags
 455 
 456 # Test GraphQL query via Anonymous Apex (for syntax validation)
 457 sf apex run --target-org my-sandbox <<'EOF'
 458 // GraphQL syntax can't be tested directly in Apex
 459 // But you can verify field access:
 460 System.debug([SELECT Id, Name FROM Account LIMIT 1]);
 461 EOF
 462 ```
 463 
 464 ### GraphQL Troubleshooting
 465 
 466 | Issue | Possible Cause | Solution |
 467 |-------|---------------|----------|
 468 | "Field not found" | FLS restriction | Check user has read access |
 469 | "Object not supported" | GraphQL scope | Not all objects support GraphQL |
 470 | Cursor pagination fails | Invalid cursor | Use exact cursor from `pageInfo.endCursor` |
 471 | Null data | Query error | Check `errors` array in wire result |
 472 
 473 ### Monitor GraphQL Performance
 474 
 475 ```bash
 476 # Open Developer Console for network inspection
 477 sf org open --target-org my-sandbox \
 478   --path /lightning/setup/ApexDebugLogDetail/home
 479 
 480 # View Event Monitoring logs (if enabled)
 481 sf data query \
 482   --query "SELECT EventType, LogDate FROM EventLogFile WHERE EventType='LightningPageView' ORDER BY LogDate DESC LIMIT 5" \
 483   --target-org my-sandbox
 484 ```
 485 
 486 ---
 487 
 488 ## Workspace API (Console Apps)
 489 
 490 ### Console Detection
 491 
 492 ```bash
 493 # Check if an app is a Console app
 494 sf data query \
 495   --query "SELECT DeveloperName, NavType FROM AppDefinition WHERE NavType='Console'" \
 496   --target-org my-sandbox
 497 
 498 # List all Lightning Apps
 499 sf data query \
 500   --query "SELECT DeveloperName, NavType, Label FROM AppDefinition ORDER BY Label" \
 501   --target-org my-sandbox
 502 ```
 503 
 504 ### Console App Testing
 505 
 506 ```bash
 507 # Open Service Console
 508 sf org open --target-org my-sandbox \
 509   --path /lightning/app/standard__ServiceConsole
 510 
 511 # Open Sales Console
 512 sf org open --target-org my-sandbox \
 513   --path /lightning/app/standard__SalesConsole
 514 
 515 # Open custom console app
 516 sf org open --target-org my-sandbox \
 517   --path /lightning/app/c__MyConsoleApp
 518 ```
