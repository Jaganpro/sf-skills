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

## Document Map

| Need | Document | Description |
|------|----------|-------------|
| **Component patterns** | [references/component-patterns.md](references/component-patterns.md) | Wire, GraphQL, Modal, Navigation, TypeScript |
| **LMS guide** | [references/lms-guide.md](references/lms-guide.md) | Lightning Message Service deep dive |
| **Jest testing** | [references/jest-testing.md](references/jest-testing.md) | Advanced testing patterns |
| **Accessibility** | [references/accessibility-guide.md](references/accessibility-guide.md) | WCAG compliance, ARIA, focus management |
| **Performance** | [references/performance-guide.md](references/performance-guide.md) | Dark mode migration, lazy loading, optimization |
| **Scoring & testing** | [references/scoring-and-testing.md](references/scoring-and-testing.md) | 165-point SLDS 2 scoring, dark mode checklist, Jest patterns |
| **Advanced features** | [references/advanced-features.md](references/advanced-features.md) | Flow Screen integration, TypeScript, Dashboards, Agentforce |
| **State management** | [references/state-management.md](references/state-management.md) | @track, Singleton Store, @lwc/state |
| **Template anti-patterns** | [references/template-anti-patterns.md](references/template-anti-patterns.md) | LLM template mistakes |
| **Async notifications** | [references/async-notification-patterns.md](references/async-notification-patterns.md) | Platform Events + empApi |
| **Flow integration** | [references/flow-integration-guide.md](references/flow-integration-guide.md) | Flow-LWC communication |

---

## PICKLES Framework (Architecture Methodology)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PICKLES FRAMEWORK                                │
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

| Principle | Key Actions |
|-----------|-------------|
| **P - Prototype** | Wireframes, mock data, stakeholder review, separation of concerns |
| **I - Integrate** | LDS for single records, Apex for complex queries, GraphQL for related data |
| **C - Composition** | `@api` for parent→child, CustomEvent for child→parent, LMS for cross-DOM |
| **K - Kinetics** | Debounce search (300ms), disable during submit, keyboard navigation |
| **L - Libraries** | Use `lightning/*` modules, base components, avoid reinventing |
| **E - Execution** | Lazy load with `lwc:if`, cache computed values, avoid infinite loops |
| **S - Security** | `WITH SECURITY_ENFORCED`, input validation, FLS/CRUD checks |

**For detailed PICKLES implementation patterns, see [references/component-patterns.md](references/component-patterns.md)**

---

## Key Component Patterns

### Wire vs Imperative Apex Calls

| Aspect | Wire (@wire) | Imperative Calls |
|--------|--------------|------------------|
| **Execution** | Automatic / Reactive | Manual / Programmatic |
| **DML** | Read-Only | Insert/Update/Delete |
| **Data Updates** | Auto on param change | Manual refresh |
| **Caching** | Built-in | None |

**Quick Decision**: Use `@wire` for read-only display with auto-refresh. Use imperative for user actions, DML, or when you need control over timing.

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

**Decision Tree**: Same parent? → Events up, `@api` down. Different DOM trees? → LMS. LWC ↔ Aura/VF? → LMS.

### Lifecycle Hook Guidance

| Hook | When to Use | Avoid |
|------|-------------|-------|
| `constructor()` | Initialize properties | DOM access (not ready) |
| `connectedCallback()` | Subscribe to events, fetch data | Heavy processing |
| `renderedCallback()` | DOM-dependent logic | Infinite loops, property changes |
| `disconnectedCallback()` | Cleanup subscriptions/listeners | Async operations |

---

## SLDS 2 Validation & Dark Mode

> See [references/scoring-and-testing.md](references/scoring-and-testing.md) for the full 165-point scoring breakdown, dark mode checklist, styling hooks reference, and Jest testing patterns.

**Quick summary**: 8 categories, 165 total points. 150+ Production-ready | 125+ Good | 100+ Functional | <75 Needs work. Dark mode requires CSS variables only (`--slds-g-color-*`), no hardcoded colors.

---

## Accessibility

WCAG compliance is mandatory for all components.

| Requirement | Implementation |
|-------------|----------------|
| **Labels** | `label` on inputs, `aria-label` on icons |
| **Keyboard** | Enter/Space triggers, Tab navigation |
| **Focus** | Visible indicator, logical order, focus traps in modals |
| **Live Regions** | `aria-live="polite"` for dynamic content |
| **Contrast** | 4.5:1 minimum for text |

**For comprehensive guide, see [references/accessibility-guide.md](references/accessibility-guide.md)**

---

## Metadata Configuration

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
        <target>lightning__Dashboard</target>
    </targets>
    <targetConfigs>
        <targetConfig targets="lightning__RecordPage">
            <objects><object>Account</object></objects>
            <property name="title" type="String" default="Dashboard"/>
            <property name="maxRecords" type="Integer" default="10"/>
        </targetConfig>
    </targetConfigs>
</LightningComponentBundle>
```

---

## Flow Screen & Advanced Features

> See [references/advanced-features.md](references/advanced-features.md) for Flow Screen integration (FlowAttributeChangeEvent, FlowNavigationFinishEvent), TypeScript support (API 66.0 GA), LWC in Dashboards (Beta), and Agentforce discoverability.

**Flow Screen quick reference**: `@api` inputs → `FlowAttributeChangeEvent` outputs → `FlowNavigationFinishEvent` for navigation. See also [references/flow-integration-guide.md](references/flow-integration-guide.md).

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| `sf lightning generate component --type lwc` | Create new LWC |
| `sf lightning lwc test run` | Run Jest tests |
| `sf lightning lwc test run --watch` | Watch mode |
| `sf project deploy start -m LightningComponentBundle` | Deploy LWC |

```bash
# Generate new component
sf lightning generate component \
  --name accountDashboard \
  --type lwc \
  --output-dir force-app/main/default/lwc

# Run tests with coverage
sf lightning lwc test run -- --coverage

# Specific component tests
sf lightning lwc test run --spec force-app/main/default/lwc/accountList/__tests__
```

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

**Required**: Target org with LWC support (API 45.0+), `sf` CLI authenticated
**For Testing**: Node.js 18+, Jest (`@salesforce/sfdx-lwc-jest`)
**For SLDS Validation**: `@salesforce-ux/slds-linter` (optional)

---

## External References

- [PICKLES Framework (Salesforce Ben)](https://www.salesforceben.com/the-ideal-framework-for-architecting-salesforce-lightning-web-components/)
- [LWC Recipes (GitHub)](https://github.com/trailheadapps/lwc-recipes)
- [SLDS 2 Transition Guide](https://www.lightningdesignsystem.com/2e1ef8501/p/8184ad-transition-to-slds-2)
- [James Simone - Advanced Jest Testing](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/)
