<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Topic Architecture Worksheet
   2 
   3 ## Agent Overview
   4 
   5 **Agent Name:** ShopBot
   6 **Agent Purpose:** Assist online retail customers with order tracking, product search, returns, account management, and store information
   7 **Primary Channel:** Web Chat, Mobile App
   8 **Deployment Scope:** External (consumer-facing)
   9 
  10 ## Action Inventory
  11 
  12 | Action ID | Action Name | Type | Backend | Description |
  13 |-----------|-------------|------|---------|-------------|
  14 | ACT-001 | Track Order | Flow | OrderTrackingFlow | Retrieves real-time shipment status by order number |
  15 | ACT-002 | Update Delivery Address | Flow | UpdateShippingFlow | Modifies delivery address for in-transit orders |
  16 | ACT-003 | Estimate Delivery Date | Apex | DeliveryEstimator | Calculates estimated delivery based on ZIP and carrier |
  17 | ACT-004 | Search Products | Flow | ProductSearchFlow | Searches catalog by keyword, category, or SKU |
  18 | ACT-005 | Check Product Availability | Apex | InventoryChecker | Verifies in-stock status by store or warehouse |
  19 | ACT-006 | Get Product Recommendations | Apex | RecommendationEngine | Suggests products based on browsing/purchase history |
  20 | ACT-007 | Compare Products | Flow | ProductComparisonFlow | Side-by-side comparison of up to 3 products |
  21 | ACT-008 | Initiate Return | Flow | ReturnInitiationFlow | Starts return process and generates return label |
  22 | ACT-009 | Check Return Eligibility | Apex | ReturnEligibilityChecker | Validates if item is within return window |
  23 | ACT-010 | Process Exchange | Flow | ExchangeFlow | Swaps item for different size/color |
  24 | ACT-011 | Track Return Status | Flow | ReturnTrackingFlow | Shows status of initiated return |
  25 | ACT-012 | Update Account Info | Flow | AccountUpdateFlow | Changes email, phone, password |
  26 | ACT-013 | View Order History | Flow | OrderHistoryFlow | Displays past 12 months of orders |
  27 | ACT-014 | Manage Payment Methods | Flow | PaymentManagementFlow | Adds/removes credit cards, PayPal |
  28 | ACT-015 | View Loyalty Points | Flow | LoyaltyPointsFlow | Shows points balance and redemption options |
  29 | ACT-016 | Find Store Locations | Flow | StoreLocatorFlow | Finds nearest stores by ZIP or city |
  30 | ACT-017 | Check Store Hours | Knowledge | StoreInfoKB | Retrieves hours, holiday closures, services |
  31 | ACT-018 | Schedule In-Store Pickup | Flow | PickupSchedulingFlow | Books time slot for BOPIS orders |
  32 | ACT-019 | Apply Promo Code | Flow | PromoCodeFlow | Validates and applies discount codes to cart |
  33 | ACT-020 | Size Guide Lookup | Knowledge | SizeGuideKB | Provides sizing charts by brand/category |
  34 
  35 **Total Actions:** 20
  36 
  37 ## Topic Groupings
  38 
  39 ### Topic 1: Order Tracking
  40 
  41 **Classification Description:**
  42 ```
  43 Questions about finding orders, checking delivery status, tracking shipments, updating delivery addresses, or estimating when packages will arrive.
  44 ```
  45 
  46 **Actions Assigned:**
  47 - Track Order (ACT-001)
  48 - Update Delivery Address (ACT-002)
  49 - Estimate Delivery Date (ACT-003)
  50 
  51 **Scope Definition:**
  52 This topic handles all inquiries related to orders that have been placed and are in fulfillment or transit. Covers tracking numbers, delivery updates, carrier information, and address changes for in-transit packages.
  53 
  54 **Out-of-Scope (within this topic):**
  55 - Order cancellations (must escalate to customer service if order hasn't shipped)
  56 - Returns or refunds (handled by Returns & Exchanges topic)
  57 - Pre-purchase delivery estimates (handled by Product Search topic)
  58 
  59 ---
  60 
  61 ### Topic 2: Product Search
  62 
  63 **Classification Description:**
  64 ```
  65 Finding products, checking what's in stock, getting recommendations, comparing items, looking up sizes, or asking about product features and availability.
  66 ```
  67 
  68 **Actions Assigned:**
  69 - Search Products (ACT-004)
  70 - Check Product Availability (ACT-005)
  71 - Get Product Recommendations (ACT-006)
  72 - Compare Products (ACT-007)
  73 - Size Guide Lookup (ACT-020)
  74 
  75 **Scope Definition:**
  76 Helps customers discover and evaluate products. Includes keyword search, category browsing, inventory checks, personalized recommendations, feature comparisons, and sizing information.
  77 
  78 **Out-of-Scope (within this topic):**
  79 - Adding items to cart or completing purchase (direct users to website/app)
  80 - Price negotiations or bulk discounts (escalate to sales team)
  81 - Custom or special orders (escalate to customer service)
  82 
  83 ---
  84 
  85 ### Topic 3: Returns & Exchanges
  86 
  87 **Classification Description:**
  88 ```
  89 Starting a return, checking if something can be returned, exchanging items for different sizes or colors, tracking return status, or asking about refund timelines.
  90 ```
  91 
  92 **Actions Assigned:**
  93 - Initiate Return (ACT-008)
  94 - Check Return Eligibility (ACT-009)
  95 - Process Exchange (ACT-010)
  96 - Track Return Status (ACT-011)
  97 
  98 **Scope Definition:**
  99 Manages the complete returns and exchange lifecycle, from eligibility verification through return label generation and refund tracking. Covers standard 30-day return policy and exchanges for size/color.
 100 
 101 **Out-of-Scope (within this topic):**
 102 - Returns outside 30-day window (escalate for exception review)
 103 - Damaged or defective items (escalate to quality team)
 104 - Gift returns without receipt (escalate to customer service)
 105 
 106 ---
 107 
 108 ### Topic 4: Account Management
 109 
 110 **Classification Description:**
 111 ```
 112 Updating account information like email or password, viewing past orders, managing saved payment methods, or checking loyalty points and rewards.
 113 ```
 114 
 115 **Actions Assigned:**
 116 - Update Account Info (ACT-012)
 117 - View Order History (ACT-013)
 118 - Manage Payment Methods (ACT-014)
 119 - View Loyalty Points (ACT-015)
 120 
 121 **Scope Definition:**
 122 Self-service account management for registered customers. Includes profile updates, order history access, payment method management, and loyalty program information.
 123 
 124 **Out-of-Scope (within this topic):**
 125 - Account deletion or data export requests (escalate to privacy team)
 126 - Forgotten passwords (direct to password reset flow)
 127 - Loyalty program enrollment changes (escalate to loyalty team)
 128 
 129 ---
 130 
 131 ### Topic 5: Store Information
 132 
 133 **Classification Description:**
 134 ```
 135 Finding physical store locations, checking store hours, scheduling in-store pickup, or asking about services available at specific stores.
 136 ```
 137 
 138 **Actions Assigned:**
 139 - Find Store Locations (ACT-016)
 140 - Check Store Hours (ACT-017)
 141 - Schedule In-Store Pickup (ACT-018)
 142 
 143 **Scope Definition:**
 144 Information about physical retail locations, including addresses, hours, special services (alterations, gift wrapping), and buy-online-pickup-in-store (BOPIS) scheduling.
 145 
 146 **Out-of-Scope (within this topic):**
 147 - Product availability at specific stores (use Product Search topic's inventory check)
 148 - Event hosting or private shopping appointments (escalate to store manager)
 149 - Career/employment inquiries (direct to careers website)
 150 
 151 ---
 152 
 153 ## Topic Distinctness Matrix
 154 
 155 | Topic Pair | Semantic Overlap | Confusable Utterances | Mitigation |
 156 |------------|------------------|----------------------|------------|
 157 | Order Tracking ↔ Returns & Exchanges | Medium | "Where is my return?" | Keyword detection: "return" triggers Returns topic even if phrased as tracking |
 158 | Product Search ↔ Store Information | Low | "Do you have this in stock at the downtown store?" | Two-step flow: Product Search checks inventory, then Store Information provides address/hours |
 159 | Account Management ↔ Order Tracking | Medium | "I need to see my orders" | Context matters: if user wants to track a specific order → Order Tracking; if browsing history → Account Management |
 160 | Returns & Exchanges ↔ Account Management | Low | "Can I see my return history?" | Return history is part of Order History (Account Management), but active returns → Returns & Exchanges topic |
 161 
 162 ## Cross-Topic Interaction Matrix
 163 
 164 | From Topic | To Topic | Interaction Type | Trigger | Example |
 165 |------------|----------|------------------|---------|---------|
 166 | Order Tracking | Returns & Exchanges | Sequential | Order received but customer wants to return | "My package arrived but the color is wrong" → Start in Order Tracking, transition to Initiate Return |
 167 | Product Search | Store Information | Conditional | Customer wants to buy in-store | "I found the shoes I want—can I pick them up today?" → Product Search finds item, Store Information schedules pickup |
 168 | Returns & Exchanges | Account Management | Sequential | Return processed, customer wants refund confirmation | "My return was received—where's my refund?" → Return tracking shows received, Account Management shows order history with refund status |
 169 | Store Information | Product Search | Parallel | Customer at store wants to know if item is available | "I'm at your Chicago store—do you have size 10 Nike running shoes?" → Store Information confirms location, Product Search checks inventory |
 170 | Account Management | Order Tracking | Sequential | Customer views order history, wants to track specific order | "I placed an order last week—where is it?" → Order History shows order, Track Order provides shipment details |
 171 
 172 ## Global Out-of-Scope Definition
 173 
 174 **What This Agent Does NOT Handle:**
 175 
 176 1. **Payment Disputes and Chargebacks**
 177    - **User Might Say:** "I'm disputing this charge with my bank"
 178    - **Agent Response:** "For payment disputes, please contact our billing team at billing@shopbot.com or call 1-800-555-0199. They'll work with you to resolve this."
 179 
 180 2. **Legal or Compliance Questions**
 181    - **User Might Say:** "What's your policy on ADA compliance?"
 182    - **Agent Response:** "For legal and compliance inquiries, please email legal@shopbot.com. They can provide detailed policy information."
 183 
 184 3. **Bulk or Wholesale Orders**
 185    - **User Might Say:** "I need 500 units for my business"
 186    - **Agent Response:** "For bulk orders over 100 items, our wholesale team can offer special pricing. Visit shopbot.com/wholesale or call 1-800-555-0177."
 187 
 188 4. **Product Design or Feature Requests**
 189    - **User Might Say:** "You should make this jacket in green"
 190    - **Agent Response:** "I appreciate the feedback! You can submit product suggestions at shopbot.com/feedback, and our design team reviews all submissions quarterly."
 191 
 192 5. **Medical or Safety Advice**
 193    - **User Might Say:** "Is this safe for someone with a peanut allergy?" (if selling food/cosmetics)
 194    - **Agent Response:** "For allergy and safety concerns, please consult the product label and speak with your healthcare provider. I can't provide medical advice."
 195 
 196 ## Topic-Level Instructions
 197 
 198 ### Order Tracking Instructions
 199 ```
 200 Before attempting to track an order, collect the order number or email address used at checkout. If the user provides a tracking number instead, use that directly with Track Order action.
 201 
 202 For delivery address updates, verify the order hasn't already shipped. If tracking shows "Out for Delivery" or "Delivered," inform the user that address changes are no longer possible and suggest contacting the carrier.
 203 
 204 If tracking shows no movement for 3+ business days, acknowledge the delay, provide the tracking number, and escalate to fulfillment team with case number.
 205 ```
 206 
 207 ### Product Search Instructions
 208 ```
 209 When searching for products, start with broad keywords if the user's query is vague (e.g., "shoes" → prompt for category like running, dress, casual). Use filters like size, color, price range, and brand to narrow results.
 210 
 211 If a product is out of stock online but available in stores (per Check Product Availability), proactively offer in-store pickup or notify-when-available options.
 212 
 213 For product comparisons, limit to 3 items maximum. If the user wants to compare more, suggest comparing in batches or directing them to the website comparison tool.
 214 ```
 215 
 216 ### Returns & Exchanges Instructions
 217 ```
 218 Always verify return eligibility BEFORE initiating a return. Check the return window (30 days from delivery), item condition requirements (unworn, tags attached), and restricted categories (final sale, intimate apparel, earrings).
 219 
 220 For exchanges, confirm the desired size/color is in stock before processing. If out of stock, offer return + repurchase with a discount code to match any price changes.
 221 
 222 Return labels are emailed within 5 minutes of initiation. If user doesn't receive it, check spam folder first, then resend via Initiate Return action.
 223 ```
 224 
 225 ### Account Management Instructions
 226 ```
 227 For password updates, direct users to the "Forgot Password" link rather than processing in chat (security best practice).
 228 
 229 When showing order history, default to last 12 months. If the user needs older orders, escalate to customer service with account email.
 230 
 231 Loyalty points expire 12 months from earn date. If a user asks why points decreased, explain expiration policy and show earn/redemption history via View Loyalty Points action.
 232 ```
 233 
 234 ### Store Information Instructions
 235 ```
 236 When providing store hours, always include today's hours first, then general weekly schedule. Flag upcoming holiday closures within the next 7 days.
 237 
 238 For in-store pickup scheduling, confirm the item is available at the selected store BEFORE booking a pickup time. Use Check Product Availability (ACT-005) first, then Schedule In-Store Pickup (ACT-018).
 239 
 240 If a user asks about store-specific services (tailoring, gift wrap, personal shopping), check Store Hours action which includes services. If not listed, provide store phone number for direct inquiry.
 241 ```
 242 
 243 ## Utterance Coverage Plan
 244 
 245 ### Order Tracking Utterances
 246 
 247 **Happy Path:**
 248 - "Where is my order?"
 249 - "Can you track order #12345?"
 250 - "When will my package arrive?"
 251 
 252 **Synonyms/Variants:**
 253 - "What's the status of my shipment?"
 254 - "Has my order shipped yet?"
 255 - "Track my delivery"
 256 
 257 **Edge Cases:**
 258 - "I have 3 orders, which one is coming today?" (multiple orders)
 259 - "My tracking says delivered but I don't have it" (delivery exception)
 260 
 261 ---
 262 
 263 ### Product Search Utterances
 264 
 265 **Happy Path:**
 266 - "Show me blue running shoes"
 267 - "Do you have Nike Air Max in size 10?"
 268 - "I'm looking for a winter jacket"
 269 
 270 **Synonyms/Variants:**
 271 - "Find me sneakers"
 272 - "Search for coats under $100"
 273 - "What dresses do you have in red?"
 274 
 275 **Edge Cases:**
 276 - "I saw this on Instagram but don't know the name" (visual search not supported, need to escalate or ask for more details)
 277 - "Do you have anything like [competitor product]?" (requires comparison knowledge)
 278 
 279 ---
 280 
 281 ### Returns & Exchanges Utterances
 282 
 283 **Happy Path:**
 284 - "I want to return this"
 285 - "How do I send back order #67890?"
 286 - "Can I exchange this for a different size?"
 287 
 288 **Synonyms/Variants:**
 289 - "I need to send this back"
 290 - "Start a return for me"
 291 - "This doesn't fit, can I swap it?"
 292 
 293 **Edge Cases:**
 294 - "I lost my receipt but want to return this" (gift return, no receipt)
 295 - "It's been 35 days, can I still return?" (outside policy window)
 296 
 297 ---
 298 
 299 ### Account Management Utterances
 300 
 301 **Happy Path:**
 302 - "Update my email address"
 303 - "Show me my order history"
 304 - "How many loyalty points do I have?"
 305 
 306 **Synonyms/Variants:**
 307 - "Change my phone number"
 308 - "What did I order last month?"
 309 - "Check my rewards balance"
 310 
 311 **Edge Cases:**
 312 - "I can't log in, reset my password" (authentication issue, redirect to self-service)
 313 - "Delete my account" (GDPR/privacy request, escalate)
 314 
 315 ---
 316 
 317 ### Store Information Utterances
 318 
 319 **Happy Path:**
 320 - "Find stores near me"
 321 - "What time does the downtown location close?"
 322 - "Can I pick up my order today?"
 323 
 324 **Synonyms/Variants:**
 325 - "Store hours"
 326 - "Locations in Chicago"
 327 - "Schedule a BOPIS pickup"
 328 
 329 **Edge Cases:**
 330 - "Is the store open on Christmas?" (holiday hours)
 331 - "Do you have a store in [city without stores]?" (location request outside footprint)
 332 
 333 ---
 334 
 335 ## Topic Architecture Validation
 336 
 337 ### Semantic Distinctness Checklist
 338 - [✓] No two topics have >40% classification description overlap
 339 - [✓] Each topic name clearly indicates its purpose
 340 - [✓] Classification descriptions use user language, not technical jargon
 341 - [✓] Ambiguous utterances have mitigation strategies (keyword detection, two-step flows)
 342 - [✓] Cross-topic interactions are documented
 343 
 344 ### Completeness Checklist
 345 - [✓] All actions from inventory are assigned to a topic
 346 - [✓] Each topic has 2+ actions (no single-action topics)
 347 - [✓] Agent-level out-of-scope is defined (5 categories)
 348 - [✓] Topic-level instructions exist for all topics
 349 - [✓] Utterance coverage plan includes edge cases
 350 
 351 ### Performance Checklist
 352 - [✓] Total topics: 5 (optimal range: 3-7)
 353 - [✓] Topic count justification: Five topics balance specificity with manageability. Combining "Order Tracking" and "Returns" would create confusion (very different intents); splitting "Product Search" into subcategories (apparel, electronics, etc.) would create routing complexity.
 354 - [✓] No topics with >50% overlap in classification descriptions
 355 - [✓] All topics have distinct primary intents
 356 
 357 ## Version Control
 358 
 359 **Version:** 1.0.0
 360 **Last Updated:** 2026-02-07
 361 **Author:** Retail CX Team
 362 **Approved By:** Marcus Thompson, Director of E-Commerce
 363 **Next Review:** 2026-03-07 (30-day post-launch review)
 364 
 365 ## Notes and Assumptions
 366 
 367 **Data Availability Assumptions:**
 368 - Order tracking assumes integration with ShipStation API for real-time carrier data
 369 - Product search assumes Elasticsearch index updated hourly from inventory system
 370 - Loyalty points assume integration with Salesforce Loyalty Management
 371 
 372 **Business Rules:**
 373 - Return window is 30 days from delivery date, not order date
 374 - BOPIS orders must be picked up within 7 days or auto-cancelled
 375 - Loyalty points expire 12 months from earn date per program T&Cs
 376 
 377 **Integration Dependencies:**
 378 - Carrier tracking APIs (FedEx, UPS, USPS) for delivery estimates
 379 - Store inventory API (real-time sync every 15 minutes)
 380 - Payment gateway API for refund status checks
