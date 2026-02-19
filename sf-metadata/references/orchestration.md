<!-- Parent: sf-metadata/SKILL.md -->
   1 # Multi-Skill Orchestration: sf-metadata Perspective
   2 
   3 This document details how sf-metadata fits into the multi-skill workflow for Salesforce development.
   4 
   5 ---
   6 
   7 ## Standard Orchestration Order
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────────────┐
  11 │  STANDARD MULTI-SKILL ORCHESTRATION ORDER                                   │
  12 ├─────────────────────────────────────────────────────────────────────────────┤
  13 │  1. sf-metadata  ◀── YOU ARE HERE                                          │
  14 │     └── Create object/field definitions (LOCAL files)                       │
  15 │                                                                             │
  16 │  2. sf-flow                                                                 │
  17 │     └── Create flow definitions (LOCAL files)                               │
  18 │                                                                             │
  19 │  3. sf-deploy                                                               │
  20 │     └── Deploy all metadata (REMOTE)                                        │
  21 │                                                                             │
  22 │  4. sf-data                                                                 │
  23 │     └── Create test data (REMOTE - objects must exist!)                     │
  24 └─────────────────────────────────────────────────────────────────────────────┘
  25 ```
  26 
  27 ---
  28 
  29 ## Why sf-metadata Goes First
  30 
  31 | Step | Depends On sf-metadata | What Fails Without It |
  32 |------|------------------------|----------------------|
  33 | sf-flow | ✅ Must exist | Flow references non-existent field/object |
  34 | sf-deploy | ✅ Must exist | Nothing to deploy |
  35 | sf-data | ✅ Must be deployed | `SObject type 'X' not supported` |
  36 
  37 **sf-metadata creates the foundation** that all other skills build upon.
  38 
  39 ---
  40 
  41 ## Integration + Agentforce Extended Order
  42 
  43 When building agents with external API integrations:
  44 
  45 ```
  46 ┌─────────────────────────────────────────────────────────────────────────────┐
  47 │  INTEGRATION + AGENTFORCE ORCHESTRATION ORDER                               │
  48 ├─────────────────────────────────────────────────────────────────────────────┤
  49 │  1. sf-metadata  ◀── YOU ARE HERE                                          │
  50 │     └── Create object/field definitions                                     │
  51 │                                                                             │
  52 │  2. sf-connected-apps                                                       │
  53 │     └── Create OAuth Connected App (if external API needed)                 │
  54 │                                                                             │
  55 │  3. sf-integration                                                          │
  56 │     └── Create Named Credential + External Service                          │
  57 │                                                                             │
  58 │  4. sf-apex                                                                 │
  59 │     └── Create @InvocableMethod (if custom logic needed)                    │
  60 │                                                                             │
  61 │  5. sf-flow                                                                 │
  62 │     └── Create Flow wrapper (HTTP Callout or Apex wrapper)                  │
  63 │                                                                             │
  64 │  6. sf-deploy                                                               │
  65 │     └── Deploy all metadata                                                 │
  66 │                                                                             │
  67 │  7. sf-ai-agentforce                                                        │
  68 │     └── Create agent with flow:// target                                    │
  69 │                                                                             │
  70 │  8. sf-deploy                                                               │
  71 │     └── Publish agent (sf agent publish authoring-bundle)                   │
  72 └─────────────────────────────────────────────────────────────────────────────┘
  73 ```
  74 
  75 ---
  76 
  77 ## sf-metadata Responsibilities in Orchestration
  78 
  79 ### Before sf-flow
  80 
  81 sf-metadata must create:
  82 - Custom Objects (the flow will reference)
  83 - Custom Fields (used in flow variables, assignments)
  84 - Picklist Values (used in flow decisions)
  85 - Record Types (used in flow record creates)
  86 
  87 ### Before sf-apex
  88 
  89 sf-metadata must create:
  90 - Custom Objects (Apex queries/DML targets)
  91 - Custom Fields (referenced in SOQL, field sets)
  92 - Custom Metadata Types (configuration storage)
  93 
  94 ### Example: Quote Builder Flow
  95 
  96 ```
  97 sf-metadata creates:
  98 ├── Quote__c.object-meta.xml
  99 ├── Quote_Line_Item__c.object-meta.xml
 100 ├── Quote__c.Status__c.field-meta.xml (Picklist)
 101 ├── Quote_Line_Item__c.Product__c.field-meta.xml (Lookup)
 102 └── Quote_Access.permissionset-meta.xml
 103 
 104 sf-apex creates:
 105 └── PricingCalculator.cls (@InvocableMethod)
 106 
 107 sf-flow creates:
 108 └── Quote_Builder_Flow.flow-meta.xml (references above)
 109 
 110 sf-deploy:
 111 └── Deploys all to org
 112 ```
 113 
 114 ---
 115 
 116 ## Common Errors from Wrong Order
 117 
 118 | Error | Cause | Correct Order |
 119 |-------|-------|---------------|
 120 | `Field does not exist: Status__c` | Flow created before field | sf-metadata → sf-flow |
 121 | `Invalid reference: Quote__c` | Flow created before object | sf-metadata → sf-flow |
 122 | `SObject type 'Quote__c' not supported` | Data created before deploy | sf-deploy → sf-data |
 123 | `Cannot find FlowDefinition` | Agent references missing flow | sf-flow → sf-ai-agentforce |
 124 
 125 ---
 126 
 127 ## Invocation Pattern
 128 
 129 After creating metadata with sf-metadata:
 130 
 131 ```
 132 # Deploy metadata
 133 Skill(skill="sf-deploy", args="Deploy to [target-org]")
 134 
 135 # Then create test data
 136 Skill(skill="sf-data", args="Create 251 Quote__c records")
 137 ```
 138 
 139 ---
 140 
 141 ## Cross-Skill Integration Table
 142 
 143 | From Skill | To sf-metadata | When |
 144 |------------|----------------|------|
 145 | sf-apex | → sf-metadata | "Describe Quote__c" (discover fields before coding) |
 146 | sf-flow | → sf-metadata | "Describe object fields, record types" (verify structure) |
 147 | sf-data | → sf-metadata | "Describe Custom_Object__c fields" (discover structure) |
 148 | sf-ai-agentforce | → sf-metadata | "Create custom object for agent data" |
 149 
 150 ---
 151 
 152 ## Best Practices
 153 
 154 1. **Always create Permission Sets** with object/field metadata
 155 2. **Use sf sobject describe** to verify existing structure before creating
 156 3. **Check sfdx-project.json** exists before generating metadata
 157 4. **Use consistent naming** across related objects (Quote__c, Quote_Line_Item__c)
 158 5. **Document relationships** in object descriptions
 159 
 160 ---
 161 
 162 ## Related Documentation
 163 
 164 | Topic | Location |
 165 |-------|----------|
 166 | Metadata templates | `sf-metadata/assets/` |
 167 | Field types guide | `sf-metadata/references/field-types-guide.md` |
 168 | Naming conventions | `sf-metadata/references/naming-conventions.md` |
 169 | sf-deploy skill | `sf-deploy/SKILL.md` |
