# Styling React Apps

React UI bundles **don't have access to Lightning base components or `lightning/*` modules**, so the automatic SLDS styling LWCs get isn't available. You have three viable approaches; pick one **per component** (mixing inside one component is the most common review failure).

## The three approaches

| Approach | When to choose | Pros | Cons |
|---|---|---|---|
| **SLDS blueprints (CSS classes)** | You want native Salesforce look, full markup control | Pixel-accurate Lightning feel; latest SLDS available | You manage every CSS class manually; no auto-updates |
| **`@salesforce/design-system-react`** | You want SLDS components without writing the markup | Pre-built React components; familiar Lightning API | Pins an older SLDS CSS version |
| **Tailwind + shadcn/ui** | You want a custom-branded look or fresh design system | Fast to compose; great DX; modern aesthetic | Drifts from native SLDS unless you tokenize carefully |

## 1. SLDS Blueprints

Apply the SLDS class names directly in JSX. Import the SLDS CSS once globally.

```bash
npm install @salesforce-ux/design-system
```

```css
/* src/styles/slds.css */
@import "@salesforce-ux/design-system/assets/styles/salesforce-lightning-design-system.css";
```

```tsx
function AccountCard() {
  return (
    <article className="slds-card">
      <div className="slds-card__header slds-grid">
        <header className="slds-media slds-media_center slds-has-flexi-truncate">
          <div className="slds-media__body">
            <h2 className="slds-card__header-title">
              <span>Account</span>
            </h2>
          </div>
        </header>
      </div>
      <div className="slds-card__body slds-card__body_inner">
        Acme Corp
      </div>
      <footer className="slds-card__footer">
        <button className="slds-button slds-button_brand">View</button>
      </footer>
    </article>
  );
}
```

> Blueprint = HTML + CSS class contract. You own the markup; SLDS owns the look. There is **no behavior** — you wire interaction yourself.

## 2. `@salesforce/design-system-react`

Pre-built React components matching SLDS.

```bash
npm install @salesforce/design-system-react
```

Wrap with `IconSettings` to configure the sprite path so icons resolve:

```tsx
import IconSettings from "@salesforce/design-system-react/components/icon-settings";
import Card from "@salesforce/design-system-react/components/card";
import Button from "@salesforce/design-system-react/components/button";

export default function App() {
  return (
    <IconSettings iconPath="/assets/icons">
      <Card heading="Acme Corp">
        <Button variant="brand" label="View" />
      </Card>
    </IconSettings>
  );
}
```

Caveat: this package pins an older SLDS CSS — newer SLDS tokens / blueprints may not match. Don't combine with `@salesforce-ux/design-system` in the same component (versions can clash).

## 3. Tailwind + shadcn/ui

The pattern used by `multiframework-recipes` for the **app shell** (Navbar, Layout, Card primitives). shadcn copies component source into your project so you customize via Tailwind classes directly.

```bash
# Tailwind 4 + shadcn (see official shadcn docs for full init)
npx shadcn@latest init
npx shadcn@latest add button card input
```

`global.css` is your design-system entry point:

```css
@import "tailwindcss";

@layer base {
  body {
    @apply min-h-screen antialiased text-foreground bg-background;
  }
}

:root {
  --color-background: oklch(1 0 0);
  --color-foreground: oklch(0.145 0 0);
  --color-primary:    oklch(0.205 0 0);
  --color-secondary:  oklch(0.97 0 0);
  --color-border:     oklch(0.922 0 0);
  --radius:           0.5rem;
  --ring:             #0176d3;          /* Salesforce brand blue for native focus feel */
}

.dark {
  --color-background: oklch(0.145 0 0);
  --color-foreground: oklch(0.985 0 0);
}

@theme inline {
  --color-background: var(--color-background);
  --color-foreground: var(--color-foreground);
  --color-primary:    var(--color-primary);
  --color-secondary:  var(--color-secondary);
  --color-border:     var(--color-border);
}
```

Now utilities like `bg-background`, `text-foreground`, `border-border`, `ring-ring` work across components.

### Notable token differences vs SLDS

| Token | SLDS 1 | SLDS 2 | shadcn default |
|---|---|---|---|
| Border radius (button/card) | `0.25rem` (4px) | `15rem` (pill) | `0.5rem` |
| Focus ring color | Salesforce blue (`#0176d3`) | Same | Black/grey |
| Secondary background | Light grey (`#f3f3f3`) | Same | Darker grey |

If you want a Salesforce-native feel with shadcn, override these tokens in `global.css` rather than per-component.

## Migration: `lightning-card` → shadcn `Card`

This is the canonical example because it shows **template-driven (LWC slots)** vs **composition-driven (React)**.

### Original LWC

```html
<lightning-card title="Account" icon-name="standard:account">
  <p slot="actions">Edit</p>
  <p>Acme Corp</p>
  <p slot="footer">Updated 2 days ago</p>
</lightning-card>
```

### React with shadcn

```tsx
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter
} from "@/components/ui/card";

export function AccountCard() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Account</CardTitle>
        <button className="text-sm">Edit</button>
      </CardHeader>
      <CardContent>Acme Corp</CardContent>
      <CardFooter className="text-xs text-muted-foreground">
        Updated 2 days ago
      </CardFooter>
    </Card>
  );
}
```

Each named slot becomes an explicit sub-component. You see the structure top-to-bottom in JSX.

## Icons

| Source | Pattern |
|---|---|
| SLDS sprite (CSS) | `<svg className="slds-icon slds-icon_x-small"><use xlinkHref="/assets/icons/utility-sprite/svg/symbols.svg#event" /></svg>` |
| `design-system-react` | Wrap in `<IconSettings iconPath="/assets/icons">`, then `<Icon category="utility" name="event" />` |
| Tailwind / shadcn | Use `lucide-react` (`<Calendar />`) or your preferred icon set |

> Workspace rule (.cursorrules): prefer `utility:` icons over `standard:` for transparent backgrounds. Same applies in React app icon picks.

## One styling system per component

The single most common review failure is mixing systems inside one component:

```tsx
// ❌ Mixing — hostile to readers and to dark mode
<div className="flex items-center gap-4">          {/* Tailwind */}
  <button className="slds-button slds-button_brand"> {/* SLDS */}
    Save
  </button>
</div>

// ✅ Pick one
<div className="slds-grid slds-grid_vertical-align-center slds-gutters">
  <button className="slds-button slds-button_brand">Save</button>
</div>

// ✅ Or commit to Tailwind
<div className="flex items-center gap-4">
  <Button variant="default">Save</Button>
</div>
```

It's fine to use **Tailwind for the app shell** and **SLDS inside data recipes**, as long as the boundary is the component itself.

## Dark mode

- Tailwind/shadcn: define `.dark` overrides in `global.css`; toggle by adding `class="dark"` on `<html>`.
- SLDS blueprints: SLDS 2 has dark theming variables. SLDS 1 does not — you'd build dark overrides yourself.
- `design-system-react`: limited; the pinned SLDS version may not support modern dark theming.

## Reference

The **styling** examples in the [Multi-Framework Recipes](https://github.com/trailheadapps/multiframework-recipes) repo demonstrate all three approaches side-by-side, including the exact `global.css` token setup and a fully migrated `Card` example.
