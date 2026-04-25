# Testing UI Bundles

The reference repo ships a **Vitest + React Testing Library + Playwright** stack with an 85% coverage threshold and per-recipe accessibility tests (`vitest-axe`). Treat this as the default.

| Layer | Tool | Purpose |
|---|---|---|
| Unit / component | **Vitest** + **@testing-library/react** | Render recipe components with mocked SDK, assert on DOM |
| Accessibility | **vitest-axe** | Runs axe-core against the rendered container |
| End-to-end | **Playwright** | Runs the built `dist/` against a static server; no live org required |
| Org-side Apex | **sf-testing** skill | Apex test runner — this is *not* this stack's job |

## Install

```bash
npm install --save-dev vitest @vitest/ui @vitest/coverage-v8 \
  @testing-library/react @testing-library/jest-dom @testing-library/user-event @testing-library/dom \
  vitest-axe jsdom \
  @playwright/test serve
```

## `package.json` scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:coverage": "vitest --run --coverage",
    "test:e2e": "playwright test",
    "build:e2e": "npm run build && node scripts/rewrite-e2e-assets.mjs"
  }
}
```

`npm run test` is watch mode; `test -- --run` is CI mode. `test:coverage` emits text + HTML + lcov.

## `vitest.config.ts`

```ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@api": path.resolve(__dirname, "./src/api"),
      "@components": path.resolve(__dirname, "./src/components"),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./vitest.setup.ts",
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      reportsDirectory: "./coverage",
      thresholds: {
        global: { branches: 85, functions: 85, lines: 85, statements: 85 },
      },
    },
  },
});
```

### `vitest.setup.ts`

Two jsdom-specific stubs matter for axe-core:

```ts
import "@testing-library/jest-dom/vitest";
import * as matchers from "vitest-axe/matchers";
import { expect } from "vitest";

expect.extend(matchers);

// axe-core's color-contrast rule reaches into canvas + computed styles for
// pseudo-elements. jsdom implements neither — stub so axe doesn't throw.
HTMLCanvasElement.prototype.getContext = (() => null) as any;

const origGetComputedStyle = window.getComputedStyle;
window.getComputedStyle = (el, pseudoEl) =>
  pseudoEl ? ({} as CSSStyleDeclaration) : origGetComputedStyle(el);
```

Without these, every axe assertion throws `TypeError: getContext is not a function`.

## The standard recipe test pattern

Each recipe gets a `<Name>.test.tsx` sibling file. Mock `@salesforce/sdk-data` globally, control `graphql` / `fetch` per test, assert on DOM:

```tsx
// src/recipes/hello/BindingAccountName.test.tsx
import { render, screen } from "@testing-library/react";
import type { Mock } from "vitest";
import { createDataSDK } from "@salesforce/sdk-data";
import { axe } from "vitest-axe";
import BindingAccountName from "./BindingAccountName";

vi.mock("@salesforce/sdk-data", () => ({
  createDataSDK: vi.fn(),
  gql: (strings: TemplateStringsArray) => strings.join(""),
}));

const SUCCESS = {
  data: {
    uiapi: {
      query: {
        Account: {
          edges: [{ node: { Id: "001", Name: { value: "Acme Corp" } } }],
        },
      },
    },
  },
  errors: [],
};

describe("BindingAccountName", () => {
  const mockGraphql = vi.fn();

  beforeEach(() => {
    (createDataSDK as Mock).mockResolvedValue({ graphql: mockGraphql });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the account name after data loads", async () => {
    mockGraphql.mockResolvedValue(SUCCESS);
    render(<BindingAccountName />);
    expect(await screen.findByText("Acme Corp")).toBeInTheDocument();
  });

  it("renders error state on rejected promise", async () => {
    mockGraphql.mockRejectedValue(new Error("Network down"));
    render(<BindingAccountName />);
    expect(await screen.findByText(/network down/i)).toBeInTheDocument();
  });

  it("is accessible", async () => {
    mockGraphql.mockResolvedValue(SUCCESS);
    const { container } = render(<BindingAccountName />);
    await screen.findByText("Acme Corp");
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### LWC → React test-pattern translation

| LWC Jest | React equivalent |
|---|---|
| `registerApexTestWireAdapter` / `registerLdsTestWireAdapter` | `vi.mock('@salesforce/sdk-data', () => ...)` with a `vi.fn()` graphql |
| `adapter.emit(data); await Promise.resolve()` | `mockGraphql.mockResolvedValue(data)` + `await screen.findByText(...)` |
| `el.shadowRoot.querySelector(...)` | `screen.getByRole(...)` / `screen.getByText(...)` / `container.querySelector(...)` |
| `flushPromises()` | `findBy*` queries poll automatically; or `await waitFor(() => ...)` |
| `@salesforce/sfdx-lwc-jest` | Vitest + React Testing Library |

### Mock patterns by scenario

| Scenario | Mock shape |
|---|---|
| Query success | `mockGraphql.mockResolvedValue({ data: {...}, errors: [] })` |
| Query with errors | `mockGraphql.mockResolvedValue({ data: null, errors: [{ message: "..." }] })` |
| Network / transport failure | `mockGraphql.mockRejectedValue(new Error("..."))` |
| REST via `sdk.fetch` | `mockResolvedValue({ graphql: ..., fetch: vi.fn().mockResolvedValue({ ok: true, json: async () => ... }) })` |
| Mutation then query sequence | `mockGraphql.mockResolvedValueOnce(mutationRes).mockResolvedValueOnce(queryRes)` |

## Accessibility testing

Every recipe ends with an axe check:

```tsx
it("is accessible", async () => {
  const { container } = render(<Component />);
  await screen.findByText(/something/);   // wait for async render
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

This is non-negotiable in the reference repo and catches SLDS markup mistakes (missing `aria-label`, `role="status"` vs `role="alert"`, incorrect heading hierarchy). If SLDS React components break color-contrast, use axe's `rules` override per test — don't disable axe globally.

## `router` tests

Wrap the component under test in `MemoryRouter` with the route you want to test:

```tsx
import { MemoryRouter, Routes, Route } from "react-router";

render(
  <MemoryRouter initialEntries={["/route-parameters/001ABC"]}>
    <Routes>
      <Route path="/route-parameters/:accountId" element={<RouteParametersDetail />} />
    </Routes>
  </MemoryRouter>
);
```

`useParams()` resolves from the matched route; don't try to mock it.

## End-to-end with Playwright

The reference repo runs e2e against the built `dist/` via `serve`, not `vite preview`. `vite preview` invokes the Salesforce plugin which can fail without a connected org; a static server doesn't.

### `playwright.config.ts`

```ts
import { defineConfig, devices } from "@playwright/test";

const E2E_PORT = 5175;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: `http://localhost:${E2E_PORT}`,
    trace: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "Mobile Chrome", use: { ...devices["Pixel 5"] } },
  ],
  webServer: {
    command: `npx serve dist -l ${E2E_PORT}`,
    url: `http://localhost:${E2E_PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: process.env.CI ? 120_000 : 60_000,
  },
});
```

### What e2e tests *can't* do

- No real org data — the built bundle includes no `schema.graphql` at runtime.
- No ACC — the Lightning Out widget won't render outside a Salesforce host.
- No cookies / session — `createDataSDK()` will fail or return capability-missing.

Write e2e for: routing, layout regressions, empty-state rendering, keyboard navigation, focus management. Leave data-dependent flows to unit tests with mocked SDK.

## Coverage thresholds

The reference repo sets `branches/functions/lines/statements: 85`. Enforce this in CI (`vitest --run --coverage`). The config's `exclude` block matters:

```ts
coverage: {
  exclude: [
    "node_modules/",
    "src/**/*.d.ts",
    "src/main.tsx",
    "src/vite-env.d.ts",
    "src/components/**/index.ts",    // barrel files
    "**/*.config.ts",
    "build/",
    "dist/",
    "coverage/",
    "eslint.config.js",
  ],
},
```

## CI wiring

```yaml
# .github/workflows/ci.yml (excerpt)
- name: "Install React app dependencies"
  run: npm ci --prefix force-app/main/.../uiBundles/myApp

- name: "Lint"
  run: npm run lint --prefix force-app/main/.../uiBundles/myApp

- name: "Test"
  run: npm run test --prefix force-app/main/.../uiBundles/myApp -- --run --coverage

- name: "Build"
  run: npm run build --prefix force-app/main/.../uiBundles/myApp

- name: "Playwright"
  run: npm run test:e2e --prefix force-app/main/.../uiBundles/myApp
```

Full CI sequence: [ci-deploy.md](ci-deploy.md).

## Troubleshooting

| Symptom | Cause |
|---|---|
| `TypeError: getContext is not a function` in axe tests | Missing `HTMLCanvasElement` stub in `vitest.setup.ts` |
| `Cannot find module '@salesforce/sdk-data'` in tests | Vitest needs a `vi.mock(...)` hoist; verify it's at the top of the file |
| `findBy*` queries time out but UI clearly renders | Check whether the mocked `graphql` actually resolves — missing `.mockResolvedValue(...)` returns `undefined` |
| Playwright webServer times out in CI | Increase `timeout` to 120s; confirm `dist/` exists before `webServer` runs |
| Coverage report shows 0% for route pages | `src/pages` is glob-included but the pages just forward to recipes; test the recipes directly or exclude `src/pages` |
