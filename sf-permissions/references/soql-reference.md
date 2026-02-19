<!-- Parent: sf-permissions/SKILL.md -->
   1 # Permission SOQL Reference
   2 
   3 Quick reference for SOQL queries used in sf-permissions.
   4 
   5 ## Permission Set Queries
   6 
   7 ### List All Permission Sets
   8 
   9 ```sql
  10 SELECT Id, Name, Label, Description, IsOwnedByProfile, Type
  11 FROM PermissionSet
  12 WHERE IsOwnedByProfile = false
  13 ORDER BY Label
  14 ```
  15 
  16 ### List Permission Set Groups
  17 
  18 ```sql
  19 SELECT Id, DeveloperName, MasterLabel, Status, Description
  20 FROM PermissionSetGroup
  21 ORDER BY MasterLabel
  22 ```
  23 
  24 ### Get PSG Components (PS in a Group)
  25 
  26 ```sql
  27 SELECT
  28     PermissionSetGroupId,
  29     PermissionSetGroup.DeveloperName,
  30     PermissionSetId,
  31     PermissionSet.Name,
  32     PermissionSet.Label
  33 FROM PermissionSetGroupComponent
  34 ```
  35 
  36 ### Get User's Permission Set Assignments
  37 
  38 ```sql
  39 SELECT
  40     AssigneeId,
  41     PermissionSetId,
  42     PermissionSet.Name,
  43     PermissionSetGroupId,
  44     PermissionSetGroup.DeveloperName
  45 FROM PermissionSetAssignment
  46 WHERE AssigneeId = '005xx...'
  47 AND PermissionSet.IsOwnedByProfile = false
  48 ```
  49 
  50 ## Object Permission Queries
  51 
  52 ### Get All Object Permissions for a PS
  53 
  54 ```sql
  55 SELECT
  56     SobjectType,
  57     PermissionsCreate,
  58     PermissionsRead,
  59     PermissionsEdit,
  60     PermissionsDelete,
  61     PermissionsViewAllRecords,
  62     PermissionsModifyAllRecords
  63 FROM ObjectPermissions
  64 WHERE ParentId = '0PS...'
  65 ORDER BY SobjectType
  66 ```
  67 
  68 ### Find PS with Specific Object Access
  69 
  70 ```sql
  71 SELECT
  72     Parent.Name,
  73     Parent.Label,
  74     SobjectType,
  75     PermissionsDelete
  76 FROM ObjectPermissions
  77 WHERE SobjectType = 'Account'
  78 AND PermissionsDelete = true
  79 ```
  80 
  81 ## Field Permission Queries
  82 
  83 ### Get Field Permissions for a PS
  84 
  85 ```sql
  86 SELECT Field, PermissionsRead, PermissionsEdit
  87 FROM FieldPermissions
  88 WHERE ParentId = '0PS...'
  89 ORDER BY Field
  90 ```
  91 
  92 ### Find PS with Specific Field Access
  93 
  94 ```sql
  95 SELECT
  96     Parent.Name,
  97     Parent.Label,
  98     Field,
  99     PermissionsRead,
 100     PermissionsEdit
 101 FROM FieldPermissions
 102 WHERE Field = 'Account.AnnualRevenue'
 103 AND PermissionsEdit = true
 104 ```
 105 
 106 ## Setup Entity Access Queries
 107 
 108 ### Get All Setup Entity Access for a PS
 109 
 110 ```sql
 111 SELECT SetupEntityType, SetupEntityId
 112 FROM SetupEntityAccess
 113 WHERE ParentId = '0PS...'
 114 ```
 115 
 116 ### Find PS with Apex Class Access
 117 
 118 ```sql
 119 SELECT Parent.Name, Parent.Label
 120 FROM SetupEntityAccess
 121 WHERE SetupEntityType = 'ApexClass'
 122 AND SetupEntityId IN (
 123     SELECT Id FROM ApexClass WHERE Name = 'MyApexClass'
 124 )
 125 ```
 126 
 127 ### Find PS with Custom Permission
 128 
 129 ```sql
 130 SELECT Parent.Name, Parent.Label
 131 FROM SetupEntityAccess
 132 WHERE SetupEntityType = 'CustomPermission'
 133 AND SetupEntityId IN (
 134     SELECT Id FROM CustomPermission WHERE DeveloperName = 'Can_Approve'
 135 )
 136 ```
 137 
 138 ### Find PS with Visualforce Page Access
 139 
 140 ```sql
 141 SELECT Parent.Name, Parent.Label
 142 FROM SetupEntityAccess
 143 WHERE SetupEntityType = 'ApexPage'
 144 AND SetupEntityId IN (
 145     SELECT Id FROM ApexPage WHERE Name = 'MyVFPage'
 146 )
 147 ```
 148 
 149 ### Find PS with Flow Access
 150 
 151 ```sql
 152 SELECT Parent.Name, Parent.Label
 153 FROM SetupEntityAccess
 154 WHERE SetupEntityType = 'Flow'
 155 AND SetupEntityId = '301xx...'  -- Active Flow Version ID
 156 ```
 157 
 158 ## User Count Queries
 159 
 160 ### Count Users per Permission Set
 161 
 162 ```sql
 163 SELECT PermissionSetId, COUNT(AssigneeId) userCount
 164 FROM PermissionSetAssignment
 165 GROUP BY PermissionSetId
 166 ```
 167 
 168 ### Count Users per Permission Set Group
 169 
 170 ```sql
 171 SELECT PermissionSetGroupId, COUNT(AssigneeId) userCount
 172 FROM PermissionSetAssignment
 173 WHERE PermissionSetGroupId != null
 174 GROUP BY PermissionSetGroupId
 175 ```
 176 
 177 ## System Permission Queries
 178 
 179 ### Find PS with ModifyAllData
 180 
 181 ```sql
 182 SELECT Id, Name, Label
 183 FROM PermissionSet
 184 WHERE PermissionsModifyAllData = true
 185 AND IsOwnedByProfile = false
 186 ```
 187 
 188 ### Find PS with ViewSetup
 189 
 190 ```sql
 191 SELECT Id, Name, Label
 192 FROM PermissionSet
 193 WHERE PermissionsViewSetup = true
 194 AND IsOwnedByProfile = false
 195 ```
 196 
 197 ## Metadata Queries
 198 
 199 ### List All Custom Permissions
 200 
 201 ```sql
 202 SELECT Id, DeveloperName, MasterLabel, Description
 203 FROM CustomPermission
 204 ORDER BY MasterLabel
 205 ```
 206 
 207 ### List All Apex Classes
 208 
 209 ```sql
 210 SELECT Id, Name, NamespacePrefix, IsValid
 211 FROM ApexClass
 212 ORDER BY Name
 213 ```
 214 
 215 ### List All Flows (with Active Version)
 216 
 217 ```sql
 218 SELECT Id, DeveloperName, MasterLabel, ProcessType, ActiveVersionId
 219 FROM FlowDefinition
 220 WHERE ActiveVersionId != null
 221 ORDER BY MasterLabel
 222 ```
 223 
 224 ## Entity Definition Queries
 225 
 226 ### List Customizable Objects
 227 
 228 ```sql
 229 SELECT QualifiedApiName, Label
 230 FROM EntityDefinition
 231 WHERE IsCustomizable = true
 232 ORDER BY Label
 233 ```
 234 
 235 ### Get Fields for an Object
 236 
 237 ```sql
 238 SELECT QualifiedApiName, Label, DataType
 239 FROM FieldDefinition
 240 WHERE EntityDefinition.QualifiedApiName = 'Account'
 241 ORDER BY Label
 242 ```
 243 
 244 ## Notes
 245 
 246 - All permission queries are **read-only** - they don't modify data
 247 - `ParentId` in ObjectPermissions/FieldPermissions refers to the Permission Set ID
 248 - `SetupEntityId` is the ID of the Apex Class, VF Page, Flow, or Custom Permission
 249 - System permissions are fields on the PermissionSet object (e.g., `PermissionsModifyAllData`)
