# Error Handling

GraphQL responses can carry **both `data` and `errors`** in the same payload — partial success is a real outcome. `sdk.fetch?.()` calls add transport errors and HTTP-level errors on top. Pick a strategy per call site based on what "good enough" means for that operation.

## Three GraphQL error strategies

### 1. Strict — fail on any error

> Use when: data integrity matters; partial data would mislead the user.

```ts
async function strictExecute<T>(query: string, variables?: object): Promise<T> {
  const sdk = await createDataSDK();
  const response = await sdk.graphql?.(query, variables);
  if (!response) throw new Error("GraphQL surface unavailable");
  if (response.errors?.length) {
    throw new Error(response.errors.map(e => e.message).join("; "));
  }
  return response.data as T;
}
```

Good fit: financial summaries, compliance lookups, anything where a partial result is worse than no result.

### 2. Tolerant — log errors, use partial data

> Use when: optional fields can be missing; the UI degrades gracefully.

```ts
async function tolerantExecute<T>(query: string, variables?: object): Promise<T> {
  const sdk = await createDataSDK();
  const response = await sdk.graphql?.(query, variables);
  if (!response?.data) {
    throw new Error("No data returned");
  }
  if (response.errors?.length) {
    console.warn("GraphQL partial errors:", response.errors);
  }
  return response.data as T;
}
```

Good fit: list views with optional fields (e.g. `Photo`, `Industry`) where missing values render as empty cells.

### 3. Permissive — fail only when nothing usable came back

> Use when: mutations succeed but can't read back every requested field; the operation itself is what matters.

```ts
async function permissiveExecute<T>(query: string, variables?: object): Promise<T> {
  const sdk = await createDataSDK();
  const response = await sdk.graphql?.(query, variables);
  if (!response) throw new Error("GraphQL surface unavailable");
  if (!response.data && response.errors?.length) {
    throw new Error(response.errors.map(e => e.message).join("; "));
  }
  return response.data as T;
}
```

Good fit: `<Object>Update` mutations that return a `Record` containing fields the user lacks read access to.

## Picking a strategy

```
Is this a mutation that may have field-read errors?
  ├─ yes → Permissive
  └─ no
      Is the data critical (financial, legal, privileged)?
      ├─ yes → Strict
      └─ no  → Tolerant
```

## `sdk.fetch?.()` errors

`fetch` errors come in two layers:

### Transport errors

Network failures, aborted requests, CSRF mismatches. The `fetch` promise rejects.

```ts
try {
  const res = await sdk.fetch?.("/services/data/v66.0/ui-api/records/...", {
    method: "GET"
  });
  if (!res) throw new Error("fetch surface unavailable");
  if (!res.ok) {
    // HTTP error path — see below
    throw new HttpError(res.status, await res.text());
  }
  return await res.json();
} catch (e) {
  // Transport error path
  console.error("Transport failure", e);
  throw e;
}
```

### HTTP errors

Non-2XX responses. Distinguish auth-sensitive flows (`401`, `403`) from server errors.

```ts
if (res.status === 401) {
  await onSignInRefresh();
  return retryOnce();
}
if (res.status === 403) {
  showPermissionsHelp();
  throw new Error("Insufficient permissions for this action");
}
if (res.status >= 500) {
  throw new Error(`Server error ${res.status}`);
}
```

For auth-sensitive flows, prefer wiring `on401` / `on403` callbacks at the SDK level so the same behavior runs for every call:

```ts
const sdk = await createDataSDK({
  webapp: {
    on401: () => signInAgain(),
    on403: () => showPermissionsHelp()
  }
});
```

## React error boundaries

For component-tree errors (rendering, derived state), use Error Boundaries. Boundaries do **not** catch async errors from `sdk.graphql?.()` — those need standard `try / catch` or Promise `.catch()`. Use both layered.

```tsx
class RecipeBoundary extends React.Component<
  React.PropsWithChildren,
  { error: Error | null }
> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("Boundary caught:", error, info);
  }
  render() {
    if (this.state.error) {
      return <ErrorState message={this.state.error.message} />;
    }
    return this.props.children;
  }
}
```

Wrap recipe pages, not individual fields:

```tsx
<RecipeBoundary>
  <SingleRecord />
</RecipeBoundary>
```

## Loading / empty / error UI states

Every data-fetching component should handle four states explicitly:

| State | When | What to show |
|---|---|---|
| **Loading** | First fetch in flight | Skeleton or spinner — never an empty page |
| **Error** | `try/catch` triggered | Friendly message + retry button |
| **Empty** | Fetch succeeded, zero results | Helpful guidance, not a blank list |
| **Loaded** | Data present | The actual UI |

```tsx
function ContactsList() {
  const [state, setState] = useState<{
    status: "loading" | "error" | "empty" | "loaded";
    data?: Contact[];
    error?: string;
  }>({ status: "loading" });

  useEffect(() => {
    executeGraphQL<ListContacts>({ query: QUERY })
      .then(d => {
        const rows = d.uiapi.query.Contact.edges?.map(e => e?.node) ?? [];
        setState({
          status: rows.length ? "loaded" : "empty",
          data: rows as Contact[]
        });
      })
      .catch(err => {
        setState({
          status: "error",
          error: err instanceof Error ? err.message : "Request failed"
        });
      });
  }, []);

  if (state.status === "loading") return <Skeleton />;
  if (state.status === "error")   return <ErrorState message={state.error!} />;
  if (state.status === "empty")   return <EmptyState />;
  return <Table rows={state.data!} />;
}
```

> Use `err instanceof Error`, **not** `(err as Error).message`. The cast tells TypeScript to be quiet; the type guard tells the reader and the type system what's actually being checked.

## Anti-patterns

```ts
// ❌ Type cast to silence TS — no real check
.catch(err => setError((err as Error).message))

// ✅ Type guard — narrows safely
.catch(err => setError(err instanceof Error ? err.message : "Request failed"))

// ❌ Ignoring partial errors when they would mislead
return response.data;            // even with response.errors set

// ❌ Treating fetch != ok as success
const res = await sdk.fetch?.("/services/...");
return await res!.json();        // 401 page becomes garbage JSON
```

## LWC vs React error handling

| Concern | LWC | React |
|---|---|---|
| Tree-level errors | `errorCallback(error, stack)` lifecycle | Error Boundaries (`getDerivedStateFromError` + `componentDidCatch`) |
| Async data errors | `@wire` returns `{ data, error }` standardized | Promise `try/catch` in async functions |
| Standardization | Built into the framework | Convention only — pick one strategy and apply consistently |

Reference: the **error-handling** examples in the [Multi-Framework Recipes](https://github.com/trailheadapps/multiframework-recipes) repo cover boundaries, partial errors, and the four UI states above.
