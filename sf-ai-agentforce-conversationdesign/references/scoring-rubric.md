<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->

# Scoring System (120 Points) — Detailed Criteria

## Category 1: Persona & Tone (15 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Agent role and scope clearly defined | 3 | Name, role, department, target audience documented |
| Tone register appropriate for context | 3 | Casual/neutral/formal selected with justification |
| Personality traits documented | 3 | 3-5 traits with descriptions and behavioral examples |
| Welcome and error messages configured | 3 | Within 800-char limit, brand-aligned, helpful |
| Communication style consistent | 3 | Sentence length, vocabulary level, empathy patterns uniform |

## Category 2: Topic Architecture (20 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Bottom-up design methodology used | 4 | Actions listed first, then grouped into topics |
| Topics are semantically distinct | 4 | Classification descriptions share <30% vocabulary |
| Reasonable topic count (<=10) | 3 | Focused agent with clear scope boundaries |
| Classification descriptions are specific | 3 | Positive phrasing, mutually exclusive, testable |
| Actions properly assigned | 3 | Each action in exactly one topic, <=5 actions per topic |
| Out-of-scope clearly defined | 3 | Explicit list of what the agent does NOT handle |

## Category 3: Instruction Quality (20 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Three-level structure used | 4 | Agent-level, topic-level, and action-level instructions present |
| Positive framing throughout | 4 | "Always do X" not "Don't do Y" pattern |
| Guidance over determinism | 4 | Instructions guide reasoning, not hard-code outcomes |
| No business rules in instructions | 4 | Conditional logic delegated to Flow/Apex |
| Appropriate instruction length | 4 | Agent: 200-500w, Topic: 100-300w, Action: 50-150w |

## Category 4: Dialog Flow Design (15 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Six-phase lifecycle followed | 3 | Greeting -> Classification -> Gathering -> Processing -> Response -> Close |
| Progressive disclosure used | 3 | 2-3 choices max per turn, essentials first |
| Context preserved across turns | 3 | Agent references prior turns, avoids re-asking |
| Error recovery paths defined | 3 | Clarification prompts, disambiguation, graceful fallbacks |
| Conversation endings handled | 3 | Explicit close, summary, follow-up offer |

## Category 5: Utterance Coverage (15 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Happy path utterances (per topic) | 3 | >=5 natural phrasings for primary intent |
| Synonym coverage | 3 | Alternate vocabulary and phrasing styles |
| Edge case utterances | 3 | Ambiguous, multi-intent, misspelled inputs |
| Adversarial inputs tested | 3 | Prompt injection, off-topic, manipulation attempts |
| Out-of-scope utterances defined | 3 | Inputs that should NOT match any topic |

## Category 6: Escalation Design (15 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Escalation triggers defined | 3 | Sentiment, complexity, policy, explicit, safety triggers |
| Priority levels assigned | 3 | P1/P2/P3 with clear criteria |
| Routing rules configured | 3 | Omni-Channel queues, skills, routing model |
| Context handoff specified | 3 | Data passed to human agent (case, history, customer info) |
| Escalation messages crafted | 3 | What agent says during handoff (empathetic, informative) |

## Category 7: Guardrails & Safety (10 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Einstein Trust Layer acknowledged | 2 | Toxicity detection, PII masking understood |
| Topic classification as safety | 2 | Out-of-scope rejection prevents hallucination |
| Instruction-level guardrails | 2 | Explicit limitations in agent instructions |
| PII handling defined | 2 | What data to collect, mask, or refuse |
| Deterministic safety in Flow/Apex | 2 | Hard limits enforced in code, not instructions |

## Category 8: Continuous Improvement (10 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| KPIs defined | 2 | Resolution rate, classification accuracy, CSAT metrics |
| Monitoring plan documented | 2 | What dashboards/reports to watch |
| Iteration cycle defined | 2 | Monitor -> Analyze -> Fix -> Retest -> Deploy |
| Regression testing strategy | 2 | Existing test cases preserved when changing instructions |
| Utterance analysis process | 2 | Regular review of unmatched/misrouted utterances |
