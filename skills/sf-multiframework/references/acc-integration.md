# Agentforce Conversation Client (ACC) Integration

ACC is a **Lightning Web Component Interface (LWCI)** built on Lightning Out 2.0. It embeds an Agentforce **Employee Agent** chat UI inside a non-LWC host (your React app). It handles streaming, dynamic Lightning Type rendering, and brand styling.

> ACC for **internal apps** (employee use cases) is the path documented here. For external customer-facing apps, refer to the standalone *Agentforce Conversation Client Developer Guide*. For programmatic open/close inside a custom LWC (no React), use the ACC API directly.

## Why use ACC

- Drop-in chat container — no rebuild from scratch
- Token-by-token streaming infrastructure included
- **Dynamic Lightning Type rendering** — input/output/list/picklist UI components rendered on the fly based on agent responses
- Brand styling hooks (fonts, colors, borders, spacing, component substitutions)
- Cross-framework — embed in any non-LWC stack
- Lets you ship "write once, deploy anywhere" UX (Service Cloud, public site, or React app)

## Prerequisites

### 1. Org-side configuration

| Setting | Path | Action |
|---|---|---|
| Agentforce preference | Setup → Einstein → Einstein Generative AI → Agentforce Studio → Agentforce Agents | **Enable** |
| Employee Agent | Same area | At least one configured with topics + actions |
| Cookie policy | Setup → My Domain → Routing and Policies | **Uncheck** *Require first-party use of Salesforce cookies* |
| Trusted Domains for Inline Frames | Setup → Session Settings | Add prod URL **and** local dev URL (e.g. `http://localhost:5173`), iFrame type **Lightning Out** |

Skipping any of these is the #1 cause of "FAB doesn't appear" or "panel disconnects on navigation" errors.

### 2. Project-side dependencies

```bash
cd force-app/main/default/uiBundles/myApp
npm install @salesforce/agentforce-conversation-client
```

## Two integration paths

### Path A — Agentforce Vibes (natural-language scaffolding)

If you're using VS Code with Agentforce Vibes:

1. Open the Vibes panel and confirm the Salesforce skills + rules are enabled.
2. Confirm your DX project has the standard structure (see [project-structure.md](project-structure.md)).
3. Use natural-language prompts:

> "Create an Agentforce Employee Agent panel that is docked to the right of the main screen."

> "The Agentforce Employee Agent panel should start as a floating FAB icon docked to the lower left of the page; when a user clicks the icon, it should expand into a full chat panel."

Vibes manipulates `index.tsx`, installs npm dependencies, and configures dock/floating/inline modes for you.

### Path B — Manual integration

Use `createAccWidget` from the package directly, with a `useRef` container and `useEffect` lifecycle.

```tsx
import { useEffect, useRef } from "react";
import { createAccWidget } from "@salesforce/agentforce-conversation-client";

export function ChatPanel() {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetRef = useRef<{ destroy: () => void } | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    widgetRef.current = createAccWidget({
      container: containerRef.current,
      mode: "floating",                 // or "inline" / "docked"
      welcomeMessage: "How can I help today?",
      brand: {
        primaryColor: "#0176d3",
        borderRadius: "0.5rem"
      }
      // additional SDK style tokens supported per official docs
    });

    return () => {
      widgetRef.current?.destroy();
    };
  }, []);

  return <div ref={containerRef} className="acc-host" />;
}
```

> The exact `createAccWidget` option shape evolves with the package. Always check the installed `@salesforce/agentforce-conversation-client` version's TypeScript declarations or README for the current API.

## Display modes

| Mode | Behavior | Use case |
|---|---|---|
| **Floating** | Default. FAB icon → expands to chat panel | Single-page apps where chat is secondary |
| **Docked** | Persistent panel attached to a side of the viewport | Apps where chat is a primary surface |
| **Inline** | Renders inside a designated parent container | Embedding chat as a section of a dashboard |

## What ACC handles for you

| Capability | What it does |
|---|---|
| **Streaming** | Token-by-token rendering, progress status indicators, low perceived latency |
| **Lightning Types** | Auto-maps `lightning__textType`, custom Lightning Types, etc. to the right UI renderer |
| **Dynamic rendering** | Constructs UI components in real time based on agent planner output |
| **Branding** | SDK exposes style tokens (header color, message block colors, fonts, radii) |
| **Welcome message** | Configurable "secure connection" confirmation when the panel opens |
| **Inline rich UI** | Cards, lists, form-style inputs (e.g. flight booking, property listings) rendered directly in the conversation |

## Integration checklist

- [ ] Agentforce preference is **enabled** in Setup
- [ ] At least one Employee Agent with topics + actions exists
- [ ] My Domain → "Require first-party use of Salesforce cookies" is **off**
- [ ] Session Settings → Trusted Domains for Inline Frames includes both prod and local dev origins
- [ ] iFrame type for those domains is **Lightning Out**
- [ ] `@salesforce/agentforce-conversation-client` installed
- [ ] Mount uses `useRef` for the container element
- [ ] Mount runs in `useEffect` and **cleans up** in the return function
- [ ] If using Vibes, all Salesforce MCP servers and skills are enabled
- [ ] Smoke-test: FAB appears, panel opens, agent connects, Lightning Types render

## Common ACC failure patterns

| Symptom | Cause | Fix |
|---|---|---|
| FAB never appears | Trusted Domain not added, or cookies still restricted | Verify both Setup steps; ensure iFrame type is Lightning Out |
| Panel opens but agent disconnects on nav | Origin mismatch between deployed app and Trusted Domain entry | Add the exact origin (`https://app.example.com`, including port if non-standard) |
| Welcome message missing | Agentforce preference disabled | Setup → Einstein → enable Agentforce |
| Rich Lightning Types render as plain text | Agent action output not configured to use a Lightning Type | Update GenAiFunction output schema (delegate to sf-ai-agentforce) |
| Streaming stutters / cuts off | Network instability — ACC handles this, but logs help | Inspect browser devtools → Network → keepalive |
| Chat panel state lost on React re-render | Widget destroyed/recreated | Memoize the container, only recreate when mount key changes |
| Branding doesn't apply | SDK style tokens passed wrong key names | Check installed package version's docs for current option names |

## Local dev specifics

- The Vite dev server origin (default `http://localhost:5173`) **must** be added to Trusted Domains for Inline Frames.
- Restart the dev server after adding the domain in Salesforce — the iframe needs a fresh load.
- ACC will not work in `localhost` until *both* the cookie policy AND trusted domain entries are in place.

## What to do when ACC isn't right

| Need | Use instead |
|---|---|
| External-facing customer chat | Standalone Agentforce Conversation Client (separate guide) |
| Programmatic open/close inside a custom LWC | ACC API directly |
| Chat with a Service Agent (not Employee) | Different ACC flavor — check the standalone guide |
| Custom UI for agent output you fully control | Build the agent action with a custom Lightning Type and a custom LWC renderer (delegate to sf-ai-agentforce / sf-lwc) |

## See also

- [Integrate ACC in a React App (official Beta docs)](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/reactdev-acc.html)
- [setup.md](setup.md) — full org configuration sequence
- Lightning Types in Agent Action — official Salesforce docs
