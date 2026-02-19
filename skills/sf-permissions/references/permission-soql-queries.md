<!-- Parent: sf-permissions/SKILL.md -->

# Permission SOQL Queries

## Permission Set & Group Queries

```sql
-- All Permission Sets (excluding PSGs)
SELECT Id, Name, Label, Description, IsOwnedByProfile
FROM PermissionSet
WHERE IsOwnedByProfile = false AND Type != 'Group'

-- All Permission Set Groups
SELECT Id, DeveloperName, MasterLabel, Status, Description
FROM PermissionSetGroup

-- PSG Components (which PS are in which PSG)
SELECT PermissionSetGroupId, PermissionSetGroup.DeveloperName,
       PermissionSetId, PermissionSet.Name
FROM PermissionSetGroupComponent

-- User's PS Assignments
SELECT AssigneeId, PermissionSetId, PermissionSet.Name,
       PermissionSetGroupId, PermissionSetGroup.DeveloperName
FROM PermissionSetAssignment
WHERE AssigneeId = '005...'
```

## Object Permissions

```sql
-- Object permissions for a specific PS
SELECT SobjectType, PermissionsCreate, PermissionsRead,
       PermissionsEdit, PermissionsDelete,
       PermissionsViewAllRecords, PermissionsModifyAllRecords
FROM ObjectPermissions
WHERE ParentId = '0PS...'

-- Find PS with specific object access
SELECT Parent.Name, Parent.Label, SobjectType,
       PermissionsCreate, PermissionsRead, PermissionsEdit, PermissionsDelete
FROM ObjectPermissions
WHERE SobjectType = 'Account' AND PermissionsDelete = true
```

## Field Permissions

```sql
-- Field permissions for a specific PS
SELECT Field, PermissionsRead, PermissionsEdit
FROM FieldPermissions
WHERE ParentId = '0PS...'

-- Find PS with specific field access
SELECT Parent.Name, Field, PermissionsRead, PermissionsEdit
FROM FieldPermissions
WHERE Field = 'Account.AnnualRevenue' AND PermissionsEdit = true
```

## Setup Entity Access (Apex, VF, Flows, Custom Permissions)

```sql
-- Setup entity access for a PS
SELECT SetupEntityType, SetupEntityId
FROM SetupEntityAccess
WHERE ParentId = '0PS...'

-- Find PS with access to specific Apex class
SELECT Parent.Name, Parent.Label
FROM SetupEntityAccess
WHERE SetupEntityType = 'ApexClass'
AND SetupEntityId IN (SELECT Id FROM ApexClass WHERE Name = 'MyClass')

-- Custom permissions
SELECT Parent.Name
FROM SetupEntityAccess
WHERE SetupEntityType = 'CustomPermission'
AND SetupEntityId IN (SELECT Id FROM CustomPermission WHERE DeveloperName = 'Can_Approve')
```
