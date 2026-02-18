<!-- Parent: sf-ai-agentscript/SKILL.md -->

# Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.2.0 | 2026-02-17 | **TDD Validation v2.2.0 — Action metadata properties validated**: 2 new agents (Val_Action_Meta_Props, Val_IO_Meta_Props). Corrected "Features NOT Valid" table → "Feature Validity by Context" — properties ARE valid on action definitions with targets, only invalid on `@utils.transition`. Validated 9 properties: `label` (action/topic/I/O), `require_user_confirmation`, `include_in_progress_indicator`, `progress_indicator_message`, `is_required`, `is_user_input`, `is_displayable`, `is_used_by_planner`. Root cause: v1.3.0 only tested on `@utils.transition`, never on target-backed actions. Added "Action I/O Metadata Properties" section with complete property tables. Clarified reserved field names (reserved as variable names, valid as I/O metadata properties). Updated actions-reference.md (label property, Input Properties table, Output Properties expansion). Updated known-issues.md Issue 6 (compiles on target-backed actions). Updated VALIDATION.md Tier 4 + findings. Updated syntax-reference.md with Action Metadata Properties subsection. 24 validation agents total. |
| 2.0.0 | 2026-02-16 | **Production learnings audit**: Fixed `<>` operator references in 3 files. Fixed config block field names. Removed false `label:` claims. Added 3 new known issues (I/O schemas, connections block, EinsteinAgentApiChannel). Added Two-Level Action System section. |
| 1.9.0 | 2026-02-14 | **TDD v1.9.0 (16/16 PASS)**: 3 new agents. TDD disproved `else:` + nested `if`. `<>` not valid. Multiple `available when` IS valid. |
| 1.8.0 | 2026-02-12 | **Gap analysis audit**: Added official-sources.md, known-issues.md, migration-guide.md. Verification Protocol + Self-Improvement. |
| 1.7.0 | 2026-02-09 | **CRITICAL FIX**: `apex://` works directly, GenAiFunction NOT needed for Agent Script. Rewrote action sections. |
| 1.6.0 | 2026-02-07 | Content migration from former sf-ai-agentforce-legacy. Created actions-reference.md (602 lines). |
| 1.5.0 | 2026-02-06 | Action patterns & prompt template docs (from @kunello PR #20). |
| 1.3.0 | 2026-01-20 | Lifecycle hooks validated. Features NOT Valid section (corrected in v2.2.0). |
| 1.2.0 | 2026-01-20 | Gap analysis vs agent-script-recipes. Expanded Action Target Protocols. |
| 1.1.0 | 2026-01-20 | "Ultimate Guide" tribal knowledge integration. |
| 1.0.x | 2026-01 | Initial release through progressive testing validation. |
