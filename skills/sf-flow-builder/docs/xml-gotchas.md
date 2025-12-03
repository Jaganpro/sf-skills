# Salesforce Flow XML Metadata Gotchas

Critical XML metadata constraints and known issues when deploying flows via Metadata API.

## recordLookups Conflicts

**NEVER use both** `<storeOutputAutomatically>` AND `<outputReference>` together.

**Choose ONE approach:**
```xml
<!-- Option 1: Auto-store (creates variable automatically) -->
<storeOutputAutomatically>true</storeOutputAutomatically>

<!-- Option 2: Explicit variable -->
<outputReference>varAccountRecord</outputReference>
```

## Element Ordering in recordLookups

Elements must follow this order:
1. `<name>` 2. `<label>` 3. `<locationX>` 4. `<locationY>` 5. `<assignNullValuesIfNoRecordsFound>` 6. `<connector>` 7. `<filterLogic>` 8. `<filters>` 9. `<getFirstRecordOnly>` 10. `<object>` 11. `<outputReference>` OR `<storeOutputAutomatically>` 12. `<queriedFields>`

## Transform Element

**Recommendation**: Create Transform elements in Flow Builder UI, then deploy - do NOT hand-write.

Issues with hand-written Transform:
- Complex nested XML structure with strict ordering
- `inputReference` placement varies by context
- Multiple conflicting rules in Metadata API

## Subflow Calling Limitation (Metadata API Constraint)

**Record-triggered flows (`processType="AutoLaunchedFlow"`) CANNOT call subflows via XML deployment.**

**Root Cause**: Salesforce Metadata API does not support the "flow" action type for AutoLaunchedFlow process types.

**Valid action types for AutoLaunchedFlow**: apex, chatterPost, emailAlert, emailSimple, and platform-specific actions - but NOT "flow".

**Error message**: "You can't use the Flows action type in flows with the Autolaunched Flow process type"

**Screen Flows (`processType="Flow"`) CAN call subflows** successfully via XML deployment.

**UI vs XML**: Flow Builder UI may use different internal mechanisms - UI capabilities may differ from direct XML deployment.

### Recommended Solution for Record-Triggered Flows

Use **inline orchestration** instead of subflows:

1. Organize logic into clear sections with descriptive element naming
2. Pattern: `Decision_CheckCriteria` → `Assignment_SetFields` → `Create_Record`
3. Add XML comments to delineate sections: `<!-- Section 1: Contact Creation -->`

**Benefits**: Single atomic flow, no deployment dependencies, full execution control.

**Reference**: [Salesforce Help Article 000396957](https://help.salesforce.com/s/articleView?id=000396957&type=1)

## Root-Level Element Ordering

Salesforce Metadata API requires **strict alphabetical ordering** at root level:

1. `<apiVersion>`
2. `<assignments>`
3. `<decisions>`
4. `<description>`
5. `<label>`
6. `<loops>`
7. `<processType>`
8. `<recordCreates>`
9. `<recordUpdates>`
10. `<start>`
11. `<status>`
12. `<variables>`

**Note**: API 60.0+ does NOT use `<bulkSupport>` - bulk processing is automatic.

## Common Deployment Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Element X is duplicated" | Elements not alphabetically ordered | Reorder elements |
| "Element bulkSupport invalid" | Using deprecated element (API 60.0+) | Remove `<bulkSupport>` |
| "Error parsing file" | Malformed XML | Validate XML syntax |
