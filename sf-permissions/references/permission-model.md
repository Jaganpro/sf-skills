<!-- Parent: sf-permissions/SKILL.md -->
   1 # Salesforce Permission Model
   2 
   3 A guide to understanding how permissions work in Salesforce.
   4 
   5 ## Overview
   6 
   7 Salesforce uses a layered permission model:
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────┐
  11 │                      USER                           │
  12 ├─────────────────────────────────────────────────────┤
  13 │                    PROFILE                          │
  14 │  (Base permissions - one per user)                  │
  15 ├─────────────────────────────────────────────────────┤
  16 │           PERMISSION SET GROUPS                     │
  17 │  (Collections of Permission Sets)                   │
  18 ├─────────────────────────────────────────────────────┤
  19 │              PERMISSION SETS                        │
  20 │  (Additive permissions)                             │
  21 └─────────────────────────────────────────────────────┘
  22 ```
  23 
  24 ## Key Concepts
  25 
  26 ### Profiles
  27 
  28 - **One profile per user** (mandatory)
  29 - Defines base-level access
  30 - Can restrict or grant permissions
  31 - Legacy approach - Salesforce recommends minimal profiles + Permission Sets
  32 
  33 ### Permission Sets (PS)
  34 
  35 - **Additive only** - can grant access, cannot revoke
  36 - Multiple PS can be assigned to a user
  37 - Can include:
  38   - Object CRUD permissions
  39   - Field-Level Security (FLS)
  40   - Apex Class access
  41   - Visualforce Page access
  42   - Flow access
  43   - Custom Permissions
  44   - Tab visibility
  45   - System permissions
  46 
  47 ### Permission Set Groups (PSG)
  48 
  49 - **Container for multiple Permission Sets**
  50 - Assign one PSG instead of many individual PS
  51 - Simplifies user provisioning
  52 - Status can be "Active" or "Outdated"
  53 
  54 ## Permission Types
  55 
  56 ### Object Permissions
  57 
  58 | Permission | Description |
  59 |------------|-------------|
  60 | Create | Insert new records |
  61 | Read | View records |
  62 | Edit | Update existing records |
  63 | Delete | Remove records |
  64 | View All | Read all records regardless of sharing |
  65 | Modify All | Full access regardless of sharing |
  66 
  67 ### Field-Level Security (FLS)
  68 
  69 | Permission | Description |
  70 |------------|-------------|
  71 | Read | View field value |
  72 | Edit | Modify field value |
  73 
  74 Note: Edit includes Read access.
  75 
  76 ### Setup Entity Access
  77 
  78 Access to programmatic components:
  79 
  80 | Entity Type | Examples |
  81 |-------------|----------|
  82 | ApexClass | Controller classes, utility classes |
  83 | ApexPage | Visualforce pages |
  84 | Flow | Screen flows, autolaunched flows |
  85 | CustomPermission | Feature flags, custom access controls |
  86 
  87 ### System Permissions
  88 
  89 Organization-wide permissions like:
  90 
  91 - ViewSetup
  92 - ModifyAllData
  93 - ViewAllData
  94 - ManageUsers
  95 - ApiEnabled
  96 - RunReports
  97 - ExportReport
  98 
  99 ## Common Permission Patterns
 100 
 101 ### Sales User Pattern
 102 
 103 ```
 104 Permission Set Group: Sales_Cloud_User
 105 ├── Account_Access (PS)
 106 │   └── Account: CRUD
 107 ├── Opportunity_Access (PS)
 108 │   └── Opportunity: CRUD
 109 └── Report_Runner (PS)
 110     └── System: RunReports, ExportReport
 111 ```
 112 
 113 ### API Integration Pattern
 114 
 115 ```
 116 Permission Set: Integration_User
 117 ├── System: ApiEnabled
 118 ├── Objects: Read on required objects
 119 └── Custom Permission: API_Access_Enabled
 120 ```
 121 
 122 ### Admin Lite Pattern
 123 
 124 ```
 125 Permission Set: Admin_Lite
 126 ├── System: ViewSetup (NOT ModifyAllData)
 127 ├── System: ManageUsers
 128 └── Custom Permission: Can_Manage_Users
 129 ```
 130 
 131 ## Best Practices
 132 
 133 ### 1. Minimum Necessary Access
 134 
 135 Grant only the permissions users actually need.
 136 
 137 ### 2. Use Permission Set Groups
 138 
 139 Group related PS into PSGs for easier management:
 140 - `Sales_Cloud_User` (PSG) instead of 5 individual PS
 141 - `Service_Cloud_User` (PSG) for case management
 142 
 143 ### 3. Audit Regularly
 144 
 145 Use sf-permissions to:
 146 - Find PS with overly broad access (ModifyAllData)
 147 - Identify unused PS
 148 - Document permission structures
 149 
 150 ### 4. Naming Conventions
 151 
 152 ```
 153 Permission Set:     [Department]_[Capability]_PS
 154 Permission Set Group: [Department]_[Role]_PSG
 155 
 156 Examples:
 157   - Sales_Account_Edit_PS
 158   - Sales_Manager_PSG
 159   - HR_Employee_Data_Access_PS
 160 ```
 161 
 162 ### 5. Document Custom Permissions
 163 
 164 Custom Permissions should have clear names:
 165 - `Can_Approve_Expenses`
 166 - `View_Salary_Data`
 167 - `Export_Customer_Data`
 168 
 169 ## Related Salesforce Documentation
 170 
 171 - [Permission Sets](https://help.salesforce.com/s/articleView?id=sf.perm_sets_overview.htm)
 172 - [Permission Set Groups](https://help.salesforce.com/s/articleView?id=sf.perm_set_groups.htm)
 173 - [Field-Level Security](https://help.salesforce.com/s/articleView?id=sf.users_fields_fls.htm)
