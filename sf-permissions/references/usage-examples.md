<!-- Parent: sf-permissions/SKILL.md -->
   1 # sf-permissions Usage Examples
   2 
   3 Real-world examples of using sf-permissions for permission analysis.
   4 
   5 ## CLI Examples
   6 
   7 ### 1. View Org Permission Hierarchy
   8 
   9 ```bash
  10 # ASCII tree output (default)
  11 python cli.py hierarchy
  12 
  13 # Mermaid diagram for documentation
  14 python cli.py hierarchy --format mermaid > hierarchy.md
  15 
  16 # Specify target org
  17 python cli.py hierarchy --target-org my-sandbox
  18 ```
  19 
  20 ### 2. Permission Detection
  21 
  22 #### Object Permissions
  23 
  24 ```bash
  25 # Who has delete access to Account?
  26 python cli.py detect object Account --access delete
  27 
  28 # Who has any access to a custom object?
  29 python cli.py detect object My_Custom_Object__c
  30 
  31 # Who has Create, Read, Update access to Opportunity?
  32 python cli.py detect object Opportunity --access create,read,edit
  33 ```
  34 
  35 #### Field Permissions
  36 
  37 ```bash
  38 # Who can edit Account.AnnualRevenue?
  39 python cli.py detect field Account.AnnualRevenue --access edit
  40 
  41 # Who has read access to a sensitive field?
  42 python cli.py detect field Contact.SSN__c --access read
  43 ```
  44 
  45 #### Apex Class Access
  46 
  47 ```bash
  48 # Who has access to a specific Apex class?
  49 python cli.py detect apex MyApexController
  50 ```
  51 
  52 #### Custom Permissions
  53 
  54 ```bash
  55 # Who has a custom permission?
  56 python cli.py detect custom Can_Approve_Expenses
  57 ```
  58 
  59 #### System Permissions
  60 
  61 ```bash
  62 # Who has ModifyAllData (dangerous permission)?
  63 python cli.py detect system ModifyAllData
  64 
  65 # Who can view setup?
  66 python cli.py detect system ViewSetup
  67 ```
  68 
  69 ### 3. User Analysis
  70 
  71 ```bash
  72 # Analyze permissions for a specific user
  73 python cli.py user john.smith@company.com
  74 
  75 # Use user ID
  76 python cli.py user 005xx000001234AAA
  77 
  78 # Mermaid output
  79 python cli.py user john.smith@company.com --format mermaid
  80 ```
  81 
  82 ### 4. Export Permission Sets
  83 
  84 ```bash
  85 # Export to CSV
  86 python cli.py export Sales_Manager -o /tmp/sales_manager.csv
  87 
  88 # Export to JSON
  89 python cli.py export Sales_Manager -o /tmp/sales_manager.json
  90 ```
  91 
  92 ### 5. Permission Set Details
  93 
  94 ```bash
  95 # View Permission Set details
  96 python cli.py ps Sales_Manager
  97 
  98 # View Permission Set Group details
  99 python cli.py psg Sales_Cloud_User
 100 
 101 # List users with a Permission Set
 102 python cli.py users Sales_Manager
 103 ```
 104 
 105 ---
 106 
 107 ## Python API Examples
 108 
 109 ### Connect to Salesforce
 110 
 111 ```python
 112 from auth import get_sf_connection
 113 
 114 # Use default org
 115 sf = get_sf_connection()
 116 
 117 # Use specific org
 118 sf = get_sf_connection('my-sandbox')
 119 ```
 120 
 121 ### Build Permission Hierarchy
 122 
 123 ```python
 124 from hierarchy_viewer import get_org_permission_hierarchy
 125 
 126 hierarchy = get_org_permission_hierarchy(sf)
 127 
 128 print(f"PSGs: {hierarchy.total_psg_count}")
 129 print(f"Total PS: {hierarchy.total_ps_count}")
 130 
 131 for psg in hierarchy.permission_set_groups:
 132     print(f"  {psg.master_label} ({len(psg.permission_sets)} PS)")
 133 ```
 134 
 135 ### Detect Permissions
 136 
 137 ```python
 138 from permission_detector import (
 139     detect_object_permission,
 140     detect_field_permission,
 141     detect_apex_class_permission,
 142     detect_custom_permission,
 143 )
 144 
 145 # Find PS with Account delete
 146 results = detect_object_permission(sf, 'Account', ['delete'])
 147 
 148 for r in results:
 149     print(f"{r.permission_set_label}: {r.assigned_user_count} users")
 150     if r.is_in_group:
 151         print(f"  In group: {r.group_label}")
 152 
 153 # Find PS with field edit access
 154 results = detect_field_permission(sf, 'Account', 'AnnualRevenue', ['edit'])
 155 
 156 # Find PS with Apex access
 157 results = detect_apex_class_permission(sf, 'MyController')
 158 
 159 # Find PS with custom permission
 160 results = detect_custom_permission(sf, 'Can_Approve_Expenses')
 161 ```
 162 
 163 ### Analyze User Permissions
 164 
 165 ```python
 166 from user_analyzer import analyze_user_permissions, compare_user_permissions
 167 
 168 # Analyze single user
 169 analysis = analyze_user_permissions(sf, 'john@company.com')
 170 
 171 print(f"User: {analysis.user.name}")
 172 print(f"Profile: {analysis.user.profile_name}")
 173 print(f"Total PS: {analysis.total_permission_sets}")
 174 
 175 # Via groups
 176 for group in analysis.via_groups:
 177     print(f"Via {group['label']}:")
 178     for ps in group['permission_sets']:
 179         print(f"  - {ps['label']}")
 180 
 181 # Direct assignments
 182 for ps in analysis.direct_assignments:
 183     print(f"Direct: {ps.label}")
 184 
 185 # Compare two users
 186 comparison = compare_user_permissions(sf, 'user1@company.com', 'user2@company.com')
 187 print(f"Shared: {len(comparison['shared'])} PS")
 188 print(f"User1 only: {len(comparison['ps1_only'])} PS")
 189 print(f"User2 only: {len(comparison['ps2_only'])} PS")
 190 ```
 191 
 192 ### Export to Files
 193 
 194 ```python
 195 from permission_exporter import (
 196     export_permission_set_to_csv,
 197     export_permission_set_to_json,
 198     compare_permission_sets,
 199 )
 200 
 201 # Export to CSV
 202 path = export_permission_set_to_csv(sf, 'Sales_Manager', '/tmp/sm.csv')
 203 
 204 # Export to JSON
 205 path = export_permission_set_to_json(sf, 'Sales_Manager', '/tmp/sm.json')
 206 
 207 # Compare two PS
 208 diff = compare_permission_sets(sf, 'Sales_Manager', 'Sales_Rep')
 209 print(f"Differences: {len(diff['ps1_only'])} in SM only")
 210 ```
 211 
 212 ### Render Output
 213 
 214 ```python
 215 from renderers.ascii_tree import (
 216     render_hierarchy_tree,
 217     render_detection_table,
 218     render_user_tree,
 219 )
 220 from renderers.mermaid import (
 221     render_hierarchy_mermaid,
 222     render_user_mermaid,
 223 )
 224 
 225 # ASCII output (Rich library)
 226 render_hierarchy_tree(hierarchy)
 227 render_user_tree(analysis)
 228 render_detection_table(results, "Account delete access")
 229 
 230 # Mermaid diagrams
 231 mermaid_code = render_hierarchy_mermaid(hierarchy)
 232 print(mermaid_code)  # Paste into markdown
 233 ```
 234 
 235 ---
 236 
 237 ## Common Workflows
 238 
 239 ### Security Audit
 240 
 241 ```python
 242 # 1. Find all PS with dangerous permissions
 243 dangerous_perms = ['ModifyAllData', 'ViewAllData', 'ManageUsers']
 244 
 245 for perm in dangerous_perms:
 246     results = detect_system_permission(sf, perm)
 247     print(f"\n{perm}: {len(results)} PS")
 248     for r in results:
 249         if r.assigned_user_count > 0:
 250             print(f"  ⚠️  {r.permission_set_label}: {r.assigned_user_count} users")
 251 ```
 252 
 253 ### User Provisioning Check
 254 
 255 ```python
 256 # Verify a user has expected permissions
 257 expected_ps = ['Sales_Account_Access', 'Report_Runner', 'API_Access']
 258 
 259 analysis = analyze_user_permissions(sf, 'new.user@company.com')
 260 user_ps_names = set()
 261 
 262 for g in analysis.via_groups:
 263     for ps in g['permission_sets']:
 264         user_ps_names.add(ps['name'])
 265 for ps in analysis.direct_assignments:
 266     user_ps_names.add(ps.name)
 267 
 268 missing = set(expected_ps) - user_ps_names
 269 if missing:
 270     print(f"Missing PS: {missing}")
 271 else:
 272     print("All expected PS assigned ✅")
 273 ```
 274 
 275 ### Documentation Generation
 276 
 277 ```python
 278 # Generate permission documentation
 279 
 280 hierarchy = get_org_permission_hierarchy(sf)
 281 
 282 # Create markdown documentation
 283 doc = "# Org Permission Structure\n\n"
 284 doc += render_hierarchy_mermaid(hierarchy) + "\n\n"
 285 
 286 doc += "## Permission Set Groups\n\n"
 287 for psg in hierarchy.permission_set_groups:
 288     doc += f"### {psg.master_label}\n"
 289     doc += f"- Status: {psg.status}\n"
 290     doc += f"- Users: {psg.assigned_user_count}\n"
 291     doc += f"- Permission Sets:\n"
 292     for ps in psg.permission_sets:
 293         doc += f"  - {ps.label}\n"
 294     doc += "\n"
 295 
 296 with open('/tmp/permissions-doc.md', 'w') as f:
 297     f.write(doc)
 298 ```
