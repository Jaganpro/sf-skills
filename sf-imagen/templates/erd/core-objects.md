# ERD Template: Core Salesforce Objects

## Prompt Template

```
Professional Salesforce ERD diagram showing:

OBJECTS:
- Account (blue box, center position)
  - Type: Standard Object
  - Role: Master record for customers/partners

- Contact (green box, linked to Account)
  - Type: Standard Object
  - Relationship: Lookup to Account (optional parent)

- Opportunity (yellow box, linked to Account)
  - Type: Standard Object
  - Relationship: Master-Detail to Account (required parent)

- Case (orange box, linked to Account and Contact)
  - Type: Standard Object
  - Relationship: Lookup to Account, Lookup to Contact

RELATIONSHIPS:
- Lookup: Dashed arrow (---->)
- Master-Detail: Solid thick arrow (====>)

STYLING:
- Clean white background
- Pastel fill colors with dark borders
- Clear labels on relationship arrows
- Professional diagram layout
- Include legend in corner

FORMAT:
- Landscape orientation
- Centered composition
- Readable text at normal zoom
```

## Usage

```bash
gemini "/generate '[paste prompt above with customizations]'"
timg ~/gemini-images/[generated-file].png
```
