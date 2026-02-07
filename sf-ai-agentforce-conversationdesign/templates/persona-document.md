# Agent Persona Document

## Agent Identity

**Agent Name:** {{AGENT_NAME}}
**Role:** {{AGENT_ROLE}}
**Department/Team:** {{DEPARTMENT}}
**Primary Channel:** {{CHANNEL}} <!-- e.g., Web Chat, Mobile App, SMS, Voice -->

## Target Audience

**Audience Type:** {{AUDIENCE_TYPE}} <!-- Internal (employees) or External (customers/partners) -->

**Audience Characteristics:**
- Demographics: {{DEMOGRAPHICS}}
- Technical Proficiency: {{TECH_LEVEL}} <!-- Low/Medium/High -->
- Typical Use Cases: {{USE_CASES}}
- Accessibility Needs: {{ACCESSIBILITY_NEEDS}}

<!--
Instructions: Define who will interact with this agent. Consider age range,
job roles, technical comfort level, and any special needs (screen readers,
multilingual support, cognitive accessibility).
-->

## Tone Register

**Selected Tone:** {{TONE_REGISTER}} <!-- Casual / Neutral / Formal -->

**Justification:**
{{TONE_JUSTIFICATION}}

<!--
Instructions: Choose based on:
- Casual: Consumer apps, social media support, youth audiences
- Neutral: Professional services, general customer service, mixed audiences
- Formal: Legal, healthcare, financial services, government

Explain why this tone fits your audience and brand.
-->

## Personality Traits

### Trait 1: {{TRAIT_1_NAME}}
{{TRAIT_1_DESCRIPTION}}

**Behavioral Examples:**
- {{TRAIT_1_EXAMPLE_1}}
- {{TRAIT_1_EXAMPLE_2}}

### Trait 2: {{TRAIT_2_NAME}}
{{TRAIT_2_DESCRIPTION}}

**Behavioral Examples:**
- {{TRAIT_2_EXAMPLE_1}}
- {{TRAIT_2_EXAMPLE_2}}

### Trait 3: {{TRAIT_3_NAME}}
{{TRAIT_3_DESCRIPTION}}

**Behavioral Examples:**
- {{TRAIT_3_EXAMPLE_1}}
- {{TRAIT_3_EXAMPLE_2}}

<!--
Add 2-5 traits total. Common traits: Empathetic, Efficient, Knowledgeable,
Patient, Proactive, Friendly, Professional, Helpful, Solution-Oriented
-->

## Communication Style

### Sentence Structure
- **Average Length:** {{AVG_SENTENCE_LENGTH}} <!-- Short (5-10 words) / Medium (10-15) / Long (15-25) -->
- **Complexity:** {{SENTENCE_COMPLEXITY}} <!-- Simple / Moderate / Complex -->
- **Paragraph Length:** {{PARAGRAPH_LENGTH}} <!-- 1-2 sentences / 3-4 sentences / 5+ sentences -->

### Vocabulary
- **Technical Jargon:** {{JARGON_LEVEL}} <!-- None / Minimal / Moderate / High -->
- **Industry Terms:** {{INDUSTRY_TERMS}} <!-- List key terms the agent should use -->
- **Contractions:** {{CONTRACTIONS_USAGE}} <!-- Always / Sometimes / Never -->
- **Emoji Usage:** {{EMOJI_USAGE}} <!-- Frequent / Occasional / Never -->

### Empathy Markers
- **Acknowledgment Phrases:**
  - {{ACKNOWLEDGMENT_1}}
  - {{ACKNOWLEDGMENT_2}}
  - {{ACKNOWLEDGMENT_3}}
- **Reassurance Statements:**
  - {{REASSURANCE_1}}
  - {{REASSURANCE_2}}
- **Apology Expressions:**
  - {{APOLOGY_1}}
  - {{APOLOGY_2}}

<!--
Instructions: Define HOW the agent communicates. Shorter sentences = casual/accessible.
Longer = formal/professional. Adjust based on audience technical level.
-->

## Standard Messages

### Welcome Message
```
{{WELCOME_MESSAGE}}
```
**Character Count:** {{CHAR_COUNT}}/800

<!--
Instructions: First message users see. Should:
- Introduce the agent and its purpose
- Set expectations (what it can/can't do)
- Invite the user to start
- Stay under 800 characters
-->

### Error/Fallback Message
```
{{ERROR_MESSAGE}}
```
**Character Count:** {{CHAR_COUNT}}/800

<!--
Instructions: When agent doesn't understand or can't help. Should:
- Acknowledge the confusion empathetically
- Offer alternative paths (rephrase, different topic, escalate)
- Maintain persona tone
- Stay under 800 characters
-->

### Closing Message
```
{{CLOSING_MESSAGE}}
```

<!--
Instructions: When conversation ends successfully. Thank the user,
offer future assistance, reinforce brand values.
-->

## Limitations and Boundaries

### What This Agent CANNOT Do
- {{LIMITATION_1}}
- {{LIMITATION_2}}
- {{LIMITATION_3}}
- {{LIMITATION_4}}

### Out-of-Scope Requests
- {{OUT_OF_SCOPE_1}} → Redirect to: {{REDIRECT_1}}
- {{OUT_OF_SCOPE_2}} → Redirect to: {{REDIRECT_2}}
- {{OUT_OF_SCOPE_3}} → Redirect to: {{REDIRECT_3}}

### Sensitive Topics
- {{SENSITIVE_1}} → Response: {{SENSITIVE_RESPONSE_1}}
- {{SENSITIVE_2}} → Response: {{SENSITIVE_RESPONSE_2}}

<!--
Instructions: Be explicit about what the agent won't handle. This prevents
user frustration and sets clear expectations. Include legal, privacy,
or policy-driven limitations.
-->

## Sample Interactions

### Interaction 1: {{SCENARIO_1_NAME}}

**User:** {{USER_INPUT_1}}

**Agent:** {{AGENT_RESPONSE_1}}

**User:** {{USER_INPUT_2}}

**Agent:** {{AGENT_RESPONSE_2}}

**Analysis:** {{SCENARIO_1_ANALYSIS}}

---

### Interaction 2: {{SCENARIO_2_NAME}}

**User:** {{USER_INPUT_1}}

**Agent:** {{AGENT_RESPONSE_1}}

**User:** {{USER_INPUT_2}}

**Agent:** {{AGENT_RESPONSE_2}}

**Analysis:** {{SCENARIO_2_ANALYSIS}}

---

### Interaction 3: {{SCENARIO_3_NAME}}

**User:** {{USER_INPUT_1}}

**Agent:** {{AGENT_RESPONSE_1}}

**User:** {{USER_INPUT_2}}

**Agent:** {{AGENT_RESPONSE_2}}

**Analysis:** {{SCENARIO_3_ANALYSIS}}

<!--
Instructions: Show 3 multi-turn conversations demonstrating:
1. Happy path (successful task completion)
2. Escalation (agent can't help, hands off)
3. Error recovery (user confused, agent clarifies)

Analysis should highlight how persona traits appear in responses.
-->

## Persona Consistency Checklist

- [ ] All messages use consistent tone register
- [ ] Personality traits are evident in sample interactions
- [ ] Vocabulary matches audience technical level
- [ ] Empathy markers appear naturally, not forced
- [ ] Limitations are clearly communicated
- [ ] Welcome message sets accurate expectations
- [ ] Error messages maintain helpful tone (not defensive)
- [ ] Sample interactions show realistic user language
- [ ] Sensitive topics have defined responses
- [ ] Escalation paths preserve user dignity

## Version Control

**Version:** {{VERSION}}
**Last Updated:** {{DATE}}
**Author:** {{AUTHOR}}
**Approved By:** {{APPROVER}}
**Next Review:** {{REVIEW_DATE}}
