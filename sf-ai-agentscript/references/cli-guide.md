<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Agent Script CLI Quick Reference
   2 
   3 > Pro-Code Lifecycle: Git, CI/CD, and CLI for Agent Development
   4 
   5 ---
   6 
   7 ## The sf agent Commands
   8 
   9 | Command | Purpose | Example |
  10 |---------|---------|---------|
  11 | `sf project retrieve start` | Pull agent from org | `sf project retrieve start --metadata Agent:MyAgent --target-org sandbox` |
  12 | `sf agent validate authoring-bundle` | Check syntax before deploy | `sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG` |
  13 | `sf agent publish authoring-bundle` | Publish agent to org | `sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG --json` |
  14 | `sf agent test run` | Run batch tests | `sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json` |
  15 | `sf agent create` | Create agent from spec file | `sf agent create --api-name MyAgent --spec agent-spec.yaml -o TARGET_ORG --json` |
  16 | `sf agent generate agent-spec` | Generate agent specification | `sf agent generate agent-spec --type customer --role "Service Rep" --output-file agent-spec.yaml` |
  17 | `sf agent generate template` | Generate agent template (ISV packaging) | `sf agent generate template --agent-file MyAgent.agent --agent-version 1.0 --json` |
  18 | `sf agent preview start` | Start programmatic preview session | `sf agent preview start --api-name MyAgent -o TARGET_ORG --json` |
  19 | `sf agent preview send` | Send utterance to preview session | `sf agent preview send --session-id <id> --message "Hello" --json` |
  20 | `sf agent preview end` | End preview session | `sf agent preview end --session-id <id> --json` |
  21 | `sf org open agent` | Open Agent Builder in browser | `sf org open agent --api-name MyAgent -o TARGET_ORG` |
  22 | `sf org open authoring-bundle` | Open Agentforce Studio list view | `sf org open authoring-bundle -o TARGET_ORG` |
  23 
  24 > ⚠️ **CRITICAL**: Use `sf agent publish authoring-bundle` for Agent Script deployment, NOT `sf project deploy start`. The metadata API deploy will fail with "Required fields are missing: [BundleType]".
  25 
  26 ---
  27 
  28 ## Authoring Bundle Structure
  29 
  30 > ⚠️ **CRITICAL NAMING CONVENTION**: File must be named `AgentName.bundle-meta.xml`, NOT `AgentName.aiAuthoringBundle-meta.xml`. The metadata API expects `.bundle-meta.xml` suffix.
  31 
  32 ```
  33 force-app/main/default/aiAuthoringBundles/
  34 └── ProntoRefund/
  35     ├── ProntoRefund.agent           # Your Agent Script (REQUIRED)
  36     └── ProntoRefund.bundle-meta.xml # Metadata XML (REQUIRED)
  37 ```
  38 
  39 ### AgentName.bundle-meta.xml Content
  40 
  41 ```xml
  42 <?xml version="1.0" encoding="UTF-8"?>
  43 <AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
  44     <bundleType>AGENT</bundleType>
  45 </AiAuthoringBundle>
  46 ```
  47 
  48 > ⚠️ **COMMON ERROR**: Using `<BundleType>` (PascalCase) instead of `<bundleType>` (camelCase) will NOT cause errors, but the field name in the XML element is `bundleType` (lowercase b).
  49 
  50 ### Bundle Naming Rules
  51 
  52 | Component | Convention | Example |
  53 |-----------|------------|---------|
  54 | Folder name | PascalCase or snake_case | `ProntoRefund/` or `Pronto_Refund/` |
  55 | Agent script | Same as folder + `.agent` | `ProntoRefund.agent` |
  56 | Metadata XML | Same as folder + `.bundle-meta.xml` | `ProntoRefund.bundle-meta.xml` |
  57 
  58 ### Deployment Command (NOT sf project deploy!)
  59 
  60 ```bash
  61 # ✅ CORRECT: Use sf agent publish authoring-bundle
  62 sf agent publish authoring-bundle --api-name ProntoRefund -o TARGET_ORG
  63 
  64 # ❌ WRONG: Do NOT use sf project deploy start
  65 # This will fail with "Required fields are missing: [BundleType]"
  66 ```
  67 
  68 ---
  69 
  70 ## Pro-Code Workflow
  71 
  72 ```
  73 ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  74 │ 1 Retrieve  │ →  │ 2 Edit      │ →  │ 3 Validate  │ →  │ 4 Deploy    │
  75 │ Pull agent  │    │ CLI/editor  │    │ Check syntax│    │ Push to prod│
  76 │ from org    │    │ + Claude    │    │             │    │             │
  77 └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
  78 ```
  79 
  80 ### Step 1: Retrieve
  81 
  82 ```bash
  83 # Retrieve from sandbox
  84 sf project retrieve start --metadata Agent:ProntoRefund --target-org sandbox --json
  85 ```
  86 
  87 ### Step 2: Edit
  88 
  89 ```bash
  90 # Edit the agent script
  91 vim ./ProntoRefund/main.agent
  92 ```
  93 
  94 ### Step 3: Validate
  95 
  96 ```bash
  97 # Validate authoring bundle syntax
  98 sf agent validate authoring-bundle --api-name ProntoRefund -o TARGET_ORG --json
  99 ```
 100 
 101 ### Step 4: Publish
 102 
 103 ```bash
 104 # Publish agent to org (4-step process: Validate → Publish → Retrieve → Deploy)
 105 sf agent publish authoring-bundle --api-name ProntoRefund -o TARGET_ORG --json
 106 
 107 # Expected output:
 108 # ✔ Validate Bundle    ~1-2s
 109 # ✔ Publish Agent      ~8-10s
 110 # ✔ Retrieve Metadata  ~5-7s
 111 # ✔ Deploy Metadata    ~4-6s
 112 ```
 113 
 114 > ⚠️ Do NOT use `sf project deploy start` - it will fail with "Required fields are missing: [BundleType]"
 115 
 116 ---
 117 
 118 ## Testing Commands
 119 
 120 ```bash
 121 # Run agent tests (--api-name refers to an AiEvaluationDefinition, not the agent)
 122 sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json
 123 ```
 124 
 125 ---
 126 
 127 ## Validation Commands
 128 
 129 ```bash
 130 # Validate authoring bundle syntax
 131 sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json
 132 
 133 # Run tests against test definition
 134 sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json
 135 ```
 136 
 137 ### Common Validation Errors
 138 
 139 | Error | Cause | Fix |
 140 |-------|-------|-----|
 141 | `Internal Error, try again later` | Invalid `default_agent_user` | Query for Einstein Agent Users |
 142 | `SyntaxError: You cannot mix spaces and tabs` | Mixed indentation | Use consistent spacing |
 143 | `Transition to undefined topic "@topic.X"` | Typo in topic name | Check spelling |
 144 | `Variables cannot be both mutable AND linked` | Conflicting modifiers | Choose one modifier |
 145 
 146 ---
 147 
 148 ## Einstein Agent User Setup
 149 
 150 ### Query Existing Users
 151 
 152 ```bash
 153 sf data query --query "SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true"
 154 ```
 155 
 156 ### Username Format
 157 
 158 ```
 159 agent_user@<org-id>.ext
 160 ```
 161 
 162 Example: `agent_user@00drt00000limwjmal.ext`
 163 
 164 ### Get Org ID
 165 
 166 ```bash
 167 sf org display --json | jq -r '.result.id'
 168 ```
 169 
 170 ---
 171 
 172 ## CI/CD Integration
 173 
 174 ### GitHub Actions Example
 175 
 176 ```yaml
 177 name: Agent Testing
 178 on: [push, pull_request]
 179 jobs:
 180   test:
 181     runs-on: ubuntu-latest
 182     steps:
 183       - uses: actions/checkout@v3
 184       - name: Validate Agent
 185         run: sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json
 186       - name: Run Tests
 187         run: sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json
 188 ```
 189 
 190 ---
 191 
 192 ## Deployment Pipeline
 193 
 194 ```
 195 ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
 196 │  Sandbox    │ ───▶ │   Staging   │ ───▶ │ Production  │
 197 │   v1.3.0    │      │  Validate   │      │   v1.3.0    │
 198 └─────────────┘      └─────────────┘      └─────────────┘
 199 ```
 200 
 201 ### 6-Step Pipeline
 202 
 203 1. **Retrieve from Sandbox** - Pull latest agent bundle
 204 2. **Validate Syntax** - Check Agent Script for errors
 205 3. **Run Tests** - Execute automated agent tests
 206 4. **Code Review** - Automated best practices checks
 207 5. **Deploy to Production** - Push validated bundle
 208 6. **Verify Deployment** - Confirm agent is active
 209 
 210 ---
 211 
 212 ## Agent Creation Commands
 213 
 214 ### Create Agent from Spec File
 215 
 216 ```bash
 217 # Generate an agent specification YAML first
 218 sf agent generate agent-spec \
 219   --type customer \
 220   --role "Customer Service Representative" \
 221   --company-name "Acme Corp" \
 222   --company-description "E-commerce platform" \
 223   --output-file agent-spec.yaml
 224 
 225 # Create the agent from the spec
 226 sf agent create \
 227   --api-name MyServiceAgent \
 228   --spec agent-spec.yaml \
 229   -o TARGET_ORG --json
 230 ```
 231 
 232 ### Generate Agent Template (ISV Packaging)
 233 
 234 ```bash
 235 # Generate template for managed package distribution
 236 sf agent generate template \
 237   --agent-file force-app/main/default/aiAuthoringBundles/MyAgent/MyAgent.agent \
 238   --agent-version 1.0 \
 239   --json
 240 ```
 241 
 242 ---
 243 
 244 ## Programmatic Preview (Non-Interactive)
 245 
 246 > Unlike `sf agent preview` (interactive terminal), these subcommands enable scripted/automated agent testing — critical for CI/CD.
 247 
 248 ```bash
 249 # 1. Start a preview session
 250 SESSION_ID=$(sf agent preview start --api-name MyAgent -o TARGET_ORG --json | jq -r '.result.sessionId')
 251 
 252 # 2. Send utterances programmatically
 253 sf agent preview send --session-id $SESSION_ID --message "I need a refund" --json
 254 
 255 # 3. Send follow-up messages
 256 sf agent preview send --session-id $SESSION_ID --message "Order #12345" --json
 257 
 258 # 4. End the session
 259 sf agent preview end --session-id $SESSION_ID --json
 260 
 261 # List active preview sessions
 262 sf agent preview sessions -o TARGET_ORG --json
 263 ```
 264 
 265 ---
 266 
 267 ## Browser Quick-Open Commands
 268 
 269 ```bash
 270 # Open specific agent in Agentforce Builder
 271 sf org open agent --api-name MyAgent -o TARGET_ORG
 272 
 273 # Open Agentforce Studio (list view of all authoring bundles)
 274 sf org open authoring-bundle -o TARGET_ORG
 275 
 276 # Get URL only (for CI/CD logs or scripts)
 277 sf org open agent --api-name MyAgent -o TARGET_ORG --url-only
 278 ```
 279 
 280 ---
 281 
 282 ## Three-Phase Lifecycle
 283 
 284 ```
 285 ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
 286 │   ✏️ Draft   │  →   │  🔒 Commit  │  →   │  ✅ Activate │
 287 │   EDITABLE  │      │  READ-ONLY  │      │    LIVE     │
 288 └─────────────┘      └─────────────┘      └─────────────┘
 289 ```
 290 
 291 | Phase | Capabilities |
 292 |-------|--------------|
 293 | **Draft** | Edit freely, preview, run batch tests |
 294 | **Commit** | Script frozen, version assigned, bundle compiled |
 295 | **Activate** | Assign to Connections, go live, monitor |
 296 
 297 > **Key Insight**: Commit doesn't deploy - it freezes. Activate makes it live.
 298 
 299 ---
 300 
 301 ## API Versioning Behavior
 302 
 303 Agent versions share the same `agentId` (the `BotDefinition` / `Agent` record) but have **distinct version IDs**.
 304 
 305 | Concept | Description |
 306 |---------|-------------|
 307 | `agentId` / `BotDefinition.Id` | Unique per agent — does NOT change between versions |
 308 | `versionId` / `BotVersion.Id` | Unique per version — changes with each commit |
 309 | Default API behavior | API calls target the **active** version unless a specific `versionId` is provided |
 310 
 311 ```bash
 312 # The Agent Runtime API defaults to the active version:
 313 curl -X POST ".../einstein/ai-agent/v1" \
 314   -d '{"agentDefinitionId": "0XxXXXXXXXXXXX"}'   # Uses active version
 315 
 316 # To target a specific version (draft/committed), include versionId:
 317 curl -X POST ".../einstein/ai-agent/v1" \
 318   -d '{"agentDefinitionId": "0XxXXXXXXXXXXX", "agentVersionId": "4KdXXXXXXXXXXX"}'
 319 ```
 320 
 321 > **Key implication**: When testing draft versions via API, you must explicitly pass the version ID. Otherwise, the API will use the last activated version — which may not reflect your latest changes.
