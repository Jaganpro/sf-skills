# Recipe Conventions

These conventions come from the [`trailheadapps/multiframework-recipes`](https://github.com/trailheadapps/multiframework-recipes) reference repo. They apply when building **learning recipes** — self-contained components that demonstrate one concept at the React × Salesforce intersection. They're a strong default for production code too, with explicit exceptions called out below.

## What is a recipe?

A self-contained component that demonstrates **one** concept. Each recipe should be understandable **in isolation, top to bottom, without opening another file**.

## Goals & non-goals

| Goal | Non-goal |
|---|---|
| Teach things React devs don't know about Salesforce | Teach React fundamentals |
| Teach things Salesforce devs don't know about React | Re-document standard Hooks |
| Show idiomatic Multi-Framework patterns | Be a complete production app |

## File organization

```
src/
  recipes/
    <category>/
      RecipeName.tsx       # the recipe itself
  pages/
    <Category>.tsx         # container that imports and renders recipes in a grid
  components/
    app/                   # app shell (Navbar, Layout, CodeBlock)
    recipe/                # shared recipe UI (Skeleton, ContactTile, RecipeCard)
    ui/                    # shadcn primitives
```

## Naming

| Type | Convention | Example |
|---|---|---|
| Recipe file | PascalCase | `SingleRecord.tsx` |
| `.graphql` file | camelCase | `singleAccountQuery.graphql` |
| Hook | camelCase + `use` prefix | `useAuth.ts` |
| Page (container) | PascalCase | `ReadData.tsx` |

## Critical rule — recipe code ≠ production code

Recipes optimize for **reading**, not authoring. The reader should hit the interesting code first.

> **INLINE the thing the recipe teaches.** If a recipe is about GraphQL queries, the query MUST be visible in the recipe file. If it's about mutations, the mutation MUST be visible.

> **DO NOT** abstract queries, mutations, types, or SDK calls into shared utility files and import them into recipes.

This **overrides** the general "external `.graphql` + codegen" pattern. Recipes use **inline `gql`** instead.

Exception: a later recipe in a category may reference a pattern taught earlier ("see SingleRecord for the basic query"), but the new code it adds must still be inline.

## File structure (top to bottom — mandatory for recipes)

```tsx
/**
 * Recipe 2.1: Single Record
 *
 * Queries a single Account by ID using sdk.graphql.
 * Demonstrates the inline gql pattern and the { value } UIAPI shape.
 */

// 1. Imports
import { useEffect, useState } from "react";
import { createDataSDK, gql } from "@salesforce/sdk-data";

// 2. GraphQL query (inline, not imported)
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

// 3. Type definitions (explicit, not inferred)
interface AccountFields {
  id: string;
  name: string;
  industry: string | null;
}

// 4. Default export — the recipe component
export default function SingleRecord() {
  const [account, setAccount] = useState<AccountFields | undefined>();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const sdk = await createDataSDK();
        const res = await sdk.graphql?.(QUERY);
        const node = res?.data?.uiapi?.query?.Account?.edges?.[0]?.node;
        if (node) {
          setAccount({
            id: node.Id,
            name: node.Name.value ?? "—",
            industry: node.Industry.value ?? null
          });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Request failed");
      }
    })();
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!account) return <Skeleton />;
  return <AccountTile account={account} />;
}

// 5. Helper sub-components (below the main export)
function Skeleton() { return <div className="slds-card slds-is-loading" />; }
function ErrorState({ message }: { message: string }) {
  return <div className="slds-text-color_error">{message}</div>;
}
function AccountTile({ account }: { account: AccountFields }) {
  return (
    <article className="slds-card">
      <h2 className="slds-card__header-title">{account.name}</h2>
      <p>{account.industry ?? "Unknown industry"}</p>
    </article>
  );
}
```

## Component ordering: most relevant code first

The default-exported component goes **at the top** of the file. Helpers go **below**. This is the opposite of typical "define before use" style, but better for a reading-first codebase.

## Break complex JSX into named sub-components

If you'd write a JSX comment like `{/* Column headers */}`, that's a sign it should be a named sub-component instead. Loading skeletons, error states, cards, and list items belong below the main component.

Exception: recipes specifically *about* UI (`hello/`, `styling/`) can inline more.

## Extract reused UI to `components/recipe/`

If the same UI pattern appears across multiple **non-UI** recipes (skeletons, contact tiles, paginators, recipe cards, SLDS cards), extract it. Each recipe stays focused on its lesson.

## Commenting

| DO | DON'T |
|---|---|
| Comment platform-specific behavior: `{ value }` wrappers, `edges/node`, `__r` traversal, mutation input shapes | Comment standard React patterns (`useState`, `useEffect`, JSX) |
| Explain why an SLDS class was chosen over Tailwind | Restate what the line of code does |
| Cross-reference earlier recipes by name | Leave `console.log` or SDK debug code |

## Anti-patterns (block in review)

### ❌ Importing queries / mutations from `src/api/` into a recipe
```tsx
// BAD — hides the lesson
import { getContacts } from "@/api/contacts";
```

### ❌ Complex inferred types
```tsx
// BAD — unreadable
const [c, setC] = useState<Awaited<ReturnType<typeof getContacts>>[number]>();
```
Use explicit `interface` definitions.

### ❌ Type casts for errors
```tsx
// BAD — silences the type system
.catch(err => setError((err as Error).message))

// GOOD — type-guards
.catch(err => setError(err instanceof Error ? err.message : "Request failed"))
```

### ❌ Importing formatting utilities
```tsx
// BAD — opaque
import { formatPhone } from "@/utils/formatPhone";
<a href={`tel:${value}`}>{formatPhone(value)}</a>

// GOOD — just render
<a href={`tel:${phone}`}>{phone}</a>
```

### ❌ Mixing styling systems in one recipe
```tsx
// BAD
<div className="flex items-center gap-4">           {/* Tailwind */}
  <button className="slds-button slds-button_brand"> {/* SLDS */}
```

Pick one system per recipe. Data recipes typically use SLDS throughout.

### ❌ Debug code committed in recipes
```tsx
// BAD
createDataSDK().then(sdk => console.log(`sdk: ${JSON.stringify(sdk)}`));
```

### ❌ "Hello" recipes that teach pure React
```tsx
// BAD — works identically outside Salesforce
export default function DataBinding() {
  const [count, setCount] = useState(0);
  return <p>Count: {count}</p>;
}

// GOOD — grounded in the platform
export default function BindingAccountName() {
  // Fetches an Account via GraphQL, binds Name.value to UI
}
```

Every Hello recipe must involve the Salesforce platform. If it would work identically outside Salesforce, it belongs in a React tutorial, not here.

## Verification checklist (per recipe)

- [ ] Query / mutation is **inline** in the recipe file
- [ ] Types are **explicit interfaces**, not `Awaited<ReturnType<...>>` or `NonNullable<...>` chains
- [ ] Errors use `err instanceof Error`, not `(err as Error)`
- [ ] No utility imports for formatting (e.g. `formatPhone`)
- [ ] No `console.log` or SDK introspection debug code
- [ ] One styling system used throughout the component
- [ ] If it's a Hello recipe, it touches the Salesforce platform
- [ ] `npm run build` passes
- [ ] `npm run lint` passes

## When to break the rules

In **production application code** (not recipes), it's appropriate to:

- extract shared queries to `src/api/utils/query/*.graphql` with codegen
- abstract mutations into typed utility functions
- centralize formatting helpers
- use complex generic types where they genuinely add safety

But never inside a file labeled as a recipe.
