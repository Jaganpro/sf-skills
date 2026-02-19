<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Debugging & Observability Guide
   2 
   3 > Find the Leak Before It Finds You
   4 
   5 ---
   6 
   7 ## The Debugging Workflow
   8 
   9 ```
  10 ┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
  11 │ 📋 Interaction      │  →   │ 📊 Trace            │  →   │ ⚙️ Find the         │
  12 │    Details          │      │    Waterfall        │      │    Leak             │
  13 └─────────────────────┘      └─────────────────────┘      └─────────────────────┘
  14 ```
  15 
  16 ---
  17 
  18 ## The 4 Debugging Views
  19 
  20 | Tab | Icon | Description |
  21 |-----|------|-------------|
  22 | 📋 Interaction Details | List | The Summary View |
  23 | 📊 Trace Waterfall | Chart | The Technical View |
  24 | ↔️ Variable State Tracking | Arrows | Entry vs. Exit Values |
  25 | <> Script View with Linting | Code | Red Squiggles |
  26 
  27 ---
  28 
  29 ### View 1: Interaction Details (Summary)
  30 
  31 **Purpose**: High-level chronological list with AI-generated summaries
  32 
  33 **Shows:**
  34 - ✅ Input received from user
  35 - ✅ Reasoning decisions made
  36 - ✅ Actions executed
  37 - ✅ Output evaluation results
  38 
  39 **Best For**: Quickly understanding WHAT happened
  40 
  41 ---
  42 
  43 ### View 2: Trace Waterfall (Technical)
  44 
  45 **Purpose**: Granular view showing every internal step
  46 
  47 **Shows:**
  48 - ✅ Exact prompt sent to the LLM
  49 - ✅ Latency for each span (milliseconds)
  50 - ✅ Raw JSON input/output for every tool call
  51 - ✅ Variable state at each step
  52 
  53 **Best For**: Understanding WHY something happened
  54 
  55 ---
  56 
  57 ### View 3: Variable State Tracking
  58 
  59 **Purpose**: Real-time table of variable Entry vs Exit values
  60 
  61 **Shows:**
  62 - ✅ Which variables changed during each span
  63 - ✅ Critical security variables (verified, customer_id)
  64 - ✅ Values LLM used vs values it should have used
  65 
  66 **Best For**: Finding when LLM ignored variable state ("goal drift")
  67 
  68 ---
  69 
  70 ### View 4: Script View with Linting
  71 
  72 **Purpose**: Agent Script code with real-time syntax validation
  73 
  74 **Shows:**
  75 - ✅ Block ordering errors
  76 - ✅ Indentation issues
  77 - ✅ Missing required fields
  78 - ✅ Invalid resource references
  79 
  80 **Best For**: Catching errors before deployment
  81 
  82 ---
  83 
  84 ### View Selection Guide
  85 
  86 | Question | Use This View |
  87 |----------|---------------|
  88 | "What happened in this conversation?" | **Interaction Details** |
  89 | "What exactly did the LLM see?" | **Trace Waterfall** |
  90 | "Why did the variable have wrong value?" | **Variable State** |
  91 | "Why won't my agent compile?" | **Script View** |
  92 
  93 ---
  94 
  95 ## The 6 Span Types
  96 
  97 | # | Span Type | Internal Name | Description |
  98 |---|-----------|---------------|-------------|
  99 | 1 | ➡️ **Topic Enter** | `topic_enter` | Execution enters a new topic |
 100 | 2 | ▶ **before_reasoning** | `before_reasoning` | Deterministic pre-processing |
 101 | 3 | 🧠 **reasoning** | `reasoning` | LLM processes instructions |
 102 | 4 | ⚡ **Action Call** | `action_call` | Action invoked |
 103 | 5 | → **Transition** | `transition` | Topic navigation |
 104 | 6 | ✓ **after_reasoning** | `after_reasoning` | Deterministic post-processing |
 105 
 106 ---
 107 
 108 ## Reading a Trace Waterfall
 109 
 110 ### Example Timeline
 111 
 112 ```
 113 SPAN                    DURATION    TIMELINE
 114 ────────────────────────────────────────────────────────────────────
 115 ➡️ Topic Enter          15ms        ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 116 ▶ before_reasoning      850ms       ████████████████████░░░░░░░░░░░░
 117 🧠 reasoning            1250ms      ██████████████████████████████░░
 118 ⚡ Action Call          450ms       ██████████████░░░░░░░░░░░░░░░░░░
 119 ```
 120 
 121 ### Latency Benchmarks
 122 
 123 | Span Type | Expected Duration | If Slower... |
 124 |-----------|-------------------|--------------|
 125 | `topic_enter` | 10-20ms | Check topic complexity |
 126 | `before_reasoning` | 50-500ms | Data fetch issues |
 127 | `reasoning` | 1-3s | Normal LLM latency |
 128 | `action_call` | 100-500ms | External service slow |
 129 | `after_reasoning` | 10-50ms | Logging overhead |
 130 
 131 ---
 132 
 133 ## Variable State Analysis
 134 
 135 ### Entry vs Exit Pattern
 136 
 137 | Step | Variable | Entry | Exit | Problem? |
 138 |------|----------|-------|------|----------|
 139 | 1 | `customer_verified` | `False` | `False` | - |
 140 | 2 | `customer_verified` | `False` | `True` | - |
 141 | 3 | `refund_processed` | `False` | `True` | ⚠️ Processed while verified=False! |
 142 
 143 > **KEY INSIGHT**: If a critical variable like `is_verified` was `False` when an action executed, you've found your leak point.
 144 
 145 ---
 146 
 147 ## Common Debug Patterns
 148 
 149 ### Pattern 1: Wrong Policy Applied
 150 
 151 **Symptom**: Customer received wrong regional policy
 152 
 153 **Trace Analysis:**
 154 1. Check Variable State → `CustomerCountry` was empty at filter step
 155 2. Check variable declaration → `mutable string = ""`
 156 3. **Root Cause**: Should be `linked string` with `source: @session.Country`
 157 
 158 **Fix:**
 159 ```yaml
 160 # Wrong
 161 CustomerCountry: mutable string = ""
 162 
 163 # Correct
 164 CustomerCountry: linked string
 165   source: @session.Country
 166 ```
 167 
 168 ---
 169 
 170 ### Pattern 2: Action Executed Without Authorization
 171 
 172 **Symptom**: Refund processed without identity verification
 173 
 174 **Trace Analysis:**
 175 1. Check reasoning span → LLM selected `process_refund`
 176 2. Check action definition → No `available when` guard
 177 3. **Root Cause**: LLM could see and select unguarded action
 178 
 179 **Fix:**
 180 ```yaml
 181 # Wrong - no guard
 182 process_refund: @actions.process_refund
 183   description: "Issue refund"
 184 
 185 # Correct - guarded
 186 process_refund: @actions.process_refund
 187   description: "Issue refund"
 188   available when @variables.customer_verified == True
 189 ```
 190 
 191 ---
 192 
 193 ### Pattern 3: Post-Action Logic Didn't Run
 194 
 195 **Symptom**: CRM case wasn't created after refund approval
 196 
 197 **Trace Analysis:**
 198 1. Check instruction resolution order → Post-action check at bottom
 199 2. Check transition → Topic transitioned before check could run
 200 3. **Root Cause**: Post-action check must be at TOP
 201 
 202 **Fix:**
 203 ```yaml
 204 # Wrong - check at bottom
 205 instructions: ->
 206   | Help with refund.
 207   transition to @topic.next
 208 
 209   if @variables.refund_done:  # Never reaches here!
 210     run @actions.log_refund
 211 
 212 # Correct - check at TOP
 213 instructions: ->
 214   if @variables.refund_done:
 215     run @actions.log_refund
 216     transition to @topic.success
 217 
 218   | Help with refund.
 219 ```
 220 
 221 ---
 222 
 223 ### Pattern 4: Infinite Loop
 224 
 225 **Symptom**: Agent keeps returning to same topic
 226 
 227 **Trace Analysis:**
 228 1. Check transitions → `topic_enter` repeating for same topic
 229 2. Check conditions → No exit condition defined
 230 3. **Root Cause**: Missing state change or exit condition
 231 
 232 **Fix:**
 233 ```yaml
 234 # Wrong - no exit condition
 235 instructions: ->
 236   | Continue processing.
 237 
 238 # Correct - track state, add exit
 239 instructions: ->
 240   if @variables.processing_complete == True:
 241     transition to @topic.done
 242 
 243   | Continue processing.
 244   set @variables.step_count = @variables.step_count + 1
 245 ```
 246 
 247 ---
 248 
 249 ### Pattern 5: LLM Ignores Variable State (Goal Drift)
 250 
 251 **Symptom**: LLM makes decision contradicting variable value
 252 
 253 **Trace Analysis:**
 254 1. Check Variable State → Variable had correct value
 255 2. Check resolved instructions → Condition should have pruned text
 256 3. **Root Cause**: Using pipe syntax (`|`) instead of arrow (`->`)
 257 
 258 **Fix:**
 259 ```yaml
 260 # Wrong - pipe doesn't support conditionals
 261 instructions: |
 262   if @variables.verified:
 263     Help the user.
 264   # This is literal text, not a condition!
 265 
 266 # Correct - arrow enables conditionals
 267 instructions: ->
 268   if @variables.verified:
 269     | Help the user.
 270   else:
 271     | Please verify first.
 272 ```
 273 
 274 ---
 275 
 276 ## Diagnostic Checklist
 277 
 278 ### Quick Triage
 279 
 280 | Check | Command/Action |
 281 |-------|----------------|
 282 | Syntax valid? | `sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json` |
 283 | User exists? | `sf data query -q "SELECT Username FROM User WHERE Profile.Name='Einstein Agent User'"` |
 284 | Topic exists? | Search for topic name in script |
 285 | Variable initialized? | Check `variables:` block |
 286 
 287 ### Deep Investigation
 288 
 289 | Issue | What to Check |
 290 |-------|---------------|
 291 | Wrong output | Variable State (Entry/Exit values) |
 292 | Skipped logic | Instruction resolution order |
 293 | Security bypass | `available when` guards |
 294 | Data missing | Action target protocol, linked variable sources |
 295 | Slow response | Trace Waterfall latencies |
 296 
 297 ---
 298 
 299 ## The Big Picture
 300 
 301 > **"Prompts are suggestions. Guards are guarantees."**
 302 
 303 The LLM might ignore your instructions. The only way to truly prevent unwanted behavior is through **deterministic guards** like `available when`.
 304 
 305 **When you remove an action from the LLM's toolkit, it literally cannot invoke it. That's not a suggestion - that's enforcement.**
 306 
 307 ---
 308 
 309 ## Key Takeaways
 310 
 311 | # | Takeaway |
 312 |---|----------|
 313 | 1 | **Two Views for Two Purposes** - Interaction Details for quick understanding, Trace Waterfall for forensics |
 314 | 2 | **Entry vs Exit Reveals Problems** - Variable state changes show exactly when/where issues occurred |
 315 | 3 | **`available when` Blocks Actions** - Makes unauthorized actions invisible, not just discouraged |
 316 | 4 | **Post-Action at TOP** - Check for completed actions at the start of instructions |
 317 | 5 | **Linked vs Mutable** - Wrong variable modifier causes empty values |
 318 
 319 ---
 320 
 321 ## Planner Engine Differences
 322 
 323 Salesforce has multiple planner engines. Behavior differs between them, which affects debugging.
 324 
 325 | Capability | Java Planner (Legacy) | Atlas/Daisy Planner (New) |
 326 |-----------|----------------------|--------------------------|
 327 | **Citations** | Supported | May not be supported |
 328 | **Localization** | Full support | Limited support |
 329 | **Lightning UI components** | Renders in chat | Does not render |
 330 | **`$Context.ConversationContext`** | Available | May not be available |
 331 | **Debug logging detail** | Verbose | More concise |
 332 | **CopilotContext reliability** | Consistent | May vary |
 333 | **Trace data availability** | Requires committed version | Requires committed + activated version |
 334 
 335 ### Identifying Your Planner
 336 
 337 Check Setup > Agentforce > Agent Settings to see which planner engine is active. Behavior differences between planners are the most common source of "it worked in dev but not in prod" issues.
 338 
 339 ### Debugging Tips by Planner
 340 
 341 **Java Planner:**
 342 - More verbose trace output — look for detailed span data
 343 - Lightning components render — test rich UI interactions
 344 - Citations appear in responses — verify citation accuracy
 345 
 346 **Atlas/Daisy Planner:**
 347 - Trace output may be more concise — focus on variable state changes
 348 - Lightning components won't render — test text-based fallbacks
 349 - Context variables may behave differently — verify `$Context` access patterns
