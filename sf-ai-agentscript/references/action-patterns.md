<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Advanced Action Patterns
   2 
   3 > Context-aware descriptions, instruction references, and binding strategies
   4 
   5 **Related**: [SKILL.md — Action Chaining](../SKILL.md) | [action-prompt-templates.md](action-prompt-templates.md)
   6 
   7 ---
   8 
   9 ## 1. Context-Aware Action Descriptions
  10 
  11 The same underlying action can have **different descriptions** across topics. This improves LLM action selection by matching the description to the user's expertise level or business context.
  12 
  13 ### Beginner vs. Advanced Mode
  14 
  15 ```agentscript
  16 topic beginner_help:
  17   reasoning:
  18     actions:
  19       search_help: @actions.search_knowledge_base
  20         description: "Search for help articles"
  21 
  22 topic advanced_help:
  23   reasoning:
  24     actions:
  25       search_help: @actions.search_knowledge_base
  26         description: "Execute knowledge base query with advanced filters (type, date range, tags). Returns paginated results with relevance scoring. Supports Boolean operators and wildcards."
  27 ```
  28 
  29 **Result**: Beginner users see simple language; advanced users see technical capabilities.
  30 
  31 ### `available when` + Description Override
  32 
  33 Combine conditional availability with contextual descriptions for stronger control:
  34 
  35 ```agentscript
  36 topic business_hours:
  37   reasoning:
  38     actions:
  39       create_case: @actions.create_support_case
  40         available when @variables.during_business_hours == True
  41         description: "Create a support case for immediate assignment to available agents"
  42 
  43 topic after_hours:
  44   reasoning:
  45     actions:
  46       create_case: @actions.create_support_case
  47         available when @variables.during_business_hours == False
  48         description: "Create a support case for next-business-day follow-up"
  49 ```
  50 
  51 ### When to use description overrides
  52 
  53 | Scenario | Use Override? |
  54 |----------|--------------|
  55 | Same action serves different user expertise levels | ✅ Yes |
  56 | Same action has different context in different topics | ✅ Yes |
  57 | Action is always used the same way | ❌ No — single description suffices |
  58 | Action name alone is already clear | ❌ No — don't over-engineer |
  59 
  60 ---
  61 
  62 ## 2. Instruction Action References
  63 
  64 The `{!@actions.action_name}` syntax embeds a **reference to the full action definition** (not just the name) into reasoning instructions. This gives the LLM richer context about the action's inputs, outputs, and purpose — improving selection accuracy when multiple actions could apply.
  65 
  66 ### Basic Syntax
  67 
  68 ```agentscript
  69 topic business_hours_routing:
  70   data:
  71     @variables.next_open_time: ...
  72 
  73   reasoning:
  74     instructions: ->
  75       if @variables.next_open_time:
  76         | We are currently OUTSIDE business hours.
  77           The next available time is {!@variables.next_open_time}.
  78           Create a support case using {!@actions.create_case} to ensure
  79           follow-up during business hours.
  80       else:
  81         | We are currently WITHIN business hours.
  82           Connect the customer to live support using {!@actions.transfer_to_agent}.
  83 ```
  84 
  85 ### Conditional Instruction Patterns
  86 
  87 Guide the LLM toward specific actions based on state:
  88 
  89 ```agentscript
  90 topic identity_verification:
  91   reasoning:
  92     instructions: ->
  93       if @variables.verification_attempts < 3:
  94         | Verify identity using {!@actions.verify_email_code}
  95           or {!@actions.verify_phone_code}.
  96       else:
  97         | Maximum attempts reached. Escalate using {!@actions.escalate_to_security}.
  98 ```
  99 
 100 ```agentscript
 101 topic order_inquiry:
 102   reasoning:
 103     instructions: ->
 104       if @variables.order_status == "shipped":
 105         | Track shipment using {!@actions.get_tracking_info}.
 106       if @variables.order_status == "processing":
 107         | Check status using {!@actions.get_fulfillment_status}.
 108       if @variables.order_status == "cancelled":
 109         | Process refund using {!@actions.initiate_refund}.
 110 ```
 111 
 112 ### Combining with `available when`
 113 
 114 For maximum control, use both instruction references AND deterministic guards:
 115 
 116 ```agentscript
 117 topic secure_operations:
 118   reasoning:
 119     instructions: ->
 120       if @variables.verified == True:
 121         | You can now access sensitive operations using {!@actions.view_account_details}.
 122       else:
 123         | Please verify your identity first.
 124 
 125     actions:
 126       view_account_details: @actions.get_account_info
 127         available when @variables.verified == True
 128         description: "View sensitive account information"
 129 ```
 130 
 131 **Result**: Instruction guidance steers the LLM, while `available when` provides a deterministic safety net.
 132 
 133 ### Descriptions vs. References: When to Use Which
 134 
 135 | Approach | When to Use |
 136 |----------|-------------|
 137 | **Description overrides** | Action needs different descriptions per topic/context |
 138 | **Instruction references** | Need to explicitly guide LLM toward an action in instructions |
 139 | **Both** | Maximum control — override description AND reference in instructions |
 140 
 141 ---
 142 
 143 ## 3. Input Binding Decision Matrix
 144 
 145 Agent Script supports four input binding approaches. Use this matrix to choose:
 146 
 147 | Binding | Syntax | Use When | Example |
 148 |---------|--------|----------|---------|
 149 | **LLM slot-filling** | `...` | User provides the value in conversation | `with query=...` |
 150 | **Variable binding** | `@variables.X` | Data exists from prior turns or actions | `with id=@variables.customer_id` |
 151 | **Fixed value** | literal | System constant or business rule | `with format="pdf"` |
 152 | **Mixed** | combination | Complex actions needing multiple sources | See below |
 153 
 154 ### Mixed Binding Example
 155 
 156 ```agentscript
 157 process_refund: @actions.process_refund_request
 158   with order_id=@variables.order_id          # Variable — from previous action
 159        reason=...                             # Slot-fill — user explains why
 160        amount=@variables.order_total          # Variable — stored value
 161        refund_method="original_payment"       # Fixed — business rule
 162        require_approval=True                  # Fixed — policy constant
 163 ```
 164 
 165 ### Combined Pattern: Capture → Reuse → Extend
 166 
 167 ```agentscript
 168 # Step 1: Capture data from first action
 169 search: @actions.search_products
 170   with query=...
 171   set @variables.product_id = @outputs.top_result_id
 172 
 173 # Step 2: Reuse captured value + collect new input
 174 add_to_cart: @actions.add_to_cart
 175   with product_id=@variables.product_id      # Reuse from step 1
 176        quantity=...                           # New user input
 177        apply_discount=True                    # Business rule
 178 ```
 179 
 180 ---
 181 
 182 ## 4. Callback Behavior Notes
 183 
 184 These supplement the "Action Chaining with `run` Keyword" section in SKILL.md.
 185 
 186 ### Callbacks only execute if the parent action succeeds
 187 
 188 ```agentscript
 189 verify_payment: @actions.verify_payment_method
 190   with payment_method_id=...
 191   set @variables.verified = @outputs.success
 192   run @actions.process_payment                 # Only runs if verify succeeds
 193     with payment_method_id=...
 194 ```
 195 
 196 If `verify_payment_method` fails (Flow error, Apex exception), `process_payment` **will not execute**. Design your conversation flow to handle the failure case separately.
 197 
 198 ### Flatten, don't nest
 199 
 200 ```agentscript
 201 # ❌ WRONG — nested callbacks (not allowed)
 202 action1: @actions.first
 203   run @actions.second
 204     run @actions.third     # ERROR: Nested callbacks not supported
 205 
 206 # ✅ CORRECT — sequential callbacks (flat structure)
 207 action1: @actions.first
 208   run @actions.second
 209   run @actions.third
 210 ```
 211 
 212 ### Practical callback chain: Create → Notify → Log
 213 
 214 ```agentscript
 215 create_case: @actions.create_support_case
 216   with subject=...
 217        description=...
 218        priority=@variables.priority
 219   set @variables.case_id = @outputs.id
 220   run @actions.notify_team
 221     with case_id=@variables.case_id
 222          priority=@variables.priority
 223   run @actions.log_case_creation
 224     with case_id=@variables.case_id
 225 ```
 226 
 227 ---
 228 
 229 ## 5. Additional Error Patterns
 230 
 231 These supplement the "Common Issues" table in SKILL.md.
 232 
 233 | Error | Cause | Fix |
 234 |-------|-------|-----|
 235 | Missing colon after action name | `my_action` instead of `my_action:` | Add colon: `my_action:` |
 236 | Missing type annotation on input | `email:` with no type | Add type: `email: string` |
 237 | Wrong target protocol | `flows://MyFlow` | Use `flow://MyFlow` (no trailing `s`) |
 238 | `Input:` without quotes | `with Input:email=...` | Quote it: `with "Input:email"=...` |
 239 | `...` as variable default | `my_var: mutable string = ...` | Use `""` for defaults; `...` is slot-filling only |
 240 | Vague action description | `description: "Does a search"` | Be specific: `description: "Searches KB for articles matching the query"` |
 241 
 242 ---
 243 
 244 ---
 245 
 246 ## 6. JSON Parsing Pattern
 247 
 248 Agent Script cannot parse JSON strings inline. When an action returns a JSON string that needs to be decomposed into individual fields, use a Flow or Apex action to parse it.
 249 
 250 ### Problem
 251 
 252 ```agentscript
 253 # This will NOT work - cannot parse JSON inline in Agent Script
 254 set @variables.name = @outputs.json_response["name"]     # Not supported
 255 set @variables.email = @outputs.json_response.email       # May work for objects, not JSON strings
 256 ```
 257 
 258 ### Solution: Flow/Apex JSON Parser
 259 
 260 ```agentscript
 261 # Step 1: Call the action that returns JSON
 262 get_data: @actions.fetch_external_data
 263    with endpoint = "customer_profile"
 264    set @variables.raw_json = @outputs.response_body
 265 
 266 # Step 2: Pass JSON to a parser action (Flow or Apex)
 267 parse: @actions.parse_json_response
 268    with json_string = @variables.raw_json
 269    set @variables.customer_name = @outputs.name
 270    set @variables.customer_email = @outputs.email
 271    set @variables.customer_tier = @outputs.tier
 272 ```
 273 
 274 ### Apex Parser Example
 275 
 276 ```apex
 277 public class JsonParserAction {
 278     public class ParseRequest {
 279         @InvocableVariable(required=true)
 280         public String jsonString;
 281     }
 282 
 283     public class ParseResult {
 284         @InvocableVariable public String name;
 285         @InvocableVariable public String email;
 286         @InvocableVariable public String tier;
 287     }
 288 
 289     @InvocableMethod(label='Parse Customer JSON')
 290     public static List<ParseResult> parse(List<ParseRequest> requests) {
 291         List<ParseResult> results = new List<ParseResult>();
 292         for (ParseRequest req : requests) {
 293             Map<String, Object> parsed = (Map<String, Object>) JSON.deserializeUntyped(req.jsonString);
 294             ParseResult result = new ParseResult();
 295             result.name = (String) parsed.get('name');
 296             result.email = (String) parsed.get('email');
 297             result.tier = (String) parsed.get('tier');
 298             results.add(result);
 299         }
 300         return results;
 301     }
 302 }
 303 ```
 304 
 305 > **Tip**: For complex nested JSON, create typed Apex wrapper classes instead of using `deserializeUntyped`.
 306 
 307 ---
 308 
 309 *Consolidated from @kunello's [PR #20](https://github.com/Jaganpro/sf-skills/pull/20) research on Agent Script Recipes action configuration patterns.*
