<!-- Parent: sf-diagram-mermaid/SKILL.md -->
   1 # ERD Conventions for sf-diagram
   2 
   3 Standardized conventions for Salesforce data model diagrams with object type indicators, LDV markers, OWD annotations, and relationship type labels.
   4 
   5 ## Object Type Indicators
   6 
   7 | Indicator | Object Type | Color (Flowchart) | Fill | Stroke | API Suffix |
   8 |-----------|-------------|-------------------|------|--------|------------|
   9 | `[STD]` | Standard Object | Sky Blue | `#bae6fd` | `#0369a1` | None |
  10 | `[CUST]` | Custom Object | Orange | `#fed7aa` | `#c2410c` | `__c` |
  11 | `[EXT]` | External Object | Green | `#a7f3d0` | `#047857` | `__x` |
  12 
  13 ### Examples
  14 
  15 ```
  16 Account [STD]         → Standard Salesforce object
  17 Invoice__c [CUST]     → Custom object
  18 SAP_Product__x [EXT]  → External object via Salesforce Connect
  19 ```
  20 
  21 ---
  22 
  23 ## LDV (Large Data Volume) Indicator
  24 
  25 Objects with **>2M records** should display an LDV indicator to highlight potential performance considerations.
  26 
  27 | Record Count | Display Format | Example |
  28 |--------------|----------------|---------|
  29 | < 2,000,000 | (none) | Account |
  30 | 2M - 10M | `LDV[~XM]` | `LDV[~4M]` |
  31 | 10M - 100M | `LDV[~XXM]` | `LDV[~15M]` |
  32 | > 100M | `LDV[~XXXM]` | `LDV[~250M]` |
  33 
  34 ### Query Record Count
  35 
  36 ```bash
  37 sf data query --query "SELECT COUNT() FROM Account" --target-org myorg --json
  38 ```
  39 
  40 ### In Diagram
  41 
  42 **erDiagram format** (in entity description):
  43 ```mermaid
  44 Account {
  45     Id Id PK "[STD] LDV[~4M]"
  46     Text Name "Required"
  47 }
  48 ```
  49 
  50 **Flowchart format** (in node label):
  51 ```mermaid
  52 Account["Account<br/>LDV[~4M]"]
  53 ```
  54 
  55 ---
  56 
  57 ## OWD (Org-Wide Default) Display
  58 
  59 Display sharing model on entities to show default record access levels.
  60 
  61 | OWD Setting | Display | Meaning |
  62 |-------------|---------|---------|
  63 | Private | `OWD:Private` | Owner + role hierarchy only |
  64 | PublicRead | `OWD:Read` | All users can view |
  65 | PublicReadWrite | `OWD:ReadWrite` | All users can view and edit |
  66 | PublicReadWriteTransfer | `OWD:Full` | All users have full access |
  67 | ControlledByParent | `OWD:Parent` | Inherits from master object |
  68 | FullAccess | `OWD:Full` | Full access to all |
  69 
  70 ### Query OWD
  71 
  72 ```bash
  73 sf sobject describe --sobject Account --target-org myorg --json | jq '.result.sharingModel'
  74 ```
  75 
  76 ### Common OWD Patterns
  77 
  78 | Object | Typical OWD | Notes |
  79 |--------|-------------|-------|
  80 | Account | Private | Most orgs restrict account access |
  81 | Contact | ControlledByParent | Usually follows Account OWD |
  82 | Opportunity | Private | Sales data is sensitive |
  83 | Case | Private or Public Read | Depends on support model |
  84 | Lead | Public Read/Write | Often shared across sales |
  85 
  86 ---
  87 
  88 ## Relationship Type Labels
  89 
  90 Distinguish between Lookup and Master-Detail relationships for understanding data dependencies.
  91 
  92 | Label | Relationship | Cascade Delete | Roll-Up | Required Parent |
  93 |-------|--------------|----------------|---------|-----------------|
  94 | `LK` | Lookup | No | No | No |
  95 | `MD` | Master-Detail | Yes | Yes | Yes |
  96 
  97 ### In erDiagram Syntax
  98 
  99 ```mermaid
 100 erDiagram
 101     Account ||--o{ Contact : "LK - has many"
 102     Account ||--o{ Invoice__c : "MD - owns"
 103 ```
 104 
 105 ### In Flowchart Syntax
 106 
 107 | Type | Arrow | Visual |
 108 |------|-------|--------|
 109 | Lookup | `-->` | Single arrow |
 110 | Master-Detail | `==>` | Thick double arrow |
 111 
 112 ```mermaid
 113 flowchart TB
 114     Account -->|"LK"| Contact
 115     Account ==>|"MD"| Invoice
 116 ```
 117 
 118 ---
 119 
 120 ## Cardinality Notation (Crow's Foot)
 121 
 122 Standard ERD cardinality symbols:
 123 
 124 | Symbol | Meaning | Description |
 125 |--------|---------|-------------|
 126 | `\|\|` | Exactly one | One and only one |
 127 | `\|o` | Zero or one | Optional, at most one |
 128 | `o{` | Zero or many | Optional, any number |
 129 | `\|{` | One or many | Required, at least one |
 130 
 131 ### Common Salesforce Patterns
 132 
 133 ```mermaid
 134 erDiagram
 135     %% One Account has many Contacts (optional)
 136     Account ||--o{ Contact : "has many"
 137 
 138     %% One Opportunity has many Line Items (optional)
 139     Opportunity ||--o{ OpportunityLineItem : "contains"
 140 
 141     %% Contact required for OpportunityContactRole
 142     Contact ||--|{ OpportunityContactRole : "plays role"
 143 
 144     %% Self-referential (Account hierarchy)
 145     Account ||--o{ Account : "parent of"
 146 ```
 147 
 148 ---
 149 
 150 ## Entity Metadata Row Pattern
 151 
 152 Add a special metadata row in erDiagram entities to consolidate annotations:
 153 
 154 ```mermaid
 155 erDiagram
 156     Account {
 157         Id Id PK "[STD]"
 158         Text Name "Required"
 159         Lookup ParentId FK "Account (Self)"
 160         Text __metadata__ "LDV[~4M] | OWD:Private"
 161     }
 162 ```
 163 
 164 **Note**: The `__metadata__` row is a convention for displaying object-level info within the erDiagram entity block.
 165 
 166 ---
 167 
 168 ## Color Palette for ERD
 169 
 170 ### Entity Colors (for Flowchart ERD)
 171 
 172 | Object Type | Fill | Stroke | Text |
 173 |-------------|------|--------|------|
 174 | Standard | `#bae6fd` | `#0369a1` | `#1f2937` |
 175 | Custom | `#fed7aa` | `#c2410c` | `#1f2937` |
 176 | External | `#a7f3d0` | `#047857` | `#1f2937` |
 177 
 178 ### Subgraph Colors (for Grouping)
 179 
 180 | Category | Fill | Stroke | Style |
 181 |----------|------|--------|-------|
 182 | Standard Group | `#f0f9ff` | `#0369a1` | dashed |
 183 | Custom Group | `#fff7ed` | `#c2410c` | dashed |
 184 | External Group | `#ecfdf5` | `#047857` | dashed |
 185 | Legend | `#f8fafc` | `#334155` | dashed |
 186 
 187 ### Style Declarations
 188 
 189 ```mermaid
 190 %% Standard Object - Sky Blue
 191 style Account fill:#bae6fd,stroke:#0369a1,color:#1f2937
 192 
 193 %% Custom Object - Orange
 194 style Invoice fill:#fed7aa,stroke:#c2410c,color:#1f2937
 195 
 196 %% External Object - Green
 197 style SAP_Product fill:#a7f3d0,stroke:#047857,color:#1f2937
 198 
 199 %% Subgraph - Standard group
 200 style std fill:#f0f9ff,stroke:#0369a1,stroke-dasharray:5
 201 ```
 202 
 203 ---
 204 
 205 ## Query Commands Reference
 206 
 207 ### Batch Query Script
 208 
 209 Use the provided Python script for efficient metadata queries:
 210 
 211 ```bash
 212 python3 ~/.claude/plugins/marketplaces/sf-skills/sf-diagram-mermaid/scripts/query-org-metadata.py \
 213     --objects Account,Contact,Lead,Opportunity,Case \
 214     --target-org myorg \
 215     --output table
 216 ```
 217 
 218 ### Manual Queries
 219 
 220 **Record Count (LDV)**:
 221 ```bash
 222 sf data query --query "SELECT COUNT() FROM Account" --target-org myorg --json
 223 ```
 224 
 225 **OWD Setting**:
 226 ```bash
 227 sf sobject describe --sobject Account --target-org myorg --json | jq '.result.sharingModel'
 228 ```
 229 
 230 **Object Type Check**:
 231 ```bash
 232 sf sobject describe --sobject Invoice__c --target-org myorg --json | jq '.result.custom'
 233 ```
 234 
 235 ---
 236 
 237 ## Complete Example
 238 
 239 ### Flowchart ERD with All Conventions
 240 
 241 ```mermaid
 242 %%{init: {"flowchart": {"nodeSpacing": 60, "rankSpacing": 50}} }%%
 243 flowchart TB
 244     subgraph legend["LEGEND"]
 245         direction LR
 246         L_STD["Standard [STD]"]
 247         L_CUST["Custom [CUST]"]
 248         L_EXT["External [EXT]"]
 249         L_LK["─── LK (Lookup)"]
 250         L_MD["═══ MD (Master-Detail)"]
 251 
 252         style L_STD fill:#bae6fd,stroke:#0369a1,color:#1f2937
 253         style L_CUST fill:#fed7aa,stroke:#c2410c,color:#1f2937
 254         style L_EXT fill:#a7f3d0,stroke:#047857,color:#1f2937
 255         style L_LK fill:#f8fafc,stroke:#334155,color:#1f2937
 256         style L_MD fill:#f8fafc,stroke:#334155,color:#1f2937
 257     end
 258 
 259     subgraph std["STANDARD OBJECTS"]
 260         Account["Account<br/>LDV[~4M] | OWD:Private"]
 261         Contact["Contact<br/>OWD:Parent"]
 262         Opportunity["Opportunity<br/>LDV[~2M] | OWD:Private"]
 263     end
 264 
 265     subgraph cust["CUSTOM OBJECTS"]
 266         Invoice["Invoice__c<br/>OWD:Private"]
 267         InvoiceLine["Invoice_Line__c"]
 268     end
 269 
 270     subgraph ext["EXTERNAL OBJECTS"]
 271         SAP["SAP_Product__x"]
 272     end
 273 
 274     %% Relationships
 275     Account -->|"LK"| Contact
 276     Account -->|"LK"| Opportunity
 277     Account ==>|"MD"| Invoice
 278     Invoice ==>|"MD"| InvoiceLine
 279     InvoiceLine -->|"LK"| SAP
 280 
 281     %% Standard Objects - Sky Blue
 282     style Account fill:#bae6fd,stroke:#0369a1,color:#1f2937
 283     style Contact fill:#bae6fd,stroke:#0369a1,color:#1f2937
 284     style Opportunity fill:#bae6fd,stroke:#0369a1,color:#1f2937
 285 
 286     %% Custom Objects - Orange
 287     style Invoice fill:#fed7aa,stroke:#c2410c,color:#1f2937
 288     style InvoiceLine fill:#fed7aa,stroke:#c2410c,color:#1f2937
 289 
 290     %% External Objects - Green
 291     style SAP fill:#a7f3d0,stroke:#047857,color:#1f2937
 292 
 293     %% Subgraph styling
 294     style legend fill:#f8fafc,stroke:#334155,stroke-dasharray:5
 295     style std fill:#f0f9ff,stroke:#0369a1,stroke-dasharray:5
 296     style cust fill:#fff7ed,stroke:#c2410c,stroke-dasharray:5
 297     style ext fill:#ecfdf5,stroke:#047857,stroke-dasharray:5
 298 ```
 299 
 300 ---
 301 
 302 ## Best Practices
 303 
 304 1. **Always include a legend** in flowchart diagrams for color/arrow meaning
 305 2. **Query live org data** for accurate LDV and OWD values
 306 3. **Use consistent naming** - API names, not labels
 307 4. **Group related objects** using subgraphs
 308 5. **Limit fields shown** to key relationships (5-10 per entity max)
 309 6. **Show relationship direction** - parent on left, child on right
 310 7. **Mark required relationships** with appropriate cardinality
 311 
 312 ---
 313 
 314 ## References
 315 
 316 - [Salesforce Data Model Notation](https://developer.salesforce.com/docs/platform/data-models/guide/salesforce-data-model-notation.html)
 317 - [Mermaid ERD Syntax](https://mermaid.js.org/syntax/entityRelationshipDiagram.html)
 318 - [Mermaid Flowchart Syntax](https://mermaid.js.org/syntax/flowchart.html)
 319 - [sf-diagram Color Palette](color-palette.md)
