<!-- Parent: sf-permissions/SKILL.md -->
# Permission SOQL Reference

Quick reference for SOQL queries used in sf-permissions.

## Permission Set Queries

### List All Permission Sets

```sql
SELECT Id, Name, Label, Description, IsOwnedByProfile, Type
FROM PermissionSet
WHERE IsOwnedByProfile = false
ORDER BY Label
```

### List Permission Set Groups

```sql
SELECT Id, DeveloperName, MasterLabel, Status, Description
FROM PermissionSetGroup
ORDER BY MasterLabel
```

### Get PSG Components (PS in a Group)

```sql
SELECT
    PermissionSetGroupId,
    PermissionSetGroup.DeveloperName,
    PermissionSetId,
    PermissionSet.Name,
    PermissionSet.Label
FROM PermissionSetGroupComponent
```

### Get User's Permission Set Assignments

```sql
SELECT
    AssigneeId,
    PermissionSetId,
    PermissionSet.Name,
    PermissionSetGroupId,
    PermissionSetGroup.DeveloperName
FROM PermissionSetAssignment
WHERE AssigneeId = '005xx...'
AND PermissionSet.IsOwnedByProfile = false
```

## Object Permission Queries

### Get All Object Permissions for a PS

```sql
SELECT
    SobjectType,
    PermissionsCreate,
    PermissionsRead,
    PermissionsEdit,
    PermissionsDelete,
    PermissionsViewAllRecords,
    PermissionsModifyAllRecords
FROM ObjectPermissions
WHERE ParentId = '0PS...'
ORDER BY SobjectType
```

### Find PS with Specific Object Access

```sql
SELECT
    Parent.Name,
    Parent.Label,
    SobjectType,
    PermissionsDelete
FROM ObjectPermissions
WHERE SobjectType = 'Account'
AND PermissionsDelete = true
```

## Field Permission Queries

### Get Field Permissions for a PS

```sql
SELECT Field, PermissionsRead, PermissionsEdit
FROM FieldPermissions
WHERE ParentId = '0PS...'
ORDER BY Field
```

### Find PS with Specific Field Access

```sql
SELECT
    Parent.Name,
    Parent.Label,
    Field,
    PermissionsRead,
    PermissionsEdit
FROM FieldPermissions
WHERE Field = 'Account.AnnualRevenue'
AND PermissionsEdit = true
```

## Setup Entity Access Queries

### Get All Setup Entity Access for a PS

```sql
SELECT SetupEntityType, SetupEntityId
FROM SetupEntityAccess
WHERE ParentId = '0PS...'
```

### Find PS with Apex Class Access

```sql
SELECT Parent.Name, Parent.Label
FROM SetupEntityAccess
WHERE SetupEntityType = 'ApexClass'
AND SetupEntityId IN (
    SELECT Id FROM ApexClass WHERE Name = 'MyApexClass'
)
```

### Find PS with Custom Permission

```sql
SELECT Parent.Name, Parent.Label
FROM SetupEntityAccess
WHERE SetupEntityType = 'CustomPermission'
AND SetupEntityId IN (
    SELECT Id FROM CustomPermission WHERE DeveloperName = 'Can_Approve'
)
```

### Find PS with Visualforce Page Access

```sql
SELECT Parent.Name, Parent.Label
FROM SetupEntityAccess
WHERE SetupEntityType = 'ApexPage'
AND SetupEntityId IN (
    SELECT Id FROM ApexPage WHERE Name = 'MyVFPage'
)
```

### Find PS with Flow Access

```sql
SELECT Parent.Name, Parent.Label
FROM SetupEntityAccess
WHERE SetupEntityType = 'Flow'
AND SetupEntityId = '301xx...'  -- Active Flow Version ID
```

## User Count Queries

### Count Users per Permission Set

```sql
SELECT PermissionSetId, COUNT(AssigneeId) userCount
FROM PermissionSetAssignment
GROUP BY PermissionSetId
```

### Count Users per Permission Set Group

```sql
SELECT PermissionSetGroupId, COUNT(AssigneeId) userCount
FROM PermissionSetAssignment
WHERE PermissionSetGroupId != null
GROUP BY PermissionSetGroupId
```

## System Permission Queries

### Find PS with ModifyAllData

```sql
SELECT Id, Name, Label
FROM PermissionSet
WHERE PermissionsModifyAllData = true
AND IsOwnedByProfile = false
```

### Find PS with ViewSetup

```sql
SELECT Id, Name, Label
FROM PermissionSet
WHERE PermissionsViewSetup = true
AND IsOwnedByProfile = false
```

## Metadata Queries

### List All Custom Permissions

```sql
SELECT Id, DeveloperName, MasterLabel, Description
FROM CustomPermission
ORDER BY MasterLabel
```

### List All Apex Classes

```sql
SELECT Id, Name, NamespacePrefix, IsValid
FROM ApexClass
ORDER BY Name
```

### List All Flows (with Active Version)

```sql
SELECT Id, DeveloperName, MasterLabel, ProcessType, ActiveVersionId
FROM FlowDefinition
WHERE ActiveVersionId != null
ORDER BY MasterLabel
```

## Entity Definition Queries

### List Customizable Objects

```sql
SELECT QualifiedApiName, Label
FROM EntityDefinition
WHERE IsCustomizable = true
ORDER BY Label
```

### Get Fields for an Object

```sql
SELECT QualifiedApiName, Label, DataType
FROM FieldDefinition
WHERE EntityDefinition.QualifiedApiName = 'Account'
ORDER BY Label
```

## Notes

- All permission queries are **read-only** - they don't modify data
- `ParentId` in ObjectPermissions/FieldPermissions refers to the Permission Set ID
- `SetupEntityId` is the ID of the Apex Class, VF Page, Flow, or Custom Permission
- System permissions are fields on the PermissionSet object (e.g., `PermissionsModifyAllData`)
