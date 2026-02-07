# Topic Architecture Worksheet

## Agent Overview

**Agent Name:** ShopBot
**Agent Purpose:** Assist online retail customers with order tracking, product search, returns, account management, and store information
**Primary Channel:** Web Chat, Mobile App
**Deployment Scope:** External (consumer-facing)

## Action Inventory

| Action ID | Action Name | Type | Backend | Description |
|-----------|-------------|------|---------|-------------|
| ACT-001 | Track Order | Flow | OrderTrackingFlow | Retrieves real-time shipment status by order number |
| ACT-002 | Update Delivery Address | Flow | UpdateShippingFlow | Modifies delivery address for in-transit orders |
| ACT-003 | Estimate Delivery Date | Apex | DeliveryEstimator | Calculates estimated delivery based on ZIP and carrier |
| ACT-004 | Search Products | Flow | ProductSearchFlow | Searches catalog by keyword, category, or SKU |
| ACT-005 | Check Product Availability | Apex | InventoryChecker | Verifies in-stock status by store or warehouse |
| ACT-006 | Get Product Recommendations | Apex | RecommendationEngine | Suggests products based on browsing/purchase history |
| ACT-007 | Compare Products | Flow | ProductComparisonFlow | Side-by-side comparison of up to 3 products |
| ACT-008 | Initiate Return | Flow | ReturnInitiationFlow | Starts return process and generates return label |
| ACT-009 | Check Return Eligibility | Apex | ReturnEligibilityChecker | Validates if item is within return window |
| ACT-010 | Process Exchange | Flow | ExchangeFlow | Swaps item for different size/color |
| ACT-011 | Track Return Status | Flow | ReturnTrackingFlow | Shows status of initiated return |
| ACT-012 | Update Account Info | Flow | AccountUpdateFlow | Changes email, phone, password |
| ACT-013 | View Order History | Flow | OrderHistoryFlow | Displays past 12 months of orders |
| ACT-014 | Manage Payment Methods | Flow | PaymentManagementFlow | Adds/removes credit cards, PayPal |
| ACT-015 | View Loyalty Points | Flow | LoyaltyPointsFlow | Shows points balance and redemption options |
| ACT-016 | Find Store Locations | Flow | StoreLocatorFlow | Finds nearest stores by ZIP or city |
| ACT-017 | Check Store Hours | Knowledge | StoreInfoKB | Retrieves hours, holiday closures, services |
| ACT-018 | Schedule In-Store Pickup | Flow | PickupSchedulingFlow | Books time slot for BOPIS orders |
| ACT-019 | Apply Promo Code | Flow | PromoCodeFlow | Validates and applies discount codes to cart |
| ACT-020 | Size Guide Lookup | Knowledge | SizeGuideKB | Provides sizing charts by brand/category |

**Total Actions:** 20

## Topic Groupings

### Topic 1: Order Tracking

**Classification Description:**
```
Questions about finding orders, checking delivery status, tracking shipments, updating delivery addresses, or estimating when packages will arrive.
```

**Actions Assigned:**
- Track Order (ACT-001)
- Update Delivery Address (ACT-002)
- Estimate Delivery Date (ACT-003)

**Scope Definition:**
This topic handles all inquiries related to orders that have been placed and are in fulfillment or transit. Covers tracking numbers, delivery updates, carrier information, and address changes for in-transit packages.

**Out-of-Scope (within this topic):**
- Order cancellations (must escalate to customer service if order hasn't shipped)
- Returns or refunds (handled by Returns & Exchanges topic)
- Pre-purchase delivery estimates (handled by Product Search topic)

---

### Topic 2: Product Search

**Classification Description:**
```
Finding products, checking what's in stock, getting recommendations, comparing items, looking up sizes, or asking about product features and availability.
```

**Actions Assigned:**
- Search Products (ACT-004)
- Check Product Availability (ACT-005)
- Get Product Recommendations (ACT-006)
- Compare Products (ACT-007)
- Size Guide Lookup (ACT-020)

**Scope Definition:**
Helps customers discover and evaluate products. Includes keyword search, category browsing, inventory checks, personalized recommendations, feature comparisons, and sizing information.

**Out-of-Scope (within this topic):**
- Adding items to cart or completing purchase (direct users to website/app)
- Price negotiations or bulk discounts (escalate to sales team)
- Custom or special orders (escalate to customer service)

---

### Topic 3: Returns & Exchanges

**Classification Description:**
```
Starting a return, checking if something can be returned, exchanging items for different sizes or colors, tracking return status, or asking about refund timelines.
```

**Actions Assigned:**
- Initiate Return (ACT-008)
- Check Return Eligibility (ACT-009)
- Process Exchange (ACT-010)
- Track Return Status (ACT-011)

**Scope Definition:**
Manages the complete returns and exchange lifecycle, from eligibility verification through return label generation and refund tracking. Covers standard 30-day return policy and exchanges for size/color.

**Out-of-Scope (within this topic):**
- Returns outside 30-day window (escalate for exception review)
- Damaged or defective items (escalate to quality team)
- Gift returns without receipt (escalate to customer service)

---

### Topic 4: Account Management

**Classification Description:**
```
Updating account information like email or password, viewing past orders, managing saved payment methods, or checking loyalty points and rewards.
```

**Actions Assigned:**
- Update Account Info (ACT-012)
- View Order History (ACT-013)
- Manage Payment Methods (ACT-014)
- View Loyalty Points (ACT-015)

**Scope Definition:**
Self-service account management for registered customers. Includes profile updates, order history access, payment method management, and loyalty program information.

**Out-of-Scope (within this topic):**
- Account deletion or data export requests (escalate to privacy team)
- Forgotten passwords (direct to password reset flow)
- Loyalty program enrollment changes (escalate to loyalty team)

---

### Topic 5: Store Information

**Classification Description:**
```
Finding physical store locations, checking store hours, scheduling in-store pickup, or asking about services available at specific stores.
```

**Actions Assigned:**
- Find Store Locations (ACT-016)
- Check Store Hours (ACT-017)
- Schedule In-Store Pickup (ACT-018)

**Scope Definition:**
Information about physical retail locations, including addresses, hours, special services (alterations, gift wrapping), and buy-online-pickup-in-store (BOPIS) scheduling.

**Out-of-Scope (within this topic):**
- Product availability at specific stores (use Product Search topic's inventory check)
- Event hosting or private shopping appointments (escalate to store manager)
- Career/employment inquiries (direct to careers website)

---

## Topic Distinctness Matrix

| Topic Pair | Semantic Overlap | Confusable Utterances | Mitigation |
|------------|------------------|----------------------|------------|
| Order Tracking ↔ Returns & Exchanges | Medium | "Where is my return?" | Keyword detection: "return" triggers Returns topic even if phrased as tracking |
| Product Search ↔ Store Information | Low | "Do you have this in stock at the downtown store?" | Two-step flow: Product Search checks inventory, then Store Information provides address/hours |
| Account Management ↔ Order Tracking | Medium | "I need to see my orders" | Context matters: if user wants to track a specific order → Order Tracking; if browsing history → Account Management |
| Returns & Exchanges ↔ Account Management | Low | "Can I see my return history?" | Return history is part of Order History (Account Management), but active returns → Returns & Exchanges topic |

## Cross-Topic Interaction Matrix

| From Topic | To Topic | Interaction Type | Trigger | Example |
|------------|----------|------------------|---------|---------|
| Order Tracking | Returns & Exchanges | Sequential | Order received but customer wants to return | "My package arrived but the color is wrong" → Start in Order Tracking, transition to Initiate Return |
| Product Search | Store Information | Conditional | Customer wants to buy in-store | "I found the shoes I want—can I pick them up today?" → Product Search finds item, Store Information schedules pickup |
| Returns & Exchanges | Account Management | Sequential | Return processed, customer wants refund confirmation | "My return was received—where's my refund?" → Return tracking shows received, Account Management shows order history with refund status |
| Store Information | Product Search | Parallel | Customer at store wants to know if item is available | "I'm at your Chicago store—do you have size 10 Nike running shoes?" → Store Information confirms location, Product Search checks inventory |
| Account Management | Order Tracking | Sequential | Customer views order history, wants to track specific order | "I placed an order last week—where is it?" → Order History shows order, Track Order provides shipment details |

## Global Out-of-Scope Definition

**What This Agent Does NOT Handle:**

1. **Payment Disputes and Chargebacks**
   - **User Might Say:** "I'm disputing this charge with my bank"
   - **Agent Response:** "For payment disputes, please contact our billing team at billing@shopbot.com or call 1-800-555-0199. They'll work with you to resolve this."

2. **Legal or Compliance Questions**
   - **User Might Say:** "What's your policy on ADA compliance?"
   - **Agent Response:** "For legal and compliance inquiries, please email legal@shopbot.com. They can provide detailed policy information."

3. **Bulk or Wholesale Orders**
   - **User Might Say:** "I need 500 units for my business"
   - **Agent Response:** "For bulk orders over 100 items, our wholesale team can offer special pricing. Visit shopbot.com/wholesale or call 1-800-555-0177."

4. **Product Design or Feature Requests**
   - **User Might Say:** "You should make this jacket in green"
   - **Agent Response:** "I appreciate the feedback! You can submit product suggestions at shopbot.com/feedback, and our design team reviews all submissions quarterly."

5. **Medical or Safety Advice**
   - **User Might Say:** "Is this safe for someone with a peanut allergy?" (if selling food/cosmetics)
   - **Agent Response:** "For allergy and safety concerns, please consult the product label and speak with your healthcare provider. I can't provide medical advice."

## Topic-Level Instructions

### Order Tracking Instructions
```
Before attempting to track an order, collect the order number or email address used at checkout. If the user provides a tracking number instead, use that directly with Track Order action.

For delivery address updates, verify the order hasn't already shipped. If tracking shows "Out for Delivery" or "Delivered," inform the user that address changes are no longer possible and suggest contacting the carrier.

If tracking shows no movement for 3+ business days, acknowledge the delay, provide the tracking number, and escalate to fulfillment team with case number.
```

### Product Search Instructions
```
When searching for products, start with broad keywords if the user's query is vague (e.g., "shoes" → prompt for category like running, dress, casual). Use filters like size, color, price range, and brand to narrow results.

If a product is out of stock online but available in stores (per Check Product Availability), proactively offer in-store pickup or notify-when-available options.

For product comparisons, limit to 3 items maximum. If the user wants to compare more, suggest comparing in batches or directing them to the website comparison tool.
```

### Returns & Exchanges Instructions
```
Always verify return eligibility BEFORE initiating a return. Check the return window (30 days from delivery), item condition requirements (unworn, tags attached), and restricted categories (final sale, intimate apparel, earrings).

For exchanges, confirm the desired size/color is in stock before processing. If out of stock, offer return + repurchase with a discount code to match any price changes.

Return labels are emailed within 5 minutes of initiation. If user doesn't receive it, check spam folder first, then resend via Initiate Return action.
```

### Account Management Instructions
```
For password updates, direct users to the "Forgot Password" link rather than processing in chat (security best practice).

When showing order history, default to last 12 months. If the user needs older orders, escalate to customer service with account email.

Loyalty points expire 12 months from earn date. If a user asks why points decreased, explain expiration policy and show earn/redemption history via View Loyalty Points action.
```

### Store Information Instructions
```
When providing store hours, always include today's hours first, then general weekly schedule. Flag upcoming holiday closures within the next 7 days.

For in-store pickup scheduling, confirm the item is available at the selected store BEFORE booking a pickup time. Use Check Product Availability (ACT-005) first, then Schedule In-Store Pickup (ACT-018).

If a user asks about store-specific services (tailoring, gift wrap, personal shopping), check Store Hours action which includes services. If not listed, provide store phone number for direct inquiry.
```

## Utterance Coverage Plan

### Order Tracking Utterances

**Happy Path:**
- "Where is my order?"
- "Can you track order #12345?"
- "When will my package arrive?"

**Synonyms/Variants:**
- "What's the status of my shipment?"
- "Has my order shipped yet?"
- "Track my delivery"

**Edge Cases:**
- "I have 3 orders, which one is coming today?" (multiple orders)
- "My tracking says delivered but I don't have it" (delivery exception)

---

### Product Search Utterances

**Happy Path:**
- "Show me blue running shoes"
- "Do you have Nike Air Max in size 10?"
- "I'm looking for a winter jacket"

**Synonyms/Variants:**
- "Find me sneakers"
- "Search for coats under $100"
- "What dresses do you have in red?"

**Edge Cases:**
- "I saw this on Instagram but don't know the name" (visual search not supported, need to escalate or ask for more details)
- "Do you have anything like [competitor product]?" (requires comparison knowledge)

---

### Returns & Exchanges Utterances

**Happy Path:**
- "I want to return this"
- "How do I send back order #67890?"
- "Can I exchange this for a different size?"

**Synonyms/Variants:**
- "I need to send this back"
- "Start a return for me"
- "This doesn't fit, can I swap it?"

**Edge Cases:**
- "I lost my receipt but want to return this" (gift return, no receipt)
- "It's been 35 days, can I still return?" (outside policy window)

---

### Account Management Utterances

**Happy Path:**
- "Update my email address"
- "Show me my order history"
- "How many loyalty points do I have?"

**Synonyms/Variants:**
- "Change my phone number"
- "What did I order last month?"
- "Check my rewards balance"

**Edge Cases:**
- "I can't log in, reset my password" (authentication issue, redirect to self-service)
- "Delete my account" (GDPR/privacy request, escalate)

---

### Store Information Utterances

**Happy Path:**
- "Find stores near me"
- "What time does the downtown location close?"
- "Can I pick up my order today?"

**Synonyms/Variants:**
- "Store hours"
- "Locations in Chicago"
- "Schedule a BOPIS pickup"

**Edge Cases:**
- "Is the store open on Christmas?" (holiday hours)
- "Do you have a store in [city without stores]?" (location request outside footprint)

---

## Topic Architecture Validation

### Semantic Distinctness Checklist
- [✓] No two topics have >40% classification description overlap
- [✓] Each topic name clearly indicates its purpose
- [✓] Classification descriptions use user language, not technical jargon
- [✓] Ambiguous utterances have mitigation strategies (keyword detection, two-step flows)
- [✓] Cross-topic interactions are documented

### Completeness Checklist
- [✓] All actions from inventory are assigned to a topic
- [✓] Each topic has 2+ actions (no single-action topics)
- [✓] Agent-level out-of-scope is defined (5 categories)
- [✓] Topic-level instructions exist for all topics
- [✓] Utterance coverage plan includes edge cases

### Performance Checklist
- [✓] Total topics: 5 (optimal range: 3-7)
- [✓] Topic count justification: Five topics balance specificity with manageability. Combining "Order Tracking" and "Returns" would create confusion (very different intents); splitting "Product Search" into subcategories (apparel, electronics, etc.) would create routing complexity.
- [✓] No topics with >50% overlap in classification descriptions
- [✓] All topics have distinct primary intents

## Version Control

**Version:** 1.0.0
**Last Updated:** 2026-02-07
**Author:** Retail CX Team
**Approved By:** Marcus Thompson, Director of E-Commerce
**Next Review:** 2026-03-07 (30-day post-launch review)

## Notes and Assumptions

**Data Availability Assumptions:**
- Order tracking assumes integration with ShipStation API for real-time carrier data
- Product search assumes Elasticsearch index updated hourly from inventory system
- Loyalty points assume integration with Salesforce Loyalty Management

**Business Rules:**
- Return window is 30 days from delivery date, not order date
- BOPIS orders must be picked up within 7 days or auto-cancelled
- Loyalty points expire 12 months from earn date per program T&Cs

**Integration Dependencies:**
- Carrier tracking APIs (FedEx, UPS, USPS) for delivery estimates
- Store inventory API (real-time sync every 15 minutes)
- Payment gateway API for refund status checks
