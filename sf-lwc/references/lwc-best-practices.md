<!-- Parent: sf-lwc/SKILL.md -->
   1 # Lightning Web Components Best Practices
   2 
   3 This guide provides comprehensive best practices for building production-ready LWC components, organized around the **PICKLES Framework** and incorporating advanced patterns from industry experts.
   4 
   5 ---
   6 
   7 ## PICKLES Framework Overview
   8 
   9 The PICKLES Framework provides a structured approach to LWC architecture. Use it as a checklist during component design and implementation.
  10 
  11 ```
  12 🥒 P - Prototype    → Validate ideas with wireframes & mock data
  13 🥒 I - Integrate    → Choose data source (LDS, Apex, GraphQL)
  14 🥒 C - Composition  → Structure component hierarchy & communication
  15 🥒 K - Kinetics     → Handle user interactions & event flow
  16 🥒 L - Libraries    → Leverage platform APIs & base components
  17 🥒 E - Execution    → Optimize performance & lifecycle hooks
  18 🥒 S - Security     → Enforce permissions & data protection
  19 ```
  20 
  21 **Reference**: [PICKLES Framework (Salesforce Ben)](https://www.salesforceben.com/the-ideal-framework-for-architecting-salesforce-lightning-web-components/)
  22 
  23 ---
  24 
  25 ## Component Design Principles
  26 
  27 ### Single Responsibility (PICKLES: Composition)
  28 
  29 Each component should do one thing well.
  30 
  31 ```
  32 ✅ GOOD: accountCard, accountList, accountForm (separate components)
  33 ❌ BAD: accountManager (does display, list, and form in one)
  34 ```
  35 
  36 ### Composition Over Inheritance
  37 
  38 Build complex UIs by composing simple components.
  39 
  40 ```html
  41 <!-- Compose components -->
  42 <template>
  43     <c-page-header title="Accounts"></c-page-header>
  44     <c-account-filters onfilter={handleFilter}></c-account-filters>
  45     <c-account-list accounts={filteredAccounts}></c-account-list>
  46     <c-pagination total={totalCount} onpage={handlePage}></c-pagination>
  47 </template>
  48 ```
  49 
  50 ### Unidirectional Data Flow
  51 
  52 Data flows down (props), events bubble up.
  53 
  54 ```
  55 ┌─────────────────────────────────────────────────────────────────┐
  56 │                    DATA FLOW PATTERN                             │
  57 ├─────────────────────────────────────────────────────────────────┤
  58 │                                                                  │
  59 │   Parent Component                                               │
  60 │   ┌─────────────────────────────────────────────────────────┐   │
  61 │   │  state: accounts = [...]                                │   │
  62 │   │                                                          │   │
  63 │   │  ┌──────────┐     ┌──────────┐     ┌──────────┐        │   │
  64 │   │  │ Child A  │ ←── │ Child B  │ ←── │ Child C  │        │   │
  65 │   │  │          │     │          │     │          │        │   │
  66 │   │  │ @api     │     │ @api     │     │ @api     │        │   │
  67 │   │  │ accounts │     │ selected │     │ details  │        │   │
  68 │   │  └────┬─────┘     └────┬─────┘     └────┬─────┘        │   │
  69 │   │       │                │                │               │   │
  70 │   │       │   Events       │   Events       │   Events      │   │
  71 │   │       └────────────────┴────────────────┘               │   │
  72 │   │              ↑ bubbles to parent                        │   │
  73 │   └─────────────────────────────────────────────────────────┘   │
  74 │                                                                  │
  75 └─────────────────────────────────────────────────────────────────┘
  76 ```
  77 
  78 ---
  79 
  80 ## Data Integration (PICKLES: Integrate)
  81 
  82 ### Data Source Decision Tree
  83 
  84 | Scenario | Recommended Approach |
  85 |----------|---------------------|
  86 | Single record by ID | Lightning Data Service (`getRecord`) |
  87 | Simple record CRUD | `lightning-record-form` / `lightning-record-edit-form` |
  88 | Complex queries | Apex with `@AuraEnabled(cacheable=true)` |
  89 | Related records, filtering | GraphQL wire adapter |
  90 | Real-time updates | Platform Events / Streaming API |
  91 | External data | Named Credentials + Apex callout |
  92 
  93 ### GraphQL vs Apex Decision
  94 
  95 | Use GraphQL When | Use Apex When |
  96 |------------------|---------------|
  97 | Fetching related objects | Complex business logic |
  98 | Client-side filtering | Aggregate queries (COUNT, SUM) |
  99 | Cursor-based pagination | Bulk DML operations |
 100 | Reducing over-fetching | Callouts to external systems |
 101 
 102 ### Wire Service Best Practices
 103 
 104 ```javascript
 105 // Store wire result for refreshApex
 106 wiredAccountsResult;
 107 
 108 @wire(getAccounts, { searchTerm: '$searchTerm' })
 109 wiredAccounts(result) {
 110     this.wiredAccountsResult = result;  // Store for refresh
 111     const { data, error } = result;
 112     if (data) {
 113         this.accounts = data;
 114         this.error = undefined;
 115     } else if (error) {
 116         this.error = this.reduceErrors(error);
 117         this.accounts = [];
 118     }
 119 }
 120 
 121 // Refresh when needed
 122 async handleRefresh() {
 123     await refreshApex(this.wiredAccountsResult);
 124 }
 125 ```
 126 
 127 ### Error Handling Pattern
 128 
 129 ```javascript
 130 // Centralized error reducer
 131 reduceErrors(errors) {
 132     if (!Array.isArray(errors)) {
 133         errors = [errors];
 134     }
 135 
 136     return errors
 137         .filter(error => !!error)
 138         .map(error => {
 139             // UI API errors
 140             if (error.body?.message) return error.body.message;
 141             // JS errors
 142             if (error.message) return error.message;
 143             // GraphQL errors
 144             if (error.graphQLErrors) {
 145                 return error.graphQLErrors.map(e => e.message).join(', ');
 146             }
 147             return JSON.stringify(error);
 148         })
 149         .join('; ');
 150 }
 151 ```
 152 
 153 ---
 154 
 155 ## Event Patterns (PICKLES: Kinetics)
 156 
 157 ### Custom Events
 158 
 159 ```javascript
 160 // Child dispatches event
 161 this.dispatchEvent(new CustomEvent('select', {
 162     detail: { recordId: this.recordId },
 163     bubbles: true,    // Bubbles through DOM
 164     composed: true    // Crosses shadow boundary
 165 }));
 166 
 167 // Parent handles event
 168 handleSelect(event) {
 169     const recordId = event.detail.recordId;
 170 }
 171 ```
 172 
 173 ### Event Naming Conventions
 174 
 175 ```
 176 ✅ GOOD                    ❌ BAD
 177 ────────────────────────   ────────────────────────
 178 onselect                   onSelectItem
 179 onrecordchange             on-record-change
 180 onsave                     onSaveClicked
 181 onerror                    onErrorOccurred
 182 ```
 183 
 184 ### When to Use LMS vs Events
 185 
 186 | Scenario | Use |
 187 |----------|-----|
 188 | Parent-child communication | Custom events |
 189 | Sibling components (same parent) | Events via parent |
 190 | Components on different parts of page | Lightning Message Service |
 191 | LWC to Aura communication | LMS |
 192 | LWC to Visualforce | LMS |
 193 
 194 ### Debouncing Pattern
 195 
 196 ```javascript
 197 delayTimeout;
 198 
 199 handleSearch(event) {
 200     const searchTerm = event.target.value;
 201     clearTimeout(this.delayTimeout);
 202 
 203     this.delayTimeout = setTimeout(() => {
 204         this.searchTerm = searchTerm;
 205     }, 300);  // 300ms debounce
 206 }
 207 ```
 208 
 209 ---
 210 
 211 ## Spread Patterns & Destructuring
 212 
 213 ### lwc:spread Directive
 214 
 215 The `lwc:spread` directive dynamically spreads object properties as component attributes. Useful for reducing boilerplate and enabling dynamic attribute binding.
 216 
 217 **Reference**: [Saurabh Samir - lwc:spread Directive](https://medium.com/@saurabh.samirs)
 218 
 219 #### Basic Usage
 220 
 221 ```html
 222 <!-- Without lwc:spread (verbose) -->
 223 <lightning-button
 224     label={buttonLabel}
 225     variant={buttonVariant}
 226     disabled={isDisabled}
 227     onclick={handleClick}>
 228 </lightning-button>
 229 
 230 <!-- With lwc:spread (dynamic) -->
 231 <lightning-button lwc:spread={buttonAttributes} onclick={handleClick}></lightning-button>
 232 ```
 233 
 234 ```javascript
 235 get buttonAttributes() {
 236     return {
 237         label: this.buttonLabel,
 238         variant: this.isImportant ? 'brand' : 'neutral',
 239         disabled: this.isProcessing
 240     };
 241 }
 242 ```
 243 
 244 #### lwc:spread vs @api Object Binding
 245 
 246 | Approach | Use When | Reactivity |
 247 |----------|----------|------------|
 248 | `lwc:spread={obj}` | Passing multiple attributes dynamically | Re-renders on object change |
 249 | `@api config` | Passing structured data to custom component | Must spread in child |
 250 | Individual `@api` props | Simple, known properties | Each prop triggers render |
 251 
 252 #### Conditional Attribute Spreading
 253 
 254 ```javascript
 255 get inputAttributes() {
 256     const attrs = {
 257         label: 'Search',
 258         type: 'text',
 259         value: this.searchTerm
 260     };
 261 
 262     // Conditionally add attributes
 263     if (this.isRequired) {
 264         attrs.required = true;
 265     }
 266 
 267     if (this.maxLength) {
 268         attrs['max-length'] = this.maxLength;
 269     }
 270 
 271     return attrs;
 272 }
 273 ```
 274 
 275 ```html
 276 <lightning-input lwc:spread={inputAttributes} onchange={handleChange}></lightning-input>
 277 ```
 278 
 279 #### Event Handlers with lwc:spread
 280 
 281 **Important**: Event handlers must be bound separately, not spread:
 282 
 283 ```html
 284 <!-- ✅ CORRECT: Event handler separate from spread -->
 285 <lightning-button lwc:spread={buttonProps} onclick={handleClick}></lightning-button>
 286 
 287 <!-- ❌ INCORRECT: onclick in spread object won't work -->
 288 <!-- buttonProps = { label: 'Save', onclick: this.handleClick } -->
 289 ```
 290 
 291 ### lwc:on Directive (Spring '26 - API 66.0)
 292 
 293 The `lwc:on` directive solves the limitation above by enabling **dynamic event binding** directly from JavaScript. It allows you to bind multiple event handlers at runtime.
 294 
 295 **Requires**: API 66.0+ (Spring '26)
 296 
 297 #### Basic Usage
 298 
 299 ```javascript
 300 // component.js
 301 export default class DynamicEventComponent extends LightningElement {
 302     // Define event handlers as object properties
 303     eventHandlers = {
 304         click: this.handleClick.bind(this),
 305         mouseover: this.handleMouseOver.bind(this),
 306         focus: this.handleFocus.bind(this)
 307     };
 308 
 309     handleClick() {
 310         console.log('Element clicked!');
 311     }
 312 
 313     handleMouseOver() {
 314         console.log('Mouse over!');
 315     }
 316 
 317     handleFocus() {
 318         console.log('Element focused!');
 319     }
 320 }
 321 ```
 322 
 323 ```html
 324 <!-- template.html -->
 325 <template>
 326     <!-- Bind multiple event handlers dynamically -->
 327     <button lwc:on={eventHandlers}>Click Me</button>
 328 </template>
 329 ```
 330 
 331 #### Combining lwc:spread and lwc:on
 332 
 333 For fully dynamic components, combine both directives:
 334 
 335 ```javascript
 336 // component.js
 337 export default class FullyDynamicButton extends LightningElement {
 338     // Properties via lwc:spread
 339     buttonAttributes = {
 340         label: 'Save',
 341         variant: 'brand',
 342         disabled: false
 343     };
 344 
 345     // Events via lwc:on
 346     buttonEvents = {
 347         click: this.handleClick.bind(this),
 348         focus: this.handleFocus.bind(this)
 349     };
 350 
 351     handleClick() {
 352         this.dispatchEvent(new CustomEvent('save'));
 353     }
 354 
 355     handleFocus() {
 356         console.log('Button focused');
 357     }
 358 }
 359 ```
 360 
 361 ```html
 362 <!-- template.html -->
 363 <template>
 364     <!-- Best of both worlds: dynamic props AND dynamic events -->
 365     <lightning-button
 366         lwc:spread={buttonAttributes}
 367         lwc:on={buttonEvents}>
 368     </lightning-button>
 369 </template>
 370 ```
 371 
 372 #### Dynamic Event Handlers from @api
 373 
 374 Pass event handler configurations from parent components:
 375 
 376 ```javascript
 377 // childComponent.js
 378 export default class ChildComponent extends LightningElement {
 379     @api eventConfig; // { click: handler, change: handler }
 380 
 381     get resolvedHandlers() {
 382         // Ensure handlers are properly bound
 383         const handlers = {};
 384         if (this.eventConfig) {
 385             Object.entries(this.eventConfig).forEach(([event, handler]) => {
 386                 handlers[event] = typeof handler === 'function' ? handler : () => {};
 387             });
 388         }
 389         return handlers;
 390     }
 391 }
 392 ```
 393 
 394 ```html
 395 <!-- childComponent.html -->
 396 <template>
 397     <div lwc:on={resolvedHandlers}>
 398         <slot></slot>
 399     </div>
 400 </template>
 401 ```
 402 
 403 #### Removing Event Listeners
 404 
 405 Remove specific event listeners by omitting them from the object:
 406 
 407 ```javascript
 408 // Toggle mouseover handler on/off
 409 toggleHoverHandler() {
 410     if (this._hoverEnabled) {
 411         // Remove mouseover by omitting it
 412         this.eventHandlers = {
 413             click: this.handleClick.bind(this)
 414         };
 415     } else {
 416         // Add mouseover back
 417         this.eventHandlers = {
 418             click: this.handleClick.bind(this),
 419             mouseover: this.handleMouseOver.bind(this)
 420         };
 421     }
 422     this._hoverEnabled = !this._hoverEnabled;
 423 }
 424 ```
 425 
 426 #### lwc:spread vs lwc:on Comparison
 427 
 428 | Directive | Purpose | Use Case |
 429 |-----------|---------|----------|
 430 | `lwc:spread` | Dynamic **properties/attributes** | Pass label, variant, disabled dynamically |
 431 | `lwc:on` | Dynamic **event handlers** | Bind click, change, custom events dynamically |
 432 | Both together | Fully dynamic configuration | Reusable wrapper components, dynamic UIs |
 433 
 434 **Important Notes**:
 435 - Do NOT mutate the object passed to `lwc:on` - create a new object to update handlers
 436 - Event type names should be lowercase without the `on` prefix (use `click` not `onclick`)
 437 - Always use `.bind(this)` or arrow functions to preserve context
 438 
 439 ### Object Spread & Destructuring
 440 
 441 Modern JavaScript patterns for cleaner data handling in LWC.
 442 
 443 #### Object Spread for Config Merging
 444 
 445 ```javascript
 446 // Default + user config pattern
 447 const defaultConfig = {
 448     pageSize: 10,
 449     sortField: 'Name',
 450     sortDirection: 'ASC'
 451 };
 452 
 453 get tableConfig() {
 454     return {
 455         ...defaultConfig,
 456         ...this.userConfig  // User config overrides defaults
 457     };
 458 }
 459 ```
 460 
 461 #### Destructuring with Defaults
 462 
 463 ```javascript
 464 // Extract values with fallbacks
 465 handleRecordLoad(record) {
 466     const {
 467         Name = 'Unknown',
 468         Industry = 'Not Specified',
 469         AnnualRevenue = 0
 470     } = record.fields;
 471 
 472     this.accountName = Name.value;
 473     this.industry = Industry.value;
 474     this.revenue = AnnualRevenue.value;
 475 }
 476 ```
 477 
 478 #### Nested Destructuring
 479 
 480 ```javascript
 481 // Deep extraction in single statement
 482 processResult(result) {
 483     const {
 484         data: {
 485             record: {
 486                 fields: { Name, BillingCity }
 487             }
 488         },
 489         error
 490     } = result;
 491 
 492     if (error) {
 493         this.handleError(error);
 494         return;
 495     }
 496 
 497     this.name = Name.value;
 498     this.city = BillingCity.value;
 499 }
 500 ```
 501 
 502 #### Array Spread Patterns
 503 
 504 ```javascript
 505 // Immutable array updates (required for LWC reactivity)
 506 addItem(newItem) {
 507     this.items = [...this.items, newItem];  // Append
 508 }
 509 
 510 removeItem(index) {
 511     this.items = [
 512         ...this.items.slice(0, index),
 513         ...this.items.slice(index + 1)
 514     ];  // Remove at index
 515 }
 516 
 517 updateItem(index, updates) {
 518     this.items = this.items.map((item, i) =>
 519         i === index ? { ...item, ...updates } : item
 520     );  // Update at index
 521 }
 522 ```
 523 
 524 #### Parameter Spreading in Apex Calls
 525 
 526 ```javascript
 527 async handleSubmit() {
 528     const result = await createRecord({
 529         ...this.recordData,
 530         CreatedBy__c: this.currentUserId,
 531         Status__c: 'Pending'
 532     });
 533 }
 534 ```
 535 
 536 ### When to Use Each Pattern
 537 
 538 | Pattern | Best For | Avoid When |
 539 |---------|----------|------------|
 540 | `lwc:spread` | Many dynamic attributes, base component wrappers | Need event binding, simple static props |
 541 | Object spread | Config merging, immutable updates | Deep objects (consider structuredClone) |
 542 | Destructuring | Extracting multiple values, API responses | Simple single-property access |
 543 | Array spread | Adding/removing items immutably | Large arrays (performance concern) |
 544 
 545 ---
 546 
 547 ## Complex Template Expressions (Spring '26 Beta - API 66.0)
 548 
 549 Spring '26 introduces **complex template expressions**, enabling JavaScript expressions directly in templates. This was previously limited to simple property and getter bindings.
 550 
 551 > ⚠️ **Beta Feature**: Use getters in production until this becomes GA. Document any complex expressions for future migration.
 552 
 553 ### Before vs After
 554 
 555 ```html
 556 <!-- BEFORE Spring '26: Required getters for any logic -->
 557 <template>
 558     <!-- Simple property binding only -->
 559     <template lwc:if={isValid}>...</template>
 560 
 561     <!-- Complex conditions needed a getter -->
 562     <template lwc:if={showLoadingState}>...</template>
 563 </template>
 564 ```
 565 
 566 ```javascript
 567 // Required getter in JS
 568 get showLoadingState() {
 569     return this.isLoading && this.items.length === 0;
 570 }
 571 ```
 572 
 573 ```html
 574 <!-- AFTER Spring '26 (Beta): Complex expressions in template -->
 575 <template>
 576     <!-- Logical operators -->
 577     <template lwc:if={!isLoading && items.length > 0}>
 578         <c-item-list items={items}></c-item-list>
 579     </template>
 580 
 581     <!-- Optional chaining -->
 582     <template lwc:if={user?.permissions?.canEdit}>
 583         <lightning-button label="Edit"></lightning-button>
 584     </template>
 585 
 586     <!-- Arithmetic expressions -->
 587     <span class="slds-text-body_small">
 588         Total: ${total * taxRate}
 589     </span>
 590 
 591     <!-- Comparison operators -->
 592     <template lwc:if={items.length >= minItems}>
 593         <c-pagination></c-pagination>
 594     </template>
 595 </template>
 596 ```
 597 
 598 ### Supported Expression Types
 599 
 600 | Expression Type | Example | Notes |
 601 |-----------------|---------|-------|
 602 | **Logical NOT** | `{!isLoading}` | Negation |
 603 | **Logical AND** | `{a && b}` | Short-circuit evaluation |
 604 | **Logical OR** | `{a \|\| b}` | Short-circuit evaluation |
 605 | **Comparison** | `{count > 0}`, `{status === 'active'}` | `==`, `===`, `!=`, `!==`, `<`, `>`, `<=`, `>=` |
 606 | **Arithmetic** | `{price * quantity}` | `+`, `-`, `*`, `/`, `%` |
 607 | **Optional Chaining** | `{user?.profile?.name}` | Safe property access |
 608 | **Nullish Coalescing** | `{value ?? 'default'}` | Default for null/undefined |
 609 | **Ternary** | `{isActive ? 'Yes' : 'No'}` | Conditional value |
 610 | **Array Access** | `{items[0]}` | Index-based access |
 611 | **String Concatenation** | `{firstName + ' ' + lastName}` | String joining |
 612 
 613 ### Best Practices for Complex Expressions
 614 
 615 ```html
 616 <!-- ✅ GOOD: Simple inline logic -->
 617 <template lwc:if={!isLoading && hasData}>
 618     ...
 619 </template>
 620 
 621 <!-- ✅ GOOD: Optional chaining for safety -->
 622 <span>{account?.Owner?.Name}</span>
 623 
 624 <!-- ⚠️ CAUTION: Keep expressions readable -->
 625 <!-- If expression is long, consider a getter for maintainability -->
 626 <template lwc:if={isEditable && hasPermission && !isLocked && status === 'draft'}>
 627     <!-- Consider: get canEdit() { return ...; } -->
 628 </template>
 629 
 630 <!-- ❌ AVOID: Side effects in expressions -->
 631 <!-- Don't call methods that modify state -->
 632 ```
 633 
 634 ### Migration Strategy
 635 
 636 1. **New code**: Use complex expressions for simple conditions
 637 2. **Existing code**: Keep getters that have unit tests
 638 3. **Complex logic**: Continue using getters for maintainability
 639 4. **Document**: Mark complex expressions in templates for review when GA
 640 
 641 ### Limitations (Beta)
 642 
 643 - No function calls in expressions (use getters)
 644 - No template literals with `${}` interpolation
 645 - Cannot reference `this` directly
 646 - No destructuring in expressions
 647 
 648 ---
 649 
 650 ## Performance Optimization (PICKLES: Execution)
 651 
 652 ### Lifecycle Hook Guidance
 653 
 654 | Hook | When to Use | Avoid |
 655 |------|-------------|-------|
 656 | `constructor()` | Initialize properties | DOM access (not ready) |
 657 | `connectedCallback()` | Subscribe to events, fetch data | Heavy processing |
 658 | `renderedCallback()` | DOM-dependent logic | Infinite loops, property changes |
 659 | `disconnectedCallback()` | Cleanup subscriptions/listeners | Async operations |
 660 
 661 ### Lazy Loading
 662 
 663 ```html
 664 <!-- Only render when needed -->
 665 <template lwc:if={showDetails}>
 666     <c-expensive-component record-id={recordId}></c-expensive-component>
 667 </template>
 668 ```
 669 
 670 ### Efficient Rendering
 671 
 672 ```javascript
 673 // Bad: Creates new array every render
 674 get filteredItems() {
 675     return this.items.filter(item => item.active);
 676 }
 677 
 678 // Good: Cache the result
 679 _filteredItems;
 680 _itemsHash;
 681 
 682 get filteredItems() {
 683     const currentHash = JSON.stringify(this.items);
 684     if (currentHash !== this._itemsHash) {
 685         this._filteredItems = this.items.filter(item => item.active);
 686         this._itemsHash = currentHash;
 687     }
 688     return this._filteredItems;
 689 }
 690 ```
 691 
 692 ### Virtual Scrolling
 693 
 694 Use `lightning-datatable` with `enable-infinite-loading` for large datasets instead of rendering all items.
 695 
 696 ---
 697 
 698 ## Advanced Jest Testing Patterns
 699 
 700 Based on [James Simone's advanced testing patterns](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/).
 701 
 702 ### Render Cycle Helper
 703 
 704 LWC re-rendering is asynchronous. Use this helper to document and await render cycles:
 705 
 706 ```javascript
 707 // testUtils.js
 708 export const runRenderingLifecycle = async (reasons = ['render']) => {
 709     while (reasons.length > 0) {
 710         await Promise.resolve(reasons.pop());
 711     }
 712 };
 713 
 714 // Usage in tests
 715 it('updates after property change', async () => {
 716     const element = createElement('c-example', { is: Example });
 717     document.body.appendChild(element);
 718 
 719     element.greeting = 'new value';
 720     await runRenderingLifecycle(['property change', 'render']);
 721 
 722     expect(element.shadowRoot.querySelector('div').textContent).toBe('new value');
 723 });
 724 ```
 725 
 726 ### Proxy Unboxing (Lightning Web Security)
 727 
 728 Lightning Web Security proxifies objects. Unbox them for assertions:
 729 
 730 ```javascript
 731 // LWS proxifies complex objects - unbox for comparison
 732 const unboxedData = JSON.parse(JSON.stringify(component.data));
 733 expect(unboxedData).toEqual(expectedData);
 734 ```
 735 
 736 ### DOM Cleanup Pattern
 737 
 738 Clean up after each test to prevent state bleed:
 739 
 740 ```javascript
 741 describe('c-my-component', () => {
 742     afterEach(() => {
 743         // Clean up DOM
 744         while (document.body.firstChild) {
 745             document.body.removeChild(document.body.firstChild);
 746         }
 747         jest.clearAllMocks();
 748     });
 749 });
 750 ```
 751 
 752 ### ResizeObserver Polyfill
 753 
 754 Some components use ResizeObserver. Add polyfill in jest.setup.js:
 755 
 756 ```javascript
 757 // jest.setup.js
 758 if (!window.ResizeObserver) {
 759     window.ResizeObserver = class ResizeObserver {
 760         constructor(callback) {
 761             this.callback = callback;
 762         }
 763         observe() {}
 764         unobserve() {}
 765         disconnect() {}
 766     };
 767 }
 768 ```
 769 
 770 ### Mocking Apex Methods
 771 
 772 ```javascript
 773 jest.mock('@salesforce/apex/MyController.getData', () => ({
 774     default: jest.fn()
 775 }), { virtual: true });
 776 
 777 // In test
 778 import getData from '@salesforce/apex/MyController.getData';
 779 
 780 it('displays data', async () => {
 781     getData.mockResolvedValue(MOCK_DATA);
 782     // ... test code
 783 });
 784 ```
 785 
 786 ---
 787 
 788 ## Security Best Practices (PICKLES: Security)
 789 
 790 ### FLS Enforcement
 791 
 792 ```apex
 793 // Always use SECURITY_ENFORCED or stripInaccessible
 794 @AuraEnabled(cacheable=true)
 795 public static List<Account> getAccounts() {
 796     return [SELECT Id, Name FROM Account WITH SECURITY_ENFORCED];
 797 }
 798 
 799 // For DML operations
 800 SObjectAccessDecision decision = Security.stripInaccessible(
 801     AccessType.CREATABLE,
 802     records
 803 );
 804 insert decision.getRecords();
 805 ```
 806 
 807 ### Input Sanitization
 808 
 809 ```apex
 810 // Apex should escape user input
 811 String searchKey = '%' + String.escapeSingleQuotes(searchTerm) + '%';
 812 ```
 813 
 814 ### XSS Prevention
 815 
 816 LWC automatically escapes content in templates. Never bypass this.
 817 
 818 ```html
 819 <!-- Safe: LWC auto-escapes -->
 820 <p>{userInput}</p>
 821 ```
 822 
 823 ---
 824 
 825 ## Accessibility (a11y)
 826 
 827 ### Required Practices
 828 
 829 | Element | Requirement |
 830 |---------|-------------|
 831 | Buttons | `label` or `aria-label` |
 832 | Icons | `alternative-text` |
 833 | Form inputs | Associated `<label>` |
 834 | Dynamic content | `aria-live` region |
 835 | Loading states | `aria-busy="true"` |
 836 
 837 ### Keyboard Navigation
 838 
 839 ```javascript
 840 handleKeyDown(event) {
 841     switch (event.key) {
 842         case 'Enter':
 843         case ' ':
 844             this.handleSelect(event);
 845             break;
 846         case 'Escape':
 847             this.handleClose();
 848             break;
 849         case 'ArrowDown':
 850             this.focusNext();
 851             event.preventDefault();
 852             break;
 853     }
 854 }
 855 ```
 856 
 857 ### Focus Trap Pattern (for Modals)
 858 
 859 Based on [James Simone's modal pattern](https://www.jamessimone.net/blog/joys-of-apex/lwc-composable-modal/):
 860 
 861 ```javascript
 862 _focusableElements = [];
 863 
 864 _onOpen() {
 865     // Collect focusable elements
 866     this._focusableElements = [
 867         ...this.querySelectorAll('.focusable'),
 868         ...this.template.querySelectorAll('lightning-button, button, [tabindex="0"]')
 869     ].filter(el => !el.disabled);
 870 
 871     // Focus first element
 872     this._focusableElements[0]?.focus();
 873 
 874     // Add ESC handler
 875     window.addEventListener('keyup', this._handleKeyUp);
 876 }
 877 
 878 _handleKeyUp = (event) => {
 879     if (event.code === 'Escape') {
 880         this.close();
 881     }
 882 }
 883 
 884 disconnectedCallback() {
 885     window.removeEventListener('keyup', this._handleKeyUp);
 886 }
 887 ```
 888 
 889 ---
 890 
 891 ## SLDS 2 & Dark Mode
 892 
 893 ### Dark Mode Checklist
 894 
 895 - [ ] No hardcoded hex colors (`#FFFFFF`, `#333333`)
 896 - [ ] No hardcoded RGB/RGBA values
 897 - [ ] All colors use CSS variables (`var(--slds-g-color-*)`)
 898 - [ ] Fallback values provided for SLDS 1 compatibility
 899 - [ ] Icons use SLDS utility icons (auto-adjust for dark mode)
 900 
 901 ### SLDS 1 → SLDS 2 Migration
 902 
 903 ```css
 904 /* BEFORE (SLDS 1 - Deprecated) */
 905 .my-card {
 906     background-color: #ffffff;
 907     color: #333333;
 908 }
 909 
 910 /* AFTER (SLDS 2 - Dark Mode Ready) */
 911 .my-card {
 912     background-color: var(--slds-g-color-surface-container-1, #ffffff);
 913     color: var(--slds-g-color-on-surface, #181818);
 914 }
 915 ```
 916 
 917 ### Key Global Styling Hooks
 918 
 919 | Category | SLDS 2 Variable |
 920 |----------|-----------------|
 921 | Surface | `--slds-g-color-surface-1` to `-4` |
 922 | Text | `--slds-g-color-on-surface` |
 923 | Border | `--slds-g-color-border-1`, `-2` |
 924 | Spacing | `--slds-g-spacing-0` to `-12` |
 925 
 926 **Important**: `--slds-c-*` (component-level hooks) are NOT supported in SLDS 2 yet.
 927 
 928 ---
 929 
 930 ## Testing Checklist
 931 
 932 ### Unit Test Coverage
 933 
 934 - [ ] Component renders without errors
 935 - [ ] Data displays correctly when loaded
 936 - [ ] Error state displays when fetch fails
 937 - [ ] Empty state displays when no data
 938 - [ ] Events dispatch with correct payload
 939 - [ ] User interactions work correctly
 940 - [ ] Loading states are shown/hidden appropriately
 941 
 942 ### Manual Testing
 943 
 944 - [ ] Works in Lightning Experience
 945 - [ ] Works in Salesforce Mobile
 946 - [ ] Works in Experience Cloud (if targeted)
 947 - [ ] Works in Dark Mode (SLDS 2)
 948 - [ ] Keyboard navigation works
 949 - [ ] Screen reader announces properly
 950 - [ ] No console errors
 951 - [ ] Performance acceptable with real data
 952 
 953 ---
 954 
 955 ## Common Mistakes
 956 
 957 ### 1. Modifying @api Properties
 958 
 959 ```javascript
 960 // ❌ BAD
 961 @api items;
 962 handleClick() {
 963     this.items.push(newItem);  // Mutation!
 964 }
 965 
 966 // ✅ GOOD
 967 handleClick() {
 968     this.items = [...this.items, newItem];
 969 }
 970 ```
 971 
 972 ### 2. Forgetting to Clean Up
 973 
 974 ```javascript
 975 // ❌ BAD: Memory leak
 976 connectedCallback() {
 977     this.subscription = subscribe(...);
 978 }
 979 
 980 // ✅ GOOD
 981 disconnectedCallback() {
 982     unsubscribe(this.subscription);
 983 }
 984 ```
 985 
 986 ### 3. Wire with Non-Reactive Parameters
 987 
 988 ```javascript
 989 // ❌ BAD
 990 let recordId = '001xxx';
 991 @wire(getRecord, { recordId: recordId })
 992 
 993 // ✅ GOOD
 994 @api recordId;
 995 @wire(getRecord, { recordId: '$recordId' })
 996 ```
 997 
 998 ---
 999 
1000 ## Resources
1001 
1002 - [PICKLES Framework (Salesforce Ben)](https://www.salesforceben.com/the-ideal-framework-for-architecting-salesforce-lightning-web-components/)
1003 - [LWC Recipes (GitHub)](https://github.com/trailheadapps/lwc-recipes)
1004 - [SLDS 2 Transition Guide](https://www.lightningdesignsystem.com/2e1ef8501/p/8184ad-transition-to-slds-2)
1005 - [James Simone - Advanced Jest Testing](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/)
1006 - [James Simone - Composable Modal](https://www.jamessimone.net/blog/joys-of-apex/lwc-composable-modal/)
1007 - [SLDS Styling Hooks](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-custom-properties.html)
