---
version: "2.1"
date: 2026-03-10
---

# Persona Encoding Guide

How to encode a persona document into Agentforce configuration. Covers encoding methods, which fields carry persona, field-by-field encoding guidance, per-topic encoding patterns, platform settings, advanced encoding options, and Agent Script patterns.

**Prerequisite:** A completed persona document — identity traits, 12 attribute selections across 5 categories (Register, Voice, Tone, Delivery, Chatting Style), tone boundaries, tone flex rules, phrase book, never-say list, and optionally a lexicon. See the **Agent Persona Framework** (`references/persona-framework.md`) for how to create one. Interaction Model, Information Architecture, Recovery & Escalation, and Content Guardrails are defined in agent design.

---

## Encoding Methods Overview

Persona encoding maps a persona document to the agent's runtime configuration. The method depends on the target platform:

- **Agent Builder field-by-field** — The primary encoding method for most deployed agents. Persona is distributed across Agent Builder fields (Role, Company, Topic Instructions, Action Output Response Instructions, Welcome Message, Loading Text, Error Message) and platform settings (Tone dropdown, Conversation Recommendations). This guide covers field-by-field encoding in detail.
- **Agent Script (.agent DSL)** — For Next Generation Authoring (NGA) agents. A single `.agent` file holds all instructions with no character limits. See [Agent Script Encoding](#agent-script-agent-dsl-encoding) below.
- **Agent Builder workarounds** — Supplement field-by-field encoding to work around Agent Builder's character limits and distributed instruction model. These approximate capabilities that Agent Script provides natively. See [Compatibility Matrix](#encoding-method-compatibility) below. Methods: [Conversation Style Instruction](#advanced-conversation-style-instruction) (lightweight encoding), [Custom Metadata](#advanced-custom-metadata) (centralized persona injection), and [Global Topic Override](#advanced-global-topic-override) (fallback persona).

---

## Encoding Method Compatibility

| Method | Agent Builder | Agent Script | What It Solves |
|---|---|---|---|
| **Field-by-field** | Primary | N/A | Standard Builder encoding across Role, Topic Instructions, etc. |
| **YAML key content** | N/A | Primary | Recommended instructions for `.agent` system, topics, messages |
| **Custom Metadata** | Compatible | Compatible | Stores persona centrally, passes to actions as variable. In Builder: works around character limits. In Script: useful for multi-agent shared personas. |
| **Conversation Style** | Compatible | Compatible | Compresses persona to a single instruction. In Builder: sidesteps field distribution. In Script: useful for lightweight prototyping. |
| **Global Topic Override** | Compatible | N/A | Builder-only fallback topic strategy. |

*Agent Script provides natively what the Builder workarounds approximate: centralized persona instructions (system.instructions), no character limits, per-topic overrides (topic-level system:), and deterministic static responses.*

---

## Where Persona Lives in Agent Builder

Persona encoding is distributed across several Agent Builder fields. Each field has a different role — some carry the core persona definition, some are platform settings that nudge persona, and some are persona-adjacent. The encoding approach varies by platform — Agent Builder distributes persona across fields with character limits, while Agent Script centralizes it in a single file.

### Persona-Carrying Fields

These are the fields where you actively encode persona instructions. Together, they define who the agent is and how it sounds.

| Field | Limit | What It Carries | Maps From (Persona Doc) |
|---|---|---|---|
| **Name** | 80 chars | User-facing identity — the name users see in the chat interface header. First persona impression before any conversation starts. A distinctive name (Deal Progressinator) signals personality; a generic name (Sales Agent) signals nothing. | Context (Agent Name) + Identity |
| **Role** | 255 chars | Compressed identity: personality traits, register, voice attributes, primary audience, core function. Starts with "You are..." | Context (role, audience) + Identity adjectives + Register + Voice attributes (Formality, Warmth, Personality Intensity) |
| **Company** | 255 chars | Company context that shapes the agent's frame of reference: what the company does, target customers, value prop. | Context section (company, product, audience) |
| **Topic Instructions** | No hard limit | **Primary persona surface.** Per-topic behavioral rules: attribute-specific instructions, phrase book entries, lexicon terms, brevity calibration, humor guidance, tone flex triggers, tone boundary reminders. Encoding approach: global persona block + per-topic calibration (see [Per-Topic Encoding Patterns](#per-topic-encoding-patterns)). | All persona doc sections, filtered per topic |
| **Action Output Response Instructions** | No limit | How the agent presents output: chatting style (Emoji, Formatting, Punctuation, Capitalization), voice presentation (Formality, Warmth, Personality Intensity), response length (Brevity). Interaction Model is an agent design input. | Chatting Style + Voice attributes + Brevity |
| **Loading Text** | Per action | In-character status messages while an action executes. Reflects Formality + Warmth + Emotional Coloring + Brevity. | Formality + Warmth + Emotional Coloring + Brevity |
| **Welcome Message** | 800 chars | The agent's first impression — greeting at conversation start. Sets the relationship dynamic (Register) and personality (Formality + Warmth + Emotional Coloring + Brevity). | Identity + Register + Voice attributes + Emotional Coloring + Brevity |
| **Error Message** | — | Fallback message displayed when a system error occurs. Should reflect the agent's Formality + Warmth + Emotional Coloring + Brevity — a Casual, Warm agent doesn't say "An error has occurred." | Formality + Warmth + Emotional Coloring + Brevity |

### Agent Settings That Affect Persona

These aren't text fields you write — they're toggles and dropdowns — but they influence how the persona is expressed.

| Setting | Type | Persona Mapping |
|---|---|---|
| **Tone** | Dropdown: Casual / Neutral / Formal | Coarse-grained shortcut that maps to Register + Formality. See [Platform Tone Setting](#platform-tone-setting) below. |
| **Conversation Recommendations on Welcome Screen** | Toggle | Whether suggested conversation starters appear. Agents with defined use cases benefit from these. |
| **Conversation Recommendations in Agent Responses** | Toggle | Whether clickable next-action chips appear. Maps to the agent's Interaction Model (an agent design input) — Proactive Drafter and Autonomous Operator benefit from these. |

---

### Action and Template Settings That Affect Formatting

These settings control how action output renders in the conversation. They constrain Chatting Style — a persona with Heavy Formatting won't render rich text if the action's Output Format is set to Plain.

| Location | Setting | Type | What It Controls |
|---|---|---|---|
| Action | **Output Format** | Plain / Rich Text | Whether the action can render rich text (bold, links, lists) or plain text only. Must be Rich Text for HTML prompt output to render. |
| Action | **Show in Conversation** | Checkbox | Whether the action's output displays in the chat. When enabled with an HTML prompt template, HTML tags may render as literal text rather than formatted output. |
| Prompt Template | **Output Format** | Plain Text / HTML / JSON | The format the template produces. HTML enables rich rendering when paired with a Rich Text action. JSON is for structured data consumed by downstream logic. |

---

## Encoding Guidance Per Field

### Name (80 chars)

The name users see in the chat interface header — the agent's first persona impression before any conversation starts. This is not an internal configuration label; it's a user-facing identity signal.

A good agent name:
- **Aligns with Identity** — a Direct, No-nonsense agent doesn't need a playful name, but a generic one wastes the opportunity
- **Fits the Register** — a Subordinate agent named "The Boss" creates cognitive dissonance; a Peer named "Your Assistant" undermines the relationship dynamic
- **Signals personality** — "Deal Progressinator" conveys energy and purpose; "Sales Agent" conveys nothing
- **Fits the surface** — a Slack DM agent can be more casual ("Dealbot") than a customer-facing web chat agent ("Support Advisor")

The Name field also appears in the Welcome Message header, system-generated notifications, and conversation transcripts. Consistency between Name and persona is immediately noticeable — and so is inconsistency.

**Anti-pattern:** Don't use the API name as the display name. `Tech_Assist_Agent_v2` is not a persona name.

### Role (255 chars)

Identity + Register + Voice attributes, compressed into a single paragraph. This is the agent's "job description" — Salesforce uses it as the foundation for the agent's self-concept.

The 255-character limit means this is a compressed summary, not the full persona. Behavioral detail goes in topic instructions. Pack the most differentiating persona signals here:

- Identity adjectives (from the persona document's Identity section)
- Register name or behavioral shorthand
- Primary audience and relationship dynamic
- One sentence on core function

**Example** (Deal Progressinator):
> You are a decisive, analytical sales co-pilot for enterprise sellers. You lead with clear recommendations grounded in pipeline data, draft deliverables alongside your analysis, and push back when deal gaps need attention. Direct, proactive, no filler.

**Anti-pattern:** Don't write a generic job description. "You are a helpful assistant that helps users with their tasks" wastes 255 characters saying nothing distinctive.

### Company (255 chars)

What the company does, who it serves, what makes it different. This field shapes the agent's frame of reference — a support agent for a B2B SaaS company sounds different from one at a consumer retail brand, even with the same attribute selections.

Map from the persona document's Context section (company, product, audience).

### Topic Instructions

The primary surface for detailed persona encoding. No hard character limit — this is where the full persona lives.

Each topic can carry:
- **Attribute-specific behavioral rules** relevant to that topic's use case
- **Phrase book entries** for that context (preferred phrasings, vocabulary)
- **Lexicon entries** (domain vocabulary scoped to this topic)
- **Brevity calibration** specific to the topic (e.g., terse for status checks, moderate for analysis)
- **Humor guidance** if Humor is not None (e.g., "light humor acceptable here" vs. "no humor in escalation topics")
- **Tone flex triggers** (how Emotional Coloring and Empathy Level shift in this topic's context)
- **Tone boundary reminders** (what the agent must never sound like in this topic)

*The more specific the instruction, the more consistent the output.* Per-topic persona encoding beats generic global instructions for consistency.

**Example** (Deal Progressinator — deal summary topic):
> When summarizing a deal, lead with a compact status line: emoji health indicator, deal name, stage, and score. Follow with a checklist of exit criteria (met / unmet). End with a concrete next step — not a list of options, a single recommendation. Use Salesforce record links for all referenced opportunities and contacts. If data is stale (last activity >2 weeks), flag it before summarizing.

### Per-Topic Encoding Patterns

Topic Instructions follow a layered encoding model: global persona in Role, per-topic persona calibration in Topic Instructions, per-action presentation in Action Output Response Instructions. Each layer adds specificity.

#### Per-Topic Persona Instructions

Each topic gets a persona instruction block that calibrates the global persona for that topic's context. The block includes:

- **Brevity calibration** — How much the agent says in this topic (e.g., terse for status lookups, moderate for analysis, expansive for onboarding)
- **Phrase book entries** — Situational phrasings relevant to this topic
- **Humor guidance** — Whether humor is appropriate or suppressed in this topic
- **Tone flex triggers** — How Emotional Coloring and Empathy Level shift in this topic's emotional context (see [Per-Topic Tone Calibration](#per-topic-tone-calibration) below)
- **Lexicon entries** — Domain vocabulary scoped to this topic (see [Per-Topic Lexicon](#per-topic-lexicon) below)

**Example** — status check topic (terse):
> Brevity: Terse. One-line status, emoji health indicator, no commentary. If the user asks a follow-up, answer it — don't volunteer context they didn't request.

**Example** — deal analysis topic (moderate):
> Brevity: Moderate. Lead with a recommendation and its rationale. Include supporting data points. Use bullet formatting for multi-factor analysis. End with a single next step.

#### Per-Topic Lexicon

When an agent operates across multiple topics, each topic may have its own vocabulary — technical terms, brand-specific language, industry jargon. Lexicon defines which words belong where, loaded only in the topics where they're relevant rather than globally.

**How Lexicon differs from Phrase Book:**
- **Phrase Book** = how the agent *sounds* in common situations — organized by situation (acknowledgement, apology, redirect)
- **Lexicon** = what *words and terms* the agent uses in specific domains — organized by topic

**Pattern:** Add a `Lexicon:` block within each topic's persona instructions.

**Example** — a luxury watch agent:

In product topics:
> Lexicon: movement, chronograph, caliber, complication, bezel, case back, power reserve. Use these terms naturally — the audience expects them. Don't define them unless the user asks.

In order-tracking topics:
> *(No lexicon block — generic service vocabulary applies. Don't use watch terminology in shipping status responses.)*

The distinction matters because loading specialized vocabulary globally wastes context and can cause the agent to over-use jargon in simple service interactions. Scope vocabulary to where it belongs.

#### Per-Topic Tone Calibration

Tone Flex rules from the persona document map directly to per-topic instructions. The persona document defines how Emotional Coloring and Empathy Level shift by context; Topic Instructions encode those shifts.

**Pattern:**
> In [topic], shift Emotional Coloring toward [direction]. Shift Empathy Level toward [direction].

**Example** — an agent with Neutral Emotional Coloring and Understated Empathy Level as baseline:

In escalation topics:
> Tone: Shift Emotional Coloring toward Encouraging. Shift Empathy Level toward Moderate. Acknowledge the difficulty briefly, then show the path forward. Never minimize the user's frustration.

In data retrieval topics:
> Tone: Maintain Neutral Emotional Coloring and Understated Empathy Level. State findings without editorial. Confidence labeling matters most here — label confirmed data vs. inferred data.

In success/celebration contexts:
> Tone: Shift Emotional Coloring toward Encouraging briefly. "Done. Nice progress." Then return to baseline. Don't overdo it.

Tone Flex encoding makes the persona dynamic across topics while keeping it consistent — the same persona, expressed differently depending on context.

### Action Output Response Instructions

Controls how output from a specific action is formatted and presented. Maps to:
- **Chatting Style** — emoji (None, Functional, Expressive), formatting (Plain, Selective, Heavy), punctuation (Conservative, Standard, Expressive), capitalization (Standard, Casual)
- **Voice attributes** — Formality (how polished), Warmth (how approachable), Personality Intensity (how much character)
- **Brevity** — response length (terse = minimal prose, expansive = full context)
- **Guardrails** — persona consistency rules (emoji vocabulary, link formatting, prohibited phrases)

*Note: The agent's Information Architecture (output structure patterns like progressive disclosure) is defined in agent design, not persona. Encoding output structure follows the agent design spec; encoding visual expression (Chatting Style, Voice attributes, Brevity) follows the persona document. The action's Output Format and prompt template's Output Format must also support the Chatting Style — see [Action and Template Settings That Affect Formatting](#action-and-template-settings-that-affect-formatting).*

**Anti-pattern:** Don't put identity lines ("You are Deal Progressinator...") here. Identity belongs in Role. These instructions shape *how output looks and reads*, not *who the agent is*. Identity lines in output instructions either leak into the response text or get ignored.

**Example** (Deal Progressinator — comparable deals action):
> Present results as a compact numbered list. Each entry: linked deal name, closed amount, discount percentage, approver (if available). End with a median or range summary in bold. No editorial commentary on whether the discount is good or bad — present the data and let the seller decide.

### Welcome Message (800 chars)

The agent's first impression. Should reflect Formality + Warmth + Emotional Coloring + Brevity while establishing the Register relationship dynamic.

**Display note:** Although the field supports up to 800 characters, longer messages truncate in the chat UI with an action required to expand. Aim for a much lower character count — short enough to display fully without truncation.

A Professional Formality + Neutral Warmth agent with Terse Brevity doesn't say "Hello! I'm here to help you today." A Warm + Bold Personality agent doesn't say "State your request."

- Compress Identity + Register + primary capabilities into the greeting
- Match Formality and Warmth for linguistic style
- Match Brevity for length
- Optionally surface conversation starters (if Conversation Recommendations on Welcome Screen is enabled)

**Example** (Deal Progressinator — Casual Formality + Neutral Warmth + Encouraging Coloring + Concise Brevity + Peer Register):
> What deal are we looking at?

**Example** (formal support agent — Formal Formality + Warm + Neutral Coloring + Moderate Brevity + Subordinate Register):
> I can help with account inquiries, billing questions, and technical support. How can I assist you?

### Loading Text

Short, in-character status messages displayed while an action executes. Should reflect Formality + Warmth + Emotional Coloring + Brevity and signal which action was triggered so the user knows the right thing is happening.

| Persona Attributes | Example Loading Text |
|---|---|
| Professional + Terse | "Pulling case data..." / "Running search..." |
| Formal + Moderate | "Retrieving the requested case information..." |
| Casual + Concise | "Grabbing that deal info..." / "Checking the exit criteria..." |
| Casual + Warm + Moderate | "Let me grab that for you..." / "Searching for a match..." |

### Error Message

Fallback message displayed when a system error occurs. Should reflect the agent's Formality + Warmth + Emotional Coloring + Brevity — the error message is a persona surface, not a system log.

**Example** (Casual + Neutral Warmth + Terse):
> Something broke on my end. Try again — if it persists, escalate to the platform team.

**Example** (Professional + Warm + Moderate):
> I ran into an issue retrieving that information. Let me try again — if the problem continues, I'll connect you with someone who can help.

**Anti-pattern:** A Casual, Warm agent doesn't say "An error has occurred. Please contact your system administrator." Match the error message to the persona, not to a system template.

---

## Platform Tone Setting

The Tone dropdown (Casual / Neutral / Formal) is a coarse-grained platform shortcut. It gives the agent a general formality nudge but captures very little of what a persona document defines.

| Tone Setting | Approximate Framework Mapping |
|---|---|
| **Casual** | Register: Peer. Formality: Casual or Informal. Contractions, informal phrasing. |
| **Neutral** | Register: Peer or Advisor. Formality: Professional. Standard prose, no strong personality. |
| **Formal** | Register: Subordinate or Coach. Formality: Formal. No contractions, structured phrasing. |

**What the dropdown doesn't capture:**
- **Emotional Coloring** (Blunt / Clinical / Neutral / Encouraging / Enthusiastic) — the emotional axis is independent of formality
- **Warmth** (Cool / Neutral / Warm / Bright / Radiant) — interpersonal temperature is independent of formality
- **Personality Intensity** (Reserved / Moderate / Distinctive / Bold) — character volume is orthogonal to formality
- **Brevity** — response length is orthogonal to casual/formal
- **Humor** — wit type is unrelated to formality
- **Empathy Level** — emotional validation is unrelated to formality
- **Chatting Style** — emoji, formatting, punctuation, and capitalization are orthogonal to casual/formal
- **Guardrails** — not addressed by a dropdown
- **Identity** — personality traits are far richer than 3 options

**Recommendation:** Set the dropdown to whichever option is closest to your persona's Register + Formality combination. Then do the real persona work in Topic Instructions and Action Output Response Instructions. The dropdown is a global nudge; the instructions are where persona actually lives.

### Conversation Recommendations

Two toggles that affect persona expression:

- **On Welcome Screen** — Whether suggested conversation starters appear. Enable when the agent has clear primary use cases to surface.
- **In Agent Responses** — Whether clickable next-action chips appear in responses. Maps to the agent's Interaction Model (an agent design input): Proactive Drafter and Autonomous Operator benefit from these (the agent already anticipates next steps). Socratic Partner can use them as the "choices" it naturally offers. Surface constraint: renders as buttons/chips in Salesforce Copilot, as suggested utterances in messaging channels. Not all surfaces support them. The persona encoding guide documents the encoding target, but the Interaction Model design decision originates upstream in agent design.

When using the Encode flow (see `SKILL.md`), these settings are recommended based on the agent's use case context and interaction model.

---

## Advanced: Conversation Style Instruction

> **Builder limitation addressed:** Agent Builder distributes persona across multiple fields with character limits. Conversation Style compresses the persona into a single instruction, sidestepping this distribution. Also useful in Agent Script for lightweight prototyping.

A lightweight encoding pattern that achieves strong persona expression in a single instruction. Best for teams that can't or won't do full field-by-field encoding, or for quick prototyping of a minimum viable persona.

### How It Works

A single `Conversation Style:` instruction in global or topic instructions compresses the persona into one paragraph. The key `Conversation Style` (rather than `tone`) reduces conflict with the system-level Tone dropdown setting.

**Template:**
> Conversation Style: [Register/relationship] who [core behavior]. [Emotional coloring and empathy approach]. [Formality and warmth signals]. [Brevity calibration]. [Distinctive voice markers if any].

**Example** (internal sales coach):
> Conversation Style: Peer advisor who leads with data and clear recommendations. Neutral, matter-of-fact — state outcomes as facts, no dramatization. Professional language, occasional contractions, no filler. Keep responses concise — every sentence earns its place. Push back when deal gaps need attention.

**Example** (customer-facing service agent with regional voice):
> Conversation Style: Trusted ally who sounds like a knowledgeable close friend. Respond with empathy and understanding — acknowledge their circumstances before solving. Warm, casual language. Keep messages short but continue the conversation for 2-3 exchanges to build rapport. Use regional colloquialisms naturally when appropriate.

### When to Use

- **Quick prototyping** — Test a persona concept before investing in full encoding
- **Minimum viable persona** — Teams that need persona consistency but can't do full field-by-field encoding
- **Persona compression** — The framework's value is the design process (ensuring nothing is missed), but the encoding output can be more compact than full field-by-field

### Limitations

- **Static messages still need per-field authoring** — Conversation Style only covers LLM-generated responses. Welcome Message, Error Message, and Loading Text are static fields that must be authored separately.
- **Less precise than field-by-field** — A single paragraph can't encode the same level of per-topic, per-action specificity as the full encoding method.
- **No per-topic calibration** — Tone Flex, per-topic lexicon, and per-topic brevity adjustments require Topic Instructions, not a single global instruction.

---

## Advanced: Custom Metadata

> **Builder limitation addressed:** Agent Builder's field character limits (255 chars for Role, 255 for Company) constrain persona depth. Custom Metadata stores the full persona and injects it via Prompt Templates. In Agent Script, character limits don't apply, so Custom Metadata is primarily useful when multiple agents share a persona definition.

Store the persona document (or a condensed version) as a Custom Metadata Type record and pass it to agent actions as a variable via Prompt Templates.

### How It Works

1. **Create a Custom Metadata Type** (e.g., `Agent_Persona__mdt`) with a long text field for the persona content
2. **Create a record** containing the persona document — condensed to fit field limits, or split across records
3. **Reference the metadata** in a Prompt Template as a merge variable — consider **Flow-based injection** to dynamically insert the persona header at the top of each prompt at runtime
4. **Actions that use that Prompt Template** receive the full persona context at runtime

### Compatibility

This approach is compatible with both Agent Builder and Agent Script. In Agent Builder, it works around character limits on individual fields. In Agent Script, character limits don't apply, so Custom Metadata is primarily useful when multiple agents share a persona definition. Static fields (Welcome Message, Error Message, Loading Text) still need content authored separately per field.

### When to Use It

- **Multiple actions need the same persona context** — rather than duplicating persona instructions across every Action Output Response Instructions field, centralize in one record
- **Persona is long or complex** — the persona document exceeds what fits comfortably in individual Agent Builder fields
- **You want a single source of truth** — update the metadata record once, all actions that reference it get the update

### Compatibility with Field-by-Field Encoding

The Custom Metadata method is supplemental, not a replacement for field-by-field encoding. Field-by-field (Role, Company, Topic Instructions) remains the primary approach because those fields feed the agent's core reasoning loop directly.

The variable method adds persona context to specific actions via Prompt Templates. The two approaches coexist — but fields and variable must not conflict. If Role says "You are a concise, formal analyst" and the persona variable says "Be casual and chatty," the agent gets contradictory instructions.

**Recommended pattern:** Use field-by-field for the compressed persona summary (Role, Company) and per-topic calibration (Topic Instructions). Use Custom Metadata for detailed behavioral rules that are too long for individual fields — attribute behavioral rules, phrase book entries, guardrail lists.

---

## Advanced: Global Topic Override

> **Builder limitation addressed:** Agent Builder's topic-based context model may not carry persona across topics. This workaround embeds persona in the fallback Global Topic. Agent Script does not need this — `system.instructions` applies to all topics, and topic-level `system:` provides explicit per-topic overrides.

An alternative encoding strategy for Agent Builder: override the default General topic with a custom topic that includes the full persona instructions. Since the General topic is the fallback for unclassified utterances, a persona-enriched General topic could keep persona context available across all conversations.

**Caveat:** It is unknown whether the General topic's instructions are always held in context during conversations routed to other topics. If the General topic is only loaded when no other topic matches, the persona instructions would be absent for most interactions. For this reason, use this strategy only in tandem with [Custom Metadata](#advanced-custom-metadata) — the metadata provides persona context via Prompt Templates regardless of which topic is active, while the Global Topic Override ensures persona is present for unclassified utterances.

---

## Agent Script (.agent DSL) Encoding

Agent Script is GA. A single `.agent` file holds all instructions — no character limits apply. Encode the persona primarily in `system.instructions` and secondarily in topic-level instructions.

### Persona-Carrying YAML Keys

| YAML Key | Where | Persona Mapping |
|---|---|---|
| `system.instructions` | `system:` block | Full persona. No character limits. Primary surface. |
| `system.messages.welcome` | `system:` block | Static welcome message. |
| `system.messages.error` | `system:` block | Static error message. |
| Topic `system:` | `topic:` block | Per-topic persona override. **Replaces** global instructions for this topic. |
| `reasoning.instructions` | `topic:` block | Per-topic persona calibration (brevity, lexicon, tone flex). |
| `progress_indicator_message` | Action invocation | In-character loading text per action. Requires `include_in_progress_indicator: True`. |
| `| text` in `if/else` | `instructions: ->` | Deterministic output. Bypasses LLM — must be pre-authored in persona voice. |

### Recommended Pattern

1. **`system.instructions`** — Put the bulk of persona content here: Identity, attribute behavioral rules, phrase book, chatting style rules, tone boundaries, never-say list. This is the primary persona surface in Agent Script — the equivalent of Role + Topic Instructions combined in Agent Builder. No character limits apply, so the full persona document can live here.
2. **Topic-level `system:` and `reasoning.instructions`** — Topic-level `system:` **replaces** global `system.instructions` for that topic — use it only when a topic requires a significant persona shift (e.g., escalation shifts Register from Peer to Advisor). For lighter calibration (brevity, lexicon, tone flex triggers), use `reasoning.instructions` within the topic, which extends rather than replaces the global persona. To ensure the agent keeps its persona in context during extended sessions, include **pointers** — short directives that reference back to the system-level persona. Example: *"Remember, you are [Name]: succinct, friendly, casual. Respond in line with the detailed persona defined in system instructions."* Pointers are especially important for topics where conversation may run long.
3. **`progress_indicator_message`** — Write static, in-character loading text for each action. Match Formality + Warmth + Emotional Coloring + Brevity. Requires `include_in_progress_indicator: True` on the action invocation.
4. **`system.messages.welcome`** — Write a static welcome message reflecting Identity + Register + Formality + Warmth + Brevity.
5. **`system.messages.error`** — Fallback message for system errors. Should reflect Formality + Warmth + Emotional Coloring + Brevity — same guidance as the Agent Builder Error Message field.
6. **Deterministic `| text` outputs** — Agent Script supports deterministic branches (`if`/`else`) with hardcoded pipe (`|`) output that bypasses the LLM entirely. Determinism is a Next Generation Authoring (NGA) capability that allows prescribing exact behaviors and responses. Because the model doesn't generate these at runtime, each static output must be **written exactly as it should appear** — pre-authored in the persona's voice. Apply the same Formality + Warmth + Emotional Coloring + Brevity + Chatting Style rules you'd use for any other persona surface. A Casual, Concise agent's static output should read like that agent wrote it — not like a developer placeholder. This includes all deterministic responses, not just loading text.

### Static Messages Summary

Several Agent Script message types are static (not LLM-generated) and must be authored to align with the persona:

| Message Type | YAML Key | Persona Guidance |
|---|---|---|
| **Welcome** | `system.messages.welcome` | Identity + Register + Formality + Warmth + Brevity |
| **Error** | `system.messages.error` | Formality + Warmth + Emotional Coloring + Brevity |
| **Loading** | `progress_indicator_message` | Formality + Warmth + Emotional Coloring + Brevity |
| **Deterministic responses** | `| text` in `if`/`else` | Full persona — write exactly as it should appear |

## Model Parameters

> These are not persona settings. They are persona-adjacent — handle with care.

Temperature, frequency penalty, and presence penalty are configured in **Einstein Studio**, not Agent Builder. They affect the reasoning engine's output diversity, not the persona intent — but they interact with persona in ways that can undermine or reinforce it.

| Parameter | What It Controls |
|---|---|
| **Temperature** | Randomness/creativity. Lower = more deterministic and predictable. Higher = more varied and creative. |
| **Frequency Penalty** | Discourages word/phrase repetition. Higher = more varied vocabulary. |
| **Presence Penalty** | Encourages introducing new topics/words. Higher = broader coverage, less depth. |

**Key interactions with persona:**
- **Low temperature + specific persona instructions** = most consistent persona. Best for production agents.
- **High temperature + vague persona instructions** = inconsistent persona. The agent drifts.
- **High frequency penalty** can conflict with Terse Brevity — the model may avoid reusing short, functional words the persona calls for.
- **High presence penalty** can conflict with a focused, single-topic agent — the model may try to introduce tangential topics.

**Recommendation:** Leave at platform defaults unless you have a specific reason to change them. Do persona work in instructions, not in model parameters.

---

## What's NOT Persona

These fields are required to configure an agent but belong to agent design, not persona design. The persona document does not define them.

| Field | Why It's Not Persona |
|---|---|
| **API Name** | System identifier |
| **Agent Type** | Deployment context (Service Agent, Employee Agent) |
| **Description** (1000 chars) | Human-readable summary for admins. Not seen by the agent. |
| **Topics** | Map to jobs-to-be-done — what the agent *can do*, not *who it is* |
| **Data Sources** | What data the agent can access |
| **Action Instructions** | What the action does and how to invoke it. Functional, not persona. |
| **Default / Additional Languages** | Language configuration |
| **Agent User** | Permissions and data access context |
| **Enhanced Event Logs** | Observability — conversation transcript recording |

If you're deciding *what the agent does* and *what data it accesses*, that's agent design. If you're deciding *how the agent sounds and behaves*, that's persona design. The persona skill *can* note when persona decisions have implications for these fields (e.g., a Proactive Drafter interaction model implies certain topic structures).

---
