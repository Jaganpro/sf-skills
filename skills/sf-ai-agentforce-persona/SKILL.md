---
name: sf-ai-agentforce-persona
description: >
  Deep persona design for Agentforce agents with 50-point scoring.
  TRIGGER when: user designs agent personas, defines agent personality/identity,
  creates persona documents, encodes persona into Agent Builder fields or
  Agent Script, translates brand guidelines to agent voice, or asks about
  agent tone/voice/register.
  DO NOT TRIGGER when: building agent metadata (use sf-ai-agentforce), testing
  agents (use sf-ai-agentforce-testing), or Agent Script DSL
  (use sf-ai-agentscript).
version: 1.3
license: MIT
metadata:
  author: "cascadi"
  scoring: "50 points across 5 categories"
  last_validated: "2026-03-10"
tags: [salesforce, agentforce, persona, identity, register, tone, voice,
  formality, warmth, personality-intensity, brevity, humor, chatting-style,
  archetype, brand-input, agent-script-encoding, agent-personality]
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
  - Glob
  - Grep
---

# Agent Persona Design

## How to Use

This skill designs an AI agent persona through a fast input-to-sample-dialog loop. Provide any starting input — a brand guide PDF, a URL, a prior persona document, or a text description — and the skill drafts a complete persona, shows you how the agent sounds in sample dialog, and lets you refine until it's right.

**What it produces:**
- A persona document (`_local/generated/[agent-name]-persona.md`) defining who the agent is, how it sounds, and what it never does
- Scoring available on request (50-point rubric)
- Encoding available as a separate workflow (persona → platform-specific field values)

**What it drives downstream:** The persona document feeds into conversation design and Agent Builder encoding. Those are separate steps — this skill defines the *persona*, not dialog flows or field configurations.

**Session resumption:** If you stop mid-workflow, your partial progress is preserved in the conversation and can be resumed.

## When to Use This Skill

- Designing a new Agentforce agent and need to define its personality before building
- Retrofitting persona consistency onto an existing agent whose tone is inconsistent
- Translating brand guidelines or tone documents into a structured persona
- Aligning stakeholders on what an agent should sound like before development begins
- Documenting an agent's voice for handoff between design and implementation teams

**Scope boundary:** This skill defines WHO the agent is. It does not define dialog flows, utterance templates, or interaction branching — those belong in conversation design.

## Framework Reference

Read `references/persona-framework.md` for the full framework. It defines:

- **Identity** — 3-5 personality adjectives that anchor every other decision
- **12 attributes** across 5 categories:
  - **Register** — Subordinate / Peer / Advisor / Coach
  - **Voice** — Formality, Warmth, Personality Intensity (3 independent attributes)
  - **Tone** — Emotional Coloring, Empathy Level (+ Tone Boundaries, Tone Flex)
  - **Delivery** — Brevity, Humor
  - **Chatting Style** — Emoji, Formatting, Punctuation, Capitalization
- **Persona archetype presets** — 6 starting points that pre-populate all 12 attributes
- **Phrase Book & Never-Say List** — what to say and what to never say
- **Tone Flex** — how tone shifts by context
- **Lexicon** — per-topic vocabulary

Attributes are ordered by dependency — upstream choices constrain downstream ones. Constraint notes in the framework explain how earlier choices pull later ones.

---

## Entry Point Detection

Detect the user's intent from their opening message:

- **User provides brand input, text description, or no document** → **Design flow** (Steps 1-6 below)
- **User provides a completed persona.md document and asks to encode** → **Encode flow** (below)
- **User provides a persona.md + a list of topics or actions** → **Encode flow**
- **Ambiguous** → Ask: "Are you designing a new persona or encoding an existing one for Agentforce?"

---

## Design Flow

The design flow prioritizes **speed to sample dialog** — the designer should see how the agent sounds as fast as possible, then refine.

```
INPUT --> DRAFT --> SAMPLE DIALOG --> REFINE --> DOWNLOAD
  |          |           |                |           |
  |          |           |                |           +-- persona.md
  |          |           |                +-- conversational OR deterministic editing
  |          |           +-- with/without persona toggle (shows delta)
  |          +-- auto-generate persona from input + archetype matching
  +-- brand guide PDF, URL, prior persona.md, or text description
```

**One-shot capability:** Drop a brand guide PDF → view sample dialog → download persona.md. The user can edit the persona.md directly and regenerate sample dialog.

### Step 1: Input

Accept any starting input. No detection question needed — accept whatever the user provides.

**Accepted inputs:**
- Brand guide or tone-of-voice document (PDF, text)
- Organization URL
- Prior persona document (persona.md from a previous session)
- Free-text description (e.g., "a sales coach who talks like Crocodile Dundee")
- Existing agent system prompt or .agent file
- Any combination of the above

**If the user provides nothing** (invokes the skill without additional input):
> "Share something to get started — a brand guide, a URL, or just describe the agent in your own words. I'll draft a persona and show you how it sounds in conversation."

Do NOT ask a detection question ("Do you have agent design work?"). Accept whatever arrives and proceed.

### Step 2: Minimal Context

Collect only what the input doesn't already answer. **Every question is skippable.** Zero questions is valid — if the input provides enough signal, skip directly to Draft.

**Context signals to extract or ask about (priority order):**

1. **Internal vs. external audience** — affects register, formality, warmth. If the user says "internal sales coach," audience is already answered.
2. **At least 1 use case or JTBD** — needed to generate meaningful sample dialog.
3. **Agent name** — if not provided in input, will be suggested in Step 3B.

**Do NOT collect:** surface (encoding question, not persona), interaction model (agent design, not persona), agent type, topic list.

**Extraction before asking:** Parse the user's input for context signals before deciding what to ask. "Design an internal sales coach persona for Buc-ee's" already answers audience (internal), role (sales coach), and implies a brand context. Don't re-ask what's already given.

**May ask 1-2 clarifying questions** to surface tensions in the input (e.g., "Your brand guide emphasizes both 'bold irreverence' and 'trusted expertise' — which should win when they conflict?"). But every question is skippable.

### Step 3: Draft

This step is the skill's intelligence — it must execute explicitly as specified below, not left to per-session judgment. The draft is **invisible to the user** — no intermediate output is shown. The first thing the designer sees is the sample dialog.

#### 3A: Input Parsing

Extract persona signals from the user's input:

- **Tone/voice signals:** Look for adjectives, "we are..." statements, competitive positioning language, formality markers.
- **Negative signals:** "Never," "don't," "we are NOT" statements — often the strongest persona signals. These feed the Never-Say List.
- **Audience signals:** Who the brand talks to, formal vs. informal examples, relationship language.
- **If input is a prior persona.md:** Extract attributes directly, skip archetype matching.

#### 3B: Name

If the agent name was not provided:
- Suggest up to 3 names that align with the extracted Identity signals
- Allow the user to write their own
- Reassure: "You can change this later."

If a name was provided, use it and skip this sub-step.

#### 3C: Archetype Matching

Map extracted signals to the closest **persona archetype preset** from the framework:

1. Score input signals against each of the 6 presets (The Steady Hand, Drover, The Concierge, Y.T., The Qualifier, Bluebonnet)
2. Select the closest match as the starting point
3. Pre-populate all 12 attributes from the preset
4. Override attributes where the input provides clear signals (e.g., brand guide says "never use slang" → Formality: Formal)

#### 3D: Confidence Annotations

Mark each attribute as:
- **Strong signal** — clear evidence in input (quote or cite the source)
- **Default** — inferred from preset, no direct evidence in input

These annotations are shown during refinement (Step 5) so the designer knows where to focus.

#### 3E: Generation

From the attribute map, generate:
- **Identity traits** — 3-5 adjectives with behavioral definitions
- **Phrase Book** — example phrases tuned to all selected attributes
- **Never-Say List** — anti-phrases derived from Tone Boundaries, Identity contradictions, and input's negative signals
- **Tone Boundaries** — what the agent must never sound like
- **Tone Flex** — baseline + triggers + shift rules
- **Negative Identity** — 2-4 character-level anti-patterns ("Not a salesperson", "Not a snob"). Generate from negative signals in the input and from Identity traits (what kind of character would contradict these traits?).
- **Values** *(optional)* — Only if the user explicitly stated beliefs, values, or worldview in their input. Never infer values from brand input or other signals. If the user said "we believe everyone deserves X" or "our philosophy is Y", capture it. Otherwise, omit.

#### 3F: State Object

Maintain the full attribute map as an explicit **state object** across the conversation. Every regeneration works from this state, not from conversation history. The state object contains:
- All 12 attribute values
- Confidence annotation per attribute (strong signal / default)
- Identity traits
- Negative Identity statements
- Values (if provided by user — never inferred)
- Phrase Book
- Never-Say List
- Tone Boundaries
- Tone Flex rules

Update the state object on every change. When regenerating sample dialog, read from the state object — not from prior conversation turns.

### Step 4: Sample Dialog

Present a few turns of conversation (3-5 exchanges) based on the use case from Step 2.

**Requirements:**
- The dialog demonstrates the persona in action — word choice, tone, brevity, humor, formatting
- Include at least one "interesting" turn: an error, a clarification, or an emotional moment — not just happy path
- None of these agents say "Hello! How can I help you today?" — the sample should make the persona's impact obvious

**With/without persona view:**
On the **first** sample dialog, show two versions:
1. **With persona** — the agent responding with the designed persona applied
2. **Without persona** — a generic neutral agent with no persona instructions, responding to the same prompts

This demonstrates the value of the design process — the delta between "generic" and "designed" should be obvious. After the first showing, the with/without view is available on request only (don't double output length on every regeneration).

**After presenting the sample dialog,** invite refinement:
> "How does that sound? You can describe what to change ('make it warmer', 'less formal'), ask to see all settings, or request a different scenario."

### Step 5: Refine

Two editing modes, both available at any time. The user can mix them freely.

#### Conversational Editing

The user describes changes in natural language. Map common requests to specific attribute changes using this table:

| User says | Attribute change | Also consider |
|---|---|---|
| "warmer" | Warmth: increase one position | Empathy Level: increase one position |
| "cooler" / "less warm" | Warmth: decrease one position | Empathy Level: decrease one position |
| "more formal" | Formality: increase one position | Register: shift toward Advisor |
| "less formal" / "more casual" | Formality: decrease one position | |
| "shorter" / "more concise" | Brevity: decrease one position (toward Terse) | |
| "longer" / "more detail" | Brevity: increase one position (toward Expansive) | |
| "more personality" | Personality Intensity: increase one position | Humor: consider enabling if None |
| "less personality" / "more neutral" | Personality Intensity: decrease one position | |
| "less robotic" | Warmth: increase + Personality Intensity: increase | |
| "more professional" | Formality: Professional, Humor: None or Dry | Personality Intensity: Moderate |
| "friendlier" | Warmth: increase + Emotional Coloring: Encouraging | Empathy Level: increase |
| "more direct" / "blunter" | Emotional Coloring: toward Blunt, Brevity: toward Terse | Empathy Level: toward Minimal |
| "more encouraging" | Emotional Coloring: Encouraging | Empathy Level: Moderate or High |
| "funnier" | Humor: increase one position | Personality Intensity: increase if Reserved |
| "no humor" | Humor: None | |
| "more emoji" | Emoji: increase one position | |
| "less emoji" | Emoji: decrease one position | |

When a request is ambiguous (e.g., "make it warmer" could mean Warmth, Empathy, or Emotional Coloring), apply the primary mapping and narrate the change so the user can correct: "I increased Warmth to Warm. If you meant more emotional validation, I can also increase Empathy Level."

#### Deterministic Editing

Invoked by asking to "show all settings," "show the attribute table," or "let me see the details."

Display all attributes in a summary table with confidence annotations:

| Category | Attribute | Value | Signal |
|---|---|---|---|
| Register | Register | Peer | default |
| Voice | Formality | Casual | strong — brand guide: "we keep it relaxed" |
| Voice | Warmth | Warm | strong — brand guide: "like a trusted friend" |
| ... | ... | ... | ... |

The user selects specific attributes to adjust. Present the attribute's spectrum and current value. After adjustment, regenerate sample dialog with the change.

Offer: "Pick any attribute to adjust, or describe what you want to change in your own words."

**Detail sections** are available during refinement but not forced:
- **Phrase Book** — generated automatically, visible on request. Preamble: "The Phrase Book is the single most effective lever for making an agent sound like itself."
- **Never-Say List** — visible on request. Useful for catching generic chatbot filler.
- **Tone Flex** — visible on request. Shows how tone shifts by context.
- **Tone Boundaries** — visible on request.
- **Lexicon** — visible on request, when agent has topic-specific vocabulary.
- **Scoring** — available on "score this persona" (50-point rubric, see Scoring section below).

#### Diff-Based Regeneration

After a single-attribute change:
1. **Hold ALL unchanged attributes constant** in the state object
2. Regenerate sample dialog varying only the changed attribute's expression
3. **Narrate the change:** "I adjusted Formality from Casual to Professional. Notice the contractions are gone and sentence structure is more polished. Everything else stayed the same."

This prevents the "slot machine" effect where one change causes unexpected cascading changes in the sample dialog. The user should be able to see exactly what each attribute change does.

#### Natural Exit Points

After 2-3 rounds of refinement, offer:
> "This persona is shaping up well. Ready to download, or want to keep refining?"

Don't wait for the user to remember that downloading is an option. But don't force exit — the user decides when they're done.

### Step 6: Download

Generate and write the persona document:
- Read `assets/persona-template.md` for structure
- Fill every section from the state object
- Include the sample dialog in the document
- Default path: `_local/generated/[agent-name]-persona.md`

**After download, offer next steps:**
- "Want to keep editing? Changes will regenerate the document."
- "Want to score this persona? I'll run the 50-point rubric."
- "Ready to encode for Agentforce? I can generate field values for Agent Builder or Agent Script." (Encode flow)

---

## Scoring

Score the persona document against a 50-point rubric. Scoring is **on-demand** — triggered when the user asks ("score this persona"), not auto-triggered after draft. Write the scorecard to: `_local/generated/[agent-name]-persona-scorecard.md`.

*For an unbiased score, have a different person run the scoring rubric on the generated persona.*

| Category | Points | What It Measures |
|---|---|---|
| **Identity Coherence** | /10 | Traits are distinct, non-contradictory, and behaviorally defined. Each trait generates specific, observable agent behaviors — not vague aspirations. |
| **Attribute Consistency** | /10 | Each attribute within a category is independently set and coherent with Identity. Attribute combinations respect constraint notes (Register → Voice → Tone → Delivery → Chatting Style). Tone Boundaries are consistent with the selected Emotional Coloring and Empathy Level. Tone Flex rules stay within the persona's flex range and never cross Tone Boundaries. |
| **Behavioral Specificity** | /10 | Attribute selections include concrete behavioral examples (what the agent says/does), not just abstract descriptions. Rules are testable. Chatting Style, Tone Boundaries, and Tone Flex triggers are explicit. Never-Say List entries are specific and actionable. |
| **Phrase Book Quality** | /10 | Phrases are consistent with all Voice attributes (Formality, Warmth, Personality Intensity) + Emotional Coloring + Empathy Level + Brevity + Humor + Chatting Style. Never-Say List items are distinct from Tone Boundaries (phrase-level, not quality-level). Variety in acknowledgements. Language matches the persona's register. The Phrase Book is the most effective encoding lever — weight this category accordingly. |
| **Sample Quality** | /10 | Sample dialog demonstrates persona attributes in recognizable ways. A reader could identify which persona produced these responses without seeing the attribute table. With/without persona delta is clear — the sample sounds distinctly different from a generic agent. Samples cover happy path, uncertainty, and persona boundary scenarios. |

**Scoring rules:**
- Score each category independently. Provide a number and 1-2 sentences of justification.
- Flag any inconsistencies between attributes (e.g., "Cool warmth but Enthusiastic coloring — these create tension. Is it intentional?"). Check upstream-downstream constraint alignment. Note productive tensions that are working vs. contradictions that aren't.
- If any category scores below 7, provide a specific suggestion for improvement.
- Total score interpretation:
  - **45-50**: Production-ready persona. Minor polish only.
  - **35-44**: Strong foundation. Address flagged inconsistencies before encoding.
  - **25-34**: Needs revision. Identity or attribute selections may not cohere.
  - **Below 25**: Restart from Identity. The persona lacks a clear point of view.

---

## Encode Flow

A standalone entry point for encoding an existing persona document into platform-specific field values and instructions. Accessible when the user provides a completed persona.md.

Read `references/persona-encoding-guide.md` for field-by-field encoding guidance and `assets/persona-encoding-template.md` for the output structure.

### Encoding-Specific Context

Collect context needed for encoding but NOT gathered during persona design:

1. **Platform** — "Are you encoding for Agent Builder or Agent Script (.agent file)?"
   - **Agent Builder** — Field-by-field encoding with character limits. Advanced methods available.
   - **Agent Script** — Recommended instructions for YAML keys. No character limits.
2. **Company context** — For Agent Builder: "The Company field (255 chars) describes what your company does and who it serves. What should go here?" For Agent Script: "What should the `system.instructions` include about the company?" (no character limit). If declined, note "Not specified."
3. **Surface** — Where the agent appears (web chat, Slack, voice, etc.). Affects Chatting Style encoding and platform-specific constraints.
4. **Agent type** — Employee Agent, Customer Agent, Service Agent, etc.
5. **Topics** *(optional)* — List of agent topics. If provided, generate per-topic persona instructions with tailored brevity calibration, phrase book entries, lexicon, and tone flex triggers. For Agent Script, also generate per-topic `system:` overrides and `reasoning.instructions` content when warranted.
6. **Actions** *(optional)* — List of agent actions. If provided, generate persona-consistent loading text for each action. For Agent Script, generate `progress_indicator_message` for each.

### Generation

Using the completed persona document + encoding context, generate the platform-specific encoding:

#### If Agent Builder

**Agent Configuration Fields:**
1. **Name** (80 chars) — Show character count.
2. **Role** (255 chars) — Compress Identity + Register + audience + core function into "You are..." Show character count.
3. **Company** (255 chars) — Show character count.
4. **Welcome Message** (800 chars) — Reflect Identity + Register + Voice + Tone + Brevity. Show character count.
5. **Error Message** — Reflect Formality + Warmth + Emotional Coloring + Brevity.

**Platform Settings:**
6. **Tone dropdown** — Recommend based on Formality attribute. Note it's a coarse approximation.
7. **Conversation Recommendations on Welcome Screen** — On when use cases are defined; Off when open-ended.
8. **Conversation Recommendations in Agent Responses** — On for proactive agents; Off for socratic agents.

**Instruction Blocks:**
9. **Global persona instruction block** — For appending to Topic Instructions. Synthesize from all persona sections.
10. **Per-topic persona instructions** — If topics were provided: tailored instructions per topic with brevity calibration, phrase book entries, lexicon terms, tone flex triggers, humor guidance.
11. **Per-topic lexicon** — If topics were provided and the agent has domain vocabulary.
12. **Action Output Response Instructions block** — Chatting Style rules, Voice presentation, Brevity calibration.

**Loading Text:**
13. **Generic loading text examples** — 3-4 examples reflecting Voice + Tone + Brevity.
14. **Per-action loading text** — If actions were provided: persona-consistent loading text for each specific action.
15. **Situational messages** *(optional)* — If the persona has specific requirements for common situations (escalation, scope boundary, topic transition, end of conversation), generate pre-authored messages in the persona's voice.

#### If Agent Script

**System Block:**
1. **system.instructions** — Full persona content: Identity, attribute behavioral rules, phrase book, chatting style rules, tone boundaries, never-say list. No character limit — the complete persona lives here.
2. **system.messages.welcome** — Static welcome message reflecting Identity + Register + Formality + Warmth + Brevity.
3. **system.messages.error** — Static error message reflecting Formality + Warmth + Emotional Coloring + Brevity.

**Per-Topic Overrides** (if topics provided):
4. **Topic-level system: override** — For topics that shift persona significantly (e.g., escalation shifts Emotional Coloring toward Encouraging). Only generate when the topic's tone flex warrants a system-level override.
5. **Per-topic reasoning.instructions** — Persona calibration per topic: brevity calibration, lexicon, tone flex triggers, phrase book entries, humor guidance.

**Static Messages** (if actions provided):
6. **Per-action progress_indicator_message** — In-character loading text for each action.
7. **Deterministic response examples** — Example `| text` pipes for common if/else branches (error recovery, identity verification, status confirmations) written in the persona's voice.
8. **Situational messages** *(optional)* — Pre-authored messages for common conversational situations. These can be encoded as `| text` deterministic outputs or as guidance in `reasoning.instructions`.

#### Output

Present all generated values and ask the user to review. Character-limited fields (Agent Builder) show the count.

Write the encoding output using the `Write` tool. Default path: `_local/generated/[agent-name]-persona-encoding.md`.

---

## Output

The skill produces up to three Markdown files:

1. **Persona document** (`_local/generated/[agent-name]-persona.md`) — follows the `assets/persona-template.md` structure. The design artifact defining who the agent is, how it sounds, and what it never does. Includes sample dialog.
2. **Scorecard** (`_local/generated/[agent-name]-persona-scorecard.md`) — 50-point rubric evaluation. Generated on request.
3. **Encoding output** (`_local/generated/[agent-name]-persona-encoding.md`) — follows the `assets/persona-encoding-template.md` structure. Platform-specific: Agent Builder field values and settings, or Agent Script YAML key content. Generated on request via the Encode flow.
