---
name: sf-ai-agentforce-conversationdesign
description: >
  Conversation design skill for Salesforce Agentforce. Generates persona
  documents, topic architectures, instruction sets, utterance libraries,
  escalation matrices, and guardrail configurations. Validates existing
  agents against conversation design best practices with 120-point scoring.
license: MIT
compatibility: "Agentforce license, API v65.0+, Einstein Agent runtime"
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
  scoring: "120 points across 8 categories"
  last_validated: "2026-02-07"
  validation_status: "PASS"
---

# SF-AI-Agentforce-ConversationDesign Skill

> **"Users don't fail conversations — conversations fail users."**

Conversation design is the discipline of crafting agent interactions that feel natural, resolve issues efficiently, and gracefully handle the unexpected. This skill brings structured conversation design methodology to Salesforce Agentforce, combining industry frameworks (Google, IBM, PatternFly) with Salesforce-specific implementation patterns.

---

## ⚡ Quick Start

**New agent?** Start here:
1. Design your persona → [Persona Design Guide](docs/persona-design-guide.md)
2. Architect your topics → [Topic Architecture Guide](docs/topic-architecture-guide.md)
3. Write instructions → [Instruction Writing Guide](docs/instruction-writing-guide.md)
4. Score your design → [Quality Scorecard](templates/quality-scorecard.md)

**Existing agent needs improvement?** Start here:
1. Run the [Quality Scorecard](templates/quality-scorecard.md) assessment
2. Review [Anti-Patterns](resources/anti-patterns.md) for quick wins
3. Build an [Improvement Plan](templates/improvement-plan.md)

---

## 📚 Document Map

### Tier 1 — Start Here
| Document | Purpose |
|----------|---------|
| **This file (SKILL.md)** | Scoring rubric, methodology overview, core principles |
| [README.md](README.md) | Quick start, prerequisites, getting started |

### Tier 1.5 — Reference Guides (Extracted)
| Document | Purpose |
|----------|---------|
| [Scoring Rubric](references/scoring-rubric.md) | Full 8-category detailed criteria tables |
| [Quality Assessment](references/quality-assessment.md) | Assessment process + quick health check |
| [Continuous Improvement](references/continuous-improvement.md) | Iteration cycle, KPIs, utterance analysis |

### Tier 2 — Design Guides
| Document | Purpose |
|----------|---------|
| [Persona Design Guide](docs/persona-design-guide.md) | How to define agent personality, tone, and communication style |
| [Topic Architecture Guide](docs/topic-architecture-guide.md) | Bottom-up topic design, classification descriptions, scope boundaries |
| [Instruction Writing Guide](docs/instruction-writing-guide.md) | Three-level instruction framework with do's, don'ts, and examples |

### Tier 3 — Reference Resources
| Document | Purpose |
|----------|---------|
| [Conversation Patterns](resources/conversation-patterns.md) | IBM's 5 patterns mapped to Agentforce implementation |
| [Industry Frameworks](resources/industry-frameworks.md) | Google, IBM, PatternFly, Salesforce framework mappings |
| [Anti-Patterns](resources/anti-patterns.md) | Common mistakes with examples and fixes |
| [Guardrail Hierarchy](resources/guardrail-hierarchy.md) | Four-layer guardrail model for safety |
| [Escalation Patterns](resources/escalation-patterns.md) | Trigger catalog and Omni-Channel routing |
| [Quality Metrics](resources/quality-metrics.md) | KPI definitions, benchmarks, measurement methods |

### Tier 4 — Templates & Examples
| Document | Purpose |
|----------|---------|
| [Persona Document](templates/persona-document.md) | Fill-in persona template |
| [Topic Architecture](templates/topic-architecture.md) | Topic mapping worksheet |
| [Utterance Library](templates/utterance-library.csv) | Structured utterance collection template |
| [Escalation Matrix](templates/escalation-matrix.md) | Escalation decision matrix |
| [Quality Scorecard](templates/quality-scorecard.md) | 120-point assessment template |
| [Improvement Plan](templates/improvement-plan.md) | Prioritized improvement template |
| [Service Agent Persona](examples/service-agent-persona.md) | Example: SaaS customer service persona |
| [Retail Topic Architecture](examples/retail-topic-architecture.md) | Example: retail agent topic hierarchy |
| [Healthcare Escalation](examples/healthcare-escalation.md) | Example: healthcare escalation matrix |

---

## 🏆 Scoring System (120 Points)

> See [references/scoring-rubric.md](references/scoring-rubric.md) for the full per-criterion breakdown of all 8 categories.

### Category Summary

| # | Category | Points | Weight |
|---|----------|--------|--------|
| 1 | Persona & Tone | 15 | 12.5% |
| 2 | Topic Architecture | 20 | 16.7% |
| 3 | Instruction Quality | 20 | 16.7% |
| 4 | Dialog Flow Design | 15 | 12.5% |
| 5 | Utterance Coverage | 15 | 12.5% |
| 6 | Escalation Design | 15 | 12.5% |
| 7 | Guardrails & Safety | 10 | 8.3% |
| 8 | Continuous Improvement | 10 | 8.3% |
| | **TOTAL** | **120** | **100%** |

### Grade Scale

| Grade | Score Range | Description |
|-------|------------|-------------|
| **A** | 108-120 | Production-ready, exceptional design |
| **B** | 96-107 | Good design, minor gaps |
| **C** | 84-95 | Adequate, needs targeted improvements |
| **D** | 72-83 | Significant gaps, not production-ready |
| **F** | <72 | Major redesign required |

---

## 🎭 Persona Design

A persona defines your agent's personality, communication style, and behavioral constraints — the foundation for consistent, brand-aligned interactions.

### Persona Components

1. **Identity** — Name, role, department, target audience
2. **Tone Register** — Casual, neutral, or formal (Agentforce setting)
3. **Personality Traits** — 3-5 traits that shape response style
4. **Communication Style** — Sentence length, vocabulary level, empathy patterns
5. **Limitations** — What the agent explicitly will not do
6. **Messages** — Welcome message and error/fallback message (<=800 chars each)

### Salesforce Implementation

```
Agent Builder → Agent Settings → Instructions (Agent-Level)
Agent Builder → Agent Settings → Tone (Casual/Neutral/Formal)
Agent Builder → Channels → Welcome Message / Error Message
```

The persona lives primarily in **agent-level instructions**. Write them like training a new employee on Day 1 — focus on who they are and how they communicate, not on specific task procedures.

> **Deep Dive:** [Persona Design Guide](docs/persona-design-guide.md) | **Template:** [Persona Document](templates/persona-document.md) | **Example:** [Service Agent Persona](examples/service-agent-persona.md)

---

## 🏗️ Topic Architecture

Topics group related actions under classification descriptions for routing. Use **bottom-up design**: list all actions → group by user intent → write classification descriptions → test for semantic distinctness.

### Architecture Rules

| Rule | Guideline | Rationale |
|------|-----------|-----------|
| Topic count | <=10 per agent | More topics = more classification ambiguity |
| Actions per topic | <=5 per topic | Keeps topics focused and testable |
| Classification overlap | <30% shared vocabulary | Prevents misrouting between similar topics |
| Scope boundaries | Explicit out-of-scope list | Prevents hallucination on unknown intents |

### Classification Descriptions

The single most important text in your agent design — they determine routing accuracy.

```
✅ GOOD: "This topic handles questions about existing order status, including
tracking information, estimated delivery dates, and order modification
requests. It does NOT handle new order placement or returns."

❌ BAD: "Order stuff"
```

> **Test:** Can you read two descriptions and immediately tell which utterance belongs where?

> **Deep Dive:** [Topic Architecture Guide](docs/topic-architecture-guide.md) | **Template:** [Topic Architecture](templates/topic-architecture.md) | **Example:** [Retail Topic Architecture](examples/retail-topic-architecture.md)

---

## ✍️ Instruction Writing

Instructions operate at three levels: **Agent-level** (persona, global rules, 200-500w), **Topic-level** (workflow logic, 100-300w), **Action-level** (when/how to invoke, 50-150w).

### Core Principles

1. **Guidance over determinism** — Guide reasoning, don't hard-code every decision. "Prioritize empathy and escalate if unresolved within 2-3 exchanges" vs scripting every anger keyword.
2. **Positive framing** — "Always verify identity before accessing account details" not "Don't ever access without verifying."
3. **Business principles, not decision trees** — If your instruction contains `if...then...else` with thresholds, it belongs in Flow/Apex.
4. **Knowledge over hard-coding** — Use Knowledge actions (RAG) for policies, don't inline policy text in instructions.

> **Deep Dive:** [Instruction Writing Guide](docs/instruction-writing-guide.md)

---

## 🔄 Dialog Flow Patterns

Every conversation follows a **six-phase lifecycle**: Greeting → Classification → Gathering → Processing → Response → Close.

**Key design rules:**
- **Progressive disclosure**: Max 2-3 choices per turn. If more options exist, ask a qualifying question first.
- **Context preservation**: Reference prior turns, avoid re-asking for information already provided.
- **Error recovery**: Define clarification prompts, disambiguation paths, and graceful fallbacks for every phase.
- **Explicit closing**: Summarize what was accomplished, offer follow-up, farewell appropriate to tone.

---

## 📝 Utterance Design

Utterances are test cases for your topic architecture — they validate that classification descriptions route correctly.

### Categories & Targets

| Category | Purpose | Target per Topic |
|----------|---------|-----------------|
| **Happy Path** | Primary intent, clear phrasing | >=5 |
| **Synonym** | Alternate vocabulary | >=3 |
| **Edge Case** | Ambiguous, multi-intent | >=2 |
| **Adversarial** | Injection, manipulation (global) | >=5 |
| **Out-of-Scope** | Should NOT match (global) | >=5 |

**Process:** Start with real data (CRM cases, chat logs) → brainstorm synonyms → add edge cases → include adversarial → test in Testing Center → iterate on failures.

> **Template:** [Utterance Library](templates/utterance-library.csv)

---

## 🚨 Escalation Design

Escalation is not failure — it's a safety net ensuring customers always reach resolution.

### Trigger Catalog

| Trigger Type | Condition | Priority |
|-------------|-----------|----------|
| **Explicit** | Customer requests human agent | P1 |
| **Safety** | Self-harm, threats, emergency, legal | P1 |
| **Sentiment** | Customer frustration or anger | P2 |
| **Complexity** | >6 turns without resolution | P2 |
| **Policy** | Request exceeds agent authority | P2 |
| **Technical** | Action failure, system error | P3 |

When escalating, pass: conversation transcript, customer identity, issue summary, actions taken, and escalation reason. Agentforce provides a pre-built Escalation Topic that routes via Omni-Channel.

> **Deep Dive:** [Escalation Patterns](resources/escalation-patterns.md) | **Template:** [Escalation Matrix](templates/escalation-matrix.md)

---

## 🛡️ Guardrails & Safety

Safety operates through four layers: **Einstein Trust Layer** (platform — toxicity detection, PII masking, automatic), **Topic Classification** (scope boundaries as first defense), **Instructions** (behavioral constraints — "never provide legal/medical advice"), **Flow/Apex** (deterministic business rule enforcement).

> **Critical Rule:** Never rely on instructions alone for safety-critical decisions. Instructions are probabilistic. Financial limits, compliance checks, and approval gates MUST be in Flow or Apex.

> **Deep Dive:** [Guardrail Hierarchy](resources/guardrail-hierarchy.md)

---

## 📊 Quality Assessment & Continuous Improvement

> See [references/quality-assessment.md](references/quality-assessment.md) for the full assessment process and 5-question quick health check.

> See [references/continuous-improvement.md](references/continuous-improvement.md) for the Monitor → Analyze → Fix → Retest → Deploy iteration cycle, KPI targets, and utterance analysis process.

---

## ⚠️ Anti-Patterns

| # | Anti-Pattern | Impact | Fix |
|---|-------------|--------|-----|
| 1 | **Negative instructions** | Confuses LLM reasoning | Reframe positively |
| 2 | **Over-constraining** | Rigid, brittle responses | Use guiding principles |
| 3 | **Business rules in instructions** | Inconsistent enforcement | Move to Flow/Apex |
| 4 | **Monolithic topics** | Poor classification accuracy | Split into focused topics |
| 5 | **Overlapping classifications** | Misrouting | Make descriptions distinct |
| 6 | **Missing escalation paths** | Dead-end conversations | Define triggers for all failure modes |
| 7 | **No utterance testing** | Untested classification | Build utterance library |
| 8 | **Hard-coded policies** | Stale information | Use Knowledge actions |
| 9 | **Ignoring context** | Repetitive re-asking | Leverage conversation state |
| 10 | **Happy-path-only testing** | Fragile in production | Test edge cases and adversarial |

> **Deep Dive:** [Anti-Patterns](resources/anti-patterns.md) — Full examples with before/after fixes.

---

## 🔗 Chain Integration

This skill is the **first step** in the Agentforce development chain:

| From This Skill | To Skill | What's Handed Off |
|-----------------|----------|-------------------|
| Topic architecture | sf-ai-agentscript | Topic names, actions, classification descriptions |
| Instruction sets | sf-ai-agentscript | Three-level instructions for agent script |
| Utterance library | sf-ai-agentforce-testing | Test cases for multi-turn testing |
| Escalation matrix | sf-flow | Escalation flow logic |
| Action definitions | sf-apex / sf-flow | Action implementation requirements |

---

## 📎 Credits & References

- Google Conversation Design Guidelines
- IBM Natural Conversation Framework
- Red Hat PatternFly AI Design System
- Salesforce Conversational AI Design Guide
- Salesforce Architect: Agentic Patterns & Taxonomy

See [CREDITS.md](CREDITS.md) for full attribution.
