<!-- Parent: sf-deploy/SKILL.md -->
   1 # Deployment Report Template
   2 
   3 Standard output format for Salesforce deployment summaries.
   4 
   5 ## Full Report Format
   6 
   7 ```markdown
   8 ## Salesforce Deployment Report
   9 
  10 ### Pre-Deployment Checks
  11 ✓ Org authenticated: <org-alias> (<org-id>)
  12 ✓ Project validated: sfdx-project.json found
  13 ✓ Components identified: X classes, Y triggers, Z components
  14 
  15 ### Deployment Execution
  16 → Deployment initiated: <timestamp>
  17 → Job ID: <deployment-job-id>
  18 → Test Level: RunLocalTests
  19 
  20 ### Results
  21 ✓ Status: Succeeded
  22 ✓ Components Deployed: X/X
  23 ✓ Tests Passed: Y/Y (Z% coverage)
  24 
  25 ### Deployed Components
  26 - ApexClass: AccountController, ContactTriggerHandler
  27 - LightningComponentBundle: accountCard, contactList
  28 - CustomObject: CustomObject__c
  29 
  30 ### Next Steps
  31 1. Verify functionality in target org
  32 2. Monitor for any post-deployment issues
  33 3. Update documentation and changelog
  34 ```
  35 
  36 ## Compact Report Format
  37 
  38 For quick summaries:
  39 
  40 ```markdown
  41 ✓ Deployment: [org-alias] | Job: [job-id]
  42   Components: X/X | Tests: Y/Y (Z% coverage)
  43   Status: Succeeded
  44 ```
  45 
  46 ## Failure Report Format
  47 
  48 ```markdown
  49 ## Deployment Failed
  50 
  51 ### Error Summary
  52 ✗ Status: Failed
  53 ✗ Failed Components: 2/15
  54 
  55 ### Errors
  56 1. ApexClass: MyController
  57    - Line 45: Variable 'acc' does not exist
  58 
  59 2. CustomField: Account.Custom__c
  60    - Missing referenced field: Contact.Email
  61 
  62 ### Suggested Actions
  63 1. Fix compilation error in MyController.cls:45
  64 2. Deploy Contact.Email field before Account.Custom__c
  65 3. Re-run deployment after fixes
  66 ```
  67 
  68 ## CI/CD Pipeline Output
  69 
  70 For automated pipelines (GitHub Actions, GitLab CI):
  71 
  72 ```yaml
  73 deployment:
  74   status: success|failure
  75   job_id: "0Af..."
  76   org: "<alias>"
  77   components:
  78     total: 15
  79     deployed: 15
  80     failed: 0
  81   tests:
  82     total: 45
  83     passed: 45
  84     failed: 0
  85     coverage: 87.5
  86   duration: "2m 34s"
  87   errors: []
  88 ```
