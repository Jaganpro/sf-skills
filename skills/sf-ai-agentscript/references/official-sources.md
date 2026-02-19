<!-- Parent: sf-ai-agentscript/SKILL.md -->
# Official Sources Registry

> Canonical Salesforce documentation URLs for Agent Script. Use this registry to verify syntax, resolve errors, and stay current with platform changes.

---

## Primary References (Agent Script Documentation)

| # | Page | URL | Use When |
|---|------|-----|----------|
| 1 | Agent Script Overview | https://developer.salesforce.com/docs/ai/agentforce/guide/agent-script.html | Starting point, general concepts |
| 2 | Blocks Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-blocks.html | Block structure, required fields |
| 3 | Flow Integration | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-flow.html | `flow://` targets, Flow wiring |
| 4 | Actions Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-actions.html | Action definitions, targets, I/O |
| 5 | Variables Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-variables.html | Mutable, linked, types, sources |
| 6 | Tools Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-tools.html | `@utils.*` utilities, transitions |
| 7 | Utils Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-utils.html | Utility action details |
| 8 | Instructions Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-instructions.html | Pipe vs arrow, resolution order |
| 9 | Expressions Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-expressions.html | Operators, template injection |
| 10 | Before/After Reasoning | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-before-after.html | Lifecycle hooks syntax |
| 11 | Operators Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-operators.html | Comparison, logical, arithmetic |
| 12 | Topics Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-topics.html | Topic structure, transitions |
| 13 | Examples | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-example.html | Complete working examples |
| 14 | Agent DX (CLI) | https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx.html | CLI commands, bundle structure |

> **URL Prefix Note**: Agent Script docs migrated from `/docs/einstein/genai/guide/ascript-*` (older beta path) to `/docs/ai/agentforce/guide/ascript-*` (current path). If a URL 404s, try swapping the prefix.

---

## Recipe Repository

| # | Page | URL | Content |
|---|------|-----|---------|
| 1 | Recipes Overview | https://developer.salesforce.com/sample-apps/agent-script-recipes/getting-started/overview | Getting started guide |
| 2 | GitHub Repository | https://github.com/trailheadapps/agent-script-recipes | Source code, AGENT_SCRIPT.md rules |
| 3 | Hello World | https://developer.salesforce.com/sample-apps/agent-script-recipes/language-essentials/hello-world | Minimal agent example |
| 4 | Action Definitions | https://developer.salesforce.com/sample-apps/agent-script-recipes/action-configuration/action-definitions | Action config patterns |
| 5 | Multi-Topic Navigation | https://developer.salesforce.com/sample-apps/agent-script-recipes/architectural-patterns/multi-topic-navigation | Topic routing patterns |
| 6 | Error Handling | https://developer.salesforce.com/sample-apps/agent-script-recipes/architectural-patterns/error-handling | Error handling patterns |
| 7 | Bidirectional Navigation | https://developer.salesforce.com/sample-apps/agent-script-recipes/architectural-patterns/bidirectional-navigation | Two-way topic transitions |
| 8 | Advanced Input Bindings | https://developer.salesforce.com/sample-apps/agent-script-recipes/action-configuration/advanced-input-bindings | Slot-fill, fixed, variable binding |

---

## Diagnostic Decision Tree

When something fails, use this tree to determine which doc page to fetch:

```
Error or Ambiguity
       │
       ├─ Compilation / SyntaxError
       │     ├─ Block-level error → Fetch #2 (Blocks Reference)
       │     ├─ Expression error  → Fetch #9 (Expressions) + #11 (Operators)
       │     └─ Action error      → Fetch #4 (Actions Reference)
       │
       ├─ Action not executing
       │     ├─ Action defined but LLM doesn't pick it → Fetch #4 (Actions) + #6 (Tools)
       │     └─ Action target not found               → Fetch #4 (Actions) + #14 (Agent DX)
       │
       ├─ Variable not updating
       │     ├─ Linked var empty     → Fetch #5 (Variables)
       │     └─ Mutable not changing → Fetch #5 (Variables) + #8 (Instructions)
       │
       ├─ Topic transition wrong
       │     ├─ Wrong topic selected  → Fetch #12 (Topics) + #7 (Utils)
       │     └─ Transition vs delegation confusion → Fetch #6 (Tools) + #12 (Topics)
       │
       ├─ Lifecycle hook issue
       │     └─ before/after_reasoning error → Fetch #10 (Before/After)
       │
       └─ New / unfamiliar syntax
             └─ Start with #1 (Overview), then narrow to specific reference
```

---

## Fallback Search Patterns

When a specific URL 404s or doesn't have the answer:

```bash
# Primary search pattern
site:developer.salesforce.com agent script <topic>

# Recipe search
site:developer.salesforce.com sample-apps agent-script-recipes <topic>

# GitHub issues (known bugs, community solutions)
site:github.com trailheadapps agent-script-recipes <error message>

# Salesforce Stack Exchange
site:salesforce.stackexchange.com agent script <topic>
```

---

## URL Health Check

When verifying URLs, use WebFetch to confirm each resolves. If a URL redirects or 404s:

1. Try swapping the URL prefix (see note above)
2. Use the fallback search pattern
3. If consistently broken, update this file and note the date

---

*Last updated: 2026-02-12*
