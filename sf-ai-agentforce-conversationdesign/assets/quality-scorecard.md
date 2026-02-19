# Agent Quality Scorecard (120 Points)

## Agent Metadata

**Agent Name:** {{AGENT_NAME}}
**Version:** {{VERSION}}
**Assessment Date:** {{DATE}}
**Assessor:** {{ASSESSOR}}
**Assessment Type:** {{TYPE}} <!-- Initial / Iteration / Production Review -->

---

## Scoring Summary

| Category | Points Available | Points Earned | Percentage |
|----------|------------------|---------------|------------|
| Persona & Tone | 15 | {{PERSONA_SCORE}} | {{PERSONA_PCT}}% |
| Topic Architecture | 20 | {{TOPIC_SCORE}} | {{TOPIC_PCT}}% |
| Instruction Quality | 20 | {{INSTRUCTION_SCORE}} | {{INSTRUCTION_PCT}}% |
| Dialog Flow Design | 15 | {{DIALOG_SCORE}} | {{DIALOG_PCT}}% |
| Utterance Coverage | 15 | {{UTTERANCE_SCORE}} | {{UTTERANCE_PCT}}% |
| Escalation Design | 15 | {{ESCALATION_SCORE}} | {{ESCALATION_PCT}}% |
| Guardrails & Safety | 10 | {{GUARDRAILS_SCORE}} | {{GUARDRAILS_PCT}}% |
| Continuous Improvement | 10 | {{IMPROVEMENT_SCORE}} | {{IMPROVEMENT_PCT}}% |
| **TOTAL** | **120** | **{{TOTAL_SCORE}}** | **{{TOTAL_PCT}}%** |

**Overall Grade:** {{GRADE}} <!-- A / B / C / D / F -->

---

## Category 1: Persona & Tone (15 points)

### 1.1 Persona Definition Clarity (3 points)
**Criteria:** Agent has well-defined role, personality traits, and target audience.

**Score:** {{SCORE_1_1}}/3
- [ ] 3 pts: Complete persona with role, 3+ traits, audience demographics
- [ ] 2 pts: Partial persona (missing audience or <3 traits)
- [ ] 1 pt: Minimal persona (role only, no traits)
- [ ] 0 pts: No defined persona

**Notes:** {{NOTES_1_1}}

---

### 1.2 Tone Register Appropriateness (3 points)
**Criteria:** Tone (casual/neutral/formal) matches audience and channel.

**Score:** {{SCORE_1_2}}/3
- [ ] 3 pts: Tone perfectly aligned with audience; justified in docs
- [ ] 2 pts: Tone mostly appropriate; minor mismatches
- [ ] 1 pt: Tone conflicts with audience (e.g., casual for legal)
- [ ] 0 pts: No consistent tone

**Notes:** {{NOTES_1_2}}

---

### 1.3 Tone Consistency Across Interactions (3 points)
**Criteria:** Agent maintains consistent tone in all messages (welcome, error, action responses).

**Score:** {{SCORE_1_3}}/3
- [ ] 3 pts: 100% tone consistency; no register shifts
- [ ] 2 pts: Mostly consistent; 1-2 minor shifts
- [ ] 1 pt: Frequent shifts (formal → casual mid-conversation)
- [ ] 0 pts: No consistency; tone varies randomly

**Notes:** {{NOTES_1_3}}

---

### 1.4 Empathy and User-Centricity (3 points)
**Criteria:** Agent uses acknowledgment phrases, reassurance, and handles user frustration gracefully.

**Score:** {{SCORE_1_4}}/3
- [ ] 3 pts: Frequent empathy markers; adapts to sentiment
- [ ] 2 pts: Some empathy; doesn't adapt to frustration
- [ ] 1 pt: Rare empathy; robotic tone
- [ ] 0 pts: No empathy; defensive or dismissive

**Notes:** {{NOTES_1_4}}

---

### 1.5 Welcome/Error Message Quality (3 points)
**Criteria:** Welcome message sets expectations; error message maintains helpfulness.

**Score:** {{SCORE_1_5}}/3
- [ ] 3 pts: Both ≤800 chars; clear, helpful, on-brand
- [ ] 2 pts: One message suboptimal (too long, unclear)
- [ ] 1 pt: Both messages poor quality
- [ ] 0 pts: Missing or non-functional messages

**Notes:** {{NOTES_1_5}}

---

**Category 1 Total:** {{PERSONA_SCORE}}/15

---

## Category 2: Topic Architecture (20 points)

### 2.1 Topic Count and Granularity (4 points)
**Criteria:** Agent has 3-7 topics; not too broad or too narrow.

**Score:** {{SCORE_2_1}}/4
- [ ] 4 pts: 3-7 topics; optimal granularity
- [ ] 3 pts: 2 or 8 topics; slight granularity issues
- [ ] 2 pts: 1 or 9-10 topics; poor granularity
- [ ] 0 pts: >10 topics or 0 topics

**Notes:** {{NOTES_2_1}}

---

### 2.2 Classification Description Quality (4 points)
**Criteria:** Descriptions use user language; enable accurate routing.

**Score:** {{SCORE_2_2}}/4
- [ ] 4 pts: All user-centric; no jargon; clear boundaries
- [ ] 3 pts: Mostly user-centric; minor jargon
- [ ] 2 pts: Technical descriptions (mentions Apex, objects)
- [ ] 0 pts: Missing or incomprehensible descriptions

**Notes:** {{NOTES_2_2}}

---

### 2.3 Topic Semantic Distinctness (4 points)
**Criteria:** Topics have <40% overlap; minimal confusable utterances.

**Score:** {{SCORE_2_3}}/4
- [ ] 4 pts: All topics <40% overlap; clear boundaries
- [ ] 3 pts: One pair 40-60% overlap
- [ ] 2 pts: Multiple pairs 40-60% overlap
- [ ] 0 pts: >60% overlap between topics

**Notes:** {{NOTES_2_3}}

---

### 2.4 Action Distribution Across Topics (4 points)
**Criteria:** Each topic has 2-5 actions; no single-action topics.

**Score:** {{SCORE_2_4}}/4
- [ ] 4 pts: All topics have 2-5 actions
- [ ] 3 pts: One topic has 1 or 6+ actions
- [ ] 2 pts: Multiple topics imbalanced
- [ ] 0 pts: Most topics have 1 action or >6 actions

**Notes:** {{NOTES_2_4}}

---

### 2.5 Global Out-of-Scope Definition (4 points)
**Criteria:** Agent has explicit out-of-scope list with redirects.

**Score:** {{SCORE_2_5}}/4
- [ ] 4 pts: 3+ out-of-scope items; clear redirects
- [ ] 3 pts: 1-2 items; partial redirects
- [ ] 2 pts: Implicit out-of-scope (not documented)
- [ ] 0 pts: No out-of-scope definition

**Notes:** {{NOTES_2_5}}

---

**Category 2 Total:** {{TOPIC_SCORE}}/20

---

## Category 3: Instruction Quality (20 points)

### 3.1 Agent-Level Instructions Completeness (5 points)
**Criteria:** Instructions cover role, scope, tone, escalation triggers, safety.

**Score:** {{SCORE_3_1}}/5
- [ ] 5 pts: All elements present; clear and actionable
- [ ] 4 pts: Missing one element
- [ ] 3 pts: Missing 2 elements
- [ ] 2 pts: Missing 3+ elements
- [ ] 0 pts: No agent-level instructions

**Notes:** {{NOTES_3_1}}

---

### 3.2 Topic-Level Instructions Specificity (5 points)
**Criteria:** Each topic has 2-5 sentences with action sequencing, data requirements, error handling.

**Score:** {{SCORE_3_2}}/5
- [ ] 5 pts: All topics have specific, actionable instructions
- [ ] 4 pts: Most topics have instructions; 1-2 generic
- [ ] 3 pts: Half of topics have quality instructions
- [ ] 2 pts: Most instructions are generic or missing
- [ ] 0 pts: No topic-level instructions

**Notes:** {{NOTES_3_2}}

---

### 3.3 Action-Level Instructions Clarity (5 points)
**Criteria:** Actions have preconditions, required inputs, expected outputs.

**Score:** {{SCORE_3_3}}/5
- [ ] 5 pts: All actions documented with inputs/outputs
- [ ] 4 pts: 80%+ actions documented
- [ ] 3 pts: 50-79% actions documented
- [ ] 2 pts: <50% actions documented
- [ ] 0 pts: No action-level instructions

**Notes:** {{NOTES_3_3}}

---

### 3.4 Error Handling Guidance (3 points)
**Criteria:** Instructions cover what to do when actions fail.

**Score:** {{SCORE_3_4}}/3
- [ ] 3 pts: All failure modes addressed; fallback paths defined
- [ ] 2 pts: Partial error guidance; missing some cases
- [ ] 1 pt: Generic "escalate on error" only
- [ ] 0 pts: No error handling guidance

**Notes:** {{NOTES_3_4}}

---

### 3.5 Instruction Hierarchy Coherence (2 points)
**Criteria:** Agent/topic/action instructions don't conflict; clear precedence.

**Score:** {{SCORE_3_5}}/2
- [ ] 2 pts: No conflicts; clear precedence rules
- [ ] 1 pt: Minor conflicts or unclear precedence
- [ ] 0 pts: Major conflicts between instruction levels

**Notes:** {{NOTES_3_5}}

---

**Category 3 Total:** {{INSTRUCTION_SCORE}}/20

---

## Category 4: Dialog Flow Design (15 points)

### 4.1 Conversation Efficiency (4 points)
**Criteria:** Agent minimizes turns to goal; no unnecessary questions.

**Score:** {{SCORE_4_1}}/4
- [ ] 4 pts: Optimal turn count (2-4 for simple tasks)
- [ ] 3 pts: 1-2 unnecessary turns
- [ ] 2 pts: 3+ unnecessary turns (over-questioning)
- [ ] 0 pts: Circular conversations or infinite loops

**Notes:** {{NOTES_4_1}}

---

### 4.2 Data Collection Strategy (4 points)
**Criteria:** Agent collects required data efficiently; uses context.

**Score:** {{SCORE_4_2}}/4
- [ ] 4 pts: Leverages context; asks only missing data
- [ ] 3 pts: Minor redundant questions
- [ ] 2 pts: Asks for already-provided data
- [ ] 0 pts: No data collection strategy

**Notes:** {{NOTES_4_2}}

---

### 4.3 Confirmation and Validation (4 points)
**Criteria:** Agent confirms critical actions; validates inputs.

**Score:** {{SCORE_4_3}}/4
- [ ] 4 pts: Confirms all destructive/irreversible actions
- [ ] 3 pts: Confirms most critical actions
- [ ] 2 pts: Inconsistent confirmations
- [ ] 0 pts: No confirmations

**Notes:** {{NOTES_4_3}}

---

### 4.4 Multi-Turn Coherence (3 points)
**Criteria:** Agent maintains context across turns; handles topic switches.

**Score:** {{SCORE_4_4}}/3
- [ ] 3 pts: Perfect context retention; graceful topic switches
- [ ] 2 pts: Minor context loss or awkward switches
- [ ] 1 pt: Frequent context loss
- [ ] 0 pts: No multi-turn capability

**Notes:** {{NOTES_4_4}}

---

**Category 4 Total:** {{DIALOG_SCORE}}/15

---

## Category 5: Utterance Coverage (15 points)

### 5.1 Happy Path Coverage (4 points)
**Criteria:** 10-15 utterances per topic for standard requests.

**Score:** {{SCORE_5_1}}/4
- [ ] 4 pts: 10-15 per topic; diverse phrasing
- [ ] 3 pts: 7-9 per topic
- [ ] 2 pts: 4-6 per topic
- [ ] 0 pts: <4 per topic

**Notes:** {{NOTES_5_1}}

---

### 5.2 Synonym and Variant Coverage (4 points)
**Criteria:** Utterances include synonyms, slang, abbreviations.

**Score:** {{SCORE_5_2}}/4
- [ ] 4 pts: All topics have 3+ synonym variants
- [ ] 3 pts: Most topics have 2 synonym variants
- [ ] 2 pts: Minimal synonym coverage
- [ ] 0 pts: No synonym variants

**Notes:** {{NOTES_5_2}}

---

### 5.3 Edge Case Coverage (4 points)
**Criteria:** Ambiguous, multi-intent, typo-laden utterances included.

**Score:** {{SCORE_5_3}}/4
- [ ] 4 pts: 3+ edge cases per topic
- [ ] 3 pts: 1-2 edge cases per topic
- [ ] 2 pts: <1 edge case per topic
- [ ] 0 pts: No edge cases

**Notes:** {{NOTES_5_3}}

---

### 5.4 Adversarial Utterance Testing (3 points)
**Criteria:** Utterances include attempts to break agent (jailbreak, injection).

**Score:** {{SCORE_5_4}}/3
- [ ] 3 pts: 5+ adversarial utterances tested
- [ ] 2 pts: 2-4 adversarial utterances
- [ ] 1 pt: 1 adversarial utterance
- [ ] 0 pts: No adversarial testing

**Notes:** {{NOTES_5_4}}

---

**Category 5 Total:** {{UTTERANCE_SCORE}}/15

---

## Category 6: Escalation Design (15 points)

### 6.1 Escalation Trigger Definition (4 points)
**Criteria:** Clear triggers for when to escalate.

**Score:** {{SCORE_6_1}}/4
- [ ] 4 pts: 5+ distinct triggers with conditions
- [ ] 3 pts: 3-4 triggers
- [ ] 2 pts: 1-2 triggers
- [ ] 0 pts: No defined triggers

**Notes:** {{NOTES_6_1}}

---

### 6.2 Context Handoff Completeness (4 points)
**Criteria:** All necessary data passed to human agent.

**Score:** {{SCORE_6_2}}/4
- [ ] 4 pts: Comprehensive context (conversation, data, reason)
- [ ] 3 pts: Most context passed; minor gaps
- [ ] 2 pts: Partial context only
- [ ] 0 pts: No context handoff

**Notes:** {{NOTES_6_2}}

---

### 6.3 Escalation Message Quality (4 points)
**Criteria:** Pre/during/post messages maintain persona and set expectations.

**Score:** {{SCORE_6_3}}/4
- [ ] 4 pts: All 3 message types present; high quality
- [ ] 3 pts: 2 message types present
- [ ] 2 pts: 1 message type present
- [ ] 0 pts: No escalation messages

**Notes:** {{NOTES_6_3}}

---

### 6.4 De-Escalation Strategy (3 points)
**Criteria:** Agent attempts to resolve before escalating.

**Score:** {{SCORE_6_4}}/3
- [ ] 3 pts: 2+ de-escalation strategies defined
- [ ] 2 pts: 1 de-escalation strategy
- [ ] 1 pt: Implicit strategy only
- [ ] 0 pts: No de-escalation; escalates immediately

**Notes:** {{NOTES_6_4}}

---

**Category 6 Total:** {{ESCALATION_SCORE}}/15

---

## Category 7: Guardrails & Safety (10 points)

### 7.1 PII and Data Privacy (3 points)
**Criteria:** Agent doesn't request/expose PII unnecessarily.

**Score:** {{SCORE_7_1}}/3
- [ ] 3 pts: Minimal PII collection; masking in logs
- [ ] 2 pts: Some unnecessary PII requests
- [ ] 1 pt: Excessive PII collection
- [ ] 0 pts: No PII considerations

**Notes:** {{NOTES_7_1}}

---

### 7.2 Harmful Content Prevention (3 points)
**Criteria:** Agent rejects harmful requests (violence, illegal, discriminatory).

**Score:** {{SCORE_7_2}}/3
- [ ] 3 pts: Tested with harmful prompts; all rejected
- [ ] 2 pts: Most harmful prompts rejected
- [ ] 1 pt: Some harmful prompts slip through
- [ ] 0 pts: No harmful content testing

**Notes:** {{NOTES_7_2}}

---

### 7.3 Brand and Compliance Alignment (2 points)
**Criteria:** Agent adheres to brand guidelines and regulatory requirements.

**Score:** {{SCORE_7_3}}/2
- [ ] 2 pts: Fully compliant; brand-aligned
- [ ] 1 pt: Minor deviations
- [ ] 0 pts: Non-compliant or off-brand

**Notes:** {{NOTES_7_3}}

---

### 7.4 Graceful Degradation (2 points)
**Criteria:** Agent handles system failures without exposing errors.

**Score:** {{SCORE_7_4}}/2
- [ ] 2 pts: All failures handled gracefully
- [ ] 1 pt: Some failures expose technical errors
- [ ] 0 pts: Crashes or exposes stack traces

**Notes:** {{NOTES_7_4}}

---

**Category 7 Total:** {{GUARDRAILS_SCORE}}/10

---

## Category 8: Continuous Improvement (10 points)

### 8.1 Conversation Logging and Analytics (3 points)
**Criteria:** Agent logs conversations for analysis.

**Score:** {{SCORE_8_1}}/3
- [ ] 3 pts: Full logging with analytics plan
- [ ] 2 pts: Partial logging
- [ ] 1 pt: Minimal logging
- [ ] 0 pts: No logging

**Notes:** {{NOTES_8_1}}

---

### 8.2 Feedback Mechanisms (3 points)
**Criteria:** Users can rate/provide feedback on agent performance.

**Score:** {{SCORE_8_2}}/3
- [ ] 3 pts: Multi-channel feedback (thumbs, CSAT, comments)
- [ ] 2 pts: Single feedback method
- [ ] 1 pt: Implicit feedback only
- [ ] 0 pts: No feedback mechanism

**Notes:** {{NOTES_8_2}}

---

### 8.3 Iteration Plan (2 points)
**Criteria:** Agent has defined iteration schedule and success metrics.

**Score:** {{SCORE_8_3}}/2
- [ ] 2 pts: Clear iteration plan with metrics
- [ ] 1 pt: Vague plan or no metrics
- [ ] 0 pts: No iteration plan

**Notes:** {{NOTES_8_3}}

---

### 8.4 A/B Testing Readiness (2 points)
**Criteria:** Agent supports testing variants (personas, instructions, flows).

**Score:** {{SCORE_8_4}}/2
- [ ] 2 pts: A/B testing framework in place
- [ ] 1 pt: Manual testing only
- [ ] 0 pts: No testing capability

**Notes:** {{NOTES_8_4}}

---

**Category 8 Total:** {{IMPROVEMENT_SCORE}}/10

---

## Final Score and Grade

**Total Score:** {{TOTAL_SCORE}}/120 ({{TOTAL_PCT}}%)

**Grade:** {{GRADE}}

### Grading Scale
- **A (108-120 pts):** Production-ready; minor optimizations only
- **B (96-107 pts):** Near production; 1-2 categories need improvement
- **C (84-95 pts):** Functional but needs significant iteration
- **D (72-83 pts):** Major gaps; not ready for production
- **F (<72 pts):** Foundational issues; requires redesign

---

## Recommendations

### High Priority (Must Fix Before Production)
1. {{RECOMMENDATION_1}}
2. {{RECOMMENDATION_2}}
3. {{RECOMMENDATION_3}}

### Medium Priority (Should Fix in Next Iteration)
1. {{RECOMMENDATION_4}}
2. {{RECOMMENDATION_5}}

### Low Priority (Nice to Have)
1. {{RECOMMENDATION_6}}

---

## Next Steps

**Immediate Actions:**
- [ ] {{ACTION_1}}
- [ ] {{ACTION_2}}

**Next Assessment Date:** {{NEXT_ASSESSMENT_DATE}}

**Sign-Off:**
- Assessor: {{ASSESSOR_SIGNATURE}}
- Date: {{SIGN_OFF_DATE}}
