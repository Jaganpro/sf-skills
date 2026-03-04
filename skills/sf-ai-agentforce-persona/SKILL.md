---
name: sf-ai-agentforce-persona
description: >
  Deep persona design for Agentforce agents with 50-point scoring.
  TRIGGER when: user designs agent personas, defines agent personality/identity,
  creates persona documents, encodes persona into Agent Builder fields, or asks
  about agent tone/voice/register.
  DO NOT TRIGGER when: building agent metadata (use sf-ai-agentforce), testing
  agents (use sf-ai-agentforce-testing), or Agent Script DSL
  (use sf-ai-agentscript).
version: 1.0
license: MIT
metadata:
  author: "cascadi"
  scoring: "50 points across 5 categories"
  last_validated: "2026-03-04"
tags: [salesforce, agentforce, persona, identity, register, tone, voice, brevity, humor, chatting-style, emoji, formatting, punctuation, capitalization, archetype, agent-personality]
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
  - Glob
  - Grep
---

# Agent Persona Design

## How to Use

This skill designs an AI agent persona through a guided questionnaire. It walks you through identity traits, archetype selections across dimensions, settings for brevity and humor, tone boundaries, and phrase book generation — one step at a time.

**What it produces:**
- A persona document (`generated/[agent-name]-persona.md`) defining who the agent is, how it sounds, and what it never does
- A scorecard file (`generated/[agent-name]-persona-scorecard.md`) evaluating the persona against a 50-point rubric
- An encoding output file (`generated/[agent-name]-persona-encoding.md`) with copy-paste-ready Agent Builder field values, platform setting recommendations, and reusable instruction blocks

**What it drives downstream:** The persona document feeds into conversation design, and the encoding output provides the field values for Agent Builder configuration (Role, Company, Topic Instructions, Action Output Response Instructions, Welcome Message, Loading Text). Those are separate steps — this skill defines the *persona* and translates it into Agent Builder fields, but does not define dialog flows.

**Session resumption:** If you stop mid-workflow, your partial progress is preserved in the conversation and can be resumed.

## When to Use This Skill

- Designing a new Agentforce agent and need to define its personality before building
- Retrofitting persona consistency onto an existing agent whose tone is inconsistent
- Aligning stakeholders on what an agent should sound like before development begins
- Documenting an agent's voice for handoff between design and implementation teams

**Scope boundary:** This skill defines WHO the agent is. It does not define dialog flows, utterance templates, or interaction branching — those belong in conversation design. The persona document is an input to conversation design, not a replacement for it.

## Framework Reference

Read `references/persona-framework.md` for the full framework. It defines:

- **Identity** — 3-5 personality adjectives that anchor every other decision
- **Dimensions** (Register, Voice, Tone) — each with a spectrum and 3-4 named archetypes, ordered by dependency
- **Settings** (Brevity, Empathy Level, Humor) — simple single-knob tuning with one-line descriptions
- **Chatting Style** (Emoji, Formatting, Punctuation, Capitalization) — visual and textual convention settings grouped under one section
- **Tone Boundaries** — authored per persona within the Tone section: what the agent must never sound like

Dimensions are ordered by dependency — upstream choices constrain downstream ones. Constraint notes in the framework explain how earlier choices pull later ones.

## GENERATION GUARDRAILS

These behavioral constraints apply when executing the persona design workflow:

- **Context fields are agent design, not persona** — Name, role, audience, agent type, surface, use cases originate in agent design. Persona design imports or minimally gathers them.
- **Persona-carrying fields in Agentforce** — Role (255 chars), Company (255 chars), Topic Instructions, Action Output Response Instructions, Loading Text, Welcome Message (800 chars). Platform settings that affect persona: Tone dropdown, Conversation Recommendations toggles. Interaction Model, Information Architecture, Recovery & Escalation, and Content Guardrails are agent design inputs.
- **Dimension presentation format** — Dimension name + one-line definition, spectrum line, then compact `- Label: description` list matching spectrum labels. Not full behavioral bullet tables (those go in the generated persona document). Settings (Brevity, Empathy Level, Humor) use a simple table format: Setting | Description.
- **Dependency ordering** — Dimensions and settings are ordered by dependency: Identity → Register → Voice → Brevity → Tone (+Empathy Level) → Humor → Chatting Style (Emoji, Formatting, Punctuation, Capitalization). Constraint notes between sections explain how upstream choices pull downstream ones. No explicit tier labels.
- **Dimensions vs. settings** — Dimensions (Register, Voice, Tone) use archetype menus with spectrum lines and behavioral bullets. Settings (Brevity, Empathy Level, Humor) are simpler single-knob tuning with one-line descriptions. Chatting Style groups four visual/textual convention settings (Emoji, Formatting, Punctuation, Capitalization).
- **Cross-skill relationship** — Interaction Model (initiative, autonomy, collaboration) and Information Architecture (output structure, surface formatting) are defined in agent design. Persona imports the Interaction Model selection as context; Chatting Style is the persona-side visual expression preference.

## Guided Mode Workflow

Walk the user through persona creation in 7 steps. Read `references/persona-framework.md` before starting.

**`AskUserQuestion` usage rules:**
- **Use it for pure archetype/setting selection only** — where the user picks one option from a menu and that's the complete answer (e.g., choosing Peer vs. Coach vs. Subordinate, or Terse vs. Concise vs. Moderate vs. Expansive).
- **Never use it for open-ended or revision questions.** If the answer might require explanation, elaboration, or free-text input, ask in prose and let the user respond naturally. Forcing "select an option then explain in Other" is a bad interaction pattern.
- Concretely: Steps 1 (Context) and 2 (Identity) are prose conversations. Step 3 (Dimensions + Settings) archetype/setting picks use `AskUserQuestion`; Tone Boundaries are proposed and confirmed in prose. Step 6 (Score) review is prose.
- **Recommended-option convention:** When presenting recommended options in `AskUserQuestion` multiselect, mark recommended items with ⭐️. Include at the end of the question text: "(⭐️ = Recommended)"

### Step 1: Context

Most context fields (role, audience, agent type, surface, use cases) are agent design decisions, not persona decisions. They originate in agent design. But persona design needs them as inputs — they inform every archetype recommendation that follows.

**Exception: Agent name is a persona decision.** The name is user-facing — users see it in the chat header before any conversation starts. It should align with Identity and Register. A distinctive name signals personality; a generic name signals nothing. See the Identity → Naming section in the framework.

**Detection:** Start by asking whether agent design work already exists.

> "Do you have an agent design document — a use case definition, agent scope, or blueprint — for this agent? Or are we starting fresh?"

**Path A — Import from agent design:** The user provides or points to an existing agent design artifact. Extract these fields:

| Field | Source in Agent Design |
|---|---|
| Agent name | Use Case Definition → Agent Name |
| Role | Use Case Definition → Description |
| Audience | Use Case Definition → Target Users |
| Agent Type | Agent Scope → Agent Role / channel context |
| Surface | Agent Scope → Channel |
| Primary use cases | Use Case Definition → Use Cases (or prioritized JTBD) |
| Interaction Model | Agent Scope → Interaction Model (§2.7) |

Present the extracted context as a summary table and ask the user to confirm. If anything is missing or unclear, ask only about the gaps.

**Path B — Gather minimum context:** No agent design exists. Gather the basics — enough to proceed with persona, not a full agent design exercise. Ask all at once:

1. **Agent name** — What is this agent called?
2. **Role** — What does it do? (e.g., "helps TSEs manage support cases", "guides customers through onboarding")
3. **Audience** — Internal employees or external customers?
4. **Agent Type** — The Agentforce deployment type (e.g., Employee Agent, Customer Agent, Service Agent, Sales Agent, Custom Agent). Agent Type and Audience are related but distinct — Agent Type is the deployment category, Audience is who the human users are.
5. **Surface** — Where the agent appears, expressed as **Platform/Environment > Surface**. A surface is a distinct UI interaction context where a user can access or encounter agent capabilities — it feels like a different "place" or experience to the user. Two surfaces on the same platform (e.g., Copilot panel vs. Lightning record page) may need different persona tuning because they feel like different places.

   | Platform / Environment | Surfaces |
   |---|---|
   | Salesforce | Copilot panel, Lightning record page, Field-level AI generation (inline assist) |
   | Slack | Agent DM, Agent in channel |
   | Website | Embedded chat widget, Full-page chat |
   | WhatsApp | Messaging conversation |
   | Third-party (e.g., ChatGPT) | Chat with Salesforce integration |

   Surface matters for persona because it constrains Chatting Style (inline field assist can't use heavy formatting; Slack DM can use casual capitalization) and channel-appropriate Voice (Slack DM is more casual than a web chat widget). Surface also informs agent design decisions about Interaction Model and Information Architecture.

6. **Primary use cases** — 2-4 things users will ask it to do most often
7. **Interaction Model** — "How much should this agent do on its own?" A lightweight question to inform phrase book design — not a full agent design exercise.
   - **Socratic Partner** — Asks before acting, confirms everything
   - **Balanced Collaborator** — Asks on ambiguous, drafts on predictable
   - **Proactive Drafter** — Drafts first, confirms on irreversible
   - **Autonomous Operator** — Acts first, reports after

Store these answers — they inform every recommendation that follows.

### Step 2: Identity

Based on the context from Step 1, propose **3-5 personality adjectives** that would serve this agent well. For each adjective, provide a one-sentence behavioral definition (what it looks like in practice, not just what the word means).

Present your proposal and ask the user to confirm, revise, or replace. Identity is generative — the user writes their own, your proposal is a starting point.

**Stop and wait.** Do not proceed to Step 3 until the user has confirmed, revised, or replaced the proposed traits. Identity anchors every subsequent decision — the user must actively sign off before you use it to generate recommendations. If the user hasn't responded, wait.

**Validation rule:** Each adjective must be distinct (no synonyms) and non-contradictory. If two traits conflict, flag it and ask the user to resolve.

Optionally ask: "Want to give this agent a backstory? A fictional background (e.g., 'studied hospitality', 'spent 10 years in field service') that informs word choice — the agent never says it aloud." If yes, capture 1-2 sentences. If no, skip.

### Step 3: Dimensions & Settings

Work through dimensions and settings in dependency order. Upstream choices constrain downstream ones — present them in this sequence:

**Register → Voice → Brevity → Tone (+ Empathy Level) → Humor → Chatting Style (Emoji, Formatting, Punctuation, Capitalization)**

For each **dimension** (Register, Voice, Tone):

1. **Present the dimension in prose** — dimension name + one-line definition from the framework (e.g., "Register — Relationship + formality level: *Who are you to me?*"), the spectrum line, and your recommendation with rationale based on Identity + context. Include the relevant constraint note from the framework explaining how upstream choices pull this dimension.
2. **Ask the user to select** — use `AskUserQuestion` with the archetypes as options. Each option's label is the archetype name and its description is the one-liner from the framework. Do NOT duplicate the archetype list in the prose above — the `AskUserQuestion` IS the archetype menu. The prose presents the dimension context and recommendation; the tool presents the choices.

For each **setting** (Brevity, Empathy Level, Humor) and each **Chatting Style sub-setting** (Emoji, Formatting, Punctuation, Capitalization):

1. **Present the setting in prose** — setting name, what it controls, and your recommendation based on upstream choices.
2. **Ask the user to select** — use `AskUserQuestion` with the setting options. Each option's label is the setting name and its description is the one-liner from the framework.

**Batching:** `AskUserQuestion` supports up to 4 questions per call. A reasonable batching that respects dependency order:

- **Call 1:** Register + Voice (2 questions). Present both dimension contexts and recommendations in prose above the call.
- **Call 2:** Brevity + Tone + Empathy Level (3 questions). Present all three contexts in prose, noting how Register + Voice constrain these. Brevity and Tone are largely independent of each other, so they can be batched. Empathy Level depends on Tone selection, but since both are in the same call the user sees the context.
- **Call 3:** Humor + Emoji + Formatting (3 questions). Present constraint notes from Voice + Tone → Humor and Voice → Chatting Style in prose.
- **Call 4:** Punctuation + Capitalization (2 questions). Present the remaining Chatting Style sub-settings. These are lightweight — constraint note from Voice covers both.

Sequential (one dimension/setting per call) is also fine — batching is optional. The key constraint: dependency order must be maintained.

**Voice dimension additions:**
- After presenting the Voice archetype selection, mention: "All Voice archetypes taper responses as the user demonstrates familiarity — first interactions get full context, repeat interactions get shorter versions. Tapering behavior is calibrated by the Brevity setting (coming next)."
- If the Surface from Step 1 is a voice channel (phone, voice assistant, IVR), present optional voice channel parameters: pitch range (Low/Mid/High), speaking rate (Slow/Moderate/Fast), energy level (Calm/Moderate/Energetic), and warmth/aural smile (Neutral/Warm/Bright). These are physical voice qualities on top of the Voice archetype. Skip for text-based agents.

**Tone Boundaries sub-step:**

After the user confirms Empathy Level, propose Tone Boundaries in prose:
- Present the 4 default tone boundaries (Never apologize for asking clarifying questions; Never apologize for not knowing something; Only apologize when the agent caused an explicit mistake; Never ask the user for empathy)
- Propose context-specific boundaries based on the Tone archetype selected
- When Humor ≠ None, include: "No humor in error states, escalation, or high-stakes contexts"
- User confirms/revises in prose (NOT AskUserQuestion — this is authored content)

**Humor setting additions:**
- When Humor ≠ None, note that a tone boundary will be auto-proposed: "No humor in error states, escalation, or high-stakes contexts."

After all dimensions and settings are selected, display a summary table:

| Area | Selection | Rationale |
|---|---|---|
| Register | ... | ... |
| Voice | ... | ... |
| Brevity | ... | ... |
| Tone | ... | ... |
| Empathy Level | ... | ... |
| Humor | ... | ... |
| Emoji | ... | ... |
| Formatting | ... | ... |
| Punctuation | ... | ... |
| Capitalization | ... | ... |

Ask: "Does this combination feel right for [agent name]? Any dimension or setting you want to revisit?"

### Step 4: Phrase Book

**Phrase Book generation:**

Replace the fixed 4-category Phrase Book with a dynamic system driven by archetype and setting selections:

1. **Category selection:** Based on selected archetypes, settings, and the imported Interaction Model, generate a recommended set of phrase categories. Present as `AskUserQuestion` multiselect. Mark recommended categories with ⭐️. Include at the end of the question text: "(⭐️ = Recommended)". Examples of selection-driven categories:
   - All agents: Acknowledgement, Apology, Redirect/Handoff
   - Terse Brevity: skip Welcome (they don't greet)
   - Non-Terse agents: Welcome/Greeting
   - Socratic Partner IM (imported): Asking Clarification
   - Encouraging Realist / Coach Register: Celebrating Progress, Teaching Moments
   - Proactive Drafter IM (imported): Confirming Action
   - Humor ≠ None: Humor Examples (showing humor type in context)

2. **Additional categories:** Follow up with a second `AskUserQuestion` multiselect offering categories NOT in the recommended set (none marked with ⭐️). User can select extras or type in "Other."

3. **Phrase drafting:** Draft ALL phrases for all selected categories based on everything known about the persona (Identity, Voice, Brevity, Tone, Humor, Register, context). Present the full draft Phrase Book to the user for review and feedback. The user reviews and adjusts — they are NOT expected to write phrases from scratch.

### Step 5: Generate

Read `assets/persona-template.md` and fill every section with the confirmed selections:

1. **Identity** — adjectives + behavioral definitions from Step 2; backstory if provided
2. **Persona Profile** — summary table from Step 3 (includes Brevity, Empathy Level, Humor rows)
3. **Archetype Detail** — for each selected archetype and setting, the full behavioral description from the framework. Includes Brevity, Tone + Empathy Level + Tone Boundaries, Humor, and Chatting Style (Emoji, Formatting, Punctuation, Capitalization) sections.
4. **Phrase Book** — the confirmed phrase table from Step 4
5. **Sample Interactions** — generate 3 sample conversations that demonstrate the persona in action:
   - One routine/happy-path interaction
   - One where the agent handles uncertainty or low confidence
   - One where the agent encounters a persona boundary scenario (tone boundary violation, off-topic request)

Each sample should be 3-5 turns (user + agent) and should distinctively reflect the chosen Identity, Voice, Brevity, Tone, Humor, and Chatting Style. The agent's responses should feel noticeably different from a generic assistant.

Write the completed persona document using the `Write` tool. Default path: `generated/[agent-name]-persona.md`.

### Step 6: Score

Score the generated persona document against a 50-point rubric. Write the scorecard to a separate file: `generated/[agent-name]-persona-scorecard.md`. The scorecard file should include frontmatter with datetime, persona skill version, and the persona document filename being scored.

*For an unbiased score, have someone else run the skill in Audit mode on the generated persona.*

| Category | Points | What It Measures |
|---|---|---|
| **Identity Coherence** | /10 | Traits are distinct, non-contradictory, and behaviorally defined. Each trait generates specific, observable agent behaviors — not vague aspirations. |
| **Dimension Consistency** | /10 | Every archetype and setting selection traces back to Identity. Upstream-downstream constraint alignment is respected (Register → Voice → Brevity → Tone → Humor → Chatting Style). Cross-skill coherence: the imported Interaction Model is compatible with persona selections. Tone Boundaries are consistent with the Tone archetype. |
| **Behavioral Specificity** | /10 | Each archetype includes concrete behavioral examples (what the agent says/does), not just abstract descriptions. Rules are testable. Chatting Style and Tone Boundaries are explicit. |
| **Phrase Book Quality** | /10 | Phrases are consistent with Voice + Tone + Brevity + Humor + Chatting Style. Variety in acknowledgements. Language matches the persona's register. |
| **Sample Quality** | /10 | Interactions demonstrate the persona distinctively. A reader could identify which persona produced these responses. Samples cover happy path, uncertainty, and persona boundary scenarios. |

**Scoring rules:**
- Score each category independently. Provide a number and 1-2 sentences of justification.
- Flag any inconsistencies between dimensions or settings (e.g., "Personable voice but Clinical Analyst tone — these may conflict in practice"). Check upstream-downstream constraint alignment.
- If any category scores below 7, provide a specific suggestion for improvement.
- Total score interpretation:
  - **45-50**: Production-ready persona. Minor polish only.
  - **35-44**: Strong foundation. Address flagged inconsistencies before encoding.
  - **25-34**: Needs revision. Identity or dimension selections may not cohere.
  - **Below 25**: Restart from Identity. The persona lacks a clear point of view.

Present the scorecard and ask if the user wants to revise any section before finalizing.

### Step 7: Encode

Generate copy-paste-ready Agent Builder field values from the completed persona document. Read `references/persona-encoding-guide.md` for field-by-field encoding guidance and `assets/persona-encoding-template.md` for the output structure.

**Company context:** The Company field (255 chars) requires company context not gathered in Step 1. Ask in prose:

> "The Agent Builder Company field (255 chars) describes what your company does and who it serves — it shapes the agent's frame of reference. What should go here? For example: 'B2B SaaS platform for enterprise revenue operations. Serves sales leaders and ops teams at companies with 500+ employees.'"

If the user declines or company context doesn't apply (e.g., a generic internal tool), note "Not specified" in the encoding output.

**Generation:** Using the confirmed persona document, generate values for each Agent Builder field:

1. **Name** (80 chars) — The Agent Name from Step 1. Show character count.
2. **Role** (255 chars) — Compress Identity adjectives + Register archetype + audience + core function into a "You are..." paragraph. Show character count. If over limit, compress — prioritize identity adjectives and register.
3. **Company** (255 chars) — The company context gathered above. Show character count.
4. **Welcome Message** (800 chars) — Generate a greeting reflecting Identity + Register + Voice + Tone + Brevity. For Terse brevity, keep minimal — a single-line prompt or functional opener. Show character count.
5. **Error Message** — Generate a fallback error message reflecting Voice + Tone + Brevity. The agent's Voice should come through even in errors — a Conversational agent doesn't say "An error has occurred."
6. **Tone dropdown** — Recommend Casual, Neutral, or Formal based on the Register + Voice mapping from the encoding guide's Platform Tone Setting section. Note that the dropdown is a coarse approximation — real persona work lives in the instruction fields.
7. **Conversation Recommendations on Welcome Screen** — Recommend On when primary use cases are defined (users benefit from seeing what the agent can do); Off when the agent's scope is open-ended.
8. **Conversation Recommendations in Agent Responses** — Recommend On for Proactive Drafter and Autonomous Operator interaction models (the agent anticipates next steps); Off for Socratic Partner (the agent asks, not suggests).
9. **Persona instruction block** — A reusable block of persona instructions for appending to any Topic Instructions field. Synthesize from: Identity adjectives + behavioral definitions, archetype behavioral bullets (Register, Voice, Tone), brevity calibration, empathy level, humor guidance, tone boundary reminders, voice calibration, chatting style rules (Emoji vocabulary, Formatting, Punctuation, Capitalization), and relevant phrase book entries. Include a note: "Adapt per topic — add topic-specific brevity calibration, phrase book entries, and humor guidance as needed."
10. **Action Output Response Instructions block** — A reusable block for action output formatting. Include: Chatting Style rules (Emoji vocabulary, Formatting conventions, Punctuation rules, Capitalization convention), Voice presentation guidance, Brevity calibration for output length.
11. **Loading Text examples** — 3-4 example loading text strings reflecting Voice + Tone + Brevity. Include a note: "Adapt per action — replace the generic verb with the specific action being performed."

Present all generated values and ask the user to review. Character-limited fields show the count (e.g., "Role (237/255 chars)").

Write the encoding output using the `Write` tool. Default path: `generated/[agent-name]-persona-encoding.md`.

## Output

The skill produces three Markdown files:

1. **Persona document** (`generated/[agent-name]-persona.md`) — follows the `assets/persona-template.md` structure. The design artifact defining who the agent is, how it sounds, and what it never does.
2. **Scorecard** (`generated/[agent-name]-persona-scorecard.md`) — 50-point rubric evaluation with datetime, skill version, and reference to the scored persona document.
3. **Encoding output** (`generated/[agent-name]-persona-encoding.md`) — follows the `assets/persona-encoding-template.md` structure. Copy-paste-ready Agent Builder field values (Name, Role, Company, Welcome Message, Error Message), platform setting recommendations (Tone dropdown, Conversation Recommendations), and reusable instruction blocks (Topic Instructions persona block, Action Output Response Instructions block, Loading Text examples). See `references/persona-encoding-guide.md` for detailed encoding guidance beyond what the skill generates.
