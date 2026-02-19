<!-- Parent: sf-diagram-mermaid/SKILL.md -->
   1 # Mermaid Quick Reference
   2 
   3 Quick reference guide for Mermaid diagram syntax used in sf-diagram.
   4 
   5 ## Sequence Diagrams
   6 
   7 ### Basic Syntax
   8 
   9 ```mermaid
  10 sequenceDiagram
  11     participant A as Alice
  12     participant B as Bob
  13 
  14     A->>B: Hello Bob
  15     B-->>A: Hi Alice
  16 ```
  17 
  18 ### Arrow Types
  19 
  20 | Arrow | Meaning | Usage |
  21 |-------|---------|-------|
  22 | `->` | Solid line, no head | Internal processing |
  23 | `-->` | Dotted line, no head | Optional/weak connection |
  24 | `->>` | Solid line, arrowhead | Request/Call |
  25 | `-->>` | Dotted line, arrowhead | Response/Return |
  26 | `-x` | Solid line, X end | Failed/Cancelled |
  27 | `--x` | Dotted line, X end | Failed response |
  28 | `-)` | Solid, open arrow | Async (fire-and-forget) |
  29 | `--)` | Dotted, open arrow | Async response |
  30 
  31 ### Participants and Actors
  32 
  33 ```mermaid
  34 sequenceDiagram
  35     %% Rectangle participant
  36     participant A as Application
  37 
  38     %% Actor (stick figure)
  39     actor U as User
  40 
  41     %% With emoji
  42     participant SF as ☁️ Salesforce
  43 ```
  44 
  45 ### Grouping with Boxes
  46 
  47 ```mermaid
  48 sequenceDiagram
  49     box Blue Client Side
  50         participant B as Browser
  51         participant A as App
  52     end
  53 
  54     box Orange Server Side
  55         participant SF as Salesforce
  56     end
  57 
  58     B->>A: Request
  59     A->>SF: API Call
  60 ```
  61 
  62 ### Activation (Lifelines)
  63 
  64 ```mermaid
  65 sequenceDiagram
  66     participant A as Client
  67     participant B as Server
  68 
  69     A->>+B: Request
  70     Note right of B: Processing...
  71     B-->>-A: Response
  72 ```
  73 
  74 Shorthand: `+` activates, `-` deactivates
  75 
  76 ### Loops and Conditionals
  77 
  78 ```mermaid
  79 sequenceDiagram
  80     participant C as Client
  81     participant S as Server
  82 
  83     loop Every 5 seconds
  84         C->>S: Poll for status
  85         S-->>C: Status response
  86     end
  87 ```
  88 
  89 ```mermaid
  90 sequenceDiagram
  91     participant C as Client
  92     participant S as Server
  93 
  94     C->>S: Request
  95 
  96     alt Success
  97         S-->>C: 200 OK
  98     else Client Error
  99         S-->>C: 400 Bad Request
 100     else Server Error
 101         S-->>C: 500 Error
 102     end
 103 ```
 104 
 105 ### Notes
 106 
 107 ```mermaid
 108 sequenceDiagram
 109     participant A as Client
 110     participant B as Server
 111 
 112     Note left of A: Client prepares request
 113     Note right of B: Server processes
 114     Note over A,B: This spans both participants
 115 
 116     A->>B: Request
 117 ```
 118 
 119 ### Autonumber
 120 
 121 ```mermaid
 122 sequenceDiagram
 123     autonumber
 124     participant A as Client
 125     participant B as Server
 126 
 127     A->>B: First (1)
 128     B-->>A: Second (2)
 129     A->>B: Third (3)
 130 ```
 131 
 132 ### Breaks and Critical Sections
 133 
 134 ```mermaid
 135 sequenceDiagram
 136     participant A
 137     participant B
 138 
 139     critical Establish connection
 140         A->>B: Connect
 141         B-->>A: Connected
 142     option Connection failed
 143         A->>A: Log error
 144     end
 145 
 146     break When rate limited
 147         A->>A: Wait 60 seconds
 148     end
 149 ```
 150 
 151 ---
 152 
 153 ## Entity Relationship Diagrams
 154 
 155 ### Basic Syntax
 156 
 157 ```mermaid
 158 erDiagram
 159     CUSTOMER ||--o{ ORDER : places
 160     ORDER ||--|{ LINE_ITEM : contains
 161 ```
 162 
 163 ### Cardinality Notation
 164 
 165 | Symbol | Meaning |
 166 |--------|---------|
 167 | `\|o` | Zero or one |
 168 | `\|\|` | Exactly one |
 169 | `}o` | Zero or many |
 170 | `}\|` | One or many |
 171 
 172 ### Full Cardinality Examples
 173 
 174 ```mermaid
 175 erDiagram
 176     A ||--|| B : "one-to-one"
 177     C ||--o{ D : "one-to-many"
 178     E }o--o{ F : "many-to-many"
 179     G |o--o| H : "zero-or-one to zero-or-one"
 180 ```
 181 
 182 ### Entity Attributes
 183 
 184 ```mermaid
 185 erDiagram
 186     ACCOUNT {
 187         Id Id PK "Primary Key"
 188         Text Name "Required field"
 189         Lookup OwnerId FK "Foreign Key"
 190         Currency AnnualRevenue
 191         Checkbox IsActive
 192     }
 193 ```
 194 
 195 ### Attribute Keys
 196 
 197 | Key | Meaning |
 198 |-----|---------|
 199 | PK | Primary Key |
 200 | FK | Foreign Key |
 201 | UK | Unique Key |
 202 
 203 ---
 204 
 205 ## Flowcharts
 206 
 207 ### Basic Syntax
 208 
 209 ```mermaid
 210 %%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
 211 flowchart LR
 212     A[Start] --> B{Decision}
 213     B -->|Yes| C[Action 1]
 214     B -->|No| D[Action 2]
 215     C --> E[End]
 216     D --> E
 217 
 218     style A fill:#a7f3d0,stroke:#047857,color:#1f2937
 219     style B fill:#fde68a,stroke:#b45309,color:#1f2937
 220     style C fill:#c7d2fe,stroke:#4338ca,color:#1f2937
 221     style D fill:#c7d2fe,stroke:#4338ca,color:#1f2937
 222     style E fill:#a7f3d0,stroke:#047857,color:#1f2937
 223 ```
 224 
 225 ### Direction
 226 
 227 | Code | Direction |
 228 |------|-----------|
 229 | `TB` / `TD` | Top to Bottom |
 230 | `BT` | Bottom to Top |
 231 | `LR` | Left to Right |
 232 | `RL` | Right to Left |
 233 
 234 ### Node Shapes
 235 
 236 ```mermaid
 237 flowchart LR
 238     A[Rectangle]
 239     B(Rounded)
 240     C([Stadium])
 241     D[[Subroutine]]
 242     E[(Database)]
 243     F((Circle))
 244     G>Asymmetric]
 245     H{Diamond}
 246     I{{Hexagon}}
 247     J[/Parallelogram/]
 248     K[\Parallelogram alt\]
 249     L[/Trapezoid\]
 250     M[\Trapezoid alt/]
 251 ```
 252 
 253 ### Link Types
 254 
 255 ```mermaid
 256 flowchart LR
 257     A --> B
 258     A --- C
 259     A -.-> D
 260     A ==> E
 261     A --text--> F
 262     A ---|text| G
 263 ```
 264 
 265 | Link | Description |
 266 |------|-------------|
 267 | `-->` | Arrow |
 268 | `---` | Line (no arrow) |
 269 | `-.->` | Dotted arrow |
 270 | `==>` | Thick arrow |
 271 | `--text-->` | Arrow with text |
 272 
 273 ### Subgraphs
 274 
 275 ```mermaid
 276 %%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
 277 flowchart TB
 278     subgraph sf["☁️ SALESFORCE"]
 279         A[Trigger]
 280         B[Flow]
 281     end
 282 
 283     subgraph ext["🏭 EXTERNAL"]
 284         C[API]
 285     end
 286 
 287     A --> B
 288     B --> C
 289 
 290     style sf fill:#ecfeff,stroke:#0e7490,stroke-dasharray:5
 291     style ext fill:#ecfdf5,stroke:#047857,stroke-dasharray:5
 292     style A fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
 293     style B fill:#c7d2fe,stroke:#4338ca,color:#1f2937
 294     style C fill:#a7f3d0,stroke:#047857,color:#1f2937
 295 ```
 296 
 297 ---
 298 
 299 ## Theming
 300 
 301 ### Init Directive
 302 
 303 For spacing configuration (recommended):
 304 ```mermaid
 305 %%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
 306 flowchart LR
 307     A --> B
 308 
 309     style A fill:#a5f3fc,stroke:#0e7490,color:#1f2937
 310     style B fill:#a5f3fc,stroke:#0e7490,color:#1f2937
 311 ```
 312 
 313 For theme variables (legacy - prefer individual `style` declarations):
 314 ```mermaid
 315 %%{init: {'theme': 'base', 'themeVariables': {
 316   'primaryColor': '#00A1E0',
 317   'primaryTextColor': '#032D60',
 318   'lineColor': '#706E6B'
 319 }}}%%
 320 flowchart LR
 321     A --> B
 322 ```
 323 
 324 ### Available Themes
 325 
 326 | Theme | Description |
 327 |-------|-------------|
 328 | `default` | Standard theme |
 329 | `base` | Base for customization |
 330 | `dark` | Dark mode |
 331 | `forest` | Green tones |
 332 | `neutral` | Grayscale |
 333 
 334 ### Common Theme Variables
 335 
 336 **Sequence Diagrams:**
 337 - `actorBkg`, `actorTextColor`, `actorBorder`
 338 - `signalColor`, `signalTextColor`
 339 - `labelBoxBkgColor`, `labelTextColor`
 340 - `noteBkgColor`, `noteTextColor`
 341 
 342 **ER Diagrams:**
 343 - `primaryColor`, `primaryTextColor`
 344 - `lineColor`
 345 - `attributeBackgroundColorOdd/Even`
 346 
 347 **Flowcharts:**
 348 - `primaryColor`, `primaryTextColor`
 349 - `lineColor`, `nodeBorder`
 350 - `mainBkg`, `clusterBkg`
 351 
 352 ---
 353 
 354 ## Special Characters
 355 
 356 ### Escaping
 357 
 358 Use `#` codes for special characters:
 359 
 360 | Code | Character |
 361 |------|-----------|
 362 | `#quot;` | " |
 363 | `#amp;` | & |
 364 | `#lt;` | < |
 365 | `#gt;` | > |
 366 | `#59;` | ; |
 367 
 368 ### Line Breaks in Text
 369 
 370 Use `<br/>` for line breaks:
 371 
 372 ```mermaid
 373 sequenceDiagram
 374     participant A as Line 1<br/>Line 2
 375 ```
 376 
 377 ---
 378 
 379 ## Tips and Tricks
 380 
 381 ### 1. Comments
 382 
 383 ```mermaid
 384 sequenceDiagram
 385     %% This is a comment
 386     A->>B: Hello
 387 ```
 388 
 389 ### 2. Multiline Notes
 390 
 391 ```mermaid
 392 sequenceDiagram
 393     Note over A,B: Line 1<br/>Line 2<br/>Line 3
 394 ```
 395 
 396 ### 3. Styling Individual Nodes
 397 
 398 Using `style` declarations (sf-skills standard):
 399 ```mermaid
 400 %%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
 401 flowchart LR
 402     A[Success] --> B[Error]
 403 
 404     style A fill:#a7f3d0,stroke:#047857,color:#1f2937
 405     style B fill:#fecaca,stroke:#b91c1c,color:#1f2937
 406 ```
 407 
 408 Using `classDef` (alternative approach):
 409 ```mermaid
 410 flowchart LR
 411     A:::success --> B:::error
 412 
 413     classDef success fill:#a7f3d0,stroke:#047857,color:#1f2937
 414     classDef error fill:#fecaca,stroke:#b91c1c,color:#1f2937
 415 ```
 416 
 417 ### 4. Click Events (Interactive)
 418 
 419 ```mermaid
 420 flowchart LR
 421     A[Salesforce Docs]
 422     click A "https://developer.salesforce.com" "Open Docs"
 423 ```
 424 
 425 ---
 426 
 427 ## Resources
 428 
 429 - [Mermaid Official Docs](https://mermaid.js.org/intro/)
 430 - [Mermaid Live Editor](https://mermaid.live/)
 431 - [Sequence Diagram Syntax](https://mermaid.js.org/syntax/sequenceDiagram.html)
 432 - [ER Diagram Syntax](https://mermaid.js.org/syntax/entityRelationshipDiagram.html)
 433 - [Flowchart Syntax](https://mermaid.js.org/syntax/flowchart.html)
