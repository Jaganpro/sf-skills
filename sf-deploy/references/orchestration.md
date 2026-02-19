<!-- Parent: sf-deploy/SKILL.md -->
   1 # Multi-Skill Orchestration: sf-deploy Perspective
   2 
   3 This document details how sf-deploy fits into the multi-skill workflow for Salesforce development.
   4 
   5 ---
   6 
   7 ## Standard Orchestration Order
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────────────┐
  11 │  STANDARD MULTI-SKILL ORCHESTRATION ORDER                                   │
  12 ├─────────────────────────────────────────────────────────────────────────────┤
  13 │  1. sf-metadata                                                             │
  14 │     └── Create object/field definitions (LOCAL files)                       │
  15 │                                                                             │
  16 │  2. sf-flow                                                                 │
  17 │     └── Create flow definitions (LOCAL files)                               │
  18 │                                                                             │
  19 │  3. sf-deploy  ◀── YOU ARE HERE                                            │
  20 │     └── Deploy all metadata (REMOTE)                                        │
  21 │                                                                             │
  22 │  4. sf-data                                                                 │
  23 │     └── Create test data (REMOTE - objects must exist!)                     │
  24 └─────────────────────────────────────────────────────────────────────────────┘
  25 ```
  26 
  27 ---
  28 
  29 ## Why sf-deploy Goes Third (Not Last)
  30 
  31 sf-deploy is the **bridge** between local files and the org:
  32 
  33 | Before sf-deploy | After sf-deploy |
  34 |------------------|-----------------|
  35 | Metadata exists locally | Metadata exists in org |
  36 | Flows reference objects | Flows can run |
  37 | Data can't be created | sf-data can create records |
  38 
  39 **sf-data REQUIRES deployed objects**. The error `SObject type 'X' not supported` means objects weren't deployed.
  40 
  41 ---
  42 
  43 ## Deploy Order WITHIN sf-deploy
  44 
  45 When deploying multiple metadata types:
  46 
  47 ```
  48 ┌─────────────────────────────────────────────────────────────────────────────┐
  49 │  INTERNAL DEPLOY ORDER                                                      │
  50 ├─────────────────────────────────────────────────────────────────────────────┤
  51 │  1. Custom Objects & Fields                                                 │
  52 │     └── Objects must exist before anything references them                  │
  53 │                                                                             │
  54 │  2. Permission Sets                                                         │
  55 │     └── Field-Level Security requires fields to exist                       │
  56 │                                                                             │
  57 │  3. Apex Classes                                                            │
  58 │     └── @InvocableMethod for Flow actions                                   │
  59 │                                                                             │
  60 │  4. Flows (as Draft)                                                        │
  61 │     └── Flows reference fields and Apex                                     │
  62 │                                                                             │
  63 │  5. Activate Flows                                                          │
  64 │     └── Change status Draft → Active                                        │
  65 └─────────────────────────────────────────────────────────────────────────────┘
  66 ```
  67 
  68 **Why this order?**
  69 - Flows need fields to exist
  70 - Users need Permission Sets for field visibility
  71 - Triggers may depend on active flows
  72 - Draft flows can be tested before activation
  73 
  74 ---
  75 
  76 ## Integration + Agentforce Extended Order
  77 
  78 When deploying agents with external API integrations:
  79 
  80 ```
  81 ┌─────────────────────────────────────────────────────────────────────────────┐
  82 │  AGENTFORCE DEPLOYMENT ORDER                                                │
  83 ├─────────────────────────────────────────────────────────────────────────────┤
  84 │  1. sf-connected-apps → Create OAuth Connected App                          │
  85 │  2. sf-integration    → Create Named Credential + External Service          │
  86 │  3. sf-apex           → Create @InvocableMethod (if needed)                 │
  87 │  4. sf-flow           → Create Flow wrapper                                 │
  88 │                                                                             │
  89 │  5. sf-deploy         ◀── FIRST DEPLOYMENT                                 │
  90 │     └── Deploy: Objects, Fields, Permission Sets, Apex, Flows              │
  91 │                                                                             │
  92 │  6. sf-ai-agentscript → Create agent with flow:// target                   │
  93 │                                                                             │
  94 │  7. sf-deploy         ◀── SECOND DEPLOYMENT (Agent Publish)                │
  95 │     └── sf agent publish authoring-bundle --api-name [AgentName]           │
  96 │                                                                             │
  97 │  8. sf-data           → Create test data                                    │
  98 └─────────────────────────────────────────────────────────────────────────────┘
  99 ```
 100 
 101 ---
 102 
 103 ## Common Deployment Errors from Wrong Order
 104 
 105 | Error | Cause | Fix |
 106 |-------|-------|-----|
 107 | `Invalid reference: Quote__c` | Object not deployed | Deploy objects first |
 108 | `Field does not exist: Status__c` | Field not deployed | Deploy fields first |
 109 | `no CustomObject named X found` | Permission Set deployed before object | Deploy objects, then Permission Sets |
 110 | `SObject type 'X' not supported` | sf-data ran before deploy | Deploy before creating data |
 111 | `Flow is invalid` | Flow references missing object | Deploy objects before flows |
 112 | `Flow not found` | Agent references undeploy flow | Deploy flows before agent publish |
 113 
 114 ---
 115 
 116 ## Two-Step Deployment Pattern (Recommended)
 117 
 118 Always validate before deploying:
 119 
 120 ```bash
 121 # Step 1: Dry-run validation
 122 sf project deploy start --dry-run --source-dir force-app --target-org alias
 123 
 124 # Step 2: Actual deployment (only if validation passes)
 125 sf project deploy start --source-dir force-app --target-org alias
 126 ```
 127 
 128 ---
 129 
 130 ## Cross-Skill Dependencies
 131 
 132 Before deploying, verify these prerequisites:
 133 
 134 | Dependency | Check Command | Required For |
 135 |------------|---------------|--------------|
 136 | TAF Package | `sf package installed list` | TAF trigger pattern |
 137 | Custom Objects | `sf sobject describe` | Apex/Flow field refs |
 138 | Permission Sets | `sf org list metadata --metadata-type PermissionSet` | FLS for fields |
 139 | Flows | `sf org list metadata --metadata-type Flow` | Agent actions |
 140 
 141 ---
 142 
 143 ## sf-ai-agentscript Integration
 144 
 145 For agent deployments, use the specialized commands:
 146 
 147 ```bash
 148 # Deploy dependencies first
 149 sf project deploy start --metadata ApexClass,Flow --target-org alias
 150 
 151 # Validate agent syntax
 152 sf agent validate authoring-bundle --api-name AgentName --target-org alias
 153 
 154 # Publish agent
 155 sf agent publish authoring-bundle --api-name AgentName --target-org alias
 156 
 157 # Activate agent
 158 sf agent activate --api-name AgentName --target-org alias
 159 ```
 160 
 161 ---
 162 
 163 ## Invocation Patterns
 164 
 165 | From Skill | To sf-deploy | When |
 166 |------------|--------------|------|
 167 | sf-metadata | → sf-deploy | "Deploy objects to [org]" |
 168 | sf-flow | → sf-deploy | "Deploy flow with --dry-run" |
 169 | sf-apex | → sf-deploy | "Deploy classes with RunLocalTests" |
 170 | sf-ai-agentscript | → sf-deploy | "Deploy and publish agent" |
 171 
 172 ---
 173 
 174 ## Related Documentation
 175 
 176 | Topic | Location |
 177 |-------|----------|
 178 | Deployment workflows | `sf-deploy/references/deployment-workflows.md` |
 179 | Agent deployment guide | `sf-deploy/references/agent-deployment-guide.md` |
 180 | Deploy script template | `sf-deploy/references/deploy.sh` |
