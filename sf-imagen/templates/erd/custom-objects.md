# ERD Template: Custom Objects

## Prompt Template

```
Professional Salesforce ERD diagram showing custom objects:

OBJECTS:
[List custom objects with relationships]

COLOR CODING:
- Standard Objects: Blue (#bae6fd fill, #0369a1 border)
- Custom Objects: Orange (#fed7aa fill, #c2410c border)
- External Objects: Green (#a7f3d0 fill, #047857 border)

RELATIONSHIPS:
- Lookup (LK): Dashed arrow, optional parent
- Master-Detail (MD): Solid thick arrow, cascade delete

STYLING:
- Clean white background
- Pastel fill colors with dark borders
- Relationship labels on arrows
- Professional diagram layout
- Include color legend

FORMAT:
- Auto-layout based on relationships
- Primary objects centered
- Child objects positioned below/right of parents
```

## Example

```bash
gemini "/generate 'Salesforce ERD for real estate app:
- Property__c (orange, center): Main custom object
- Listing__c (orange, right): Master-Detail to Property__c
- Showing__c (orange, below): Lookup to both Property__c and Contact

Orange boxes for custom objects, blue for standard (Contact).
Include legend. Professional style.'"
```
