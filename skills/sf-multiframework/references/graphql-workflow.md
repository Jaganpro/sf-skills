# GraphQL Workflow

Multi-Framework apps use the **Salesforce GraphQL UI API** (`uiapi`) for record reads and writes. This guide covers the full type-safe pipeline: schema introspection → codegen → operations → typed call sites.

## Pipeline overview

```
Connected org
  │  npm run graphql:schema           (org → schema.graphql)
  ▼
schema.graphql                        (gitignored, regenerated)
  │  npm run graphql:codegen          (schema + operations → types)
  ▼
src/api/graphql-operations-types.ts   (generated)
  │  imported by call sites
  ▼
React components
```

## Step 1 — Generate the schema from a connected org

```bash
npm run graphql:schema
```

What it does:
- Authenticates against the currently authorized org
- Runs an introspection query
- Writes `schema.graphql` to the project root

Notes:
- `schema.graphql` is **not** committed (it's org-specific).
- Re-run any time the org schema changes (new objects, new fields).
- Scratch org support is uncertain — sandbox is the safest bet.

## Step 2 — Define operations

### Pattern A — Inline `gql` (simple)

```ts
import { createDataSDK, gql } from "@salesforce/sdk-data";

const SINGLE_ACCOUNT = gql`
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

Best for:
- Recipe / single-component reads
- No variables, no fragments
- The lesson should be visible inline

### Pattern B — External `.graphql` file (complex / shared)

```
src/api/utils/query/listAccountsQuery.graphql
src/api/utils/mutation/updateAccountMutation.graphql
```

```graphql
# listAccountsQuery.graphql
query ListAccounts($first: Int = 20, $after: String) {
  uiapi {
    query {
      Account(first: $first, after: $after, orderBy: { Name: { order: ASC } }) {
        edges {
          node {
            Id
            Name { value }
            Industry { value }
            BillingCity { value }
          }
        }
        pageInfo { endCursor hasNextPage }
      }
    }
  }
}
```

Best for:
- Queries with variables, fragments, or shared use across files
- Anything codegen should produce types for

## Step 3 — Generate types

```bash
npm run graphql:codegen
```

This reads `codegen.yml` and emits `src/api/graphql-operations-types.ts` containing:

- `<OperationName>Query` / `<OperationName>Mutation` — response type
- `<OperationName>QueryVariables` / `<OperationName>MutationVariables` — variables type

### `codegen.yml` essentials

```yaml
schema: ./schema.graphql
documents:
  - "src/**/*.graphql"
  - "src/**/*.ts"
  - "src/**/*.tsx"
generates:
  src/api/graphql-operations-types.ts:
    plugins:
      - typescript
      - typescript-operations
    config:
      scalars:
        Currency:        string
        Date:            string
        DateTime:        string
        Email:           string
        EncryptedString: string
        Long:            number
        MultiPicklist:   string
        Percent:         number
        Phone:           string
        Picklist:        string
        TextArea:        string
        Time:            string
        Url:             string
```

The full UI API scalar list is critical — without it, codegen falls back to `any` for many fields. The `multiframework-recipes` `codegen.yml` is a known-good template.

## Step 4 — Use typed operations

### External file usage

```tsx
import QUERY from "./query/listAccountsQuery.graphql?raw";
import type {
  ListAccountsQuery,
  ListAccountsQueryVariables,
  NodeOfConnection
} from "../graphql-operations-types";
import { executeGraphQL } from "../graphqlClient";

type AccountNode = NodeOfConnection<
  NonNullable<ListAccountsQuery["uiapi"]>["query"]["Account"]
>;

export async function getAccounts(first: number) {
  const data = await executeGraphQL<ListAccountsQuery, ListAccountsQueryVariables>({
    query: QUERY,
    variables: { first }
  });
  return data.uiapi.query.Account.edges?.map(e => e?.node) ?? [];
}
```

`?raw` is a Vite import suffix that gives you the file as a string.

### Inline usage

```tsx
import { createDataSDK, gql } from "@salesforce/sdk-data";

const QUERY = gql`
  query SingleAccount {
    uiapi { query { Account(first: 1) { edges { node { Id Name { value } } } } } }
  }
`;

const sdk = await createDataSDK();
const data = await sdk.graphql?.(QUERY);
```

For inline `gql` queries, codegen still picks up the operation if your `documents` glob includes `.ts` / `.tsx`.

## Mutations

```graphql
# updateAccountMutation.graphql
mutation UpdateAccount($input: AccountUpdateInput!) {
  uiapi {
    AccountUpdate(input: $input) {
      Record {
        Id
        Name { value }
        Industry { value }
      }
    }
  }
}
```

Mutation input types follow the pattern `<ObjectName>CreateInput` / `<ObjectName>UpdateInput`. Search the schema first:

```bash
# Find available fields
rg "type Account implements Record" schema.graphql

# Find filter / sort / input options
rg "input Account_Filter|input Account_OrderBy|input AccountUpdateInput" schema.graphql
```

> Some fields **cannot be returned** from a mutation. If you get partial data + errors back, use the **Permissive** error strategy or remove the offending fields from the return shape. See [error-handling.md](error-handling.md).

## Schema exploration tips

When designing a query, search `schema.graphql`:

| You need | Search pattern |
|---|---|
| Available fields on an object | `type <ObjectName> implements Record` |
| Filter inputs | `input <ObjectName>_Filter` |
| Order-by inputs | `input <ObjectName>_OrderBy` |
| Mutation create/update inputs | `input <ObjectName>CreateInput` / `input <ObjectName>UpdateInput` |
| Connections | `type <ObjectName>Connection` |

## Recipe vs production patterns

`multiframework-recipes` ships an **explicit anti-pattern guidance**: in **recipes**, queries should be **inline `gql`** so the lesson is visible top-to-bottom. In **production code**, `.graphql` files + codegen are usually the better choice for shared operations.

Choose per use case:

| Use case | Pattern |
|---|---|
| Educational recipe / docs example | Inline `gql` |
| One-off component, no variables | Inline `gql` |
| Shared list query used by 3+ pages | External `.graphql` + codegen |
| Mutation with complex input | External `.graphql` + codegen |

## Common GraphQL errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Codegen produces empty types file | `schema.graphql` missing | `npm run graphql:schema` |
| `Property 'value' does not exist on type 'string'` | Forgot the `{ value }` wrapper | Read field as `record.Name.value` |
| `edges` is `null` despite data | Filter excluded everything; pageInfo / size mismatch | Drop filter, narrow with explicit field args |
| Mutation succeeds but errors mention a return field | Field can't be selected on mutation return | Remove that field from the mutation, or switch to Permissive |
| Codegen types fall back to `any` | Scalar mappings missing in `codegen.yml` | Add full UIAPI scalar list (see above) |
| `gql` template highlights nothing | GraphQL ESLint plugin / extension not configured | Install `@graphql-eslint/eslint-plugin` and configure |
