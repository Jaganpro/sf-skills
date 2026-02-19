<!-- Parent: sf-lwc/SKILL.md -->
   1 # Accessibility Guide for LWC
   2 
   3 Comprehensive guide to building WCAG 2.1 AA compliant Lightning Web Components.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [Accessibility Standards](#accessibility-standards)
  10 2. [Semantic HTML](#semantic-html)
  11 3. [ARIA Attributes](#aria-attributes)
  12 4. [Keyboard Navigation](#keyboard-navigation)
  13 5. [Focus Management](#focus-management)
  14 6. [Color and Contrast](#color-and-contrast)
  15 7. [Screen Reader Support](#screen-reader-support)
  16 8. [Live Regions](#live-regions)
  17 9. [Form Accessibility](#form-accessibility)
  18 10. [Common Patterns](#common-patterns)
  19 11. [Testing](#testing)
  20 12. [Tools and Resources](#tools-and-resources)
  21 
  22 ---
  23 
  24 ## Accessibility Standards
  25 
  26 ### WCAG 2.1 AA Compliance
  27 
  28 All Lightning Web Components should meet WCAG 2.1 Level AA standards.
  29 
  30 | Principle | Description |
  31 |-----------|-------------|
  32 | **Perceivable** | Information must be presentable to users in ways they can perceive |
  33 | **Operable** | UI components must be operable (keyboard, mouse, voice) |
  34 | **Understandable** | Information and UI must be understandable |
  35 | **Robust** | Content must work with assistive technologies |
  36 
  37 ### Key Requirements
  38 
  39 | Requirement | Standard | Implementation |
  40 |-------------|----------|----------------|
  41 | **Color contrast** | 4.5:1 for normal text, 3:1 for large text | Use SLDS color tokens |
  42 | **Keyboard navigation** | All interactive elements accessible via keyboard | Tab order, Enter/Space triggers |
  43 | **Screen reader support** | ARIA labels, roles, live regions | Proper semantic HTML + ARIA |
  44 | **Focus indicators** | Visible focus state | Use SLDS focus utilities |
  45 | **Alternative text** | All images have alt text | `alt` attribute on images |
  46 
  47 ---
  48 
  49 ## Semantic HTML
  50 
  51 ### Use Proper HTML Elements
  52 
  53 ```html
  54 <!-- BAD: Non-semantic markup -->
  55 <div onclick={handleClick}>Click me</div>
  56 
  57 <!-- GOOD: Semantic button -->
  58 <button onclick={handleClick}>Click me</button>
  59 ```
  60 
  61 ### Headings Hierarchy
  62 
  63 ```html
  64 <!-- BAD: Skipping heading levels -->
  65 <h1>Page Title</h1>
  66 <h3>Subsection</h3> <!-- Skipped h2 -->
  67 
  68 <!-- GOOD: Logical heading structure -->
  69 <h1>Page Title</h1>
  70 <h2>Main Section</h2>
  71 <h3>Subsection</h3>
  72 ```
  73 
  74 ### Landmarks
  75 
  76 ```html
  77 <template>
  78     <header class="slds-page-header">
  79         <h1>Dashboard</h1>
  80     </header>
  81 
  82     <nav aria-label="Primary navigation">
  83         <ul>
  84             <li><a href="#home">Home</a></li>
  85             <li><a href="#accounts">Accounts</a></li>
  86         </ul>
  87     </nav>
  88 
  89     <main>
  90         <article>
  91             <h2>Account Details</h2>
  92             <!-- Content -->
  93         </article>
  94     </main>
  95 
  96     <aside aria-label="Related information">
  97         <!-- Sidebar content -->
  98     </aside>
  99 
 100     <footer>
 101         <p>Copyright 2025</p>
 102     </footer>
 103 </template>
 104 ```
 105 
 106 ---
 107 
 108 ## ARIA Attributes
 109 
 110 ### ARIA Labels
 111 
 112 ```html
 113 <!-- Icon button without visible text -->
 114 <button aria-label="Delete record" onclick={handleDelete}>
 115     <lightning-icon icon-name="utility:delete" size="small"></lightning-icon>
 116 </button>
 117 
 118 <!-- Form field with additional context -->
 119 <lightning-input
 120     label="Phone"
 121     aria-describedby="phone-help"
 122     value={phone}
 123     onchange={handlePhoneChange}>
 124 </lightning-input>
 125 <div id="phone-help" class="slds-text-color_weak">
 126     Enter phone number with country code
 127 </div>
 128 ```
 129 
 130 ### ARIA Roles
 131 
 132 ```html
 133 <!-- Custom list -->
 134 <div role="list">
 135     <div role="listitem">Item 1</div>
 136     <div role="listitem">Item 2</div>
 137 </div>
 138 
 139 <!-- Alert message -->
 140 <div role="alert" class="slds-notify slds-notify_alert">
 141     <span class="slds-assistive-text">Error</span>
 142     <p>Form validation failed</p>
 143 </div>
 144 
 145 <!-- Dialog/Modal -->
 146 <div role="dialog"
 147      aria-modal="true"
 148      aria-labelledby="modal-heading"
 149      aria-describedby="modal-description">
 150     <h2 id="modal-heading">Confirm Action</h2>
 151     <p id="modal-description">Are you sure you want to delete this record?</p>
 152 </div>
 153 ```
 154 
 155 ### ARIA States
 156 
 157 ```html
 158 <!-- Expandable section -->
 159 <button
 160     aria-expanded={isExpanded}
 161     aria-controls="details-section"
 162     onclick={toggleExpanded}>
 163     Show Details
 164 </button>
 165 <div id="details-section" class={sectionClass}>
 166     <!-- Details content -->
 167 </div>
 168 
 169 <!-- Loading state -->
 170 <div aria-busy={isLoading}>
 171     <template lwc:if={isLoading}>
 172         <lightning-spinner alternative-text="Loading data"></lightning-spinner>
 173     </template>
 174     <template lwc:else>
 175         <!-- Content -->
 176     </template>
 177 </div>
 178 
 179 <!-- Required field -->
 180 <lightning-input
 181     label="Name"
 182     required
 183     aria-required="true"
 184     value={name}>
 185 </lightning-input>
 186 ```
 187 
 188 ---
 189 
 190 ## Keyboard Navigation
 191 
 192 ### Tab Order
 193 
 194 ```html
 195 <!-- Natural tab order -->
 196 <form>
 197     <lightning-input label="First Name" tabindex="0"></lightning-input>
 198     <lightning-input label="Last Name" tabindex="0"></lightning-input>
 199     <lightning-button label="Submit" tabindex="0"></lightning-button>
 200 </form>
 201 
 202 <!-- Skip to main content link -->
 203 <a href="#main-content" class="slds-assistive-text slds-assistive-text_focus">
 204     Skip to main content
 205 </a>
 206 <main id="main-content">
 207     <!-- Content -->
 208 </main>
 209 ```
 210 
 211 ### Keyboard Event Handlers
 212 
 213 ```javascript
 214 // accountCard.js
 215 export default class AccountCard extends LightningElement {
 216     handleKeyDown(event) {
 217         // Enter or Space activates
 218         if (event.key === 'Enter' || event.key === ' ') {
 219             event.preventDefault();
 220             this.handleSelect();
 221         }
 222 
 223         // Arrow navigation
 224         if (event.key === 'ArrowDown') {
 225             event.preventDefault();
 226             this.focusNextItem();
 227         } else if (event.key === 'ArrowUp') {
 228             event.preventDefault();
 229             this.focusPreviousItem();
 230         }
 231 
 232         // Escape closes
 233         if (event.key === 'Escape') {
 234             this.handleClose();
 235         }
 236     }
 237 
 238     focusNextItem() {
 239         const items = this.template.querySelectorAll('[role="listitem"]');
 240         const currentIndex = Array.from(items).indexOf(document.activeElement);
 241         const nextIndex = (currentIndex + 1) % items.length;
 242         items[nextIndex].focus();
 243     }
 244 
 245     focusPreviousItem() {
 246         const items = this.template.querySelectorAll('[role="listitem"]');
 247         const currentIndex = Array.from(items).indexOf(document.activeElement);
 248         const prevIndex = currentIndex === 0 ? items.length - 1 : currentIndex - 1;
 249         items[prevIndex].focus();
 250     }
 251 }
 252 ```
 253 
 254 ```html
 255 <!-- accountCard.html -->
 256 <template>
 257     <div role="list">
 258         <template for:each={accounts} for:item="account">
 259             <div key={account.Id}
 260                  role="listitem"
 261                  tabindex="0"
 262                  onkeydown={handleKeyDown}
 263                  onclick={handleSelect}
 264                  data-id={account.Id}>
 265                 {account.Name}
 266             </div>
 267         </template>
 268     </div>
 269 </template>
 270 ```
 271 
 272 ---
 273 
 274 ## Focus Management
 275 
 276 ### Focus Trap in Modals
 277 
 278 ```javascript
 279 // composableModal.js
 280 export default class ComposableModal extends LightningElement {
 281     _focusableElements = [];
 282     _isOpen = false;
 283 
 284     @api
 285     toggleModal() {
 286         this._isOpen = !this._isOpen;
 287 
 288         if (this._isOpen) {
 289             // Capture focusable elements
 290             this._focusableElements = this.getFocusableElements();
 291 
 292             // Focus first element
 293             requestAnimationFrame(() => {
 294                 this._focusableElements[0]?.focus();
 295             });
 296 
 297             // Add keyboard listener
 298             window.addEventListener('keydown', this._handleKeyDown);
 299 
 300             // Store previous focus
 301             this._previousFocus = document.activeElement;
 302         } else {
 303             // Remove keyboard listener
 304             window.removeEventListener('keydown', this._handleKeyDown);
 305 
 306             // Restore focus
 307             this._previousFocus?.focus();
 308         }
 309     }
 310 
 311     getFocusableElements() {
 312         const selector = [
 313             'a[href]',
 314             'button:not([disabled])',
 315             'input:not([disabled])',
 316             'select:not([disabled])',
 317             'textarea:not([disabled])',
 318             '[tabindex]:not([tabindex="-1"])'
 319         ].join(',');
 320 
 321         return Array.from(this.template.querySelectorAll(selector));
 322     }
 323 
 324     _handleKeyDown = (event) => {
 325         if (event.key === 'Tab') {
 326             this.trapFocus(event);
 327         } else if (event.key === 'Escape') {
 328             this.toggleModal();
 329         }
 330     }
 331 
 332     trapFocus(event) {
 333         const firstElement = this._focusableElements[0];
 334         const lastElement = this._focusableElements[this._focusableElements.length - 1];
 335         const activeElement = this.template.activeElement;
 336 
 337         if (event.shiftKey) {
 338             // Shift+Tab: Moving backward
 339             if (activeElement === firstElement) {
 340                 event.preventDefault();
 341                 lastElement.focus();
 342             }
 343         } else {
 344             // Tab: Moving forward
 345             if (activeElement === lastElement) {
 346                 event.preventDefault();
 347                 firstElement.focus();
 348             }
 349         }
 350     }
 351 
 352     disconnectedCallback() {
 353         window.removeEventListener('keydown', this._handleKeyDown);
 354     }
 355 }
 356 ```
 357 
 358 ### Managing Focus After Actions
 359 
 360 ```javascript
 361 handleDelete(event) {
 362     const itemId = event.target.dataset.id;
 363     const itemIndex = this.items.findIndex(item => item.Id === itemId);
 364 
 365     // Delete item
 366     this.items = this.items.filter(item => item.Id !== itemId);
 367 
 368     // Focus next item or previous if last item deleted
 369     requestAnimationFrame(() => {
 370         const focusIndex = itemIndex < this.items.length ? itemIndex : itemIndex - 1;
 371         if (focusIndex >= 0) {
 372             const nextItem = this.template.querySelector(`[data-id="${this.items[focusIndex].Id}"]`);
 373             nextItem?.focus();
 374         }
 375     });
 376 }
 377 ```
 378 
 379 ---
 380 
 381 ## Color and Contrast
 382 
 383 ### Use SLDS Color Tokens
 384 
 385 ```css
 386 /* BAD: Hardcoded colors */
 387 .my-component {
 388     color: #333333;
 389     background-color: #ffffff;
 390     border-color: #dddddd;
 391 }
 392 
 393 /* GOOD: SLDS tokens with proper contrast */
 394 .my-component {
 395     color: var(--slds-g-color-on-surface, #181818);
 396     background-color: var(--slds-g-color-surface-container-1, #ffffff);
 397     border-color: var(--slds-g-color-border-1, #c9c9c9);
 398 }
 399 ```
 400 
 401 ### Testing Contrast
 402 
 403 ```html
 404 <!-- Text: 4.5:1 minimum contrast ratio -->
 405 <p class="slds-text-body_regular">Regular body text</p>
 406 
 407 <!-- Large text (18pt+): 3:1 minimum -->
 408 <h1 class="slds-text-heading_large">Large heading</h1>
 409 
 410 <!-- Links: Must be distinguishable from surrounding text -->
 411 <p>
 412     Visit our <a href="/help" class="slds-text-link">help center</a> for support.
 413 </p>
 414 ```
 415 
 416 ### Color Independence
 417 
 418 ```html
 419 <!-- BAD: Relies only on color to convey status -->
 420 <span class="text-red">Error</span>
 421 
 422 <!-- GOOD: Uses icon + text + color -->
 423 <span class="slds-text-color_error">
 424     <lightning-icon icon-name="utility:error" size="x-small"></lightning-icon>
 425     Error
 426 </span>
 427 
 428 <!-- GOOD: Status indicators with patterns -->
 429 <div class="slds-badge slds-theme_error">
 430     <lightning-icon icon-name="utility:close" size="xx-small"></lightning-icon>
 431     Failed
 432 </div>
 433 ```
 434 
 435 ---
 436 
 437 ## Screen Reader Support
 438 
 439 ### Assistive Text
 440 
 441 ```html
 442 <!-- Hidden text for screen readers -->
 443 <span class="slds-assistive-text">Required field</span>
 444 <lightning-input label="Email" required value={email}></lightning-input>
 445 
 446 <!-- Button with icon only -->
 447 <button aria-label="Edit record">
 448     <lightning-icon icon-name="utility:edit" size="small"></lightning-icon>
 449     <span class="slds-assistive-text">Edit</span>
 450 </button>
 451 
 452 <!-- Loading state announcement -->
 453 <template lwc:if={isLoading}>
 454     <span class="slds-assistive-text">Loading data, please wait</span>
 455     <lightning-spinner size="small"></lightning-spinner>
 456 </template>
 457 ```
 458 
 459 ### Image Alternative Text
 460 
 461 ```html
 462 <!-- Decorative images (no alt needed, hide from screen readers) -->
 463 <img src="decorative-icon.png" alt="" role="presentation">
 464 
 465 <!-- Informative images (descriptive alt text) -->
 466 <img src="chart.png" alt="Sales trend showing 15% increase over last quarter">
 467 
 468 <!-- Functional images (describe action) -->
 469 <a href="/profile">
 470     <img src="user-avatar.png" alt="View your profile">
 471 </a>
 472 ```
 473 
 474 ---
 475 
 476 ## Live Regions
 477 
 478 ### ARIA Live Regions
 479 
 480 ```javascript
 481 // notificationComponent.js
 482 export default class NotificationComponent extends LightningElement {
 483     @track messages = [];
 484 
 485     addMessage(message, type = 'info') {
 486         const id = Date.now();
 487         this.messages = [...this.messages, { id, message, type }];
 488 
 489         // Auto-remove after 5 seconds
 490         setTimeout(() => {
 491             this.messages = this.messages.filter(m => m.id !== id);
 492         }, 5000);
 493     }
 494 }
 495 ```
 496 
 497 ```html
 498 <!-- notificationComponent.html -->
 499 <template>
 500     <!-- Polite: Announced after current speech -->
 501     <div aria-live="polite" aria-atomic="true" class="slds-assistive-text">
 502         <template for:each={messages} for:item="msg">
 503             <p key={msg.id}>{msg.message}</p>
 504         </template>
 505     </div>
 506 
 507     <!-- Visual notifications -->
 508     <div class="slds-notify-container">
 509         <template for:each={messages} for:item="msg">
 510             <div key={msg.id} class={msg.type} role="status">
 511                 <p>{msg.message}</p>
 512             </div>
 513         </template>
 514     </div>
 515 </template>
 516 ```
 517 
 518 ### Assertive vs Polite
 519 
 520 ```html
 521 <!-- Polite: Non-urgent updates (search results, status changes) -->
 522 <div aria-live="polite" class="slds-assistive-text">
 523     {searchResultsCount} results found
 524 </div>
 525 
 526 <!-- Assertive: Urgent messages (errors, warnings) -->
 527 <div aria-live="assertive" role="alert" class="slds-notify slds-notify_alert">
 528     <span class="slds-assistive-text">Error</span>
 529     Form submission failed. Please correct the errors and try again.
 530 </div>
 531 ```
 532 
 533 ---
 534 
 535 ## Form Accessibility
 536 
 537 ### Accessible Form Fields
 538 
 539 ```html
 540 <template>
 541     <form onsubmit={handleSubmit}>
 542         <!-- Required field with validation -->
 543         <lightning-input
 544             label="Email"
 545             type="email"
 546             name="email"
 547             required
 548             value={email}
 549             onchange={handleEmailChange}
 550             message-when-value-missing="Email is required"
 551             message-when-bad-input="Please enter a valid email">
 552         </lightning-input>
 553 
 554         <!-- Field with help text -->
 555         <lightning-input
 556             label="Phone"
 557             type="tel"
 558             value={phone}
 559             field-level-help="Enter phone number with country code"
 560             aria-describedby="phone-help"
 561             onchange={handlePhoneChange}>
 562         </lightning-input>
 563         <div id="phone-help" class="slds-text-color_weak slds-m-top_xx-small">
 564             Format: +1 (555) 555-5555
 565         </div>
 566 
 567         <!-- Error state -->
 568         <template lwc:if={errors.industry}>
 569             <lightning-input
 570                 label="Industry"
 571                 value={industry}
 572                 variant="label-hidden"
 573                 aria-invalid="true"
 574                 aria-describedby="industry-error"
 575                 class="slds-has-error">
 576             </lightning-input>
 577             <div id="industry-error" class="slds-form-element__help" role="alert">
 578                 {errors.industry}
 579             </div>
 580         </template>
 581 
 582         <!-- Submit button -->
 583         <lightning-button
 584             type="submit"
 585             label="Save"
 586             variant="brand"
 587             disabled={isSubmitting}>
 588         </lightning-button>
 589     </form>
 590 </template>
 591 ```
 592 
 593 ### Fieldset and Legend
 594 
 595 ```html
 596 <!-- Radio button group -->
 597 <fieldset class="slds-form-element">
 598     <legend class="slds-form-element__legend slds-form-element__label">
 599         Contact Method <abbr class="slds-required" title="required">*</abbr>
 600     </legend>
 601     <div class="slds-form-element__control">
 602         <lightning-radio-group
 603             name="contactMethod"
 604             label="Contact Method"
 605             options={contactOptions}
 606             value={selectedMethod}
 607             onchange={handleMethodChange}
 608             variant="label-hidden"
 609             required>
 610         </lightning-radio-group>
 611     </div>
 612 </fieldset>
 613 ```
 614 
 615 ---
 616 
 617 ## Common Patterns
 618 
 619 ### Accessible Tabs
 620 
 621 ```javascript
 622 // tabsComponent.js
 623 export default class TabsComponent extends LightningElement {
 624     @track activeTab = 'tab1';
 625 
 626     handleTabKeyDown(event) {
 627         const tabs = Array.from(this.template.querySelectorAll('[role="tab"]'));
 628         const currentIndex = tabs.indexOf(event.target);
 629 
 630         let nextIndex;
 631         if (event.key === 'ArrowRight') {
 632             nextIndex = (currentIndex + 1) % tabs.length;
 633         } else if (event.key === 'ArrowLeft') {
 634             nextIndex = currentIndex === 0 ? tabs.length - 1 : currentIndex - 1;
 635         } else if (event.key === 'Home') {
 636             nextIndex = 0;
 637         } else if (event.key === 'End') {
 638             nextIndex = tabs.length - 1;
 639         }
 640 
 641         if (nextIndex !== undefined) {
 642             event.preventDefault();
 643             tabs[nextIndex].focus();
 644             this.activeTab = tabs[nextIndex].dataset.tab;
 645         }
 646     }
 647 
 648     handleTabClick(event) {
 649         this.activeTab = event.currentTarget.dataset.tab;
 650     }
 651 }
 652 ```
 653 
 654 ```html
 655 <!-- tabsComponent.html -->
 656 <template>
 657     <div class="slds-tabs_default">
 658         <ul role="tablist" class="slds-tabs_default__nav">
 659             <li class="slds-tabs_default__item" role="presentation">
 660                 <a role="tab"
 661                    tabindex={tab1Tabindex}
 662                    aria-selected={isTab1Active}
 663                    aria-controls="tab1-panel"
 664                    data-tab="tab1"
 665                    onclick={handleTabClick}
 666                    onkeydown={handleTabKeyDown}>
 667                     Tab 1
 668                 </a>
 669             </li>
 670             <li class="slds-tabs_default__item" role="presentation">
 671                 <a role="tab"
 672                    tabindex={tab2Tabindex}
 673                    aria-selected={isTab2Active}
 674                    aria-controls="tab2-panel"
 675                    data-tab="tab2"
 676                    onclick={handleTabClick}
 677                    onkeydown={handleTabKeyDown}>
 678                     Tab 2
 679                 </a>
 680             </li>
 681         </ul>
 682 
 683         <div id="tab1-panel"
 684              role="tabpanel"
 685              aria-labelledby="tab1"
 686              class={tab1PanelClass}>
 687             <!-- Tab 1 content -->
 688         </div>
 689 
 690         <div id="tab2-panel"
 691              role="tabpanel"
 692              aria-labelledby="tab2"
 693              class={tab2PanelClass}>
 694             <!-- Tab 2 content -->
 695         </div>
 696     </div>
 697 </template>
 698 ```
 699 
 700 ### Accessible Data Table
 701 
 702 ```html
 703 <template>
 704     <table class="slds-table slds-table_bordered" role="grid">
 705         <thead>
 706             <tr>
 707                 <th scope="col" role="columnheader">
 708                     <span class="slds-truncate">Account Name</span>
 709                 </th>
 710                 <th scope="col" role="columnheader">
 711                     <span class="slds-truncate">Industry</span>
 712                 </th>
 713                 <th scope="col" role="columnheader">
 714                     <span class="slds-truncate">Actions</span>
 715                 </th>
 716             </tr>
 717         </thead>
 718         <tbody>
 719             <template for:each={accounts} for:item="account">
 720                 <tr key={account.Id} role="row">
 721                     <th scope="row" role="gridcell">
 722                         <a href={account.link}>{account.Name}</a>
 723                     </th>
 724                     <td role="gridcell">
 725                         {account.Industry}
 726                     </td>
 727                     <td role="gridcell">
 728                         <button aria-label={account.editLabel}
 729                                 data-id={account.Id}
 730                                 onclick={handleEdit}>
 731                             <lightning-icon icon-name="utility:edit" size="x-small"></lightning-icon>
 732                         </button>
 733                     </td>
 734                 </tr>
 735             </template>
 736         </tbody>
 737     </table>
 738 </template>
 739 ```
 740 
 741 ---
 742 
 743 ## Testing
 744 
 745 ### Automated Testing
 746 
 747 ```javascript
 748 // Jest accessibility tests
 749 it('has proper ARIA labels', () => {
 750     const element = createElement('c-my-component', {
 751         is: MyComponent
 752     });
 753     document.body.appendChild(element);
 754 
 755     const button = element.shadowRoot.querySelector('button');
 756     expect(button.getAttribute('aria-label')).toBeTruthy();
 757 });
 758 
 759 it('manages focus when modal opens', async () => {
 760     const element = createElement('c-modal', { is: Modal });
 761     document.body.appendChild(element);
 762 
 763     element.openModal();
 764     await flushPromises();
 765 
 766     const firstFocusable = element.shadowRoot.querySelector('.focusable');
 767     expect(document.activeElement).toBe(firstFocusable);
 768 });
 769 
 770 it('announces status changes to screen readers', async () => {
 771     const element = createElement('c-notification', {
 772         is: Notification
 773     });
 774     document.body.appendChild(element);
 775 
 776     element.showMessage('Success');
 777     await flushPromises();
 778 
 779     const liveRegion = element.shadowRoot.querySelector('[aria-live]');
 780     expect(liveRegion.textContent).toContain('Success');
 781 });
 782 ```
 783 
 784 ### Manual Testing Checklist
 785 
 786 - [ ] Navigate entire component using only keyboard (Tab, Shift+Tab, Enter, Space, Arrows)
 787 - [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
 788 - [ ] Verify color contrast ratios (4.5:1 minimum for text)
 789 - [ ] Test at 200% zoom
 790 - [ ] Verify focus indicators are visible
 791 - [ ] Test with high contrast mode
 792 - [ ] Verify all interactive elements have accessible names
 793 - [ ] Test form validation announcements
 794 
 795 ---
 796 
 797 ## Tools and Resources
 798 
 799 ### Browser Extensions
 800 
 801 | Tool | Purpose |
 802 |------|---------|
 803 | **axe DevTools** | Automated accessibility testing |
 804 | **Lighthouse** | Built into Chrome DevTools, accessibility audit |
 805 | **WAVE** | Visual accessibility evaluation |
 806 | **Color Contrast Analyzer** | Check WCAG contrast compliance |
 807 
 808 ### Screen Readers
 809 
 810 | Platform | Screen Reader |
 811 |----------|---------------|
 812 | Windows | NVDA (free), JAWS |
 813 | macOS | VoiceOver (built-in) |
 814 | iOS | VoiceOver (built-in) |
 815 | Android | TalkBack (built-in) |
 816 
 817 ### Testing Commands
 818 
 819 ```bash
 820 # Run axe accessibility tests
 821 npm install --save-dev @axe-core/cli
 822 axe https://your-app.lightning.force.com
 823 
 824 # Lighthouse CLI
 825 npm install -g lighthouse
 826 lighthouse https://your-app.lightning.force.com --only-categories=accessibility
 827 ```
 828 
 829 ### Resources
 830 
 831 - [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
 832 - [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
 833 - [Salesforce Lightning Design System Accessibility](https://www.lightningdesignsystem.com/accessibility/overview/)
 834 - [WebAIM Resources](https://webaim.org/resources/)
 835 
 836 ---
 837 
 838 ## Related Resources
 839 
 840 - [component-patterns.md](component-patterns.md) - Implementation patterns
 841 - [jest-testing.md](jest-testing.md) - Testing strategies
 842 - [performance-guide.md](performance-guide.md) - Performance optimization
