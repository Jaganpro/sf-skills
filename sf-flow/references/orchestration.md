<!-- Parent: sf-flow/SKILL.md -->
   1 # Multi-Skill Orchestration: sf-flow Perspective
   2 
   3 This document details how sf-flow fits into the multi-skill workflow for Salesforce development.
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
  16 │  2. sf-flow  ◀── YOU ARE HERE                                              │
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
  29 ## Why sf-flow Depends on sf-metadata
  30 
  31 | sf-flow Uses | From sf-metadata | What Fails Without It |
  32 |--------------|------------------|----------------------|
  33 | Object references | Custom Objects | `Invalid reference: Quote__c` |
  34 | Field references | Custom Fields | `Field does not exist: Status__c` |
  35 | Picklist values | Picklist Fields | Flow decision uses non-existent value |
  36 | Record Types | Record Type metadata | `Invalid record type: Inquiry` |
  37 
  38 **Rule**: If your Flow references custom objects or fields, create them with sf-metadata FIRST.
  39 
  40 ---
  41 
  42 ## sf-flow's Role in the Triangle Architecture
  43 
  44 Flow acts as the **orchestrator** in the Flow-LWC-Apex triangle:
  45 
  46 ```
  47                     ┌─────────────────────┐
  48                     │       FLOW          │◀── YOU ARE HERE
  49                     │  (Orchestrator)     │
  50                     └──────────┬──────────┘
  51                                │
  52          ┌─────────────────────┼─────────────────────┐
  53          │                     │                     │
  54          ▼                     ▼                     │
  55 ┌─────────────────┐   ┌─────────────────┐           │
  56 │   LWC Screen    │   │  Apex Invocable │           │
  57 │   Component     │   │     Action      │           │
  58 └────────┬────────┘   └────────┬────────┘           │
  59          │    @AuraEnabled     │                     │
  60          └──────────┬──────────┘                     │
  61                     ▼                                │
  62          ┌─────────────────────┐                     │
  63          │   Apex Controller   │─────────────────────┘
  64          └─────────────────────┘   Results back to Flow
  65 ```
  66 
  67 See `references/triangle-pattern.md` for detailed Flow XML patterns.
  68 
  69 ---
  70 
  71 ## Integration + Agentforce Extended Order
  72 
  73 When building agents with Flow actions:
  74 
  75 ```
  76 ┌─────────────────────────────────────────────────────────────────────────────┐
  77 │  AGENTFORCE FLOW ORCHESTRATION                                              │
  78 ├─────────────────────────────────────────────────────────────────────────────┤
  79 │  1. sf-metadata                                                             │
  80 │     └── Create object/field definitions                                     │
  81 │                                                                             │
  82 │  2. sf-connected-apps (if external API)                                     │
  83 │     └── Create OAuth Connected App                                          │
  84 │                                                                             │
  85 │  3. sf-integration (if external API)                                        │
  86 │     └── Create Named Credential + External Service                          │
  87 │                                                                             │
  88 │  4. sf-apex (if custom logic needed)                                        │
  89 │     └── Create @InvocableMethod classes                                     │
  90 │                                                                             │
  91 │  5. sf-flow  ◀── YOU ARE HERE                                              │
  92 │     └── Create Flow (HTTP Callout, Apex wrapper, or standard)               │
  93 │                                                                             │
  94 │  6. sf-deploy                                                               │
  95 │     └── Deploy all metadata                                                 │
  96 │                                                                             │
  97 │  7. sf-ai-agentforce                                                        │
  98 │     └── Create agent with flow:// target                                    │
  99 │                                                                             │
 100 │  8. sf-deploy                                                               │
 101 │     └── Publish agent (sf agent publish authoring-bundle)                   │
 102 └─────────────────────────────────────────────────────────────────────────────┘
 103 ```
 104 
 105 ---
 106 
 107 ## Flows for Agentforce: Critical Requirements
 108 
 109 When creating Flows that will be called by Agentforce agents:
 110 
 111 ### 1. Variable Name Matching
 112 
 113 Agent Script input/output names MUST match Flow variable API names exactly:
 114 
 115 ```xml
 116 <!-- Flow variable -->
 117 <variables>
 118     <name>inp_AccountId</name>
 119     <dataType>String</dataType>
 120     <isInput>true</isInput>
 121 </variables>
 122 ```
 123 
 124 ```yaml
 125 # Agent Script action - names must match!
 126 actions:
 127   - name: GetAccountDetails
 128     target: flow://Get_Account_Details
 129     inputs:
 130       - name: inp_AccountId  # Must match Flow variable name
 131         source: slot
 132 ```
 133 
 134 ### 2. Flow Requirements for Agents
 135 
 136 | Requirement | Why |
 137 |-------------|-----|
 138 | Autolaunched or Screen Flow | Record-triggered flows cannot be called directly |
 139 | `isInput: true` for inputs | Agent needs to pass values |
 140 | `isOutput: true` for outputs | Agent needs to read results |
 141 | Descriptive variable names | Agent uses these in responses |
 142 
 143 ### 3. Common Integration Errors
 144 
 145 | Error | Cause | Fix |
 146 |-------|-------|-----|
 147 | "Internal Error" on publish | Variable name mismatch | Match Flow var names exactly |
 148 | "Flow not found" | Flow not deployed | sf-deploy before sf-ai-agentforce |
 149 | Agent can't read output | Missing `isOutput: true` | Add output flag to Flow variable |
 150 
 151 ---
 152 
 153 ## Cross-Skill Integration Table
 154 
 155 | From Skill | To sf-flow | When |
 156 |------------|------------|------|
 157 | sf-ai-agentforce | → sf-flow | "Create Autolaunched Flow for agent action" |
 158 | sf-apex | → sf-flow | "Create Flow wrapper for Apex logic" |
 159 | sf-integration | → sf-flow | "Create HTTP Callout Flow" |
 160 
 161 | From sf-flow | To Skill | When |
 162 |--------------|----------|------|
 163 | sf-flow | → sf-metadata | "Describe Invoice__c" (verify fields before flow) |
 164 | sf-flow | → sf-deploy | "Deploy flow with --dry-run" |
 165 | sf-flow | → sf-data | "Create 200 test Accounts" (after deploy) |
 166 
 167 ---
 168 
 169 ## Deployment Order for Flow Dependencies
 170 
 171 When deploying Flows that reference Apex or LWC:
 172 
 173 ```
 174 1. APEX CLASSES        (if @InvocableMethod called)
 175    └── Deploy first
 176 
 177 2. LWC COMPONENTS      (if used in Screen Flow)
 178    └── Deploy second
 179 
 180 3. FLOWS               ◀── Deploy LAST
 181    └── References deployed Apex/LWC
 182 ```
 183 
 184 ---
 185 
 186 ## Best Practices
 187 
 188 1. **Always verify objects exist** before creating Flow references
 189 2. **Use sf-metadata describe** to confirm field API names
 190 3. **Deploy as Draft first** for complex flows
 191 4. **Test with 251 records** for bulk safety
 192 5. **Match variable names exactly** when creating for Agentforce
 193 
 194 ---
 195 
 196 ## Related Documentation
 197 
 198 | Topic | Location |
 199 |-------|----------|
 200 | Triangle pattern (Flow perspective) | `sf-flow/references/triangle-pattern.md` |
 201 | LWC integration | `sf-flow/references/lwc-integration-guide.md` |
 202 | Apex action template | `sf-flow/assets/apex-action-template.xml` |
 203 | sf-ai-agentforce | `sf-ai-agentforce/SKILL.md` |
