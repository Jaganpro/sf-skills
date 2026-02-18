<!-- Parent: sf-ai-agentscript/SKILL.md -->

# `complex_data_type_name` Mapping Table

> **"#1 source of compile errors"** - Use this table when defining action inputs/outputs in Agentforce Assets.

| Data Type | `complex_data_type_name` Value | Notes |
|-----------|-------------------------------|-------|
| `string` | *(none needed)* | Primitive type |
| `number` | *(none needed)* | Primitive type |
| `boolean` | *(none needed)* | Primitive type |
| `object` (SObject) | `lightning__recordInfoType` | Use for Account, Contact, etc. |
| `list[string]` | `lightning__textType` | Collection of text values |
| `list[object]` | `lightning__textType` | Serialized as JSON text |
| Apex Inner Class | `@apexClassType/NamespacedClass__InnerClass` | Namespace required |
| Custom LWC Type | `lightning__c__CustomTypeName` | Custom component types |
| Currency field | `lightning__currencyType` | For monetary values |
| `datetime` | `lightning__dateTimeStringType` | DateTime values (TDD v2.1.0) |

## Agent Script → Lightning Type Mapping (TDD Validated v2.1.0)

> Use this when troubleshooting type errors between Agent Script action I/O and Apex/Flow targets.

| Agent Script Type | Lightning Type | Apex Type | Notes |
|-------------------|---------------|-----------|-------|
| `string` | `lightning__textType` | `String` | No `complex_data_type_name` needed |
| `number` | `lightning__numberType` | `Decimal` / `Double` | No `complex_data_type_name` needed |
| `boolean` | `lightning__booleanType` | `Boolean` | No `complex_data_type_name` needed |
| `datetime` | `lightning__dateTimeStringType` | `DateTime` | **Actions only** — not valid for variables |
| `date` | `lightning__dateType` | `Date` | Valid for both variables and actions |
| `currency` | `lightning__currencyType` | `Decimal` | Annotated with currency type |

**Pro Tip**: Don't manually edit `complex_data_type_name` - use the UI dropdown in **Agentforce Assets > Action Definition**, then export/import the action definition.
