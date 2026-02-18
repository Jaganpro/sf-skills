<!-- Parent: sf-flow/SKILL.md -->

# LWC & Apex Integration Patterns

## LWC Integration (Screen Flows)

Embed custom Lightning Web Components in Flow Screens for rich, interactive UIs.

### Templates

| Template | Purpose |
|----------|---------|
| `templates/screen-flow-with-lwc.xml` | Flow embedding LWC component |
| `templates/apex-action-template.xml` | Flow calling Apex @InvocableMethod |

### Flow XML Pattern

```xml
<screens>
    <fields>
        <extensionName>c:recordSelector</extensionName>
        <fieldType>ComponentInstance</fieldType>
        <inputParameters>
            <name>recordId</name>
            <value><elementReference>var_RecordId</elementReference></value>
        </inputParameters>
        <outputParameters>
            <assignToReference>var_SelectedId</assignToReference>
            <name>selectedRecordId</name>
        </outputParameters>
    </fields>
</screens>
```

### Documentation

| Resource | Location |
|----------|----------|
| LWC Integration Guide | [docs/lwc-integration-guide.md](../docs/lwc-integration-guide.md) |
| LWC Component Setup | [sf-lwc/docs/flow-integration-guide.md](../../sf-lwc/docs/flow-integration-guide.md) |
| Triangle Architecture | [docs/triangle-pattern.md](../docs/triangle-pattern.md) |

---

## Apex Integration

Call Apex `@InvocableMethod` classes from Flow for complex business logic.

### Flow XML Pattern

```xml
<actionCalls>
    <name>Process_Record</name>
    <actionName>RecordProcessor</actionName>
    <actionType>apex</actionType>
    <inputParameters>
        <name>recordId</name>
        <value><elementReference>var_RecordId</elementReference></value>
    </inputParameters>
    <outputParameters>
        <assignToReference>var_IsSuccess</assignToReference>
        <name>isSuccess</name>
    </outputParameters>
    <faultConnector>
        <targetReference>Handle_Error</targetReference>
    </faultConnector>
</actionCalls>
```

### Documentation

| Resource | Location |
|----------|----------|
| Apex Action Template | `templates/apex-action-template.xml` |
| Apex @InvocableMethod Guide | [sf-apex/docs/flow-integration.md](../../sf-apex/docs/flow-integration.md) |
| Triangle Architecture | [docs/triangle-pattern.md](../docs/triangle-pattern.md) |
