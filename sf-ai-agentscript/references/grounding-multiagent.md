<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Data Grounding & Multi-Agent Guide
   2 
   3 > High-stakes enterprise agents cannot rely on training data. They must be **grounded in real-time business data** and coordinate with **specialized agents** for complex tasks.
   4 
   5 ---
   6 
   7 ## Two Pillars
   8 
   9 | Pillar | Icon | Description |
  10 |--------|------|-------------|
  11 | 🔽 **Retriever Actions** | Filter | Dynamic filtering ensures agents only see relevant data |
  12 | 🔀 **Multi-Agent SOMA** | Branch | Primary agents delegate to expert agents |
  13 
  14 ---
  15 
  16 ## Retriever Actions
  17 
  18 ### Connecting Agents to Data Cloud
  19 
  20 Retriever Actions connect your agent to Data Cloud Search Indexes, enabling context-aware knowledge retrieval.
  21 
  22 **Capabilities:**
  23 - ✅ Search Index wraps unstructured data (PDFs, docs, web pages)
  24 - ✅ Chunking parses text, tables, and images into searchable segments
  25 - ✅ Returns relevant chunks based on semantic similarity
  26 - ✅ Integrated with Data Cloud for current data
  27 
  28 ### Basic Retriever Action
  29 
  30 ```yaml
  31 actions:
  32   fetch_refund_policy:
  33     description: "Retrieve refund policy from knowledge base"
  34     target: "retriever://RefundSOP_Retriever"
  35     inputs:
  36       query: string
  37     outputs:
  38       chunks: list[object]
  39       relevance_scores: list[number]
  40 ```
  41 
  42 ### Retrieval Pipeline
  43 
  44 ```
  45 ┌────────────┐    ┌────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐
  46 │ User Query │ → │ Dynamic Filter │ → │ Data Cloud Index│ → │ Relevant Chunks │ → │ LLM Response │
  47 └────────────┘    └────────────────┘    └─────────────────┘    └─────────────────┘    └──────────────┘
  48 ```
  49 
  50 ---
  51 
  52 ### Filtered Retrieval with Flows
  53 
  54 > Agent Script cannot filter retrieval results inline. When you need filtered knowledge retrieval, wrap the retriever in a Flow.
  55 
  56 **Problem**: Direct `retriever://` targets don't support inline filtering.
  57 
  58 **Solution**: Use `flow://` to wrap the retriever with filter logic.
  59 
  60 ```yaml
  61 # WRONG - No filtering capability
  62 actions:
  63   fetch_policy:
  64     target: "retriever://RefundSOP_Index"  # Can't filter!
  65 
  66 # CORRECT - Flow handles filtering
  67 actions:
  68   fetch_regional_policy:
  69     description: "Fetch policy filtered by customer region"
  70     inputs:
  71       query: string
  72       customer_country: string
  73         description: "Country code for regional filtering"
  74     outputs:
  75       chunks: list[object]
  76       policy_region: string
  77     target: "flow://GetRegionalRefundPolicy"  # Flow filters internally
  78 ```
  79 
  80 > ⚠️ **Security Note**: Filtering in a Flow prevents accidental cross-region data exposure. The Flow enforces the filter - the LLM cannot bypass it.
  81 
  82 ---
  83 
  84 ### Safe Expressions
  85 
  86 Agent Script uses a safe subset of Python for expressions:
  87 
  88 **Allowed Operations:**
  89 | Category | Operators |
  90 |----------|-----------|
  91 | **Comparison** | `==`, `!=` (not-equal), `>`, `<`, `>=`, `<=` |
  92 | **Logical** | `and`, `or`, `not` |
  93 | **String** | `contains`, `startswith`, `endswith` |
  94 
  95 **Security Constraints:**
  96 - ❌ No `import` statements
  97 - ❌ No file access
  98 - ❌ No arbitrary code execution
  99 
 100 ```python
 101 # Valid safe expressions:
 102 @variables.risk_score > 80
 103 @variables.country == "Germany"
 104 @variables.is_vip and @variables.order_total > 100
 105 not @variables.verified
 106 
 107 # INVALID (security risk):
 108 import os     # NOT ALLOWED
 109 eval(...)     # NOT ALLOWED
 110 open(...)     # NOT ALLOWED
 111 ```
 112 
 113 ---
 114 
 115 ## The 6 Action Target Protocols
 116 
 117 Every action uses a `target:` field to specify where to send the request.
 118 
 119 | Protocol | Use When | Example |
 120 |----------|----------|---------|
 121 | `flow://` | Data operations, business logic | `target: "flow://GetOrderStatus"` |
 122 | `apex://` | Custom calculations, validation | `target: "apex://RefundCalculator"` |
 123 | `generatePromptResponse://` | Grounded LLM responses | `target: "generatePromptResponse://Summary"` |
 124 | `retriever://` | RAG knowledge search | `target: "retriever://Policy_Index"` |
 125 | `externalService://` | Third-party APIs | `target: "externalService://AddressAPI"` |
 126 | `standardInvocableAction://` | Built-in SF actions | `target: "standardInvocableAction://email"` |
 127 
 128 ---
 129 
 130 ### Protocol 1: Salesforce Flow (`flow://`)
 131 
 132 **Use Case**: Data operations, business logic, filtered retrieval
 133 
 134 ```yaml
 135 actions:
 136   get_order_status:
 137     description: "Retrieves order details by order number"
 138     inputs:
 139       order_number: string
 140         description: "The order ID to look up"
 141     outputs:
 142       status: string
 143       tracking_number: string
 144     target: "flow://GetOrderStatus"
 145 ```
 146 
 147 ---
 148 
 149 ### Protocol 2: Apex Class (`apex://`)
 150 
 151 **Use Case**: Custom calculations, complex validation
 152 
 153 ```yaml
 154 actions:
 155   calculate_refund:
 156     description: "Calculate refund amount based on policy rules"
 157     inputs:
 158       order_id: string
 159       refund_reason: string
 160     outputs:
 161       refund_amount: currency
 162       requires_approval: boolean
 163     target: "apex://RefundCalculatorService"
 164 ```
 165 
 166 ---
 167 
 168 ### Protocol 3: Prompt Template (`generatePromptResponse://`)
 169 
 170 **Use Case**: Grounded LLM responses, summarization
 171 
 172 ```yaml
 173 actions:
 174   summarize_case:
 175     description: "Generate a summary of the customer case"
 176     inputs:
 177       "Input:caseId": id
 178         description: "The Case record ID"
 179     outputs:
 180       promptResponse: string
 181         is_displayable: True
 182     target: "generatePromptResponse://Generate_Case_Summary"
 183 ```
 184 
 185 > ⚠️ Note: Input keys use quoted strings with colon notation (`"Input:caseId"`)
 186 
 187 ---
 188 
 189 ### Protocol 4: Data Cloud Retriever (`retriever://`)
 190 
 191 **Use Case**: Knowledge base search, FAQ lookup
 192 
 193 ```yaml
 194 actions:
 195   search_knowledge:
 196     description: "Search the knowledge base for relevant info"
 197     inputs:
 198       query: string
 199     outputs:
 200       chunks: list[object]
 201       relevance_scores: list[number]
 202     target: "retriever://RefundPolicy_Retriever"
 203 ```
 204 
 205 ---
 206 
 207 ### Protocol 5: External Service (`externalService://`)
 208 
 209 **Use Case**: Third-party APIs via Named Credentials
 210 
 211 ```yaml
 212 actions:
 213   verify_address:
 214     description: "Validate shipping address via external API"
 215     inputs:
 216       street: string
 217       city: string
 218       postal_code: string
 219     outputs:
 220       is_valid: boolean
 221       normalized_address: object
 222     target: "externalService://AddressValidation"
 223 ```
 224 
 225 ---
 226 
 227 ### Protocol 6: Standard Invocable (`standardInvocableAction://`)
 228 
 229 **Use Case**: Built-in Salesforce actions (email, tasks, Chatter)
 230 
 231 ```yaml
 232 actions:
 233   send_email:
 234     description: "Send confirmation email to customer"
 235     inputs:
 236       recipient_email: string
 237       template_id: id
 238     outputs:
 239       success: boolean
 240     target: "standardInvocableAction://emailSimple"
 241 ```
 242 
 243 ---
 244 
 245 ### Protocol Selection Guide
 246 
 247 | If you need... | Use this protocol |
 248 |----------------|-------------------|
 249 | Complex data queries, record updates | `flow://` |
 250 | Custom calculations, validation | `apex://` |
 251 | LLM-generated summaries | `generatePromptResponse://` |
 252 | Knowledge search, RAG | `retriever://` |
 253 | External REST APIs | `externalService://` |
 254 | Standard SF actions | `standardInvocableAction://` |
 255 
 256 ### Conditional Knowledge Retrieval Pattern
 257 
 258 Use `available when` to route to different knowledge bases based on user context:
 259 
 260 ```yaml
 261 topic knowledge_router:
 262    description: "Route to appropriate knowledge base"
 263    reasoning:
 264       instructions: ->
 265          | Let me find the right information for you.
 266       actions:
 267          search_premium_kb: @actions.search_premium_knowledge
 268             description: "Search premium support articles"
 269             available when @variables.customer_tier == "premium"
 270             with query = ...
 271          search_standard_kb: @actions.search_standard_knowledge
 272             description: "Search standard support articles"
 273             available when @variables.customer_tier != "premium"
 274             with query = ...
 275 ```
 276 
 277 > **Why this matters**: Different customer tiers may need access to different knowledge bases with different SLA guidance, pricing, or support procedures. The `available when` guard ensures the LLM can only search the appropriate knowledge base.
 278 
 279 ---
 280 
 281 ## Same Org Multi-Agent (SOMA)
 282 
 283 When a primary agent encounters specialized needs, it can coordinate with expert agents.
 284 
 285 ### Two Coordination Patterns
 286 
 287 | Pattern | Description | Return Behavior |
 288 |---------|-------------|-----------------|
 289 | 🔀 **Delegation** | Farm out, then return | ✅ Control returns to original agent |
 290 | ➡️ **Handoff** | Transfer permanently | ❌ No return - original agent exits |
 291 
 292 ---
 293 
 294 ### Pattern 1: Delegation
 295 
 296 **Flow:**
 297 ```
 298 ┌─────────┐    DELEGATE    ┌────────────┐    RETURN    ┌─────────┐
 299 │ Primary │ ─────────────▶ │ Specialist │ ───────────▶ │ Primary │
 300 └─────────┘                └────────────┘              └─────────┘
 301 ```
 302 
 303 **Use Cases:**
 304 - Tax questions → Compliance Agent
 305 - Technical issues → Support Specialist
 306 - Order changes → Fulfillment Agent
 307 
 308 **Implementation:**
 309 ```yaml
 310 # Delegation uses topic reference (NOT @utils.transition)
 311 # Parent orchestrates — child returns control
 312 reasoning:
 313   actions:
 314     ask_compliance: @topic.compliance
 315       description: "Consult compliance specialist on tax questions"
 316       # ✅ Returns to this topic after specialist finishes
 317 
 318     ask_refund_help: @topic.refund_specialist
 319       description: "Consult refund specialist for calculations"
 320       # ✅ Control returns to continue conversation
 321 ```
 322 
 323 ---
 324 
 325 ### Pattern 2: Handoff
 326 
 327 **Flow:**
 328 ```
 329 ┌─────────┐    HANDOFF    ┌────────┐    NO RETURN
 330 │ Primary │ ────────────▶ │ Target │ ────────────▶ ✗
 331 └─────────┘               └────────┘
 332 ```
 333 
 334 **Use Cases:**
 335 - Escalation to human agent
 336 - Domain boundary (Sales → Support)
 337 - Fraud detection requiring specialized handling
 338 
 339 **Implementation:**
 340 ```yaml
 341 # Permanent handoff - conversation leaves this agent
 342 reasoning:
 343   actions:
 344     escalate_to_human: @utils.escalate
 345       description: "Transfer to live support"
 346       # Conversation ends for this agent
 347 ```
 348 
 349 ---
 350 
 351 ### Delegation vs Handoff Decision
 352 
 353 | Use This | When You Need |
 354 |----------|---------------|
 355 | `@topic.X` (in reasoning.actions) | Temporary delegation — control returns |
 356 | `@utils.transition to @topic.X` | Permanent handoff — no return |
 357 | `@utils.escalate` | Permanent handoff to human |
 358 | `@agent.X` (Connections) | Permanent handoff to another agent |
 359 
 360 > **KEY INSIGHT**: The difference is whether the original agent continues after the specialist finishes.
 361 
 362 ### SOMA Limitations (Community-Confirmed)
 363 
 364 | Limitation | Description | Workaround |
 365 |-----------|-------------|------------|
 366 | Single action per supervision call | Delegated topic can only execute ONE action before returning | Break complex operations into separate delegation calls |
 367 | `related_agent` nodes may fail | SOMA configuration with related agent references can cause "Node does not have corresponding topic" errors | Use `@topic.X` delegation within same agent instead |
 368 | No cross-agent variable sharing | Delegated agents cannot read/write parent agent's variables | Pass data through action inputs/outputs |
 369 
 370 ---
 371 
 372 ## Variable Configuration for Grounding
 373 
 374 ### Linked Variables for Session Context
 375 
 376 ```yaml
 377 variables:
 378   # WRONG - mutable allows modification
 379   CustomerCountry: mutable string = ""
 380 
 381   # CORRECT - linked preserves session data
 382   CustomerCountry: linked string
 383     source: @session.Country
 384 ```
 385 
 386 **Why This Matters:**
 387 - `mutable string = ""` starts empty - filter won't work
 388 - `linked string` pulls from session - filter gets real value
 389 
 390 ---
 391 
 392 ### Debug Exercise: Wrong Policy Applied
 393 
 394 **Symptom**: German customer received US refund policy
 395 
 396 **Root Cause Trace:**
 397 
 398 | Step | Wrong Implementation | Correct Implementation |
 399 |------|---------------------|------------------------|
 400 | 1. Session Start | `CustomerCountry: ""` | `CustomerCountry: "Germany"` |
 401 | 2. Filter | `Region == ""` | `Region == "Germany"` |
 402 | 3. Knowledge Fetch | US_Refund_Policy | EU_Refund_Policy_GDPR |
 403 | 4. Refund | $10 credit | Full refund (€45.99) |
 404 
 405 **Fix**: Change `mutable string = ""` to `linked string` with `source: @session.Country`
 406 
 407 ---
 408 
 409 ## Best Practices
 410 
 411 ### 1. Always Filter Regional Data
 412 Never return unfiltered results for region-specific policies.
 413 
 414 ### 2. Use Flows for Complex Filtering
 415 Agent Script can't filter inline - wrap retrievers in Flows.
 416 
 417 ### 3. Validate Session Variables
 418 Ensure linked variables have sources - empty values cause wrong retrievals.
 419 
 420 ### 4. Choose Delegation vs Handoff Carefully
 421 - `@topic.X` (delegation) — returns control to parent topic
 422 - `@utils.transition to @topic.X` (handoff) — permanent, no return
 423 
 424 ### 5. Use `available when` for Sensitive Protocols
 425 Guard external service calls with verification checks.
 426 
 427 ```yaml
 428 actions:
 429   call_payment_api: @actions.charge_card
 430     target: "externalService://PaymentGateway"
 431     available when @variables.customer_verified == True
 432 ```
