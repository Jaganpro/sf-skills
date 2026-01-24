---
name: sf-lwc
description: >
  Lightning Web Components development skill with PICKLES architecture methodology,
  component scaffolding, wire service patterns, event handling, Apex integration,
  GraphQL support, and Jest test generation. Build modern Salesforce UIs with
  proper reactivity, accessibility, dark mode compatibility, and performance patterns.
license: MIT
metadata:
  version: "2.1.0"
  author: "Jag Valaiyapathy"
  scoring: "165 points across 8 categories (SLDS 2 + Dark Mode compliant)"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/post-tool-validate.py"
          timeout: 120000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-lwc"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-lwc"
      timeout: 5000
---

# sf-lwc: Lightning Web Components Development

Expert frontend engineer specializing in Lightning Web Components for Salesforce. Generate production-ready LWC components using the **PICKLES Framework** for architecture, with proper data binding, Apex/GraphQL integration, event handling, SLDS 2 styling, and comprehensive Jest tests.

## Core Responsibilities

1. **Component Scaffolding**: Generate complete LWC bundles (JS, HTML, CSS, meta.xml)
2. **PICKLES Architecture**: Apply structured design methodology for robust components
3. **Wire Service Patterns**: Implement @wire decorators for data fetching (Apex & GraphQL)
4. **Apex/GraphQL Integration**: Connect LWC to backend with @AuraEnabled and GraphQL
5. **Event Handling**: Component communication (CustomEvent, LMS, pubsub)
6. **Lifecycle Management**: Proper use of connectedCallback, renderedCallback, etc.
7. **Jest Testing**: Generate comprehensive unit tests with advanced patterns
8. **Accessibility**: WCAG compliance with ARIA attributes, focus management
9. **Dark Mode**: SLDS 2 compliant styling with global styling hooks
10. **Performance**: Lazy loading, virtual scrolling, debouncing, efficient rendering

---

## PICKLES Framework (Architecture Methodology)

The **PICKLES Framework** provides a structured approach to designing robust Lightning Web Components. Apply each principle during component design and implementation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     🥒 PICKLES FRAMEWORK                            │
├─────────────────────────────────────────────────────────────────────┤
│  P → Prototype    │  Validate ideas with wireframes & mock data    │
│  I → Integrate    │  Choose data source (LDS, Apex, GraphQL, API)  │
│  C → Composition  │  Structure component hierarchy & communication │
│  K → Kinetics     │  Handle user interactions & event flow         │
│  L → Libraries    │  Leverage platform APIs & base components      │
│  E → Execution    │  Optimize performance & lifecycle hooks        │
│  S → Security     │  Enforce permissions, FLS, and data protection │
└─────────────────────────────────────────────────────────────────────┘
```

### Quick Reference

| Principle | Key Actions |
|-----------|-------------|
| **P - Prototype** | Wireframes, mock data, stakeholder review, separation of concerns |
| **I - Integrate** | LDS for single records, Apex for complex queries, GraphQL for related data |
| **C - Composition** | `@api` for parent→child, CustomEvent for child→parent, LMS for cross-DOM |
| **K - Kinetics** | Debounce search (300ms), disable during submit, keyboard navigation |
| **L - Libraries** | Use `lightning/*` modules, base components, avoid reinventing |
| **E - Execution** | Lazy load with `lwc:if`, cache computed values, avoid infinite loops |
| **S - Security** | `WITH SECURITY_ENFORCED`, input validation, FLS/CRUD checks |

**For detailed PICKLES implementation patterns, see [resources/component-patterns.md](resources/component-patterns.md)**

---

## Key Component Patterns

### Wire vs Imperative Apex Calls

| Aspect | Wire (@wire) | Imperative Calls |
|--------|--------------|------------------|
| **Execution** | Automatic / Reactive | Manual / Programmatic |
| **DML** | ❌ Read-Only | ✅ Insert/Update/Delete |
| **Data Updates** | ✅ Auto on param change | ❌ Manual refresh |
| **Control** | Low (framework decides) | Full (you decide) |
| **Caching** | ✅ Built-in | ❌ None |

**Quick Decision**: Use `@wire` for read-only display with auto-refresh. Use imperative for user actions, DML, or when you need control over timing.

**For complete comparison with code examples and decision tree, see [resources/component-patterns.md](resources/component-patterns.md#wire-vs-imperative-apex-calls)**

### Data Source Decision Tree

| Scenario | Recommended Approach |
|----------|---------------------|
| Single record by ID | Lightning Data Service (`getRecord`) |
| Simple record CRUD | `lightning-record-form` / `lightning-record-edit-form` |
| Complex queries | Apex with `@AuraEnabled(cacheable=true)` |
| Related records | GraphQL wire adapter |
| Real-time updates | Platform Events / Streaming API |
| External data | Named Credentials + Apex callout |

### Communication Patterns

| Pattern | Direction | Use Case |
|---------|-----------|----------|
| `@api` properties | Parent → Child | Pass data down |
| Custom Events | Child → Parent | Bubble actions up |
| Lightning Message Service | Any → Any | Cross-DOM communication |
| Pub/Sub | Sibling → Sibling | Same page, no hierarchy |

### Communication Pattern Quick Reference

```
┌─────────────────────────────────────────────────────────────────────┐
│              LWC COMMUNICATION - MADE SIMPLE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Parent → Child     │  [Parent] ─────→ [Child]   │  @api properties │
│                                                                     │
│  Child → Parent     │  [Child] ─────→ [Parent]   │  Custom Events   │
│                                                                     │
│  Sibling Components │  [A] → [Parent] → [B]      │  Events + @api   │
│                                                                     │
│  Unrelated          │  [Comp 1] ←─LMS─→ [Comp 2] │  Message Service │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Decision Tree**:
- Same parent? → Use parent as middleware (events up, `@api` down)
- Different DOM trees? → Use Lightning Message Service
- LWC ↔ Aura/VF? → Use Lightning Message Service

**For complete sibling communication code example, see [resources/component-patterns.md](resources/component-patterns.md#sibling-communication-via-parent)**

### Lifecycle Hook Guidance

| Hook | When to Use | Avoid |
|------|-------------|-------|
| `constructor()` | Initialize properties | DOM access (not ready) |
| `connectedCallback()` | Subscribe to events, fetch data | Heavy processing |
| `renderedCallback()` | DOM-dependent logic | Infinite loops, property changes |
| `disconnectedCallback()` | Cleanup subscriptions/listeners | Async operations |

**For complete code examples (Wire Service, GraphQL, Modal, Navigation, TypeScript), see:**
- [resources/component-patterns.md](resources/component-patterns.md) - Comprehensive patterns with full source code
- [resources/lms-guide.md](resources/lms-guide.md) - Lightning Message Service deep dive

---

## SLDS 2 Validation (165-Point Scoring)

The sf-lwc skill includes automated SLDS 2 validation that ensures dark mode compatibility, accessibility, and modern styling.

| Category | Points | Key Checks |
|----------|--------|------------|
| **SLDS Class Usage** | 25 | Valid class names, proper `slds-*` utilities |
| **Accessibility** | 25 | ARIA labels, roles, alt-text, keyboard navigation |
| **Dark Mode Readiness** | 25 | No hardcoded colors, CSS variables only |
| **SLDS Migration** | 20 | No deprecated SLDS 1 patterns/tokens |
| **Styling Hooks** | 20 | Proper `--slds-g-*` variable usage |
| **Component Structure** | 15 | Uses `lightning-*` base components |
| **Performance** | 10 | Efficient selectors, no `!important` |
| **PICKLES Compliance** | 25 | Architecture methodology adherence (optional) |

**Scoring Thresholds**:
```
⭐⭐⭐⭐⭐ 150-165 pts → Production-ready, full SLDS 2 + Dark Mode
⭐⭐⭐⭐   125-149 pts → Good component, minor styling issues
⭐⭐⭐     100-124 pts → Functional, needs SLDS cleanup
⭐⭐       75-99 pts  → Basic functionality, SLDS issues
⭐         <75 pts   → Needs significant work
```

---

## Dark Mode Readiness

Dark mode is exclusive to SLDS 2 themes. Components must use global styling hooks to support light/dark theme switching.

### Dark Mode Checklist

- [ ] **No hardcoded hex colors** (`#FFFFFF`, `#333333`)
- [ ] **No hardcoded RGB/RGBA values**
- [ ] **All colors use CSS variables** (`var(--slds-g-color-*)`)
- [ ] **Fallback values provided** for SLDS 1 compatibility
- [ ] **No inline color styles** in HTML templates
- [ ] **Icons use SLDS utility icons** (auto-adjust for dark mode)

### Global Styling Hooks (Common)

| Category | SLDS 2 Variable | Purpose |
|----------|-----------------|---------|
| **Surface** | `--slds-g-color-surface-1` to `-4` | Background colors |
| **Container** | `--slds-g-color-surface-container-1` to `-3` | Card/section backgrounds |
| **Text** | `--slds-g-color-on-surface` | Primary text |
| **Border** | `--slds-g-color-border-1`, `-2` | Borders |
| **Brand** | `--slds-g-color-brand-1`, `-2` | Brand accent |
| **Spacing** | `--slds-g-spacing-0` to `-12` | Margins/padding |

**Example Migration**:
```css
/* SLDS 1 (Deprecated) */
.my-card { background-color: #ffffff; color: #333333; }

/* SLDS 2 (Dark Mode Ready) */
.my-card {
    background-color: var(--slds-g-color-surface-container-1, #ffffff);
    color: var(--slds-g-color-on-surface, #181818);
}
```

**For complete styling hooks reference and migration guide, see [resources/performance-guide.md](resources/performance-guide.md)**

---

## Jest Testing

Advanced testing patterns ensure robust, maintainable components.

### Essential Patterns

```javascript
// Render cycle helper
const runRenderingLifecycle = async (reasons = ['render']) => {
    while (reasons.length > 0) {
        await Promise.resolve(reasons.pop());
    }
};

// DOM cleanup
afterEach(() => {
    while (document.body.firstChild) {
        document.body.removeChild(document.body.firstChild);
    }
    jest.clearAllMocks();
});

// Proxy unboxing (LWS compatibility)
const unboxedData = JSON.parse(JSON.stringify(component.data));
expect(unboxedData).toEqual(expectedData);
```

### Test Template Structure

```javascript
import { createElement } from 'lwc';
import MyComponent from 'c/myComponent';
import getData from '@salesforce/apex/MyController.getData';

jest.mock('@salesforce/apex/MyController.getData', () => ({
    default: jest.fn()
}), { virtual: true });

describe('c-my-component', () => {
    afterEach(() => { /* DOM cleanup */ });

    it('displays data when loaded successfully', async () => {
        getData.mockResolvedValue(MOCK_DATA);
        const element = createElement('c-my-component', { is: MyComponent });
        document.body.appendChild(element);
        await runRenderingLifecycle();
        // Assertions...
    });
});
```

**For complete testing patterns (ResizeObserver polyfill, advanced mocks, event testing), see [resources/jest-testing.md](resources/jest-testing.md)**

---

## Accessibility

WCAG compliance is mandatory for all components.

### Quick Checklist

| Requirement | Implementation |
|-------------|----------------|
| **Labels** | `label` on inputs, `aria-label` on icons |
| **Keyboard** | Enter/Space triggers, Tab navigation |
| **Focus** | Visible indicator, logical order, focus traps in modals |
| **Live Regions** | `aria-live="polite"` for dynamic content |
| **Contrast** | 4.5:1 minimum for text |

```html
<!-- Accessible dynamic content -->
<div aria-live="polite" class="slds-assistive-text">
    {statusMessage}
</div>
```

**For comprehensive accessibility guide (focus management, ARIA patterns, screen reader testing), see [resources/accessibility-guide.md](resources/accessibility-guide.md)**

---

## Metadata Configuration

### meta.xml Targets

```xml
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>66.0</apiVersion>
    <isExposed>true</isExposed>
    <masterLabel>Account Dashboard</masterLabel>
    <description>SLDS 2 compliant account dashboard with dark mode support</description>
    <targets>
        <target>lightning__RecordPage</target>
        <target>lightning__AppPage</target>
        <target>lightning__HomePage</target>
        <target>lightning__FlowScreen</target>
        <target>lightningCommunity__Page</target>
        <target>lightning__Dashboard</target> <!-- Spring '26 Beta -->
    </targets>
    <targetConfigs>
        <targetConfig targets="lightning__RecordPage">
            <objects>
                <object>Account</object>
            </objects>
            <property name="title" type="String" default="Dashboard"/>
            <property name="maxRecords" type="Integer" default="10"/>
        </targetConfig>
    </targetConfigs>
</LightningComponentBundle>
```

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| `sf lightning generate component --type lwc` | Create new LWC |
| `sf lightning lwc test run` | Run Jest tests |
| `sf lightning lwc test run --watch` | Watch mode |
| `sf project deploy start -m LightningComponentBundle` | Deploy LWC |

### Generate New Component

```bash
sf lightning generate component \
  --name accountDashboard \
  --type lwc \
  --output-dir force-app/main/default/lwc
```

### Run Tests

```bash
# All tests
sf lightning lwc test run

# Specific component
sf lightning lwc test run --spec force-app/main/default/lwc/accountList/__tests__

# With coverage
sf lightning lwc test run -- --coverage
```

---

## Flow Screen Integration

LWC components can be embedded in Flow Screens for custom UI experiences within guided processes.

### Key Concepts

| Mechanism | Direction | Purpose |
|-----------|-----------|---------|
| `@api` with `role="inputOnly"` | Flow → LWC | Pass context data |
| `FlowAttributeChangeEvent` | LWC → Flow | Return user selections |
| `FlowNavigationFinishEvent` | LWC → Flow | Programmatic Next/Back/Finish |
| `availableActions` | Flow → LWC | Check available navigation |

### Quick Example

```javascript
import { FlowAttributeChangeEvent, FlowNavigationFinishEvent } from 'lightning/flowSupport';

@api recordId;           // Input from Flow
@api selectedRecordId;   // Output to Flow
@api availableActions = [];

handleSelect(event) {
    this.selectedRecordId = event.detail.id;
    // CRITICAL: Notify Flow of the change
    this.dispatchEvent(new FlowAttributeChangeEvent(
        'selectedRecordId',
        this.selectedRecordId
    ));
}

handleNext() {
    if (this.availableActions.includes('NEXT')) {
        this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
    }
}
```

**For complete Flow integration patterns, see:**
- [docs/flow-integration-guide.md](docs/flow-integration-guide.md)
- [docs/triangle-pattern.md](docs/triangle-pattern.md)

---

## Advanced Features

### TypeScript Support (Spring '26 - GA in API 66.0)

Lightning Web Components now support TypeScript with the `@salesforce/lightning-types` package.

```typescript
interface AccountRecord {
    Id: string;
    Name: string;
    Industry?: string;
}

export default class AccountList extends LightningElement {
    @api recordId: string | undefined;
    @track private _accounts: AccountRecord[] = [];

    @wire(getAccounts, { maxRecords: '$maxRecords' })
    wiredAccounts(result: WireResult<AccountRecord[]>): void {
        // Typed wire handling...
    }
}
```

**Requirements**: TypeScript 5.4.5+, `@salesforce/lightning-types` package

### LWC in Dashboards (Beta - Spring '26)

Components can be embedded as custom dashboard widgets.

```xml
<targets>
    <target>lightning__Dashboard</target>
</targets>
<targetConfigs>
    <targetConfig targets="lightning__Dashboard">
        <property name="metricType" type="String" label="Metric Type"/>
        <property name="refreshInterval" type="Integer" default="30"/>
    </targetConfig>
</targetConfigs>
```

**Note**: Requires enablement via Salesforce Customer Support

### Agentforce Discoverability (Spring '26 - GA in API 66.0)

Make components discoverable by Agentforce agents:

```xml
<capabilities>
    <capability>lightning__agentforce</capability>
</capabilities>
```

**Best Practices**:
- Clear `masterLabel` and `description`
- Detailed property descriptions
- Semantic naming conventions

**For TypeScript patterns and advanced configurations, see [resources/component-patterns.md](resources/component-patterns.md)**

---

## Cross-Skill Integration

| Skill | Use Case |
|-------|----------|
| sf-apex | Generate Apex controllers (`@AuraEnabled`, `@InvocableMethod`) |
| sf-flow | Embed components in Flow Screens, pass data to/from Flow |
| sf-testing | Generate Jest tests |
| sf-deploy | Deploy components |
| sf-metadata | Create message channels |

---

## Dependencies

**Required**:
- Target org with LWC support (API 45.0+)
- `sf` CLI authenticated

**For Testing**:
- Node.js 18+
- Jest (`@salesforce/sfdx-lwc-jest`)

**For SLDS Validation**:
- `@salesforce-ux/slds-linter` (optional)

Install: `/plugin install github:Jaganpro/sf-skills/sf-lwc`

---

## Additional Resources

### Documentation Files

| Resource | Purpose |
|----------|---------|
| [resources/component-patterns.md](resources/component-patterns.md) | Complete code examples (Wire, GraphQL, Modal, Navigation, TypeScript) |
| [resources/lms-guide.md](resources/lms-guide.md) | Lightning Message Service deep dive |
| [resources/jest-testing.md](resources/jest-testing.md) | Advanced testing patterns (James Simone) |
| [resources/accessibility-guide.md](resources/accessibility-guide.md) | WCAG compliance, ARIA patterns, focus management |
| [resources/performance-guide.md](resources/performance-guide.md) | Dark mode migration, lazy loading, optimization |
| [docs/state-management.md](docs/state-management.md) | **NEW**: @track, Singleton Store, @lwc/state, Platform State Managers |
| [docs/template-anti-patterns.md](docs/template-anti-patterns.md) | **NEW**: LLM template mistakes (inline expressions, ternary operators) |
| [docs/async-notification-patterns.md](docs/async-notification-patterns.md) | **NEW**: Platform Events + empApi subscription patterns |
| [docs/flow-integration-guide.md](docs/flow-integration-guide.md) | Flow-LWC communication, apex:// type bindings |

### External References

- [PICKLES Framework (Salesforce Ben)](https://www.salesforceben.com/the-ideal-framework-for-architecting-salesforce-lightning-web-components/)
- [LWC Recipes (GitHub)](https://github.com/trailheadapps/lwc-recipes)
- [SLDS 2 Transition Guide](https://www.lightningdesignsystem.com/2e1ef8501/p/8184ad-transition-to-slds-2)
- [SLDS Styling Hooks](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-custom-properties.html)
- [James Simone - Composable Modal](https://www.jamessimone.net/blog/joys-of-apex/lwc-composable-modal/)
- [James Simone - Advanced Jest Testing](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/)

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
