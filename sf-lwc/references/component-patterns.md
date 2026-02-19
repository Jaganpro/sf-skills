<!-- Parent: sf-lwc/SKILL.md -->
   1 # LWC Component Patterns
   2 
   3 Comprehensive code examples for common Lightning Web Component patterns.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [PICKLES Framework Details](#pickles-framework-details)
  10 2. [Wire Service Patterns](#wire-service-patterns)
  11    - [Wire vs Imperative Apex Calls](#wire-vs-imperative-apex-calls)
  12 3. [GraphQL Patterns](#graphql-patterns)
  13 4. [Modal Component Pattern](#modal-component-pattern)
  14 5. [Record Picker Pattern](#record-picker-pattern)
  15 6. [Workspace API Pattern](#workspace-api-pattern)
  16 7. [Parent-Child Communication](#parent-child-communication)
  17 8. [Sibling Communication (via Parent)](#sibling-communication-via-parent)
  18 9. [Navigation Patterns](#navigation-patterns)
  19 10. [TypeScript Patterns](#typescript-patterns)
  20 11. [Apex Controller Patterns](#apex-controller-patterns)
  21 
  22 ---
  23 
  24 ## PICKLES Framework Details
  25 
  26 ### P - Prototype
  27 
  28 **Purpose**: Validate ideas early before full implementation.
  29 
  30 | Action | Description |
  31 |--------|-------------|
  32 | Wireframe | Create high-level component sketches |
  33 | Mock Data | Use sample data to test functionality |
  34 | Stakeholder Review | Gather feedback before development |
  35 | Separation of Concerns | Break into smaller functional pieces |
  36 
  37 ```javascript
  38 // Mock data pattern for prototyping
  39 const MOCK_ACCOUNTS = [
  40     { Id: '001MOCK001', Name: 'Acme Corp', Industry: 'Technology' },
  41     { Id: '001MOCK002', Name: 'Global Inc', Industry: 'Finance' }
  42 ];
  43 
  44 export default class AccountPrototype extends LightningElement {
  45     accounts = MOCK_ACCOUNTS; // Replace with wire/Apex later
  46 }
  47 ```
  48 
  49 ### I - Integrate
  50 
  51 **Purpose**: Determine how components interact with data systems.
  52 
  53 **Integration Checklist**:
  54 - [ ] Implement error handling with clear user notifications
  55 - [ ] Add loading spinners to prevent duplicate requests
  56 - [ ] Use LDS for single-object operations (minimizes DML)
  57 - [ ] Respect FLS and CRUD in Apex implementations
  58 - [ ] Store `wiredResult` for `refreshApex()` support
  59 
  60 ### C - Composition
  61 
  62 **Purpose**: Structure how LWCs nest and communicate.
  63 
  64 **Best Practices**:
  65 - Maintain shallow component hierarchies (max 3-4 levels)
  66 - Single responsibility per component
  67 - Clean up subscriptions in `disconnectedCallback()`
  68 - Use custom events purposefully, not for every interaction
  69 
  70 ```javascript
  71 // Parent-managed composition pattern
  72 // parent.js
  73 handleChildEvent(event) {
  74     this.selectedId = event.detail.id;
  75     // Update child via @api
  76     this.template.querySelector('c-child').selectedId = this.selectedId;
  77 }
  78 ```
  79 
  80 ### K - Kinetics
  81 
  82 **Purpose**: Manage user interaction and event responsiveness.
  83 
  84 ```javascript
  85 // Debounce pattern for search
  86 delayTimeout;
  87 
  88 handleSearchChange(event) {
  89     const searchTerm = event.target.value;
  90     clearTimeout(this.delayTimeout);
  91     this.delayTimeout = setTimeout(() => {
  92         this.dispatchEvent(new CustomEvent('search', {
  93             detail: { searchTerm }
  94         }));
  95     }, 300);
  96 }
  97 ```
  98 
  99 ### L - Libraries
 100 
 101 **Purpose**: Leverage Salesforce-provided and platform tools.
 102 
 103 **Recommended Platform Features**:
 104 
 105 | API/Module | Use Case |
 106 |------------|----------|
 107 | `lightning/navigation` | Page/record navigation |
 108 | `lightning/uiRecordApi` | LDS operations (getRecord, updateRecord) |
 109 | `lightning/platformShowToastEvent` | User notifications |
 110 | `lightning/modal` | Native modal dialogs |
 111 | Base Components | Pre-built UI (button, input, datatable) |
 112 | `lightning/refresh` | Dispatch refresh events |
 113 
 114 **Avoid reinventing** what base components already provide!
 115 
 116 ### E - Execution
 117 
 118 **Purpose**: Optimize performance and resource efficiency.
 119 
 120 **Performance Checklist**:
 121 - [ ] Lazy load with `if:true` / `lwc:if`
 122 - [ ] Use `key` directive in iterations
 123 - [ ] Cache computed values in getters
 124 - [ ] Avoid property updates that trigger re-renders
 125 - [ ] Use browser DevTools Performance tab
 126 
 127 ### S - Security
 128 
 129 **Purpose**: Enforce access control and data protection.
 130 
 131 ```apex
 132 // Secure Apex pattern
 133 @AuraEnabled(cacheable=true)
 134 public static List<Account> getAccounts(String searchTerm) {
 135     String searchKey = '%' + String.escapeSingleQuotes(searchTerm) + '%';
 136     return [
 137         SELECT Id, Name, Industry
 138         FROM Account
 139         WHERE Name LIKE :searchKey
 140         WITH SECURITY_ENFORCED
 141         LIMIT 50
 142     ];
 143 }
 144 ```
 145 
 146 ---
 147 
 148 ## Wire Service Patterns
 149 
 150 ### Wire vs Imperative Apex Calls
 151 
 152 LWC can interact with Apex in two ways: **@wire** (reactive/declarative) and **imperative calls** (manual/programmatic). Understanding when to use each is critical for building performant, maintainable components.
 153 
 154 #### Quick Comparison
 155 
 156 ```
 157 ┌─────────────────────────────────────────────────────────────────────────────────────┐
 158 │                    WIRE vs IMPERATIVE APEX CALLS                                     │
 159 ├──────────────────┬──────────────────────────────┬────────────────────────────────────┤
 160 │    Aspect        │      Wire (@wire)            │      Imperative Calls              │
 161 ├──────────────────┼──────────────────────────────┼────────────────────────────────────┤
 162 │ Execution        │ Automatic / Reactive         │ Manual / Programmatic              │
 163 │ DML Operations   │ ❌ Read-Only                 │ ✅ Insert / Update / Delete        │
 164 │ Data Updates     │ ✅ Auto on Parameter Change  │ ❌ Manual Refresh Required         │
 165 │ Control          │ ⚠️ Low (framework decides)   │ ✅ Full (you decide when/how)      │
 166 │ Error Handling   │ ✅ Framework Managed         │ ⚠️ Developer Managed               │
 167 │ Supported Objects│ ⚠️ UI API Only               │ ✅ All Objects                     │
 168 │ Caching          │ ✅ Built-in (cacheable=true) │ ❌ No automatic caching            │
 169 └──────────────────┴──────────────────────────────┴────────────────────────────────────┘
 170 ```
 171 
 172 #### Pros & Cons
 173 
 174 | Wire (@wire) | Imperative Calls |
 175 |--------------|------------------|
 176 | ✅ Auto UI sync & caching | ✅ Supports DML & all objects |
 177 | ✅ Less boilerplate code | ✅ Full control over timing |
 178 | ✅ Reactive to parameter changes | ✅ Can handle complex logic |
 179 | ❌ Read-only, limited objects | ❌ Manual handling, no auto refresh |
 180 | ❌ Can't control execution timing | ❌ More error handling code needed |
 181 
 182 #### When to Use Each
 183 
 184 **Use Wire (@wire) when:**
 185 - 📌 Read-only data display
 186 - 📌 Auto-refresh UI when parameters change
 187 - 📌 Stable parameters (recordId, filter values)
 188 - 📌 Working with UI API supported objects
 189 
 190 **Use Imperative Calls when:**
 191 - 📌 User actions (clicks, form submissions)
 192 - 📌 DML operations (Insert, Update, Delete)
 193 - 📌 Dynamic parameters determined at runtime
 194 - 📌 Custom objects or complex queries
 195 - 📌 Need control over execution timing
 196 
 197 #### Side-by-Side Code Examples
 198 
 199 **Wire Example** - Data loads automatically when `selectedIndustry` changes:
 200 
 201 ```javascript
 202 import { LightningElement, wire } from 'lwc';
 203 import fetchAccounts from '@salesforce/apex/AccountController.fetchAccounts';
 204 
 205 export default class WireExample extends LightningElement {
 206     selectedIndustry = 'Technology';
 207     accounts;
 208     error;
 209 
 210     // Automatically re-fetches when selectedIndustry changes
 211     @wire(fetchAccounts, { industry: '$selectedIndustry' })
 212     wiredAccounts({ data, error }) {
 213         if (data) {
 214             this.accounts = data;
 215             this.error = undefined;
 216         } else if (error) {
 217             this.error = error;
 218             this.accounts = undefined;
 219         }
 220     }
 221 }
 222 ```
 223 
 224 **Imperative Example** - Data loads only when user triggers action:
 225 
 226 ```javascript
 227 import { LightningElement } from 'lwc';
 228 import fetchAccounts from '@salesforce/apex/AccountController.fetchAccounts';
 229 
 230 export default class ImperativeExample extends LightningElement {
 231     selectedIndustry = 'Technology';
 232     accounts;
 233     error;
 234     isLoading = false;
 235 
 236     // Called explicitly when user clicks button or submits form
 237     async fetchAccounts() {
 238         this.isLoading = true;
 239         try {
 240             this.accounts = await fetchAccounts({
 241                 industry: this.selectedIndustry
 242             });
 243             this.error = undefined;
 244         } catch (error) {
 245             this.error = error;
 246             this.accounts = undefined;
 247         } finally {
 248             this.isLoading = false;
 249         }
 250     }
 251 }
 252 ```
 253 
 254 #### Decision Tree
 255 
 256 ```
 257                     ┌─────────────────────────────┐
 258                     │   Need to modify data?      │
 259                     │   (Insert/Update/Delete)    │
 260                     └─────────────┬───────────────┘
 261                                   │
 262                     ┌─────────────┴───────────────┐
 263                     │                             │
 264                    YES                            NO
 265                     │                             │
 266                     ▼                             ▼
 267          ┌─────────────────┐        ┌─────────────────────────┐
 268          │   IMPERATIVE    │        │  Should data auto-      │
 269          │   (Use await)   │        │  refresh on param       │
 270          └─────────────────┘        │  change?                │
 271                                     └───────────┬─────────────┘
 272                                                 │
 273                                     ┌───────────┴───────────┐
 274                                     │                       │
 275                                    YES                      NO
 276                                     │                       │
 277                                     ▼                       ▼
 278                          ┌─────────────────┐     ┌─────────────────┐
 279                          │   @WIRE         │     │   IMPERATIVE    │
 280                          │   (Reactive)    │     │   (On-demand)   │
 281                          └─────────────────┘     └─────────────────┘
 282 ```
 283 
 284 ---
 285 
 286 ### 1. Basic Data Display (Wire Service)
 287 
 288 ```javascript
 289 // accountCard.js
 290 import { LightningElement, api, wire } from 'lwc';
 291 import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
 292 import NAME_FIELD from '@salesforce/schema/Account.Name';
 293 import INDUSTRY_FIELD from '@salesforce/schema/Account.Industry';
 294 
 295 const FIELDS = [NAME_FIELD, INDUSTRY_FIELD];
 296 
 297 export default class AccountCard extends LightningElement {
 298     @api recordId;
 299 
 300     @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
 301     account;
 302 
 303     get name() {
 304         return getFieldValue(this.account.data, NAME_FIELD);
 305     }
 306 
 307     get industry() {
 308         return getFieldValue(this.account.data, INDUSTRY_FIELD);
 309     }
 310 
 311     get isLoading() {
 312         return !this.account.data && !this.account.error;
 313     }
 314 }
 315 ```
 316 
 317 ```html
 318 <!-- accountCard.html -->
 319 <template>
 320     <template lwc:if={isLoading}>
 321         <lightning-spinner alternative-text="Loading"></lightning-spinner>
 322     </template>
 323     <template lwc:if={account.data}>
 324         <div class="slds-box slds-theme_default">
 325             <h2 class="slds-text-heading_medium">{name}</h2>
 326             <p class="slds-text-color_weak">{industry}</p>
 327         </div>
 328     </template>
 329     <template lwc:if={account.error}>
 330         <p class="slds-text-color_error">{account.error.body.message}</p>
 331     </template>
 332 </template>
 333 ```
 334 
 335 ### 2. Wire Service with Apex
 336 
 337 ```javascript
 338 // contactList.js
 339 import { LightningElement, api, wire } from 'lwc';
 340 import getContacts from '@salesforce/apex/ContactController.getContacts';
 341 import { refreshApex } from '@salesforce/apex';
 342 
 343 export default class ContactList extends LightningElement {
 344     @api recordId;
 345     contacts;
 346     error;
 347     wiredContactsResult;
 348 
 349     @wire(getContacts, { accountId: '$recordId' })
 350     wiredContacts(result) {
 351         this.wiredContactsResult = result; // Store for refreshApex
 352         const { error, data } = result;
 353         if (data) {
 354             this.contacts = data;
 355             this.error = undefined;
 356         } else if (error) {
 357             this.error = error;
 358             this.contacts = undefined;
 359         }
 360     }
 361 
 362     async handleRefresh() {
 363         await refreshApex(this.wiredContactsResult);
 364     }
 365 }
 366 ```
 367 
 368 ---
 369 
 370 ## GraphQL Patterns
 371 
 372 > **Module Note**: `lightning/graphql` supersedes `lightning/uiGraphQLApi` and provides newer features like mutations, optional fields, and dynamic query construction.
 373 
 374 ### GraphQL Query (Wire Adapter)
 375 
 376 ```javascript
 377 // graphqlContacts.js
 378 import { LightningElement, wire } from 'lwc';
 379 import { gql, graphql } from 'lightning/graphql';
 380 
 381 const CONTACTS_QUERY = gql`
 382     query ContactsQuery($first: Int, $after: String) {
 383         uiapi {
 384             query {
 385                 Contact(first: $first, after: $after) {
 386                     edges {
 387                         node {
 388                             Id
 389                             Name { value }
 390                             Email { value }
 391                             Account {
 392                                 Name { value }
 393                             }
 394                         }
 395                         cursor
 396                     }
 397                     pageInfo {
 398                         hasNextPage
 399                         endCursor
 400                     }
 401                 }
 402             }
 403         }
 404     }
 405 `;
 406 
 407 export default class GraphqlContacts extends LightningElement {
 408     contacts;
 409     pageInfo;
 410     error;
 411     _cursor;
 412 
 413     @wire(graphql, {
 414         query: CONTACTS_QUERY,
 415         variables: '$queryVariables'
 416     })
 417     wiredContacts({ data, error }) {
 418         if (data) {
 419             const result = data.uiapi.query.Contact;
 420             this.contacts = result.edges.map(edge => ({
 421                 id: edge.node.Id,
 422                 name: edge.node.Name.value,
 423                 email: edge.node.Email?.value,
 424                 accountName: edge.node.Account?.Name?.value
 425             }));
 426             this.pageInfo = result.pageInfo;
 427         } else if (error) {
 428             this.error = error;
 429         }
 430     }
 431 
 432     get queryVariables() {
 433         return { first: 10, after: this._cursor };
 434     }
 435 
 436     loadMore() {
 437         if (this.pageInfo?.hasNextPage) {
 438             this._cursor = this.pageInfo.endCursor;
 439         }
 440     }
 441 }
 442 ```
 443 
 444 ### GraphQL Mutations (Spring '26 - GA in API 66.0)
 445 
 446 Mutations allow create, update, and delete operations via GraphQL. Use `executeMutation` for imperative operations.
 447 
 448 ```javascript
 449 // graphqlAccountMutation.js
 450 import { LightningElement, track } from 'lwc';
 451 import { gql, executeMutation } from 'lightning/graphql';
 452 import { ShowToastEvent } from 'lightning/platformShowToastEvent';
 453 
 454 // Create mutation
 455 const CREATE_ACCOUNT = gql`
 456     mutation CreateAccount($name: String!, $industry: String) {
 457         uiapi {
 458             AccountCreate(input: {
 459                 Account: {
 460                     Name: $name
 461                     Industry: $industry
 462                 }
 463             }) {
 464                 Record {
 465                     Id
 466                     Name { value }
 467                     Industry { value }
 468                 }
 469             }
 470         }
 471     }
 472 `;
 473 
 474 // Update mutation
 475 const UPDATE_ACCOUNT = gql`
 476     mutation UpdateAccount($id: ID!, $name: String!) {
 477         uiapi {
 478             AccountUpdate(input: {
 479                 Account: {
 480                     Id: $id
 481                     Name: $name
 482                 }
 483             }) {
 484                 Record {
 485                     Id
 486                     Name { value }
 487                 }
 488             }
 489         }
 490     }
 491 `;
 492 
 493 // Delete mutation
 494 const DELETE_ACCOUNT = gql`
 495     mutation DeleteAccount($id: ID!) {
 496         uiapi {
 497             AccountDelete(input: { Account: { Id: $id } }) {
 498                 Id
 499             }
 500         }
 501     }
 502 `;
 503 
 504 export default class GraphqlAccountMutation extends LightningElement {
 505     @track accountName = '';
 506     @track industry = '';
 507     isLoading = false;
 508 
 509     handleNameChange(event) {
 510         this.accountName = event.target.value;
 511     }
 512 
 513     handleIndustryChange(event) {
 514         this.industry = event.target.value;
 515     }
 516 
 517     async handleCreate() {
 518         if (!this.accountName) return;
 519 
 520         this.isLoading = true;
 521         try {
 522             const result = await executeMutation(CREATE_ACCOUNT, {
 523                 variables: {
 524                     name: this.accountName,
 525                     industry: this.industry || null
 526                 }
 527             });
 528 
 529             const newRecord = result.data.uiapi.AccountCreate.Record;
 530             this.showToast('Success', `Account "${newRecord.Name.value}" created`, 'success');
 531             this.resetForm();
 532         } catch (error) {
 533             this.handleError(error);
 534         } finally {
 535             this.isLoading = false;
 536         }
 537     }
 538 
 539     async handleUpdate(accountId, newName) {
 540         try {
 541             const result = await executeMutation(UPDATE_ACCOUNT, {
 542                 variables: { id: accountId, name: newName }
 543             });
 544             this.showToast('Success', 'Account updated', 'success');
 545             return result.data.uiapi.AccountUpdate.Record;
 546         } catch (error) {
 547             this.handleError(error);
 548         }
 549     }
 550 
 551     async handleDelete(accountId) {
 552         try {
 553             await executeMutation(DELETE_ACCOUNT, {
 554                 variables: { id: accountId }
 555             });
 556             this.showToast('Success', 'Account deleted', 'success');
 557         } catch (error) {
 558             this.handleError(error);
 559         }
 560     }
 561 
 562     handleError(error) {
 563         const message = error.graphQLErrors
 564             ? error.graphQLErrors.map(e => e.message).join(', ')
 565             : error.message || 'Unknown error';
 566         this.showToast('Error', message, 'error');
 567     }
 568 
 569     showToast(title, message, variant) {
 570         this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
 571     }
 572 
 573     resetForm() {
 574         this.accountName = '';
 575         this.industry = '';
 576     }
 577 }
 578 ```
 579 
 580 ### GraphQL Mutation Operations
 581 
 582 | Operation | Mutation Type | Notes |
 583 |-----------|---------------|-------|
 584 | **Create** | `{Object}Create` | Can request fields from newly created record |
 585 | **Update** | `{Object}Update` | Cannot query fields in same request |
 586 | **Delete** | `{Object}Delete` | Cannot query fields in same request |
 587 
 588 ### allOrNone Parameter
 589 
 590 Control transaction behavior with `allOrNone` (default: `true`):
 591 
 592 ```javascript
 593 const BATCH_CREATE = gql`
 594     mutation BatchCreate($allOrNone: Boolean = true) {
 595         uiapi(allOrNone: $allOrNone) {
 596             acc1: AccountCreate(input: { Account: { Name: "Account 1" } }) {
 597                 Record { Id }
 598             }
 599             acc2: AccountCreate(input: { Account: { Name: "Account 2" } }) {
 600                 Record { Id }
 601             }
 602         }
 603     }
 604 `;
 605 
 606 // If allOrNone=true: All rollback if any fails
 607 // If allOrNone=false: Only failed operations rollback
 608 ```
 609 
 610 ---
 611 
 612 ## Modal Component Pattern
 613 
 614 Based on [James Simone's composable modal pattern](https://www.jamessimone.net/blog/joys-of-apex/lwc-composable-modal/).
 615 
 616 ```javascript
 617 // composableModal.js
 618 import { LightningElement, api } from 'lwc';
 619 
 620 const OUTER_MODAL_CLASS = 'outerModalContent';
 621 
 622 export default class ComposableModal extends LightningElement {
 623     @api modalHeader;
 624     @api modalTagline;
 625     @api modalSaveHandler;
 626 
 627     _isOpen = false;
 628     _focusableElements = [];
 629 
 630     @api
 631     toggleModal() {
 632         this._isOpen = !this._isOpen;
 633         if (this._isOpen) {
 634             this._focusableElements = [...this.querySelectorAll('.focusable')];
 635             this._focusFirstElement();
 636             window.addEventListener('keyup', this._handleKeyUp);
 637         } else {
 638             window.removeEventListener('keyup', this._handleKeyUp);
 639         }
 640     }
 641 
 642     get modalAriaHidden() {
 643         return !this._isOpen;
 644     }
 645 
 646     get modalClass() {
 647         return this._isOpen
 648             ? 'slds-modal slds-visible slds-fade-in-open'
 649             : 'slds-modal slds-hidden';
 650     }
 651 
 652     get backdropClass() {
 653         return this._isOpen ? 'slds-backdrop slds-backdrop_open' : 'slds-backdrop';
 654     }
 655 
 656     _handleKeyUp = (event) => {
 657         if (event.code === 'Escape') {
 658             this.toggleModal();
 659         } else if (event.code === 'Tab') {
 660             this._handleTabNavigation(event);
 661         }
 662     }
 663 
 664     _handleTabNavigation(event) {
 665         // Focus trap logic - keep focus within modal
 666         const activeEl = this.template.activeElement;
 667         const lastIndex = this._focusableElements.length - 1;
 668         const currentIndex = this._focusableElements.indexOf(activeEl);
 669 
 670         if (event.shiftKey && currentIndex === 0) {
 671             this._focusableElements[lastIndex]?.focus();
 672         } else if (!event.shiftKey && currentIndex === lastIndex) {
 673             this._focusFirstElement();
 674         }
 675     }
 676 
 677     _focusFirstElement() {
 678         if (this._focusableElements.length > 0) {
 679             this._focusableElements[0].focus();
 680         }
 681     }
 682 
 683     handleBackdropClick(event) {
 684         if (event.target.classList.contains(OUTER_MODAL_CLASS)) {
 685             this.toggleModal();
 686         }
 687     }
 688 
 689     handleSave() {
 690         if (this.modalSaveHandler) {
 691             this.modalSaveHandler();
 692         }
 693         this.toggleModal();
 694     }
 695 
 696     disconnectedCallback() {
 697         window.removeEventListener('keyup', this._handleKeyUp);
 698     }
 699 }
 700 ```
 701 
 702 ```html
 703 <!-- composableModal.html -->
 704 <template>
 705     <!-- Backdrop -->
 706     <div class={backdropClass}></div>
 707 
 708     <!-- Modal -->
 709     <div class={modalClass}
 710          role="dialog"
 711          aria-modal="true"
 712          aria-hidden={modalAriaHidden}
 713          aria-labelledby="modal-heading">
 714 
 715         <div class="slds-modal__container outerModalContent"
 716              onclick={handleBackdropClick}>
 717 
 718             <div class="slds-modal__content slds-p-around_medium">
 719                 <!-- Header -->
 720                 <template lwc:if={modalHeader}>
 721                     <h2 id="modal-heading" class="slds-text-heading_medium">
 722                         {modalHeader}
 723                     </h2>
 724                 </template>
 725                 <template lwc:if={modalTagline}>
 726                     <p class="slds-m-top_x-small slds-text-color_weak">
 727                         {modalTagline}
 728                     </p>
 729                 </template>
 730 
 731                 <!-- Slotted Content -->
 732                 <div class="slds-m-top_medium">
 733                     <slot name="modalContent"></slot>
 734                 </div>
 735 
 736                 <!-- Footer -->
 737                 <div class="slds-m-top_medium slds-text-align_right">
 738                     <lightning-button
 739                         label="Cancel"
 740                         onclick={toggleModal}
 741                         class="slds-m-right_x-small focusable">
 742                     </lightning-button>
 743                     <lightning-button
 744                         variant="brand"
 745                         label="Save"
 746                         onclick={handleSave}
 747                         class="focusable">
 748                     </lightning-button>
 749                 </div>
 750             </div>
 751         </div>
 752     </div>
 753 
 754     <!-- Hidden background content -->
 755     <div aria-hidden={_isOpen}>
 756         <slot name="body"></slot>
 757     </div>
 758 </template>
 759 ```
 760 
 761 ---
 762 
 763 ## Record Picker Pattern
 764 
 765 ```javascript
 766 // recordPicker.js
 767 import { LightningElement, api } from 'lwc';
 768 
 769 export default class RecordPicker extends LightningElement {
 770     @api label = 'Select Record';
 771     @api objectApiName = 'Account';
 772     @api placeholder = 'Search...';
 773     @api required = false;
 774     @api multiSelect = false;
 775 
 776     _selectedIds = [];
 777 
 778     @api
 779     get value() {
 780         return this.multiSelect ? this._selectedIds : this._selectedIds[0];
 781     }
 782 
 783     set value(val) {
 784         this._selectedIds = Array.isArray(val) ? val : val ? [val] : [];
 785     }
 786 
 787     handleChange(event) {
 788         const recordId = event.detail.recordId;
 789         if (this.multiSelect) {
 790             if (!this._selectedIds.includes(recordId)) {
 791                 this._selectedIds = [...this._selectedIds, recordId];
 792             }
 793         } else {
 794             this._selectedIds = recordId ? [recordId] : [];
 795         }
 796 
 797         this.dispatchEvent(new CustomEvent('select', {
 798             detail: {
 799                 recordId: this.value,
 800                 recordIds: this._selectedIds
 801             }
 802         }));
 803     }
 804 
 805     handleRemove(event) {
 806         const idToRemove = event.target.dataset.id;
 807         this._selectedIds = this._selectedIds.filter(id => id !== idToRemove);
 808         this.dispatchEvent(new CustomEvent('select', {
 809             detail: { recordIds: this._selectedIds }
 810         }));
 811     }
 812 }
 813 ```
 814 
 815 ```html
 816 <!-- recordPicker.html -->
 817 <template>
 818     <lightning-record-picker
 819         label={label}
 820         placeholder={placeholder}
 821         object-api-name={objectApiName}
 822         onchange={handleChange}
 823         required={required}>
 824     </lightning-record-picker>
 825 
 826     <template lwc:if={multiSelect}>
 827         <div class="slds-m-top_x-small">
 828             <template for:each={_selectedIds} for:item="id">
 829                 <lightning-pill
 830                     key={id}
 831                     label={id}
 832                     data-id={id}
 833                     onremove={handleRemove}>
 834                 </lightning-pill>
 835             </template>
 836         </div>
 837     </template>
 838 </template>
 839 ```
 840 
 841 ---
 842 
 843 ## Workspace API Pattern
 844 
 845 ```javascript
 846 // workspaceTabManager.js
 847 import { LightningElement, wire } from 'lwc';
 848 import { IsConsoleNavigation, getFocusedTabInfo, openTab, closeTab,
 849          setTabLabel, setTabIcon, refreshTab } from 'lightning/platformWorkspaceApi';
 850 
 851 export default class WorkspaceTabManager extends LightningElement {
 852     @wire(IsConsoleNavigation) isConsole;
 853 
 854     async openRecordTab(recordId, objectApiName) {
 855         if (!this.isConsole) return;
 856 
 857         await openTab({
 858             recordId,
 859             focus: true,
 860             icon: `standard:${objectApiName.toLowerCase()}`,
 861             label: 'Loading...'
 862         });
 863     }
 864 
 865     async openSubtab(parentTabId, recordId) {
 866         if (!this.isConsole) return;
 867 
 868         await openTab({
 869             parentTabId,
 870             recordId,
 871             focus: true
 872         });
 873     }
 874 
 875     async getCurrentTabInfo() {
 876         if (!this.isConsole) return null;
 877         return await getFocusedTabInfo();
 878     }
 879 
 880     async updateTabLabel(tabId, label) {
 881         if (!this.isConsole) return;
 882         await setTabLabel(tabId, label);
 883     }
 884 
 885     async updateTabIcon(tabId, iconName) {
 886         if (!this.isConsole) return;
 887         await setTabIcon(tabId, iconName);
 888     }
 889 
 890     async refreshCurrentTab() {
 891         if (!this.isConsole) return;
 892         const tabInfo = await getFocusedTabInfo();
 893         await refreshTab(tabInfo.tabId);
 894     }
 895 
 896     async closeCurrentTab() {
 897         if (!this.isConsole) return;
 898         const tabInfo = await getFocusedTabInfo();
 899         await closeTab(tabInfo.tabId);
 900     }
 901 }
 902 ```
 903 
 904 ---
 905 
 906 ## Parent-Child Communication
 907 
 908 ```javascript
 909 // parent.js
 910 import { LightningElement } from 'lwc';
 911 
 912 export default class Parent extends LightningElement {
 913     selectedAccountId;
 914 
 915     handleAccountSelected(event) {
 916         this.selectedAccountId = event.detail.accountId;
 917     }
 918 }
 919 ```
 920 
 921 ```html
 922 <!-- parent.html -->
 923 <template>
 924     <c-account-list onaccountselected={handleAccountSelected}></c-account-list>
 925     <template lwc:if={selectedAccountId}>
 926         <c-account-detail account-id={selectedAccountId}></c-account-detail>
 927     </template>
 928 </template>
 929 ```
 930 
 931 ```javascript
 932 // child.js (accountList)
 933 import { LightningElement } from 'lwc';
 934 
 935 export default class AccountList extends LightningElement {
 936     handleRowAction(event) {
 937         const accountId = event.detail.row.Id;
 938 
 939         // Dispatch event to parent
 940         this.dispatchEvent(new CustomEvent('accountselected', {
 941             detail: { accountId },
 942             bubbles: true,
 943             composed: false // Don't cross shadow DOM boundaries
 944         }));
 945     }
 946 }
 947 ```
 948 
 949 ---
 950 
 951 ## Sibling Communication (via Parent)
 952 
 953 When two child components need to communicate but share the same parent, use the **parent as middleware**. This is the recommended pattern for master-detail UIs.
 954 
 955 ```
 956 ┌─────────────────────────────────────────────────────────────────────┐
 957 │                    SIBLING COMMUNICATION FLOW                       │
 958 ├─────────────────────────────────────────────────────────────────────┤
 959 │                                                                     │
 960 │                         ┌──────────┐                                │
 961 │                         │  Parent  │  ← Manages state               │
 962 │                         └────┬─────┘                                │
 963 │                    ┌─────────┴─────────┐                            │
 964 │                    │                   │                            │
 965 │              CustomEvent          @api property                     │
 966 │                (up)                 (down)                          │
 967 │                    │                   │                            │
 968 │              ┌─────┴─────┐       ┌─────┴─────┐                      │
 969 │              │  Child A  │       │  Child B  │                      │
 970 │              │  (List)   │       │  (Detail) │                      │
 971 │              └───────────┘       └───────────┘                      │
 972 │                                                                     │
 973 └─────────────────────────────────────────────────────────────────────┘
 974 ```
 975 
 976 **The flow**:
 977 1. **Child A** dispatches a custom event (e.g., user selects an account)
 978 2. **Parent** catches the event and updates its state
 979 3. **Parent** passes data to **Child B** via `@api` property
 980 
 981 ### Complete Example: Account List → Account Detail
 982 
 983 ```javascript
 984 // accountContainer.js - Parent orchestrates communication between siblings
 985 import { LightningElement } from 'lwc';
 986 
 987 export default class AccountContainer extends LightningElement {
 988     // State managed at parent level
 989     selectedAccountId;
 990     selectedAccountName;
 991 
 992     // Child A (accountList) fires this event
 993     handleAccountSelect(event) {
 994         this.selectedAccountId = event.detail.accountId;
 995         this.selectedAccountName = event.detail.accountName;
 996     }
 997 
 998     // Clear selection (triggered by Child B)
 999     handleClearSelection() {
1000         this.selectedAccountId = null;
1001         this.selectedAccountName = null;
1002     }
1003 
1004     get hasSelection() {
1005         return !!this.selectedAccountId;
1006     }
1007 }
1008 ```
1009 
1010 ```html
1011 <!-- accountContainer.html -->
1012 <template>
1013     <div class="slds-grid slds-gutters">
1014         <!-- Child A: Account List -->
1015         <div class="slds-col slds-size_1-of-2">
1016             <c-account-list
1017                 onaccountselect={handleAccountSelect}
1018                 selected-id={selectedAccountId}>
1019             </c-account-list>
1020         </div>
1021 
1022         <!-- Child B: Account Detail (receives data via @api) -->
1023         <div class="slds-col slds-size_1-of-2">
1024             <template lwc:if={hasSelection}>
1025                 <c-account-detail
1026                     account-id={selectedAccountId}
1027                     account-name={selectedAccountName}
1028                     onclearselection={handleClearSelection}>
1029                 </c-account-detail>
1030             </template>
1031             <template lwc:else>
1032                 <div class="slds-box slds-theme_shade">
1033                     Select an account to view details
1034                 </div>
1035             </template>
1036         </div>
1037     </div>
1038 </template>
1039 ```
1040 
1041 ```javascript
1042 // accountList.js - Child A: Dispatches events UP to parent
1043 import { LightningElement, api, wire } from 'lwc';
1044 import getAccounts from '@salesforce/apex/AccountController.getAccounts';
1045 
1046 export default class AccountList extends LightningElement {
1047     @api selectedId; // Highlight selected row (from parent)
1048     accounts;
1049     error;
1050 
1051     @wire(getAccounts)
1052     wiredAccounts({ data, error }) {
1053         if (data) {
1054             this.accounts = data;
1055             this.error = undefined;
1056         } else if (error) {
1057             this.error = error;
1058             this.accounts = undefined;
1059         }
1060     }
1061 
1062     handleRowClick(event) {
1063         const accountId = event.currentTarget.dataset.id;
1064         const accountName = event.currentTarget.dataset.name;
1065 
1066         // Dispatch event to parent (not bubbles - parent listens directly)
1067         this.dispatchEvent(new CustomEvent('accountselect', {
1068             detail: { accountId, accountName }
1069         }));
1070     }
1071 
1072     // Computed: Check if row should be highlighted
1073     getRowClass(accountId) {
1074         return accountId === this.selectedId
1075             ? 'slds-item slds-is-selected'
1076             : 'slds-item';
1077     }
1078 }
1079 ```
1080 
1081 ```javascript
1082 // accountDetail.js - Child B: Receives data via @api from parent
1083 import { LightningElement, api, wire } from 'lwc';
1084 import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
1085 import INDUSTRY_FIELD from '@salesforce/schema/Account.Industry';
1086 import REVENUE_FIELD from '@salesforce/schema/Account.AnnualRevenue';
1087 
1088 const FIELDS = [INDUSTRY_FIELD, REVENUE_FIELD];
1089 
1090 export default class AccountDetail extends LightningElement {
1091     @api accountId;      // Received from parent
1092     @api accountName;    // Received from parent
1093 
1094     @wire(getRecord, { recordId: '$accountId', fields: FIELDS })
1095     account;
1096 
1097     get industry() {
1098         return getFieldValue(this.account.data, INDUSTRY_FIELD);
1099     }
1100 
1101     get revenue() {
1102         return getFieldValue(this.account.data, REVENUE_FIELD);
1103     }
1104 
1105     get isLoading() {
1106         return !this.account.data && !this.account.error;
1107     }
1108 
1109     handleClose() {
1110         // Dispatch event back to parent to clear selection
1111         this.dispatchEvent(new CustomEvent('clearselection'));
1112     }
1113 }
1114 ```
1115 
1116 ### When to Use Sibling Pattern vs LMS
1117 
1118 | Scenario | Sibling Pattern | LMS |
1119 |----------|-----------------|-----|
1120 | Components share same parent | ✅ Recommended | ❌ Overkill |
1121 | State is simple (1-2 values) | ✅ | ❌ |
1122 | Need bidirectional updates | ✅ | ✅ |
1123 | Components in different DOM trees | ❌ | ✅ Required |
1124 | Cross-framework (LWC ↔ Aura) | ❌ | ✅ Required |
1125 | Many consumers need same data | ❌ Consider LMS | ✅ |
1126 | Component hierarchy is deep (4+ levels) | ❌ Consider LMS | ✅ |
1127 
1128 **Rule of thumb**: If components share a parent and data flow is simple, use sibling pattern. If components are "far apart" in the DOM or you need pub/sub semantics, use LMS.
1129 
1130 ---
1131 
1132 ## Navigation Patterns
1133 
1134 ```javascript
1135 // navigator.js
1136 import { LightningElement } from 'lwc';
1137 import { NavigationMixin } from 'lightning/navigation';
1138 
1139 export default class Navigator extends NavigationMixin(LightningElement) {
1140 
1141     navigateToRecord(recordId, objectApiName = 'Account') {
1142         this[NavigationMixin.Navigate]({
1143             type: 'standard__recordPage',
1144             attributes: {
1145                 recordId,
1146                 objectApiName,
1147                 actionName: 'view'
1148             }
1149         });
1150     }
1151 
1152     navigateToList(objectApiName, filterName = 'Recent') {
1153         this[NavigationMixin.Navigate]({
1154             type: 'standard__objectPage',
1155             attributes: {
1156                 objectApiName,
1157                 actionName: 'list'
1158             },
1159             state: { filterName }
1160         });
1161     }
1162 
1163     navigateToNewRecord(objectApiName, defaultValues = {}) {
1164         this[NavigationMixin.Navigate]({
1165             type: 'standard__objectPage',
1166             attributes: {
1167                 objectApiName,
1168                 actionName: 'new'
1169             },
1170             state: {
1171                 defaultFieldValues: Object.entries(defaultValues)
1172                     .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
1173                     .join(',')
1174             }
1175         });
1176     }
1177 
1178     navigateToRelatedList(recordId, relationshipApiName) {
1179         this[NavigationMixin.Navigate]({
1180             type: 'standard__recordRelationshipPage',
1181             attributes: {
1182                 recordId,
1183                 relationshipApiName,
1184                 actionName: 'view'
1185             }
1186         });
1187     }
1188 
1189     navigateToNamedPage(pageName, params = {}) {
1190         this[NavigationMixin.Navigate]({
1191             type: 'standard__namedPage',
1192             attributes: {
1193                 pageName
1194             },
1195             state: params
1196         });
1197     }
1198 }
1199 ```
1200 
1201 ---
1202 
1203 ## TypeScript Patterns
1204 
1205 ### TypeScript Component Pattern
1206 
1207 ```typescript
1208 // accountList.ts
1209 import { LightningElement, api, wire, track } from 'lwc';
1210 import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
1211 import getAccounts from '@salesforce/apex/AccountController.getAccounts';
1212 import ACCOUNT_NAME_FIELD from '@salesforce/schema/Account.Name';
1213 
1214 // Define interfaces for type safety
1215 interface AccountRecord {
1216     Id: string;
1217     Name: string;
1218     Industry?: string;
1219     AnnualRevenue?: number;
1220 }
1221 
1222 interface WireResult<T> {
1223     data?: T;
1224     error?: Error;
1225 }
1226 
1227 export default class AccountList extends LightningElement {
1228     // Typed @api properties
1229     @api recordId: string | undefined;
1230 
1231     @api
1232     get maxRecords(): number {
1233         return this._maxRecords;
1234     }
1235     set maxRecords(value: number) {
1236         this._maxRecords = value;
1237     }
1238 
1239     // Typed @track properties
1240     @track private _accounts: AccountRecord[] = [];
1241     @track private _error: string | null = null;
1242 
1243     private _maxRecords: number = 10;
1244     private _wiredResult: WireResult<AccountRecord[]> | undefined;
1245 
1246     // Typed wire service
1247     @wire(getAccounts, { maxRecords: '$maxRecords' })
1248     wiredAccounts(result: WireResult<AccountRecord[]>): void {
1249         this._wiredResult = result;
1250         const { data, error } = result;
1251 
1252         if (data) {
1253             this._accounts = data;
1254             this._error = null;
1255         } else if (error) {
1256             this._error = this.reduceErrors(error);
1257             this._accounts = [];
1258         }
1259     }
1260 
1261     // Typed getters
1262     get accounts(): AccountRecord[] {
1263         return this._accounts;
1264     }
1265 
1266     get hasAccounts(): boolean {
1267         return this._accounts.length > 0;
1268     }
1269 
1270     // Typed event handlers
1271     handleSelect(event: CustomEvent<{ accountId: string }>): void {
1272         const { accountId } = event.detail;
1273         this.dispatchEvent(new CustomEvent('accountselected', {
1274             detail: { accountId },
1275             bubbles: true,
1276             composed: true
1277         }));
1278     }
1279 
1280     // Typed utility methods
1281     private reduceErrors(error: Error | Error[]): string {
1282         const errors = Array.isArray(error) ? error : [error];
1283         return errors
1284             .filter((e): e is Error => e !== null)
1285             .map(e => e.message || 'Unknown error')
1286             .join('; ');
1287     }
1288 }
1289 ```
1290 
1291 ### TypeScript Jest Test Pattern
1292 
1293 ```typescript
1294 // accountList.test.ts
1295 import { createElement, LightningElement } from 'lwc';
1296 import AccountList from 'c/accountList';
1297 import getAccounts from '@salesforce/apex/AccountController.getAccounts';
1298 
1299 // Type definitions for tests
1300 interface AccountRecord {
1301     Id: string;
1302     Name: string;
1303     Industry?: string;
1304 }
1305 
1306 // Mock Apex
1307 jest.mock(
1308     '@salesforce/apex/AccountController.getAccounts',
1309     () => ({ default: jest.fn() }),
1310     { virtual: true }
1311 );
1312 
1313 const MOCK_ACCOUNTS: AccountRecord[] = [
1314     { Id: '001xx000003DGQ', Name: 'Acme Corp', Industry: 'Technology' }
1315 ];
1316 
1317 describe('c-account-list', () => {
1318     let element: LightningElement & { maxRecords?: number };
1319 
1320     afterEach(() => {
1321         while (document.body.firstChild) {
1322             document.body.removeChild(document.body.firstChild);
1323         }
1324         jest.clearAllMocks();
1325     });
1326 
1327     it('displays accounts after data loads', async () => {
1328         (getAccounts as jest.Mock).mockResolvedValue(MOCK_ACCOUNTS);
1329 
1330         element = createElement('c-account-list', { is: AccountList });
1331         document.body.appendChild(element);
1332 
1333         await Promise.resolve();
1334 
1335         const items = element.shadowRoot?.querySelectorAll('.slds-item');
1336         expect(items?.length).toBe(MOCK_ACCOUNTS.length);
1337     });
1338 });
1339 ```
1340 
1341 ### TypeScript Features for LWC
1342 
1343 | Feature | LWC Support | Notes |
1344 |---------|-------------|-------|
1345 | **Interface definitions** | ✅ | Define shapes for records, events, props |
1346 | **Typed @api properties** | ✅ | Getter/setter patterns with types |
1347 | **Typed @wire results** | ✅ | Generic `WireResult<T>` pattern |
1348 | **Typed event handlers** | ✅ | `CustomEvent<T>` for event detail typing |
1349 | **Private class fields** | ✅ | Use `private` keyword |
1350 | **Strict null checking** | ✅ | Optional chaining `?.` and nullish coalescing `??` |
1351 
1352 ---
1353 
1354 ## Apex Controller Patterns
1355 
1356 ### Cacheable Methods (for @wire)
1357 
1358 ```apex
1359 public with sharing class LwcController {
1360 
1361     @AuraEnabled(cacheable=true)
1362     public static List<Account> getAccounts(String searchTerm) {
1363         String searchKey = '%' + String.escapeSingleQuotes(searchTerm) + '%';
1364         return [
1365             SELECT Id, Name, Industry, AnnualRevenue
1366             FROM Account
1367             WHERE Name LIKE :searchKey
1368             WITH SECURITY_ENFORCED
1369             ORDER BY Name
1370             LIMIT 50
1371         ];
1372     }
1373 
1374     @AuraEnabled(cacheable=true)
1375     public static List<PicklistOption> getIndustryOptions() {
1376         List<PicklistOption> options = new List<PicklistOption>();
1377         Schema.DescribeFieldResult fieldResult =
1378             Account.Industry.getDescribe();
1379         for (Schema.PicklistEntry entry : fieldResult.getPicklistValues()) {
1380             if (entry.isActive()) {
1381                 options.add(new PicklistOption(entry.getLabel(), entry.getValue()));
1382             }
1383         }
1384         return options;
1385     }
1386 
1387     public class PicklistOption {
1388         @AuraEnabled public String label;
1389         @AuraEnabled public String value;
1390 
1391         public PicklistOption(String label, String value) {
1392             this.label = label;
1393             this.value = value;
1394         }
1395     }
1396 }
1397 ```
1398 
1399 ### Non-Cacheable Methods (for DML)
1400 
1401 ```apex
1402 @AuraEnabled
1403 public static Account createAccount(String accountJson) {
1404     Account acc = (Account) JSON.deserialize(accountJson, Account.class);
1405 
1406     // FLS check
1407     SObjectAccessDecision decision = Security.stripInaccessible(
1408         AccessType.CREATABLE,
1409         new List<Account>{ acc }
1410     );
1411 
1412     insert decision.getRecords();
1413     return (Account) decision.getRecords()[0];
1414 }
1415 
1416 @AuraEnabled
1417 public static void deleteAccounts(List<Id> accountIds) {
1418     if (accountIds == null || accountIds.isEmpty()) {
1419         throw new AuraHandledException('No accounts to delete');
1420     }
1421 
1422     List<Account> toDelete = [
1423         SELECT Id FROM Account
1424         WHERE Id IN :accountIds
1425         WITH SECURITY_ENFORCED
1426     ];
1427 
1428     delete toDelete;
1429 }
1430 ```
1431 
1432 ### Error Handling Pattern
1433 
1434 ```apex
1435 @AuraEnabled
1436 public static List<Contact> getContactsWithErrorHandling(Id accountId) {
1437     try {
1438         if (accountId == null) {
1439             throw new AuraHandledException('Account ID is required');
1440         }
1441 
1442         List<Contact> contacts = [
1443             SELECT Id, Name, Email, Phone
1444             FROM Contact
1445             WHERE AccountId = :accountId
1446             WITH SECURITY_ENFORCED
1447             ORDER BY Name
1448             LIMIT 100
1449         ];
1450 
1451         return contacts;
1452     } catch (Exception e) {
1453         throw new AuraHandledException('Error fetching contacts: ' + e.getMessage());
1454     }
1455 }
1456 ```
1457 
1458 ---
1459 
1460 ## Related Resources
1461 
1462 - [lms-guide.md](lms-guide.md) - Lightning Message Service deep dive
1463 - [jest-testing.md](jest-testing.md) - Advanced testing patterns
1464 - [accessibility-guide.md](accessibility-guide.md) - WCAG compliance
1465 - [performance-guide.md](performance-guide.md) - Optimization techniques
1466 
1467 ---
1468 
1469 ## External References
1470 
1471 - [PICKLES Framework (Salesforce Ben)](https://www.salesforceben.com/the-ideal-framework-for-architecting-salesforce-lightning-web-components/)
1472 - [LWC Recipes (GitHub)](https://github.com/trailheadapps/lwc-recipes)
1473 - [James Simone - Composable Modal](https://www.jamessimone.net/blog/joys-of-apex/lwc-composable-modal/)
