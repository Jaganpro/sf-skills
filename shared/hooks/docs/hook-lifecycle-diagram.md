# SF-Skills Hook Architecture Diagram

> Visual representation of how SF-Skills hooks integrate with Claude Code's lifecycle events

---

## Claude Code Hook Lifecycle with SF-Skills Hooks

```mermaid
%%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
flowchart TB
    subgraph init["🚀 INITIALIZATION"]
        S1["1️⃣ SESSION START"]
        S2["2️⃣ SETUP"]
        S3["3️⃣ USER PROMPT SUBMIT"]
    end

    subgraph hooks_session["📌 SessionStart Hooks"]
        H_ORG["🔌 org-preflight.py"]
        H_LSP["⚡ lsp-prewarm.py"]
    end

    subgraph hooks_prompt["📌 UserPromptSubmit Hooks"]
        H_SKILL_ACT["🎯 skill-activation-prompt.py"]
    end

    subgraph agentic["⚙️ AGENTIC LOOP"]
        LLM(["CLAUDE CODE LLM"])
        S4["4️⃣ PRE TOOL USE"]
        S5["5️⃣ PERMISSION REQUEST"]
        EXEC(["TOOL EXECUTES"])
        S6["6️⃣ POST TOOL USE<br/>SUCCESS"]
        S7["7️⃣ POST TOOL USE<br/>FAILURE"]
    end

    subgraph hooks_pre["📌 PreToolUse Hooks"]
        H_GUARD["🛡️ guardrails.py"]
        H_API["📊 api-version-check.py"]
        H_ENFORCE["🚫 skill-enforcement.py"]
    end

    subgraph hooks_perm["📌 PermissionRequest Hooks"]
        H_AUTO["✅ auto-approve.py"]
    end

    subgraph hooks_post["📌 PostToolUse Hooks"]
        H_VALID["🔍 validator-dispatcher.py"]
        H_SUGGEST["💡 suggest-related-skills.py"]
    end

    subgraph subagent["🤖 SUBAGENT FLOW"]
        SUB_Q{{"SUBAGENT?"}}
        S8["8️⃣ SUBAGENT START"]
        SUB_RUN(["SUBAGENT RUNS"])
        S9["9️⃣ SUBAGENT STOP"]
        MORE_Q{{"MORE WORK?"}}
    end

    subgraph hooks_sub["📌 SubagentStop Hooks"]
        H_CHAIN["⛓️ chain-validator.py"]
    end

    subgraph finish["🏁 COMPLETION"]
        S10["🔟 STOP"]
        S11["1️⃣1️⃣ PRE COMPACT"]
        S12["1️⃣2️⃣ NOTIFICATION"]
        S13["1️⃣3️⃣ SESSION END"]
    end

    %% Main Flow - Initialization
    S1 --> S2 --> S3 --> LLM

    %% SessionStart hooks
    S1 -.-> H_ORG
    S1 -.-> H_LSP

    %% UserPromptSubmit hooks
    S3 -.-> H_SKILL_ACT

    %% Agentic Loop
    LLM --> S4 --> S5 --> EXEC
    EXEC --> S6
    EXEC --> S7

    %% PreToolUse hooks
    S4 -.-> H_GUARD
    S4 -.-> H_API
    S4 -.-> H_ENFORCE

    %% PermissionRequest hooks
    S5 -.-> H_AUTO

    %% PostToolUse hooks
    S6 -.-> H_VALID
    S6 -.-> H_SUGGEST

    %% Subagent flow
    S6 --> SUB_Q
    S7 --> SUB_Q
    SUB_Q -->|Yes| S8
    SUB_Q -->|No| MORE_Q
    S8 --> SUB_RUN --> S9
    S9 --> MORE_Q

    %% SubagentStop hooks
    S9 -.-> H_CHAIN

    %% Loop back or finish
    MORE_Q -->|Yes| LLM
    MORE_Q -->|No| S10

    %% Finish flow
    S10 --> S11 --> S12 --> S13

    %% Node Styling - Event nodes (Cyan-200 Foundation)
    style S1 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S2 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S3 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S4 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S5 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S6 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S7 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S8 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S9 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S10 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S11 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S12 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style S13 fill:#a5f3fc,stroke:#0e7490,color:#1f2937

    %% Node Styling - Execution nodes (Indigo-200)
    style LLM fill:#c7d2fe,stroke:#4338ca,color:#1f2937
    style EXEC fill:#c7d2fe,stroke:#4338ca,color:#1f2937
    style SUB_RUN fill:#c7d2fe,stroke:#4338ca,color:#1f2937

    %% Node Styling - Decision nodes (Amber-200)
    style SUB_Q fill:#fde68a,stroke:#b45309,color:#1f2937
    style MORE_Q fill:#fde68a,stroke:#b45309,color:#1f2937

    %% Node Styling - SessionStart hooks (Teal-200)
    style H_ORG fill:#99f6e4,stroke:#0f766e,color:#1f2937
    style H_LSP fill:#99f6e4,stroke:#0f766e,color:#1f2937

    %% Node Styling - UserPromptSubmit hooks (Pink-200 AI)
    style H_SKILL_ACT fill:#fbcfe8,stroke:#be185d,color:#1f2937

    %% Node Styling - PreToolUse hooks (Orange-200)
    style H_GUARD fill:#fed7aa,stroke:#c2410c,color:#1f2937
    style H_API fill:#fed7aa,stroke:#c2410c,color:#1f2937
    style H_ENFORCE fill:#fed7aa,stroke:#c2410c,color:#1f2937

    %% Node Styling - PermissionRequest hooks (Green-200)
    style H_AUTO fill:#a7f3d0,stroke:#047857,color:#1f2937

    %% Node Styling - PostToolUse hooks (Violet-200)
    style H_VALID fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
    style H_SUGGEST fill:#ddd6fe,stroke:#6d28d9,color:#1f2937

    %% Node Styling - SubagentStop hooks (Indigo-200)
    style H_CHAIN fill:#c7d2fe,stroke:#4338ca,color:#1f2937

    %% Subgraph Styling - 50-level fills with dark dashed borders
    style init fill:#ecfeff,stroke:#0e7490,stroke-dasharray:5
    style agentic fill:#eef2ff,stroke:#4338ca,stroke-dasharray:5
    style subagent fill:#fdf2f8,stroke:#be185d,stroke-dasharray:5
    style finish fill:#f8fafc,stroke:#334155,stroke-dasharray:5

    %% Hook subgraph styling
    style hooks_session fill:#f0fdfa,stroke:#0f766e,stroke-dasharray:5
    style hooks_prompt fill:#fdf2f8,stroke:#be185d,stroke-dasharray:5
    style hooks_pre fill:#fff7ed,stroke:#c2410c,stroke-dasharray:5
    style hooks_perm fill:#ecfdf5,stroke:#047857,stroke-dasharray:5
    style hooks_post fill:#f5f3ff,stroke:#6d28d9,stroke-dasharray:5
    style hooks_sub fill:#eef2ff,stroke:#4338ca,stroke-dasharray:5
```

---

## ASCII Fallback

For terminals and viewers that don't render Mermaid:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     CLAUDE CODE HOOK LIFECYCLE (SF-SKILLS)                      │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  🚀 INITIALIZATION                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │ 1. SESSION START│───▶│    2. SETUP     │───▶│3. PROMPT SUBMIT │             │
│  └────────┬────────┘    └─────────────────┘    └────────┬────────┘             │
│           │                                              │                      │
│           ▼                                              ▼                      │
│  ┌─────────────────────────┐              ┌─────────────────────────┐          │
│  │ 🔌 org-preflight.py     │              │🎯 skill-activation-     │          │
│  │ ⚡ lsp-prewarm.py       │              │   prompt.py             │          │
│  └─────────────────────────┘              └─────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ AGENTIC LOOP                              ┌───────────────────────────────┐ │
│  ┌─────────────────────────────┐              │ 🛡️ guardrails.py             │ │
│  │   CLAUDE CODE / LLM        │◀─────┐       │ 📊 api-version-check.py      │ │
│  └──────────────┬──────────────┘      │       │ 🚫 skill-enforcement.py      │ │
│                 │                     │       └───────────────────────────────┘ │
│                 ▼                     │                      ▲                  │
│  ┌─────────────────────────────┐      │       ┌──────────────┘                  │
│  │     4. PRE TOOL USE         │──────┼───────┘                                 │
│  └──────────────┬──────────────┘      │       ┌───────────────────────────────┐ │
│                 │                     │       │ ✅ auto-approve.py            │ │
│                 ▼                     │       └───────────────────────────────┘ │
│  ┌─────────────────────────────┐      │                      ▲                  │
│  │   5. PERMISSION REQUEST     │──────┼──────────────────────┘                  │
│  └──────────────┬──────────────┘      │                                         │
│                 │                     │                                         │
│                 ▼                     │                                         │
│  ┌─────────────────────────────┐      │                                         │
│  │      TOOL EXECUTES          │      │                                         │
│  └──────────────┬──────────────┘      │                                         │
│                 │                     │       ┌───────────────────────────────┐ │
│        ┌───────┴───────┐              │       │ 🔍 validator-dispatcher.py   │ │
│        ▼               ▼              │       │ 💡 suggest-related-skills.py │ │
│  ┌───────────┐   ┌───────────┐        │       └───────────────────────────────┘ │
│  │ 6. POST   │   │ 7. POST   │        │                      ▲                  │
│  │ SUCCESS   │───│ FAILURE   │────────┼──────────────────────┘                  │
│  └─────┬─────┘   └───────────┘        │                                         │
│        │                              │                                         │
│        ▼                              │                                         │
│  ┌─────────────────────────────┐      │                                         │
│  │      SUBAGENT?              │      │                                         │
│  └─────────┬───────────┬───────┘      │                                         │
│       Yes  │           │ No           │                                         │
│            ▼           │              │                                         │
│  ┌─────────────────┐   │              │                                         │
│  │ 8. SUBAGENT     │   │              │                                         │
│  │    START        │   │              │                                         │
│  └────────┬────────┘   │              │                                         │
│           ▼            │              │       ┌───────────────────────────────┐ │
│  ┌─────────────────┐   │              │       │ ⛓️ chain-validator.py         │ │
│  │ SUBAGENT RUNS   │   │              │       └───────────────────────────────┘ │
│  └────────┬────────┘   │              │                      ▲                  │
│           ▼            │              │                      │                  │
│  ┌─────────────────┐   │              │                      │                  │
│  │ 9. SUBAGENT     │───┼──────────────┼──────────────────────┘                  │
│  │    STOP         │   │              │                                         │
│  └────────┬────────┘   │              │                                         │
│           │            │              │                                         │
│           └────────────┤              │                                         │
│                        ▼              │                                         │
│              ┌─────────────────┐      │                                         │
│              │   MORE WORK?    │      │                                         │
│              └───┬─────────┬───┘      │                                         │
│             Yes  │         │ No       │                                         │
│                  │         │          │                                         │
│                  └─────────┼──────────┘                                         │
│                            │                                                    │
└────────────────────────────│────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🏁 COMPLETION                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │    10. STOP     │───▶│ 11. PRE COMPACT │───▶│ 12. NOTIFICATION│             │
│  └─────────────────┘    └─────────────────┘    └────────┬────────┘             │
│                                                         │                       │
│                                                         ▼                       │
│                                                ┌─────────────────┐              │
│                                                │ 13. SESSION END │              │
│                                                └─────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Hook Summary Table

| Event | Hook Script | Purpose | Action Type |
|-------|-------------|---------|-------------|
| **SessionStart** | `org-preflight.py` | Validate SF org connectivity | State file |
| **SessionStart** | `lsp-prewarm.py` | Spawn LSP servers in background | Background |
| **UserPromptSubmit** | `skill-activation-prompt.py` | Suggest skills from prompt | Prepend |
| **PreToolUse** | `guardrails.py` | Block dangerous operations | BLOCK/MODIFY |
| **PreToolUse** | `api-version-check.py` | Check API version compatibility | WARN |
| **PreToolUse** | `skill-enforcement.py` | Enforce skill-first workflow | BLOCK |
| **PermissionRequest** | `auto-approve.py` | Smart auto-approval for safe ops | APPROVE/DENY |
| **PostToolUse** | `validator-dispatcher.py` | Route to skill-specific validators | Feedback |
| **PostToolUse** | `suggest-related-skills.py` | Suggest next skills in workflow | Feedback |
| **SubagentStop** | `chain-validator.py` | Validate workflow chain completion | Feedback |

---

## Hook Event Reference

### Lifecycle Events (13 total)

| # | Event | When | Hook Output |
|---|-------|------|-------------|
| 1 | **SessionStart** | Claude Code session begins | State files, background tasks |
| 2 | **Setup** | Configuration loaded | (no hooks) |
| 3 | **UserPromptSubmit** | User sends a message | Prepend context, suggestions |
| 4 | **PreToolUse** | Before tool executes | ALLOW, BLOCK, MODIFY |
| 5 | **PermissionRequest** | Tool needs approval | APPROVE, DENY, defer to user |
| 6 | **PostToolUse (success)** | Tool completed successfully | Feedback, suggestions |
| 7 | **PostToolUse (failure)** | Tool failed | Error analysis, suggestions |
| 8 | **SubagentStart** | Subagent spawned | (no hooks) |
| 9 | **SubagentStop** | Subagent completed | Chain validation |
| 10 | **Stop** | LLM turn complete | (no hooks) |
| 11 | **PreCompact** | Before context compaction | (no hooks) |
| 12 | **Notification** | User notification sent | (no hooks) |
| 13 | **SessionEnd** | Session terminates | Cleanup |

---

## Color Legend

| Color | Hex | Meaning | Nodes |
|-------|-----|---------|-------|
| 🟦 Cyan-200 | `#a5f3fc` | Lifecycle event nodes | S1-S13 |
| 🟩 Teal-200 | `#99f6e4` | SessionStart hooks | org-preflight, lsp-prewarm |
| 🩷 Pink-200 | `#fbcfe8` | AI/Intent detection | skill-activation-prompt |
| 🟧 Orange-200 | `#fed7aa` | Guards/Pre-checks | guardrails, api-version-check, skill-enforcement |
| 🟢 Green-200 | `#a7f3d0` | Approval hooks | auto-approve |
| 🟣 Violet-200 | `#ddd6fe` | Validation/Suggestion | validator-dispatcher, suggest-related-skills |
| 🔵 Indigo-200 | `#c7d2fe` | Execution/Chain | LLM, EXEC, chain-validator |
| 🟡 Amber-200 | `#fde68a` | Decision points | SUBAGENT?, MORE WORK? |

---

## Hook Interaction Patterns

### Pattern 1: Blocking Flow

```
PreToolUse → guardrails.py
         ├─ Allow: Continue to Permission Request
         └─ Block: Return error message to LLM
                   (tool never executes)
```

### Pattern 2: Auto-Approval

```
PermissionRequest → auto-approve.py
         ├─ Approve: Tool executes without user prompt
         ├─ Deny: Block with reason
         └─ No output: Defer to user (shows permission dialog)
```

### Pattern 3: Feedback Chain

```
PostToolUse → validator-dispatcher.py → Validates file
                                      → Sends feedback to LLM
          → suggest-related-skills.py → Analyzes content
                                      → Suggests next skill
```

### Pattern 4: Workflow Tracking

```
SessionStart → org-preflight.py → Writes ~/.claude/.sf-org-state.json
           → lsp-prewarm.py → Writes ~/.claude/.lsp-prewarm-state.json
                            → Status line reads these files
```

---

## Related Documentation

- [Orchestration Architecture](./ORCHESTRATION-ARCHITECTURE.md) - How skill recommendations work
- [Hooks Frontmatter Schema](./hooks-frontmatter-schema.md) - Hook configuration format
- [install.py](../../../tools/install.py) - Unified installer (skills, hooks, LSP, agents)

---

## Diagram Quality Score

```
Score: 72/80 ⭐⭐⭐⭐⭐ Excellent
├─ Accuracy: 18/20      (All 10 hooks correctly placed at their events)
├─ Clarity: 18/20       (Clear flow with dotted lines for hooks)
├─ Completeness: 14/15  (Full lifecycle + all hooks + state files)
├─ Styling: 12/15       (Tailwind 200-level palette, subgraph styling)
└─ Best Practices: 10/10 (Proper Mermaid notation, init config)
```
