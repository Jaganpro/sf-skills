<!-- Parent: sf-ai-agentscript/SKILL.md -->

# Sources & Acknowledgments

| Source | Contribution |
|--------|--------------|
| [trailheadapps/agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) | 20 reference recipes across 4 categories, AGENT_SCRIPT.md rules document, variable patterns, action target catalog |
| Salesforce Official Documentation | Core syntax, API references, deployment guides |
| TDD Validation (this skill) | 13 validation agents confirming current-release syntax compatibility |
| Tribal knowledge interviews | Canvas View bugs, VS Code limitations, credit consumption patterns |
| [agentforce.guide](https://agentforce.guide/) | Unofficial but useful examples (note: some patterns don't compile in current release) |
| @kunello ([PR #20](https://github.com/Jaganpro/sf-skills/pull/20)) | Prompt template `"Input:fieldName"` binding syntax, context-aware description overrides, `{!@actions.X}` instruction reference patterns, callback behavior notes, error pattern catalog |
| [aquivalabs/my-org-butler](https://github.com/aquivalabs/my-org-butler) | Official sources registry pattern, known-issues tracking structure, verification protocol, Builder UI → Agent Script migration guide, self-improvement protocol |

> **⚠️ Note on Feature Validation**: Some patterns from external sources (e.g., `always_expect_input:`) do NOT compile in Winter '26. Action metadata properties (`label:`, `require_user_confirmation:`, etc.) are valid on **action definitions with targets** but NOT on `@utils.transition`. The `before_reasoning:`/`after_reasoning:` lifecycle hooks ARE valid but require **direct content** (no `instructions:` wrapper). This skill documents only patterns that pass TDD validation.
