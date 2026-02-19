<!-- Parent: sf-deploy/SKILL.md -->
   1 # Salesforce Deployment Workflow Examples
   2 
   3 This file contains practical examples of common Salesforce deployment scenarios using the sf-deploy skill.
   4 
   5 ## Example 1: Basic Production Deployment
   6 
   7 ### User Request:
   8 ```
   9 "Deploy my changes to production with full test coverage"
  10 ```
  11 
  12 ### Skill Execution:
  13 
  14 1. **Pre-deployment checks**
  15    ```bash
  16    sf org display --target-org production
  17    sf project deploy start --dry-run --test-level RunLocalTests --target-org production --wait 30
  18    ```
  19 
  20 2. **Validation output**
  21    ```
  22    ✓ Deployment validation succeeded
  23    ✓ Tests passed: 145/145 (92% coverage)
  24    ✓ Components validated: 23
  25    ```
  26 
  27 3. **Quick deploy** (using validation ID)
  28    ```bash
  29    sf project deploy quick --job-id 0Af5g00000XXXXX --target-org production
  30    ```
  31 
  32 4. **Final output**
  33    ```
  34    ## Salesforce Deployment Report
  35 
  36    ✓ Status: Succeeded
  37    ✓ Components Deployed: 23/23
  38    ✓ Tests Passed: 145/145 (92% coverage)
  39    ✓ Duration: 8m 32s
  40 
  41    ### Deployed Components:
  42    - ApexClass: AccountController, ContactTriggerHandler, LeadProcessor
  43    - ApexTrigger: AccountTrigger, ContactTrigger
  44    - LightningComponentBundle: accountCard, contactList
  45    ```
  46 
  47 ---
  48 
  49 ## Example 2: Selective Component Deployment
  50 
  51 ### User Request:
  52 ```
  53 "Deploy only the new Lightning Web Components to sandbox"
  54 ```
  55 
  56 ### Skill Execution:
  57 
  58 1. **Identify LWC components**
  59    ```bash
  60    # Find all LWC components
  61    ls -R force-app/main/default/lwc/
  62    ```
  63 
  64 2. **Deploy specific directory**
  65    ```bash
  66    sf project deploy start \
  67      --source-dir force-app/main/default/lwc \
  68      --target-org dev-sandbox \
  69      --test-level NoTestRun \
  70      --wait 15
  71    ```
  72 
  73 3. **Output**
  74    ```
  75    ✓ Deployment succeeded
  76    ✓ Components Deployed:
  77      - accountCard (LWC)
  78      - contactList (LWC)
  79      - opportunityBoard (LWC)
  80    ```
  81 
  82 ---
  83 
  84 ## Example 3: Hotfix Deployment
  85 
  86 ### User Request:
  87 ```
  88 "I need to deploy an urgent bug fix in AccountController to production"
  89 ```
  90 
  91 ### Skill Execution:
  92 
  93 1. **Verify the specific file**
  94    ```bash
  95    cat force-app/main/default/classes/AccountController.cls
  96    ```
  97 
  98 2. **Run targeted tests**
  99    ```bash
 100    sf apex test run \
 101      --tests AccountControllerTest \
 102      --target-org production \
 103      --wait 5
 104    ```
 105 
 106 3. **Deploy single class**
 107    ```bash
 108    sf project deploy start \
 109      --source-dir force-app/main/default/classes/AccountController.cls \
 110      --target-org production \
 111      --test-level RunSpecifiedTests \
 112      --tests AccountControllerTest \
 113      --wait 10
 114    ```
 115 
 116 4. **Verification**
 117    ```bash
 118    sf project deploy report --job-id <job-id> --target-org production
 119    ```
 120 
 121 ---
 122 
 123 ## Example 4: Manifest-Based Deployment
 124 
 125 ### User Request:
 126 ```
 127 "Deploy using the package.xml manifest for release v2.3"
 128 ```
 129 
 130 ### Skill Execution:
 131 
 132 1. **Read manifest file**
 133    ```bash
 134    cat manifest/package-v2.3.xml
 135    ```
 136 
 137 2. **Validate deployment**
 138    ```bash
 139    sf project deploy start \
 140      --manifest manifest/package-v2.3.xml \
 141      --target-org production \
 142      --dry-run \
 143      --test-level RunLocalTests \
 144      --wait 30
 145    ```
 146 
 147 3. **Quick deploy**
 148    ```bash
 149    sf project deploy quick --job-id 0Af5g00000XXXXX --target-org production
 150    ```
 151 
 152 ---
 153 
 154 ## Example 5: Scratch Org Development Workflow
 155 
 156 ### User Request:
 157 ```
 158 "Create a scratch org and deploy my feature branch"
 159 ```
 160 
 161 ### Skill Execution:
 162 
 163 1. **Create scratch org**
 164    ```bash
 165    sf org create scratch \
 166      --definition-file config/project-scratch-def.json \
 167      --alias feature-branch-123 \
 168      --duration-days 7 \
 169      --set-default
 170    ```
 171 
 172 2. **Push source**
 173    ```bash
 174    sf project deploy start --target-org feature-branch-123
 175    ```
 176 
 177 3. **Assign permission sets**
 178    ```bash
 179    sf org assign permset --name AdminPermSet --target-org feature-branch-123
 180    ```
 181 
 182 4. **Import test data**
 183    ```bash
 184    sf data import tree --plan data/sample-data-plan.json --target-org feature-branch-123
 185    ```
 186 
 187 5. **Open org**
 188    ```bash
 189    sf org open --target-org feature-branch-123
 190    ```
 191 
 192 ---
 193 
 194 ## Example 6: Deployment Rollback
 195 
 196 ### User Request:
 197 ```
 198 "The deployment failed, I need to rollback to the previous version"
 199 ```
 200 
 201 ### Skill Execution:
 202 
 203 1. **Retrieve current production metadata** (if not backed up)
 204    ```bash
 205    sf project retrieve start \
 206      --manifest manifest/package-production.xml \
 207      --target-org production
 208    ```
 209 
 210 2. **Check out previous version from git**
 211    ```bash
 212    git checkout v2.2-stable
 213    ```
 214 
 215 3. **Deploy previous version**
 216    ```bash
 217    sf project deploy start \
 218      --manifest manifest/package-v2.2.xml \
 219      --target-org production \
 220      --test-level RunLocalTests \
 221      --wait 30
 222    ```
 223 
 224 4. **Verify rollback**
 225    ```bash
 226    sf org open --target-org production
 227    ```
 228 
 229 ---
 230 
 231 ## Example 7: Destructive Changes
 232 
 233 ### User Request:
 234 ```
 235 "Remove the deprecated CustomObject__c and old Apex classes"
 236 ```
 237 
 238 ### Skill Execution:
 239 
 240 1. **Create destructiveChanges.xml**
 241    ```xml
 242    <?xml version="1.0" encoding="UTF-8"?>
 243    <Package xmlns="http://soap.sforce.com/2006/04/metadata">
 244        <types>
 245            <members>DeprecatedClass1</members>
 246            <members>DeprecatedClass2</members>
 247            <name>ApexClass</name>
 248        </types>
 249        <types>
 250            <members>CustomObject__c</members>
 251            <name>CustomObject</name>
 252        </types>
 253        <version>58.0</version>
 254    </Package>
 255    ```
 256 
 257 2. **Deploy with destructive changes**
 258    ```bash
 259    sf project deploy start \
 260      --manifest manifest/package.xml \
 261      --post-destructive-changes manifest/destructiveChanges.xml \
 262      --target-org production \
 263      --test-level RunLocalTests \
 264      --wait 30
 265    ```
 266 
 267 ---
 268 
 269 ## Example 8: Multi-Environment Deployment
 270 
 271 ### User Request:
 272 ```
 273 "Deploy to dev, then staging, then production after each passes validation"
 274 ```
 275 
 276 ### Skill Execution:
 277 
 278 1. **Deploy to Dev**
 279    ```bash
 280    sf project deploy start --target-org dev --test-level NoTestRun --wait 10
 281    ```
 282 
 283 2. **Deploy to Staging**
 284    ```bash
 285    sf project deploy start --target-org staging --test-level RunLocalTests --wait 20
 286    ```
 287 
 288 3. **Validate Production**
 289    ```bash
 290    sf project deploy start --target-org production --dry-run --test-level RunLocalTests --wait 30
 291    ```
 292 
 293 4. **Deploy to Production** (after manual approval)
 294    ```bash
 295    sf project deploy quick --job-id <validation-job-id> --target-org production
 296    ```
 297 
 298 ---
 299 
 300 ## Example 9: Code Coverage Analysis
 301 
 302 ### User Request:
 303 ```
 304 "Check my code coverage and identify classes that need more tests"
 305 ```
 306 
 307 ### Skill Execution:
 308 
 309 1. **Run all tests**
 310    ```bash
 311    sf apex test run \
 312      --test-level RunLocalTests \
 313      --target-org dev \
 314      --code-coverage \
 315      --result-format human \
 316      --wait 15
 317    ```
 318 
 319 2. **Analyze coverage report**
 320    ```
 321    Overall Code Coverage: 87%
 322 
 323    Classes with <75% coverage:
 324    - LeadProcessor: 62%
 325    - OpportunityHelper: 71%
 326    - AccountBatchProcessor: 45%
 327 
 328    Recommendations:
 329    1. Add test methods for LeadProcessor.processLeads()
 330    2. Test error handling in OpportunityHelper
 331    3. Create comprehensive tests for AccountBatchProcessor
 332    ```
 333 
 334 ---
 335 
 336 ## Example 10: Deployment Error Recovery
 337 
 338 ### User Request:
 339 ```
 340 "Deployment failed with 'INVALID_CROSS_REFERENCE_KEY' error"
 341 ```
 342 
 343 ### Skill Execution:
 344 
 345 1. **Analyze error**
 346    ```
 347    Error: INVALID_CROSS_REFERENCE_KEY
 348    Component: CustomObject__c.SomeLookupField__c
 349    Message: Field references non-existent object
 350    ```
 351 
 352 2. **Identify dependency**
 353    ```bash
 354    grep -r "ReferencedObject__c" force-app/
 355    ```
 356 
 357 3. **Solution provided**
 358    ```
 359    The error indicates that SomeLookupField__c references an object
 360    that doesn't exist in the target org.
 361 
 362    Solutions:
 363    1. Deploy the referenced object first
 364    2. Include both objects in the same deployment
 365    3. Update the field to reference a different object
 366    4. Check if the referenced object exists: sf org list metadata --metadata-type CustomObject
 367    ```
 368 
 369 4. **Deploy with dependencies**
 370    ```bash
 371    # Include both in manifest
 372    sf project deploy start \
 373      --manifest manifest/package-with-dependencies.xml \
 374      --target-org production
 375    ```
 376 
 377 ---
 378 
 379 ## Tips for Successful Deployments
 380 
 381 1. **Always validate first** - Use `--dry-run` for production
 382 2. **Monitor test execution** - Watch for test failures early
 383 3. **Check code coverage** - Ensure >75% minimum
 384 4. **Deploy incrementally** - Smaller deployments are easier to troubleshoot
 385 5. **Use version control** - Tag releases for easy rollback
 386 6. **Document changes** - Keep deployment logs
 387 7. **Test in sandbox** - Never test directly in production
 388 8. **Handle dependencies** - Deploy referenced metadata first
 389 
 390 ---
 391 
 392 *These examples demonstrate common patterns. The sf-deploy skill adapts to your specific use case and provides guided assistance.*
