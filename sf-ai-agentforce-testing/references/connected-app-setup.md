<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # Authentication Guide for Agent Testing
   2 
   3 Guide to authentication methods for agent preview and API-based testing.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 > **v2.121.7 Breaking Change**: The `--client-app` flag has been **removed** from `sf agent preview`. Live preview now uses standard org authentication — no Connected App required.
  10 
  11 Agent testing uses **two different auth methods** depending on the testing approach:
  12 
  13 | Testing Approach | Auth Method | Setup Required |
  14 |------------------|-------------|----------------|
  15 | **Preview (Simulated)** | Standard org auth | `sf org login web` |
  16 | **Preview (Live)** | Standard org auth | `sf org login web` |
  17 | **Agent Runtime API** (multi-turn) | External Client App (ECA) | Client Credentials flow |
  18 
  19 ---
  20 
  21 ## Preview Authentication
  22 
  23 Both simulated and live preview modes use standard Salesforce CLI authentication. No Connected App or ECA is required.
  24 
  25 ### Authenticate to Your Org
  26 
  27 ```bash
  28 # Web-based OAuth login
  29 sf org login web --alias myorg
  30 
  31 # Verify authentication
  32 sf org display --target-org myorg
  33 ```
  34 
  35 ### Run Live Preview
  36 
  37 ```bash
  38 # Simulated mode (default - no real actions executed)
  39 sf agent preview --api-name Customer_Support_Agent --target-org myorg
  40 
  41 # Live mode (real Flows/Apex execute)
  42 sf agent preview --api-name Customer_Support_Agent --use-live-actions --target-org myorg
  43 
  44 # Live mode with debug output
  45 sf agent preview \
  46   --api-name Customer_Support_Agent \
  47   --use-live-actions \
  48   --apex-debug \
  49   --output-dir ./logs \
  50   --target-org myorg
  51 
  52 # Save transcripts
  53 sf agent preview \
  54   --api-name Customer_Support_Agent \
  55   --use-live-actions \
  56   --output-dir ./preview-logs \
  57   --target-org myorg
  58 ```
  59 
  60 ---
  61 
  62 ## Output Files
  63 
  64 When using `--output-dir`, you get:
  65 
  66 ### transcript.json
  67 
  68 Conversation record:
  69 
  70 ```json
  71 {
  72   "conversationId": "0Af7X000000001",
  73   "messages": [
  74     {"role": "user", "content": "Where is my order?", "timestamp": "..."},
  75     {"role": "assistant", "content": "Let me check...", "timestamp": "..."}
  76   ],
  77   "status": "completed"
  78 }
  79 ```
  80 
  81 ### responses.json
  82 
  83 Full API details including action invocations:
  84 
  85 ```json
  86 {
  87   "messages": [
  88     {
  89       "role": "function",
  90       "name": "get_order_status",
  91       "content": {
  92         "orderId": "a1J7X00000001",
  93         "status": "Shipped",
  94         "trackingNumber": "1Z999..."
  95       },
  96       "executionTimeMs": 450
  97     }
  98   ],
  99   "metrics": {
 100     "flowInvocations": 1,
 101     "apexInvocations": 0,
 102     "totalDuration": 3050
 103   }
 104 }
 105 ```
 106 
 107 ### apex-debug.log
 108 
 109 When using `--apex-debug`:
 110 
 111 ```
 112 13:45:22.123 (123456789)|USER_DEBUG|[15]|DEBUG|Processing order lookup
 113 13:45:22.234 (234567890)|SOQL_EXECUTE_BEGIN|[20]|Aggregations:0|SELECT Id, Status...
 114 13:45:22.345 (345678901)|SOQL_EXECUTE_END|[20]|Rows:1
 115 ```
 116 
 117 ---
 118 
 119 ## Troubleshooting
 120 
 121 ### 401 Unauthorized
 122 
 123 **Cause:** Org authentication expired or invalid.
 124 
 125 **Solution:**
 126 1. Re-authenticate: `sf org login web --alias [alias]`
 127 2. Verify auth is valid: `sf org display --target-org [alias]`
 128 3. Ensure user has Agentforce permissions
 129 
 130 ### Actions not executing
 131 
 132 **Cause:** Actions require deployed Flows/Apex.
 133 
 134 **Solution:**
 135 1. Verify Flow is active via SOQL: `sf data query --query "SELECT Id, ActiveVersionId, Status FROM FlowDefinitionView WHERE ApiName = '[FlowName]'" --target-org [OrgAlias]`
 136 2. Deploy/activate Flow via metadata: `sf project deploy start --metadata Flow:[FlowName] --target-org [OrgAlias]`
 137 3. Verify Apex is deployed: `sf project deploy start --metadata ApexClass:[ClassName]`
 138 4. Check agent is activated: `sf agent activate --api-name [Agent]`
 139 
 140 ### Timeout errors
 141 
 142 **Cause:** Flow or Apex taking too long.
 143 
 144 **Solution:**
 145 1. Add debug logs: `--apex-debug`
 146 2. Check Flow for long-running operations
 147 3. Verify external callouts are responsive
 148 
 149 ---
 150 
 151 ## Agent Runtime API Auth (ECA)
 152 
 153 For **multi-turn API testing** (not CLI preview), you need an External Client App with Client Credentials flow.
 154 
 155 ### Standard Auth vs ECA Comparison
 156 
 157 | Aspect | Standard Auth (Preview) | Client Credentials (ECA) |
 158 |--------|------------------------|--------------------------|
 159 | **Used by** | `sf agent preview` (simulated + live) | Agent Runtime API (multi-turn testing) |
 160 | **App type** | None required | External Client App (ECA) |
 161 | **Auth flow** | Standard CLI auth (browser login) | Client Credentials (machine-to-machine) |
 162 | **User interaction** | Browser redirect | None — fully automated |
 163 | **Best for** | Manual interactive testing | Automated multi-turn API testing |
 164 | **Setup guide** | This section | [ECA Setup Guide](eca-setup-guide.md) |
 165 
 166 ### Decision Flow
 167 
 168 ```
 169 What are you testing?
 170     │
 171     ├─ Interactive preview (sf agent preview)?
 172     │   → Standard org auth (sf org login web) — no app setup needed
 173     │
 174     └─ Multi-turn API conversations?
 175         → Use External Client App (Client Credentials) — see eca-setup-guide.md
 176 ```
 177 
 178 ### When You Need an ECA
 179 
 180 If you're doing **multi-turn API testing** via Agent Runtime API, you'll need:
 181 - An **External Client App** with Client Credentials flow ([ECA Setup Guide](eca-setup-guide.md))
 182 - Scopes: `api`, `chatbot_api`, `sfap_api`
 183 
 184 Preview testing (simulated or live) only requires standard `sf org login web`.
 185 
 186 ---
 187 
 188 ## Related Skills
 189 
 190 | Skill | Use For |
 191 |-------|---------|
 192 | sf-connected-apps | Create and manage Connected Apps and ECAs |
 193 | sf-flow | Debug failing Flow actions |
 194 | sf-apex | Debug failing Apex actions |
 195 | sf-debug | Analyze debug logs |
