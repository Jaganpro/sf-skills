<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Instruction Resolution Guide
   2 
   3 > One Pass. Top to Bottom. Before the LLM Sees Anything.
   4 
   5 ---
   6 
   7 ## The Three Phases
   8 
   9 Agent Script instructions resolve in a predictable order. Understanding this flow gives you precise control over what the LLM sees and when actions execute.
  10 
  11 | Phase | Icon | Name | Description |
  12 |-------|------|------|-------------|
  13 | 1 | ▶ | **Pre-LLM Setup** | Instructions resolve line-by-line, deterministically |
  14 | 2 | ⚙ | **LLM Reasoning** | LLM sees only resolved text and available actions |
  15 | 3 | ↻ | **Post-Action Loop** | After action completes, topic loops with updated variables |
  16 
  17 ---
  18 
  19 ## Phase 1: Pre-LLM Resolution
  20 
  21 > Everything resolves top-to-bottom BEFORE the LLM processes them.
  22 
  23 ### What Happens
  24 
  25 | Step | Description |
  26 |------|-------------|
  27 | **Conditions evaluate** | `if/else` logic evaluates and prunes paths |
  28 | **Actions execute** | `run @actions.X` executes immediately |
  29 | **Templates resolve** | Template syntax resolves to actual values |
  30 | **Transitions short-circuit** | `transition to` can exit the topic immediately |
  31 
  32 ### Example
  33 
  34 ```yaml
  35 topic refund_request:
  36   description: "Handle refund requests"
  37   reasoning:
  38     instructions: ->
  39       # --- PRE-LLM: These resolve BEFORE the LLM sees anything ---
  40 
  41       # Security gate - check attempt limit
  42       if @variables.attempt_count >= 3:
  43         transition to @topic.escalation
  44 
  45       # Load data deterministically
  46       run @actions.get_churn_score
  47         with customer_id = @variables.customer_id
  48         set @variables.churn_score = @outputs.score
  49 
  50       # Increment counter
  51       set @variables.attempt_count = @variables.attempt_count + 1
  52 
  53       # --- LLM INSTRUCTIONS: Only this text reaches the LLM ---
  54       | Customer churn score: {!@variables.churn_score}
  55 
  56       if @variables.churn_score >= 80:
  57         | Offer a full cash refund to retain this customer.
  58       else:
  59         | Offer a $10 credit as a goodwill gesture.
  60 ```
  61 
  62 ### Execution Timeline
  63 
  64 ```
  65 ┌─────────────────────────────────────────────────────────────────┐
  66 │ ▶ PRE-LLM                                        [LINE-BY-LINE] │
  67 ├─────────────────────────────────────────────────────────────────┤
  68 │ ● Message Received                                       ~10ms  │
  69 │ ● Instructions Resolve                               ~50-500ms  │
  70 │ ● Templates Hydrate                                       ~5ms  │
  71 └─────────────────────────────────────────────────────────────────┘
  72 ```
  73 
  74 ---
  75 
  76 ## Phase 2: LLM Processing
  77 
  78 > The LLM receives clean, final instructions with all values populated.
  79 
  80 ### What the LLM Sees
  81 
  82 The LLM **never** sees your conditionals - only the resolved result.
  83 
  84 **Your code:**
  85 ```yaml
  86 instructions: ->
  87   | Customer churn score: {!@variables.churn_score}
  88 
  89   if @variables.churn_score >= 80:
  90     | Offer a full cash refund to retain this customer.
  91   else:
  92     | Offer a $10 credit as a goodwill gesture.
  93 ```
  94 
  95 **What the LLM actually sees (if churn_score = 85):**
  96 ```
  97 Customer churn score: 85
  98 Offer a full cash refund to retain this customer.
  99 ```
 100 
 101 ### Action Visibility
 102 
 103 The `available when` clause is also evaluated deterministically:
 104 
 105 ```yaml
 106 actions:
 107   process_refund: @actions.process_refund
 108     description: "Issue the refund"
 109     available when @variables.is_verified == True
 110 ```
 111 
 112 If `is_verified` is `False`, the LLM **never sees** `process_refund` as an option.
 113 
 114 ---
 115 
 116 ## Phase 3: Post-Action Loop
 117 
 118 > When the LLM invokes an action, the topic loops back. Instructions resolve AGAIN.
 119 
 120 ### What Happens
 121 
 122 | Step | Description |
 123 |------|-------------|
 124 | **Outputs stored** | LLM action completes, outputs stored in variables |
 125 | **Re-resolve** | Topic instructions resolve again (same top-to-bottom pass) |
 126 | **New conditions trigger** | Conditions can trigger based on new values |
 127 | **Follow-up executes** | Deterministic follow-up actions run |
 128 
 129 ### The Loop Pattern
 130 
 131 ```
 132 TURN 1: Initial Request
 133 ├─ User asks for refund
 134 ├─ Instructions resolve (refund_status is empty)
 135 ├─ LLM sees "Help the customer with their refund request"
 136 ├─ LLM calls process_refund action
 137 └─ Action sets refund_status = "Approved"
 138          ↓ LOOP
 139 TURN 2: After Action (Same Topic)
 140 ├─ Topic loops back
 141 ├─ Instructions resolve AGAIN
 142 ├─ Condition triggers: refund_status == "Approved"
 143 ├─ Deterministic action runs: create_crm_case
 144 └─ Transition to success_confirmation
 145 ```
 146 
 147 ### Example: Deterministic Follow-Up
 148 
 149 ```yaml
 150 topic refund_request:
 151   description: "Handle refund requests with deterministic follow-up"
 152   reasoning:
 153     instructions: ->
 154       # --- POST-ACTION CHECK: Did we just process a refund? ---
 155       # This block runs AGAIN after the LLM action completes!
 156 
 157       if @variables.refund_status == "Approved":
 158         # Deterministic follow-up - LLM cannot skip this!
 159         run @actions.create_crm_case
 160           with customer_id = @variables.customer_id
 161           with refund_amount = @variables.refund_amount
 162         transition to @topic.success_confirmation
 163 
 164       # --- PRE-LLM: Normal instruction flow ---
 165       | Customer churn score: {!@variables.churn_score}
 166       | Help the customer with their refund request.
 167 
 168     actions:
 169       process_refund: @actions.process_refund
 170         description: "Issue the refund"
 171         set @variables.refund_status = @outputs.status
 172         set @variables.refund_amount = @outputs.amount
 173 ```
 174 
 175 > 💡 **KEY INSIGHT**: The post-action check pattern ensures business-critical follow-up actions ALWAYS execute. The LLM cannot "forget" or "decide not to" - it's code, not a suggestion.
 176 
 177 ---
 178 
 179 ## The Instruction Pattern Structure
 180 
 181 ### Recommended Order
 182 
 183 ```yaml
 184 reasoning:
 185   instructions: ->
 186     # 1. POST-ACTION CHECKS (at TOP - triggers on loop)
 187     if @variables.action_completed == True:
 188       run @actions.follow_up_action
 189       transition to @topic.next_step
 190 
 191     # 2. PRE-LLM DATA LOADING
 192     run @actions.load_required_data
 193       set @variables.data = @outputs.result
 194 
 195     # 3. DYNAMIC INSTRUCTIONS FOR LLM
 196     | Here is the context: {!@variables.data}
 197 
 198     if @variables.condition:
 199       | Do this thing.
 200     else:
 201       | Do that thing.
 202 
 203   actions:
 204     # LLM-selectable actions
 205     my_action: @actions.do_something
 206       set @variables.action_completed = True
 207 ```
 208 
 209 ### Why This Order Matters
 210 
 211 1. **Post-action at TOP**: When the topic loops after action completion, the check triggers immediately
 212 2. **Data loading next**: LLM needs current data to make decisions
 213 3. **Instructions last**: LLM sees resolved values from data loading
 214 
 215 ---
 216 
 217 ## Execution Timeline Summary
 218 
 219 | Phase | What Happens | Duration |
 220 |-------|--------------|----------|
 221 | **Pre-LLM** | Message received, instructions resolve, templates hydrate | ~60-515ms |
 222 | **LLM** | LLM processes resolved instructions, decides on response/action | ~1-3s |
 223 | **Post-Action** | Action executes, topic loops with updated variables | ~150-550ms |
 224 
 225 ---
 226 
 227 ## Common Patterns
 228 
 229 ### Pattern 1: Security Gate with Early Exit
 230 
 231 ```yaml
 232 instructions: ->
 233   if @variables.failed_attempts >= 3:
 234     | Account locked due to too many attempts.
 235     transition to @topic.lockout  # Early exit - LLM never reasons
 236 
 237   | Please verify your identity.
 238 ```
 239 
 240 ### Pattern 2: Data-Dependent Instructions
 241 
 242 ```yaml
 243 instructions: ->
 244   run @actions.get_account_tier
 245     set @variables.tier = @outputs.tier
 246 
 247   if @variables.tier == "Gold":
 248     | You're a Gold member! Enjoy priority support.
 249   if @variables.tier == "Silver":
 250     | Welcome back, Silver member.
 251   else:
 252     | Thanks for contacting support.
 253 ```
 254 
 255 ### Pattern 3: Action Chaining
 256 
 257 ```yaml
 258 instructions: ->
 259   # Step 1 complete?
 260   if @variables.step1_done == True and @variables.step2_done == False:
 261     run @actions.step2
 262       set @variables.step2_done = True
 263 
 264   # Step 2 complete?
 265   if @variables.step2_done == True:
 266     transition to @topic.complete
 267 
 268   | Let's start with step 1.
 269 
 270 actions:
 271   do_step1: @actions.step1
 272     set @variables.step1_done = True
 273 ```
 274 
 275 ---
 276 
 277 ## Syntax Patterns Reference
 278 
 279 | Pattern | Purpose |
 280 |---------|---------|
 281 | `instructions: ->` | Arrow syntax enables inline expressions |
 282 | `if @variables.x:` | Conditional - resolves BEFORE LLM |
 283 | `run @actions.x` | Execute action during resolution |
 284 | `set @var = @outputs.y` | Capture action output |
 285 | Curly-bang: {!@variables.x} | Template injection into LLM text |
 286 | `available when` | Control action visibility to LLM |
 287 | `transition to @topic.x` | Deterministic topic change |
 288 
 289 ---
 290 
 291 ## Anti-Patterns to Avoid
 292 
 293 ### ❌ Data Load After LLM Text
 294 
 295 ```yaml
 296 # WRONG - LLM sees empty values
 297 instructions: ->
 298   | Customer name: {!@variables.name}  # name is empty!
 299   run @actions.load_customer
 300     set @variables.name = @outputs.name
 301 ```
 302 
 303 ### ✅ Correct Order
 304 
 305 ```yaml
 306 # RIGHT - Load first, then reference
 307 instructions: ->
 308   run @actions.load_customer
 309     set @variables.name = @outputs.name
 310   | Customer name: {!@variables.name}  # name is populated
 311 ```
 312 
 313 ### ❌ Post-Action Check at Bottom
 314 
 315 ```yaml
 316 # WRONG - Never triggers because transition happens first
 317 instructions: ->
 318   | Help with refund.
 319   transition to @topic.main  # Exits before check!
 320 
 321   if @variables.refund_done:
 322     run @actions.log_refund
 323 ```
 324 
 325 ### ✅ Post-Action Check at Top
 326 
 327 ```yaml
 328 # RIGHT - Check first, then normal flow
 329 instructions: ->
 330   if @variables.refund_done:
 331     run @actions.log_refund
 332     transition to @topic.success
 333 
 334   | Help with refund.
 335 ```
 336 
 337 ---
 338 
 339 ## Key Takeaways
 340 
 341 | # | Takeaway |
 342 |---|----------|
 343 | 1 | **One Pass Resolution** - Instructions resolve top-to-bottom BEFORE the LLM sees anything |
 344 | 2 | **Inline Pattern** - Use `reasoning.instructions: ->` with inline conditionals |
 345 | 3 | **LLM Sees Clean Text** - No if/else logic visible, no action calls visible |
 346 | 4 | **Post-Action Loop** - Topic loops back after LLM action, instructions resolve AGAIN |
 347 | 5 | **Deterministic Follow-Up** - Use post-action checks to guarantee critical actions |
