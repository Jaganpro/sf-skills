<!-- Parent: sf-lwc/SKILL.md -->
   1 # Lightning Message Service (LMS) Guide
   2 
   3 Complete guide to cross-DOM component communication using Lightning Message Service.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [Overview](#overview)
  10 2. [When to Use LMS](#when-to-use-lms)
  11 3. [Message Channel Setup](#message-channel-setup)
  12 4. [Publishing Messages](#publishing-messages)
  13 5. [Subscribing to Messages](#subscribing-to-messages)
  14 6. [Scopes](#scopes)
  15 7. [Advanced Patterns](#advanced-patterns)
  16 8. [Best Practices](#best-practices)
  17 9. [Troubleshooting](#troubleshooting)
  18 
  19 ---
  20 
  21 ## Overview
  22 
  23 Lightning Message Service (LMS) enables communication between components across different DOM contexts:
  24 - Lightning Web Components (LWC)
  25 - Aura Components
  26 - Visualforce pages (in Lightning Experience)
  27 
  28 **Key Benefits**:
  29 - Cross-DOM communication (Shadow DOM boundaries)
  30 - Loosely coupled components
  31 - Publish-subscribe pattern
  32 - Type-safe messaging with message channels
  33 
  34 ---
  35 
  36 ## When to Use LMS
  37 
  38 | Use Case | Recommended Pattern |
  39 |----------|---------------------|
  40 | Parent → Child | `@api` properties (simple, direct) |
  41 | Child → Parent | Custom Events (simple, direct) |
  42 | Sibling → Sibling (same hierarchy) | Parent mediator + Custom Events |
  43 | **Cross-DOM communication** | **Lightning Message Service** |
  44 | **App Builder page components** | **Lightning Message Service** |
  45 | **Aura ↔ LWC communication** | **Lightning Message Service** |
  46 | **Visualforce ↔ LWC (in LEX)** | **Lightning Message Service** |
  47 
  48 **Rule of Thumb**: Use LMS when components cannot directly reference each other or cross DOM boundaries.
  49 
  50 ---
  51 
  52 ## Message Channel Setup
  53 
  54 ### 1. Create Message Channel Metadata
  55 
  56 Lightning Message Channels are metadata files that define the message schema.
  57 
  58 **File**: `force-app/main/default/messageChannels/AccountSelected__c.messageChannel-meta.xml`
  59 
  60 ```xml
  61 <?xml version="1.0" encoding="UTF-8"?>
  62 <LightningMessageChannel xmlns="http://soap.sforce.com/2006/04/metadata">
  63     <description>Message channel for account selection events</description>
  64     <isExposed>true</isExposed>
  65     <lightningMessageFields>
  66         <description>Account ID</description>
  67         <fieldName>accountId</fieldName>
  68     </lightningMessageFields>
  69     <lightningMessageFields>
  70         <description>Account Name</description>
  71         <fieldName>accountName</fieldName>
  72     </lightningMessageFields>
  73     <lightningMessageFields>
  74         <description>Source component identifier</description>
  75         <fieldName>source</fieldName>
  76     </lightningMessageFields>
  77     <masterLabel>Account Selected</masterLabel>
  78 </LightningMessageChannel>
  79 ```
  80 
  81 ### 2. Deploy Message Channel
  82 
  83 ```bash
  84 sf project deploy start -m LightningMessageChannel:AccountSelected__c
  85 ```
  86 
  87 ### 3. Import Message Channel in Component
  88 
  89 ```javascript
  90 import ACCOUNT_SELECTED_CHANNEL from '@salesforce/messageChannel/AccountSelected__c';
  91 ```
  92 
  93 ---
  94 
  95 ## Publishing Messages
  96 
  97 ### Basic Publisher Pattern
  98 
  99 ```javascript
 100 // accountPublisher.js
 101 import { LightningElement, wire } from 'lwc';
 102 import { publish, MessageContext } from 'lightning/messageService';
 103 import ACCOUNT_SELECTED_CHANNEL from '@salesforce/messageChannel/AccountSelected__c';
 104 
 105 export default class AccountPublisher extends LightningElement {
 106     @wire(MessageContext)
 107     messageContext;
 108 
 109     handleAccountClick(event) {
 110         const accountId = event.target.dataset.id;
 111         const accountName = event.target.dataset.name;
 112 
 113         // Create payload
 114         const payload = {
 115             accountId: accountId,
 116             accountName: accountName,
 117             source: 'accountPublisher'
 118         };
 119 
 120         // Publish message
 121         publish(this.messageContext, ACCOUNT_SELECTED_CHANNEL, payload);
 122     }
 123 }
 124 ```
 125 
 126 ```html
 127 <!-- accountPublisher.html -->
 128 <template>
 129     <div class="slds-card">
 130         <div class="slds-card__header">
 131             <h2 class="slds-text-heading_medium">Account List</h2>
 132         </div>
 133         <div class="slds-card__body">
 134             <template for:each={accounts} for:item="account">
 135                 <div key={account.Id}
 136                      class="slds-box slds-m-around_small"
 137                      data-id={account.Id}
 138                      data-name={account.Name}
 139                      onclick={handleAccountClick}>
 140                     {account.Name}
 141                 </div>
 142             </template>
 143         </div>
 144     </div>
 145 </template>
 146 ```
 147 
 148 ### Publisher with Conditional Logic
 149 
 150 ```javascript
 151 handlePublish(accountData) {
 152     // Validate before publishing
 153     if (!this.messageContext) {
 154         console.error('MessageContext not initialized');
 155         return;
 156     }
 157 
 158     if (!accountData || !accountData.Id) {
 159         console.error('Invalid account data');
 160         return;
 161     }
 162 
 163     const payload = {
 164         accountId: accountData.Id,
 165         accountName: accountData.Name,
 166         source: this.componentName,
 167         timestamp: Date.now()
 168     };
 169 
 170     publish(this.messageContext, ACCOUNT_SELECTED_CHANNEL, payload);
 171 
 172     // Optional: Show toast confirmation
 173     this.dispatchEvent(new ShowToastEvent({
 174         title: 'Selection Published',
 175         message: `Account "${accountData.Name}" selected`,
 176         variant: 'success'
 177     }));
 178 }
 179 ```
 180 
 181 ---
 182 
 183 ## Subscribing to Messages
 184 
 185 ### Basic Subscriber Pattern
 186 
 187 ```javascript
 188 // accountSubscriber.js
 189 import { LightningElement, wire } from 'lwc';
 190 import { subscribe, unsubscribe, MessageContext, APPLICATION_SCOPE } from 'lightning/messageService';
 191 import ACCOUNT_SELECTED_CHANNEL from '@salesforce/messageChannel/AccountSelected__c';
 192 
 193 export default class AccountSubscriber extends LightningElement {
 194     subscription = null;
 195     selectedAccountId;
 196     selectedAccountName;
 197 
 198     @wire(MessageContext)
 199     messageContext;
 200 
 201     connectedCallback() {
 202         this.subscribeToChannel();
 203     }
 204 
 205     disconnectedCallback() {
 206         this.unsubscribeFromChannel();
 207     }
 208 
 209     subscribeToChannel() {
 210         if (!this.subscription) {
 211             this.subscription = subscribe(
 212                 this.messageContext,
 213                 ACCOUNT_SELECTED_CHANNEL,
 214                 (message) => this.handleMessage(message),
 215                 { scope: APPLICATION_SCOPE }
 216             );
 217         }
 218     }
 219 
 220     unsubscribeFromChannel() {
 221         unsubscribe(this.subscription);
 222         this.subscription = null;
 223     }
 224 
 225     handleMessage(message) {
 226         this.selectedAccountId = message.accountId;
 227         this.selectedAccountName = message.accountName;
 228 
 229         console.log('Message received from:', message.source);
 230         console.log('Account ID:', message.accountId);
 231     }
 232 }
 233 ```
 234 
 235 ```html
 236 <!-- accountSubscriber.html -->
 237 <template>
 238     <div class="slds-card">
 239         <div class="slds-card__header">
 240             <h2 class="slds-text-heading_medium">Selected Account</h2>
 241         </div>
 242         <div class="slds-card__body">
 243             <template lwc:if={selectedAccountId}>
 244                 <dl class="slds-dl_horizontal">
 245                     <dt class="slds-dl_horizontal__label">Account ID:</dt>
 246                     <dd class="slds-dl_horizontal__detail">{selectedAccountId}</dd>
 247                     <dt class="slds-dl_horizontal__label">Account Name:</dt>
 248                     <dd class="slds-dl_horizontal__detail">{selectedAccountName}</dd>
 249                 </dl>
 250             </template>
 251             <template lwc:else>
 252                 <p class="slds-text-color_weak">No account selected</p>
 253             </template>
 254         </div>
 255     </div>
 256 </template>
 257 ```
 258 
 259 ### Subscriber with Filtering
 260 
 261 ```javascript
 262 handleMessage(message) {
 263     // Ignore messages from this component (avoid self-updates)
 264     if (message.source === this.componentName) {
 265         return;
 266     }
 267 
 268     // Filter by specific conditions
 269     if (message.accountId && message.accountId.startsWith('001')) {
 270         this.selectedAccountId = message.accountId;
 271         this.selectedAccountName = message.accountName;
 272 
 273         // Fetch additional data if needed
 274         this.loadAccountDetails(message.accountId);
 275     }
 276 }
 277 
 278 async loadAccountDetails(accountId) {
 279     try {
 280         const data = await getAccountDetails({ accountId });
 281         this.accountDetails = data;
 282     } catch (error) {
 283         this.handleError(error);
 284     }
 285 }
 286 ```
 287 
 288 ---
 289 
 290 ## Scopes
 291 
 292 LMS supports two subscription scopes:
 293 
 294 | Scope | Behavior | Use Case |
 295 |-------|----------|----------|
 296 | `APPLICATION_SCOPE` | Receive messages from entire app | Cross-page communication, global state |
 297 | `undefined` (default) | Receive messages only within active tab | Tab-specific communication |
 298 
 299 ### Application Scope Example
 300 
 301 ```javascript
 302 import { APPLICATION_SCOPE } from 'lightning/messageService';
 303 
 304 subscribe(
 305     this.messageContext,
 306     ACCOUNT_SELECTED_CHANNEL,
 307     (message) => this.handleMessage(message),
 308     { scope: APPLICATION_SCOPE }
 309 );
 310 ```
 311 
 312 ### Tab Scope Example
 313 
 314 ```javascript
 315 // No scope specified = tab scope only
 316 subscribe(
 317     this.messageContext,
 318     ACCOUNT_SELECTED_CHANNEL,
 319     (message) => this.handleMessage(message)
 320 );
 321 ```
 322 
 323 ---
 324 
 325 ## Advanced Patterns
 326 
 327 ### 1. Multiple Subscriptions
 328 
 329 ```javascript
 330 export default class MultiSubscriber extends LightningElement {
 331     accountSubscription = null;
 332     contactSubscription = null;
 333 
 334     @wire(MessageContext) messageContext;
 335 
 336     connectedCallback() {
 337         // Subscribe to account channel
 338         this.accountSubscription = subscribe(
 339             this.messageContext,
 340             ACCOUNT_SELECTED_CHANNEL,
 341             (message) => this.handleAccountMessage(message),
 342             { scope: APPLICATION_SCOPE }
 343         );
 344 
 345         // Subscribe to contact channel
 346         this.contactSubscription = subscribe(
 347             this.messageContext,
 348             CONTACT_SELECTED_CHANNEL,
 349             (message) => this.handleContactMessage(message),
 350             { scope: APPLICATION_SCOPE }
 351         );
 352     }
 353 
 354     disconnectedCallback() {
 355         unsubscribe(this.accountSubscription);
 356         unsubscribe(this.contactSubscription);
 357         this.accountSubscription = null;
 358         this.contactSubscription = null;
 359     }
 360 
 361     handleAccountMessage(message) {
 362         // Handle account-specific logic
 363     }
 364 
 365     handleContactMessage(message) {
 366         // Handle contact-specific logic
 367     }
 368 }
 369 ```
 370 
 371 ### 2. Publish-Subscribe in Same Component
 372 
 373 ```javascript
 374 export default class PublisherSubscriber extends LightningElement {
 375     subscription = null;
 376     @wire(MessageContext) messageContext;
 377 
 378     connectedCallback() {
 379         // Subscribe to messages from OTHER components
 380         this.subscription = subscribe(
 381             this.messageContext,
 382             ACCOUNT_SELECTED_CHANNEL,
 383             (message) => this.handleMessage(message),
 384             { scope: APPLICATION_SCOPE }
 385         );
 386     }
 387 
 388     disconnectedCallback() {
 389         unsubscribe(this.subscription);
 390     }
 391 
 392     handleMessage(message) {
 393         // Filter out own messages
 394         if (message.source === 'myComponent') {
 395             return;
 396         }
 397         // Process external messages
 398         this.selectedAccountId = message.accountId;
 399     }
 400 
 401     handleLocalSelection(event) {
 402         const accountId = event.detail.id;
 403 
 404         // Publish for other components
 405         publish(this.messageContext, ACCOUNT_SELECTED_CHANNEL, {
 406             accountId,
 407             source: 'myComponent'
 408         });
 409 
 410         // Update own state directly (don't rely on subscription)
 411         this.selectedAccountId = accountId;
 412     }
 413 }
 414 ```
 415 
 416 ### 3. Conditional Subscription
 417 
 418 ```javascript
 419 export default class ConditionalSubscriber extends LightningElement {
 420     @api enableLiveUpdates = false;
 421     subscription = null;
 422     @wire(MessageContext) messageContext;
 423 
 424     connectedCallback() {
 425         if (this.enableLiveUpdates) {
 426             this.subscribeToChannel();
 427         }
 428     }
 429 
 430     @api
 431     toggleLiveUpdates(enabled) {
 432         this.enableLiveUpdates = enabled;
 433         if (enabled) {
 434             this.subscribeToChannel();
 435         } else {
 436             this.unsubscribeFromChannel();
 437         }
 438     }
 439 
 440     subscribeToChannel() {
 441         if (!this.subscription) {
 442             this.subscription = subscribe(
 443                 this.messageContext,
 444                 ACCOUNT_SELECTED_CHANNEL,
 445                 (message) => this.handleMessage(message),
 446                 { scope: APPLICATION_SCOPE }
 447             );
 448         }
 449     }
 450 
 451     unsubscribeFromChannel() {
 452         if (this.subscription) {
 453             unsubscribe(this.subscription);
 454             this.subscription = null;
 455         }
 456     }
 457 }
 458 ```
 459 
 460 ### 4. Message Buffering
 461 
 462 ```javascript
 463 export default class MessageBuffer extends LightningElement {
 464     messageQueue = [];
 465     isProcessing = false;
 466 
 467     handleMessage(message) {
 468         this.messageQueue.push(message);
 469         this.processQueue();
 470     }
 471 
 472     async processQueue() {
 473         if (this.isProcessing || this.messageQueue.length === 0) {
 474             return;
 475         }
 476 
 477         this.isProcessing = true;
 478 
 479         while (this.messageQueue.length > 0) {
 480             const message = this.messageQueue.shift();
 481             await this.processMessage(message);
 482         }
 483 
 484         this.isProcessing = false;
 485     }
 486 
 487     async processMessage(message) {
 488         // Simulate async processing
 489         return new Promise(resolve => {
 490             setTimeout(() => {
 491                 this.selectedAccountId = message.accountId;
 492                 resolve();
 493             }, 100);
 494         });
 495     }
 496 }
 497 ```
 498 
 499 ---
 500 
 501 ## Best Practices
 502 
 503 ### 1. Always Unsubscribe
 504 
 505 ```javascript
 506 disconnectedCallback() {
 507     // CRITICAL: Prevent memory leaks
 508     if (this.subscription) {
 509         unsubscribe(this.subscription);
 510         this.subscription = null;
 511     }
 512 }
 513 ```
 514 
 515 ### 2. Validate MessageContext
 516 
 517 ```javascript
 518 handlePublish(data) {
 519     if (!this.messageContext) {
 520         console.warn('MessageContext not available');
 521         return;
 522     }
 523     publish(this.messageContext, CHANNEL, data);
 524 }
 525 ```
 526 
 527 ### 3. Use Descriptive Payloads
 528 
 529 ```javascript
 530 // BAD - Unclear payload
 531 publish(this.messageContext, CHANNEL, { id: '001xxx' });
 532 
 533 // GOOD - Clear, descriptive payload
 534 publish(this.messageContext, CHANNEL, {
 535     accountId: '001xxx000003DGQ',
 536     accountName: 'Acme Corp',
 537     source: 'accountList',
 538     timestamp: Date.now(),
 539     metadata: {
 540         action: 'selected',
 541         view: 'list'
 542     }
 543 });
 544 ```
 545 
 546 ### 4. Document Message Channels
 547 
 548 ```javascript
 549 /**
 550  * Publishes account selection event to AccountSelected__c channel
 551  * @param {Object} payload
 552  * @param {String} payload.accountId - Salesforce Account ID
 553  * @param {String} payload.accountName - Account Name
 554  * @param {String} payload.source - Component identifier
 555  */
 556 publishAccountSelection(payload) {
 557     publish(this.messageContext, ACCOUNT_SELECTED_CHANNEL, payload);
 558 }
 559 ```
 560 
 561 ### 5. Error Handling
 562 
 563 ```javascript
 564 handleMessage(message) {
 565     try {
 566         if (!message || !message.accountId) {
 567             throw new Error('Invalid message payload');
 568         }
 569 
 570         this.selectedAccountId = message.accountId;
 571         this.loadAccountDetails(message.accountId);
 572     } catch (error) {
 573         console.error('Error processing message:', error);
 574         this.dispatchEvent(new ShowToastEvent({
 575             title: 'Error',
 576             message: 'Failed to process message',
 577             variant: 'error'
 578         }));
 579     }
 580 }
 581 ```
 582 
 583 ---
 584 
 585 ## Troubleshooting
 586 
 587 ### Issue: Messages Not Received
 588 
 589 **Checklist**:
 590 1. Is `MessageContext` wired correctly?
 591    ```javascript
 592    @wire(MessageContext) messageContext;
 593    ```
 594 
 595 2. Is subscription active?
 596    ```javascript
 597    console.log('Subscription:', this.subscription); // Should not be null
 598    ```
 599 
 600 3. Is the message channel deployed?
 601    ```bash
 602    sf project deploy start -m LightningMessageChannel
 603    ```
 604 
 605 4. Are publisher and subscriber using the same channel?
 606    ```javascript
 607    // Both should import the same channel
 608    import CHANNEL from '@salesforce/messageChannel/AccountSelected__c';
 609    ```
 610 
 611 5. Is the scope correct?
 612    ```javascript
 613    // For cross-page: APPLICATION_SCOPE
 614    // For same page: no scope (default)
 615    ```
 616 
 617 ### Issue: Memory Leaks
 618 
 619 **Cause**: Not unsubscribing in `disconnectedCallback()`
 620 
 621 **Fix**:
 622 ```javascript
 623 disconnectedCallback() {
 624     unsubscribe(this.subscription);
 625     this.subscription = null;
 626 }
 627 ```
 628 
 629 ### Issue: Self-Updates
 630 
 631 **Cause**: Component receives its own published messages
 632 
 633 **Fix**: Filter by source
 634 ```javascript
 635 handleMessage(message) {
 636     if (message.source === this.componentName) {
 637         return; // Ignore own messages
 638     }
 639     // Process message
 640 }
 641 ```
 642 
 643 ---
 644 
 645 ## Testing LMS Components
 646 
 647 ### Mock MessageContext
 648 
 649 ```javascript
 650 // testUtils.js
 651 export const createMessageContextMock = () => {
 652     return jest.fn();
 653 };
 654 
 655 export const mockPublish = jest.fn();
 656 export const mockSubscribe = jest.fn();
 657 export const mockUnsubscribe = jest.fn();
 658 
 659 jest.mock('lightning/messageService', () => ({
 660     publish: mockPublish,
 661     subscribe: mockSubscribe,
 662     unsubscribe: mockUnsubscribe,
 663     MessageContext: Symbol('MessageContext'),
 664     APPLICATION_SCOPE: Symbol('APPLICATION_SCOPE')
 665 }), { virtual: true });
 666 ```
 667 
 668 ### Test Publisher
 669 
 670 ```javascript
 671 import { createElement } from 'lwc';
 672 import AccountPublisher from 'c/accountPublisher';
 673 import { publish } from 'lightning/messageService';
 674 import ACCOUNT_SELECTED_CHANNEL from '@salesforce/messageChannel/AccountSelected__c';
 675 
 676 jest.mock('lightning/messageService');
 677 
 678 describe('c-account-publisher', () => {
 679     afterEach(() => {
 680         jest.clearAllMocks();
 681     });
 682 
 683     it('publishes account selection', () => {
 684         const element = createElement('c-account-publisher', {
 685             is: AccountPublisher
 686         });
 687         document.body.appendChild(element);
 688 
 689         // Trigger selection
 690         const accountCard = element.shadowRoot.querySelector('[data-id="001xxx"]');
 691         accountCard.click();
 692 
 693         // Assert publish was called
 694         expect(publish).toHaveBeenCalledWith(
 695             expect.anything(),
 696             ACCOUNT_SELECTED_CHANNEL,
 697             expect.objectContaining({
 698                 accountId: '001xxx'
 699             })
 700         );
 701     });
 702 });
 703 ```
 704 
 705 ### Test Subscriber
 706 
 707 ```javascript
 708 import { createElement } from 'lwc';
 709 import AccountSubscriber from 'c/accountSubscriber';
 710 import { subscribe } from 'lightning/messageService';
 711 
 712 jest.mock('lightning/messageService');
 713 
 714 describe('c-account-subscriber', () => {
 715     let messageHandler;
 716 
 717     beforeEach(() => {
 718         subscribe.mockImplementation((context, channel, handler, options) => {
 719             messageHandler = handler;
 720             return { subscription: 'mock-subscription' };
 721         });
 722     });
 723 
 724     it('subscribes on connected', () => {
 725         const element = createElement('c-account-subscriber', {
 726             is: AccountSubscriber
 727         });
 728         document.body.appendChild(element);
 729 
 730         expect(subscribe).toHaveBeenCalled();
 731     });
 732 
 733     it('handles incoming message', async () => {
 734         const element = createElement('c-account-subscriber', {
 735             is: AccountSubscriber
 736         });
 737         document.body.appendChild(element);
 738 
 739         // Simulate message
 740         messageHandler({
 741             accountId: '001xxx',
 742             accountName: 'Acme Corp'
 743         });
 744 
 745         await Promise.resolve();
 746 
 747         const accountName = element.shadowRoot.querySelector('.account-name');
 748         expect(accountName.textContent).toBe('Acme Corp');
 749     });
 750 });
 751 ```
 752 
 753 ---
 754 
 755 ## Complete Example: Account-Contact Sync
 756 
 757 ### Message Channel
 758 
 759 ```xml
 760 <!-- ContactSelected__c.messageChannel-meta.xml -->
 761 <?xml version="1.0" encoding="UTF-8"?>
 762 <LightningMessageChannel xmlns="http://soap.sforce.com/2006/04/metadata">
 763     <description>Contact selection messaging</description>
 764     <isExposed>true</isExposed>
 765     <lightningMessageFields>
 766         <fieldName>contactId</fieldName>
 767     </lightningMessageFields>
 768     <lightningMessageFields>
 769         <fieldName>contactName</fieldName>
 770     </lightningMessageFields>
 771     <lightningMessageFields>
 772         <fieldName>accountId</fieldName>
 773     </lightningMessageFields>
 774     <masterLabel>Contact Selected</masterLabel>
 775 </LightningMessageChannel>
 776 ```
 777 
 778 ### Publisher Component
 779 
 780 ```javascript
 781 // contactList.js
 782 import { LightningElement, api, wire } from 'lwc';
 783 import { publish, MessageContext } from 'lightning/messageService';
 784 import CONTACT_SELECTED from '@salesforce/messageChannel/ContactSelected__c';
 785 import getContacts from '@salesforce/apex/ContactController.getContacts';
 786 
 787 export default class ContactList extends LightningElement {
 788     @api accountId;
 789     contacts;
 790     @wire(MessageContext) messageContext;
 791 
 792     @wire(getContacts, { accountId: '$accountId' })
 793     wiredContacts({ data, error }) {
 794         if (data) {
 795             this.contacts = data;
 796         }
 797     }
 798 
 799     handleContactSelect(event) {
 800         const contactId = event.currentTarget.dataset.id;
 801         const contact = this.contacts.find(c => c.Id === contactId);
 802 
 803         publish(this.messageContext, CONTACT_SELECTED, {
 804             contactId: contact.Id,
 805             contactName: contact.Name,
 806             accountId: this.accountId
 807         });
 808     }
 809 }
 810 ```
 811 
 812 ### Subscriber Component
 813 
 814 ```javascript
 815 // contactDetails.js
 816 import { LightningElement, wire } from 'lwc';
 817 import { subscribe, MessageContext, APPLICATION_SCOPE } from 'lightning/messageService';
 818 import CONTACT_SELECTED from '@salesforce/messageChannel/ContactSelected__c';
 819 import getContactDetails from '@salesforce/apex/ContactController.getContactDetails';
 820 
 821 export default class ContactDetails extends LightningElement {
 822     subscription = null;
 823     contactId;
 824     contactDetails;
 825     @wire(MessageContext) messageContext;
 826 
 827     connectedCallback() {
 828         this.subscription = subscribe(
 829             this.messageContext,
 830             CONTACT_SELECTED,
 831             (message) => this.handleContactSelected(message),
 832             { scope: APPLICATION_SCOPE }
 833         );
 834     }
 835 
 836     disconnectedCallback() {
 837         unsubscribe(this.subscription);
 838     }
 839 
 840     async handleContactSelected(message) {
 841         this.contactId = message.contactId;
 842         try {
 843             this.contactDetails = await getContactDetails({
 844                 contactId: message.contactId
 845             });
 846         } catch (error) {
 847             console.error('Error loading contact details:', error);
 848         }
 849     }
 850 }
 851 ```
 852 
 853 ---
 854 
 855 ## Related Resources
 856 
 857 - [component-patterns.md](component-patterns.md) - Parent-child communication
 858 - [jest-testing.md](jest-testing.md) - Testing LMS components
 859 - [Official LMS Documentation](https://developer.salesforce.com/docs/component-library/documentation/en/lwc/lwc.use_message_channel)
