<!-- Parent: sf-lwc/SKILL.md -->
# LWC Component Patterns

Comprehensive code examples for common Lightning Web Component patterns.

---

## Table of Contents

1. [PICKLES Framework Details](#pickles-framework-details)
2. [Wire Service Patterns](#wire-service-patterns)
   - [Wire vs Imperative Apex Calls](#wire-vs-imperative-apex-calls)
3. [GraphQL Patterns](#graphql-patterns)
4. [Modal Component Pattern](#modal-component-pattern)
5. [Record Picker Pattern](#record-picker-pattern)
6. [Workspace API Pattern](#workspace-api-pattern)
7. [Parent-Child Communication](#parent-child-communication)
8. [Sibling Communication (via Parent)](#sibling-communication-via-parent)
9. [Navigation Patterns](#navigation-patterns)
10. [TypeScript Patterns](#typescript-patterns)
11. [Apex Controller Patterns](#apex-controller-patterns)

---

## PICKLES Framework Details

### P - Prototype

**Purpose**: Validate ideas early before full implementation.

| Action | Description |
|--------|-------------|
| Wireframe | Create high-level component sketches |
| Mock Data | Use sample data to test functionality |
| Stakeholder Review | Gather feedback before development |
| Separation of Concerns | Break into smaller functional pieces |

```javascript
// Mock data pattern for prototyping
const MOCK_ACCOUNTS = [
    { Id: '001MOCK001', Name: 'Acme Corp', Industry: 'Technology' },
    { Id: '001MOCK002', Name: 'Global Inc', Industry: 'Finance' }
];

export default class AccountPrototype extends LightningElement {
    accounts = MOCK_ACCOUNTS; // Replace with wire/Apex later
}
```

### I - Integrate

**Purpose**: Determine how components interact with data systems.

**Integration Checklist**:
- [ ] Implement error handling with clear user notifications
- [ ] Add loading spinners to prevent duplicate requests
- [ ] Use LDS for single-object operations (minimizes DML)
- [ ] Respect FLS and CRUD in Apex implementations
- [ ] Store `wiredResult` for `refreshApex()` support

### C - Composition

**Purpose**: Structure how LWCs nest and communicate.

**Best Practices**:
- Maintain shallow component hierarchies (max 3-4 levels)
- Single responsibility per component
- Clean up subscriptions in `disconnectedCallback()`
- Use custom events purposefully, not for every interaction

```javascript
// Parent-managed composition pattern
// parent.js
handleChildEvent(event) {
    this.selectedId = event.detail.id;
    // Update child via @api
    this.template.querySelector('c-child').selectedId = this.selectedId;
}
```

### K - Kinetics

**Purpose**: Manage user interaction and event responsiveness.

```javascript
// Debounce pattern for search
delayTimeout;

handleSearchChange(event) {
    const searchTerm = event.target.value;
    clearTimeout(this.delayTimeout);
    this.delayTimeout = setTimeout(() => {
        this.dispatchEvent(new CustomEvent('search', {
            detail: { searchTerm }
        }));
    }, 300);
}
```

### L - Libraries

**Purpose**: Leverage Salesforce-provided and platform tools.

**Recommended Platform Features**:

| API/Module | Use Case |
|------------|----------|
| `lightning/navigation` | Page/record navigation |
| `lightning/uiRecordApi` | LDS operations (getRecord, updateRecord) |
| `lightning/platformShowToastEvent` | User notifications |
| `lightning/modal` | Native modal dialogs |
| Base Components | Pre-built UI (button, input, datatable) |
| `lightning/refresh` | Dispatch refresh events |

**Avoid reinventing** what base components already provide!

### E - Execution

**Purpose**: Optimize performance and resource efficiency.

**Performance Checklist**:
- [ ] Lazy load with `if:true` / `lwc:if`
- [ ] Use `key` directive in iterations
- [ ] Cache computed values in getters
- [ ] Avoid property updates that trigger re-renders
- [ ] Use browser DevTools Performance tab

### S - Security

**Purpose**: Enforce access control and data protection.

```apex
// Secure Apex pattern
@AuraEnabled(cacheable=true)
public static List<Account> getAccounts(String searchTerm) {
    String searchKey = '%' + String.escapeSingleQuotes(searchTerm) + '%';
    return [
        SELECT Id, Name, Industry
        FROM Account
        WHERE Name LIKE :searchKey
        WITH SECURITY_ENFORCED
        LIMIT 50
    ];
}
```

---

## Wire Service Patterns

### Wire vs Imperative Apex Calls

LWC can interact with Apex in two ways: **@wire** (reactive/declarative) and **imperative calls** (manual/programmatic). Understanding when to use each is critical for building performant, maintainable components.

#### Quick Comparison

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    WIRE vs IMPERATIVE APEX CALLS                                     │
├──────────────────┬──────────────────────────────┬────────────────────────────────────┤
│    Aspect        │      Wire (@wire)            │      Imperative Calls              │
├──────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ Execution        │ Automatic / Reactive         │ Manual / Programmatic              │
│ DML Operations   │ ❌ Read-Only                 │ ✅ Insert / Update / Delete        │
│ Data Updates     │ ✅ Auto on Parameter Change  │ ❌ Manual Refresh Required         │
│ Control          │ ⚠️ Low (framework decides)   │ ✅ Full (you decide when/how)      │
│ Error Handling   │ ✅ Framework Managed         │ ⚠️ Developer Managed               │
│ Supported Objects│ ⚠️ UI API Only               │ ✅ All Objects                     │
│ Caching          │ ✅ Built-in (cacheable=true) │ ❌ No automatic caching            │
└──────────────────┴──────────────────────────────┴────────────────────────────────────┘
```

#### Pros & Cons

| Wire (@wire) | Imperative Calls |
|--------------|------------------|
| ✅ Auto UI sync & caching | ✅ Supports DML & all objects |
| ✅ Less boilerplate code | ✅ Full control over timing |
| ✅ Reactive to parameter changes | ✅ Can handle complex logic |
| ❌ Read-only, limited objects | ❌ Manual handling, no auto refresh |
| ❌ Can't control execution timing | ❌ More error handling code needed |

#### When to Use Each

**Use Wire (@wire) when:**
- 📌 Read-only data display
- 📌 Auto-refresh UI when parameters change
- 📌 Stable parameters (recordId, filter values)
- 📌 Working with UI API supported objects

**Use Imperative Calls when:**
- 📌 User actions (clicks, form submissions)
- 📌 DML operations (Insert, Update, Delete)
- 📌 Dynamic parameters determined at runtime
- 📌 Custom objects or complex queries
- 📌 Need control over execution timing

#### Side-by-Side Code Examples

**Wire Example** - Data loads automatically when `selectedIndustry` changes:

```javascript
import { LightningElement, wire } from 'lwc';
import fetchAccounts from '@salesforce/apex/AccountController.fetchAccounts';

export default class WireExample extends LightningElement {
    selectedIndustry = 'Technology';
    accounts;
    error;

    // Automatically re-fetches when selectedIndustry changes
    @wire(fetchAccounts, { industry: '$selectedIndustry' })
    wiredAccounts({ data, error }) {
        if (data) {
            this.accounts = data;
            this.error = undefined;
        } else if (error) {
            this.error = error;
            this.accounts = undefined;
        }
    }
}
```

**Imperative Example** - Data loads only when user triggers action:

```javascript
import { LightningElement } from 'lwc';
import fetchAccounts from '@salesforce/apex/AccountController.fetchAccounts';

export default class ImperativeExample extends LightningElement {
    selectedIndustry = 'Technology';
    accounts;
    error;
    isLoading = false;

    // Called explicitly when user clicks button or submits form
    async fetchAccounts() {
        this.isLoading = true;
        try {
            this.accounts = await fetchAccounts({
                industry: this.selectedIndustry
            });
            this.error = undefined;
        } catch (error) {
            this.error = error;
            this.accounts = undefined;
        } finally {
            this.isLoading = false;
        }
    }
}
```

#### Decision Tree

```
                    ┌─────────────────────────────┐
                    │   Need to modify data?      │
                    │   (Insert/Update/Delete)    │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴───────────────┐
                    │                             │
                   YES                            NO
                    │                             │
                    ▼                             ▼
         ┌─────────────────┐        ┌─────────────────────────┐
         │   IMPERATIVE    │        │  Should data auto-      │
         │   (Use await)   │        │  refresh on param       │
         └─────────────────┘        │  change?                │
                                    └───────────┬─────────────┘
                                                │
                                    ┌───────────┴───────────┐
                                    │                       │
                                   YES                      NO
                                    │                       │
                                    ▼                       ▼
                         ┌─────────────────┐     ┌─────────────────┐
                         │   @WIRE         │     │   IMPERATIVE    │
                         │   (Reactive)    │     │   (On-demand)   │
                         └─────────────────┘     └─────────────────┘
```

---

### 1. Basic Data Display (Wire Service)

```javascript
// accountCard.js
import { LightningElement, api, wire } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import NAME_FIELD from '@salesforce/schema/Account.Name';
import INDUSTRY_FIELD from '@salesforce/schema/Account.Industry';

const FIELDS = [NAME_FIELD, INDUSTRY_FIELD];

export default class AccountCard extends LightningElement {
    @api recordId;

    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    account;

    get name() {
        return getFieldValue(this.account.data, NAME_FIELD);
    }

    get industry() {
        return getFieldValue(this.account.data, INDUSTRY_FIELD);
    }

    get isLoading() {
        return !this.account.data && !this.account.error;
    }
}
```

```html
<!-- accountCard.html -->
<template>
    <template lwc:if={isLoading}>
        <lightning-spinner alternative-text="Loading"></lightning-spinner>
    </template>
    <template lwc:if={account.data}>
        <div class="slds-box slds-theme_default">
            <h2 class="slds-text-heading_medium">{name}</h2>
            <p class="slds-text-color_weak">{industry}</p>
        </div>
    </template>
    <template lwc:if={account.error}>
        <p class="slds-text-color_error">{account.error.body.message}</p>
    </template>
</template>
```

### 2. Wire Service with Apex

```javascript
// contactList.js
import { LightningElement, api, wire } from 'lwc';
import getContacts from '@salesforce/apex/ContactController.getContacts';
import { refreshApex } from '@salesforce/apex';

export default class ContactList extends LightningElement {
    @api recordId;
    contacts;
    error;
    wiredContactsResult;

    @wire(getContacts, { accountId: '$recordId' })
    wiredContacts(result) {
        this.wiredContactsResult = result; // Store for refreshApex
        const { error, data } = result;
        if (data) {
            this.contacts = data;
            this.error = undefined;
        } else if (error) {
            this.error = error;
            this.contacts = undefined;
        }
    }

    async handleRefresh() {
        await refreshApex(this.wiredContactsResult);
    }
}
```

---

## GraphQL Patterns

> **Module Note**: `lightning/graphql` supersedes `lightning/uiGraphQLApi` and provides newer features like mutations, optional fields, and dynamic query construction.

### GraphQL Query (Wire Adapter)

```javascript
// graphqlContacts.js
import { LightningElement, wire } from 'lwc';
import { gql, graphql } from 'lightning/graphql';

const CONTACTS_QUERY = gql`
    query ContactsQuery($first: Int, $after: String) {
        uiapi {
            query {
                Contact(first: $first, after: $after) {
                    edges {
                        node {
                            Id
                            Name { value }
                            Email { value }
                            Account {
                                Name { value }
                            }
                        }
                        cursor
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
    }
`;

export default class GraphqlContacts extends LightningElement {
    contacts;
    pageInfo;
    error;
    _cursor;

    @wire(graphql, {
        query: CONTACTS_QUERY,
        variables: '$queryVariables'
    })
    wiredContacts({ data, error }) {
        if (data) {
            const result = data.uiapi.query.Contact;
            this.contacts = result.edges.map(edge => ({
                id: edge.node.Id,
                name: edge.node.Name.value,
                email: edge.node.Email?.value,
                accountName: edge.node.Account?.Name?.value
            }));
            this.pageInfo = result.pageInfo;
        } else if (error) {
            this.error = error;
        }
    }

    get queryVariables() {
        return { first: 10, after: this._cursor };
    }

    loadMore() {
        if (this.pageInfo?.hasNextPage) {
            this._cursor = this.pageInfo.endCursor;
        }
    }
}
```

### GraphQL Mutations (Spring '26 - GA in API 66.0)

Mutations allow create, update, and delete operations via GraphQL. Use `executeMutation` for imperative operations.

```javascript
// graphqlAccountMutation.js
import { LightningElement, track } from 'lwc';
import { gql, executeMutation } from 'lightning/graphql';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

// Create mutation
const CREATE_ACCOUNT = gql`
    mutation CreateAccount($name: String!, $industry: String) {
        uiapi {
            AccountCreate(input: {
                Account: {
                    Name: $name
                    Industry: $industry
                }
            }) {
                Record {
                    Id
                    Name { value }
                    Industry { value }
                }
            }
        }
    }
`;

// Update mutation
const UPDATE_ACCOUNT = gql`
    mutation UpdateAccount($id: ID!, $name: String!) {
        uiapi {
            AccountUpdate(input: {
                Account: {
                    Id: $id
                    Name: $name
                }
            }) {
                Record {
                    Id
                    Name { value }
                }
            }
        }
    }
`;

// Delete mutation
const DELETE_ACCOUNT = gql`
    mutation DeleteAccount($id: ID!) {
        uiapi {
            AccountDelete(input: { Account: { Id: $id } }) {
                Id
            }
        }
    }
`;

export default class GraphqlAccountMutation extends LightningElement {
    @track accountName = '';
    @track industry = '';
    isLoading = false;

    handleNameChange(event) {
        this.accountName = event.target.value;
    }

    handleIndustryChange(event) {
        this.industry = event.target.value;
    }

    async handleCreate() {
        if (!this.accountName) return;

        this.isLoading = true;
        try {
            const result = await executeMutation(CREATE_ACCOUNT, {
                variables: {
                    name: this.accountName,
                    industry: this.industry || null
                }
            });

            const newRecord = result.data.uiapi.AccountCreate.Record;
            this.showToast('Success', `Account "${newRecord.Name.value}" created`, 'success');
            this.resetForm();
        } catch (error) {
            this.handleError(error);
        } finally {
            this.isLoading = false;
        }
    }

    async handleUpdate(accountId, newName) {
        try {
            const result = await executeMutation(UPDATE_ACCOUNT, {
                variables: { id: accountId, name: newName }
            });
            this.showToast('Success', 'Account updated', 'success');
            return result.data.uiapi.AccountUpdate.Record;
        } catch (error) {
            this.handleError(error);
        }
    }

    async handleDelete(accountId) {
        try {
            await executeMutation(DELETE_ACCOUNT, {
                variables: { id: accountId }
            });
            this.showToast('Success', 'Account deleted', 'success');
        } catch (error) {
            this.handleError(error);
        }
    }

    handleError(error) {
        const message = error.graphQLErrors
            ? error.graphQLErrors.map(e => e.message).join(', ')
            : error.message || 'Unknown error';
        this.showToast('Error', message, 'error');
    }

    showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }

    resetForm() {
        this.accountName = '';
        this.industry = '';
    }
}
```

### GraphQL Mutation Operations

| Operation | Mutation Type | Notes |
|-----------|---------------|-------|
| **Create** | `{Object}Create` | Can request fields from newly created record |
| **Update** | `{Object}Update` | Cannot query fields in same request |
| **Delete** | `{Object}Delete` | Cannot query fields in same request |

### allOrNone Parameter

Control transaction behavior with `allOrNone` (default: `true`):

```javascript
const BATCH_CREATE = gql`
    mutation BatchCreate($allOrNone: Boolean = true) {
        uiapi(allOrNone: $allOrNone) {
            acc1: AccountCreate(input: { Account: { Name: "Account 1" } }) {
                Record { Id }
            }
            acc2: AccountCreate(input: { Account: { Name: "Account 2" } }) {
                Record { Id }
            }
        }
    }
`;

// If allOrNone=true: All rollback if any fails
// If allOrNone=false: Only failed operations rollback
```

---

## Modal Component Pattern

Based on [James Simone's composable modal pattern](https://www.jamessimone.net/blog/joys-of-apex/lwc-composable-modal/).

```javascript
// composableModal.js
import { LightningElement, api } from 'lwc';

const OUTER_MODAL_CLASS = 'outerModalContent';

export default class ComposableModal extends LightningElement {
    @api modalHeader;
    @api modalTagline;
    @api modalSaveHandler;

    _isOpen = false;
    _focusableElements = [];

    @api
    toggleModal() {
        this._isOpen = !this._isOpen;
        if (this._isOpen) {
            this._focusableElements = [...this.querySelectorAll('.focusable')];
            this._focusFirstElement();
            window.addEventListener('keyup', this._handleKeyUp);
        } else {
            window.removeEventListener('keyup', this._handleKeyUp);
        }
    }

    get modalAriaHidden() {
        return !this._isOpen;
    }

    get modalClass() {
        return this._isOpen
            ? 'slds-modal slds-visible slds-fade-in-open'
            : 'slds-modal slds-hidden';
    }

    get backdropClass() {
        return this._isOpen ? 'slds-backdrop slds-backdrop_open' : 'slds-backdrop';
    }

    _handleKeyUp = (event) => {
        if (event.code === 'Escape') {
            this.toggleModal();
        } else if (event.code === 'Tab') {
            this._handleTabNavigation(event);
        }
    }

    _handleTabNavigation(event) {
        // Focus trap logic - keep focus within modal
        const activeEl = this.template.activeElement;
        const lastIndex = this._focusableElements.length - 1;
        const currentIndex = this._focusableElements.indexOf(activeEl);

        if (event.shiftKey && currentIndex === 0) {
            this._focusableElements[lastIndex]?.focus();
        } else if (!event.shiftKey && currentIndex === lastIndex) {
            this._focusFirstElement();
        }
    }

    _focusFirstElement() {
        if (this._focusableElements.length > 0) {
            this._focusableElements[0].focus();
        }
    }

    handleBackdropClick(event) {
        if (event.target.classList.contains(OUTER_MODAL_CLASS)) {
            this.toggleModal();
        }
    }

    handleSave() {
        if (this.modalSaveHandler) {
            this.modalSaveHandler();
        }
        this.toggleModal();
    }

    disconnectedCallback() {
        window.removeEventListener('keyup', this._handleKeyUp);
    }
}
```

```html
<!-- composableModal.html -->
<template>
    <!-- Backdrop -->
    <div class={backdropClass}></div>

    <!-- Modal -->
    <div class={modalClass}
         role="dialog"
         aria-modal="true"
         aria-hidden={modalAriaHidden}
         aria-labelledby="modal-heading">

        <div class="slds-modal__container outerModalContent"
             onclick={handleBackdropClick}>

            <div class="slds-modal__content slds-p-around_medium">
                <!-- Header -->
                <template lwc:if={modalHeader}>
                    <h2 id="modal-heading" class="slds-text-heading_medium">
                        {modalHeader}
                    </h2>
                </template>
                <template lwc:if={modalTagline}>
                    <p class="slds-m-top_x-small slds-text-color_weak">
                        {modalTagline}
                    </p>
                </template>

                <!-- Slotted Content -->
                <div class="slds-m-top_medium">
                    <slot name="modalContent"></slot>
                </div>

                <!-- Footer -->
                <div class="slds-m-top_medium slds-text-align_right">
                    <lightning-button
                        label="Cancel"
                        onclick={toggleModal}
                        class="slds-m-right_x-small focusable">
                    </lightning-button>
                    <lightning-button
                        variant="brand"
                        label="Save"
                        onclick={handleSave}
                        class="focusable">
                    </lightning-button>
                </div>
            </div>
        </div>
    </div>

    <!-- Hidden background content -->
    <div aria-hidden={_isOpen}>
        <slot name="body"></slot>
    </div>
</template>
```

---

## Record Picker Pattern

```javascript
// recordPicker.js
import { LightningElement, api } from 'lwc';

export default class RecordPicker extends LightningElement {
    @api label = 'Select Record';
    @api objectApiName = 'Account';
    @api placeholder = 'Search...';
    @api required = false;
    @api multiSelect = false;

    _selectedIds = [];

    @api
    get value() {
        return this.multiSelect ? this._selectedIds : this._selectedIds[0];
    }

    set value(val) {
        this._selectedIds = Array.isArray(val) ? val : val ? [val] : [];
    }

    handleChange(event) {
        const recordId = event.detail.recordId;
        if (this.multiSelect) {
            if (!this._selectedIds.includes(recordId)) {
                this._selectedIds = [...this._selectedIds, recordId];
            }
        } else {
            this._selectedIds = recordId ? [recordId] : [];
        }

        this.dispatchEvent(new CustomEvent('select', {
            detail: {
                recordId: this.value,
                recordIds: this._selectedIds
            }
        }));
    }

    handleRemove(event) {
        const idToRemove = event.target.dataset.id;
        this._selectedIds = this._selectedIds.filter(id => id !== idToRemove);
        this.dispatchEvent(new CustomEvent('select', {
            detail: { recordIds: this._selectedIds }
        }));
    }
}
```

```html
<!-- recordPicker.html -->
<template>
    <lightning-record-picker
        label={label}
        placeholder={placeholder}
        object-api-name={objectApiName}
        onchange={handleChange}
        required={required}>
    </lightning-record-picker>

    <template lwc:if={multiSelect}>
        <div class="slds-m-top_x-small">
            <template for:each={_selectedIds} for:item="id">
                <lightning-pill
                    key={id}
                    label={id}
                    data-id={id}
                    onremove={handleRemove}>
                </lightning-pill>
            </template>
        </div>
    </template>
</template>
```

---

## Workspace API Pattern

```javascript
// workspaceTabManager.js
import { LightningElement, wire } from 'lwc';
import { IsConsoleNavigation, getFocusedTabInfo, openTab, closeTab,
         setTabLabel, setTabIcon, refreshTab } from 'lightning/platformWorkspaceApi';

export default class WorkspaceTabManager extends LightningElement {
    @wire(IsConsoleNavigation) isConsole;

    async openRecordTab(recordId, objectApiName) {
        if (!this.isConsole) return;

        await openTab({
            recordId,
            focus: true,
            icon: `standard:${objectApiName.toLowerCase()}`,
            label: 'Loading...'
        });
    }

    async openSubtab(parentTabId, recordId) {
        if (!this.isConsole) return;

        await openTab({
            parentTabId,
            recordId,
            focus: true
        });
    }

    async getCurrentTabInfo() {
        if (!this.isConsole) return null;
        return await getFocusedTabInfo();
    }

    async updateTabLabel(tabId, label) {
        if (!this.isConsole) return;
        await setTabLabel(tabId, label);
    }

    async updateTabIcon(tabId, iconName) {
        if (!this.isConsole) return;
        await setTabIcon(tabId, iconName);
    }

    async refreshCurrentTab() {
        if (!this.isConsole) return;
        const tabInfo = await getFocusedTabInfo();
        await refreshTab(tabInfo.tabId);
    }

    async closeCurrentTab() {
        if (!this.isConsole) return;
        const tabInfo = await getFocusedTabInfo();
        await closeTab(tabInfo.tabId);
    }
}
```

---

## Parent-Child Communication

```javascript
// parent.js
import { LightningElement } from 'lwc';

export default class Parent extends LightningElement {
    selectedAccountId;

    handleAccountSelected(event) {
        this.selectedAccountId = event.detail.accountId;
    }
}
```

```html
<!-- parent.html -->
<template>
    <c-account-list onaccountselected={handleAccountSelected}></c-account-list>
    <template lwc:if={selectedAccountId}>
        <c-account-detail account-id={selectedAccountId}></c-account-detail>
    </template>
</template>
```

```javascript
// child.js (accountList)
import { LightningElement } from 'lwc';

export default class AccountList extends LightningElement {
    handleRowAction(event) {
        const accountId = event.detail.row.Id;

        // Dispatch event to parent
        this.dispatchEvent(new CustomEvent('accountselected', {
            detail: { accountId },
            bubbles: true,
            composed: false // Don't cross shadow DOM boundaries
        }));
    }
}
```

---

## Sibling Communication (via Parent)

When two child components need to communicate but share the same parent, use the **parent as middleware**. This is the recommended pattern for master-detail UIs.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SIBLING COMMUNICATION FLOW                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                         ┌──────────┐                                │
│                         │  Parent  │  ← Manages state               │
│                         └────┬─────┘                                │
│                    ┌─────────┴─────────┐                            │
│                    │                   │                            │
│              CustomEvent          @api property                     │
│                (up)                 (down)                          │
│                    │                   │                            │
│              ┌─────┴─────┐       ┌─────┴─────┐                      │
│              │  Child A  │       │  Child B  │                      │
│              │  (List)   │       │  (Detail) │                      │
│              └───────────┘       └───────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**The flow**:
1. **Child A** dispatches a custom event (e.g., user selects an account)
2. **Parent** catches the event and updates its state
3. **Parent** passes data to **Child B** via `@api` property

### Complete Example: Account List → Account Detail

```javascript
// accountContainer.js - Parent orchestrates communication between siblings
import { LightningElement } from 'lwc';

export default class AccountContainer extends LightningElement {
    // State managed at parent level
    selectedAccountId;
    selectedAccountName;

    // Child A (accountList) fires this event
    handleAccountSelect(event) {
        this.selectedAccountId = event.detail.accountId;
        this.selectedAccountName = event.detail.accountName;
    }

    // Clear selection (triggered by Child B)
    handleClearSelection() {
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
