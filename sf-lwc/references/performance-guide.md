<!-- Parent: sf-lwc/SKILL.md -->
   1 # Performance Optimization Guide for LWC
   2 
   3 Comprehensive guide to optimizing Lightning Web Component performance, including dark mode implementation, lazy loading, and rendering optimization.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [Dark Mode Implementation](#dark-mode-implementation)
  10 2. [Rendering Performance](#rendering-performance)
  11 3. [Lazy Loading](#lazy-loading)
  12 4. [Data Management](#data-management)
  13 5. [Event Optimization](#event-optimization)
  14 6. [Memory Management](#memory-management)
  15 7. [Bundle Size Optimization](#bundle-size-optimization)
  16 8. [Performance Testing](#performance-testing)
  17 9. [Common Anti-Patterns](#common-anti-patterns)
  18 
  19 ---
  20 
  21 ## Dark Mode Implementation
  22 
  23 Dark mode is exclusive to SLDS 2 themes. Components must use global styling hooks to support light/dark theme switching.
  24 
  25 ### Complete SLDS 2 Color Token Reference
  26 
  27 #### Surface Colors
  28 
  29 | Token | Light Mode | Dark Mode | Purpose |
  30 |-------|------------|-----------|---------|
  31 | `--slds-g-color-surface-1` | `#FFFFFF` | `#0B0B0B` | Primary surface (body background) |
  32 | `--slds-g-color-surface-2` | `#F3F3F3` | `#181818` | Secondary surface |
  33 | `--slds-g-color-surface-3` | `#E5E5E5` | `#2B2B2B` | Tertiary surface |
  34 | `--slds-g-color-surface-4` | `#C9C9C9` | `#3E3E3E` | Quaternary surface |
  35 
  36 #### Container Colors
  37 
  38 | Token | Light Mode | Dark Mode | Purpose |
  39 |-------|------------|-----------|---------|
  40 | `--slds-g-color-surface-container-1` | `#FAFAFA` | `#1A1A1A` | Card backgrounds, panels |
  41 | `--slds-g-color-surface-container-2` | `#F7F7F7` | `#232323` | Nested containers |
  42 | `--slds-g-color-surface-container-3` | `#F3F3F3` | `#2E2E2E` | Deep nesting |
  43 
  44 #### Text Colors
  45 
  46 | Token | Light Mode | Dark Mode | Purpose |
  47 |-------|------------|-----------|---------|
  48 | `--slds-g-color-on-surface` | `#181818` | `#FAFAFA` | Primary text |
  49 | `--slds-g-color-on-surface-1` | `#444444` | `#C9C9C9` | Secondary text |
  50 | `--slds-g-color-on-surface-2` | `#706E6B` | `#A0A0A0` | Muted/disabled text |
  51 | `--slds-g-color-on-surface-inverse` | `#FFFFFF` | `#181818` | Inverse text (buttons, badges) |
  52 
  53 #### Border Colors
  54 
  55 | Token | Light Mode | Dark Mode | Purpose |
  56 |-------|------------|-----------|---------|
  57 | `--slds-g-color-border-1` | `#C9C9C9` | `#444444` | Primary borders |
  58 | `--slds-g-color-border-2` | `#E5E5E5` | `#3E3E3E` | Secondary borders (dividers) |
  59 
  60 #### Brand Colors
  61 
  62 | Token | Light Mode | Dark Mode | Purpose |
  63 |-------|------------|-----------|---------|
  64 | `--slds-g-color-brand-1` | `#0176D3` | `#1B96FF` | Primary brand (buttons, links) |
  65 | `--slds-g-color-brand-2` | `#014486` | `#0B5CAB` | Brand hover/active states |
  66 
  67 #### Status Colors
  68 
  69 | Token | Light Mode | Dark Mode | Purpose |
  70 |-------|------------|-----------|---------|
  71 | `--slds-g-color-success-1` | `#2E844A` | `#45C65A` | Success states |
  72 | `--slds-g-color-error-1` | `#EA001E` | `#FE5C4C` | Error states |
  73 | `--slds-g-color-warning-1` | `#FFB75D` | `#FFB75D` | Warning states |
  74 | `--slds-g-color-info-1` | `#0176D3` | `#1B96FF` | Info states |
  75 
  76 #### Spacing Tokens
  77 
  78 | Token | Value (rem) | Value (px) |
  79 |-------|-------------|------------|
  80 | `--slds-g-spacing-0` | 0 | 0 |
  81 | `--slds-g-spacing-1` | 0.125 | 2 |
  82 | `--slds-g-spacing-2` | 0.25 | 4 |
  83 | `--slds-g-spacing-3` | 0.5 | 8 |
  84 | `--slds-g-spacing-4` | 0.75 | 12 |
  85 | `--slds-g-spacing-5` | 1 | 16 |
  86 | `--slds-g-spacing-6` | 1.5 | 24 |
  87 | `--slds-g-spacing-7` | 2 | 32 |
  88 | `--slds-g-spacing-8` | 3 | 48 |
  89 
  90 ### Migration Examples
  91 
  92 #### Before: SLDS 1 (Hardcoded Colors)
  93 
  94 ```css
  95 /* accountCard.css - SLDS 1 (Deprecated) */
  96 .card {
  97     background-color: #ffffff;
  98     color: #333333;
  99     border: 1px solid #dddddd;
 100     border-radius: 4px;
 101     padding: 16px;
 102     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
 103 }
 104 
 105 .card-header {
 106     color: #000000;
 107     font-size: 16px;
 108     font-weight: 700;
 109     margin-bottom: 8px;
 110 }
 111 
 112 .card-text {
 113     color: #666666;
 114     font-size: 14px;
 115 }
 116 
 117 .card-link {
 118     color: #0176d3;
 119 }
 120 
 121 .card-link:hover {
 122     color: #014486;
 123     text-decoration: underline;
 124 }
 125 ```
 126 
 127 #### After: SLDS 2 (Dark Mode Ready)
 128 
 129 ```css
 130 /* accountCard.css - SLDS 2 */
 131 .card {
 132     background-color: var(--slds-g-color-surface-container-1, #ffffff);
 133     color: var(--slds-g-color-on-surface, #181818);
 134     border: 1px solid var(--slds-g-color-border-2, #e5e5e5);
 135     border-radius: var(--slds-g-radius-border-2, 0.25rem);
 136     padding: var(--slds-g-spacing-5, 1rem);
 137     box-shadow: 0 2px 4px var(--slds-g-color-border-1, rgba(0, 0, 0, 0.1));
 138 }
 139 
 140 .card-header {
 141     color: var(--slds-g-color-on-surface, #181818);
 142     font-size: var(--slds-g-font-size-5, 1rem);
 143     font-weight: var(--slds-g-font-weight-bold, 700);
 144     margin-bottom: var(--slds-g-spacing-3, 0.5rem);
 145 }
 146 
 147 .card-text {
 148     color: var(--slds-g-color-on-surface-1, #444444);
 149     font-size: var(--slds-g-font-size-3, 0.875rem);
 150 }
 151 
 152 .card-link {
 153     color: var(--slds-g-color-brand-1, #0176d3);
 154 }
 155 
 156 .card-link:hover {
 157     color: var(--slds-g-color-brand-2, #014486);
 158     text-decoration: underline;
 159 }
 160 ```
 161 
 162 ### Component-Level Example
 163 
 164 ```javascript
 165 // darkModeCard.js
 166 import { LightningElement } from 'lwc';
 167 
 168 export default class DarkModeCard extends LightningElement {
 169     // No JavaScript changes needed for dark mode!
 170     // All theming is handled via CSS variables
 171 }
 172 ```
 173 
 174 ```html
 175 <!-- darkModeCard.html -->
 176 <template>
 177     <div class="card">
 178         <div class="card-header">
 179             <h2 class="card-title">Account Details</h2>
 180         </div>
 181         <div class="card-body">
 182             <p class="card-text">This card automatically adapts to light/dark mode</p>
 183             <a href="#" class="card-link">Learn more</a>
 184         </div>
 185     </div>
 186 </template>
 187 ```
 188 
 189 ```css
 190 /* darkModeCard.css */
 191 .card {
 192     background-color: var(--slds-g-color-surface-container-1, #ffffff);
 193     border: 1px solid var(--slds-g-color-border-2, #e5e5e5);
 194     border-radius: var(--slds-g-radius-border-2, 0.25rem);
 195     padding: var(--slds-g-spacing-5, 1rem);
 196 }
 197 
 198 .card-header {
 199     border-bottom: 1px solid var(--slds-g-color-border-2, #e5e5e5);
 200     margin-bottom: var(--slds-g-spacing-4, 0.75rem);
 201     padding-bottom: var(--slds-g-spacing-3, 0.5rem);
 202 }
 203 
 204 .card-title {
 205     color: var(--slds-g-color-on-surface, #181818);
 206     font-size: var(--slds-g-font-size-5, 1rem);
 207     font-weight: var(--slds-g-font-weight-bold, 700);
 208     margin: 0;
 209 }
 210 
 211 .card-body {
 212     color: var(--slds-g-color-on-surface-1, #444444);
 213 }
 214 
 215 .card-text {
 216     margin-bottom: var(--slds-g-spacing-4, 0.75rem);
 217 }
 218 
 219 .card-link {
 220     color: var(--slds-g-color-brand-1, #0176d3);
 221     text-decoration: none;
 222 }
 223 
 224 .card-link:hover {
 225     color: var(--slds-g-color-brand-2, #014486);
 226     text-decoration: underline;
 227 }
 228 ```
 229 
 230 ### Validation Script
 231 
 232 ```bash
 233 # Check for hardcoded colors in CSS
 234 grep -r "#[0-9A-Fa-f]\{3,6\}" force-app/main/default/lwc/ --include="*.css"
 235 
 236 # Check for rgb/rgba values
 237 grep -r "rgb\|rgba" force-app/main/default/lwc/ --include="*.css"
 238 
 239 # Install SLDS Linter
 240 npm install -g @salesforce-ux/slds-linter
 241 
 242 # Run validation
 243 slds-linter lint force-app/main/default/lwc/
 244 ```
 245 
 246 ---
 247 
 248 ## Rendering Performance
 249 
 250 ### Conditional Rendering
 251 
 252 ```javascript
 253 // BAD: Re-renders entire list
 254 <template for:each={allItems} for:item="item">
 255     <div if:true={item.visible} key={item.id}>
 256         {item.name}
 257     </div>
 258 </template>
 259 
 260 // GOOD: Filter before rendering
 261 get visibleItems() {
 262     return this.allItems.filter(item => item.visible);
 263 }
 264 
 265 <template for:each={visibleItems} for:item="item">
 266     <div key={item.id}>{item.name}</div>
 267 </template>
 268 ```
 269 
 270 ### Use `lwc:if` for Large Blocks
 271 
 272 ```html
 273 <!-- lwc:if removes from DOM (better for large blocks) -->
 274 <template lwc:if={showDashboard}>
 275     <c-dashboard data={dashboardData}></c-dashboard>
 276 </template>
 277 
 278 <!-- if:true hides with CSS (better for frequent toggling) -->
 279 <div if:true={showMessage} class="message">
 280     {message}
 281 </div>
 282 ```
 283 
 284 ### Key Directive for Lists
 285 
 286 ```html
 287 <!-- CRITICAL: Use unique, stable keys -->
 288 <template for:each={accounts} for:item="account">
 289     <div key={account.Id}>  <!-- Use record ID, not index -->
 290         {account.Name}
 291     </div>
 292 </template>
 293 ```
 294 
 295 ### Getter Caching
 296 
 297 ```javascript
 298 // BAD: Recalculates on every render
 299 get formattedValue() {
 300     return this.expensiveCalculation(this.data);
 301 }
 302 
 303 // GOOD: Cache the result
 304 @track _cachedValue;
 305 _cacheKey;
 306 
 307 get formattedValue() {
 308     const currentKey = JSON.stringify(this.data);
 309     if (this._cacheKey !== currentKey) {
 310         this._cacheKey = currentKey;
 311         this._cachedValue = this.expensiveCalculation(this.data);
 312     }
 313     return this._cachedValue;
 314 }
 315 ```
 316 
 317 ### Avoid renderedCallback Loops
 318 
 319 ```javascript
 320 // BAD: Infinite loop
 321 renderedCallback() {
 322     this.count++; // Triggers re-render
 323 }
 324 
 325 // GOOD: Guard against loops
 326 renderedCallback() {
 327     if (!this._rendered) {
 328         this._rendered = true;
 329         this.initializeChart();
 330     }
 331 }
 332 ```
 333 
 334 ---
 335 
 336 ## Lazy Loading
 337 
 338 ### Dynamic Imports
 339 
 340 ```javascript
 341 // accountManager.js
 342 export default class AccountManager extends LightningElement {
 343     @track showCharts = false;
 344     chartModule;
 345 
 346     async handleShowCharts() {
 347         if (!this.chartModule) {
 348             // Lazy load chart component
 349             this.chartModule = await import('c/accountChart');
 350         }
 351         this.showCharts = true;
 352     }
 353 }
 354 ```
 355 
 356 ### Intersection Observer for Lazy Loading
 357 
 358 ```javascript
 359 // lazyImageLoader.js
 360 export default class LazyImageLoader extends LightningElement {
 361     @api src;
 362     @api alt;
 363 
 364     isVisible = false;
 365     observer;
 366 
 367     renderedCallback() {
 368         if (!this.observer) {
 369             this.observer = new IntersectionObserver((entries) => {
 370                 entries.forEach(entry => {
 371                     if (entry.isIntersecting) {
 372                         this.isVisible = true;
 373                         this.observer.disconnect();
 374                     }
 375                 });
 376             }, { rootMargin: '50px' });
 377 
 378             const img = this.template.querySelector('img');
 379             if (img) {
 380                 this.observer.observe(img);
 381             }
 382         }
 383     }
 384 
 385     get imageSrc() {
 386         return this.isVisible ? this.src : 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
 387     }
 388 
 389     disconnectedCallback() {
 390         if (this.observer) {
 391             this.observer.disconnect();
 392         }
 393     }
 394 }
 395 ```
 396 
 397 ```html
 398 <!-- lazyImageLoader.html -->
 399 <template>
 400     <img src={imageSrc} alt={alt} loading="lazy">
 401 </template>
 402 ```
 403 
 404 ### Virtual Scrolling
 405 
 406 ```javascript
 407 // virtualList.js
 408 export default class VirtualList extends LightningElement {
 409     @api items = [];
 410     @track visibleItems = [];
 411 
 412     itemHeight = 50;
 413     containerHeight = 500;
 414     scrollTop = 0;
 415 
 416     get visibleCount() {
 417         return Math.ceil(this.containerHeight / this.itemHeight);
 418     }
 419 
 420     get startIndex() {
 421         return Math.floor(this.scrollTop / this.itemHeight);
 422     }
 423 
 424     get endIndex() {
 425         return Math.min(
 426             this.startIndex + this.visibleCount + 1,
 427             this.items.length
 428         );
 429     }
 430 
 431     get paddingTop() {
 432         return this.startIndex * this.itemHeight;
 433     }
 434 
 435     get paddingBottom() {
 436         return (this.items.length - this.endIndex) * this.itemHeight;
 437     }
 438 
 439     connectedCallback() {
 440         this.updateVisibleItems();
 441     }
 442 
 443     handleScroll(event) {
 444         this.scrollTop = event.target.scrollTop;
 445         this.updateVisibleItems();
 446     }
 447 
 448     updateVisibleItems() {
 449         this.visibleItems = this.items.slice(
 450             this.startIndex,
 451             this.endIndex
 452         );
 453     }
 454 }
 455 ```
 456 
 457 ```html
 458 <!-- virtualList.html -->
 459 <template>
 460     <div class="container"
 461          style={containerStyle}
 462          onscroll={handleScroll}>
 463         <div style={paddingTopStyle}></div>
 464         <template for:each={visibleItems} for:item="item">
 465             <div key={item.id} class="item">
 466                 {item.name}
 467             </div>
 468         </template>
 469         <div style={paddingBottomStyle}></div>
 470     </div>
 471 </template>
 472 ```
 473 
 474 ---
 475 
 476 ## Data Management
 477 
 478 ### Debouncing
 479 
 480 ```javascript
 481 // searchComponent.js
 482 export default class SearchComponent extends LightningElement {
 483     searchTerm = '';
 484     delayTimeout;
 485 
 486     handleSearchChange(event) {
 487         const searchTerm = event.target.value;
 488 
 489         // Clear previous timeout
 490         clearTimeout(this.delayTimeout);
 491 
 492         // Set new timeout (300ms debounce)
 493         this.delayTimeout = setTimeout(() => {
 494             this.performSearch(searchTerm);
 495         }, 300);
 496     }
 497 
 498     async performSearch(term) {
 499         try {
 500             const results = await searchAccounts({ searchTerm: term });
 501             this.results = results;
 502         } catch (error) {
 503             this.handleError(error);
 504         }
 505     }
 506 
 507     disconnectedCallback() {
 508         clearTimeout(this.delayTimeout);
 509     }
 510 }
 511 ```
 512 
 513 ### Throttling
 514 
 515 ```javascript
 516 // scrollTracker.js
 517 export default class ScrollTracker extends LightningElement {
 518     lastScrollTime = 0;
 519     throttleDelay = 100;
 520 
 521     handleScroll(event) {
 522         const now = Date.now();
 523 
 524         if (now - this.lastScrollTime >= this.throttleDelay) {
 525             this.lastScrollTime = now;
 526             this.processScroll(event);
 527         }
 528     }
 529 
 530     processScroll(event) {
 531         // Handle scroll logic
 532         console.log('Scroll position:', event.target.scrollTop);
 533     }
 534 }
 535 ```
 536 
 537 ### Caching Wire Results
 538 
 539 ```javascript
 540 // accountList.js
 541 export default class AccountList extends LightningElement {
 542     @api recordId;
 543     wiredAccountsResult;
 544 
 545     @wire(getAccounts, { accountId: '$recordId' })
 546     wiredAccounts(result) {
 547         this.wiredAccountsResult = result; // Cache for refreshApex
 548         if (result.data) {
 549             this.accounts = result.data;
 550         } else if (result.error) {
 551             this.error = result.error;
 552         }
 553     }
 554 
 555     async handleRefresh() {
 556         // Refresh cached wire result
 557         await refreshApex(this.wiredAccountsResult);
 558     }
 559 }
 560 ```
 561 
 562 ---
 563 
 564 ## Event Optimization
 565 
 566 ### Event Delegation
 567 
 568 ```javascript
 569 // BAD: Multiple event listeners
 570 <template for:each={items} for:item="item">
 571     <button key={item.id} onclick={handleClick} data-id={item.id}>
 572         {item.name}
 573     </button>
 574 </template>
 575 
 576 // GOOD: Single delegated listener
 577 <div onclick={handleContainerClick}>
 578     <template for:each={items} for:item="item">
 579         <button key={item.id} data-id={item.id}>
 580             {item.name}
 581         </button>
 582     </template>
 583 </div>
 584 
 585 handleContainerClick(event) {
 586     if (event.target.tagName === 'BUTTON') {
 587         const itemId = event.target.dataset.id;
 588         this.processClick(itemId);
 589     }
 590 }
 591 ```
 592 
 593 ### Prevent Event Bubbling
 594 
 595 ```javascript
 596 handleClick(event) {
 597     event.stopPropagation(); // Stop bubbling
 598     event.preventDefault();   // Prevent default action
 599 
 600     // Process event
 601 }
 602 ```
 603 
 604 ---
 605 
 606 ## Memory Management
 607 
 608 ### Cleanup in disconnectedCallback
 609 
 610 ```javascript
 611 export default class ResourceManager extends LightningElement {
 612     subscription;
 613     intervalId;
 614     observer;
 615 
 616     connectedCallback() {
 617         // Subscribe to events
 618         this.subscription = subscribe(
 619             this.messageContext,
 620             CHANNEL,
 621             this.handleMessage
 622         );
 623 
 624         // Set interval
 625         this.intervalId = setInterval(() => {
 626             this.updateData();
 627         }, 5000);
 628 
 629         // Create observer
 630         this.observer = new IntersectionObserver(
 631             this.handleIntersection
 632         );
 633     }
 634 
 635     disconnectedCallback() {
 636         // CRITICAL: Clean up all resources
 637         if (this.subscription) {
 638             unsubscribe(this.subscription);
 639             this.subscription = null;
 640         }
 641 
 642         if (this.intervalId) {
 643             clearInterval(this.intervalId);
 644             this.intervalId = null;
 645         }
 646 
 647         if (this.observer) {
 648             this.observer.disconnect();
 649             this.observer = null;
 650         }
 651     }
 652 }
 653 ```
 654 
 655 ### Remove Event Listeners
 656 
 657 ```javascript
 658 export default class EventManager extends LightningElement {
 659     boundHandler;
 660 
 661     connectedCallback() {
 662         this.boundHandler = this.handleResize.bind(this);
 663         window.addEventListener('resize', this.boundHandler);
 664     }
 665 
 666     disconnectedCallback() {
 667         window.removeEventListener('resize', this.boundHandler);
 668     }
 669 
 670     handleResize() {
 671         // Handle resize
 672     }
 673 }
 674 ```
 675 
 676 ---
 677 
 678 ## Bundle Size Optimization
 679 
 680 ### Code Splitting
 681 
 682 ```javascript
 683 // Import only what you need
 684 import { getRecord } from 'lightning/uiRecordApi';
 685 import NAME_FIELD from '@salesforce/schema/Account.Name';
 686 
 687 // Don't import entire modules
 688 // BAD: import * as uiRecordApi from 'lightning/uiRecordApi';
 689 ```
 690 
 691 ### Minimize Dependencies
 692 
 693 ```javascript
 694 // BAD: Import heavy library for simple task
 695 import moment from 'moment';
 696 
 697 get formattedDate() {
 698     return moment(this.date).format('MM/DD/YYYY');
 699 }
 700 
 701 // GOOD: Use native APIs
 702 get formattedDate() {
 703     return new Intl.DateTimeFormat('en-US').format(new Date(this.date));
 704 }
 705 ```
 706 
 707 ---
 708 
 709 ## Performance Testing
 710 
 711 ### Chrome DevTools Performance Tab
 712 
 713 ```javascript
 714 // Add performance marks
 715 export default class PerformanceTracked extends LightningElement {
 716     connectedCallback() {
 717         performance.mark('component-start');
 718         this.initializeComponent();
 719         performance.mark('component-end');
 720         performance.measure(
 721             'component-initialization',
 722             'component-start',
 723             'component-end'
 724         );
 725 
 726         const measure = performance.getEntriesByName('component-initialization')[0];
 727         console.log('Initialization took:', measure.duration, 'ms');
 728     }
 729 }
 730 ```
 731 
 732 ### Lighthouse Audit
 733 
 734 ```bash
 735 lighthouse https://your-org.lightning.force.com --only-categories=performance
 736 ```
 737 
 738 ### Custom Performance Metrics
 739 
 740 ```javascript
 741 export default class MetricsTracker extends LightningElement {
 742     connectedCallback() {
 743         // Track time to interactive
 744         const startTime = performance.now();
 745 
 746         this.loadData().then(() => {
 747             const endTime = performance.now();
 748             console.log('Time to interactive:', endTime - startTime, 'ms');
 749         });
 750     }
 751 }
 752 ```
 753 
 754 ---
 755 
 756 ## Common Anti-Patterns
 757 
 758 ### 1. Excessive Wire Calls
 759 
 760 ```javascript
 761 // BAD: Multiple wire calls for related data
 762 @wire(getAccount, { accountId: '$recordId' }) account;
 763 @wire(getContacts, { accountId: '$recordId' }) contacts;
 764 @wire(getOpportunities, { accountId: '$recordId' }) opportunities;
 765 
 766 // GOOD: Single wire call with joined data
 767 @wire(getAccountWithRelated, { accountId: '$recordId' })
 768 wiredData({ data, error }) {
 769     if (data) {
 770         this.account = data.account;
 771         this.contacts = data.contacts;
 772         this.opportunities = data.opportunities;
 773     }
 774 }
 775 ```
 776 
 777 ### 2. Updating Tracked Properties in Getters
 778 
 779 ```javascript
 780 // BAD: Side effects in getter
 781 @track count = 0;
 782 
 783 get message() {
 784     this.count++; // Causes infinite re-render!
 785     return `Count: ${this.count}`;
 786 }
 787 
 788 // GOOD: Pure getter
 789 get message() {
 790     return `Count: ${this.count}`;
 791 }
 792 ```
 793 
 794 ### 3. Not Using @track Wisely
 795 
 796 ```javascript
 797 // BAD: Over-using @track
 798 @track simpleValue = 'hello';
 799 @track anotherValue = 42;
 800 
 801 // GOOD: Only track complex objects
 802 simpleValue = 'hello'; // Primitives don't need @track
 803 @track complexObject = { nested: { value: 42 } };
 804 ```
 805 
 806 ### 4. Heavy Operations in renderedCallback
 807 
 808 ```javascript
 809 // BAD: Heavy calculation every render
 810 renderedCallback() {
 811     this.calculateComplexMetrics(); // Expensive!
 812 }
 813 
 814 // GOOD: Calculate only when data changes
 815 @track _dataVersion = 0;
 816 _renderedVersion = -1;
 817 
 818 renderedCallback() {
 819     if (this._renderedVersion !== this._dataVersion) {
 820         this._renderedVersion = this._dataVersion;
 821         this.calculateComplexMetrics();
 822     }
 823 }
 824 
 825 handleDataChange() {
 826     this._dataVersion++;
 827 }
 828 ```
 829 
 830 ---
 831 
 832 ## Performance Checklist
 833 
 834 - [ ] Use SLDS 2 color tokens (dark mode ready)
 835 - [ ] Lazy load components with dynamic imports
 836 - [ ] Implement virtual scrolling for long lists (100+ items)
 837 - [ ] Debounce search inputs (300ms)
 838 - [ ] Throttle scroll/resize handlers (100ms)
 839 - [ ] Cache expensive getter calculations
 840 - [ ] Use `lwc:if` for large conditional blocks
 841 - [ ] Provide stable keys in `for:each` loops
 842 - [ ] Clean up resources in `disconnectedCallback()`
 843 - [ ] Avoid heavy operations in `renderedCallback()`
 844 - [ ] Use event delegation for list items
 845 - [ ] Minimize wire service calls
 846 - [ ] Remove unused imports
 847 - [ ] Test with Chrome DevTools Performance tab
 848 - [ ] Run Lighthouse performance audit
 849 
 850 ---
 851 
 852 ## Related Resources
 853 
 854 - [component-patterns.md](component-patterns.md) - Implementation patterns
 855 - [accessibility-guide.md](accessibility-guide.md) - A11y compliance
 856 - [jest-testing.md](jest-testing.md) - Testing strategies
 857 - [SLDS 2 Transition Guide](https://www.lightningdesignsystem.com/2e1ef8501/p/8184ad-transition-to-slds-2)
 858 - [LWC Performance Best Practices](https://developer.salesforce.com/docs/component-library/documentation/en/lwc/lwc.create_performance)
