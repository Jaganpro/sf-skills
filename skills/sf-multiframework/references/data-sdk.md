# Data SDK (`@salesforce/sdk-data`)

The Data SDK is the **only** sanctioned way to call Salesforce APIs from a React UI bundle. It abstracts authentication, CSRF token management, and base-path resolution across surfaces (Lightning Experience, Experience Cloud sites, the local Vite dev server).

> Never call `fetch()` or `axios` directly to a Salesforce endpoint from a React UI bundle.

## Why use it

| Feature | Benefit |
|---|---|
| **Surface abstraction** | Same code works in App Launcher, Experience Cloud, and `localhost` dev |
| **Capability detection** | The SDK detects the runtime and picks the right transport |
| **TypeScript-first** | Full IntelliSense, compile-time safety, Promise-based error flow |
| **Auth + CSRF** | Handled internally — you don't manage tokens |

## Public API surface

| Export | Type | Purpose |
|---|---|---|
| `createDataSDK` | async function | Factory that returns a `DataSDK` instance |
| `gql` | template tag | Identity tag for inline GraphQL queries; enables editor highlighting and codegen detection |
| `DataSDK` | interface | The SDK surface (`graphql`, `fetch`) |
| `SDKOptions` | interface | Optional surface override |
| `NodeOfConnection<T>` | utility type | Extracts node type from `{ edges { node ... } }` connection responses |

## `createDataSDK(options?)`

```ts
import { createDataSDK } from "@salesforce/sdk-data";

const sdk = await createDataSDK({
  surface: "webapp",
  webapp: {
    basePath: "/my-experience-site",
    on401: () => signInAgain(),
    on403: () => showPermissionsHelp()
  }
});
```

Options shape:

```ts
type DataSDKOptions = {
  surface?: string;                          // for explicit surface detection
  webapp?: {
    basePath?: string;                       // URL prefix for SF API calls
    on401?: () => Promise<unknown> | void;   // optional 401 hook
    on403?: () => Promise<unknown> | void;   // optional 403 hook
  };
};
```

The 401/403 callbacks are essential for **Experience Cloud** apps where users may need to sign in again or be guided to permission setup.

## `sdk.graphql?.()`

```ts
const res = await sdk.graphql?.(QUERY, variables);
```

Use **optional chaining** (`?.()`) — `graphql` is not guaranteed in every surface.

GraphQL is the **preferred** path for record reads and writes.

### Defining queries

#### Inline with `gql` (simple)

```ts
import { createDataSDK, gql } from "@salesforce/sdk-data";

const QUERY = gql`
  query SingleAccount {
    uiapi {
      query {
        Account(first: 1) {
          edges {
            node {
              Id
              Name { value }
              Industry { value }
            }
          }
        }
      }
    }
  }
`;
```

The `gql` tag is an identity template literal. It triggers:

- editor syntax highlighting (with Agentforce Vibes / GraphQL extensions)
- codegen detection
- runtime type-tagged operation registration

#### External `.graphql` file (complex / shared)

```
src/api/utils/query/singleAccountQuery.graphql
src/api/graphql-operations-types.ts          # generated
```

```ts
import QUERY from "./query/singleAccountQuery.graphql?raw";
import type { SingleAccountQuery, SingleAccountQueryVariables }
  from "../graphql-operations-types";
```

Use external files when the query has variables, fragments, or is shared across files. See [graphql-workflow.md](graphql-workflow.md) for the codegen pipeline.

### UI API response shape — every field is wrapped in `{ value }`

```ts
const data = await sdk.graphql?.(QUERY);
const edges = data?.uiapi.query.Account.edges;

edges?.forEach(edge => {
  const acct = edge?.node;
  console.log(acct?.Name.value);       // "Acme Corp"
  console.log(acct?.Industry.value);   // "Technology"
});
```

This is **Salesforce-specific**. Standard GraphQL doesn't wrap fields. Comment this in code aimed at React-first developers.

### `NodeOfConnection<T>`

```ts
import type { NodeOfConnection } from "@salesforce/sdk-data";
import type { ListAccountsQuery } from "../graphql-operations-types";

type AccountNode = NodeOfConnection<
  NonNullable<ListAccountsQuery["uiapi"]>["query"]["Account"]
>;

function renderRow(node: AccountNode) {
  return <tr><td>{node.Name.value}</td></tr>;
}
```

Use when:
- the response uses the `edges/node` connection shape
- you want a clean strongly-typed node alias for transforms / props / list rendering

Skip when your generated types are already flat / non-connection.

## `sdk.fetch?.()`

```ts
const res = await sdk.fetch?.(
  "/services/data/v66.0/ui-api/records/001xx0000000000",
  { method: "GET" }
);
```

Use for endpoints **not** covered by GraphQL. The wrapper handles:

- **CSRF token management**
- **Base path resolution** (so the same code works in dev, sandbox, Experience site)
- **401 / 403 callback hooks** registered in `createDataSDK` options

### Allow-listed endpoints

`sdk.fetch?.()` is supported for these endpoint shapes:

```
/services/apexrest/...
/services/data/v{version}/ui-api/records
/services/data/v{version}/ui-api/search-info
/services/data/v{version}/ui-api/layout
/services/data/v{version}/ui-api/session/csrf
/services/data/v{version}/connect/file/upload/config
/services/data/v{version}/connect/proxy/ui-telemetry
/services/data/v{version}/chatter/users/me
/services/data/v{version}/chatter/users/{userId}
/sfsites/c/_nc_external/system/security/session/SessionTimeServlet
/secur/logout.jsp
```

Anything outside this list is not guaranteed to work and should go through Apex REST instead.

### When to use `fetch` over GraphQL

- Apex REST endpoints exposing custom business logic GraphQL can't express.
- UI API REST endpoints not exposed via GraphQL (search-info, layout, chatter users, session/csrf).
- File upload bootstrap (`connect/file/upload/config`).
- GraphQL with a GET request (small queries with URL constraints, or when you specifically need a CSRF round-trip).

## Order of preference for data access

1. **GraphQL queries / mutations** via `sdk.graphql?.()`
2. **UI API REST / Apex REST** via `sdk.fetch?.()`
3. **GraphQL with `sdk.fetch?.()` GET** for the niche cases above
4. **Apex REST** when GraphQL can't do it

## Anti-patterns

```ts
// ❌ NEVER — bypasses auth, CSRF, base path
const res = await fetch("/services/data/v66.0/ui-api/records/001...");

// ❌ NEVER — same problem
const res = await axios.get("/services/data/...");

// ❌ Forgetting optional chaining — crashes in surfaces that don't expose graphql
const res = await sdk.graphql(QUERY);

// ✅ Correct
const res = await sdk.graphql?.(QUERY, variables);
```

## Reference wrapper (`graphqlClient.ts`)

The `multiframework-recipes` repo uses a thin wrapper:

```ts
// src/api/graphqlClient.ts
import { createDataSDK } from "@salesforce/sdk-data";
export { gql } from "@salesforce/sdk-data";

export async function executeGraphQL<TData, TVars = Record<string, unknown>>({
  query,
  variables
}: {
  query: string;
  variables?: TVars;
}): Promise<TData> {
  const sdk = await createDataSDK();
  const response = await sdk.graphql?.(query, variables);

  if (!response) throw new Error("GraphQL surface unavailable");
  if (response.errors?.length && !response.data) {
    throw new Error(response.errors.map(e => e.message).join("; "));
  }
  return response.data as TData;
}
```

This is a **Strict** error strategy. See [error-handling.md](error-handling.md) for Tolerant and Permissive variants.

## See also

- [graphql-workflow.md](graphql-workflow.md) — codegen and operation generation
- [error-handling.md](error-handling.md) — Strict / Tolerant / Permissive
- [Multi-Framework Recipes](https://github.com/trailheadapps/multiframework-recipes) — reference implementations
