<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Testing & Validation Guide
   2 
   3 > The 100-Turn Gauntlet: Automated Batch Testing with LLM-as-Judge Scoring
   4 
   5 ---
   6 
   7 ## Enterprise Testing Infrastructure
   8 
   9 ### Testing Center Overview
  10 
  11 A centralized hub for batch-testing utterances without deactivating your agent.
  12 
  13 **Capabilities:**
  14 - ✅ Run tests against draft or committed versions
  15 - ✅ No need to deactivate the live agent
  16 - ✅ Execute up to 100 test cases simultaneously
  17 - ✅ Compare results across different script versions
  18 - ✅ Export test results for stakeholder review
  19 
  20 > 💡 Think of it as "staging" for your agent - test safely while production runs.
  21 
  22 ---
  23 
  24 ## The 5 Quality Metrics
  25 
  26 | Metric | Description | Scale |
  27 |--------|-------------|-------|
  28 | **Completeness** | Did the response include ALL necessary information? | 0-5 |
  29 | **Coherence** | Did the agent sound natural vs raw JSON output? | 0-5 |
  30 | **Topic Assertion** | Did the agent route to the correct topic? | Pass/Fail |
  31 | **Action Assertion** | Did the agent invoke the expected actions? | Pass/Fail |
  32 | **Combined Score** | Determines production readiness | Composite |
  33 
  34 > ⚠️ 100% assertions with 0% coherence = correct but robotic. Both matter.
  35 
  36 ---
  37 
  38 ## Coherence: The Difference
  39 
  40 | Coherence: 0/5 ❌ | Coherence: 5/5 ✅ |
  41 |-------------------|-------------------|
  42 | **USER:** "I want a refund for order #123" | **USER:** "I want a refund for order #123" |
  43 | **AGENT:** `{"status": "success", "case_id": "5008000123", "refund_auth": true}` | **AGENT:** Great news! Your refund has been approved. For your records, your case number is 5008000123. The refund should appear on your card within 3-5 business days. |
  44 | *Raw JSON dump - not conversational* | *Complete information in natural language* |
  45 
  46 ---
  47 
  48 ## LLM-as-Judge
  49 
  50 A "Judge LLM" evaluates the "Agent LLM" using criteria that match your use case.
  51 
  52 **Benefits:**
  53 - ✅ **Scalable**: Evaluate thousands of responses automatically
  54 - ✅ **Customizable**: Criteria match your specific use case
  55 - ✅ **Consistent**: Removes human reviewer variability
  56 - ✅ **Explainable**: Each score includes reasoning
  57 - ✅ **Iterative**: Refine criteria based on edge cases
  58 
  59 > 💡 The Judge LLM compares responses against your "Golden Response" definition.
  60 
  61 ---
  62 
  63 ## Batch Testing Workflow
  64 
  65 ### Step 1: Prepare Test Cases
  66 
  67 Create a set of test utterances covering:
  68 - Happy path scenarios
  69 - Edge cases
  70 - Error conditions
  71 - Multi-turn conversations
  72 
  73 ### Step 2: Define Assertions
  74 
  75 For each test case, specify:
  76 - **Expected Topic**: Which topic should be activated
  77 - **Expected Actions**: Which actions should be invoked
  78 - **Golden Response**: Ideal response pattern
  79 
  80 ### Step 3: Run Batch
  81 
  82 ```bash
  83 # Run agent tests (--api-name refers to an AiEvaluationDefinition, not the agent)
  84 sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json
  85 ```
  86 
  87 ### Step 4: Analyze Results
  88 
  89 | Metric | Score | Status |
  90 |--------|-------|--------|
  91 | **TOPIC ASSERTION** | 100% | ✅ PASS |
  92 | **ACTION ASSERTION** | 100% | ✅ PASS |
  93 | **COMPLETENESS** | 100% | ✅ PASS |
  94 | **COHERENCE** | 0% | ❌ FAIL |
  95 
  96 ---
  97 
  98 ## The Coherence Collapse Problem
  99 
 100 ### Symptom
 101 
 102 Batch test shows:
 103 - Topic assertions: 100% ✅
 104 - Action assertions: 100% ✅
 105 - Completeness: 100% ✅
 106 - Coherence: 0% ❌
 107 
 108 ### Root Cause
 109 
 110 Agent returns raw action output instead of natural language response.
 111 
 112 ```yaml
 113 # Problem: No instruction to format response
 114 actions:
 115   get_order: @actions.get_order_details
 116     set @variables.order_data = @outputs.data
 117 # LLM just dumps the data
 118 ```
 119 
 120 ### Fix
 121 
 122 Add explicit formatting instructions:
 123 
 124 ```yaml
 125 instructions: ->
 126   run @actions.get_order_details
 127     set @variables.order_data = @outputs.data
 128 
 129   | Here are your order details:
 130   | - Order Number: {!@variables.order_data.number}
 131   | - Status: {!@variables.order_data.status}
 132   | - Estimated Delivery: {!@variables.order_data.eta}
 133   |
 134   | Is there anything else I can help with?
 135 ```
 136 
 137 ---
 138 
 139 ## Metadata Lifecycle
 140 
 141 ### The Three-Phase Lifecycle
 142 
 143 ```
 144 ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
 145 │   ✏️ Draft   │  →   │  🔒 Commit  │  →   │  ✅ Activate │
 146 │   EDITABLE  │      │  READ-ONLY  │      │    LIVE     │
 147 └─────────────┘      └─────────────┘      └─────────────┘
 148 ```
 149 
 150 > ⚠️ **Key Insight**: Commit doesn't deploy - it freezes. Activate makes it live.
 151 
 152 ---
 153 
 154 ### Phase 1: Draft (EDITABLE)
 155 
 156 Your working copy. Edit freely, run tests, iterate rapidly.
 157 
 158 **Capabilities:**
 159 - ✅ Edit script content
 160 - ✅ Preview changes
 161 - ✅ Run batch tests
 162 - ✅ No version number yet
 163 
 164 ---
 165 
 166 ### Phase 2: Commit (READ-ONLY)
 167 
 168 Freeze the script. Generates version number and Authoring Bundle.
 169 
 170 **Capabilities:**
 171 - ✅ Script becomes immutable
 172 - ✅ Authoring Bundle compiled
 173 - ✅ Version number assigned (v1.0)
 174 - ✅ Ready for activation
 175 
 176 ---
 177 
 178 ### Phase 3: Activate (LIVE)
 179 
 180 Deploy to production. Assign to Connections and go live.
 181 
 182 **Capabilities:**
 183 - ✅ Assign to Connections (Slack, Chat)
 184 - ✅ Monitor in real-time
 185 - ✅ Agent goes live
 186 - ✅ Rollback if needed
 187 
 188 ---
 189 
 190 ## Test Case Design
 191 
 192 ### Coverage Categories
 193 
 194 | Category | Examples |
 195 |----------|----------|
 196 | **Happy Path** | Standard refund request, order lookup |
 197 | **Edge Cases** | Empty cart, expired offers, boundary values |
 198 | **Error Handling** | Invalid input, service failures |
 199 | **Security** | Unauthorized access attempts |
 200 | **Multi-Turn** | Conversation continuity, context preservation |
 201 
 202 ### Test Case Template
 203 
 204 ```yaml
 205 test_case:
 206   name: "High-risk customer full refund"
 207   utterance: "I want a refund for order #12345"
 208   context:
 209     customer_id: "CUST_001"
 210     churn_risk: 85
 211   expected:
 212     topic: "refund_processor"
 213     actions: ["get_churn_score", "process_refund"]
 214     response_contains: ["approved", "full refund"]
 215   assertions:
 216     topic_match: true
 217     action_sequence: true
 218     coherence_min: 4
 219 ```
 220 
 221 ---
 222 
 223 ## Validation Commands
 224 
 225 ### Pre-Deployment Validation
 226 
 227 ```bash
 228 # Validate authoring bundle syntax
 229 sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json
 230 
 231 # Run agent tests
 232 sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json
 233 ```
 234 
 235 ### Common Validation Errors
 236 
 237 | Error | Cause | Fix |
 238 |-------|-------|-----|
 239 | `Invalid default_agent_user` | User doesn't exist | Create Einstein Agent User |
 240 | `Topic not found` | Typo in transition | Check topic name spelling |
 241 | `Mixed indentation` | Tabs + spaces | Use consistent formatting |
 242 | `Action not callable` | Wrong protocol | Check target protocol |
 243 
 244 ---
 245 
 246 ## Continuous Testing
 247 
 248 ### CI/CD Integration
 249 
 250 ```yaml
 251 # Example GitHub Actions workflow
 252 name: Agent Testing
 253 on: [push, pull_request]
 254 jobs:
 255   test:
 256     runs-on: ubuntu-latest
 257     steps:
 258       - uses: actions/checkout@v3
 259       - name: Validate Agent
 260         run: sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json
 261       - name: Run Tests
 262         run: sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json
 263 ```
 264 
 265 ### Test Automation Best Practices
 266 
 267 1. **Run validation on every commit**
 268 2. **Run full test suite before merge**
 269 3. **Monitor coherence scores over time**
 270 4. **Alert on assertion failures**
 271 5. **Track coverage by topic and action**
 272 
 273 ---
 274 
 275 ## Key Takeaways
 276 
 277 | # | Concept |
 278 |---|---------|
 279 | 1 | **Testing Center** - Run up to 100 tests simultaneously |
 280 | 2 | **5 Quality Metrics** - Completeness, Coherence, Topic/Action Assertions, Combined |
 281 | 3 | **LLM-as-Judge** - Automated scoring against golden responses |
 282 | 4 | **Coherence Matters** - 100% assertions with 0% coherence = technically correct but unusable |
 283 | 5 | **Three-Phase Lifecycle** - Draft (edit) → Commit (freeze) → Activate (live) |
 284 | 6 | **CI/CD Integration** - Automate validation and testing in deployment pipeline |
