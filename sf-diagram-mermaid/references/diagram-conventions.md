<!-- Parent: sf-diagram-mermaid/SKILL.md -->
   1 # Diagram Conventions
   2 
   3 Consistency guidelines for all sf-diagram generated diagrams.
   4 
   5 ## General Principles
   6 
   7 1. **Clarity over completeness** - Show key elements, not every detail
   8 2. **Consistent naming** - Use API names for Salesforce objects/fields
   9 3. **Accessibility first** - Colors supplement, not replace, meaning
  10 4. **Dual output** - Always provide Mermaid + ASCII fallback
  11 
  12 ---
  13 
  14 ## Sequence Diagram Conventions
  15 
  16 ### Actor Naming
  17 
  18 | System | Display Name | Icon |
  19 |--------|--------------|------|
  20 | End User | User | 👤 |
  21 | Web Browser | Browser | 🌐 |
  22 | Mobile App | Mobile App | 📱 |
  23 | Backend Server | App Server | 🖥️ |
  24 | Salesforce Auth | Salesforce<br/>Authorization Server | ☁️ |
  25 | Salesforce API | Salesforce<br/>REST API | 📊 |
  26 | External API | [System Name]<br/>API | 🏭 |
  27 | Middleware | [Name]<br/>(MuleSoft, etc.) | 🔄 |
  28 | Database | Database / Data Lake | 💾 |
  29 
  30 ### Arrow Usage
  31 
  32 | Scenario | Arrow | Example |
  33 |----------|-------|---------|
  34 | HTTP Request | `->>` | `Client->>Server: GET /api` |
  35 | HTTP Response | `-->>` | `Server-->>Client: 200 OK` |
  36 | Async (fire-forget) | `-)` | `Trigger-)Queue: Enqueue job` |
  37 | Internal call | `->` | `Service->Service: Process` |
  38 | Failed/Error | `-x` | `Client-x Server: 500 Error` |
  39 
  40 ### Standard Sections
  41 
  42 1. **Title Note** - First element, describes the flow
  43 2. **Actor Boxes** - Group related actors
  44 3. **Numbered Steps** - Use `autonumber`
  45 4. **Notes** - Add context for complex steps
  46 5. **Alt/Else** - Show branching (success/error)
  47 
  48 ### Example Structure
  49 
  50 ```
  51 %%{init: {...}}%%
  52 sequenceDiagram
  53     autonumber
  54 
  55     %% Actor groups
  56     box rgb(...) [Group Name]
  57         participant ...
  58     end
  59 
  60     %% Title
  61     Note over ...: [Flow Name]
  62 
  63     %% Main flow
  64     A->>B: Step description
  65     Note over A,B: Technical details
  66 
  67     %% Branching
  68     alt Success
  69         ...
  70     else Error
  71         ...
  72     end
  73 ```
  74 
  75 ---
  76 
  77 ## ERD Conventions
  78 
  79 ### Object Naming
  80 
  81 - Use **API Names** (e.g., `Account`, `Custom_Object__c`)
  82 - Use **CamelCase** for standard objects
  83 - Include `__c` suffix for custom objects
  84 
  85 ### Field Representation
  86 
  87 ```
  88 OBJECT {
  89     Type FieldName Annotation "Comment"
  90 }
  91 ```
  92 
  93 **Type Mapping:**
  94 
  95 | Salesforce Type | ERD Type |
  96 |-----------------|----------|
  97 | Id | Id |
  98 | Text, String | Text |
  99 | Number, Integer | Number |
 100 | Decimal, Double | Decimal |
 101 | Currency | Currency |
 102 | Percent | Percent |
 103 | Checkbox | Checkbox |
 104 | Date | Date |
 105 | DateTime | DateTime |
 106 | Picklist | Picklist |
 107 | Multi-Select Picklist | MultiPicklist |
 108 | Lookup | Lookup |
 109 | Master-Detail | MasterDetail |
 110 | Formula | Formula |
 111 | Roll-Up Summary | RollUp |
 112 | Email | Email |
 113 | Phone | Phone |
 114 | URL | URL |
 115 | Auto Number | AutoNumber |
 116 
 117 **Annotations:**
 118 
 119 | Annotation | Meaning |
 120 |------------|---------|
 121 | PK | Primary Key (Id field) |
 122 | FK | Foreign Key (Lookup/Master-Detail) |
 123 | UK | Unique Key (External ID) |
 124 
 125 **Comments:**
 126 
 127 - `"Required"` for non-nullable fields
 128 - `"FK → Object"` to indicate relationship target
 129 - `"Roll-Up: SUM(Amount)"` for roll-up formulas
 130 
 131 ### Relationship Lines
 132 
 133 | Relationship | Line | Salesforce Equivalent |
 134 |--------------|------|----------------------|
 135 | One-to-Many | `\|\|--o{` | Parent Lookup |
 136 | Many-to-Many | `}o--o{` | Junction Object |
 137 | One-to-One | `\|\|--\|\|` | Rare, use Lookup |
 138 | Master-Detail | `\|\|--\|{` | MD (cascade delete) |
 139 
 140 ### Layout Guidelines
 141 
 142 1. **Primary objects at top** - Account, Lead at top
 143 2. **Related objects below** - Contact under Account
 144 3. **Junction objects between** - Show many-to-many clearly
 145 4. **Limit fields shown** - Key fields only (5-10 per object)
 146 
 147 ---
 148 
 149 ## Flowchart Conventions
 150 
 151 ### Direction
 152 
 153 | Use Case | Direction |
 154 |----------|-----------|
 155 | Process flow | `TB` (Top to Bottom) |
 156 | System integration | `LR` (Left to Right) |
 157 | Hierarchy | `TB` |
 158 | Timeline | `LR` |
 159 
 160 ### Node Shapes
 161 
 162 | Concept | Shape | Syntax |
 163 |---------|-------|--------|
 164 | Start/End | Stadium | `([Start])` |
 165 | Process/Action | Rectangle | `[Process]` |
 166 | Decision | Diamond | `{Decision?}` |
 167 | Database | Cylinder | `[(Database)]` |
 168 | External System | Parallelogram | `[/External/]` |
 169 | Subprocess | Double Rectangle | `[[Subprocess]]` |
 170 
 171 ### Subgraph Usage
 172 
 173 Group related components:
 174 
 175 ```mermaid
 176 %%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
 177 flowchart LR
 178     subgraph sf["☁️ SALESFORCE"]
 179         A[Flow]
 180         B[Apex]
 181     end
 182 
 183     subgraph ext["🏭 EXTERNAL"]
 184         C[API]
 185     end
 186 
 187     style sf fill:#ecfeff,stroke:#0e7490,stroke-dasharray:5
 188     style ext fill:#ecfdf5,stroke:#047857,stroke-dasharray:5
 189     style A fill:#c7d2fe,stroke:#4338ca,color:#1f2937
 190     style B fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
 191     style C fill:#a7f3d0,stroke:#047857,color:#1f2937
 192 ```
 193 
 194 ---
 195 
 196 ## ASCII Diagram Conventions
 197 
 198 ### Box Drawing Characters
 199 
 200 ```
 201 Standard Box:
 202 ┌─────────────────┐
 203 │                 │
 204 └─────────────────┘
 205 
 206 Rounded corners (optional):
 207 ╭─────────────────╮
 208 │                 │
 209 ╰─────────────────╯
 210 ```
 211 
 212 ### Line Characters
 213 
 214 | Character | Unicode | Usage |
 215 |-----------|---------|-------|
 216 | `─` | U+2500 | Horizontal line |
 217 | `│` | U+2502 | Vertical line |
 218 | `┌` | U+250C | Top-left corner |
 219 | `┐` | U+2510 | Top-right corner |
 220 | `└` | U+2514 | Bottom-left corner |
 221 | `┘` | U+2518 | Bottom-right corner |
 222 | `├` | U+251C | Left T-junction |
 223 | `┤` | U+2524 | Right T-junction |
 224 | `┬` | U+252C | Top T-junction |
 225 | `┴` | U+2534 | Bottom T-junction |
 226 | `┼` | U+253C | Cross junction |
 227 
 228 ### Arrow Characters
 229 
 230 ```
 231 Right:  ───>  or  ──▶  or  ────────────────>
 232 Left:   <───  or  ◀──
 233 Up:     ▲
 234 Down:   ▼
 235 Bidirectional: <──>
 236 ```
 237 
 238 ### Width Guidelines
 239 
 240 - **Max width**: 80 characters (terminal friendly)
 241 - **Box width**: Consistent within diagram
 242 - **Label padding**: At least 1 space inside boxes
 243 
 244 ### Example ASCII Sequence
 245 
 246 ```
 247 ┌──────────┐     ┌───────────────┐     ┌────────────────┐
 248 │  Client  │     │    Server     │     │    Database    │
 249 └────┬─────┘     └───────┬───────┘     └───────┬────────┘
 250      │                   │                     │
 251      │  1. Request       │                     │
 252      │──────────────────>│                     │
 253      │                   │                     │
 254      │                   │  2. Query           │
 255      │                   │────────────────────>│
 256      │                   │                     │
 257      │                   │  3. Results         │
 258      │                   │<────────────────────│
 259      │                   │                     │
 260      │  4. Response      │                     │
 261      │<──────────────────│                     │
 262 ```
 263 
 264 ---
 265 
 266 ## Scoring Criteria
 267 
 268 ### Accuracy (20 points)
 269 - Correct actors/entities
 270 - Accurate flow sequence
 271 - Proper relationships (ERD)
 272 - Valid syntax
 273 
 274 ### Clarity (20 points)
 275 - Readable labels
 276 - Logical layout
 277 - Appropriate detail level
 278 - Good spacing
 279 
 280 ### Completeness (15 points)
 281 - All key steps included
 282 - Error paths shown (where applicable)
 283 - Annotations for context
 284 - Legend if needed
 285 
 286 ### Styling (15 points)
 287 - Consistent colors
 288 - Proper theming
 289 - Icons where helpful
 290 - Professional appearance
 291 
 292 ### Best Practices (10 points)
 293 - UML/notation conventions
 294 - Accessibility considerations
 295 - Dual format output
 296 - Documentation
 297 
 298 ---
 299 
 300 ## Validation Checklist
 301 
 302 Before delivering a diagram:
 303 
 304 - [ ] Mermaid syntax is valid (renders without errors)
 305 - [ ] ASCII fallback is provided
 306 - [ ] Colors follow palette
 307 - [ ] Icons supplement colors
 308 - [ ] Labels are clear and consistent
 309 - [ ] Appropriate detail level
 310 - [ ] Flow/relationships are accurate
 311 - [ ] Key points documented
 312 - [ ] Score calculated and shown
