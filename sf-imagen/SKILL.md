---
name: sf-imagen
description: >
  AI-powered visual content generation for Salesforce development.
  Generates ERD diagrams, LWC mockups, architecture visuals using Nano Banana Pro.
  Also provides Gemini as a parallel sub-agent for code review and research.
license: MIT
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
  scoring: "80 points across 5 categories"
---

# sf-imagen: Salesforce Visual AI Skill

Visual content generation and AI sub-agent for Salesforce development using
Gemini CLI with Nano Banana Pro extension.

## ⚠️ IMPORTANT: Prerequisites Check

**Before using this skill, ALWAYS run the prerequisites check first:**

```bash
~/.claude/plugins/marketplaces/sf-skills/sf-imagen/scripts/check-prerequisites.sh
```

**If the check fails, DO NOT invoke this skill.** The user must fix the missing prerequisites first.

## Requirements

| Requirement | Description | How to Get |
|-------------|-------------|------------|
| **Ghostty Terminal** | Required for Kitty graphics protocol | https://ghostty.org |
| **GEMINI_API_KEY** | Personal API key for Nano Banana Pro | https://aistudio.google.com/apikey |
| **Gemini CLI** | Command-line interface for Gemini | `npm install -g @google/gemini-cli` |
| **Nano Banana Extension** | Image generation extension | `gemini extensions install nanobanana` |
| **timg** | Terminal image viewer with Kitty support | `brew install timg` |

### Setting Up API Key

Add to `~/.zshrc` (DO NOT commit to version control):
```bash
export GEMINI_API_KEY="your-personal-api-key"
export NANOBANANA_MODEL=gemini-3-pro-image-preview
```

## Core Capabilities

### 1. Visual ERD Generation
Generate actual rendered ERD diagrams (not just Mermaid code):
- Query object metadata via sf-metadata
- Generate visual diagram with Nano Banana Pro
- Display inline using Kitty graphics protocol

### 2. LWC/UI Mockups
Generate wireframes and component mockups:
- Data tables, record forms, dashboard cards
- Experience Cloud page layouts
- Mobile-responsive designs following SLDS

### 3. Gemini Code Review (Sub-Agent)
Parallel code review while Claude continues working:
- Apex class/trigger review for best practices
- LWC component review for accessibility
- SOQL query optimization suggestions

### 4. Documentation Research (Sub-Agent)
Parallel Salesforce documentation research:
- Look up API references and limits
- Find best practices and patterns
- Research release notes

---

## Workflow Patterns

### Pattern A: Visual ERD Generation

**Trigger**: User asks for visual ERD, rendered diagram, or image-based data model

**Workflow**:
1. Run prerequisites check
2. Query object metadata via sf-metadata (if org connected)
3. Build Nano Banana prompt with object relationships
4. Execute Gemini CLI with `/generate` command (requires --yolo flag)
5. Display result inline using `timg -pk` (Kitty graphics)

**Example**:
```bash
# Generate image
export GEMINI_API_KEY="..." && gemini --yolo "/generate 'Professional Salesforce ERD diagram showing:
   - Account (blue box, center)
   - Contact (green box, linked to Account with lookup arrow)
   - Opportunity (yellow box, linked to Account with master-detail thick arrow)
   Include legend. Clean white background, Salesforce Lightning style.'"

# Display with Kitty graphics (in Ghostty)
timg -pk ~/nanobanana-output/[generated-file].png

# Or open in new Ghostty window
~/bin/show-image-window --latest
```

### Pattern B: LWC Mockup

**Trigger**: User asks for component mockup, wireframe, or UI design

**Workflow**:
1. Load appropriate template from `templates/lwc/`
2. Customize prompt with user requirements
3. Execute via Nano Banana
4. Display inline

### Pattern C: Parallel Code Review

**Trigger**: User asks for code review, second opinion, or "review while I work"

**Workflow**:
1. Run Gemini in background with JSON output
2. Claude continues with current task
3. Return Gemini's findings when ready

**Example**:
```bash
gemini "Review this Apex trigger for:
   - Bulkification issues
   - Best practices violations
   - Security concerns (CRUD/FLS)
   Code: [trigger code]" -o json
```

### Pattern D: Documentation Research

**Trigger**: User asks to look up, research, or find documentation

**Workflow**:
1. Run Gemini with documentation query
2. Return findings with sources

---

## Commands Reference

### Image Generation

```bash
# Generate image from prompt (MUST use --yolo for non-interactive)
export GEMINI_API_KEY="..." && gemini --yolo "/generate 'description'"

# Images are saved to ~/nanobanana-output/
```

### Image Display (Kitty Graphics - Ghostty Only)

```bash
# Display inline in current terminal
timg -pk -g 120x40 /path/to/image.png

# Open in new Ghostty window (recommended from Claude Code)
~/bin/show-image-window /path/to/image.png
~/bin/show-image-window --latest  # Most recent image
```

### Viewing in Claude Code

Since Claude Code captures terminal output (including Kitty escape sequences as raw text),
use the **Read tool** to view images inline in the conversation:

```
Read tool → /path/to/image.png → Claude's multimodal vision renders it
```

---

## Cross-Skill Integration

| Skill | Integration | Usage |
|-------|-------------|-------|
| sf-diagram | Enhance Mermaid with visual rendering | "Convert this Mermaid ERD to a visual diagram" |
| sf-metadata | Get object/field data for ERDs | Query org before generating ERD |
| sf-lwc | Generate component mockups | "Mockup for the AccountList component" |
| sf-apex | Review Apex code via Gemini | "Get Gemini's opinion on this trigger" |

---

## Helper Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `check-prerequisites.sh` | `scripts/` | Verify all requirements before use |
| `show-image.sh` | `scripts/` | Display images in current terminal |
| `show-image-window` | `~/bin/` | Open image in new Ghostty window |

---

## Template Usage

### ERD Templates (`templates/erd/`)
- `core-objects.md` - Standard CRM objects
- `custom-objects.md` - Custom data model

### LWC Templates (`templates/lwc/`)
- `data-table.md` - Lightning datatable mockups
- `record-form.md` - Record form mockups
- `dashboard-card.md` - Dashboard card mockups

### Architecture Templates (`templates/architecture/`)
- `integration-flow.md` - Integration architecture diagrams

### Review Templates (`templates/review/`)
- `apex-review.md` - Apex code review prompts
- `lwc-review.md` - LWC review prompts

---

## Troubleshooting

### Prerequisites Check Failed
Run `scripts/check-prerequisites.sh` and fix each issue:
- **Not Ghostty**: sf-imagen requires Ghostty terminal for Kitty graphics
- **No API Key**: Set GEMINI_API_KEY in ~/.zshrc (personal key from aistudio.google.com)
- **No Gemini CLI**: Install with npm
- **No Nano Banana**: Install extension via gemini CLI
- **No timg**: Install with brew

### Image Not Displaying in Claude Code
- Use the **Read tool** to view images (Claude's multimodal vision)
- Or run `~/bin/show-image-window` to open in new Ghostty window

### API Key Errors
- Ensure GEMINI_API_KEY is exported in current shell
- Verify key is valid at https://aistudio.google.com/apikey
- Check billing is enabled on Google Cloud project

---

## Security Notes

⚠️ **NEVER commit your GEMINI_API_KEY to version control**

- Store API key in `~/.zshrc` only (not in project files)
- The key is personal and tied to your Google account billing

---

## License

MIT License. Copyright (c) 2024-2025 Jag Valaiyapathy
