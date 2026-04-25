# Footguns — Multi-Framework Beta Sharp Edges

Six failure modes ordered by stakes. Read this before starting work in a Multi-Framework project.

## 1. Stale GraphQL codegen → silent prod failure (highest stakes)

**Setup.** Multi-Framework projects generate `schema.graphql` by introspecting the connected org. The schema is **deliberately not committed** to the repo — it's regenerated per developer, per scratch org. The Vite plugin runs codegen conditionally: only if `schema.graphql` exists.

**Failure mode.** If `npm run graphql:schema` is skipped before `npm run build`:

- Build passes silently (Vite skips codegen when schema is missing)
- Lint passes
- TypeScript may catch *some* shape mismatches but not all — UIAPI's `{ value }` wrapping and Relay `edges → node` shape leave room for `undefined` field access at runtime
- Bundle ships, deploys, looks fine in dev
- Specific records / specific fields fail at runtime in production with `Cannot read properties of undefined (reading 'value')` or similar

**Why TypeScript doesn't save you.** The generated `graphql-operations-types.ts` is what binds your `.tsx` field accesses to actual UIAPI return shapes. Without fresh codegen, types fall back to looser shapes (or are missing entirely), and the compiler doesn't know to error.

**Prevent it.**

```bash
npm run graphql:schema  # introspect org → write schema.graphql
npm run graphql:codegen # generate graphql-operations-types.ts
npm run build           # only safe to run after the above
```

The bundled `scripts/check_codegen_freshness.py <project-root>` enforces this — exits 0 only when both files exist and the generated types are newer than the schema.

## 2. Non-English org → silent UI break

Multi-Framework is locked to English-default orgs in beta. The check is on **default org language** (`Organization.LanguageLocaleKey`), not user locale. Other languages produce no runtime error — the UI simply fails to load (blank or partial render).

**Prevent it.** In `config/project-scratch-def.json`:

```json
{
  "language": "en_US"
}
```

For sandboxes, confirm the default language is `en_US` before deploying.

## 3. No automatic cache invalidation after mutations

LWC's `updateRecord()` notifies all `@wire` adapters bound to the same record automatically. **React has no equivalent.** The Multi-Framework data SDK (`@salesforce/sdk-data`) leaves cache management to the developer.

**Failure mode.** A user creates / updates / deletes a record. The mutation succeeds. The page still shows the old data because no `@wire` notification ever fires. The user clicks refresh, sees the new data, files a bug.

**Prevent it.** After every mutation, manually update local state:

```tsx
const [accounts, setAccounts] = useState<Account[]>([]);
const onCreate = async (input: RecordCreateInput) => {
  const result = await sdk.executeGraphQL(CreateAccountMutation, { input });
  setAccounts((prev) => [...prev, result.uiapi.AccountCreate.Record]);
};
```

See `Modify Data → UpdateRecord` and `QueryMutationTogether` recipes for canonical patterns.

## 4. Extracting GraphQL queries to `src/api/` utilities (in recipes)

The `multiframework-recipes` repo's `AGENT.md` explicitly forbids extracting queries / mutations into shared utility files **inside recipe code**. Every recipe must inline its GraphQL so a reader can see the full pattern in one file.

**Why it's a footgun.** An agent applying generic React DRY principles will instinctively suggest `src/api/accountQueries.ts`. This breaks the recipe's pedagogical contract and gets PRs rejected.

**Application code is different.** Real apps may extract — the rule is recipe-specific.

## 5. Mixing styling systems in one component

Multi-Framework apps ship with **three styling systems coexisting**:

- SLDS CSS classes (via `@salesforce-ux/design-system` 2.29.0+)
- shadcn/ui + Tailwind + Lucide icons
- `design-system-react` (drop-in React components matching SLDS)

A single component using two systems renders inconsistently and confuses anyone reading the code. ESLint does not catch this.

**Prevent it.** Pick one system per component. Document the choice in a comment when it isn't obvious from the imports.

## 6. Production-org deploy attempts

Multi-Framework is **open beta**. Deploys to production orgs are unsupported and may succeed at the metadata layer but fail at runtime, or be blocked outright.

**Prevent it.** Always target a scratch org or sandbox. The skill should refuse to assist with `sf project deploy start --target-org <production>` and redirect to scratch / sandbox flow.
