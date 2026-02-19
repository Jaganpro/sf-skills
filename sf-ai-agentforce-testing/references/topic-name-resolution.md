<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # Topic Name Resolution in CLI Tests
   2 
   3 ## Overview
   4 
   5 When writing `expectedTopic` in YAML test specs for `sf agent test create`, the topic name format depends on the topic type. Getting this wrong causes **silent assertion failures** — the test runs, the agent responds, but `topic_assertion` reports `FAILURE` because the expected name doesn't match the runtime name.
   6 
   7 ---
   8 
   9 ## Three Topic Name Formats
  10 
  11 | Format | Example | Where Found |
  12 |--------|---------|-------------|
  13 | `localDeveloperName` | `Escalation` | Planner bundle XML `<localDeveloperName>` tag |
  14 | `developerName` (bundle) | `Escalation_16j548d53a8a3b0` | Planner bundle XML `<developerName>` tag |
  15 | `developerName` (runtime) | `Escalation_16j9d687a53f890` | Test results `.generatedData.topic` |
  16 
  17 > **Important:** The bundle `developerName` hash and the runtime `developerName` hash may differ. Always use the **runtime** value from test results.
  18 
  19 ---
  20 
  21 ## Rules
  22 
  23 ### Standard Topics (no prefix)
  24 
  25 Standard topics are built-in topics that come with every agent:
  26 
  27 - `Escalation`
  28 - `Off_Topic`
  29 - `Inappropriate_Content`
  30 
  31 **In YAML specs:** Use the `localDeveloperName` — the framework resolves it to the full runtime name automatically.
  32 
  33 ```yaml
  34 # ✅ CORRECT — framework resolves to Escalation_16j9d687a53f890
  35 - utterance: "I want to talk to a human"
  36   expectedTopic: Escalation
  37 
  38 # ✅ ALSO CORRECT — explicit runtime name works too
  39 - utterance: "I want to talk to a human"
  40   expectedTopic: Escalation_16j9d687a53f890
  41 
  42 # ❌ WRONG — bundle hash differs from runtime hash
  43 - utterance: "I want to talk to a human"
  44   expectedTopic: Escalation_16j548d53a8a3b0
  45 ```
  46 
  47 ### Standard Platform Topics (Intercept Before Custom Routing)
  48 
  49 Three platform-level standard topics exist **above** the custom planner engine (`GenAiPlannerBundle`). These intercept utterances **before** the agent's custom topic routing sees them:
  50 
  51 | Platform Topic | Triggers On |
  52 |----------------|-------------|
  53 | `Inappropriate_Content` | Hate speech, violence, sexual content, insults |
  54 | `Prompt_Injection` | Instruction override attempts ("ignore your instructions", "you are now...") |
  55 | `Reverse_Engineering` | Requests to reveal system instructions ("what are your instructions?") |
  56 
  57 **Impact on Testing:**
  58 
  59 - If a platform topic matches, the custom planner **never sees the utterance** — custom catch-all topics (e.g., Escalation) won't fire for these inputs even if their description includes "inappropriate content" triggers.
  60 - Use the standard platform topic name in `expectedTopic` for guardrail tests:
  61 
  62 ```yaml
  63 testCases:
  64   # ✅ CORRECT — platform topic intercepts before custom planner
  65   - utterance: "You're terrible and I hate you"
  66     expectedTopic: Inappropriate_Content
  67 
  68   # ❌ WRONG — custom Escalation topic won't see this; platform topic fires first
  69   - utterance: "You're terrible and I hate you"
  70     expectedTopic: Escalation
  71 ```
  72 
  73 - For prompt injection and reverse engineering tests, use `Prompt_Injection` and `Reverse_Engineering` respectively, or omit `expectedTopic` entirely and use `expectedOutcome` for behavioral validation.
  74 
  75 > **Discovery:** These platform topics were confirmed during testing on a Spring '26 sandbox (Feb 2026). An agent with a custom Escalation topic that explicitly listed "inappropriate content" and "prompt injection" as triggers still routed to the platform-level topics instead.
  76 
  77 ### Promoted Topics (p_16j... prefix)
  78 
  79 Promoted topics are custom topics created in the Salesforce Setup UI. They have an org-specific prefix (`p_16j...`) and a hash suffix.
  80 
  81 **In YAML specs:** You MUST use the **full runtime `developerName`** including the hash suffix. The `localDeveloperName` (without prefix/hash) does NOT resolve for promoted topics.
  82 
  83 ```yaml
  84 # ✅ CORRECT — full runtime developerName
  85 - utterance: "My doorbell camera is offline"
  86   expectedTopic: p_16jPl000000GwEX_Field_Support_Routing_16j8eeef13560aa
  87 
  88 # ❌ WRONG — localDeveloperName without prefix/hash does NOT resolve
  89 - utterance: "My doorbell camera is offline"
  90   expectedTopic: Field_Support_Routing
  91 
  92 # ❌ WRONG — partial name without hash suffix does NOT resolve
  93 - utterance: "My doorbell camera is offline"
  94   expectedTopic: p_16jPl000000GwEX_Field_Support_Routing
  95 ```
  96 
  97 ### Summary Table
  98 
  99 | Topic Type | YAML `expectedTopic` Value | Resolution |
 100 |------------|---------------------------|------------|
 101 | Standard (Escalation, Off_Topic, etc.) | `localDeveloperName` (e.g., `Escalation`) | Framework resolves automatically |
 102 | Promoted (p_16j... prefix) | Full runtime `developerName` with hash | Must be exact match |
 103 
 104 ---
 105 
 106 ## Discovery Workflow
 107 
 108 Since promoted topic names are opaque (hash suffixes), use this workflow to discover them:
 109 
 110 ### Step 1: Write spec with best guesses
 111 
 112 ```yaml
 113 name: "My Agent Discovery Run"
 114 subjectType: AGENT
 115 subjectName: My_Agent
 116 testCases:
 117   - utterance: "Test message for topic A"
 118     expectedTopic: Topic_A_Guess
 119   - utterance: "Test message for topic B"
 120     expectedTopic: Topic_B_Guess
 121 ```
 122 
 123 ### Step 2: Deploy and run
 124 
 125 ```bash
 126 sf agent test create --spec discovery-spec.yaml --api-name Discovery_Run --target-org dev
 127 sf agent test run --api-name Discovery_Run --wait 10 --result-format json --json --target-org dev
 128 ```
 129 
 130 ### Step 3: Extract actual topic names from results
 131 
 132 ```bash
 133 # Get the job ID from the run output, then:
 134 sf agent test results --job-id <JOB_ID> --result-format json --json --target-org dev \
 135   | jq '.result.testCases[].generatedData.topic'
 136 ```
 137 
 138 This outputs the **actual runtime `developerName`** for each test case — the value the agent actually routed to.
 139 
 140 ### Step 4: Update spec with actual names
 141 
 142 Replace your guesses with the actual runtime names from Step 3.
 143 
 144 ### Step 5: Re-deploy and re-run
 145 
 146 ```bash
 147 sf agent test create --spec updated-spec.yaml --api-name My_Agent_Tests --force-overwrite --target-org dev
 148 sf agent test run --api-name My_Agent_Tests --wait 10 --result-format json --json --target-org dev
 149 ```
 150 
 151 ---
 152 
 153 ## Where to Find Topic Names
 154 
 155 | Source | How to Access | What You Get |
 156 |--------|---------------|--------------|
 157 | **Test results JSON** | `.result.testCases[].generatedData.topic` | Runtime `developerName` (most reliable) |
 158 | **Planner bundle XML** | `retrieve GenAiPlannerBundle` → `<developerName>` and `<localDeveloperName>` | Bundle names (hash may differ from runtime) |
 159 | **SOQL** | `SELECT DeveloperName FROM GenAiPlugin WHERE ...` | Metadata names |
 160 | **Setup UI** | Einstein > Agents > Topics | Display labels (not API names) |
 161 
 162 ---
 163 
 164 ## Known Gotchas
 165 
 166 1. **Hash mismatch between bundle and runtime**: The `developerName` in the planner bundle XML (e.g., `Escalation_16j548d53a8a3b0`) may have a **different hash** than the runtime name (e.g., `Escalation_16j9d687a53f890`). Always use the runtime value from test results.
 167 
 168 2. **Promoted topics require exact match**: Unlike standard topics, there is no "fuzzy" resolution. The full `p_16j..._hash` string must match exactly.
 169 
 170 3. **Topic names are org-specific**: The `16j` prefix encodes the org ID. Topic names from one org will NOT work in another org.
 171 
 172 4. **`MigrationDefaultTopic`**: Standard Salesforce Copilots (not custom agents) may route everything to `MigrationDefaultTopic`. This is expected behavior for non-custom agents.
 173 
 174 5. **Topic hash changes on agent republish**: The runtime `developerName` hash suffix changes each time an agent is republished. Tests with hardcoded full runtime names (e.g., `Escalation_16j9d687a53f890`) will break after republish. **Mitigation:** Use `localDeveloperName` wherever the framework resolves it (standard topics). For promoted topics, re-run the [discovery workflow](#discovery-workflow) after each agent publish to capture new hashes.
