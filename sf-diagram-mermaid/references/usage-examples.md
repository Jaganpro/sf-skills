<!-- Parent: sf-diagram-mermaid/SKILL.md -->
   1 # sf-diagram Usage Examples
   2 
   3 Real-world examples of using the sf-diagram skill.
   4 
   5 ---
   6 
   7 ## Example 1: OAuth Flow Diagram
   8 
   9 ### Request
  10 ```
  11 "Create a JWT Bearer OAuth flow diagram for our CI/CD pipeline integration"
  12 ```
  13 
  14 ### Generated Output
  15 
  16 #### Mermaid Diagram
  17 ```mermaid
  18 %%{init: {'theme': 'base', 'themeVariables': {
  19   'actorBkg': '#ddd6fe',
  20   'actorTextColor': '#1f2937',
  21   'actorBorder': '#6d28d9',
  22   'signalColor': '#334155',
  23   'signalTextColor': '#1f2937',
  24   'noteBkgColor': '#f8fafc',
  25   'noteTextColor': '#1f2937',
  26   'noteBorderColor': '#334155'
  27 }}}%%
  28 sequenceDiagram
  29     autonumber
  30 
  31     box rgba(221,214,254,0.3) CI/CD PIPELINE
  32         participant GH as 🔧 GitHub Actions
  33         participant K as 🔐 Secrets Manager
  34     end
  35 
  36     box rgba(167,243,208,0.3) SALESFORCE
  37         participant SF as ☁️ Salesforce
  38     end
  39 
  40     Note over GH,SF: JWT Bearer Flow for CI/CD
  41 
  42     GH->>K: 1. Retrieve private key
  43     K->>GH: 2. Return encrypted key
  44 
  45     GH->>GH: 3. Create JWT
  46     Note over GH: iss: consumer_key<br/>sub: deploy@company.com<br/>aud: login.salesforce.com
  47 
  48     GH->>GH: 4. Sign with private key
  49 
  50     GH->>SF: 5. POST /token (JWT assertion)
  51 
  52     SF->>SF: 6. Verify signature
  53     SF->>SF: 7. Validate claims
  54 
  55     SF->>GH: 8. Access token
  56 
  57     GH->>SF: 9. sf deploy start
  58     SF->>GH: 10. Deployment result
  59 ```
  60 
  61 #### ASCII Fallback
  62 ```
  63 ┌───────────────────────┐     ┌────────────────────┐
  64 │   GitHub Actions      │     │     Salesforce     │
  65 │   (Private Key)       │     │   (Certificate)    │
  66 └───────────┬───────────┘     └─────────┬──────────┘
  67             │                           │
  68             │  1. Create JWT            │
  69             │  2. Sign with key         │
  70             │                           │
  71             │  3. POST /token           │
  72             │──────────────────────────>│
  73             │                           │
  74             │  4. Verify signature      │
  75             │  5. Return access_token   │
  76             │<──────────────────────────│
  77             │                           │
  78             │  6. sf deploy start       │
  79             │──────────────────────────>│
  80 ```
  81 
  82 ### Score
  83 ```
  84 Score: 72/80 ⭐⭐⭐⭐⭐ Excellent
  85 ├─ Accuracy: 20/20     ✓ All JWT Bearer steps correct
  86 ├─ Clarity: 18/20      ✓ Clear labels, good flow
  87 ├─ Completeness: 14/15 ✓ Includes CI/CD context
  88 ├─ Styling: 12/15      ✓ Proper theming
  89 └─ Best Practices: 8/10 ✓ Good annotations
  90 ```
  91 
  92 ---
  93 
  94 ## Example 2: Data Model ERD
  95 
  96 ### Request
  97 ```
  98 "Create an ERD for our custom Invoice system with Invoice__c, Invoice_Line_Item__c, and relationships to Account and Product"
  99 ```
 100 
 101 ### Generated Output
 102 
 103 #### Mermaid Diagram
 104 ```mermaid
 105 %%{init: {'theme': 'base', 'themeVariables': {
 106   'primaryColor': '#a5f3fc',
 107   'primaryTextColor': '#1f2937',
 108   'primaryBorderColor': '#0e7490',
 109   'lineColor': '#334155',
 110   'tertiaryColor': '#f8fafc'
 111 }}}%%
 112 erDiagram
 113     Account ||--o{ Invoice__c : "billed to"
 114     Account ||--o{ Contact : "has"
 115     Invoice__c ||--|{ Invoice_Line_Item__c : "contains"
 116     Product2 ||--o{ Invoice_Line_Item__c : "included in"
 117 
 118     Account {
 119         Id Id PK
 120         Text Name "Required"
 121         Text BillingStreet
 122         Text BillingCity
 123         Text BillingState
 124         Text BillingPostalCode
 125     }
 126 
 127     Contact {
 128         Id Id PK
 129         Lookup AccountId FK "Account"
 130         Text FirstName
 131         Text LastName "Required"
 132         Email Email
 133     }
 134 
 135     Invoice__c {
 136         Id Id PK
 137         AutoNumber Name "INV-00001"
 138         MasterDetail Account__c FK "Account"
 139         Lookup Billing_Contact__c FK "Contact"
 140         Date Invoice_Date__c "Required"
 141         Date Due_Date__c "Required"
 142         Picklist Status__c "Draft, Sent, Paid, Overdue"
 143         Currency Total_Amount__c "Roll-Up SUM"
 144         Currency Paid_Amount__c
 145         Formula Amount_Due__c "Total - Paid"
 146         Text External_Id__c UK "Integration Key"
 147     }
 148 
 149     Invoice_Line_Item__c {
 150         Id Id PK
 151         AutoNumber Name "LI-00001"
 152         MasterDetail Invoice__c FK "Invoice__c"
 153         Lookup Product__c FK "Product2"
 154         Number Quantity__c "Required"
 155         Currency Unit_Price__c "Required"
 156         Formula Line_Total__c "Qty × Price"
 157         TextArea Description__c
 158     }
 159 
 160     Product2 {
 161         Id Id PK
 162         Text Name "Required"
 163         Text ProductCode
 164         Currency UnitPrice
 165         Checkbox IsActive
 166     }
 167 ```
 168 
 169 #### ASCII Fallback
 170 ```
 171 ┌─────────────────────────┐       ┌─────────────────────────┐
 172 │        ACCOUNT          │       │        CONTACT          │
 173 ├─────────────────────────┤       ├─────────────────────────┤
 174 │ Id (PK)                 │       │ Id (PK)                 │
 175 │ Name (Required)         │──┐    │ AccountId (FK) ─────────│───┐
 176 │ BillingStreet           │  │    │ FirstName               │   │
 177 │ BillingCity             │  │    │ LastName (Required)     │   │
 178 │ BillingState            │  │    │ Email                   │   │
 179 │ BillingPostalCode       │  │    └─────────────────────────┘   │
 180 └─────────────────────────┘  │                                  │
 181               │               │                                  │
 182               │ 1:N           └──────────────────────────────────┘
 183               ▼
 184 ┌─────────────────────────┐
 185 │      INVOICE__C         │
 186 ├─────────────────────────┤
 187 │ Id (PK)                 │
 188 │ Name (Auto: INV-00001)  │
 189 │ Account__c (MD)         │
 190 │ Billing_Contact__c (LK) │
 191 │ Invoice_Date__c (Req)   │
 192 │ Due_Date__c (Req)       │
 193 │ Status__c (Picklist)    │
 194 │ Total_Amount__c (Roll)  │
 195 │ Amount_Due__c (Formula) │
 196 │ External_Id__c (UK)     │
 197 └─────────────┬───────────┘
 198               │
 199               │ 1:N (Master-Detail)
 200               ▼
 201 ┌─────────────────────────┐       ┌─────────────────────────┐
 202 │  INVOICE_LINE_ITEM__C   │       │       PRODUCT2          │
 203 ├─────────────────────────┤       ├─────────────────────────┤
 204 │ Id (PK)                 │       │ Id (PK)                 │
 205 │ Name (Auto: LI-00001)   │       │ Name (Required)         │
 206 │ Invoice__c (MD) ────────│──┘    │ ProductCode             │
 207 │ Product__c (LK) ────────│──────>│ UnitPrice               │
 208 │ Quantity__c (Req)       │       │ IsActive                │
 209 │ Unit_Price__c (Req)     │       └─────────────────────────┘
 210 │ Line_Total__c (Formula) │
 211 │ Description__c          │
 212 └─────────────────────────┘
 213 ```
 214 
 215 ### Score
 216 ```
 217 Score: 74/80 ⭐⭐⭐⭐⭐ Excellent
 218 ├─ Accuracy: 20/20     ✓ All relationships correct
 219 ├─ Clarity: 19/20      ✓ Clear field annotations
 220 ├─ Completeness: 15/15 ✓ All objects included
 221 ├─ Styling: 13/15      ✓ Good layout
 222 └─ Best Practices: 7/10  ⚠ Could add more field comments
 223 ```
 224 
 225 ---
 226 
 227 ## Example 3: Integration Sequence
 228 
 229 ### Request
 230 ```
 231 "Diagram our real-time Order sync from Salesforce to SAP using Platform Events"
 232 ```
 233 
 234 ### Generated Output
 235 
 236 #### Mermaid Diagram
 237 ```mermaid
 238 %%{init: {'theme': 'base', 'themeVariables': {
 239   'actorBkg': '#ddd6fe',
 240   'actorTextColor': '#1f2937',
 241   'actorBorder': '#6d28d9',
 242   'signalColor': '#334155',
 243   'signalTextColor': '#1f2937',
 244   'noteBkgColor': '#f8fafc',
 245   'noteTextColor': '#1f2937',
 246   'noteBorderColor': '#334155'
 247 }}}%%
 248 sequenceDiagram
 249     autonumber
 250 
 251     box rgba(167,243,208,0.3) SALESFORCE
 252         participant T as 🔄 Order Trigger
 253         participant PE as 📢 Order_Sync__e
 254     end
 255 
 256     box rgba(254,215,170,0.3) INTEGRATION
 257         participant MW as 🔄 MuleSoft
 258     end
 259 
 260     box rgba(165,243,252,0.3) SAP
 261         participant SAP as 🏭 SAP S/4HANA
 262     end
 263 
 264     Note over T,SAP: Real-time Order Sync (Platform Events)
 265 
 266     T->>T: 1. Order record saved
 267     Note over T: Status changed to 'Approved'
 268 
 269     T->>PE: 2. Publish Platform Event
 270     Note over T,PE: EventBus.publish(<br/>  new Order_Sync__e(<br/>    Order_Id__c,<br/>    Action__c='CREATE'<br/>  )<br/>)
 271 
 272     PE-)MW: 3. Event delivered (CometD)
 273     Note over PE,MW: /event/Order_Sync__e
 274 
 275     activate MW
 276 
 277     MW->>MW: 4. Transform to SAP format
 278     Note over MW: Map SF Order → SAP Sales Order
 279 
 280     MW->>SAP: 5. POST /sap/api/salesorders
 281     Note over MW,SAP: IDOC or REST API
 282 
 283     alt Success
 284         SAP->>MW: 6a. 201 Created
 285         Note over SAP,MW: SAP Order #: 4500012345
 286 
 287         MW->>PE: 7a. Publish confirmation
 288         Note over MW,PE: Order_Sync_Status__e<br/>Status='SUCCESS'
 289 
 290     else Validation Error
 291         SAP->>MW: 6b. 400 Bad Request
 292         Note over SAP,MW: Missing required field
 293 
 294         MW->>PE: 7b. Publish error
 295         Note over MW,PE: Order_Sync_Status__e<br/>Status='ERROR'
 296     end
 297 
 298     deactivate MW
 299 
 300     Note over T: Flow updates Order<br/>with SAP reference
 301 ```
 302 
 303 ### Score
 304 ```
 305 Score: 70/80 ⭐⭐⭐⭐ Very Good
 306 ├─ Accuracy: 19/20     ✓ Platform Event pattern correct
 307 ├─ Clarity: 18/20      ✓ Good error handling shown
 308 ├─ Completeness: 13/15 ✓ Main paths covered
 309 ├─ Styling: 12/15      ✓ Good use of boxes
 310 └─ Best Practices: 8/10 ✓ Shows async pattern
 311 ```
 312 
 313 ---
 314 
 315 ## Example 4: Combined Request
 316 
 317 ### Request
 318 ```
 319 "I need to document our partner portal authentication.
 320 Create: 1) The OAuth flow for partner login, 2) The data model showing Partner Account, Portal User, and Opportunities they can see"
 321 ```
 322 
 323 ### Generated Output
 324 
 325 The skill generates two diagrams:
 326 
 327 1. **OAuth Authorization Code + PKCE Flow** (for the portal)
 328 2. **ERD showing Partner Access Model**
 329 
 330 Both with Mermaid and ASCII versions.
 331 
 332 ---
 333 
 334 ## Tips for Best Results
 335 
 336 1. **Be specific** - "JWT Bearer for CI/CD" is better than just "OAuth"
 337 2. **Name your systems** - "Salesforce to SAP" produces clearer diagrams
 338 3. **Mention custom objects** - Include `__c` suffix so we know they're custom
 339 4. **Request both formats** - If you need ASCII fallback, mention it explicitly
