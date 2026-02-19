<!-- Parent: sf-lwc/SKILL.md -->
   1 # LWC Template Anti-Patterns
   2 
   3 This guide documents systematic errors in Lightning Web Component templates, with special focus on patterns that LLMs commonly generate incorrectly. LWC templates have strict limitations compared to frameworks like React or Vue.
   4 
   5 > **Source**: [LLM Mistakes in Apex & LWC - Salesforce Diaries](https://salesforcediaries.com/2026/01/16/llm-mistakes-in-apex-lwc-salesforce-code-generation-rules/)
   6 
   7 ---
   8 
   9 ## Table of Contents
  10 
  11 1. [Inline JavaScript Expressions](#1-inline-javascript-expressions)
  12 2. [Ternary Operators in Templates](#2-ternary-operators-in-templates)
  13 3. [Object Literals in Attributes](#3-object-literals-in-attributes)
  14 4. [Complex Expressions](#4-complex-expressions)
  15 5. [Event Handler Mistakes](#5-event-handler-mistakes)
  16 6. [Iteration Anti-Patterns](#6-iteration-anti-patterns)
  17 7. [Conditional Rendering Issues](#7-conditional-rendering-issues)
  18 8. [Slot and Composition Errors](#8-slot-and-composition-errors)
  19 9. [Data Binding Mistakes](#9-data-binding-mistakes)
  20 10. [Style and Class Binding](#10-style-and-class-binding)
  21 
  22 ---
  23 
  24 ## 1. Inline JavaScript Expressions
  25 
  26 **Critical Rule**: LWC templates do NOT support JavaScript expressions. Only property references are allowed.
  27 
  28 ### ❌ BAD: Arithmetic in Template
  29 
  30 ```html
  31 <!-- LLM generates this - DOES NOT WORK -->
  32 <template>
  33     <p>Total: {price * quantity}</p>
  34     <p>Tax: {price * 0.1}</p>
  35     <p>Discount: {price - discount}</p>
  36 </template>
  37 ```
  38 
  39 ### ✅ GOOD: Use Getters
  40 
  41 ```javascript
  42 // component.js
  43 export default class PriceCalculator extends LightningElement {
  44     price = 100;
  45     quantity = 2;
  46     discount = 10;
  47 
  48     get total() {
  49         return this.price * this.quantity;
  50     }
  51 
  52     get tax() {
  53         return this.price * 0.1;
  54     }
  55 
  56     get discountedPrice() {
  57         return this.price - this.discount;
  58     }
  59 }
  60 ```
  61 
  62 ```html
  63 <!-- component.html -->
  64 <template>
  65     <p>Total: {total}</p>
  66     <p>Tax: {tax}</p>
  67     <p>Discount: {discountedPrice}</p>
  68 </template>
  69 ```
  70 
  71 ### ❌ BAD: String Concatenation in Template
  72 
  73 ```html
  74 <!-- DOES NOT WORK -->
  75 <template>
  76     <p>Hello, {firstName + ' ' + lastName}!</p>
  77     <a href={'/account/' + accountId}>View Account</a>
  78 </template>
  79 ```
  80 
  81 ### ✅ GOOD: Computed Properties
  82 
  83 ```javascript
  84 // component.js
  85 export default class Greeting extends LightningElement {
  86     firstName = 'John';
  87     lastName = 'Doe';
  88     accountId = '001xx000003DGbY';
  89 
  90     get fullName() {
  91         return `${this.firstName} ${this.lastName}`;
  92     }
  93 
  94     get accountUrl() {
  95         return `/account/${this.accountId}`;
  96     }
  97 }
  98 ```
  99 
 100 ```html
 101 <!-- component.html -->
 102 <template>
 103     <p>Hello, {fullName}!</p>
 104     <a href={accountUrl}>View Account</a>
 105 </template>
 106 ```
 107 
 108 ---
 109 
 110 ## 2. Ternary Operators in Templates
 111 
 112 **Critical Rule**: Ternary operators (`condition ? a : b`) are NOT allowed in LWC templates.
 113 
 114 ### ❌ BAD: Ternary in Template
 115 
 116 ```html
 117 <!-- LLM generates this - DOES NOT WORK -->
 118 <template>
 119     <p class={isActive ? 'active' : 'inactive'}>Status</p>
 120     <span>{count > 0 ? count : 'None'}</span>
 121     <button disabled={isLoading ? true : false}>Submit</button>
 122 </template>
 123 ```
 124 
 125 ### ✅ GOOD: Use Getters for Conditional Values
 126 
 127 ```javascript
 128 // component.js
 129 export default class StatusDisplay extends LightningElement {
 130     isActive = true;
 131     count = 0;
 132     isLoading = false;
 133 
 134     get statusClass() {
 135         return this.isActive ? 'active' : 'inactive';
 136     }
 137 
 138     get displayCount() {
 139         return this.count > 0 ? this.count : 'None';
 140     }
 141 
 142     get isButtonDisabled() {
 143         return this.isLoading;
 144     }
 145 }
 146 ```
 147 
 148 ```html
 149 <!-- component.html -->
 150 <template>
 151     <p class={statusClass}>Status</p>
 152     <span>{displayCount}</span>
 153     <button disabled={isButtonDisabled}>Submit</button>
 154 </template>
 155 ```
 156 
 157 ### ✅ GOOD: Use if:true/if:false for Conditional Rendering
 158 
 159 ```html
 160 <!-- component.html -->
 161 <template>
 162     <template if:true={isActive}>
 163         <p class="active">Active</p>
 164     </template>
 165     <template if:false={isActive}>
 166         <p class="inactive">Inactive</p>
 167     </template>
 168 
 169     <template if:true={hasCount}>
 170         <span>{count}</span>
 171     </template>
 172     <template if:false={hasCount}>
 173         <span>None</span>
 174     </template>
 175 </template>
 176 ```
 177 
 178 ```javascript
 179 // component.js
 180 get hasCount() {
 181     return this.count > 0;
 182 }
 183 ```
 184 
 185 ---
 186 
 187 ## 3. Object Literals in Attributes
 188 
 189 **Critical Rule**: Object literals (`{}`) cannot be passed directly as attribute values.
 190 
 191 ### ❌ BAD: Inline Object Literals
 192 
 193 ```html
 194 <!-- LLM generates this - DOES NOT WORK -->
 195 <template>
 196     <c-child-component
 197         config={{ showHeader: true, theme: 'dark' }}
 198         style={{ color: 'red', fontSize: '14px' }}>
 199     </c-child-component>
 200 
 201     <lightning-datatable
 202         columns={[{ label: 'Name', fieldName: 'name' }]}
 203         data={records}>
 204     </lightning-datatable>
 205 </template>
 206 ```
 207 
 208 ### ✅ GOOD: Define Objects in JavaScript
 209 
 210 ```javascript
 211 // component.js
 212 export default class ParentComponent extends LightningElement {
 213     config = {
 214         showHeader: true,
 215         theme: 'dark'
 216     };
 217 
 218     columns = [
 219         { label: 'Name', fieldName: 'name' },
 220         { label: 'Email', fieldName: 'email' }
 221     ];
 222 
 223     records = [];
 224 }
 225 ```
 226 
 227 ```html
 228 <!-- component.html -->
 229 <template>
 230     <c-child-component config={config}></c-child-component>
 231 
 232     <lightning-datatable
 233         columns={columns}
 234         data={records}>
 235     </lightning-datatable>
 236 </template>
 237 ```
 238 
 239 ### ❌ BAD: Inline Array Literals
 240 
 241 ```html
 242 <!-- DOES NOT WORK -->
 243 <template>
 244     <c-multi-select options={['Red', 'Green', 'Blue']}></c-multi-select>
 245 </template>
 246 ```
 247 
 248 ### ✅ GOOD: Define Arrays in JavaScript
 249 
 250 ```javascript
 251 // component.js
 252 export default class ColorPicker extends LightningElement {
 253     colorOptions = [
 254         { label: 'Red', value: 'red' },
 255         { label: 'Green', value: 'green' },
 256         { label: 'Blue', value: 'blue' }
 257     ];
 258 }
 259 ```
 260 
 261 ```html
 262 <!-- component.html -->
 263 <template>
 264     <c-multi-select options={colorOptions}></c-multi-select>
 265 </template>
 266 ```
 267 
 268 ---
 269 
 270 ## 4. Complex Expressions
 271 
 272 **Critical Rule**: No method calls, comparisons, or logical operators in templates.
 273 
 274 ### ❌ BAD: Method Calls in Template
 275 
 276 ```html
 277 <!-- LLM generates this - DOES NOT WORK -->
 278 <template>
 279     <p>{name.toUpperCase()}</p>
 280     <p>{items.length}</p>
 281     <p>{formatDate(createdDate)}</p>
 282     <p>{JSON.stringify(data)}</p>
 283 </template>
 284 ```
 285 
 286 ### ✅ GOOD: Use Getters for Transformations
 287 
 288 ```javascript
 289 // component.js
 290 export default class DataDisplay extends LightningElement {
 291     name = 'john doe';
 292     items = ['a', 'b', 'c'];
 293     createdDate = new Date();
 294     data = { key: 'value' };
 295 
 296     get upperName() {
 297         return this.name.toUpperCase();
 298     }
 299 
 300     get itemCount() {
 301         return this.items.length;
 302     }
 303 
 304     get formattedDate() {
 305         return new Intl.DateTimeFormat('en-US').format(this.createdDate);
 306     }
 307 
 308     get dataJson() {
 309         return JSON.stringify(this.data);
 310     }
 311 }
 312 ```
 313 
 314 ```html
 315 <!-- component.html -->
 316 <template>
 317     <p>{upperName}</p>
 318     <p>{itemCount}</p>
 319     <p>{formattedDate}</p>
 320     <p>{dataJson}</p>
 321 </template>
 322 ```
 323 
 324 ### ❌ BAD: Comparisons in Template
 325 
 326 ```html
 327 <!-- DOES NOT WORK -->
 328 <template>
 329     <template if:true={count > 5}>
 330         <p>Many items</p>
 331     </template>
 332 
 333     <template if:true={status === 'active'}>
 334         <p>Active</p>
 335     </template>
 336 </template>
 337 ```
 338 
 339 ### ✅ GOOD: Getter-Based Comparisons
 340 
 341 ```javascript
 342 // component.js
 343 get hasManyItems() {
 344     return this.count > 5;
 345 }
 346 
 347 get isActive() {
 348     return this.status === 'active';
 349 }
 350 ```
 351 
 352 ```html
 353 <!-- component.html -->
 354 <template>
 355     <template if:true={hasManyItems}>
 356         <p>Many items</p>
 357     </template>
 358 
 359     <template if:true={isActive}>
 360         <p>Active</p>
 361     </template>
 362 </template>
 363 ```
 364 
 365 ### ❌ BAD: Logical Operators in Template
 366 
 367 ```html
 368 <!-- DOES NOT WORK -->
 369 <template>
 370     <template if:true={isAdmin && hasPermission}>
 371         <button>Delete</button>
 372     </template>
 373 
 374     <template if:true={!isLoading}>
 375         <p>Content</p>
 376     </template>
 377 </template>
 378 ```
 379 
 380 ### ✅ GOOD: Computed Boolean Properties
 381 
 382 ```javascript
 383 // component.js
 384 get canDelete() {
 385     return this.isAdmin && this.hasPermission;
 386 }
 387 
 388 get isNotLoading() {
 389     return !this.isLoading;
 390 }
 391 ```
 392 
 393 ```html
 394 <!-- component.html -->
 395 <template>
 396     <template if:true={canDelete}>
 397         <button>Delete</button>
 398     </template>
 399 
 400     <template if:true={isNotLoading}>
 401         <p>Content</p>
 402     </template>
 403 </template>
 404 ```
 405 
 406 ---
 407 
 408 ## 5. Event Handler Mistakes
 409 
 410 ### ❌ BAD: Inline Event Handlers with Arguments
 411 
 412 ```html
 413 <!-- LLM generates this - DOES NOT WORK -->
 414 <template>
 415     <button onclick={handleClick(item.id)}>Click</button>
 416     <button onclick={() => this.handleDelete(record)}>Delete</button>
 417     <input onchange={e => this.handleChange(e.target.value)}>
 418 </template>
 419 ```
 420 
 421 ### ✅ GOOD: Handler Functions with Data Attributes
 422 
 423 ```html
 424 <!-- component.html -->
 425 <template>
 426     <template for:each={items} for:item="item">
 427         <button
 428             key={item.id}
 429             data-id={item.id}
 430             onclick={handleClick}>
 431             Click {item.name}
 432         </button>
 433     </template>
 434 </template>
 435 ```
 436 
 437 ```javascript
 438 // component.js
 439 handleClick(event) {
 440     const itemId = event.target.dataset.id;
 441     // or use event.currentTarget.dataset.id for delegated events
 442     console.log('Clicked item:', itemId);
 443 }
 444 
 445 handleChange(event) {
 446     const value = event.target.value;
 447     this.inputValue = value;
 448 }
 449 ```
 450 
 451 ### ❌ BAD: Event Binding with bind()
 452 
 453 ```html
 454 <!-- DOES NOT WORK -->
 455 <template>
 456     <button onclick={handleClick.bind(this, item)}>Click</button>
 457 </template>
 458 ```
 459 
 460 ### ✅ GOOD: Use Data Attributes for Context
 461 
 462 ```html
 463 <!-- component.html -->
 464 <template>
 465     <template for:each={items} for:item="item">
 466         <button
 467             key={item.id}
 468             data-id={item.id}
 469             data-name={item.name}
 470             data-index={item.index}
 471             onclick={handleItemClick}>
 472             {item.name}
 473         </button>
 474     </template>
 475 </template>
 476 ```
 477 
 478 ```javascript
 479 // component.js
 480 handleItemClick(event) {
 481     const { id, name, index } = event.currentTarget.dataset;
 482     // dataset values are always strings
 483     const indexNum = parseInt(index, 10);
 484 }
 485 ```
 486 
 487 ---
 488 
 489 ## 6. Iteration Anti-Patterns
 490 
 491 ### ❌ BAD: Missing Key in Iteration
 492 
 493 ```html
 494 <!-- LLM forgets key - causes rendering issues -->
 495 <template>
 496     <template for:each={items} for:item="item">
 497         <div>{item.name}</div>  <!-- Missing key! -->
 498     </template>
 499 </template>
 500 ```
 501 
 502 ### ✅ GOOD: Always Include Key
 503 
 504 ```html
 505 <!-- component.html -->
 506 <template>
 507     <template for:each={items} for:item="item">
 508         <div key={item.id}>{item.name}</div>
 509     </template>
 510 </template>
 511 ```
 512 
 513 ### ❌ BAD: Using Index as Key
 514 
 515 ```html
 516 <!-- Anti-pattern: index can cause issues with reordering -->
 517 <template>
 518     <template for:each={items} for:item="item" for:index="index">
 519         <div key={index}>{item.name}</div>
 520     </template>
 521 </template>
 522 ```
 523 
 524 ### ✅ GOOD: Use Unique Identifier as Key
 525 
 526 ```javascript
 527 // If items don't have unique IDs, generate them
 528 connectedCallback() {
 529     this.items = this.rawItems.map((item, index) => ({
 530         ...item,
 531         uniqueKey: `item-${item.name}-${index}`
 532     }));
 533 }
 534 ```
 535 
 536 ```html
 537 <!-- component.html -->
 538 <template>
 539     <template for:each={items} for:item="item">
 540         <div key={item.uniqueKey}>{item.name}</div>
 541     </template>
 542 </template>
 543 ```
 544 
 545 ### ❌ BAD: Nested Iteration Without Proper Keys
 546 
 547 ```html
 548 <!-- PROBLEMATIC -->
 549 <template>
 550     <template for:each={categories} for:item="category">
 551         <div key={category.id}>
 552             <h3>{category.name}</h3>
 553             <template for:each={category.items} for:item="item">
 554                 <!-- Key might conflict with other categories -->
 555                 <p key={item.id}>{item.name}</p>
 556             </template>
 557         </div>
 558     </template>
 559 </template>
 560 ```
 561 
 562 ### ✅ GOOD: Compound Keys for Nested Iteration
 563 
 564 ```javascript
 565 // component.js
 566 get processedCategories() {
 567     return this.categories.map(category => ({
 568         ...category,
 569         items: category.items.map(item => ({
 570             ...item,
 571             compositeKey: `${category.id}-${item.id}`
 572         }))
 573     }));
 574 }
 575 ```
 576 
 577 ```html
 578 <!-- component.html -->
 579 <template>
 580     <template for:each={processedCategories} for:item="category">
 581         <div key={category.id}>
 582             <h3>{category.name}</h3>
 583             <template for:each={category.items} for:item="item">
 584                 <p key={item.compositeKey}>{item.name}</p>
 585             </template>
 586         </div>
 587     </template>
 588 </template>
 589 ```
 590 
 591 ---
 592 
 593 ## 7. Conditional Rendering Issues
 594 
 595 ### ❌ BAD: if:true on Non-Boolean Values
 596 
 597 ```html
 598 <!-- LLM assumes truthy/falsy works like JS - it doesn't always -->
 599 <template>
 600     <!-- String 'false' is truthy! -->
 601     <template if:true={stringValue}>
 602         <p>Shown even for 'false' string!</p>
 603     </template>
 604 
 605     <!-- 0 might not behave as expected -->
 606     <template if:true={count}>
 607         <p>Count: {count}</p>
 608     </template>
 609 </template>
 610 ```
 611 
 612 ### ✅ GOOD: Explicit Boolean Conversion
 613 
 614 ```javascript
 615 // component.js
 616 get hasStringValue() {
 617     return Boolean(this.stringValue) && this.stringValue !== 'false';
 618 }
 619 
 620 get hasCount() {
 621     return this.count !== null && this.count !== undefined && this.count !== 0;
 622 }
 623 ```
 624 
 625 ```html
 626 <!-- component.html -->
 627 <template>
 628     <template if:true={hasStringValue}>
 629         <p>Has value</p>
 630     </template>
 631 
 632     <template if:true={hasCount}>
 633         <p>Count: {count}</p>
 634     </template>
 635 </template>
 636 ```
 637 
 638 ### ❌ BAD: Multiple Conditions Without Else
 639 
 640 ```html
 641 <!-- Verbose and error-prone -->
 642 <template>
 643     <template if:true={isLoading}>
 644         <lightning-spinner></lightning-spinner>
 645     </template>
 646     <template if:true={hasError}>
 647         <p>Error occurred</p>
 648     </template>
 649     <template if:true={hasData}>
 650         <p>Data loaded</p>
 651     </template>
 652 </template>
 653 ```
 654 
 655 ### ✅ GOOD: Use a State Getter
 656 
 657 ```javascript
 658 // component.js
 659 get viewState() {
 660     if (this.isLoading) return 'loading';
 661     if (this.error) return 'error';
 662     if (this.data) return 'success';
 663     return 'empty';
 664 }
 665 
 666 get isLoadingState() { return this.viewState === 'loading'; }
 667 get isErrorState() { return this.viewState === 'error'; }
 668 get isSuccessState() { return this.viewState === 'success'; }
 669 get isEmptyState() { return this.viewState === 'empty'; }
 670 ```
 671 
 672 ```html
 673 <!-- component.html -->
 674 <template>
 675     <template if:true={isLoadingState}>
 676         <lightning-spinner></lightning-spinner>
 677     </template>
 678     <template if:true={isErrorState}>
 679         <c-error-display error={error}></c-error-display>
 680     </template>
 681     <template if:true={isSuccessState}>
 682         <c-data-display data={data}></c-data-display>
 683     </template>
 684     <template if:true={isEmptyState}>
 685         <c-empty-state></c-empty-state>
 686     </template>
 687 </template>
 688 ```
 689 
 690 ---
 691 
 692 ## 8. Slot and Composition Errors
 693 
 694 ### ❌ BAD: Named Slot with Wrong Syntax
 695 
 696 ```html
 697 <!-- LLM uses Vue/React slot syntax -->
 698 <template>
 699     <!-- Wrong: Vue syntax -->
 700     <c-card>
 701         <template v-slot:header>Header</template>
 702     </c-card>
 703 
 704     <!-- Wrong: React children syntax -->
 705     <c-card header="Header Content">
 706         Body Content
 707     </c-card>
 708 </template>
 709 ```
 710 
 711 ### ✅ GOOD: LWC Slot Syntax
 712 
 713 ```html
 714 <!-- Parent component using slots -->
 715 <template>
 716     <c-card>
 717         <span slot="header">Card Header</span>
 718         <p slot="body">Card body content</p>
 719         <button slot="footer">Action</button>
 720     </c-card>
 721 </template>
 722 ```
 723 
 724 ```html
 725 <!-- c-card component template -->
 726 <template>
 727     <article class="slds-card">
 728         <header class="slds-card__header">
 729             <slot name="header"></slot>
 730         </header>
 731         <div class="slds-card__body">
 732             <slot name="body"></slot>
 733             <slot></slot> <!-- Default slot -->
 734         </div>
 735         <footer class="slds-card__footer">
 736             <slot name="footer"></slot>
 737         </footer>
 738     </article>
 739 </template>
 740 ```
 741 
 742 ---
 743 
 744 ## 9. Data Binding Mistakes
 745 
 746 ### ❌ BAD: Two-Way Binding Syntax
 747 
 748 ```html
 749 <!-- LLM uses Angular/Vue two-way binding - doesn't exist in LWC -->
 750 <template>
 751     <input [(ngModel)]="name">  <!-- Angular -->
 752     <input v-model="name">       <!-- Vue -->
 753     <input bind:value={name}>    <!-- Svelte-ish -->
 754 </template>
 755 ```
 756 
 757 ### ✅ GOOD: One-Way Binding with Event Handler
 758 
 759 ```html
 760 <!-- component.html -->
 761 <template>
 762     <lightning-input
 763         label="Name"
 764         value={name}
 765         onchange={handleNameChange}>
 766     </lightning-input>
 767 
 768     <!-- Or standard HTML input -->
 769     <input
 770         type="text"
 771         value={name}
 772         onchange={handleInputChange}
 773         oninput={handleInputChange}>
 774 </template>
 775 ```
 776 
 777 ```javascript
 778 // component.js
 779 name = '';
 780 
 781 handleNameChange(event) {
 782     this.name = event.detail.value;  // lightning-input uses detail.value
 783 }
 784 
 785 handleInputChange(event) {
 786     this.name = event.target.value;  // standard input uses target.value
 787 }
 788 ```
 789 
 790 ### ❌ BAD: Direct Property Mutation in Template
 791 
 792 ```html
 793 <!-- Cannot mutate in template -->
 794 <template>
 795     <button onclick={count++}>Increment</button>
 796 </template>
 797 ```
 798 
 799 ### ✅ GOOD: Mutate in Handler
 800 
 801 ```javascript
 802 // component.js
 803 count = 0;
 804 
 805 handleIncrement() {
 806     this.count++;
 807 }
 808 ```
 809 
 810 ```html
 811 <!-- component.html -->
 812 <template>
 813     <button onclick={handleIncrement}>Increment ({count})</button>
 814 </template>
 815 ```
 816 
 817 ---
 818 
 819 ## 10. Style and Class Binding
 820 
 821 ### ❌ BAD: Dynamic Styles in Template
 822 
 823 ```html
 824 <!-- LLM uses React/Vue style binding - doesn't work in LWC -->
 825 <template>
 826     <div style="color: {textColor}; font-size: {fontSize}px">
 827         Content
 828     </div>
 829 
 830     <div style={{ color: textColor, fontSize: fontSize + 'px' }}>
 831         Content
 832     </div>
 833 </template>
 834 ```
 835 
 836 ### ✅ GOOD: CSS Custom Properties (Recommended)
 837 
 838 ```javascript
 839 // component.js
 840 @api textColor = 'blue';
 841 @api fontSize = 14;
 842 
 843 renderedCallback() {
 844     this.template.host.style.setProperty('--text-color', this.textColor);
 845     this.template.host.style.setProperty('--font-size', `${this.fontSize}px`);
 846 }
 847 ```
 848 
 849 ```css
 850 /* component.css */
 851 .dynamic-text {
 852     color: var(--text-color, black);
 853     font-size: var(--font-size, 14px);
 854 }
 855 ```
 856 
 857 ```html
 858 <!-- component.html -->
 859 <template>
 860     <div class="dynamic-text">Content</div>
 861 </template>
 862 ```
 863 
 864 ### ✅ GOOD: Computed Style String (When Necessary)
 865 
 866 ```javascript
 867 // component.js
 868 get dynamicStyle() {
 869     return `color: ${this.textColor}; font-size: ${this.fontSize}px;`;
 870 }
 871 ```
 872 
 873 ```html
 874 <!-- component.html -->
 875 <template>
 876     <div style={dynamicStyle}>Content</div>
 877 </template>
 878 ```
 879 
 880 ### ❌ BAD: Dynamic Class with Expression
 881 
 882 ```html
 883 <!-- DOES NOT WORK -->
 884 <template>
 885     <div class="base {isActive ? 'active' : ''}">Content</div>
 886     <div class={`base ${isActive ? 'active' : ''}`}>Content</div>
 887 </template>
 888 ```
 889 
 890 ### ✅ GOOD: Computed Class String
 891 
 892 ```javascript
 893 // component.js
 894 get containerClass() {
 895     return `base ${this.isActive ? 'active' : ''} ${this.isHighlighted ? 'highlighted' : ''}`.trim();
 896 }
 897 ```
 898 
 899 ```html
 900 <!-- component.html -->
 901 <template>
 902     <div class={containerClass}>Content</div>
 903 </template>
 904 ```
 905 
 906 ---
 907 
 908 ## Quick Reference: Template Rules
 909 
 910 | What You Want | Wrong (Other Frameworks) | Right (LWC) |
 911 |---------------|-------------------------|-------------|
 912 | Arithmetic | `{a + b}` | Getter: `get sum() { return a + b; }` |
 913 | String concat | `{a + ' ' + b}` | Getter with template literal |
 914 | Ternary | `{x ? a : b}` | Getter or if:true/if:false |
 915 | Method call | `{items.length}` | Getter: `get count() { return items.length; }` |
 916 | Comparison | `if:true={x > 5}` | Getter: `get isBig() { return x > 5; }` |
 917 | Logical AND | `if:true={a && b}` | Getter: `get both() { return a && b; }` |
 918 | Negation | `if:true={!x}` | `if:false={x}` or getter |
 919 | Object literal | `config={{ key: val }}` | Class property |
 920 | Event args | `onclick={fn(x)}` | Use data attributes |
 921 | Two-way bind | `value={name}` auto-update | `value={name}` + `onchange` |
 922 
 923 ---
 924 
 925 ## Validation Checklist
 926 
 927 Before deploying LWC templates, verify:
 928 
 929 - [ ] No arithmetic operations (`+`, `-`, `*`, `/`)
 930 - [ ] No ternary operators (`? :`)
 931 - [ ] No object/array literals (`{}`, `[]`)
 932 - [ ] No method calls (`.length`, `.toUpperCase()`)
 933 - [ ] No comparisons (`>`, `<`, `===`, `!==`)
 934 - [ ] No logical operators (`&&`, `||`, `!`)
 935 - [ ] All iterations have unique `key` attributes
 936 - [ ] Event handlers don't have inline arguments
 937 - [ ] Dynamic styles use CSS custom properties or computed strings
 938 
 939 ---
 940 
 941 ## Reference
 942 
 943 - **LWC Best Practices**: See `references/lwc-best-practices.md`
 944 - **Component Patterns**: See `references/component-patterns.md`
 945 - **Source**: [Salesforce Diaries - LLM Mistakes](https://salesforcediaries.com/2026/01/16/llm-mistakes-in-apex-lwc-salesforce-code-generation-rules/)
