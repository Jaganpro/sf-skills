<!-- Parent: sf-lwc/SKILL.md -->
   1 # Advanced Jest Testing for LWC
   2 
   3 Comprehensive guide to testing Lightning Web Components using Jest, based on [James Simone's advanced testing patterns](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/).
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [Setup](#setup)
  10 2. [Core Testing Patterns](#core-testing-patterns)
  11 3. [Render Cycle Management](#render-cycle-management)
  12 4. [Mocking Strategies](#mocking-strategies)
  13 5. [Testing Wire Services](#testing-wire-services)
  14 6. [Testing Events](#testing-events)
  15 7. [Testing Navigation](#testing-navigation)
  16 8. [Testing LMS](#testing-lms)
  17 9. [Testing GraphQL](#testing-graphql)
  18 10. [Polyfills and Utilities](#polyfills-and-utilities)
  19 11. [Best Practices](#best-practices)
  20 
  21 ---
  22 
  23 ## Setup
  24 
  25 ### Install Dependencies
  26 
  27 ```bash
  28 # Install Jest and LWC testing tools
  29 npm install --save-dev @salesforce/sfdx-lwc-jest jest
  30 
  31 # Install additional utilities
  32 npm install --save-dev @testing-library/jest-dom
  33 ```
  34 
  35 ### Jest Configuration
  36 
  37 **File**: `jest.config.js`
  38 
  39 ```javascript
  40 const { jestConfig } = require('@salesforce/sfdx-lwc-jest/config');
  41 
  42 module.exports = {
  43     ...jestConfig,
  44     moduleNameMapper: {
  45         '^@salesforce/apex$': '<rootDir>/force-app/test/jest-mocks/apex',
  46         '^@salesforce/schema$': '<rootDir>/force-app/test/jest-mocks/schema',
  47         '^lightning/navigation$': '<rootDir>/force-app/test/jest-mocks/lightning/navigation',
  48         '^lightning/messageService$': '<rootDir>/force-app/test/jest-mocks/lightning/messageService'
  49     },
  50     setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  51     testPathIgnorePatterns: [
  52         '<rootDir>/node_modules/',
  53         '<rootDir>/.sfdx/'
  54     ],
  55     coverageThreshold: {
  56         global: {
  57             branches: 80,
  58             functions: 80,
  59             lines: 80,
  60             statements: 80
  61         }
  62     }
  63 };
  64 ```
  65 
  66 ### Setup File
  67 
  68 **File**: `jest.setup.js`
  69 
  70 ```javascript
  71 // ResizeObserver polyfill
  72 if (!window.ResizeObserver) {
  73     window.ResizeObserver = class ResizeObserver {
  74         constructor(callback) {
  75             this.callback = callback;
  76         }
  77         observe() {}
  78         unobserve() {}
  79         disconnect() {}
  80     };
  81 }
  82 
  83 // IntersectionObserver polyfill
  84 if (!window.IntersectionObserver) {
  85     window.IntersectionObserver = class IntersectionObserver {
  86         constructor(callback) {
  87             this.callback = callback;
  88         }
  89         observe() {}
  90         unobserve() {}
  91         disconnect() {}
  92     };
  93 }
  94 
  95 // Custom matchers
  96 expect.extend({
  97     toHaveClass(element, className) {
  98         const pass = element.classList.contains(className);
  99         return {
 100             pass,
 101             message: () => pass
 102                 ? `Expected element NOT to have class "${className}"`
 103                 : `Expected element to have class "${className}"`
 104         };
 105     }
 106 });
 107 ```
 108 
 109 ---
 110 
 111 ## Core Testing Patterns
 112 
 113 ### Basic Test Structure
 114 
 115 ```javascript
 116 import { createElement } from 'lwc';
 117 import MyComponent from 'c/myComponent';
 118 
 119 describe('c-my-component', () => {
 120     afterEach(() => {
 121         // Clean up DOM
 122         while (document.body.firstChild) {
 123             document.body.removeChild(document.body.firstChild);
 124         }
 125         // Clear all mocks
 126         jest.clearAllMocks();
 127     });
 128 
 129     it('renders correctly', () => {
 130         const element = createElement('c-my-component', {
 131             is: MyComponent
 132         });
 133         document.body.appendChild(element);
 134 
 135         expect(element.shadowRoot.querySelector('h1')).not.toBeNull();
 136     });
 137 });
 138 ```
 139 
 140 ### DOM Cleanup Pattern
 141 
 142 ```javascript
 143 describe('c-my-component', () => {
 144     let element;
 145 
 146     beforeEach(() => {
 147         element = createElement('c-my-component', { is: MyComponent });
 148         document.body.appendChild(element);
 149     });
 150 
 151     afterEach(() => {
 152         // CRITICAL: Prevent state bleed between tests
 153         while (document.body.firstChild) {
 154             document.body.removeChild(document.body.firstChild);
 155         }
 156         jest.clearAllMocks();
 157     });
 158 
 159     it('test case 1', () => {
 160         // Element is fresh for each test
 161     });
 162 
 163     it('test case 2', () => {
 164         // Element is fresh for each test
 165     });
 166 });
 167 ```
 168 
 169 ---
 170 
 171 ## Render Cycle Management
 172 
 173 ### Render Cycle Helper
 174 
 175 Based on [James Simone's pattern](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/).
 176 
 177 ```javascript
 178 // testUtils.js
 179 export const runRenderingLifecycle = async (reasons = ['render']) => {
 180     while (reasons.length > 0) {
 181         await Promise.resolve(reasons.pop());
 182     }
 183 };
 184 
 185 // Alias for brevity
 186 export const flushPromises = () => runRenderingLifecycle();
 187 ```
 188 
 189 ### Usage in Tests
 190 
 191 ```javascript
 192 import { runRenderingLifecycle, flushPromises } from './testUtils';
 193 
 194 it('updates after property change', async () => {
 195     const element = createElement('c-example', { is: Example });
 196     document.body.appendChild(element);
 197 
 198     // Change property
 199     element.greeting = 'new value';
 200 
 201     // Wait for render cycle
 202     await runRenderingLifecycle(['property change', 'render']);
 203 
 204     // Assert
 205     const div = element.shadowRoot.querySelector('div');
 206     expect(div.textContent).toBe('new value');
 207 });
 208 
 209 it('handles async operation', async () => {
 210     const element = createElement('c-example', { is: Example });
 211     document.body.appendChild(element);
 212 
 213     // Trigger async action
 214     const button = element.shadowRoot.querySelector('button');
 215     button.click();
 216 
 217     // Flush all promises
 218     await flushPromises();
 219 
 220     // Assert
 221     expect(element.shadowRoot.querySelector('.result')).not.toBeNull();
 222 });
 223 ```
 224 
 225 ---
 226 
 227 ## Mocking Strategies
 228 
 229 ### Mock Apex Imports
 230 
 231 ```javascript
 232 // __mocks__/apex.js
 233 export default function createApexTestWireAdapter() {
 234     return jest.fn();
 235 }
 236 
 237 // Component test
 238 import getAccounts from '@salesforce/apex/AccountController.getAccounts';
 239 
 240 jest.mock(
 241     '@salesforce/apex/AccountController.getAccounts',
 242     () => ({ default: jest.fn() }),
 243     { virtual: true }
 244 );
 245 
 246 describe('c-account-list', () => {
 247     it('displays accounts', async () => {
 248         const MOCK_DATA = [
 249             { Id: '001xxx', Name: 'Acme' }
 250         ];
 251 
 252         getAccounts.mockResolvedValue(MOCK_DATA);
 253 
 254         const element = createElement('c-account-list', {
 255             is: AccountList
 256         });
 257         document.body.appendChild(element);
 258 
 259         await flushPromises();
 260 
 261         const items = element.shadowRoot.querySelectorAll('.account-item');
 262         expect(items.length).toBe(1);
 263     });
 264 });
 265 ```
 266 
 267 ### Mock Schema Imports
 268 
 269 ```javascript
 270 // __mocks__/schema.js
 271 export default {
 272     'Account.Name': 'Name',
 273     'Account.Industry': 'Industry',
 274     'Contact.FirstName': 'FirstName'
 275 };
 276 
 277 // Component test
 278 jest.mock('@salesforce/schema/Account.Name', () => 'Name', { virtual: true });
 279 jest.mock('@salesforce/schema/Account.Industry', () => 'Industry', { virtual: true });
 280 ```
 281 
 282 ### Mock Platform Events
 283 
 284 ```javascript
 285 // Mock ShowToastEvent
 286 import { ShowToastEvent } from 'lightning/platformShowToastEvent';
 287 
 288 jest.mock('lightning/platformShowToastEvent', () => ({
 289     ShowToastEvent: jest.fn()
 290 }), { virtual: true });
 291 
 292 it('shows toast on success', () => {
 293     const element = createElement('c-example', { is: Example });
 294     document.body.appendChild(element);
 295 
 296     const handler = jest.fn();
 297     element.addEventListener('showtoast', handler);
 298 
 299     // Trigger action
 300     const button = element.shadowRoot.querySelector('button');
 301     button.click();
 302 
 303     // Assert toast was dispatched
 304     expect(handler).toHaveBeenCalled();
 305     expect(handler.mock.calls[0][0].detail.title).toBe('Success');
 306 });
 307 ```
 308 
 309 ---
 310 
 311 ## Testing Wire Services
 312 
 313 ### Test Wire Adapter
 314 
 315 ```javascript
 316 import { createElement } from 'lwc';
 317 import AccountCard from 'c/accountCard';
 318 import { getRecord } from 'lightning/uiRecordApi';
 319 
 320 // Emit data from wire
 321 const mockGetRecord = require('lightning/uiRecordApi');
 322 
 323 describe('c-account-card', () => {
 324     afterEach(() => {
 325         while (document.body.firstChild) {
 326             document.body.removeChild(document.body.firstChild);
 327         }
 328         jest.clearAllMocks();
 329     });
 330 
 331     it('displays account data', async () => {
 332         const element = createElement('c-account-card', {
 333             is: AccountCard
 334         });
 335         element.recordId = '001xxx000003DGQ';
 336         document.body.appendChild(element);
 337 
 338         // Emit mock data to wire
 339         mockGetRecord.emit({
 340             Id: '001xxx000003DGQ',
 341             fields: {
 342                 Name: { value: 'Acme Corp' },
 343                 Industry: { value: 'Technology' }
 344             }
 345         });
 346 
 347         await flushPromises();
 348 
 349         const name = element.shadowRoot.querySelector('.account-name');
 350         expect(name.textContent).toBe('Acme Corp');
 351     });
 352 
 353     it('displays error', async () => {
 354         const element = createElement('c-account-card', {
 355             is: AccountCard
 356         });
 357         element.recordId = '001xxx000003DGQ';
 358         document.body.appendChild(element);
 359 
 360         // Emit error to wire
 361         mockGetRecord.error();
 362 
 363         await flushPromises();
 364 
 365         const error = element.shadowRoot.querySelector('.error-message');
 366         expect(error).not.toBeNull();
 367     });
 368 });
 369 ```
 370 
 371 ### Test Imperative Apex
 372 
 373 ```javascript
 374 import getAccounts from '@salesforce/apex/AccountController.getAccounts';
 375 
 376 jest.mock(
 377     '@salesforce/apex/AccountController.getAccounts',
 378     () => ({ default: jest.fn() }),
 379     { virtual: true }
 380 );
 381 
 382 it('loads accounts imperatively', async () => {
 383     const MOCK_ACCOUNTS = [
 384         { Id: '001xxx', Name: 'Acme' }
 385     ];
 386 
 387     getAccounts.mockResolvedValue(MOCK_ACCOUNTS);
 388 
 389     const element = createElement('c-account-search', {
 390         is: AccountSearch
 391     });
 392     document.body.appendChild(element);
 393 
 394     // Trigger search
 395     const input = element.shadowRoot.querySelector('input');
 396     input.value = 'Acme';
 397     input.dispatchEvent(new Event('change'));
 398 
 399     await flushPromises();
 400 
 401     expect(getAccounts).toHaveBeenCalledWith({ searchTerm: 'Acme' });
 402 
 403     const results = element.shadowRoot.querySelectorAll('.account-item');
 404     expect(results.length).toBe(1);
 405 });
 406 
 407 it('handles apex error', async () => {
 408     getAccounts.mockRejectedValue(new Error('Network error'));
 409 
 410     const element = createElement('c-account-search', {
 411         is: AccountSearch
 412     });
 413     document.body.appendChild(element);
 414 
 415     const input = element.shadowRoot.querySelector('input');
 416     input.value = 'Test';
 417     input.dispatchEvent(new Event('change'));
 418 
 419     await flushPromises();
 420 
 421     const errorMsg = element.shadowRoot.querySelector('.error');
 422     expect(errorMsg.textContent).toContain('Network error');
 423 });
 424 ```
 425 
 426 ---
 427 
 428 ## Testing Events
 429 
 430 ### Test Custom Events
 431 
 432 ```javascript
 433 it('dispatches custom event', () => {
 434     const element = createElement('c-event-emitter', {
 435         is: EventEmitter
 436     });
 437     document.body.appendChild(element);
 438 
 439     const handler = jest.fn();
 440     element.addEventListener('itemselected', handler);
 441 
 442     // Trigger event
 443     const button = element.shadowRoot.querySelector('button');
 444     button.click();
 445 
 446     // Assert
 447     expect(handler).toHaveBeenCalled();
 448     expect(handler.mock.calls[0][0].detail.id).toBe('001xxx');
 449 });
 450 ```
 451 
 452 ### Test Event Bubbling
 453 
 454 ```javascript
 455 it('bubbles event to parent', () => {
 456     const parent = createElement('c-parent', { is: Parent });
 457     document.body.appendChild(parent);
 458 
 459     const handler = jest.fn();
 460     parent.addEventListener('itemselected', handler);
 461 
 462     // Get child component
 463     const child = parent.shadowRoot.querySelector('c-child');
 464     const button = child.shadowRoot.querySelector('button');
 465     button.click();
 466 
 467     expect(handler).toHaveBeenCalled();
 468 });
 469 ```
 470 
 471 ### Test Event Composition
 472 
 473 ```javascript
 474 it('composes event across shadow DOM', () => {
 475     const element = createElement('c-composer', {
 476         is: Composer
 477     });
 478     document.body.appendChild(element);
 479 
 480     const handler = jest.fn();
 481     document.addEventListener('customevent', handler);
 482 
 483     // Trigger composed event
 484     const button = element.shadowRoot.querySelector('button');
 485     button.click();
 486 
 487     expect(handler).toHaveBeenCalled();
 488 });
 489 ```
 490 
 491 ---
 492 
 493 ## Testing Navigation
 494 
 495 ### Mock Navigation Mixin
 496 
 497 ```javascript
 498 // __mocks__/lightning/navigation.js
 499 export const NavigationMixin = (Base) => {
 500     return class extends Base {
 501         [NavigationMixin.Navigate](pageReference, replace) {
 502             this._navigate = { pageReference, replace };
 503         }
 504     };
 505 };
 506 
 507 NavigationMixin.Navigate = Symbol('Navigate');
 508 
 509 // Component test
 510 import { NavigationMixin } from 'lightning/navigation';
 511 
 512 it('navigates to record page', async () => {
 513     const element = createElement('c-navigator', {
 514         is: Navigator
 515     });
 516     document.body.appendChild(element);
 517 
 518     const button = element.shadowRoot.querySelector('button');
 519     button.click();
 520 
 521     await flushPromises();
 522 
 523     expect(element._navigate.pageReference.type).toBe('standard__recordPage');
 524     expect(element._navigate.pageReference.attributes.recordId).toBe('001xxx');
 525 });
 526 ```
 527 
 528 ---
 529 
 530 ## Testing LMS
 531 
 532 ### Mock Message Service
 533 
 534 ```javascript
 535 // __mocks__/lightning/messageService.js
 536 export const publish = jest.fn();
 537 export const subscribe = jest.fn();
 538 export const unsubscribe = jest.fn();
 539 export const MessageContext = Symbol('MessageContext');
 540 export const APPLICATION_SCOPE = Symbol('APPLICATION_SCOPE');
 541 ```
 542 
 543 ### Test Publisher
 544 
 545 ```javascript
 546 import { publish, MessageContext } from 'lightning/messageService';
 547 import ACCOUNT_CHANNEL from '@salesforce/messageChannel/AccountSelected__c';
 548 
 549 jest.mock('lightning/messageService');
 550 
 551 it('publishes message on selection', () => {
 552     const element = createElement('c-publisher', {
 553         is: Publisher
 554     });
 555     document.body.appendChild(element);
 556 
 557     const button = element.shadowRoot.querySelector('button');
 558     button.click();
 559 
 560     expect(publish).toHaveBeenCalledWith(
 561         expect.anything(),
 562         ACCOUNT_CHANNEL,
 563         expect.objectContaining({ accountId: '001xxx' })
 564     );
 565 });
 566 ```
 567 
 568 ### Test Subscriber
 569 
 570 ```javascript
 571 import { subscribe, unsubscribe } from 'lightning/messageService';
 572 
 573 jest.mock('lightning/messageService');
 574 
 575 it('subscribes on connected', () => {
 576     const element = createElement('c-subscriber', {
 577         is: Subscriber
 578     });
 579     document.body.appendChild(element);
 580 
 581     expect(subscribe).toHaveBeenCalled();
 582 });
 583 
 584 it('unsubscribes on disconnected', () => {
 585     const element = createElement('c-subscriber', {
 586         is: Subscriber
 587     });
 588     document.body.appendChild(element);
 589     document.body.removeChild(element);
 590 
 591     expect(unsubscribe).toHaveBeenCalled();
 592 });
 593 
 594 it('handles incoming message', async () => {
 595     let messageHandler;
 596     subscribe.mockImplementation((context, channel, handler) => {
 597         messageHandler = handler;
 598         return { subscription: 'mock' };
 599     });
 600 
 601     const element = createElement('c-subscriber', {
 602         is: Subscriber
 603     });
 604     document.body.appendChild(element);
 605 
 606     // Simulate message
 607     messageHandler({ accountId: '001xxx', accountName: 'Acme' });
 608 
 609     await flushPromises();
 610 
 611     const name = element.shadowRoot.querySelector('.account-name');
 612     expect(name.textContent).toBe('Acme');
 613 });
 614 ```
 615 
 616 ---
 617 
 618 ## Testing GraphQL
 619 
 620 ### Mock GraphQL Adapter
 621 
 622 ```javascript
 623 import { graphql } from 'lightning/graphql';
 624 
 625 // Mock graphql wire adapter
 626 jest.mock('lightning/graphql', () => ({
 627     gql: jest.fn(query => query),
 628     graphql: jest.fn()
 629 }), { virtual: true });
 630 
 631 it('displays graphql query results', async () => {
 632     const element = createElement('c-graphql-component', {
 633         is: GraphqlComponent
 634     });
 635     document.body.appendChild(element);
 636 
 637     // Emit mock data
 638     const mockData = {
 639         uiapi: {
 640             query: {
 641                 Contact: {
 642                     edges: [
 643                         { node: { Id: '003xxx', Name: { value: 'John Doe' } } }
 644                     ]
 645                 }
 646             }
 647         }
 648     };
 649 
 650     graphql.emit({ data: mockData });
 651 
 652     await flushPromises();
 653 
 654     const contacts = element.shadowRoot.querySelectorAll('.contact-item');
 655     expect(contacts.length).toBe(1);
 656 });
 657 ```
 658 
 659 ---
 660 
 661 ## Polyfills and Utilities
 662 
 663 ### ResizeObserver Polyfill
 664 
 665 ```javascript
 666 if (!window.ResizeObserver) {
 667     window.ResizeObserver = class ResizeObserver {
 668         constructor(callback) {
 669             this.callback = callback;
 670         }
 671         observe() {}
 672         unobserve() {}
 673         disconnect() {}
 674     };
 675 }
 676 ```
 677 
 678 ### Proxy Unboxing (LWS Compatibility)
 679 
 680 ```javascript
 681 // Lightning Web Security proxifies objects
 682 // Unbox them for deep equality assertions
 683 
 684 it('compares complex objects', () => {
 685     const element = createElement('c-example', { is: Example });
 686     document.body.appendChild(element);
 687 
 688     // Unbox proxied data
 689     const unboxedData = JSON.parse(JSON.stringify(element.data));
 690 
 691     expect(unboxedData).toEqual({
 692         accounts: [
 693             { Id: '001xxx', Name: 'Acme' }
 694         ]
 695     });
 696 });
 697 ```
 698 
 699 ### Test Utilities Module
 700 
 701 ```javascript
 702 // testUtils.js
 703 export const runRenderingLifecycle = async (reasons = ['render']) => {
 704     while (reasons.length > 0) {
 705         await Promise.resolve(reasons.pop());
 706     }
 707 };
 708 
 709 export const flushPromises = () => runRenderingLifecycle();
 710 
 711 export const queryAll = (element, selector) => {
 712     return Array.from(element.shadowRoot.querySelectorAll(selector));
 713 };
 714 
 715 export const query = (element, selector) => {
 716     return element.shadowRoot.querySelector(selector);
 717 };
 718 
 719 export const waitFor = async (condition, timeout = 3000) => {
 720     const start = Date.now();
 721     while (!condition()) {
 722         if (Date.now() - start > timeout) {
 723             throw new Error('waitFor timeout');
 724         }
 725         await flushPromises();
 726     }
 727 };
 728 
 729 // Usage
 730 import { query, queryAll, waitFor } from './testUtils';
 731 
 732 it('uses test utils', async () => {
 733     const element = createElement('c-example', { is: Example });
 734     document.body.appendChild(element);
 735 
 736     const button = query(element, 'button');
 737     button.click();
 738 
 739     await waitFor(() => query(element, '.result') !== null);
 740 
 741     const items = queryAll(element, '.item');
 742     expect(items.length).toBeGreaterThan(0);
 743 });
 744 ```
 745 
 746 ---
 747 
 748 ## Best Practices
 749 
 750 ### 1. Always Clean Up DOM
 751 
 752 ```javascript
 753 afterEach(() => {
 754     while (document.body.firstChild) {
 755         document.body.removeChild(document.body.firstChild);
 756     }
 757     jest.clearAllMocks();
 758 });
 759 ```
 760 
 761 ### 2. Use Descriptive Test Names
 762 
 763 ```javascript
 764 // BAD
 765 it('works', () => { /* ... */ });
 766 
 767 // GOOD
 768 it('displays error message when apex call fails', () => { /* ... */ });
 769 ```
 770 
 771 ### 3. Test User Interactions
 772 
 773 ```javascript
 774 it('filters list when search input changes', async () => {
 775     const element = createElement('c-searchable-list', {
 776         is: SearchableList
 777     });
 778     document.body.appendChild(element);
 779 
 780     const input = element.shadowRoot.querySelector('input');
 781     input.value = 'test';
 782     input.dispatchEvent(new Event('input'));
 783 
 784     await flushPromises();
 785 
 786     const items = element.shadowRoot.querySelectorAll('.list-item');
 787     expect(items.length).toBeLessThan(10); // Filtered results
 788 });
 789 ```
 790 
 791 ### 4. Test Error States
 792 
 793 ```javascript
 794 it('displays error when wire service fails', async () => {
 795     mockGetRecord.error({ message: 'Network error' });
 796 
 797     const element = createElement('c-example', { is: Example });
 798     document.body.appendChild(element);
 799 
 800     await flushPromises();
 801 
 802     const error = element.shadowRoot.querySelector('.error-message');
 803     expect(error.textContent).toContain('Network error');
 804 });
 805 ```
 806 
 807 ### 5. Test Loading States
 808 
 809 ```javascript
 810 it('shows spinner during data load', async () => {
 811     const element = createElement('c-async-component', {
 812         is: AsyncComponent
 813     });
 814     document.body.appendChild(element);
 815 
 816     // Before data loads
 817     let spinner = element.shadowRoot.querySelector('lightning-spinner');
 818     expect(spinner).not.toBeNull();
 819 
 820     // Emit data
 821     mockGetData.emit([{ Id: '001xxx' }]);
 822     await flushPromises();
 823 
 824     // After data loads
 825     spinner = element.shadowRoot.querySelector('lightning-spinner');
 826     expect(spinner).toBeNull();
 827 });
 828 ```
 829 
 830 ### 6. Test Accessibility
 831 
 832 ```javascript
 833 it('has proper ARIA labels', () => {
 834     const element = createElement('c-accessible', {
 835         is: Accessible
 836     });
 837     document.body.appendChild(element);
 838 
 839     const button = element.shadowRoot.querySelector('button');
 840     expect(button.getAttribute('aria-label')).toBe('Delete record');
 841 });
 842 
 843 it('manages focus correctly', async () => {
 844     const element = createElement('c-modal', { is: Modal });
 845     document.body.appendChild(element);
 846 
 847     element.openModal();
 848     await flushPromises();
 849 
 850     const firstFocusable = element.shadowRoot.querySelector('.focusable');
 851     expect(document.activeElement).toBe(firstFocusable);
 852 });
 853 ```
 854 
 855 ### 7. Organize Tests by Feature
 856 
 857 ```javascript
 858 describe('c-account-list', () => {
 859     describe('data loading', () => {
 860         it('displays accounts when data loads successfully');
 861         it('shows error when data load fails');
 862         it('shows spinner during loading');
 863     });
 864 
 865     describe('filtering', () => {
 866         it('filters by search term');
 867         it('filters by industry');
 868         it('clears filters');
 869     });
 870 
 871     describe('selection', () => {
 872         it('selects account on click');
 873         it('dispatches selection event');
 874         it('highlights selected account');
 875     });
 876 });
 877 ```
 878 
 879 ---
 880 
 881 ## Complete Test Example
 882 
 883 ```javascript
 884 import { createElement } from 'lwc';
 885 import AccountList from 'c/accountList';
 886 import getAccounts from '@salesforce/apex/AccountController.getAccounts';
 887 import { publish } from 'lightning/messageService';
 888 import ACCOUNT_SELECTED from '@salesforce/messageChannel/AccountSelected__c';
 889 
 890 // Mocks
 891 jest.mock('@salesforce/apex/AccountController.getAccounts', () => ({
 892     default: jest.fn()
 893 }), { virtual: true });
 894 
 895 jest.mock('lightning/messageService');
 896 
 897 const MOCK_ACCOUNTS = [
 898     { Id: '001xxx001', Name: 'Acme Corp', Industry: 'Technology' },
 899     { Id: '001xxx002', Name: 'Global Inc', Industry: 'Finance' }
 900 ];
 901 
 902 const flushPromises = () => new Promise(resolve => setImmediate(resolve));
 903 
 904 describe('c-account-list', () => {
 905     afterEach(() => {
 906         while (document.body.firstChild) {
 907             document.body.removeChild(document.body.firstChild);
 908         }
 909         jest.clearAllMocks();
 910     });
 911 
 912     describe('data loading', () => {
 913         it('displays accounts when loaded successfully', async () => {
 914             getAccounts.mockResolvedValue(MOCK_ACCOUNTS);
 915 
 916             const element = createElement('c-account-list', {
 917                 is: AccountList
 918             });
 919             document.body.appendChild(element);
 920 
 921             await flushPromises();
 922 
 923             const items = element.shadowRoot.querySelectorAll('.account-item');
 924             expect(items.length).toBe(2);
 925             expect(items[0].textContent).toContain('Acme Corp');
 926         });
 927 
 928         it('displays error when fetch fails', async () => {
 929             getAccounts.mockRejectedValue(new Error('Network error'));
 930 
 931             const element = createElement('c-account-list', {
 932                 is: AccountList
 933             });
 934             document.body.appendChild(element);
 935 
 936             await flushPromises();
 937 
 938             const error = element.shadowRoot.querySelector('.error-message');
 939             expect(error).not.toBeNull();
 940             expect(error.textContent).toContain('Network error');
 941         });
 942     });
 943 
 944     describe('selection', () => {
 945         it('publishes message when account selected', async () => {
 946             getAccounts.mockResolvedValue(MOCK_ACCOUNTS);
 947 
 948             const element = createElement('c-account-list', {
 949                 is: AccountList
 950             });
 951             document.body.appendChild(element);
 952 
 953             await flushPromises();
 954 
 955             const firstAccount = element.shadowRoot.querySelector('.account-item');
 956             firstAccount.click();
 957 
 958             expect(publish).toHaveBeenCalledWith(
 959                 expect.anything(),
 960                 ACCOUNT_SELECTED,
 961                 expect.objectContaining({
 962                     accountId: '001xxx001',
 963                     accountName: 'Acme Corp'
 964                 })
 965             );
 966         });
 967     });
 968 
 969     describe('filtering', () => {
 970         it('filters accounts by search term', async () => {
 971             getAccounts.mockResolvedValue(MOCK_ACCOUNTS);
 972 
 973             const element = createElement('c-account-list', {
 974                 is: AccountList
 975             });
 976             document.body.appendChild(element);
 977 
 978             await flushPromises();
 979 
 980             const searchInput = element.shadowRoot.querySelector('input');
 981             searchInput.value = 'Acme';
 982             searchInput.dispatchEvent(new Event('input'));
 983 
 984             await flushPromises();
 985 
 986             const visibleItems = element.shadowRoot.querySelectorAll('.account-item:not(.hidden)');
 987             expect(visibleItems.length).toBe(1);
 988             expect(visibleItems[0].textContent).toContain('Acme Corp');
 989         });
 990     });
 991 });
 992 ```
 993 
 994 ---
 995 
 996 ## Related Resources
 997 
 998 - [component-patterns.md](component-patterns.md) - Component implementation patterns
 999 - [lms-guide.md](lms-guide.md) - Lightning Message Service
1000 - [James Simone - Advanced LWC Jest Testing](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/)
1001 - [LWC Recipes - Tests](https://github.com/trailheadapps/lwc-recipes/tree/main/force-app/main/default/lwc/__tests__)
