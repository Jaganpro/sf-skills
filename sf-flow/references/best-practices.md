<!-- Parent: sf-flow/SKILL.md -->

# Best Practices (Built-In Enforcement)

## CRITICAL: Record-Triggered Flow Architecture

**NEVER loop over triggered records.** `$Record` = single record; platform handles batching.

| Pattern | OK? | Notes |
|---------|-----|-------|
| `$Record.FieldName` | ✅ | Direct access |
| Loop over `$Record__c` | ❌ | Process Builder pattern, not Flow |
| Loop over `$Record` | ❌ | $Record is single, not collection |

**Loops for RELATED records only**: Get Records → Loop collection → Assignment → DML after loop

## CRITICAL: No Parent Traversal in Get Records

`recordLookups` cannot query `Parent.Field` (e.g., `Manager.Name`). **Solution**: Two Get Records - child first, then parent by Id.

## recordLookups Best Practices

| Element | Recommendation | Why |
|---------|----------------|-----|
| `getFirstRecordOnly` | Set to `true` for single-record queries | Avoids collection overhead |
| `storeOutputAutomatically` | Set to `false`, use `outputReference` | Prevents data leaks, explicit variable |
| `assignNullValuesIfNoRecordsFound` | Set to `false` | Preserves previous variable value |
| `faultConnector` | Always include | Handle query failures gracefully |
| `filterLogic` | Use `and` for multiple filters | Clear filter behavior |

## Critical Requirements
- **API 65.0**: Latest features
- **No DML in Loops**: Collect in loop → DML after loop (causes bulk failures otherwise)
- **Bulkify**: For RELATED records only - platform handles triggered record batching
- **Fault Paths**: All DML must have fault connectors
  - Fault connectors CANNOT self-reference - Route to DIFFERENT element
- **Auto-Layout**: All locationX/Y = 0 (cleaner git diffs)
- **No Parent Traversal**: Use separate Get Records for relationship field data

## XML Element Ordering (CRITICAL)

**All elements of the same type MUST be grouped together.**

Complete alphabetical order:
```
apiVersion → assignments → constants → decisions → description → environments →
formulas → interviewLabel → label → loops → processMetadataValues → processType →
recordCreates → recordDeletes → recordLookups → recordUpdates → runInMode →
screens → start → status → subflows → textTemplates → variables → waits
```

**Common Mistake**: Adding an assignment near related logic when other assignments exist earlier.
- **Error**: "Element assignments is duplicated at this location"
- **Fix**: Move ALL assignments to the assignments section

## Performance
- **Batch DML**: Get Records → Assignment → Update Records pattern
- **Filters over loops**: Use Get Records with filters instead of loops + decisions
- **Transform element**: Powerful but complex XML - NOT recommended for hand-written flows

## Design & Security
- **Variable Names (v2.0.0)**: Use prefixes:
  - `var_` Regular variables, `col_` Collections, `rec_` Record variables
  - `inp_` Input variables, `out_` Output variables
- **Element Names**: PascalCase_With_Underscores (e.g., `Check_Account_Type`)
- **Button Names (v2.0.0)**: `Action_[Verb]_[Object]` (e.g., `Action_Save_Contact`)
- **System vs User Mode**: Understand implications, validate FLS for sensitive fields
- See `docs/flow-best-practices.md` for comprehensive guidance
