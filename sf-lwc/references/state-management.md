<!-- Parent: sf-lwc/SKILL.md -->
   1 <!-- TIER: 3 | DETAILED REFERENCE -->
   2 <!-- Read after: SKILL.md -->
   3 <!-- Purpose: Modern state management patterns using @lwc/state -->
   4 
   5 # LWC State Management
   6 
   7 > Modern state management patterns for Lightning Web Components using @lwc/state and Platform State Managers
   8 
   9 ## Overview
  10 
  11 LWC state management has evolved beyond simple reactive properties. This guide covers modern patterns for managing complex state across components, including the `@lwc/state` library and Salesforce Platform State Managers.
  12 
  13 ```
  14 ┌─────────────────────────────────────────────────────────────────────────────┐
  15 │                    STATE MANAGEMENT SPECTRUM                                 │
  16 ├─────────────────────────────────────────────────────────────────────────────┤
  17 │                                                                             │
  18 │  SIMPLE ◄────────────────────────────────────────────────────────► COMPLEX │
  19 │                                                                             │
  20 │  @track/@api      Singleton Store      @lwc/state       Platform State     │
  21 │  (Component)      (Cross-Component)    (Full Library)   (Record/Layout)    │
  22 │                                                                             │
  23 │  ┌─────────┐      ┌─────────────┐      ┌────────────┐   ┌───────────────┐  │
  24 │  │ Single  │      │ Shared      │      │ Atoms +    │   │ Record Data + │  │
  25 │  │ Component│      │ Across      │      │ Computed + │   │ Layout State │  │
  26 │  │ State   │      │ Components  │      │ Actions    │   │ (Platform)   │  │
  27 │  └─────────┘      └─────────────┘      └────────────┘   └───────────────┘  │
  28 │                                                                             │
  29 │  Use when:         Use when:            Use when:        Use when:          │
  30 │  - Local state     - Shared cart        - Complex UI     - Record pages     │
  31 │  - Form fields     - User prefs         - Async state    - Flexipages       │
  32 │  - UI toggles      - Cached data        - Derived data   - Tab persistence  │
  33 │                                                                             │
  34 └─────────────────────────────────────────────────────────────────────────────┘
  35 ```
  36 
  37 ---
  38 
  39 ## When to Use Each Pattern
  40 
  41 | Pattern | Complexity | Scope | Use Case |
  42 |---------|------------|-------|----------|
  43 | **@track / reactive properties** | Low | Component | Form inputs, toggles, local UI state |
  44 | **Singleton Store** | Medium | Cross-component | Shopping cart, filters, user preferences |
  45 | **@lwc/state** | Medium-High | Cross-component | Complex forms, async state, computed values |
  46 | **Platform State Managers** | High | Page/Record | Record pages, layout-aware components |
  47 
  48 ---
  49 
  50 ## Pattern 1: Reactive Properties (Component-Level)
  51 
  52 ### Standard Reactivity
  53 
  54 ```javascript
  55 import { LightningElement } from 'lwc';
  56 
  57 export default class SimpleState extends LightningElement {
  58     // Reactive by default (primitive types and objects)
  59     counter = 0;
  60     isActive = false;
  61     user = { name: 'John', email: 'john@example.com' };
  62 
  63     // Object reassignment triggers reactivity
  64     updateUser() {
  65         // ✅ Works - new object reference
  66         this.user = { ...this.user, name: 'Jane' };
  67 
  68         // ❌ Won't trigger rerender - same reference
  69         // this.user.name = 'Jane';
  70     }
  71 
  72     increment() {
  73         this.counter++; // ✅ Primitive assignment is reactive
  74     }
  75 }
  76 ```
  77 
  78 ### Getters (Computed Properties)
  79 
  80 ```javascript
  81 export default class ComputedExample extends LightningElement {
  82     firstName = '';
  83     lastName = '';
  84     items = [];
  85 
  86     // Computed property - recalculates when dependencies change
  87     get fullName() {
  88         return `${this.firstName} ${this.lastName}`.trim();
  89     }
  90 
  91     get hasItems() {
  92         return this.items.length > 0;
  93     }
  94 
  95     get totalPrice() {
  96         return this.items.reduce((sum, item) => sum + item.price, 0);
  97     }
  98 
  99     get formattedPrice() {
 100         return new Intl.NumberFormat('en-US', {
 101             style: 'currency',
 102             currency: 'USD'
 103         }).format(this.totalPrice);
 104     }
 105 }
 106 ```
 107 
 108 ---
 109 
 110 ## Pattern 2: Singleton Store (Cross-Component State)
 111 
 112 For sharing state across components without platform dependencies.
 113 
 114 ### Store Module (`store.js`)
 115 
 116 ```javascript
 117 /**
 118  * Singleton store for cross-component state management.
 119  *
 120  * Usage:
 121  * import store from 'c/store';
 122  *
 123  * // Read state
 124  * const cart = store.getState('cart');
 125  *
 126  * // Update state
 127  * store.setState('cart', { items: [...cart.items, newItem] });
 128  *
 129  * // Subscribe to changes
 130  * store.subscribe('cart', (newCart) => { this.cart = newCart; });
 131  */
 132 
 133 // Private state container
 134 const state = new Map();
 135 
 136 // Subscribers by key
 137 const subscribers = new Map();
 138 
 139 // Get current state for a key
 140 function getState(key) {
 141     return state.get(key);
 142 }
 143 
 144 // Set state and notify subscribers
 145 function setState(key, value) {
 146     const oldValue = state.get(key);
 147     state.set(key, value);
 148 
 149     // Notify all subscribers for this key
 150     const keySubscribers = subscribers.get(key) || [];
 151     keySubscribers.forEach(callback => {
 152         try {
 153             callback(value, oldValue);
 154         } catch (e) {
 155             console.error('Store subscriber error:', e);
 156         }
 157     });
 158 }
 159 
 160 // Subscribe to state changes
 161 function subscribe(key, callback) {
 162     if (!subscribers.has(key)) {
 163         subscribers.set(key, []);
 164     }
 165     subscribers.get(key).push(callback);
 166 
 167     // Return unsubscribe function
 168     return () => {
 169         const keySubscribers = subscribers.get(key) || [];
 170         const index = keySubscribers.indexOf(callback);
 171         if (index > -1) {
 172             keySubscribers.splice(index, 1);
 173         }
 174     };
 175 }
 176 
 177 // Initialize state with default values
 178 function initState(key, defaultValue) {
 179     if (!state.has(key)) {
 180         state.set(key, defaultValue);
 181     }
 182     return state.get(key);
 183 }
 184 
 185 // Clear state (useful for testing)
 186 function clearState() {
 187     state.clear();
 188     subscribers.clear();
 189 }
 190 
 191 export default {
 192     getState,
 193     setState,
 194     subscribe,
 195     initState,
 196     clearState
 197 };
 198 ```
 199 
 200 ### Using the Store
 201 
 202 ```javascript
 203 // cartManager.js
 204 import { LightningElement } from 'lwc';
 205 import store from 'c/store';
 206 
 207 export default class CartManager extends LightningElement {
 208     cart = { items: [], total: 0 };
 209     unsubscribe;
 210 
 211     connectedCallback() {
 212         // Initialize cart state
 213         this.cart = store.initState('cart', { items: [], total: 0 });
 214 
 215         // Subscribe to cart changes from other components
 216         this.unsubscribe = store.subscribe('cart', (newCart) => {
 217             this.cart = newCart;
 218         });
 219     }
 220 
 221     disconnectedCallback() {
 222         // Clean up subscription
 223         if (this.unsubscribe) {
 224             this.unsubscribe();
 225         }
 226     }
 227 
 228     addItem(event) {
 229         const item = event.detail;
 230         const currentCart = store.getState('cart');
 231 
 232         const newCart = {
 233             items: [...currentCart.items, item],
 234             total: currentCart.total + item.price
 235         };
 236 
 237         store.setState('cart', newCart);
 238     }
 239 }
 240 ```
 241 
 242 ---
 243 
 244 ## Pattern 3: @lwc/state Library
 245 
 246 The `@lwc/state` library provides reactive state primitives with automatic dependency tracking.
 247 
 248 ### Installation
 249 
 250 ```bash
 251 # If using npm in LWC project
 252 npm install @lwc/state
 253 ```
 254 
 255 ### Core Concepts
 256 
 257 #### Atoms (Primitive State)
 258 
 259 ```javascript
 260 import { atom, computed } from '@lwc/state';
 261 
 262 // Create atoms for primitive state
 263 const countAtom = atom(0);
 264 const nameAtom = atom('');
 265 const itemsAtom = atom([]);
 266 
 267 // Read value
 268 console.log(countAtom.value); // 0
 269 
 270 // Write value - triggers reactivity
 271 countAtom.value = 5;
 272 
 273 // Reset to initial value
 274 countAtom.reset();
 275 ```
 276 
 277 #### Computed (Derived State)
 278 
 279 ```javascript
 280 import { atom, computed } from '@lwc/state';
 281 
 282 const priceAtom = atom(100);
 283 const quantityAtom = atom(2);
 284 const taxRateAtom = atom(0.08);
 285 
 286 // Computed automatically recalculates when dependencies change
 287 const subtotal = computed(() => priceAtom.value * quantityAtom.value);
 288 const tax = computed(() => subtotal.value * taxRateAtom.value);
 289 const total = computed(() => subtotal.value + tax.value);
 290 
 291 console.log(total.value); // 216 (100 * 2 * 1.08)
 292 
 293 // Update a dependency - all computed values update
 294 priceAtom.value = 150;
 295 console.log(total.value); // 324 (150 * 2 * 1.08)
 296 ```
 297 
 298 #### Actions (State Mutations)
 299 
 300 ```javascript
 301 import { atom, action } from '@lwc/state';
 302 
 303 const cartAtom = atom({ items: [], total: 0 });
 304 
 305 // Actions encapsulate state mutations
 306 const addToCart = action((item) => {
 307     const cart = cartAtom.value;
 308     cartAtom.value = {
 309         items: [...cart.items, item],
 310         total: cart.total + item.price
 311     };
 312 });
 313 
 314 const removeFromCart = action((itemId) => {
 315     const cart = cartAtom.value;
 316     const item = cart.items.find(i => i.id === itemId);
 317     cartAtom.value = {
 318         items: cart.items.filter(i => i.id !== itemId),
 319         total: cart.total - (item?.price || 0)
 320     };
 321 });
 322 
 323 const clearCart = action(() => {
 324     cartAtom.reset();
 325 });
 326 ```
 327 
 328 ### LWC Integration
 329 
 330 ```javascript
 331 import { LightningElement } from 'lwc';
 332 import { atom, computed } from '@lwc/state';
 333 
 334 // Define atoms outside component (singleton)
 335 const searchTermAtom = atom('');
 336 const resultsAtom = atom([]);
 337 const isLoadingAtom = atom(false);
 338 
 339 // Computed values
 340 const hasResults = computed(() => resultsAtom.value.length > 0);
 341 const resultCount = computed(() => resultsAtom.value.length);
 342 
 343 export default class SearchComponent extends LightningElement {
 344     // Bind atoms to component for reactivity
 345     get searchTerm() {
 346         return searchTermAtom.value;
 347     }
 348 
 349     get results() {
 350         return resultsAtom.value;
 351     }
 352 
 353     get isLoading() {
 354         return isLoadingAtom.value;
 355     }
 356 
 357     get hasResults() {
 358         return hasResults.value;
 359     }
 360 
 361     handleSearchChange(event) {
 362         searchTermAtom.value = event.target.value;
 363         this.performSearch();
 364     }
 365 
 366     async performSearch() {
 367         if (searchTermAtom.value.length < 2) {
 368             resultsAtom.value = [];
 369             return;
 370         }
 371 
 372         isLoadingAtom.value = true;
 373         try {
 374             const results = await searchRecords({ term: searchTermAtom.value });
 375             resultsAtom.value = results;
 376         } finally {
 377             isLoadingAtom.value = false;
 378         }
 379     }
 380 }
 381 ```
 382 
 383 ---
 384 
 385 ## Pattern 4: Platform State Managers
 386 
 387 Salesforce provides built-in state managers for record pages and layouts.
 388 
 389 ### stateManagerRecord
 390 
 391 Manages record data with automatic refresh and caching.
 392 
 393 ```javascript
 394 import { LightningElement, wire } from 'lwc';
 395 import { stateManagerRecord } from 'lightning/stateManagerRecord';
 396 import { getRecord } from 'lightning/uiRecordApi';
 397 
 398 export default class RecordStateExample extends LightningElement {
 399     @api recordId;
 400 
 401     // Wire with state manager for enhanced caching
 402     @wire(stateManagerRecord, {
 403         recordId: '$recordId',
 404         fields: ['Account.Name', 'Account.Industry']
 405     })
 406     recordState;
 407 
 408     get accountName() {
 409         return this.recordState?.data?.fields?.Name?.value;
 410     }
 411 
 412     get industry() {
 413         return this.recordState?.data?.fields?.Industry?.value;
 414     }
 415 
 416     // State manager provides loading/error states
 417     get isLoading() {
 418         return this.recordState?.loading;
 419     }
 420 
 421     get hasError() {
 422         return !!this.recordState?.error;
 423     }
 424 }
 425 ```
 426 
 427 ### stateManagerLayout
 428 
 429 Manages layout-aware state for flexipage components.
 430 
 431 ```javascript
 432 import { LightningElement, wire } from 'lwc';
 433 import { stateManagerLayout } from 'lightning/stateManagerLayout';
 434 
 435 export default class LayoutAwareComponent extends LightningElement {
 436     @api recordId;
 437     @api objectApiName;
 438 
 439     // Wire layout state manager
 440     @wire(stateManagerLayout, {
 441         recordId: '$recordId',
 442         objectApiName: '$objectApiName'
 443     })
 444     layoutState;
 445 
 446     get isCompact() {
 447         return this.layoutState?.density === 'compact';
 448     }
 449 
 450     get visibleFields() {
 451         return this.layoutState?.fields || [];
 452     }
 453 }
 454 ```
 455 
 456 ### Composing State Managers
 457 
 458 ```javascript
 459 import { LightningElement, wire } from 'lwc';
 460 import { stateManagerRecord } from 'lightning/stateManagerRecord';
 461 import { atom, computed } from '@lwc/state';
 462 
 463 // Custom state atoms
 464 const selectedTabAtom = atom('details');
 465 const expandedSectionsAtom = atom(new Set(['overview']));
 466 
 467 export default class ComposedStateComponent extends LightningElement {
 468     @api recordId;
 469 
 470     // Platform state for record data
 471     @wire(stateManagerRecord, {
 472         recordId: '$recordId',
 473         fields: ['Account.Name', 'Account.Type', 'Account.Industry']
 474     })
 475     recordState;
 476 
 477     // Custom state for UI
 478     get selectedTab() {
 479         return selectedTabAtom.value;
 480     }
 481 
 482     get expandedSections() {
 483         return expandedSectionsAtom.value;
 484     }
 485 
 486     isSectionExpanded(sectionId) {
 487         return expandedSectionsAtom.value.has(sectionId);
 488     }
 489 
 490     handleTabChange(event) {
 491         selectedTabAtom.value = event.detail.value;
 492     }
 493 
 494     handleSectionToggle(event) {
 495         const sectionId = event.target.dataset.section;
 496         const sections = new Set(expandedSectionsAtom.value);
 497 
 498         if (sections.has(sectionId)) {
 499             sections.delete(sectionId);
 500         } else {
 501             sections.add(sectionId);
 502         }
 503 
 504         expandedSectionsAtom.value = sections;
 505     }
 506 }
 507 ```
 508 
 509 ---
 510 
 511 ## Anti-Patterns to Avoid
 512 
 513 ### ❌ BAD: Mutating Objects In Place
 514 
 515 ```javascript
 516 // DON'T - won't trigger reactivity
 517 this.user.name = 'New Name';
 518 this.items.push(newItem);
 519 ```
 520 
 521 ### ✅ GOOD: Create New References
 522 
 523 ```javascript
 524 // DO - triggers reactivity
 525 this.user = { ...this.user, name: 'New Name' };
 526 this.items = [...this.items, newItem];
 527 ```
 528 
 529 ### ❌ BAD: Heavy Computation in Getters
 530 
 531 ```javascript
 532 // DON'T - runs every render cycle
 533 get expensiveComputation() {
 534     return this.items
 535         .map(item => complexTransform(item))
 536         .filter(item => complexFilter(item))
 537         .sort((a, b) => complexSort(a, b));
 538 }
 539 ```
 540 
 541 ### ✅ GOOD: Cache Computed Values
 542 
 543 ```javascript
 544 _cachedResult;
 545 _lastItemsHash;
 546 
 547 get optimizedComputation() {
 548     const currentHash = JSON.stringify(this.items);
 549     if (this._lastItemsHash !== currentHash) {
 550         this._cachedResult = this.items
 551             .map(item => complexTransform(item))
 552             .filter(item => complexFilter(item))
 553             .sort((a, b) => complexSort(a, b));
 554         this._lastItemsHash = currentHash;
 555     }
 556     return this._cachedResult;
 557 }
 558 ```
 559 
 560 ### ❌ BAD: Forgetting to Unsubscribe
 561 
 562 ```javascript
 563 // DON'T - memory leak
 564 connectedCallback() {
 565     store.subscribe('data', (data) => this.data = data);
 566 }
 567 ```
 568 
 569 ### ✅ GOOD: Clean Up Subscriptions
 570 
 571 ```javascript
 572 // DO - proper cleanup
 573 _unsubscribe;
 574 
 575 connectedCallback() {
 576     this._unsubscribe = store.subscribe('data', (data) => this.data = data);
 577 }
 578 
 579 disconnectedCallback() {
 580     if (this._unsubscribe) {
 581         this._unsubscribe();
 582     }
 583 }
 584 ```
 585 
 586 ---
 587 
 588 ## Best Practices Summary
 589 
 590 ```
 591 ┌─────────────────────────────────────────────────────────────────────────────┐
 592 │                    STATE MANAGEMENT BEST PRACTICES                           │
 593 ├─────────────────────────────────────────────────────────────────────────────┤
 594 │                                                                             │
 595 │  CHOOSE THE RIGHT PATTERN                                                   │
 596 │  ─────────────────────────────────────────────────────────────────────────  │
 597 │  ✅ Start with simple reactive properties                                   │
 598 │  ✅ Use singleton store for shared non-record state                         │
 599 │  ✅ Use @lwc/state for complex derived state                                │
 600 │  ✅ Use Platform State Managers on record pages                             │
 601 │  ❌ Don't over-engineer simple components                                   │
 602 │                                                                             │
 603 │  REACTIVITY                                                                 │
 604 │  ─────────────────────────────────────────────────────────────────────────  │
 605 │  ✅ Create new object/array references for updates                          │
 606 │  ✅ Use spread operator: { ...obj, newProp }                                │
 607 │  ✅ Use getters for computed values                                         │
 608 │  ❌ Don't mutate objects/arrays in place                                    │
 609 │                                                                             │
 610 │  PERFORMANCE                                                                │
 611 │  ─────────────────────────────────────────────────────────────────────────  │
 612 │  ✅ Cache expensive computations                                            │
 613 │  ✅ Debounce rapid state updates                                            │
 614 │  ✅ Clean up subscriptions in disconnectedCallback                          │
 615 │  ❌ Don't do heavy computation in getters                                   │
 616 │                                                                             │
 617 │  TESTING                                                                    │
 618 │  ─────────────────────────────────────────────────────────────────────────  │
 619 │  ✅ Test state transitions explicitly                                       │
 620 │  ✅ Verify subscription cleanup                                             │
 621 │  ✅ Mock store for unit tests                                               │
 622 │  ❌ Don't test implementation details                                       │
 623 │                                                                             │
 624 └─────────────────────────────────────────────────────────────────────────────┘
 625 ```
 626 
 627 ---
 628 
 629 ## Related Documentation
 630 
 631 - [SKILL.md](../SKILL.md) - PICKLES Framework overview
 632 - [lwc-best-practices.md](lwc-best-practices.md) - General LWC patterns
 633 - [triangle-pattern.md](triangle-pattern.md) - Component composition
 634 
 635 ---
 636 
 637 ## Source
 638 
 639 > **References**:
 640 > - [Mastering State Management in LWC using @lwc/state](https://salesforcediaries.com/2025/11/26/mastering-state-management-in-lwc-using-lwc-state/) - Salesforce Diaries
 641 > - [Platform State Managers in LWC](https://salesforcediaries.com/2025/11/26/platform-state-managers-in-lwc/) - Salesforce Diaries
