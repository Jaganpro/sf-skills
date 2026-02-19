<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Official Sources Registry
   2 
   3 > Canonical Salesforce documentation URLs for Agent Script. Use this registry to verify syntax, resolve errors, and stay current with platform changes.
   4 
   5 ---
   6 
   7 ## Primary References (Agent Script Documentation)
   8 
   9 | # | Page | URL | Use When |
  10 |---|------|-----|----------|
  11 | 1 | Agent Script Overview | https://developer.salesforce.com/docs/ai/agentforce/guide/agent-script.html | Starting point, general concepts |
  12 | 2 | Blocks Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-blocks.html | Block structure, required fields |
  13 | 3 | Flow Integration | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-flow.html | `flow://` targets, Flow wiring |
  14 | 4 | Actions Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-actions.html | Action definitions, targets, I/O |
  15 | 5 | Variables Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-variables.html | Mutable, linked, types, sources |
  16 | 6 | Tools Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-tools.html | `@utils.*` utilities, transitions |
  17 | 7 | Utils Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-utils.html | Utility action details |
  18 | 8 | Instructions Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-instructions.html | Pipe vs arrow, resolution order |
  19 | 9 | Expressions Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-expressions.html | Operators, template injection |
  20 | 10 | Before/After Reasoning | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-before-after.html | Lifecycle hooks syntax |
  21 | 11 | Operators Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-operators.html | Comparison, logical, arithmetic |
  22 | 12 | Topics Reference | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-ref-topics.html | Topic structure, transitions |
  23 | 13 | Examples | https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-example.html | Complete working examples |
  24 | 14 | Agent DX (CLI) | https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx.html | CLI commands, bundle structure |
  25 
  26 > **URL Prefix Note**: Agent Script docs migrated from `/docs/einstein/genai/guide/ascript-*` (older beta path) to `/docs/ai/agentforce/guide/ascript-*` (current path). If a URL 404s, try swapping the prefix.
  27 
  28 ---
  29 
  30 ## Recipe Repository
  31 
  32 | # | Page | URL | Content |
  33 |---|------|-----|---------|
  34 | 1 | Recipes Overview | https://developer.salesforce.com/sample-apps/agent-script-recipes/getting-started/overview | Getting started guide |
  35 | 2 | GitHub Repository | https://github.com/trailheadapps/agent-script-recipes | Source code, AGENT_SCRIPT.md rules |
  36 | 3 | Hello World | https://developer.salesforce.com/sample-apps/agent-script-recipes/language-essentials/hello-world | Minimal agent example |
  37 | 4 | Action Definitions | https://developer.salesforce.com/sample-apps/agent-script-recipes/action-configuration/action-definitions | Action config patterns |
  38 | 5 | Multi-Topic Navigation | https://developer.salesforce.com/sample-apps/agent-script-recipes/architectural-patterns/multi-topic-navigation | Topic routing patterns |
  39 | 6 | Error Handling | https://developer.salesforce.com/sample-apps/agent-script-recipes/architectural-patterns/error-handling | Error handling patterns |
  40 | 7 | Bidirectional Navigation | https://developer.salesforce.com/sample-apps/agent-script-recipes/architectural-patterns/bidirectional-navigation | Two-way topic transitions |
  41 | 8 | Advanced Input Bindings | https://developer.salesforce.com/sample-apps/agent-script-recipes/action-configuration/advanced-input-bindings | Slot-fill, fixed, variable binding |
  42 
  43 ---
  44 
  45 ## Diagnostic Decision Tree
  46 
  47 When something fails, use this tree to determine which doc page to fetch:
  48 
  49 ```
  50 Error or Ambiguity
  51        │
  52        ├─ Compilation / SyntaxError
  53        │     ├─ Block-level error → Fetch #2 (Blocks Reference)
  54        │     ├─ Expression error  → Fetch #9 (Expressions) + #11 (Operators)
  55        │     └─ Action error      → Fetch #4 (Actions Reference)
  56        │
  57        ├─ Action not executing
  58        │     ├─ Action defined but LLM doesn't pick it → Fetch #4 (Actions) + #6 (Tools)
  59        │     └─ Action target not found               → Fetch #4 (Actions) + #14 (Agent DX)
  60        │
  61        ├─ Variable not updating
  62        │     ├─ Linked var empty     → Fetch #5 (Variables)
  63        │     └─ Mutable not changing → Fetch #5 (Variables) + #8 (Instructions)
  64        │
  65        ├─ Topic transition wrong
  66        │     ├─ Wrong topic selected  → Fetch #12 (Topics) + #7 (Utils)
  67        │     └─ Transition vs delegation confusion → Fetch #6 (Tools) + #12 (Topics)
  68        │
  69        ├─ Lifecycle hook issue
  70        │     └─ before/after_reasoning error → Fetch #10 (Before/After)
  71        │
  72        └─ New / unfamiliar syntax
  73              └─ Start with #1 (Overview), then narrow to specific reference
  74 ```
  75 
  76 ---
  77 
  78 ## Fallback Search Patterns
  79 
  80 When a specific URL 404s or doesn't have the answer:
  81 
  82 ```bash
  83 # Primary search pattern
  84 site:developer.salesforce.com agent script <topic>
  85 
  86 # Recipe search
  87 site:developer.salesforce.com sample-apps agent-script-recipes <topic>
  88 
  89 # GitHub issues (known bugs, community solutions)
  90 site:github.com trailheadapps agent-script-recipes <error message>
  91 
  92 # Salesforce Stack Exchange
  93 site:salesforce.stackexchange.com agent script <topic>
  94 ```
  95 
  96 ---
  97 
  98 ## URL Health Check
  99 
 100 When verifying URLs, use WebFetch to confirm each resolves. If a URL redirects or 404s:
 101 
 102 1. Try swapping the URL prefix (see note above)
 103 2. Use the fallback search pattern
 104 3. If consistently broken, update this file and note the date
 105 
 106 ---
 107 
 108 *Last updated: 2026-02-12*
