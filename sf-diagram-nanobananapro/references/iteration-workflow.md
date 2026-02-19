<!-- Parent: sf-diagram-nanobananapro/SKILL.md -->
   1 # Iteration Workflow: Draft → Final
   2 
   3 Best practices for cost-effective image generation with sf-diagram-nanobananapro.
   4 
   5 ## Why Iterate at Low Resolution?
   6 
   7 | Resolution | Time | API Cost | Use Case |
   8 |------------|------|----------|----------|
   9 | **1K** | ~3s | $ | Drafts, prompt refinement, layout testing |
  10 | **2K** | ~5s | $$ | Medium quality, quick presentations |
  11 | **4K** | ~10s | $$$ | Production, documentation, final deliverables |
  12 
  13 **Key Insight**: Get the prompt right at 1K before spending on 4K generation.
  14 
  15 ---
  16 
  17 ## The Workflow
  18 
  19 ```
  20 ┌─────────────────────────────────────────────────────────────┐
  21 │                     DRAFT PHASE (1K)                        │
  22 │                                                             │
  23 │  1. Generate initial image with CLI                         │
  24 │     gemini --yolo "/generate 'Your prompt...'"              │
  25 │                                                             │
  26 │  2. Review in Preview                                       │
  27 │     open ~/nanobanana-output/*.png                          │
  28 │                                                             │
  29 │  3. Is the layout correct? ─────────────────┐               │
  30 │     │                                       │               │
  31 │     ▼ No                                    ▼ Yes           │
  32 │     Refine prompt or use /edit              Continue        │
  33 │     └──────────────────────────────────────►│               │
  34 └─────────────────────────────────────────────┼───────────────┘
  35                                               │
  36                                               ▼
  37 ┌─────────────────────────────────────────────────────────────┐
  38 │                    FINAL PHASE (4K)                         │
  39 │                                                             │
  40 │  4. Generate production quality with Python script          │
  41 │     uv run scripts/generate_image.py \                      │
  42 │       -p "Your refined prompt" \                            │
  43 │       -f "final-output.png" \                               │
  44 │       -r 4K                                                 │
  45 │                                                             │
  46 │  5. Open and use                                            │
  47 │     open ~/nanobanana-output/*final-output*.png             │
  48 └─────────────────────────────────────────────────────────────┘
  49 ```
  50 
  51 ---
  52 
  53 ## Common Iteration Patterns
  54 
  55 ### Pattern 1: Prompt Refinement
  56 
  57 ```bash
  58 # Attempt 1: Too generic
  59 gemini --yolo "/generate 'Account ERD'"
  60 # Result: Missing relationships, wrong colors
  61 
  62 # Attempt 2: Add specifics
  63 gemini --yolo "/generate 'Account ERD with Contact and Opportunity, blue boxes'"
  64 # Result: Better, but legend missing
  65 
  66 # Attempt 3: Add styling details
  67 gemini --yolo "/generate 'Salesforce ERD: Account (blue, center), Contact (green),
  68 Opportunity (yellow). Master-detail = thick arrow. Lookup = dashed. Include legend.'"
  69 # Result: Perfect layout!
  70 
  71 # Final: Generate at 4K
  72 uv run scripts/generate_image.py \
  73   -p "Salesforce ERD: Account (blue, center)..." \
  74   -f "crm-erd-final.png" \
  75   -r 4K
  76 ```
  77 
  78 ### Pattern 2: Edit-Based Iteration
  79 
  80 ```bash
  81 # Start with basic ERD
  82 gemini --yolo "/generate 'Account-Contact ERD'"
  83 
  84 # Edit to add more objects
  85 gemini --yolo "/edit 'Add Opportunity linked to Account with master-detail'"
  86 
  87 # Edit to improve styling
  88 gemini --yolo "/edit 'Add legend, use Salesforce Lightning blue (#0176D3)'"
  89 
  90 # Final at 4K
  91 uv run scripts/generate_image.py \
  92   -p "Account-Contact-Opportunity ERD with legend, SLDS colors" \
  93   -f "final-erd.png" \
  94   -r 4K
  95 ```
  96 
  97 ### Pattern 3: Python Script for Editing
  98 
  99 ```bash
 100 # Generate at 1K
 101 uv run scripts/generate_image.py \
 102   -p "Dashboard mockup with charts" \
 103   -f "dashboard-v1.png"
 104 
 105 # Edit with resolution control
 106 uv run scripts/generate_image.py \
 107   -p "Add a KPI summary bar at the top" \
 108   -i ~/nanobanana-output/*dashboard-v1*.png \
 109   -f "dashboard-v2.png" \
 110   -r 2K
 111 
 112 # Final version
 113 uv run scripts/generate_image.py \
 114   -p "Polish: add subtle shadows, round corners on cards" \
 115   -i ~/nanobanana-output/*dashboard-v2*.png \
 116   -f "dashboard-final.png" \
 117   -r 4K
 118 ```
 119 
 120 ---
 121 
 122 ## Timestamp Filenames
 123 
 124 The Python script automatically adds timestamps for easy versioning:
 125 
 126 ```
 127 ~/nanobanana-output/
 128 ├── 2026-01-13-10-30-15-erd-v1.png      # First attempt
 129 ├── 2026-01-13-10-32-45-erd-v2.png      # After edit
 130 ├── 2026-01-13-10-35-00-erd-final.png   # Production 4K
 131 ```
 132 
 133 **Tip**: Use descriptive filenames like `crm-erd.png` - the timestamp is auto-prepended.
 134 
 135 ---
 136 
 137 ## When to Use Each Method
 138 
 139 | Method | Best For |
 140 |--------|----------|
 141 | **CLI (`gemini --yolo`)** | Quick drafts, simple edits, style exploration |
 142 | **CLI `/edit`** | Iterative refinements of existing images |
 143 | **Python script** | 4K output, precise resolution control, automated workflows |
 144 
 145 ---
 146 
 147 ## Cost Optimization Tips
 148 
 149 1. **Never generate 4K on first attempt** - always draft at 1K first
 150 2. **Use `/edit` for small changes** - cheaper than regenerating
 151 3. **Batch similar requests** - get all ERDs right before final generation
 152 4. **Save working prompts** - reuse successful prompt patterns
 153 5. **Use `--seed` for reproducibility** - same seed = similar output
 154 
 155 ---
 156 
 157 ## Troubleshooting
 158 
 159 ### Image doesn't match prompt
 160 - Add more specific details (colors, positions, relationships)
 161 - Use SLDS color codes: `#0176D3` (blue), `#04844B` (green), `#FFB75D` (yellow)
 162 - Specify layout: "center", "top-right", "below parent"
 163 
 164 ### Edit not applying correctly
 165 - Be specific about what to change
 166 - Reference existing elements: "Move the Account box to center"
 167 - One change at a time for precision
 168 
 169 ### 4K output looks different from 1K draft
 170 - Use exact same prompt text
 171 - Consider using `--seed` for consistency
 172 - Minor variations are normal due to model behavior
