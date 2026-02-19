<!-- Parent: sf-diagram-nanobananapro/SKILL.md -->
   1 # Interview Questions Reference
   2 
   3 This document defines the questions Claude should ask (via `AskUserQuestion`) before generating images with sf-diagram-nanobananapro.
   4 
   5 ---
   6 
   7 ## How to Use This Reference
   8 
   9 When a user requests an image, Claude should:
  10 
  11 1. **Detect image type** from the request
  12 2. **Find the matching question set** below
  13 3. **Invoke AskUserQuestion** with those questions
  14 4. **Build prompt** using the answers
  15 5. **Generate image** with optimized parameters
  16 
  17 ### Skip Interview Triggers
  18 
  19 Skip questions and use defaults when user says:
  20 - "quick" - e.g., "Quick ERD of Account-Contact"
  21 - "simple" - e.g., "Simple LWC mockup"
  22 - "just generate" - e.g., "Just generate an architecture diagram"
  23 - "fast" - e.g., "Fast ERD draft"
  24 
  25 ---
  26 
  27 ## ERD Diagram Questions
  28 
  29 ### When to Use
  30 User mentions: ERD, entity relationship, data model, object relationships, schema diagram
  31 
  32 ### Questions
  33 
  34 ```json
  35 {
  36   "questions": [
  37     {
  38       "question": "Which objects should be included in the ERD?",
  39       "header": "Objects",
  40       "multiSelect": false,
  41       "options": [
  42         {
  43           "label": "Core CRM (Recommended)",
  44           "description": "Account, Contact, Opportunity, Case - standard sales/service objects"
  45         },
  46         {
  47           "label": "Sales Cloud",
  48           "description": "Lead, Campaign, Quote, Order, PriceBook, Product"
  49         },
  50         {
  51           "label": "Service Cloud",
  52           "description": "Case, Knowledge, Entitlement, Asset, ServiceContract"
  53         },
  54         {
  55           "label": "Custom objects",
  56           "description": "I'll specify the custom objects to include"
  57         }
  58       ]
  59     },
  60     {
  61       "question": "What visual style do you prefer?",
  62       "header": "Style",
  63       "multiSelect": false,
  64       "options": [
  65         {
  66           "label": "Architect.salesforce.com (Recommended)",
  67           "description": "Official Salesforce style: dark border + light fill, header banner, legend bar"
  68         },
  69         {
  70           "label": "Whiteboard",
  71           "description": "Hand-drawn look, casual feel for brainstorming"
  72         },
  73         {
  74           "label": "Technical",
  75           "description": "Detailed with field names and data types"
  76         },
  77         {
  78           "label": "Minimalist",
  79           "description": "Simple boxes, focus on relationships only"
  80         }
  81       ]
  82     },
  83     {
  84       "question": "What's the primary purpose of this ERD?",
  85       "header": "Purpose",
  86       "multiSelect": false,
  87       "options": [
  88         {
  89           "label": "Documentation (4K)",
  90           "description": "High quality for wikis, docs, long-term reference"
  91         },
  92         {
  93           "label": "Quick draft (1K)",
  94           "description": "Fast iteration, refine the prompt first"
  95         },
  96         {
  97           "label": "Presentation",
  98           "description": "Slides for stakeholders, clean and simple"
  99         },
 100         {
 101           "label": "Architecture review",
 102           "description": "Technical discussion with developers/architects"
 103         }
 104       ]
 105     },
 106     {
 107       "question": "Any special requirements? (Select all that apply)",
 108       "header": "Extras",
 109       "multiSelect": true,
 110       "options": [
 111         {
 112           "label": "Include legend",
 113           "description": "Add a legend explaining colors and relationship types"
 114         },
 115         {
 116           "label": "Show field names",
 117           "description": "Display key fields inside each object box"
 118         },
 119         {
 120           "label": "Color-code by type",
 121           "description": "Standard=blue, Custom=orange, External=green"
 122         },
 123         {
 124           "label": "None",
 125           "description": "Use default styling without extras"
 126         }
 127       ]
 128     }
 129   ]
 130 }
 131 ```
 132 
 133 ### Answer-to-Prompt Mapping
 134 
 135 | Answer | Prompt Addition |
 136 |--------|-----------------|
 137 | Core CRM | "Account, Contact, Opportunity, Case with standard relationships" |
 138 | Sales Cloud | "Lead, Campaign, Quote, Order, PriceBook, Product with conversion flows" |
 139 | Service Cloud | "Case, Knowledge, Entitlement, Asset, ServiceContract hierarchy" |
 140 | Architect.salesforce.com | "Official architect.salesforce.com style: page title, header banner with Salesforce logo, LEGEND bar (ENTITIES + RELATIONSHIPS), dark border + light translucent fill boxes (~25% opacity), labeled relationship lines, footer with copyright" |
 141 | Whiteboard | "Hand-drawn sketch style, informal, whiteboard aesthetic" |
 142 | Technical | "Include field names, data types, API names in each box" |
 143 | Documentation (4K) | Use Python script with `-r 4K`, include full header + legend |
 144 | Quick draft (1K) | Use CLI or Python with `-r 1K` |
 145 | Include legend | "Include LEGEND bar at top with ENTITIES and RELATIONSHIPS sections" |
 146 | Color-code | "Auto-detect cloud color: Sales=Teal #0B827C, Service=Magenta #9E2A7D, Platform=Purple #5A67D8" |
 147 
 148 ### Default Values (for Skip Mode)
 149 
 150 - Objects: Core CRM
 151 - Style: Architect.salesforce.com
 152 - Purpose: Quick draft (1K)
 153 - Extras: Include legend
 154 
 155 ---
 156 
 157 ## LWC Component Mockup Questions
 158 
 159 ### When to Use
 160 User mentions: LWC, Lightning Web Component, component mockup, wireframe, UI mockup, form, table, card
 161 
 162 ### Questions
 163 
 164 ```json
 165 {
 166   "questions": [
 167     {
 168       "question": "What type of component do you need?",
 169       "header": "Component",
 170       "multiSelect": false,
 171       "options": [
 172         {
 173           "label": "Data table (Recommended)",
 174           "description": "List view with columns, sorting, row actions"
 175         },
 176         {
 177           "label": "Record form",
 178           "description": "Create/edit form with fields and sections"
 179         },
 180         {
 181           "label": "Dashboard card",
 182           "description": "Metrics, charts, or KPI tiles"
 183         },
 184         {
 185           "label": "Custom layout",
 186           "description": "I'll describe the specific layout needed"
 187         }
 188       ]
 189     },
 190     {
 191       "question": "Which Salesforce object is this for?",
 192       "header": "Object",
 193       "multiSelect": false,
 194       "options": [
 195         {
 196           "label": "Account",
 197           "description": "Customer/company records"
 198         },
 199         {
 200           "label": "Contact",
 201           "description": "Individual person records"
 202         },
 203         {
 204           "label": "Opportunity",
 205           "description": "Sales deals and pipeline"
 206         },
 207         {
 208           "label": "Custom object",
 209           "description": "I'll specify the object name"
 210         }
 211       ]
 212     },
 213     {
 214       "question": "Where will this component be used?",
 215       "header": "Context",
 216       "multiSelect": false,
 217       "options": [
 218         {
 219           "label": "Lightning Record Page (Recommended)",
 220           "description": "Embedded on Account, Contact, etc. detail pages"
 221         },
 222         {
 223           "label": "Lightning App Page",
 224           "description": "Home page, dashboard, or custom app"
 225         },
 226         {
 227           "label": "Experience Cloud",
 228           "description": "Customer/partner portal (community)"
 229         },
 230         {
 231           "label": "Standalone app",
 232           "description": "Full-page Lightning app or utility bar"
 233         }
 234       ]
 235     },
 236     {
 237       "question": "Style preferences? (Select all that apply)",
 238       "header": "Style",
 239       "multiSelect": true,
 240       "options": [
 241         {
 242           "label": "SLDS standard",
 243           "description": "Standard Lightning Design System styling"
 244         },
 245         {
 246           "label": "Dense/compact",
 247           "description": "Reduced spacing for data-heavy views"
 248         },
 249         {
 250           "label": "Mobile-responsive",
 251           "description": "Adapts to mobile screen sizes"
 252         },
 253         {
 254           "label": "Card-based",
 255           "description": "Elevated card container with shadow"
 256         }
 257       ]
 258     }
 259   ]
 260 }
 261 ```
 262 
 263 ### Answer-to-Prompt Mapping
 264 
 265 | Answer | Prompt Addition |
 266 |--------|-----------------|
 267 | Data table | "Lightning datatable with columns, header with search, row actions menu" |
 268 | Record form | "Lightning record form with sections, field labels, Save/Cancel buttons" |
 269 | Dashboard card | "SLDS card component with metric value, label, trend indicator" |
 270 | Lightning Record Page | "Component sized for record page sidebar or main content" |
 271 | Experience Cloud | "Portal-friendly styling, user-facing design" |
 272 | Dense/compact | "Compact spacing, reduced padding, data-dense layout" |
 273 | Mobile-responsive | "Responsive design, single column on mobile" |
 274 
 275 ### Default Values (for Skip Mode)
 276 
 277 - Component: Data table
 278 - Object: Account
 279 - Context: Lightning Record Page
 280 - Style: SLDS standard
 281 
 282 ---
 283 
 284 ## Architecture/Integration Diagram Questions
 285 
 286 ### When to Use
 287 User mentions: architecture, integration, system diagram, data flow, API flow, authentication flow
 288 
 289 ### Questions
 290 
 291 ```json
 292 {
 293   "questions": [
 294     {
 295       "question": "What type of diagram do you need?",
 296       "header": "Diagram",
 297       "multiSelect": false,
 298       "options": [
 299         {
 300           "label": "Integration flow (Recommended)",
 301           "description": "System-to-system data synchronization"
 302         },
 303         {
 304           "label": "Data flow",
 305           "description": "Entity movement between systems"
 306         },
 307         {
 308           "label": "Authentication flow",
 309           "description": "OAuth, JWT, SSO sequence diagram"
 310         },
 311         {
 312           "label": "Event-driven",
 313           "description": "Platform Events, CDC, pub/sub architecture"
 314         }
 315       ]
 316     },
 317     {
 318       "question": "Which systems are involved?",
 319       "header": "Systems",
 320       "multiSelect": false,
 321       "options": [
 322         {
 323           "label": "Salesforce + ERP",
 324           "description": "SAP, Oracle, NetSuite, Microsoft Dynamics"
 325         },
 326         {
 327           "label": "Salesforce + Marketing",
 328           "description": "Marketo, Pardot, HubSpot, Marketing Cloud"
 329         },
 330         {
 331           "label": "Salesforce + Custom APIs",
 332           "description": "Internal services, microservices, legacy systems"
 333         },
 334         {
 335           "label": "Multiple systems",
 336           "description": "I'll specify the systems involved"
 337         }
 338       ]
 339     },
 340     {
 341       "question": "What protocols/patterns are used? (Select all that apply)",
 342       "header": "Protocols",
 343       "multiSelect": true,
 344       "options": [
 345         {
 346           "label": "REST APIs",
 347           "description": "JSON over HTTP, most common pattern"
 348         },
 349         {
 350           "label": "Platform Events / CDC",
 351           "description": "Salesforce event-driven integration"
 352         },
 353         {
 354           "label": "MuleSoft / iPaaS",
 355           "description": "Integration platform as middleware"
 356         },
 357         {
 358           "label": "SOAP / Legacy",
 359           "description": "XML-based, enterprise protocols"
 360         }
 361       ]
 362     },
 363     {
 364       "question": "What elements should be highlighted? (Select all that apply)",
 365       "header": "Elements",
 366       "multiSelect": true,
 367       "options": [
 368         {
 369           "label": "Auth badges",
 370           "description": "Show OAuth 2.0, JWT, API Key on connections"
 371         },
 372         {
 373           "label": "Error handling",
 374           "description": "Retry logic, dead letter queues, fallbacks"
 375         },
 376         {
 377           "label": "Data transforms",
 378           "description": "Mapping, conversion, enrichment steps"
 379         },
 380         {
 381           "label": "Timing/frequency",
 382           "description": "Sync intervals, batch schedules"
 383         }
 384       ]
 385     }
 386   ]
 387 }
 388 ```
 389 
 390 ### Answer-to-Prompt Mapping
 391 
 392 | Answer | Prompt Addition |
 393 |--------|-----------------|
 394 | Integration flow | "System integration diagram with bidirectional data flow arrows" |
 395 | Authentication flow | "OAuth 2.0 sequence diagram with token exchange steps" |
 396 | Salesforce + ERP | "Salesforce (cloud icon) connected to ERP (server icon)" |
 397 | REST APIs | "REST/JSON labels on connection arrows" |
 398 | Platform Events | "Platform Events pub/sub with event bus in center" |
 399 | Auth badges | "OAuth 2.0 / JWT badges on integration arrows" |
 400 | Error handling | "Error queue and retry logic shown as separate path" |
 401 
 402 ### Default Values (for Skip Mode)
 403 
 404 - Diagram: Integration flow
 405 - Systems: Salesforce + Custom APIs
 406 - Protocols: REST APIs
 407 - Elements: Auth badges
 408 
 409 ---
 410 
 411 ## Code Review Questions (Gemini Sub-Agent)
 412 
 413 ### When to Use
 414 User mentions: review, code review, check my code, analyze, audit, best practices
 415 
 416 ### Questions for Apex Review
 417 
 418 ```json
 419 {
 420   "questions": [
 421     {
 422       "question": "What type of Apex code is this?",
 423       "header": "Code Type",
 424       "multiSelect": false,
 425       "options": [
 426         {
 427           "label": "Trigger",
 428           "description": "Before/after trigger on an object"
 429         },
 430         {
 431           "label": "Batch job",
 432           "description": "Batch Apex for large data processing"
 433         },
 434         {
 435           "label": "Service class",
 436           "description": "Business logic, utility, or helper class"
 437         },
 438         {
 439           "label": "Controller",
 440           "description": "Aura/LWC controller or VF controller"
 441         }
 442       ]
 443     },
 444     {
 445       "question": "What should the review focus on?",
 446       "header": "Focus",
 447       "multiSelect": true,
 448       "options": [
 449         {
 450           "label": "Bulkification",
 451           "description": "SOQL/DML in loops, governor limits"
 452         },
 453         {
 454           "label": "Security",
 455           "description": "CRUD/FLS checks, injection vulnerabilities"
 456         },
 457         {
 458           "label": "Performance",
 459           "description": "Query optimization, caching, efficiency"
 460         },
 461         {
 462           "label": "Best practices",
 463           "description": "Naming, structure, patterns, testability"
 464         }
 465       ]
 466     }
 467   ]
 468 }
 469 ```
 470 
 471 ---
 472 
 473 ## Quick Reference Card
 474 
 475 | Image Type | Trigger Keywords | Questions |
 476 |------------|-----------------|-----------|
 477 | ERD | ERD, entity, data model, schema | Objects, Style, Purpose, Extras |
 478 | LWC Mockup | LWC, component, mockup, wireframe | Component, Object, Context, Style |
 479 | Architecture | architecture, integration, flow | Diagram, Systems, Protocols, Elements |
 480 | Code Review | review, analyze, check, audit | Code Type, Focus |
 481 
 482 ---
 483 
 484 ## Example: Full Interview Flow
 485 
 486 ### User Says
 487 "I need an ERD for my Service Cloud implementation"
 488 
 489 ### Claude Invokes AskUserQuestion
 490 ```
 491 Objects: Core CRM / Sales Cloud / Service Cloud / Custom
 492 Style: Professional / Whiteboard / Technical / Minimalist
 493 Purpose: Documentation / Quick draft / Presentation / Review
 494 Extras: Legend / Field names / Color-code / None
 495 ```
 496 
 497 ### User Selects
 498 - Objects: Service Cloud
 499 - Style: Professional
 500 - Purpose: Documentation
 501 - Extras: Legend, Color-code
 502 
 503 ### Claude Builds Prompt
 504 ```
 505 Professional Salesforce ERD diagram showing Service Cloud objects:
 506 - Case (blue, center): Main service object
 507 - Knowledge (green, right): Linked articles
 508 - Entitlement (yellow, left): Service level agreements
 509 - Asset (orange, below): Customer-owned products
 510 - ServiceContract (purple, top): Contract management
 511 
 512 Relationships:
 513 - Case → Knowledge (Lookup, dashed arrow)
 514 - Case → Asset (Lookup, dashed arrow)
 515 - Asset → ServiceContract (Master-Detail, solid arrow)
 516 
 517 Color coding: Standard objects (blue), Service objects (green/yellow)
 518 Include legend in bottom-right corner.
 519 Clean white background, SLDS styling.
 520 ```
 521 
 522 ### Claude Generates
 523 ```bash
 524 uv run scripts/generate_image.py \
 525   -p "[prompt above]" \
 526   -f "service-cloud-erd.png" \
 527   -r 4K
 528 ```
