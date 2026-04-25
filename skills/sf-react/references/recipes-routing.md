# Recipe Routing — trailheadapps/multiframework-recipes

44 recipes across 8 categories. Source: https://github.com/trailheadapps/multiframework-recipes

Use this as the lookup table when an agent needs to ground a Multi-Framework task in an official pattern.

## Hello (8) — Platform-grounded React basics

| Recipe | Use when |
|---|---|
| `HelloWorld` | Need the simplest possible Multi-Framework component as a starting point |
| `BindingAccountName` | First introduction to fetching and binding data with the `{ value }` shape |
| `ConditionalStatus` | Conditional render on a picklist value |
| `ListOfAccounts` | List rendering with the Relay `edges → node` pattern |
| `LifecycleFetch` | `useEffect` lifecycle plus async fetch |
| `ParentToChild` | Props passing parent → child |
| `ChildToParent` | Event handlers child → parent |
| `StateManagement` | Local `useState` (no persistence) |

## Read Data (8) — GraphQL queries against UIAPI

| Recipe | Use when |
|---|---|
| `SingleRecord` | Basic single-record query, field access via `{ value }` |
| `ListOfRecords` | Multiple records, basic pagination |
| `FilteredList` | `where` clause filtering |
| `SortedResults` | `orderBy` sorting |
| `PaginatedList` | Relay cursors and `pageInfo` |
| `RelatedRecords` | Parent-lookup `__r` traversal |
| `ImperativeRefetch` | Refetch button, query re-run on demand |
| `AliasedMultiObjectQuery` | Aliases for multi-object queries in one request |

## Modify Data (5) — GraphQL mutations

| Recipe | Use when |
|---|---|
| `CreateRecord` | New record creation, `RecordCreateInput` shape |
| `UpdateRecord` | Patch + manual local state update (no auto cache invalidation in React) |
| `DeleteRecord` | Delete with confirmation pattern |
| `QueryMutationTogether` | Load record then mutate it |
| `ServerErrorHandling` | `result.errors[]` vs throw |

## Salesforce APIs (4) — Non-GraphQL platform APIs

| Recipe | Use when |
|---|---|
| `DisplayCurrentUser` | Session context, current user info |
| `UiApiRest` | REST UIAPI calls to `/services/data/v66.0/ui-api/records` |
| `ApexRest` | Custom `@RestResource` callout |
| `ConnectApi` | Social / Chatter Connect API |

## Error Handling (3)

| Recipe | Use when |
|---|---|
| `GraphqlErrors` | `result.errors[]` detection and surfacing |
| `LoadingErrorEmpty` | Render-state machine: loading, error, empty |
| `ErrorBoundaryRecipe` | React error boundary wrapping a feature |

## Routing (5) — React Router 7 (note: `react-router`, not `react-router-dom`)

| Recipe | Use when |
|---|---|
| `LinkDemo` | Basic `Link` component |
| `NavLinkDemo` | `NavLink` active state |
| `RouteParameters` | URL params via `useParams` |
| `UseNavigate` | Programmatic navigation |
| `NestedRoutes` | Nested route structure |

## Styling (9) — Three systems side-by-side

Three pairs of recipes, one per styling system, applied to the same UI element. The point is to demonstrate the choice — never mix two systems in a single component.

| Recipe | System | Use when |
|---|---|---|
| `ButtonSLDS` / `AccountCardSLDS` / `IconsSLDS` | SLDS CSS classes on JSX | Maximum platform consistency |
| `ButtonShadcn` / `AccountCardShadcn` / `IconsLucide` | shadcn/ui + Lucide | Modern component library, more flexibility |
| `ButtonDSR` / `AccountCardDSR` / `IconsDSR` | `design-system-react` | Drop-in React components matching SLDS |

## Integration (2) — Combined patterns

| Recipe | Use when |
|---|---|
| `SearchableAccountList` | Query + filter + list + state in one screen |
| `DashboardAliasedQueries` | Multi-object query with aliased results, dashboard layout |

## Cross-cutting reminders

- Every recipe inlines its GraphQL query/mutation (the recipes repo's `AGENT.md` forbids extracting them to `src/api/`).
- Pick exactly one styling system per component.
- After any mutation, manually patch local state (no `updateRecord()`-style auto-notify in React).
- All UIAPI scalar fields are wrapped in `{ value }`. List fields use Relay `edges → node`.
