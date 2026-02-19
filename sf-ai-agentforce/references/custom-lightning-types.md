<!-- Parent: sf-ai-agentforce/SKILL.md -->
   1 <!-- TIER: 3 | DETAILED REFERENCE -->
   2 <!-- Read after: SKILL.md, agent-script-reference.md, actions-guide.md -->
   3 <!-- Purpose: LightningTypeBundle for custom agent action UIs (API 64.0+) -->
   4 
   5 # Custom Lightning Types for Agentforce
   6 
   7 > Build custom UI components for agent action inputs and outputs using LightningTypeBundle
   8 
   9 ## Overview
  10 
  11 **Custom Lightning Types** enable you to define custom data structures with dedicated UI components for Agentforce service agents. When an agent action requires structured input or displays complex output, you can create a custom type with:
  12 
  13 - **Schema**: Define the data structure and validation
  14 - **Editor**: Custom UI for input collection
  15 - **Renderer**: Custom UI for displaying output
  16 
  17 ```
  18 ┌─────────────────────────────────────────────────────────────────────────────┐
  19 │                    CUSTOM LIGHTNING TYPE ARCHITECTURE                        │
  20 ├─────────────────────────────────────────────────────────────────────────────┤
  21 │                                                                             │
  22 │  LightningTypeBundle/                                                       │
  23 │  └── MyCustomType/                                                          │
  24 │      ├── schema.json        ← Data structure definition                     │
  25 │      ├── editor.json        ← Input UI configuration                        │
  26 │      ├── renderer.json      ← Output UI configuration                       │
  27 │      └── MyCustomType.lightningTypeBundle-meta.xml                          │
  28 │                                                                             │
  29 │                           ▼                                                 │
  30 │                                                                             │
  31 │  ┌─────────────────────────────────────────────────────────────────┐       │
  32 │  │                     AGENT CONVERSATION                          │       │
  33 │  ├─────────────────────────────────────────────────────────────────┤       │
  34 │  │  Agent: I need some details to proceed.                         │       │
  35 │  │                                                                  │       │
  36 │  │  ┌──────────────────────────────────────────┐                   │       │
  37 │  │  │ [Custom Input UI - Editor Component]      │                   │       │
  38 │  │  │ ┌───────────────┐ ┌────────────────────┐ │                   │       │
  39 │  │  │ │ Name: [_____] │ │ Type: [Dropdown ▼] │ │                   │       │
  40 │  │  │ └───────────────┘ └────────────────────┘ │                   │       │
  41 │  │  │ [Submit]                                  │                   │       │
  42 │  │  └──────────────────────────────────────────┘                   │       │
  43 │  │                                                                  │       │
  44 │  │  Agent: Here's the result:                                      │       │
  45 │  │                                                                  │       │
  46 │  │  ┌──────────────────────────────────────────┐                   │       │
  47 │  │  │ [Custom Output UI - Renderer Component]   │                   │       │
  48 │  │  │ ┌─────────────────────────────────────┐  │                   │       │
  49 │  │  │ │ Order #12345                         │  │                   │       │
  50 │  │  │ │ Status: ✅ Confirmed                 │  │                   │       │
  51 │  │  │ │ [View Details] [Track Shipment]      │  │                   │       │
  52 │  │  │ └─────────────────────────────────────┘  │                   │       │
  53 │  │  └──────────────────────────────────────────┘                   │       │
  54 │  └─────────────────────────────────────────────────────────────────┘       │
  55 │                                                                             │
  56 └─────────────────────────────────────────────────────────────────────────────┘
  57 ```
  58 
  59 ---
  60 
  61 ## Prerequisites
  62 
  63 ### API Version Requirement
  64 
  65 **Minimum API v64.0+ (Fall '25)** for LightningTypeBundle support.
  66 
  67 ```bash
  68 # Verify org API version
  69 sf org display --target-org [alias] --json | jq '.result.apiVersion'
  70 ```
  71 
  72 ### Enhanced Chat V2 Requirement
  73 
  74 Custom Lightning Types require **Enhanced Chat V2** in Service Cloud:
  75 
  76 1. Go to **Setup → Chat → Chat Settings**
  77 2. Enable **Enhanced Chat Experience**
  78 3. Select **Version 2 (Enhanced)**
  79 
  80 > ⚠️ Without Enhanced Chat V2, custom type UI components will not render.
  81 
  82 ---
  83 
  84 ## File Structure
  85 
  86 ```
  87 force-app/main/default/
  88 └── lightningTypeBundles/
  89     └── OrderDetails/
  90         ├── schema.json
  91         ├── editor.json
  92         ├── renderer.json
  93         └── OrderDetails.lightningTypeBundle-meta.xml
  94 ```
  95 
  96 ### Bundle Metadata XML
  97 
  98 ```xml
  99 <?xml version="1.0" encoding="UTF-8"?>
 100 <LightningTypeBundle xmlns="http://soap.sforce.com/2006/04/metadata">
 101     <masterLabel>Order Details</masterLabel>
 102     <description>Custom type for order information display</description>
 103 </LightningTypeBundle>
 104 ```
 105 
 106 ---
 107 
 108 ## Schema Definition (schema.json)
 109 
 110 The schema defines your data structure using JSON Schema format:
 111 
 112 ### Basic Schema
 113 
 114 ```json
 115 {
 116     "$schema": "http://json-schema.org/draft-07/schema#",
 117     "type": "object",
 118     "title": "OrderDetails",
 119     "description": "Order information for display in agent conversations",
 120     "properties": {
 121         "orderId": {
 122             "type": "string",
 123             "title": "Order ID",
 124             "description": "Unique order identifier"
 125         },
 126         "orderStatus": {
 127             "type": "string",
 128             "title": "Order Status",
 129             "enum": ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"],
 130             "description": "Current order status"
 131         },
 132         "orderDate": {
 133             "type": "string",
 134             "format": "date",
 135             "title": "Order Date"
 136         },
 137         "totalAmount": {
 138             "type": "number",
 139             "title": "Total Amount",
 140             "minimum": 0
 141         },
 142         "items": {
 143             "type": "array",
 144             "title": "Order Items",
 145             "items": {
 146                 "type": "object",
 147                 "properties": {
 148                     "productName": {
 149                         "type": "string"
 150                     },
 151                     "quantity": {
 152                         "type": "integer",
 153                         "minimum": 1
 154                     },
 155                     "price": {
 156                         "type": "number",
 157                         "minimum": 0
 158                     }
 159                 },
 160                 "required": ["productName", "quantity", "price"]
 161             }
 162         }
 163     },
 164     "required": ["orderId", "orderStatus"]
 165 }
 166 ```
 167 
 168 ### Supported JSON Schema Types
 169 
 170 | Type | JSON Schema | Notes |
 171 |------|-------------|-------|
 172 | Text | `"type": "string"` | Standard text input |
 173 | Number | `"type": "number"` | Decimal values |
 174 | Integer | `"type": "integer"` | Whole numbers only |
 175 | Boolean | `"type": "boolean"` | True/false checkbox |
 176 | Enum | `"enum": [...]` | Dropdown selection |
 177 | Date | `"format": "date"` | Date picker |
 178 | DateTime | `"format": "date-time"` | Date and time picker |
 179 | Array | `"type": "array"` | List of items |
 180 | Object | `"type": "object"` | Nested structure |
 181 
 182 ### Validation Keywords
 183 
 184 ```json
 185 {
 186     "properties": {
 187         "email": {
 188             "type": "string",
 189             "format": "email",
 190             "maxLength": 255
 191         },
 192         "quantity": {
 193             "type": "integer",
 194             "minimum": 1,
 195             "maximum": 100
 196         },
 197         "productCode": {
 198             "type": "string",
 199             "pattern": "^PRD-[0-9]{6}$"
 200         }
 201     }
 202 }
 203 ```
 204 
 205 ---
 206 
 207 ## Editor Configuration (editor.json)
 208 
 209 The editor defines how input fields are collected from users:
 210 
 211 ### Basic Editor
 212 
 213 ```json
 214 {
 215     "component": "lightning-record-edit-form",
 216     "attributes": {
 217         "objectApiName": "Custom_Lightning_Type"
 218     },
 219     "fields": [
 220         {
 221             "name": "orderId",
 222             "component": "lightning-input",
 223             "attributes": {
 224                 "label": "Order ID",
 225                 "placeholder": "Enter order number",
 226                 "required": true
 227             }
 228         },
 229         {
 230             "name": "orderStatus",
 231             "component": "lightning-combobox",
 232             "attributes": {
 233                 "label": "Order Status",
 234                 "options": [
 235                     { "label": "Pending", "value": "Pending" },
 236                     { "label": "Processing", "value": "Processing" },
 237                     { "label": "Shipped", "value": "Shipped" },
 238                     { "label": "Delivered", "value": "Delivered" },
 239                     { "label": "Cancelled", "value": "Cancelled" }
 240                 ]
 241             }
 242         },
 243         {
 244             "name": "orderDate",
 245             "component": "lightning-input",
 246             "attributes": {
 247                 "type": "date",
 248                 "label": "Order Date"
 249             }
 250         },
 251         {
 252             "name": "totalAmount",
 253             "component": "lightning-input",
 254             "attributes": {
 255                 "type": "number",
 256                 "label": "Total Amount",
 257                 "formatter": "currency",
 258                 "step": "0.01"
 259             }
 260         }
 261     ],
 262     "submitButton": {
 263         "label": "Submit Order Details",
 264         "variant": "brand"
 265     }
 266 }
 267 ```
 268 
 269 ### Supported Editor Components
 270 
 271 | Component | Use Case | Example |
 272 |-----------|----------|---------|
 273 | `lightning-input` | Text, number, date, email, etc. | `"type": "text"` |
 274 | `lightning-combobox` | Dropdown selection | With `options` array |
 275 | `lightning-checkbox` | Boolean toggle | Single checkbox |
 276 | `lightning-checkbox-group` | Multiple selections | Array of checkboxes |
 277 | `lightning-radio-group` | Single selection from options | Radio buttons |
 278 | `lightning-textarea` | Multi-line text | Long descriptions |
 279 | `lightning-file-upload` | File attachment | Document upload |
 280 
 281 ### Conditional Fields
 282 
 283 ```json
 284 {
 285     "fields": [
 286         {
 287             "name": "hasDiscount",
 288             "component": "lightning-checkbox",
 289             "attributes": {
 290                 "label": "Apply Discount?"
 291             }
 292         },
 293         {
 294             "name": "discountCode",
 295             "component": "lightning-input",
 296             "attributes": {
 297                 "label": "Discount Code"
 298             },
 299             "conditions": {
 300                 "hasDiscount": true
 301             }
 302         }
 303     ]
 304 }
 305 ```
 306 
 307 ---
 308 
 309 ## Renderer Configuration (renderer.json)
 310 
 311 The renderer defines how output is displayed to users:
 312 
 313 ### Basic Renderer
 314 
 315 ```json
 316 {
 317     "component": "lightning-card",
 318     "attributes": {
 319         "title": "Order Details",
 320         "iconName": "standard:orders"
 321     },
 322     "body": [
 323         {
 324             "component": "lightning-layout",
 325             "attributes": {
 326                 "multipleRows": true
 327             },
 328             "body": [
 329                 {
 330                     "component": "lightning-layout-item",
 331                     "attributes": {
 332                         "size": "6"
 333                     },
 334                     "body": [
 335                         {
 336                             "component": "lightning-formatted-text",
 337                             "attributes": {
 338                                 "value": "Order #${orderId}"
 339                             }
 340                         }
 341                     ]
 342                 },
 343                 {
 344                     "component": "lightning-layout-item",
 345                     "attributes": {
 346                         "size": "6"
 347                     },
 348                     "body": [
 349                         {
 350                             "component": "lightning-badge",
 351                             "attributes": {
 352                                 "label": "${orderStatus}"
 353                             }
 354                         }
 355                     ]
 356                 }
 357             ]
 358         },
 359         {
 360             "component": "lightning-formatted-number",
 361             "attributes": {
 362                 "value": "${totalAmount}",
 363                 "style": "currency",
 364                 "currencyCode": "USD"
 365             }
 366         }
 367     ]
 368 }
 369 ```
 370 
 371 ### Supported Renderer Components
 372 
 373 | Component | Use Case |
 374 |-----------|----------|
 375 | `lightning-card` | Container with header |
 376 | `lightning-layout` | Grid layout |
 377 | `lightning-formatted-text` | Display text |
 378 | `lightning-formatted-number` | Currency, percent |
 379 | `lightning-formatted-date-time` | Date display |
 380 | `lightning-badge` | Status indicators |
 381 | `lightning-icon` | Icons |
 382 | `lightning-button` | Actions |
 383 | `lightning-datatable` | Tabular data |
 384 | `lightning-progress-bar` | Progress display |
 385 
 386 ### List Rendering
 387 
 388 For array data:
 389 
 390 ```json
 391 {
 392     "component": "lightning-datatable",
 393     "attributes": {
 394         "keyField": "productName",
 395         "data": "${items}",
 396         "columns": [
 397             { "label": "Product", "fieldName": "productName" },
 398             { "label": "Quantity", "fieldName": "quantity", "type": "number" },
 399             { "label": "Price", "fieldName": "price", "type": "currency" }
 400         ]
 401     }
 402 }
 403 ```
 404 
 405 ---
 406 
 407 ## Complete Example: Customer Address
 408 
 409 ### 1. schema.json
 410 
 411 ```json
 412 {
 413     "$schema": "http://json-schema.org/draft-07/schema#",
 414     "type": "object",
 415     "title": "CustomerAddress",
 416     "properties": {
 417         "street": {
 418             "type": "string",
 419             "title": "Street Address",
 420             "maxLength": 255
 421         },
 422         "city": {
 423             "type": "string",
 424             "title": "City"
 425         },
 426         "state": {
 427             "type": "string",
 428             "title": "State/Province"
 429         },
 430         "postalCode": {
 431             "type": "string",
 432             "title": "Postal Code",
 433             "pattern": "^[0-9]{5}(-[0-9]{4})?$"
 434         },
 435         "country": {
 436             "type": "string",
 437             "title": "Country",
 438             "enum": ["United States", "Canada", "Mexico", "United Kingdom"]
 439         },
 440         "isDefault": {
 441             "type": "boolean",
 442             "title": "Default Address",
 443             "default": false
 444         }
 445     },
 446     "required": ["street", "city", "postalCode", "country"]
 447 }
 448 ```
 449 
 450 ### 2. editor.json
 451 
 452 ```json
 453 {
 454     "layout": "vertical",
 455     "fields": [
 456         {
 457             "name": "street",
 458             "component": "lightning-textarea",
 459             "attributes": {
 460                 "label": "Street Address",
 461                 "placeholder": "Enter your street address",
 462                 "required": true,
 463                 "maxLength": 255
 464             }
 465         },
 466         {
 467             "name": "city",
 468             "component": "lightning-input",
 469             "attributes": {
 470                 "type": "text",
 471                 "label": "City",
 472                 "required": true
 473             }
 474         },
 475         {
 476             "name": "state",
 477             "component": "lightning-input",
 478             "attributes": {
 479                 "type": "text",
 480                 "label": "State/Province"
 481             }
 482         },
 483         {
 484             "name": "postalCode",
 485             "component": "lightning-input",
 486             "attributes": {
 487                 "type": "text",
 488                 "label": "Postal Code",
 489                 "required": true,
 490                 "pattern": "[0-9]{5}(-[0-9]{4})?"
 491             }
 492         },
 493         {
 494             "name": "country",
 495             "component": "lightning-combobox",
 496             "attributes": {
 497                 "label": "Country",
 498                 "required": true,
 499                 "options": [
 500                     { "label": "United States", "value": "United States" },
 501                     { "label": "Canada", "value": "Canada" },
 502                     { "label": "Mexico", "value": "Mexico" },
 503                     { "label": "United Kingdom", "value": "United Kingdom" }
 504                 ]
 505             }
 506         },
 507         {
 508             "name": "isDefault",
 509             "component": "lightning-checkbox",
 510             "attributes": {
 511                 "label": "Set as default address"
 512             }
 513         }
 514     ],
 515     "submitButton": {
 516         "label": "Save Address",
 517         "variant": "brand"
 518     }
 519 }
 520 ```
 521 
 522 ### 3. renderer.json
 523 
 524 ```json
 525 {
 526     "component": "lightning-card",
 527     "attributes": {
 528         "title": "Shipping Address",
 529         "iconName": "standard:address"
 530     },
 531     "body": [
 532         {
 533             "component": "lightning-formatted-address",
 534             "attributes": {
 535                 "street": "${street}",
 536                 "city": "${city}",
 537                 "province": "${state}",
 538                 "postalCode": "${postalCode}",
 539                 "country": "${country}"
 540             }
 541         },
 542         {
 543             "component": "lightning-badge",
 544             "conditions": {
 545                 "isDefault": true
 546             },
 547             "attributes": {
 548                 "label": "Default",
 549                 "class": "slds-m-top_small"
 550             }
 551         }
 552     ]
 553 }
 554 ```
 555 
 556 ### 4. CustomerAddress.lightningTypeBundle-meta.xml
 557 
 558 ```xml
 559 <?xml version="1.0" encoding="UTF-8"?>
 560 <LightningTypeBundle xmlns="http://soap.sforce.com/2006/04/metadata">
 561     <masterLabel>Customer Address</masterLabel>
 562     <description>Structured address for customer shipping information</description>
 563 </LightningTypeBundle>
 564 ```
 565 
 566 ---
 567 
 568 ## Using Custom Types in Agent Actions
 569 
 570 ### In GenAiFunction Metadata
 571 
 572 ```xml
 573 <GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
 574     <masterLabel>Collect Shipping Address</masterLabel>
 575     <developerName>Collect_Shipping_Address</developerName>
 576     <description>Collects customer shipping address</description>
 577 
 578     <invocationTarget>Collect_Address_Flow</invocationTarget>
 579     <invocationTargetType>flow</invocationTargetType>
 580 
 581     <capability>
 582         Collect the customer's shipping address when they want to update
 583         their delivery information or place an order.
 584     </capability>
 585 
 586     <!-- Output uses custom Lightning Type -->
 587     <genAiFunctionOutputs>
 588         <developerName>shippingAddress</developerName>
 589         <description>The customer's shipping address</description>
 590         <dataType>CustomerAddress</dataType>
 591         <isRequired>true</isRequired>
 592     </genAiFunctionOutputs>
 593 </GenAiFunction>
 594 ```
 595 
 596 ### In Agent Script
 597 
 598 ```agentscript
 599 topic address_management:
 600     label: "Address Management"
 601     description: "Manages customer addresses"
 602 
 603     actions:
 604         Collect_Shipping_Address:
 605             description: "Collect the customer's shipping address"
 606             outputs:
 607                 # Reference custom Lightning Type as output
 608                 shippingAddress: CustomerAddress
 609                     description: "Customer shipping address"
 610                     is_used_by_planner: True
 611                     is_displayable: True
 612             target: "flow://Collect_Address_Flow"
 613 
 614     reasoning:
 615         instructions: ->
 616             | When the user wants to update their shipping address,
 617             | use the Collect_Shipping_Address action.
 618             | The custom UI will collect the address details.
 619         actions:
 620             collect: @actions.Collect_Shipping_Address
 621 ```
 622 
 623 ---
 624 
 625 ## Best Practices
 626 
 627 ```
 628 ┌─────────────────────────────────────────────────────────────────────────────┐
 629 │                    CUSTOM LIGHTNING TYPES BEST PRACTICES                     │
 630 ├─────────────────────────────────────────────────────────────────────────────┤
 631 │                                                                             │
 632 │  SCHEMA DESIGN                                                              │
 633 │  ─────────────────────────────────────────────────────────────────────────  │
 634 │  ✅ Keep schemas focused on a single concept                                │
 635 │  ✅ Use meaningful property names                                           │
 636 │  ✅ Add validation constraints (min, max, pattern)                          │
 637 │  ✅ Mark required fields explicitly                                         │
 638 │  ❌ Don't nest objects more than 2 levels deep                              │
 639 │  ❌ Don't create overly complex schemas                                     │
 640 │                                                                             │
 641 │  EDITOR UX                                                                  │
 642 │  ─────────────────────────────────────────────────────────────────────────  │
 643 │  ✅ Group related fields together                                           │
 644 │  ✅ Use appropriate input types (date picker for dates)                     │
 645 │  ✅ Provide clear labels and placeholders                                   │
 646 │  ✅ Use conditional fields to reduce complexity                             │
 647 │  ❌ Don't require too many fields at once                                   │
 648 │  ❌ Don't hide critical fields behind conditions                            │
 649 │                                                                             │
 650 │  RENDERER UX                                                                │
 651 │  ─────────────────────────────────────────────────────────────────────────  │
 652 │  ✅ Highlight the most important information                                │
 653 │  ✅ Use visual hierarchy (cards, badges, icons)                             │
 654 │  ✅ Format data appropriately (currency, dates)                             │
 655 │  ✅ Keep displays scannable and concise                                     │
 656 │  ❌ Don't display raw data without formatting                               │
 657 │  ❌ Don't crowd too much information                                        │
 658 │                                                                             │
 659 │  DEPLOYMENT                                                                 │
 660 │  ─────────────────────────────────────────────────────────────────────────  │
 661 │  ✅ Deploy LightningTypeBundle before GenAiFunction                         │
 662 │  ✅ Test with Enhanced Chat V2 enabled                                      │
 663 │  ✅ Validate JSON files before deployment                                   │
 664 │  ❌ Don't reference undefined custom types                                  │
 665 │                                                                             │
 666 └─────────────────────────────────────────────────────────────────────────────┘
 667 ```
 668 
 669 ---
 670 
 671 ## Deployment
 672 
 673 ### package.xml Entry
 674 
 675 ```xml
 676 <?xml version="1.0" encoding="UTF-8"?>
 677 <Package xmlns="http://soap.sforce.com/2006/04/metadata">
 678     <types>
 679         <members>*</members>
 680         <name>LightningTypeBundle</name>
 681     </types>
 682     <version>64.0</version>
 683 </Package>
 684 ```
 685 
 686 ### Deploy Command
 687 
 688 ```bash
 689 # Deploy specific type
 690 sf project deploy start -m "LightningTypeBundle:CustomerAddress"
 691 
 692 # Deploy all types
 693 sf project deploy start -d force-app/main/default/lightningTypeBundles/
 694 
 695 # Deploy with dependencies (type + action)
 696 sf project deploy start -m "LightningTypeBundle:CustomerAddress,GenAiFunction:Collect_Shipping_Address"
 697 ```
 698 
 699 ### Deployment Order
 700 
 701 1. **LightningTypeBundle** - Deploy custom types first
 702 2. **GenAiFunction** - Deploy actions that reference the types
 703 3. **AiAuthoringBundle** - Deploy agent that uses the actions
 704 
 705 ---
 706 
 707 ## Troubleshooting
 708 
 709 | Issue | Cause | Solution |
 710 |-------|-------|----------|
 711 | UI not rendering | Enhanced Chat V2 not enabled | Enable Enhanced Chat V2 in Setup |
 712 | "Type not found" | Custom type not deployed | Deploy LightningTypeBundle first |
 713 | Schema validation error | Invalid JSON Schema | Validate against JSON Schema draft-07 |
 714 | Editor fields missing | Incorrect field names | Match `name` in editor.json to schema properties |
 715 | Renderer empty | Variable syntax error | Use `${propertyName}` for value interpolation |
 716 
 717 ---
 718 
 719 ## Related Documentation
 720 
 721 - [Actions Reference](actions-reference.md) - GenAiFunction metadata
 722 - [Agent Script Reference](agent-script-reference.md) - Action syntax
 723 - [Patterns & Practices](patterns-and-practices.md) - Agent design patterns
 724 
 725 ---
 726 
 727 ## Source
 728 
 729 > **Reference**: [How to Use Custom Lightning Types in Agentforce Service Agents](https://salesforcediaries.com/2025/11/23/how-to-use-custom-lightning-types-in-agentforce-service-agents-1/) - Salesforce Diaries
