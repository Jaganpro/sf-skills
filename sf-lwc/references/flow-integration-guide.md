<!-- Parent: sf-lwc/SKILL.md -->
   1 # LWC Flow Integration Guide
   2 
   3 This guide covers building Lightning Web Components for use in Salesforce Flow Screens.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────┐
  11 │                     FLOW ↔ LWC COMMUNICATION                        │
  12 ├─────────────────────────────────────────────────────────────────────┤
  13 │                                                                      │
  14 │   ┌─────────────────┐                    ┌─────────────────┐        │
  15 │   │      FLOW       │                    │       LWC       │        │
  16 │   │    Variables    │                    │   Component     │        │
  17 │   └────────┬────────┘                    └────────┬────────┘        │
  18 │            │                                      │                  │
  19 │            │ @api (inputOnly)                     │                  │
  20 │            ├─────────────────────────────────────▶│                  │
  21 │            │                                      │                  │
  22 │            │ FlowAttributeChangeEvent (outputOnly)│                  │
  23 │            │◀─────────────────────────────────────┤                  │
  24 │            │                                      │                  │
  25 │            │ FlowNavigationFinishEvent            │                  │
  26 │            │◀─────────────────────────────────────┤                  │
  27 │            │  (NEXT, BACK, FINISH, PAUSE)         │                  │
  28 │                                                                      │
  29 └─────────────────────────────────────────────────────────────────────┘
  30 ```
  31 
  32 ---
  33 
  34 ## Quick Reference
  35 
  36 | Direction | Mechanism | Use Case |
  37 |-----------|-----------|----------|
  38 | Flow → LWC | `@api` with `role="inputOnly"` | Pass context data to component |
  39 | LWC → Flow | `FlowAttributeChangeEvent` | Return user selections/data |
  40 | LWC → Navigation | `FlowNavigationFinishEvent` | Trigger Next/Back/Finish |
  41 
  42 ---
  43 
  44 ## Meta.xml Configuration
  45 
  46 ### Target Configuration
  47 
  48 ```xml
  49 <targets>
  50     <target>lightning__FlowScreen</target>
  51 </targets>
  52 ```
  53 
  54 ### Property Roles
  55 
  56 ```xml
  57 <targetConfig targets="lightning__FlowScreen">
  58     <!-- INPUT: Flow → Component -->
  59     <property
  60         name="recordId"
  61         type="String"
  62         label="Record ID"
  63         description="ID from Flow"
  64         role="inputOnly"/>
  65 
  66     <!-- OUTPUT: Component → Flow -->
  67     <property
  68         name="selectedValue"
  69         type="String"
  70         label="Selected Value"
  71         description="User's selection"
  72         role="outputOnly"/>
  73 </targetConfig>
  74 ```
  75 
  76 ### Supported Property Types
  77 
  78 | Type | Description | Example |
  79 |------|-------------|---------|
  80 | `String` | Text values | Record IDs, names |
  81 | `Boolean` | True/false | Flags, completion status |
  82 | `Integer` | Whole numbers | Counts, indexes |
  83 | `Date` | Date values | Due dates |
  84 | `DateTime` | Date and time | Timestamps |
  85 | `@salesforce/schema/*` | SObject references | Record types |
  86 
  87 ---
  88 
  89 ## FlowAttributeChangeEvent
  90 
  91 This is the **critical** mechanism for sending data back to Flow.
  92 
  93 ### Import
  94 
  95 ```javascript
  96 import { FlowAttributeChangeEvent } from 'lightning/flowSupport';
  97 ```
  98 
  99 ### Usage
 100 
 101 ```javascript
 102 // Dispatch event to update Flow variable
 103 // First param: @api property name (must match meta.xml exactly)
 104 // Second param: new value
 105 this.dispatchEvent(new FlowAttributeChangeEvent(
 106     'selectedRecordId',  // Property name
 107     this.recordId        // Value
 108 ));
 109 ```
 110 
 111 ### Example: Selection Handler
 112 
 113 ```javascript
 114 @api selectedRecordId;
 115 @api selectedRecordName;
 116 
 117 handleSelect(event) {
 118     const id = event.target.dataset.id;
 119     const name = event.target.dataset.name;
 120 
 121     // Update local properties
 122     this.selectedRecordId = id;
 123     this.selectedRecordName = name;
 124 
 125     // Notify Flow of BOTH changes
 126     this.dispatchEvent(new FlowAttributeChangeEvent('selectedRecordId', id));
 127     this.dispatchEvent(new FlowAttributeChangeEvent('selectedRecordName', name));
 128 }
 129 ```
 130 
 131 ### Common Mistake
 132 
 133 ```javascript
 134 // ❌ WRONG: Only updating local property
 135 this.selectedRecordId = id;
 136 
 137 // ✅ CORRECT: Update AND dispatch event
 138 this.selectedRecordId = id;
 139 this.dispatchEvent(new FlowAttributeChangeEvent('selectedRecordId', id));
 140 ```
 141 
 142 ---
 143 
 144 ## FlowNavigationFinishEvent
 145 
 146 Programmatically trigger Flow navigation from your component.
 147 
 148 ### Import
 149 
 150 ```javascript
 151 import { FlowNavigationFinishEvent } from 'lightning/flowSupport';
 152 ```
 153 
 154 ### Navigation Actions
 155 
 156 | Action | Description | When Available |
 157 |--------|-------------|----------------|
 158 | `'NEXT'` | Go to next screen | Mid-flow screens |
 159 | `'BACK'` | Go to previous screen | After first screen |
 160 | `'FINISH'` | Complete the flow | Final screens |
 161 | `'PAUSE'` | Pause flow (if enabled) | Pausable flows |
 162 
 163 ### Usage
 164 
 165 ```javascript
 166 // Navigate to next screen
 167 this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
 168 
 169 // Navigate back
 170 this.dispatchEvent(new FlowNavigationFinishEvent('BACK'));
 171 
 172 // Finish the flow
 173 this.dispatchEvent(new FlowNavigationFinishEvent('FINISH'));
 174 ```
 175 
 176 ### Check Available Actions
 177 
 178 Flow provides available actions via a special `@api` property:
 179 
 180 ```javascript
 181 // Automatically populated by Flow runtime
 182 @api availableActions = [];
 183 
 184 get canGoNext() {
 185     return this.availableActions.includes('NEXT');
 186 }
 187 
 188 get canGoBack() {
 189     return this.availableActions.includes('BACK');
 190 }
 191 
 192 handleNext() {
 193     if (this.canGoNext) {
 194         this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
 195     }
 196 }
 197 ```
 198 
 199 ### Conditional Navigation Buttons
 200 
 201 ```html
 202 <template lwc:if={canGoBack}>
 203     <lightning-button label="Back" onclick={handleBack}></lightning-button>
 204 </template>
 205 
 206 <template lwc:if={canGoNext}>
 207     <lightning-button label="Next" variant="brand" onclick={handleNext}></lightning-button>
 208 </template>
 209 ```
 210 
 211 ---
 212 
 213 ## Validation Before Navigation
 214 
 215 Always validate before allowing navigation:
 216 
 217 ```javascript
 218 handleNext() {
 219     // Validate
 220     if (!this.selectedRecordId) {
 221         this.errorMessage = 'Please select a record.';
 222         this.dispatchEvent(new FlowAttributeChangeEvent('errorMessage', this.errorMessage));
 223         return;
 224     }
 225 
 226     // Clear error
 227     this.errorMessage = null;
 228     this.dispatchEvent(new FlowAttributeChangeEvent('errorMessage', null));
 229 
 230     // Mark complete and navigate
 231     this.isComplete = true;
 232     this.dispatchEvent(new FlowAttributeChangeEvent('isComplete', true));
 233     this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
 234 }
 235 ```
 236 
 237 ---
 238 
 239 ## Apex Integration in Flow Context
 240 
 241 ### Wire Service
 242 
 243 ```javascript
 244 import { wire } from 'lwc';
 245 import getRecords from '@salesforce/apex/MyController.getRecords';
 246 
 247 @api recordId; // From Flow
 248 
 249 @wire(getRecords, { parentId: '$recordId' })
 250 wiredRecords({ error, data }) {
 251     if (data) {
 252         this.records = data;
 253     } else if (error) {
 254         this.error = this.reduceErrors(error);
 255     }
 256 }
 257 ```
 258 
 259 ### Imperative Calls
 260 
 261 ```javascript
 262 import processRecord from '@salesforce/apex/MyController.processRecord';
 263 
 264 async handleProcess() {
 265     this.isLoading = true;
 266     try {
 267         const result = await processRecord({
 268             recordId: this.selectedRecordId
 269         });
 270 
 271         if (result.success) {
 272             this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
 273         } else {
 274             this.errorMessage = result.message;
 275             this.dispatchEvent(new FlowAttributeChangeEvent('errorMessage', result.message));
 276         }
 277     } catch (error) {
 278         this.errorMessage = this.reduceErrors(error);
 279     } finally {
 280         this.isLoading = false;
 281     }
 282 }
 283 ```
 284 
 285 ---
 286 
 287 ## Flow Context Variables
 288 
 289 Flow provides special context via reserved variable names:
 290 
 291 ```xml
 292 <!-- In Flow Builder, map these to your component -->
 293 <property name="recordId" value="{!$Record.Id}"/>
 294 <property name="objectApiName" value="{!$Record.Object}"/>
 295 ```
 296 
 297 ---
 298 
 299 ## Testing LWC in Flows
 300 
 301 ### Jest Testing
 302 
 303 ```javascript
 304 import { createElement } from 'lwc';
 305 import FlowScreenComponent from 'c/flowScreenComponent';
 306 import { FlowAttributeChangeEvent, FlowNavigationFinishEvent } from 'lightning/flowSupport';
 307 
 308 // Mock the flow support module
 309 jest.mock('lightning/flowSupport', () => ({
 310     FlowAttributeChangeEvent: jest.fn(),
 311     FlowNavigationFinishEvent: jest.fn()
 312 }), { virtual: true });
 313 
 314 describe('c-flow-screen-component', () => {
 315     afterEach(() => {
 316         while (document.body.firstChild) {
 317             document.body.removeChild(document.body.firstChild);
 318         }
 319         jest.clearAllMocks();
 320     });
 321 
 322     it('dispatches FlowAttributeChangeEvent on selection', async () => {
 323         const element = createElement('c-flow-screen-component', {
 324             is: FlowScreenComponent
 325         });
 326         element.availableActions = ['NEXT', 'BACK'];
 327         document.body.appendChild(element);
 328 
 329         // Simulate selection
 330         const tile = element.shadowRoot.querySelector('.record-tile');
 331         tile.click();
 332 
 333         // Verify event dispatched
 334         expect(FlowAttributeChangeEvent).toHaveBeenCalled();
 335     });
 336 
 337     it('dispatches FlowNavigationFinishEvent on next', async () => {
 338         const element = createElement('c-flow-screen-component', {
 339             is: FlowScreenComponent
 340         });
 341         element.availableActions = ['NEXT'];
 342         element.selectedRecordId = '001xx000000001';
 343         document.body.appendChild(element);
 344 
 345         // Click next button
 346         const nextButton = element.shadowRoot.querySelector('lightning-button[label="Next"]');
 347         nextButton.click();
 348 
 349         // Verify navigation event
 350         expect(FlowNavigationFinishEvent).toHaveBeenCalledWith('NEXT');
 351     });
 352 });
 353 ```
 354 
 355 ### Manual Testing
 356 
 357 1. Create a Screen Flow in Setup
 358 2. Add your LWC component to a screen
 359 3. Map input/output variables
 360 4. Test in Flow debug mode
 361 5. Verify variable values in debug panel
 362 
 363 ---
 364 
 365 ## Common Patterns
 366 
 367 ### Selection with Confirmation
 368 
 369 ```javascript
 370 handleSelect(event) {
 371     this.selectedId = event.target.dataset.id;
 372     // Don't navigate yet - wait for explicit confirmation
 373 }
 374 
 375 handleConfirm() {
 376     if (!this.selectedId) {
 377         this.showError('Please select an item');
 378         return;
 379     }
 380 
 381     this.dispatchEvent(new FlowAttributeChangeEvent('selectedId', this.selectedId));
 382     this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
 383 }
 384 ```
 385 
 386 ### Multi-Select to Collection
 387 
 388 ```javascript
 389 @api selectedIds = [];
 390 
 391 handleToggle(event) {
 392     const id = event.target.dataset.id;
 393 
 394     if (this.selectedIds.includes(id)) {
 395         this.selectedIds = this.selectedIds.filter(i => i !== id);
 396     } else {
 397         this.selectedIds = [...this.selectedIds, id];
 398     }
 399 
 400     // Send collection back to Flow
 401     this.dispatchEvent(new FlowAttributeChangeEvent('selectedIds', this.selectedIds));
 402 }
 403 ```
 404 
 405 ### Conditional Screen (Skip Logic)
 406 
 407 ```javascript
 408 connectedCallback() {
 409     // Auto-skip if condition met
 410     if (this.shouldSkip) {
 411         this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
 412     }
 413 }
 414 ```
 415 
 416 ---
 417 
 418 ## Troubleshooting
 419 
 420 | Issue | Cause | Solution |
 421 |-------|-------|----------|
 422 | Output not updating in Flow | Missing FlowAttributeChangeEvent | Always dispatch event after updating @api property |
 423 | Navigation buttons not showing | Wrong availableActions | Check Flow provides availableActions correctly |
 424 | Component not appearing | Missing `isExposed: true` | Set in meta.xml |
 425 | Properties not mapping | Role mismatch | Use `inputOnly` for inputs, `outputOnly` for outputs |
 426 | Values reset on navigation | Local state not persisted | Use @api properties for all persisted data |
 427 
 428 ---
 429 
 430 ## Template
 431 
 432 Use the template at `assets/flow-screen-component/` as a starting point.
 433 
 434 ---
 435 
 436 ## Passing sObjects and Wrapper Classes to Flow
 437 
 438 ### Overview
 439 
 440 Flow can receive complex Apex types through `apex://` type bindings. This enables:
 441 - Passing sObjects directly (not just IDs)
 442 - Passing wrapper/DTO classes with multiple fields
 443 - Two-way data binding for record editing
 444 
 445 ### apex:// Type Syntax
 446 
 447 In your meta.xml, reference Apex classes using the `apex://` prefix:
 448 
 449 ```xml
 450 <targetConfig targets="lightning__FlowScreen">
 451     <!-- Pass entire Account record -->
 452     <property
 453         name="accountRecord"
 454         type="apex://Account"
 455         label="Account Record"
 456         role="inputOnly"/>
 457 
 458     <!-- Pass custom wrapper class -->
 459     <property
 460         name="orderSummary"
 461         type="apex://OrderController.OrderSummaryWrapper"
 462         label="Order Summary"
 463         role="inputOnly"/>
 464 
 465     <!-- Output a modified record -->
 466     <property
 467         name="updatedAccount"
 468         type="apex://Account"
 469         label="Updated Account"
 470         role="outputOnly"/>
 471 </targetConfig>
 472 ```
 473 
 474 ### Wrapper Class Requirements
 475 
 476 Apex wrapper classes must be **public** and have **public properties**:
 477 
 478 ```apex
 479 public class OrderController {
 480 
 481     // Wrapper class for Flow
 482     public class OrderSummaryWrapper {
 483         @AuraEnabled public String orderId;
 484         @AuraEnabled public String orderName;
 485         @AuraEnabled public Decimal totalAmount;
 486         @AuraEnabled public List<LineItemWrapper> lineItems;
 487         @AuraEnabled public Account customer;
 488     }
 489 
 490     public class LineItemWrapper {
 491         @AuraEnabled public String productName;
 492         @AuraEnabled public Integer quantity;
 493         @AuraEnabled public Decimal unitPrice;
 494     }
 495 
 496     // Invocable method to create the wrapper
 497     @InvocableMethod(label='Get Order Summary')
 498     public static List<OrderSummaryWrapper> getOrderSummary(List<Id> orderIds) {
 499         // Query and build wrapper...
 500     }
 501 }
 502 ```
 503 
 504 ### Using sObjects in LWC
 505 
 506 ```javascript
 507 import { api, LightningElement } from 'lwc';
 508 import { FlowAttributeChangeEvent } from 'lightning/flowSupport';
 509 
 510 export default class AccountEditor extends LightningElement {
 511     // Receive sObject from Flow
 512     @api accountRecord;
 513 
 514     // Track local modifications
 515     _modifiedAccount;
 516 
 517     connectedCallback() {
 518         // Create a working copy
 519         this._modifiedAccount = { ...this.accountRecord };
 520     }
 521 
 522     handleNameChange(event) {
 523         this._modifiedAccount.Name = event.target.value;
 524     }
 525 
 526     handleSave() {
 527         // Send modified record back to Flow
 528         this.dispatchEvent(
 529             new FlowAttributeChangeEvent('updatedAccount', this._modifiedAccount)
 530         );
 531     }
 532 }
 533 ```
 534 
 535 ### Using Wrapper Classes in LWC
 536 
 537 ```javascript
 538 import { api, LightningElement } from 'lwc';
 539 
 540 export default class OrderSummaryViewer extends LightningElement {
 541     @api orderSummary; // apex://OrderController.OrderSummaryWrapper
 542 
 543     get formattedTotal() {
 544         return this.orderSummary?.totalAmount?.toLocaleString('en-US', {
 545             style: 'currency',
 546             currency: 'USD'
 547         });
 548     }
 549 
 550     get lineItems() {
 551         return this.orderSummary?.lineItems || [];
 552     }
 553 
 554     get customerName() {
 555         // Access nested sObject
 556         return this.orderSummary?.customer?.Name || 'Unknown';
 557     }
 558 }
 559 ```
 560 
 561 ### Flow Configuration for apex:// Types
 562 
 563 1. **Create an Invocable Action** that returns your wrapper:
 564    ```apex
 565    @InvocableMethod
 566    public static List<MyWrapper> getData(List<String> inputs) { ... }
 567    ```
 568 
 569 2. **In Flow Builder**, call the Invocable Action before the screen
 570 
 571 3. **Store result** in an Apex-Defined Variable
 572 
 573 4. **Pass to LWC** via the screen component input mapping
 574 
 575 ### Common Patterns
 576 
 577 #### Pattern 1: Record Edit with Validation
 578 
 579 ```javascript
 580 // LWC that receives, edits, and returns an sObject
 581 @api inputRecord;      // apex://Contact (inputOnly)
 582 @api outputRecord;     // apex://Contact (outputOnly)
 583 @api isValid = false;  // Boolean (outputOnly)
 584 
 585 handleFieldChange(event) {
 586     const field = event.target.dataset.field;
 587     this.workingRecord[field] = event.target.value;
 588 
 589     // Validate and update outputs
 590     this.isValid = this.validateRecord();
 591     this.dispatchEvent(new FlowAttributeChangeEvent('outputRecord', this.workingRecord));
 592     this.dispatchEvent(new FlowAttributeChangeEvent('isValid', this.isValid));
 593 }
 594 ```
 595 
 596 #### Pattern 2: Multi-Record Selection
 597 
 598 ```javascript
 599 // Select from a list, output selected items
 600 @api availableRecords;  // apex://Account[] (inputOnly)
 601 @api selectedRecords = []; // apex://Account[] (outputOnly)
 602 
 603 handleSelect(event) {
 604     const id = event.target.dataset.id;
 605     const record = this.availableRecords.find(r => r.Id === id);
 606 
 607     if (record && !this.selectedRecords.find(r => r.Id === id)) {
 608         this.selectedRecords = [...this.selectedRecords, record];
 609         this.dispatchEvent(
 610             new FlowAttributeChangeEvent('selectedRecords', this.selectedRecords)
 611         );
 612     }
 613 }
 614 ```
 615 
 616 #### Pattern 3: Master-Detail Editing
 617 
 618 ```javascript
 619 // Edit parent with nested child records
 620 @api orderWrapper;  // apex://OrderController.OrderWithLines (inputOnly)
 621 @api updatedOrder;  // apex://OrderController.OrderWithLines (outputOnly)
 622 
 623 handleLineItemChange(event) {
 624     const index = event.target.dataset.index;
 625     const field = event.target.dataset.field;
 626     const value = event.target.value;
 627 
 628     // Update nested structure
 629     const updated = JSON.parse(JSON.stringify(this.orderWrapper));
 630     updated.lineItems[index][field] = value;
 631 
 632     // Recalculate totals
 633     updated.totalAmount = updated.lineItems.reduce(
 634         (sum, item) => sum + (item.quantity * item.unitPrice), 0
 635     );
 636 
 637     this.updatedOrder = updated;
 638     this.dispatchEvent(new FlowAttributeChangeEvent('updatedOrder', updated));
 639 }
 640 ```
 641 
 642 ### Limitations
 643 
 644 | Limitation | Workaround |
 645 |------------|------------|
 646 | No `@JsonAccess` support | Ensure wrapper classes don't require JSON annotation |
 647 | 1000 record limit per collection | Paginate or filter in Apex before passing |
 648 | No generic types | Create specific wrapper classes |
 649 | Complex nesting depth | Flatten deep hierarchies |
 650 
 651 ### Debugging Tips
 652 
 653 1. **Console log received data** to verify structure:
 654    ```javascript
 655    connectedCallback() {
 656        console.log('Received from Flow:', JSON.stringify(this.inputWrapper));
 657    }
 658    ```
 659 
 660 2. **Check Apex class visibility** - inner classes need `public` modifier
 661 
 662 3. **Verify @AuraEnabled** on all properties you need to access
 663 
 664 ---
 665 
 666 ## Cross-Skill Integration
 667 
 668 | Integration | See Also |
 669 |-------------|----------|
 670 | Flow → Apex → LWC | [triangle-pattern.md](triangle-pattern.md) |
 671 | Apex @AuraEnabled | [sf-apex/references/best-practices.md](../../sf-apex/references/best-practices.md) |
 672 | Flow Templates | [sf-flow/assets/](../../sf-flow/assets/) |
 673 | Async Notifications | [async-notification-patterns.md](async-notification-patterns.md) |
 674 | State Management | [state-management.md](state-management.md) |
