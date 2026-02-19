<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # Agent Script Testing Patterns
   2 
   3 Testing guide for agents built with Agent Script (`.agent` files / AiAuthoringBundle). Covers the unique challenges of testing multi-topic Agent Script agents via CLI (`sf agent test`) and Agent Runtime API.
   4 
   5 ---
   6 
   7 ## Background: Why Agent Script Testing is Different
   8 
   9 Agent Script agents use a **two-level action system**:
  10 
  11 | Level | Where | What It Does | Example |
  12 |-------|-------|-------------|---------|
  13 | **Level 1: Definition** | `topic.actions:` block | Defines action with `target:` | `get_order_status: target: "apex://OrderStatusService"` |
  14 | **Level 2: Invocation** | `reasoning.actions:` block | Invokes Level 1 via `@actions.<name>` | `check_status: @actions.get_order_status` |
  15 
  16 Multi-topic agents also have a `start_agent` entry point that routes to topics via `@utils.transition to @topic.<name>`. This creates **transition actions** (e.g., `go_order_status`).
  17 
  18 **The core testing challenge:** Single-utterance CLI tests have a "1 action per reasoning cycle" budget. For multi-topic agents, the first cycle is consumed by the topic transition — the actual business action never fires.
  19 
  20 ---
  21 
  22 ## Pattern 1: Routing Test
  23 
  24 **Goal:** Verify `start_agent` routes to the correct topic based on user input.
  25 
  26 **When to use:** Always — this is the first test for any Agent Script agent.
  27 
  28 **Key insight:** The `expectedActions` captures the **transition action** (`go_<topic>`), NOT the business action.
  29 
  30 ```yaml
  31 testCases:
  32   - utterance: "I want to check my order status"
  33     expectedTopic: order_status
  34     expectedActions:
  35       - go_order_status    # Transition action from start_agent
  36     expectedOutcome: "Agent should acknowledge and begin the order status flow"
  37 
  38   - utterance: "Check the status of my order"
  39     expectedTopic: order_status
  40     # Multiple phrasings for robust routing validation
  41 
  42   - utterance: "Where is my package?"
  43     expectedTopic: order_status
  44 ```
  45 
  46 **What to verify in results:**
  47 - `generatedData.topic` matches `expectedTopic`
  48 - `actionsSequence` contains `go_<topic_name>`
  49 
  50 ---
  51 
  52 ## Pattern 2: Action Test with Conversation History
  53 
  54 **Goal:** Test the actual business action (Apex/Flow) by pre-positioning the agent in the target topic.
  55 
  56 **When to use:** For any action that requires the agent to already be in a topic (i.e., most actions beyond the initial routing).
  57 
  58 **Key insight:** `conversationHistory` simulates prior turns so the agent starts in the target topic. The agent's response includes the `topic` field to establish context.
  59 
  60 ```yaml
  61 testCases:
  62   - utterance: "The order ID is 801ak00001g59JlAAI"
  63     conversationHistory:
  64       - role: "user"
  65         message: "I want to check my order status"
  66       - role: "agent"
  67         topic: "order_status"
  68         message: "I'd be happy to help! Could you please provide the Order ID?"
  69     expectedTopic: order_status
  70     expectedActions:
  71       - get_order_status    # Level 1 DEFINITION name (NOT invocation name)
  72     expectedOutcome: "Agent retrieves order details including number, status, and amount"
  73 ```
  74 
  75 **Conversation history format:**
  76 
  77 | Field | Required | Description |
  78 |-------|----------|-------------|
  79 | `role` | Yes | `"user"` or `"agent"` |
  80 | `message` | Yes | The message content |
  81 | `topic` | Agent only | Topic name — **required for agent messages** to establish topic context |
  82 
  83 **Common mistake:** Using the Level 2 invocation name (e.g., `check_status`) instead of the Level 1 definition name (e.g., `get_order_status`) in `expectedActions`. CLI results always report the **definition name**.
  84 
  85 ---
  86 
  87 ## Pattern 3: Error Handling Test
  88 
  89 **Goal:** Verify the agent handles invalid input or missing data gracefully.
  90 
  91 **When to use:** After validating the happy path (Pattern 2).
  92 
  93 ```yaml
  94 testCases:
  95   # Invalid input — order not found
  96   - utterance: "My order ID is INVALID_XYZ_123"
  97     conversationHistory:
  98       - role: "user"
  99         message: "Check my order status"
 100       - role: "agent"
 101         topic: "order_status"
 102         message: "Sure! What is your Order ID?"
 103     expectedTopic: order_status
 104     expectedOutcome: "Agent should inform the user that the order was not found"
 105 
 106   # Missing required input — no ID provided
 107   - utterance: "I don't know my order ID"
 108     conversationHistory:
 109       - role: "user"
 110         message: "Check my order status"
 111       - role: "agent"
 112         topic: "order_status"
 113         message: "What is your Order ID?"
 114     expectedTopic: order_status
 115     expectedOutcome: "Agent should suggest alternative ways to find the order"
 116 ```
 117 
 118 **Apex `WITH USER_MODE` errors:** If the Apex class uses `WITH USER_MODE`, the action silently returns 0 rows when the Einstein Agent User lacks permissions. The agent responds as if the record doesn't exist — no error message. Test this explicitly to catch permission gaps before production.
 119 
 120 ---
 121 
 122 ## Pattern 4: Escalation Test
 123 
 124 **Goal:** Verify escalation works from both `start_agent` and within topics.
 125 
 126 **When to use:** Always — escalation is a critical safety net.
 127 
 128 ```yaml
 129 testCases:
 130   # Escalation from start_agent (before topic routing)
 131   - utterance: "I want to talk to a real person"
 132     expectedTopic: Escalation
 133 
 134   # Escalation from within a topic
 135   - utterance: "This isn't helping, let me speak to someone"
 136     conversationHistory:
 137       - role: "user"
 138         message: "Check my order status"
 139       - role: "agent"
 140         topic: "order_status"
 141         message: "What is your Order ID?"
 142     expectedTopic: Escalation
 143 
 144   # Non-escalation (agent should NOT escalate)
 145   - utterance: "I need help with my order"
 146     expectedTopic: order_status
 147     expectedOutcome: "Agent should begin helping with the order, not escalate"
 148 ```
 149 
 150 ---
 151 
 152 ## Pattern 5: Multi-Action Sequence Test
 153 
 154 **Goal:** Test an agent that performs multiple actions in sequence (e.g., look up order, then create a case).
 155 
 156 **When to use:** Agents with topics that chain multiple actions.
 157 
 158 **Limitation:** CLI tests are single-utterance. To test multi-action sequences, use longer conversation histories.
 159 
 160 ```yaml
 161 testCases:
 162   # First action in sequence
 163   - utterance: "Order ID is 801ak00001g59JlAAI"
 164     conversationHistory:
 165       - role: "user"
 166         message: "I have a problem with my order"
 167       - role: "agent"
 168         topic: "order_support"
 169         message: "I can help! What's the Order ID?"
 170     expectedTopic: order_support
 171     expectedActions:
 172       - get_order_details
 173     expectedOutcome: "Agent retrieves order details and asks about the problem"
 174 
 175   # Second action — using extended history from first action
 176   - utterance: "Yes, please create a case for this"
 177     conversationHistory:
 178       - role: "user"
 179         message: "I have a problem with my order"
 180       - role: "agent"
 181         topic: "order_support"
 182         message: "What's the Order ID?"
 183       - role: "user"
 184         message: "801ak00001g59JlAAI"
 185       - role: "agent"
 186         topic: "order_support"
 187         message: "I found your order #00000102 (Draft, $50,000). What issue are you experiencing?"
 188       - role: "user"
 189         message: "The order is wrong, I need to file a complaint"
 190       - role: "agent"
 191         topic: "order_support"
 192         message: "I'm sorry about that. Would you like me to create a support case?"
 193     expectedTopic: order_support
 194     expectedActions:
 195       - create_support_case
 196     expectedOutcome: "Agent creates a support case and provides the case number"
 197 ```
 198 
 199 ---
 200 
 201 ## Topic Name Discovery Workflow
 202 
 203 Agent Script topic names in CLI test results may differ from the names in the `.agent` file. Follow this workflow to discover the actual runtime names:
 204 
 205 ### Step 1: Write Initial Spec
 206 
 207 Use the topic name from the `.agent` file as your best guess:
 208 
 209 ```yaml
 210 # In .agent file: "topic order_status:"
 211 expectedTopic: order_status
 212 ```
 213 
 214 ### Step 2: Run First Test
 215 
 216 ```bash
 217 sf agent test create --spec ./tests/spec.yaml --api-name MyTest --target-org dev
 218 sf agent test run --api-name MyTest --wait 10 --result-format json --json --target-org dev
 219 ```
 220 
 221 ### Step 3: Extract Actual Topic Names
 222 
 223 ```bash
 224 # Get the job ID from the run output
 225 sf agent test results --job-id <JOB_ID> --result-format json --json --target-org dev \
 226   | jq '.result.testCases[].generatedData.topic'
 227 ```
 228 
 229 ### Step 4: Update Spec
 230 
 231 Replace guessed topic names with actual runtime names from the results.
 232 
 233 ### Step 5: Re-Deploy and Re-Run
 234 
 235 ```bash
 236 sf agent test create --spec ./tests/spec.yaml --api-name MyTest --force-overwrite --target-org dev
 237 sf agent test run --api-name MyTest --wait 10 --result-format json --json --target-org dev
 238 ```
 239 
 240 ---
 241 
 242 ## Permission Pre-Check Guide
 243 
 244 Agent Script agents with `WITH USER_MODE` Apex require the Einstein Agent User to have object permissions. Missing permissions cause **silent failures** — the query returns 0 rows with no error.
 245 
 246 ### Identifying Required Permissions
 247 
 248 1. **Read the `.agent` file** — find all `target: "apex://ClassName"` entries
 249 2. **Read each Apex class** — find SOQL queries with `WITH USER_MODE`
 250 3. **Extract queried objects** — e.g., `FROM Order`, `FROM Account`
 251 4. **Check `default_agent_user`** — the user profile in the `.agent` config block
 252 
 253 ### Verifying Permissions
 254 
 255 ```bash
 256 # Find the Einstein Agent User's profile
 257 sf data query --query "SELECT Id, ProfileId, Profile.Name FROM User WHERE Username = '<default_agent_user>' LIMIT 1" --target-org dev --json
 258 
 259 # Check ObjectPermissions for the user's profile
 260 sf data query --query "SELECT SObjectType, PermissionsRead FROM ObjectPermissions WHERE ParentId IN (SELECT Id FROM PermissionSet WHERE ProfileId = '<profile_id>') AND SObjectType IN ('Order', 'Account')" --target-org dev --json
 261 ```
 262 
 263 ### Fixing Missing Permissions
 264 
 265 ```bash
 266 # Create a Permission Set (via Apex anonymous)
 267 sf apex run --target-org dev <<'EOF'
 268 PermissionSet ps = new PermissionSet(
 269     Name = 'Agent_Object_Access',
 270     Label = 'Agent Object Access'
 271 );
 272 insert ps;
 273 
 274 ObjectPermissions op = new ObjectPermissions(
 275     ParentId = ps.Id,
 276     SObjectType = 'Order',
 277     PermissionsRead = true,
 278     PermissionsViewAllRecords = false
 279 );
 280 insert op;
 281 EOF
 282 
 283 # Assign to the Einstein Agent User
 284 sf apex run --target-org dev <<'EOF'
 285 User agentUser = [SELECT Id FROM User WHERE Username = '<default_agent_user>' LIMIT 1];
 286 PermissionSet ps = [SELECT Id FROM PermissionSet WHERE Name = 'Agent_Object_Access' LIMIT 1];
 287 insert new PermissionSetAssignment(AssigneeId = agentUser.Id, PermissionSetId = ps.Id);
 288 EOF
 289 ```
 290 
 291 ---
 292 
 293 ## Agent Script vs GenAiPlannerBundle: Testing Differences
 294 
 295 | Aspect | Agent Script (AiAuthoringBundle) | GenAiPlannerBundle |
 296 |--------|----------------------------------|-------------------|
 297 | **Metadata format** | `.agent` DSL file | XML files |
 298 | **Action references** | `apex://Class` directly | GenAiFunction XML |
 299 | **Topic routing** | `start_agent` → `@utils.transition` | LLM planner routing |
 300 | **Action in CLI test** | Transition action only (1st cycle) | May get business action |
 301 | **Test approach** | Use conversationHistory for actions | Standard single-utterance |
 302 | **Discovery** | Parse `.agent` DSL | Parse XML files |
 303 | **Permission model** | `default_agent_user` in config | Org-level profile |
 304 
 305 ---
 306 
 307 ## Quick Reference: CLI YAML Fields for Agent Script
 308 
 309 ```yaml
 310 # REQUIRED top-level fields
 311 name: "My Agent Tests"              # MasterLabel — deploy fails without
 312 subjectType: AGENT                   # Must be AGENT
 313 subjectName: My_Agent_Name           # config.developer_name from .agent file
 314 
 315 testCases:
 316   - utterance: "user message"        # Required
 317     expectedTopic: topic_name        # From .agent topic block name
 318     expectedActions:                  # Flat list of strings
 319       - action_name                  # Level 1 definition name
 320     expectedOutcome: "description"   # LLM-as-judge evaluation
 321     conversationHistory:             # Pre-position in topic
 322       - role: "user"
 323         message: "prior user message"
 324       - role: "agent"
 325         topic: "topic_name"          # REQUIRED for agent messages
 326         message: "prior agent response"
 327 ```
 328 
 329 ---
 330 
 331 ## Related Resources
 332 
 333 - [SKILL.md](../SKILL.md) — Main skill documentation (Phase B: Agent Script section)
 334 - [test-spec-guide.md](test-spec-guide.md) — Complete test spec guide
 335 - [test-spec-reference.md](../references/test-spec-reference.md) — YAML schema reference
 336 - [topic-name-resolution.md](topic-name-resolution.md) — Topic name format rules
 337 - [agentscript-test-spec.yaml](../assets/agentscript-test-spec.yaml) — Template with all 5 patterns
