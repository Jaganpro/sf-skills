<!-- Parent: sf-metadata/SKILL.md -->
   1 # Profiles vs Permission Sets Guide
   2 
   3 ## Overview
   4 
   5 Salesforce provides two primary mechanisms for controlling user access: Profiles and Permission Sets. Understanding when to use each is critical for maintainable security architecture.
   6 
   7 ---
   8 
   9 ## Quick Comparison
  10 
  11 | Aspect | Profile | Permission Set |
  12 |--------|---------|----------------|
  13 | Assignment | One per user (required) | Multiple per user |
  14 | Access model | Defines base access | Adds to profile |
  15 | Modification | All-or-nothing | Granular additions |
  16 | Standard items | Yes (System Admin, etc.) | No standard sets |
  17 | Best for | Base access, login settings | Feature-based access |
  18 
  19 ---
  20 
  21 ## When to Use Profiles
  22 
  23 ### Use Profiles For:
  24 
  25 1. **Login Settings**
  26    - Login hours
  27    - Login IP ranges
  28    - Password policies
  29 
  30 2. **Default Settings**
  31    - Default record types
  32    - Default page layouts
  33    - Default applications
  34 
  35 3. **Base Object Access**
  36    - Minimum required object permissions
  37    - Tab visibility defaults
  38 
  39 4. **License-Based Access**
  40    - Different profiles for different licenses
  41    - Platform vs Full Salesforce users
  42 
  43 ### Profile Best Practices
  44 
  45 ```
  46 ✅ Create minimal profiles (least privilege)
  47 ✅ Use descriptive names (Sales_User, Service_User)
  48 ✅ Document what each profile provides
  49 ✅ Review profiles quarterly
  50 
  51 ❌ Don't create user-specific profiles
  52 ❌ Don't manage feature access in profiles
  53 ❌ Don't clone System Administrator
  54 ```
  55 
  56 ---
  57 
  58 ## When to Use Permission Sets
  59 
  60 ### Use Permission Sets For:
  61 
  62 1. **Feature Access**
  63    - Invoice approval
  64    - Report building
  65    - API access
  66 
  67 2. **Object/Field Access**
  68    - Read access to sensitive objects
  69    - Edit access to specific fields
  70 
  71 3. **Temporary Access**
  72    - Project-based access
  73    - Training access
  74 
  75 4. **Integration Users**
  76    - API permissions
  77    - System access
  78 
  79 ### Permission Set Best Practices
  80 
  81 ```
  82 ✅ Create feature-focused sets
  83 ✅ Use consistent naming conventions
  84 ✅ Combine into Permission Set Groups
  85 ✅ Document purpose and audience
  86 
  87 ❌ Don't duplicate profile permissions
  88 ❌ Don't create user-specific sets
  89 ❌ Don't include login settings
  90 ```
  91 
  92 ---
  93 
  94 ## Architecture Patterns
  95 
  96 ### Pattern 1: Minimal Profile + Permission Sets (Recommended)
  97 
  98 ```
  99 Profile: Base_User
 100 ├── Read access to common objects
 101 ├── Default applications
 102 └── Login settings
 103 
 104 Permission Sets (assigned as needed):
 105 ├── Invoice_Creator
 106 ├── Invoice_Approver
 107 ├── Report_Builder
 108 ├── API_Access
 109 └── Admin_Tools
 110 ```
 111 
 112 **Benefits:**
 113 - Flexible
 114 - Easy to audit
 115 - Scalable
 116 
 117 ---
 118 
 119 ### Pattern 2: Role-Based Permission Set Groups
 120 
 121 ```
 122 Permission Set Groups:
 123 ├── Sales_Representative
 124 │   ├── Account_Full_Access
 125 │   ├── Contact_Full_Access
 126 │   ├── Opportunity_Full_Access
 127 │   └── Reports_Basic
 128 │
 129 ├── Sales_Manager
 130 │   ├── Sales_Representative (inherit)
 131 │   ├── Team_Reports
 132 │   └── Approval_Authority
 133 │
 134 └── Sales_Operations
 135     ├── Sales_Representative (inherit)
 136     ├── Data_Import
 137     └── Admin_Reports
 138 ```
 139 
 140 **Benefits:**
 141 - Role-aligned
 142 - Inheritance via groups
 143 - Single assignment point
 144 
 145 ---
 146 
 147 ### Pattern 3: Functional Decomposition
 148 
 149 ```
 150 Base Layer (Profile):
 151 └── Standard_User_Profile
 152 
 153 Feature Layer (Permission Sets):
 154 ├── CRM_Features
 155 ├── Marketing_Features
 156 ├── Service_Features
 157 └── Commerce_Features
 158 
 159 Object Layer (Permission Sets):
 160 ├── Custom_Invoice_Access
 161 ├── Custom_Product_Access
 162 └── Integration_Object_Access
 163 
 164 Admin Layer (Permission Sets):
 165 ├── User_Management
 166 ├── Data_Management
 167 └── System_Configuration
 168 ```
 169 
 170 ---
 171 
 172 ## Permission Set Groups
 173 
 174 ### What Are They?
 175 Permission Set Groups bundle multiple Permission Sets into a single assignable unit.
 176 
 177 ### Structure
 178 ```xml
 179 <PermissionSetGroup>
 180     <label>Sales Team Access</label>
 181     <permissionSets>
 182         <permissionSet>Account_Full_Access</permissionSet>
 183         <permissionSet>Contact_Full_Access</permissionSet>
 184         <permissionSet>Opportunity_Full_Access</permissionSet>
 185     </permissionSets>
 186 </PermissionSetGroup>
 187 ```
 188 
 189 ### Benefits
 190 - Single assignment = multiple permissions
 191 - Easier onboarding
 192 - Consistent access across role
 193 - Simpler audit trail
 194 
 195 ### Muting Permission Sets
 196 Temporarily remove specific permissions from a group:
 197 ```xml
 198 <MutingPermissionSet>
 199     <label>Remove_Delete_Access</label>
 200     <objectPermissions>
 201         <allowDelete>false</allowDelete>
 202         <object>Account</object>
 203     </objectPermissions>
 204 </MutingPermissionSet>
 205 ```
 206 
 207 ---
 208 
 209 ## Migration Strategy
 210 
 211 ### Moving from Profiles to Permission Sets
 212 
 213 1. **Audit Current State**
 214    ```
 215    - List all profiles and their permissions
 216    - Identify unique permission combinations
 217    - Map profiles to user roles
 218    ```
 219 
 220 2. **Design Permission Sets**
 221    ```
 222    - Group permissions by feature/function
 223    - Create atomic permission sets
 224    - Plan permission set groups
 225    ```
 226 
 227 3. **Create Minimal Profiles**
 228    ```
 229    - Clone existing profiles
 230    - Remove feature-specific permissions
 231    - Keep only base access + settings
 232    ```
 233 
 234 4. **Create Permission Sets**
 235    ```
 236    - Build feature-based sets
 237    - Test with pilot users
 238    - Document each set's purpose
 239    ```
 240 
 241 5. **Migrate Users**
 242    ```
 243    - Assign new minimal profile
 244    - Assign relevant permission sets
 245    - Verify access is equivalent
 246    ```
 247 
 248 6. **Deprecate Old Profiles**
 249    ```
 250    - Remove users from old profiles
 251    - Archive (don't delete) old profiles
 252    - Monitor for issues
 253    ```
 254 
 255 ---
 256 
 257 ## Common Scenarios
 258 
 259 ### Scenario 1: New Feature Rollout
 260 
 261 **Situation:** Rolling out new invoice approval feature
 262 
 263 **Solution:**
 264 ```
 265 Create: Invoice_Approval_Permission_Set
 266 ├── Object: Invoice__c (Read, Edit)
 267 ├── Field: Approval_Status__c (Edit)
 268 ├── Field: Approver_Comments__c (Edit)
 269 └── Apex: Invoice_Approval_Controller (Execute)
 270 
 271 Assign to: Users who approve invoices
 272 ```
 273 
 274 ---
 275 
 276 ### Scenario 2: Temporary Contractor Access
 277 
 278 **Situation:** Contractors need limited access for 3 months
 279 
 280 **Solution:**
 281 ```
 282 Profile: Contractor_Base (minimal)
 283 Permission Set: Project_XYZ_Access (time-limited)
 284 
 285 Process:
 286 1. Assign Contractor_Base profile
 287 2. Assign Project_XYZ_Access permission set
 288 3. Set calendar reminder for removal
 289 4. Remove permission set at project end
 290 ```
 291 
 292 ---
 293 
 294 ### Scenario 3: Integration User
 295 
 296 **Situation:** External system needs API access
 297 
 298 **Solution:**
 299 ```
 300 Profile: Integration_User (minimal, API-only)
 301 Permission Sets:
 302 ├── API_Enabled (system permission)
 303 ├── ERP_Objects_Access (specific objects)
 304 └── ERP_Fields_Access (specific fields)
 305 
 306 No: UI access, reports, dashboards
 307 Yes: API, specific objects/fields only
 308 ```
 309 
 310 ---
 311 
 312 ## Anti-Patterns to Avoid
 313 
 314 ### 1. Profile Proliferation
 315 ```
 316 ❌ John_Smith_Profile
 317 ❌ Marketing_Temp_Profile
 318 ❌ Sales_With_Reports_Profile
 319 
 320 ✅ Standard profiles + targeted permission sets
 321 ```
 322 
 323 ### 2. Cloning System Administrator
 324 ```
 325 ❌ Clone System Admin for power users
 326 ❌ Modify cloned admin for "limited admin"
 327 
 328 ✅ Build from minimal profile + specific sets
 329 ```
 330 
 331 ### 3. Permission Set Sprawl
 332 ```
 333 ❌ One permission set per user request
 334 ❌ Overlapping permission sets
 335 ❌ Undocumented permission sets
 336 
 337 ✅ Feature-aligned, documented sets
 338 ✅ Regular audit and consolidation
 339 ```
 340 
 341 ### 4. Mixing Concerns
 342 ```
 343 ❌ Profile with feature permissions
 344 ❌ Permission set with login settings
 345 
 346 ✅ Profiles: settings + base access
 347 ✅ Permission sets: feature access only
 348 ```
 349 
 350 ---
 351 
 352 ## Audit Checklist
 353 
 354 ### Profiles
 355 - [ ] Each profile has clear purpose
 356 - [ ] No user-specific profiles
 357 - [ ] Minimal permissions (least privilege)
 358 - [ ] Login settings appropriate
 359 - [ ] Documented and reviewed
 360 
 361 ### Permission Sets
 362 - [ ] Named by feature/function
 363 - [ ] No overlapping permissions
 364 - [ ] Documented purpose
 365 - [ ] Grouped logically
 366 - [ ] Assignment tracked
 367 
 368 ### Permission Set Groups
 369 - [ ] Role-aligned groupings
 370 - [ ] No redundant inclusions
 371 - [ ] Muting sets used appropriately
 372 - [ ] Easy to understand structure
 373 
 374 ---
 375 
 376 ## Quick Reference
 377 
 378 ### Profile Contains
 379 - User license
 380 - Login hours/IP ranges
 381 - Password policies
 382 - Default record types
 383 - Default page layouts
 384 - Default applications
 385 - Base object permissions
 386 - Tab visibility
 387 
 388 ### Permission Set Contains
 389 - Object permissions (additive)
 390 - Field permissions (additive)
 391 - Apex class access
 392 - Visualforce page access
 393 - Custom permissions
 394 - Connected app access
 395 - External data source access
 396 
 397 ### Permission Set Group Contains
 398 - Multiple permission sets
 399 - Muting permission sets (optional)
 400 - Calculated permissions (union)
