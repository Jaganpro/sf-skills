---
name: sf-diagram-nanobananapro
description: >
  AI-powered visual content generation for Salesforce development.
  Generates ERD diagrams, LWC mockups, architecture visuals using Nano Banana Pro.
  Also provides Gemini as a parallel sub-agent for code review and research.
license: MIT
metadata:
  version: "1.5.0"
  author: "Jag Valaiyapathy"
  scoring: "80 points across 5 categories"
---

# sf-diagram-nanobananapro: Salesforce Visual AI Skill

Visual content generation and AI sub-agent for Salesforce development using
Gemini CLI with Nano Banana Pro extension.

## ⚠️ IMPORTANT: Prerequisites Check

**Before using this skill, ALWAYS run the prerequisites check first:**

```bash
~/.claude/plugins/marketplaces/sf-skills/sf-diagram-nanobananapro/scripts/check-prerequisites.sh
```

**If the check fails, DO NOT invoke this skill.** The user must fix the missing prerequisites first.

## Requirements

| Requirement | Description | How to Get |
|-------------|-------------|------------|
| **macOS** | Required for Preview app image display | Built-in |
| **GEMINI_API_KEY** | Personal API key for Nano Banana Pro | https://aistudio.google.com/apikey |
| **Gemini CLI** | Command-line interface for Gemini | `npm install -g @google/gemini-cli` |
| **Nano Banana Extension** | Image generation extension | `gemini extensions install nanobanana` |

### Optional (for 4K/editing via Python script)
| Requirement | Description | How to Get |
|-------------|-------------|------------|
| uv | Fast Python package runner | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

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
- **Display in macOS Preview app** (default)
- **Default style**: architect.salesforce.com aesthetic (see below)

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

## 🎨 Default Visual Style: Architect.salesforce.com

All ERD diagrams now default to the **official Salesforce architect.salesforce.com** aesthetic.

### The Signature Look: Dark Border + Light Fill

| Property | Value |
|----------|-------|
| **Border** | Solid 2px in cloud's brand color |
| **Fill** | Same hue at ~25% opacity (translucent) |
| **Corners** | Rounded (8-12px radius) |
| **Text** | Dark gray/black on light fill |

### Cloud-Specific Colors (Auto-Detected)

| Cloud | Border Color | Detect By Objects |
|-------|--------------|-------------------|
| **Sales Cloud** | `#0B827C` (Teal) | Lead, Opportunity, Quote, Campaign |
| **Service Cloud** | `#9E2A7D` (Magenta) | Case, Knowledge, Entitlement |
| **Platform** | `#5A67D8` (Purple) | Account, Contact only |
| **Industries** | `#BA4383` (Pink) | ServiceTerritory, WorkType |

### Standard Elements

| Element | Description |
|---------|-------------|
| **Page Title** | "[Cloud Name] Overview Data Model" at top |
| **Header Banner** | Salesforce logo + "[CLOUD] Overview" |
| **Legend Bar** | ENTITIES + RELATIONSHIPS notation |
| **Entity Boxes** | Name + API name + bullet fields |
| **Relationship Lines** | Labeled ("child of", "parent of") |
| **Footer** | Copyright + Last modified date |

See `resources/architect-aesthetic-guide.md` for full specification.

---

## 🔄 Draft → Final Workflow (Cost-Effective Iteration)

For complex visuals, iterate at low resolution before generating the final:

| Phase | Resolution | Purpose | Time | Method |
|-------|------------|---------|------|--------|
| **Draft** | 1K | Quick feedback, prompt refinement | ~3s | CLI or Python |
| **Iteration** | 1K | Style/layout adjustments | ~3s | CLI `/edit` or Python |
| **Final** | 4K | Production-quality output | ~10s | Python script only |

### Recommended Workflow

1. **Draft at 1K** - Generate initial image quickly
2. **Iterate** - Refine prompt or use `/edit` to adjust
3. **Final at 4K** - Once satisfied, generate production quality

### Example: Draft to Final

```bash
# Step 1: Draft (fast, cheap)
gemini --yolo "/generate 'Account-Contact ERD with blue boxes'"
open ~/nanobanana-output/*.png  # Review

# Step 2: Iterate with /edit
gemini --yolo "/edit 'Add Opportunity, use thicker arrows'"

# Step 3: Final at 4K (requires Python script)
uv run scripts/generate_image.py \
  -p "Account-Contact-Opportunity ERD, blue boxes, thick arrows, legend" \
  -f "crm-erd-final.png" \
  -r 4K
open ~/nanobanana-output/*crm-erd-final*.png
```

---

## Image Editing with /edit

Refine existing images with natural language instructions:

```bash
# Edit the most recent generated image
gemini --yolo "/edit 'Move Account box to center, make relationship arrows thicker'"

# Common editing commands
gemini --yolo "/edit 'Add a legend in the bottom right corner'"
gemini --yolo "/edit 'Change background to light gray'"
gemini --yolo "/edit 'Add Salesforce Lightning blue (#0176D3) to headers'"
```

### Editing via Python Script (with resolution control)

```bash
uv run scripts/generate_image.py \
  -p "Add legend in bottom right, use SLDS colors" \
  -i ~/nanobanana-output/previous-erd.png \
  -f "erd-with-legend.png" \
  -r 2K
```

---

## Artistic Styles & Variations

The CLI extension supports style modifiers for creative control:

```bash
# Apply artistic styles
gemini --yolo "/generate 'Salesforce ERD' --styles=modern,minimalist"

# Available styles
# photorealistic, watercolor, oil-painting, sketch, pixel-art
# anime, vintage, modern, abstract, minimalist

# Generate multiple variations
gemini --yolo "/generate 'Dashboard mockup' --count=3 --variations=color-palette"

# Reproducible output with seed
gemini --yolo "/generate 'Account ERD' --seed=42"
```

---

## 🎤 Interview-First Workflow (Recommended)

**Before generating any image, Claude MUST ask clarifying questions using `AskUserQuestion`.**

This ensures high-quality output by gathering requirements upfront rather than guessing.

### Automatic Interview Triggers

| User Request | Interview Questions |
|--------------|---------------------|
| ERD, data model, schema | Objects, Style, Purpose, Extras |
| LWC, component, mockup, wireframe | Component type, Object, Context, Style |
| Architecture, integration, flow | Diagram type, Systems, Protocols, Elements |

### Interview Flow

```
User: "Generate an ERD for my org"
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  Claude invokes AskUserQuestion with 4 questions:       │
│                                                         │
│  Objects: [Core CRM / Sales Cloud / Service Cloud / Custom]  │
│  Style:   [Professional / Whiteboard / Technical / Minimalist]│
│  Purpose: [Documentation 4K / Quick draft 1K / Presentation]  │
│  Extras:  [Legend / Field names / Color-code] (multi-select)  │
└─────────────────────────────────────────────────────────┘
        │
        ▼
Claude builds optimized prompt from answers
        │
        ▼
Generate image with gathered requirements
```

### Example Questions for ERD

```
Question 1: "Which objects should be included in the ERD?"
- Core CRM (Account, Contact, Opportunity, Case) ← Recommended
- Sales Cloud (Lead, Campaign, Quote, Order)
- Service Cloud (Case, Knowledge, Entitlement, Asset)
- Custom objects (I'll specify)

Question 2: "What visual style do you prefer?"
- Professional (clean lines, SLDS colors) ← Recommended
- Whiteboard (hand-drawn, casual)
- Technical (with field names)
- Minimalist (simple boxes)

Question 3: "What's the primary purpose?"
- Documentation (4K quality)
- Quick draft (1K, fast iteration) ← Recommended for first attempt
- Presentation slides
- Architecture review

Question 4: "Any special requirements?" (multi-select)
- Include legend
- Show field names
- Color-code by object type
- None
```

### Skip Interview (Quick Mode)

To skip questions and use defaults, include these keywords:
- **"quick"** → `"Quick ERD of Account-Contact"`
- **"simple"** → `"Simple LWC mockup"`
- **"just generate"** → `"Just generate an architecture diagram"`

Quick mode uses: Professional style, 1K resolution, legend included.

### Full Question Reference

See `docs/interview-questions.md` for:
- Complete question sets for all image types
- Answer-to-prompt mapping tables
- Default values for skip mode

---

## Workflow Patterns

### Pattern A: Visual ERD Generation

**Trigger**: User asks for visual ERD, rendered diagram, or image-based data model

**Workflow**:
0. **Run Interview** (unless "quick" mode) - Ask about objects, style, purpose, extras
1. Run prerequisites check
2. Query object metadata via sf-metadata (if org connected)
3. Build Nano Banana prompt using interview answers + object relationships
4. Execute Gemini CLI with `/generate` command (requires --yolo flag)
5. **Open result in macOS Preview app using `open` command**

**Example**:
```bash
# Generate image
gemini --yolo "/generate 'Professional Salesforce ERD diagram showing:
   - Account (blue box, center)
   - Contact (green box, linked to Account with lookup arrow)
   - Opportunity (yellow box, linked to Account with master-detail thick arrow)
   Include legend. Clean white background, Salesforce Lightning style.'"

# Open in macOS Preview (DEFAULT)
open ~/nanobanana-output/[generated-file].png
```

### Pattern B: LWC Mockup

**Trigger**: User asks for component mockup, wireframe, or UI design

**Workflow**:
0. **Run Interview** (unless "quick" mode) - Ask about component type, object, context, style
1. Load appropriate template from `templates/lwc/`
2. Customize prompt using interview answers + template
3. Execute via Nano Banana
4. Open in Preview app

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
gemini --yolo "/generate 'description'"

# Images are saved to ~/nanobanana-output/
```

### Image Display

```bash
# Open in macOS Preview app (default)
open /path/to/image.png

# Open most recent generated image
open ~/nanobanana-output/$(ls -t ~/nanobanana-output/*.png | head -1)

# View inline in Claude Code conversation (multimodal vision)
# Use the Read tool → /path/to/image.png
```

---

## Cross-Skill Integration

| Skill | Integration | Usage |
|-------|-------------|-------|
| sf-diagram-mermaid | Enhance Mermaid with visual rendering | "Convert this Mermaid ERD to a visual diagram" |
| sf-metadata | Get object/field data for ERDs | Query org before generating ERD |
| sf-lwc | Generate component mockups | "Mockup for the AccountList component" |
| sf-apex | Review Apex code via Gemini | "Get Gemini's opinion on this trigger" |

---

## Helper Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `check-prerequisites.sh` | `scripts/` | Verify all requirements before use |
| `generate_image.py` | `scripts/` | Direct API script for 4K resolution and image editing |

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
- **No API Key**: Set GEMINI_API_KEY in ~/.zshrc (personal key from aistudio.google.com)
- **No Gemini CLI**: Install with npm
- **No Nano Banana**: Install extension via gemini CLI

### Image Not Opening
- Ensure you're on macOS (Preview app is macOS-only)
- Check the file path exists: `ls ~/nanobanana-output/`
- Try opening manually: `open ~/nanobanana-output/[filename].png`

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
