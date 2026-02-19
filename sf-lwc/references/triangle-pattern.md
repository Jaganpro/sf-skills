<!-- Parent: sf-lwc/SKILL.md -->
   1 # Flow-LWC-Apex Triangle: LWC Perspective
   2 
   3 The **Triangle Architecture** is a foundational Salesforce pattern where Flow, LWC, and Apex work together. This guide focuses on the **LWC role** in this architecture.
   4 
   5 ---
   6 
   7 ## Architecture Overview
   8 
   9 ```
  10                          ┌─────────────────────────────────────┐
  11                          │              FLOW                   │
  12                          │         (Orchestrator)              │
  13                          └───────────────┬─────────────────────┘
  14                                          │
  15               ┌──────────────────────────┼──────────────────────────┐
  16               │                          │                          │
  17               │ screens                  │ actionCalls              │
  18               │ <componentInstance>      │ actionType="apex"        │
  19               │                          │                          │
  20               ▼                          ▼                          ▲
  21 ┌─────────────────────────┐    ┌─────────────────────────┐         │
  22 │          LWC            │    │         APEX            │         │
  23 │     (UI Component)      │───▶│   (Business Logic)      │─────────┘
  24 │                         │    │                         │
  25 │ • Rich UI/UX        ◀── YOU ARE HERE                   │
  26 │ • User Interaction      │    │ • @InvocableMethod      │
  27 │ • FlowAttribute         │    │ • @AuraEnabled          │
  28 │   ChangeEvent           │    │ • Complex Logic         │
  29 │ • FlowNavigation        │    │ • DML Operations        │
  30 │   FinishEvent           │    │                         │
  31 └─────────────────────────┘    └─────────────────────────┘
  32               │                          ▲
  33               │      @AuraEnabled        │
  34               │      wire / imperative   │
  35               └──────────────────────────┘
  36 ```
  37 
  38 ---
  39 
  40 ## LWC's Role in the Triangle
  41 
  42 | Communication Path | Mechanism | Direction |
  43 |-------------------|-----------|-----------|
  44 | Flow → LWC | `inputParameters` → `@api` | One-way input |
  45 | LWC → Flow | `FlowAttributeChangeEvent` | Event-based output |
  46 | LWC → Flow Nav | `FlowNavigationFinishEvent` | Navigation command |
  47 | LWC → Apex | `@wire` or `imperative` | Async call |
  48 | Apex → LWC | Return value / wire refresh | Response |
  49 
  50 ---
  51 
  52 ## Pattern 1: Flow Screen Component
  53 
  54 **Use Case**: Custom UI component for user selection within a guided Flow.
  55 
  56 ```
  57 ┌─────────┐     @api (in)      ┌─────────┐
  58 │  FLOW   │ ────────────────▶  │   LWC   │
  59 │ Screen  │                    │  Screen │
  60 │         │ ◀────────────────  │Component│
  61 │         │  FlowAttribute     │         │
  62 └─────────┘   ChangeEvent      └─────────┘
  63 ```
  64 
  65 ### LWC JavaScript
  66 
  67 ```javascript
  68 import { LightningElement, api } from 'lwc';
  69 import { FlowAttributeChangeEvent, FlowNavigationFinishEvent } from 'lightning/flowSupport';
  70 
  71 export default class RecordSelector extends LightningElement {
  72     // Input from Flow (read-only in component)
  73     @api recordId;
  74     @api availableActions = [];
  75 
  76     // Output to Flow (must dispatch event to update)
  77     @api selectedRecordId;
  78 
  79     handleSelect(event) {
  80         // Update local property
  81         this.selectedRecordId = event.detail.id;
  82 
  83         // CRITICAL: Dispatch event to update Flow variable
  84         this.dispatchEvent(new FlowAttributeChangeEvent(
  85             'selectedRecordId',  // Must match @api property name
  86             this.selectedRecordId
  87         ));
  88     }
  89 
  90     handleFinish() {
  91         // Navigate Flow to next screen
  92         if (this.availableActions.find(action => action === 'NEXT')) {
  93             this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
  94         }
  95     }
  96 }
  97 ```
  98 
  99 ### LWC meta.xml (Flow Target)
 100 
 101 ```xml
 102 <?xml version="1.0" encoding="UTF-8"?>
 103 <LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
 104     <apiVersion>65.0</apiVersion>
 105     <isExposed>true</isExposed>
 106     <masterLabel>Record Selector</masterLabel>
 107     <description>Custom record selection component for Flow screens</description>
 108     <targets>
 109         <target>lightning__FlowScreen</target>
 110     </targets>
 111     <targetConfigs>
 112         <targetConfig targets="lightning__FlowScreen">
 113             <property name="recordId" type="String" label="Record ID" description="Parent record ID"/>
 114             <property name="selectedRecordId" type="String" label="Selected Record ID" role="outputOnly"/>
 115         </targetConfig>
 116     </targetConfigs>
 117 </LightningComponentBundle>
 118 ```
 119 
 120 ### Property Roles
 121 
 122 | Role | Description | Flow Behavior |
 123 |------|-------------|---------------|
 124 | (none) | Input/Output | Editable in Flow builder |
 125 | `role="inputOnly"` | Input only | Cannot be used as output |
 126 | `role="outputOnly"` | Output only | Read-only in Flow builder |
 127 
 128 ---
 129 
 130 ## Pattern 2: LWC Calling Apex
 131 
 132 **Use Case**: LWC needs data or operations beyond Flow context.
 133 
 134 ### Wire Pattern (Reactive, Cached)
 135 
 136 ```javascript
 137 import { LightningElement, api, wire } from 'lwc';
 138 import getRecords from '@salesforce/apex/RecordController.getRecords';
 139 
 140 export default class RecordList extends LightningElement {
 141     @api recordId;
 142     records;
 143     error;
 144 
 145     @wire(getRecords, { parentId: '$recordId' })
 146     wiredRecords({ error, data }) {
 147         if (data) {
 148             this.records = data;
 149             this.error = undefined;
 150         } else if (error) {
 151             this.error = error;
 152             this.records = undefined;
 153         }
 154     }
 155 }
 156 ```
 157 
 158 ### Imperative Pattern (On-Demand, Fresh)
 159 
 160 ```javascript
 161 import { LightningElement, api } from 'lwc';
 162 import { FlowNavigationFinishEvent } from 'lightning/flowSupport';
 163 import processRecord from '@salesforce/apex/RecordController.processRecord';
 164 
 165 export default class RecordProcessor extends LightningElement {
 166     @api recordId;
 167     @api availableActions = [];
 168     isProcessing = false;
 169 
 170     async handleSubmit() {
 171         this.isProcessing = true;
 172         try {
 173             const result = await processRecord({ recordId: this.recordId });
 174             if (result.isSuccess) {
 175                 // Navigate Flow forward
 176                 this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
 177             }
 178         } catch (error) {
 179             // Handle error (show toast, etc.)
 180             console.error('Processing failed:', error.body.message);
 181         } finally {
 182             this.isProcessing = false;
 183         }
 184     }
 185 }
 186 ```
 187 
 188 ### When to Use Each Pattern
 189 
 190 | Pattern | Use When | Caching |
 191 |---------|----------|---------|
 192 | `@wire` | Data should refresh when inputs change | Yes (cacheable=true) |
 193 | Imperative | User-triggered action, DML needed | No |
 194 
 195 ---
 196 
 197 ## Pattern 3: Full Triangle Integration
 198 
 199 **Use Case**: LWC in Flow screen that calls Apex for complex operations.
 200 
 201 ```javascript
 202 import { LightningElement, api, wire } from 'lwc';
 203 import { FlowAttributeChangeEvent, FlowNavigationFinishEvent } from 'lightning/flowSupport';
 204 import getProducts from '@salesforce/apex/ProductController.getProducts';
 205 import calculatePricing from '@salesforce/apex/PricingService.calculate';
 206 
 207 export default class ProductSelector extends LightningElement {
 208     @api accountId;           // Input from Flow
 209     @api selectedProducts;    // Output to Flow
 210     @api totalPrice;          // Output to Flow
 211     @api availableActions = [];
 212 
 213     products;
 214     selectedIds = new Set();
 215 
 216     // Wire: Fetch products reactively
 217     @wire(getProducts, { accountId: '$accountId' })
 218     wiredProducts({ data, error }) {
 219         if (data) this.products = data;
 220     }
 221 
 222     handleProductSelect(event) {
 223         const productId = event.target.dataset.id;
 224         if (this.selectedIds.has(productId)) {
 225             this.selectedIds.delete(productId);
 226         } else {
 227             this.selectedIds.add(productId);
 228         }
 229         this.updateFlowOutputs();
 230     }
 231 
 232     async updateFlowOutputs() {
 233         // Update selected products output
 234         this.selectedProducts = Array.from(this.selectedIds);
 235         this.dispatchEvent(new FlowAttributeChangeEvent(
 236             'selectedProducts',
 237             this.selectedProducts
 238         ));
 239 
 240         // Imperative: Calculate pricing
 241         const result = await calculatePricing({
 242             productIds: this.selectedProducts
 243         });
 244         this.totalPrice = result.total;
 245         this.dispatchEvent(new FlowAttributeChangeEvent(
 246             'totalPrice',
 247             this.totalPrice
 248         ));
 249     }
 250 
 251     handleNext() {
 252         this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
 253     }
 254 }
 255 ```
 256 
 257 ---
 258 
 259 ## Jest Testing (Flow Integration)
 260 
 261 ```javascript
 262 import { createElement } from 'lwc';
 263 import RecordSelector from 'c/recordSelector';
 264 import { FlowAttributeChangeEvent, FlowNavigationFinishEvent } from 'lightning/flowSupport';
 265 
 266 // Mock lightning/flowSupport
 267 jest.mock('lightning/flowSupport', () => ({
 268     FlowAttributeChangeEvent: jest.fn(),
 269     FlowNavigationFinishEvent: jest.fn()
 270 }), { virtual: true });
 271 
 272 describe('c-record-selector', () => {
 273     afterEach(() => {
 274         while (document.body.firstChild) {
 275             document.body.removeChild(document.body.firstChild);
 276         }
 277         jest.clearAllMocks();
 278     });
 279 
 280     it('dispatches FlowAttributeChangeEvent on selection', async () => {
 281         const element = createElement('c-record-selector', {
 282             is: RecordSelector
 283         });
 284         element.recordId = '001xx000003GYHAA2';
 285         document.body.appendChild(element);
 286 
 287         // Simulate user selection
 288         const handler = jest.fn();
 289         element.addEventListener('flowattributechange', handler);
 290 
 291         const tile = element.shadowRoot.querySelector('[data-id]');
 292         tile.click();
 293 
 294         // Verify FlowAttributeChangeEvent was constructed
 295         expect(FlowAttributeChangeEvent).toHaveBeenCalledWith(
 296             'selectedRecordId',
 297             expect.any(String)
 298         );
 299     });
 300 
 301     it('dispatches FlowNavigationFinishEvent on finish', async () => {
 302         const element = createElement('c-record-selector', {
 303             is: RecordSelector
 304         });
 305         element.availableActions = ['NEXT', 'FINISH'];
 306         document.body.appendChild(element);
 307 
 308         const finishButton = element.shadowRoot.querySelector('.finish-button');
 309         finishButton.click();
 310 
 311         expect(FlowNavigationFinishEvent).toHaveBeenCalledWith('NEXT');
 312     });
 313 });
 314 ```
 315 
 316 ---
 317 
 318 ## Deployment Order
 319 
 320 When deploying integrated triangle solutions:
 321 
 322 ```
 323 1. APEX CLASSES
 324    └── @AuraEnabled controllers (LWC depends on these)
 325 
 326 2. LWC COMPONENTS      ← Deploy SECOND
 327    └── meta.xml with lightning__FlowScreen target
 328    └── JavaScript with Flow imports
 329 
 330 3. FLOWS
 331    └── Reference deployed LWC components
 332 ```
 333 
 334 ---
 335 
 336 ## Common Anti-Patterns
 337 
 338 | Anti-Pattern | Problem | Solution |
 339 |--------------|---------|----------|
 340 | Missing FlowAttributeChangeEvent | Output never updates in Flow | Always dispatch event when output changes |
 341 | Direct @api property mutation for outputs | Flow doesn't see changes | Use FlowAttributeChangeEvent |
 342 | Mixing @wire and imperative for same data | Cache/freshness conflicts | Choose one pattern per data need |
 343 | Calling Apex for Flow-available data | Unnecessary callouts | Pass via inputParameters |
 344 | Hardcoded navigation actions | Breaks in different contexts | Check availableActions first |
 345 
 346 ---
 347 
 348 ## Flow Events Reference
 349 
 350 | Event | Purpose | Parameters |
 351 |-------|---------|------------|
 352 | `FlowAttributeChangeEvent` | Update output property | (propertyName, value) |
 353 | `FlowNavigationFinishEvent` | Navigate Flow | 'NEXT', 'BACK', 'PAUSE', 'FINISH' |
 354 
 355 ---
 356 
 357 ## Related Documentation
 358 
 359 | Topic | Location |
 360 |-------|----------|
 361 | Flow screen component template | `sf-lwc/assets/flow-screen-component/` |
 362 | LWC best practices | `sf-lwc/references/lwc-best-practices.md` |
 363 | Apex triangle perspective | `sf-apex/references/triangle-pattern.md` |
 364 | Flow triangle perspective | `sf-flow/references/triangle-pattern.md` |
