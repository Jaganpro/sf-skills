<!-- Parent: sf-diagram-mermaid/SKILL.md -->
   1 # sf-diagram Color Palette
   2 
   3 Soft pastel color palette (Tailwind 200-level) with dark borders for clear definition.
   4 
   5 ## Primary Palette (Tailwind 200 + Dark Borders)
   6 
   7 ```
   8 ┌─────────────────────────────────────────────────────────────────────────────┐
   9 │  COMPONENT                │  FILL (200)  │  STROKE (700+) │  TEXT COLOR    │
  10 ├───────────────────────────┼──────────────┼────────────────┼────────────────┤
  11 │  AI & Agents              │  #fbcfe8     │  #be185d       │  #1f2937       │
  12 │  Integration (Orange)     │  #fed7aa     │  #c2410c       │  #1f2937       │
  13 │  Integration (Teal)       │  #99f6e4     │  #0f766e       │  #1f2937       │
  14 │  Diagrams (Sky)           │  #bae6fd     │  #0369a1       │  #1f2937       │
  15 │  Apex/Development         │  #ddd6fe     │  #6d28d9       │  #1f2937       │
  16 │  Flow/Automation          │  #c7d2fe     │  #4338ca       │  #1f2937       │
  17 │  Metadata (Cyan)          │  #a5f3fc     │  #0e7490       │  #1f2937       │
  18 │  Data (Amber)             │  #fde68a     │  #b45309       │  #1f2937       │
  19 │  Deploy (Green)           │  #a7f3d0     │  #047857       │  #1f2937       │
  20 │  Tooling (Slate)          │  #e2e8f0     │  #334155       │  #1f2937       │
  21 └───────────────────────────┴──────────────┴────────────────┴────────────────┘
  22 ```
  23 
  24 ## Subgraph Background Colors (Tailwind 50-level)
  25 
  26 ```
  27 ┌─────────────────────────────────────────────────────────────────────────────┐
  28 │  SUBGRAPH                 │  FILL (50)   │  STROKE (700+) │  STYLE         │
  29 ├───────────────────────────┼──────────────┼────────────────┼────────────────┤
  30 │  AI & Agents              │  #fdf2f8     │  #be185d       │  dashed        │
  31 │  Integration & Security   │  #fff7ed     │  #c2410c       │  dashed        │
  32 │  Development              │  #f5f3ff     │  #6d28d9       │  dashed        │
  33 │  Foundation               │  #ecfeff     │  #0e7490       │  dashed        │
  34 │  DevOps                   │  #ecfdf5     │  #047857       │  dashed        │
  35 │  Tooling                  │  #f8fafc     │  #334155       │  dashed        │
  36 └───────────────────────────┴──────────────┴────────────────┴────────────────┘
  37 ```
  38 
  39 **Design Philosophy**:
  40 - **Node fills**: Tailwind 200-level for visible but soft pastels
  41 - **Subgraph fills**: Tailwind 50-level for subtle background grouping
  42 - **Dark strokes**: Tailwind 700-800 level for clear definition
  43 - **Dark text**: `#1f2937` ensures readability
  44 
  45 ## Salesforce-Specific Colors
  46 
  47 ```
  48 ┌─────────────────────────────────────────────────────────────────────────────┐
  49 │  SALESFORCE COMPONENT     │  FILL (200)  │  STROKE (700+) │  TEXT COLOR    │
  50 ├───────────────────────────┼──────────────┼────────────────┼────────────────┤
  51 │  Salesforce Platform      │  #bae6fd     │  #0369a1       │  #1f2937       │
  52 │  Connected Apps/OAuth     │  #fed7aa     │  #c2410c       │  #1f2937       │
  53 │  External Systems         │  #a7f3d0     │  #047857       │  #1f2937       │
  54 │  Users/Actors             │  #ddd6fe     │  #6d28d9       │  #1f2937       │
  55 │  Platform Events          │  #99f6e4     │  #0f766e       │  #1f2937       │
  56 │  Named Credentials        │  #fed7aa     │  #c2410c       │  #1f2937       │
  57 └───────────────────────────┴──────────────┴────────────────┴────────────────┘
  58 ```
  59 
  60 ## ERD Object Type Colors
  61 
  62 Color coding for data model diagrams by object type:
  63 
  64 ```
  65 ┌─────────────────────────────────────────────────────────────────────────────┐
  66 │  OBJECT TYPE              │  FILL (200)  │  STROKE (700+) │  TEXT COLOR    │
  67 ├───────────────────────────┼──────────────┼────────────────┼────────────────┤
  68 │  Standard Objects [STD]   │  #bae6fd     │  #0369a1       │  #1f2937       │
  69 │  Custom Objects [CUST]    │  #fed7aa     │  #c2410c       │  #1f2937       │
  70 │  External Objects [EXT]   │  #a7f3d0     │  #047857       │  #1f2937       │
  71 └───────────────────────────┴──────────────┴────────────────┴────────────────┘
  72 
  73 ┌─────────────────────────────────────────────────────────────────────────────┐
  74 │  ERD SUBGRAPH             │  FILL (50)   │  STROKE (700+) │  STYLE         │
  75 ├───────────────────────────┼──────────────┼────────────────┼────────────────┤
  76 │  Standard Group           │  #f0f9ff     │  #0369a1       │  dashed        │
  77 │  Custom Group             │  #fff7ed     │  #c2410c       │  dashed        │
  78 │  External Group           │  #ecfdf5     │  #047857       │  dashed        │
  79 │  Legend                   │  #f8fafc     │  #334155       │  dashed        │
  80 └───────────────────────────┴──────────────┴────────────────┴────────────────┘
  81 ```
  82 
  83 ### ERD Style Declarations
  84 
  85 ```mermaid
  86 %% Standard Object - Sky Blue
  87 style Account fill:#bae6fd,stroke:#0369a1,color:#1f2937
  88 
  89 %% Custom Object - Orange
  90 style Invoice__c fill:#fed7aa,stroke:#c2410c,color:#1f2937
  91 
  92 %% External Object - Green
  93 style SAP_Product__x fill:#a7f3d0,stroke:#047857,color:#1f2937
  94 
  95 %% Subgraph - Standard group
  96 style std fill:#f0f9ff,stroke:#0369a1,stroke-dasharray:5
  97 
  98 %% Subgraph - Custom group
  99 style cust fill:#fff7ed,stroke:#c2410c,stroke-dasharray:5
 100 
 101 %% Subgraph - External group
 102 style ext fill:#ecfdf5,stroke:#047857,stroke-dasharray:5
 103 ```
 104 
 105 ### Relationship Arrow Colors
 106 
 107 | Relationship | Style | Notes |
 108 |--------------|-------|-------|
 109 | Lookup | `-->` (default) | Single-line arrow |
 110 | Master-Detail | `==>` | Thick double-line arrow |
 111 
 112 **Note**: Mermaid does not support individual line coloring in erDiagram. Use thick arrows (`==>`) for Master-Detail distinction in flowchart format.
 113 
 114 ## Status Colors
 115 
 116 ```
 117 ┌─────────────────────────────────────────────────────────────────────────────┐
 118 │  STATUS                   │  FILL (200)  │  STROKE (700+) │  ICON          │
 119 ├───────────────────────────┼──────────────┼────────────────┼────────────────┤
 120 │  Success                  │  #a7f3d0     │  #047857       │  ✅            │
 121 │  Error/Failure            │  #fecaca     │  #b91c1c       │  ❌            │
 122 │  Warning                  │  #fde68a     │  #b45309       │  ⚠️            │
 123 │  Info/Neutral             │  #e2e8f0     │  #334155       │  ℹ️            │
 124 │  In Progress              │  #bfdbfe     │  #1d4ed8       │  ⏳            │
 125 └───────────────────────────┴──────────────┴────────────────┴────────────────┘
 126 ```
 127 
 128 ---
 129 
 130 ## Font Family Options
 131 
 132 Mermaid supports custom fonts via `%%{init}`:
 133 
 134 ```
 135 %%{init: { "fontFamily": "Inter, sans-serif", "fontSize": "14px" }}%%
 136 ```
 137 
 138 ### Available Font Options
 139 
 140 | Font | Configuration | Best For |
 141 |------|---------------|----------|
 142 | **Default** | `"trebuchet ms", verdana, arial` | General use (Mermaid default) |
 143 | **Modern** | `"Inter", sans-serif` | Clean, professional diagrams |
 144 | **System** | `-apple-system, "Segoe UI", sans-serif` | Native OS appearance |
 145 | **Monospace** | `"Fira Code", "Consolas", monospace` | Code-focused diagrams |
 146 | **Serif** | `"Georgia", serif` | Document-style diagrams |
 147 
 148 ### Usage Example
 149 
 150 ```mermaid
 151 %%{init: { "fontFamily": "Inter, Trebuchet MS, sans-serif", "fontSize": "14px" }}%%
 152 flowchart LR
 153     A[Start] --> B[End]
 154 ```
 155 
 156 **⚠️ Limitation**: GitHub and VS Code may override custom fonts with their platform defaults.
 157 
 158 ---
 159 
 160 ## Spacing Configuration
 161 
 162 Control diagram density with `%%{init}` configuration:
 163 
 164 ```mermaid
 165 %%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
 166 ```
 167 
 168 ### Available Spacing Options
 169 
 170 | Option | Default | Recommended | Effect |
 171 |--------|---------|-------------|--------|
 172 | `nodeSpacing` | 50 | 80 | Horizontal gap between nodes |
 173 | `rankSpacing` | 50 | 70 | Vertical gap between levels |
 174 | `diagramPadding` | 20 | 20-30 | Padding around entire diagram |
 175 | `padding` | 15 | 15 | Padding between label and shape |
 176 
 177 ### Curve Styles
 178 
 179 | Style | Effect | Best For |
 180 |-------|--------|----------|
 181 | `"basis"` | Smooth curves (default) | Organic, flowing diagrams |
 182 | `"linear"` | Straight lines | Technical, clean diagrams |
 183 | `"stepBefore"` | Step/staircase lines | Very structured diagrams |
 184 
 185 ### Recommended Configuration
 186 
 187 For clean, readable diagrams:
 188 
 189 ```
 190 %%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
 191 ```
 192 
 193 **Why these values?**
 194 - **nodeSpacing: 80** — 60% more horizontal space than default
 195 - **rankSpacing: 70** — 40% more vertical space than default
 196 - **curve: basis** — Default smooth curves (omit to use default)
 197 
 198 **⚠️ Limitation**: Subgraphs may not fully inherit spacing settings due to a [known Mermaid issue](https://github.com/mermaid-js/mermaid/issues/5178).
 199 
 200 ---
 201 
 202 ## Mermaid Styling Approach
 203 
 204 ### Preferred: Individual Node Styling
 205 
 206 Use `style` declarations with 200-level fills and dark strokes:
 207 
 208 ```mermaid
 209 flowchart TB
 210     A["🤖 sf-ai-agentforce"]
 211     B["⚡ sf-apex"]
 212     C["🔗 sf-integration"]
 213 
 214     A --> B
 215     A --> C
 216 
 217     %% 200-level fill + dark stroke + dark text
 218     style A fill:#fbcfe8,stroke:#be185d,color:#1f2937
 219     style B fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
 220     style C fill:#99f6e4,stroke:#0f766e,color:#1f2937
 221 ```
 222 
 223 ### Subgraph Styling
 224 
 225 Use 50-level backgrounds with dark dashed borders:
 226 
 227 ```mermaid
 228 %%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
 229 flowchart TB
 230     subgraph ai["🤖 AI & AGENTS"]
 231         A[Agent]
 232     end
 233 
 234     subgraph dev["💻 DEVELOPMENT"]
 235         B[Apex]
 236         C[Flow]
 237     end
 238 
 239     %% 50-level fill + dark dashed border
 240     style ai fill:#fdf2f8,stroke:#be185d,stroke-dasharray:5
 241     style dev fill:#f5f3ff,stroke:#6d28d9,stroke-dasharray:5
 242 ```
 243 
 244 ---
 245 
 246 ## Node Label Patterns
 247 
 248 ### Simple Label (Recommended)
 249 
 250 ```
 251 ["🤖 sf-ai-agentforce"]
 252 ```
 253 
 254 Keep labels short for consistent rendering.
 255 
 256 ### Database/Cylinder
 257 
 258 ```
 259 [(💾 Database)]
 260 ```
 261 
 262 ---
 263 
 264 ## Complete Style Template
 265 
 266 Copy this template for consistent diagrams with the finalized color scheme:
 267 
 268 ```mermaid
 269 %%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
 270 flowchart TB
 271     subgraph ai["🤖 AI & AGENTS"]
 272         agentforce["🤖 sf-ai-agentforce"]
 273     end
 274 
 275     subgraph integration["🔌 INTEGRATION & SECURITY"]
 276         connectedapps["🔐 sf-connected-apps"]
 277         sfintegration["🔗 sf-integration"]
 278     end
 279 
 280     subgraph development["💻 DEVELOPMENT"]
 281         apex["⚡ sf-apex"]
 282         flow["🔄 sf-flow"]
 283     end
 284 
 285     subgraph foundation["📦 FOUNDATION"]
 286         metadata["📋 sf-metadata"]
 287         data["💾 sf-data"]
 288     end
 289 
 290     subgraph devops["🚀 DEVOPS"]
 291         deploy["🚀 sf-deploy"]
 292     end
 293 
 294     %% Relationships
 295     agentforce -->|"flow actions"| flow
 296     agentforce -->|"API actions"| sfintegration
 297     sfintegration -->|"OAuth apps"| connectedapps
 298     apex -->|"schema"| metadata
 299     flow -->|"schema"| metadata
 300     apex -->|"deploys"| deploy
 301 
 302     %% Node Styling - 200-level fills
 303     style agentforce fill:#fbcfe8,stroke:#be185d,color:#1f2937
 304     style connectedapps fill:#fed7aa,stroke:#c2410c,color:#1f2937
 305     style sfintegration fill:#99f6e4,stroke:#0f766e,color:#1f2937
 306     style apex fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
 307     style flow fill:#c7d2fe,stroke:#4338ca,color:#1f2937
 308     style metadata fill:#a5f3fc,stroke:#0e7490,color:#1f2937
 309     style data fill:#fde68a,stroke:#b45309,color:#1f2937
 310     style deploy fill:#a7f3d0,stroke:#047857,color:#1f2937
 311 
 312     %% Subgraph Styling - 50-level fills with dashed borders
 313     style ai fill:#fdf2f8,stroke:#be185d,stroke-dasharray:5
 314     style integration fill:#fff7ed,stroke:#c2410c,stroke-dasharray:5
 315     style development fill:#f5f3ff,stroke:#6d28d9,stroke-dasharray:5
 316     style foundation fill:#ecfeff,stroke:#0e7490,stroke-dasharray:5
 317     style devops fill:#ecfdf5,stroke:#047857,stroke-dasharray:5
 318 ```
 319 
 320 ### Label Guidelines
 321 
 322 | ✅ DO | ❌ DON'T |
 323 |-------|---------|
 324 | `["🤖 sf-ai-agentforce"]` | `["🤖 sf-ai-agentforce<br/><small>Agent Script</small>"]` |
 325 | `["⚡ sf-apex"]` | `["⚡ sf-apex<br/>Triggers, Services"]` |
 326 | Short edge labels: `"schema"` | Long labels: `"queries schema for validation"` |
 327 
 328 **Why?** Multi-line labels with `<br/>` and `<small>` tags render inconsistently across GitHub, VS Code, and other Mermaid viewers, often causing text cutoff.
 329 
 330 ---
 331 
 332 ## Text Casing Conventions
 333 
 334 ### Recommendation Summary
 335 
 336 | Context | Casing | Example |
 337 |---------|--------|---------|
 338 | **Node Labels** | lowercase | `sf-apex`, `sf-flow` |
 339 | **Subgraph Titles** | UPPERCASE | `AI & AGENTS`, `INTEGRATION & SECURITY` |
 340 | **Edge Labels** | lowercase | `schema`, `deploys`, `flow actions` |
 341 | **ASCII Diagrams** | UPPERCASE | `SALESFORCE PLATFORM`, `EXTERNAL SYSTEMS` |
 342 
 343 ### Detailed Guidelines
 344 
 345 #### Node Labels: lowercase (Recommended)
 346 ```
 347 ["🤖 sf-ai-agentforce"]    ✅ Preferred
 348 ["🤖 SF-AI-AGENTFORCE"]    ❌ Avoid
 349 ["🤖 Sf-Ai-Agentforce"]    ❌ Avoid
 350 ```
 351 
 352 **Why lowercase?**
 353 - Matches the actual skill/package naming convention
 354 - Cleaner, more modern aesthetic
 355 - Consistent with CLI tool naming (npm, pip, etc.)
 356 - Easier to read in compact diagram nodes
 357 
 358 #### Subgraph Titles: UPPERCASE
 359 ```
 360 subgraph ai["🤖 AI & AGENTS"]           ✅ UPPERCASE
 361 subgraph ai["🤖 ai & agents"]           ❌ lowercase
 362 subgraph ai["🤖 Ai & Agents"]           ❌ Title Case
 363 ```
 364 
 365 **Why UPPERCASE?**
 366 - Creates strong visual hierarchy with lowercase node labels
 367 - Subgraphs represent major categories/groups
 368 - Consistent with ASCII diagram headers
 369 - Maximum contrast between group titles and contents
 370 
 371 #### Edge Labels: lowercase
 372 ```
 373 -->|"schema"|              ✅ lowercase
 374 -->|"Schema"|              ❌ Title Case
 375 -->|"SCHEMA"|              ❌ ALL CAPS
 376 ```
 377 
 378 **Why lowercase?**
 379 - Edge labels describe relationships/actions
 380 - Should be subtle, not prominent
 381 - Consistent with node label style
 382 
 383 #### ASCII Diagrams: UPPERCASE for Headers
 384 ```
 385 ┌─────────────────────────────────────┐
 386 │         SYSTEM LANDSCAPE            │   ✅ UPPERCASE header
 387 └─────────────────────────────────────┘
 388 
 389 │  ☁️ SALESFORCE PLATFORM             │   ✅ UPPERCASE section
 390 ```
 391 
 392 **Why UPPERCASE for ASCII?**
 393 - ASCII has limited styling options (no bold, color)
 394 - UPPERCASE creates visual hierarchy
 395 - Traditional technical documentation style
 396 
 397 ### Special Cases
 398 
 399 | Element | Convention | Example |
 400 |---------|------------|---------|
 401 | Salesforce products | Official casing | `Sales Cloud`, `Service Cloud` |
 402 | Acronyms in nodes | lowercase | `sf-ai-agentforce` (not `SF-AI`) |
 403 | Acronyms in subgraphs | UPPERCASE | `AI & Agents`, `API Gateway` |
 404 | Technical terms | lowercase | `apex`, `flow`, `metadata` |
 405 
 406 ---
 407 
 408 ## Icon Reference
 409 
 410 | Category | Icon | Unicode | Usage |
 411 |----------|------|---------|-------|
 412 | AI/Agents | 🤖 | U+1F916 | Agentforce, AI features |
 413 | Apex | ⚡ | U+26A1 | Code, triggers, services |
 414 | Flow | 🔄 | U+1F504 | Automation, flows |
 415 | Metadata | 📋 | U+1F4CB | Objects, fields |
 416 | Data | 💾 | U+1F4BE | SOQL, records |
 417 | Deploy | 🚀 | U+1F680 | CI/CD, deployment |
 418 | Connected Apps | 🔐 | U+1F510 | OAuth, security |
 419 | Integration | 🔗 | U+1F517 | Named Creds, callouts |
 420 | Diagram | 📊 | U+1F4CA | Documentation |
 421 | Tooling | 🛠️ | U+1F6E0 | Utilities |
 422 | User | 👤 | U+1F464 | End users |
 423 | Browser | 🌐 | U+1F310 | Web apps |
 424 | Cloud | ☁️ | U+2601 | Salesforce platform |
 425 | External | 🏭 | U+1F3ED | External systems |
 426 | Database | 💾 | U+1F4BE | Data storage |
 427 
 428 ---
 429 
 430 ## Color Blind Accessibility
 431 
 432 This palette maintains distinguishability for common color blindness:
 433 
 434 | Condition | Our Approach |
 435 |-----------|--------------|
 436 | Protanopia | Pink vs Teal have different luminance |
 437 | Deuteranopia | Orange vs Cyan are well separated |
 438 | Tritanopia | Icons + dark text supplement colors |
 439 
 440 ### Key Principles
 441 
 442 1. **Icons supplement colors** - Every node has an icon
 443 2. **High contrast text** - Dark text (`#1f2937`) on pastel backgrounds
 444 3. **Dark stroke differentiation** - Bold borders add definition
 445 4. **Dashed subgraphs** - Pattern, not just color
 446 
 447 ---
 448 
 449 ## Light/Dark Mode Support
 450 
 451 The pastel style works best on **light backgrounds**. For dark mode contexts:
 452 - 200-level fills remain visible
 453 - Dark strokes provide clear definition
 454 - 50-level subgraph fills adapt reasonably
 455 
 456 ---
 457 
 458 ## References
 459 
 460 - [Tailwind CSS Color Palette](https://tailwindcss.com/docs/colors)
 461 - [Salesforce Lightning Design System](https://www.lightningdesignsystem.com/)
 462 - [CloudSundial Diagrams](https://cloudsundial.com/diagrams-of-identity-flows-in-context)
 463 - [Mermaid Theme Configuration](https://mermaid.js.org/config/theming.html)
