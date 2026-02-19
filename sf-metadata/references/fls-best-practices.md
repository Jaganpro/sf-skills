<!-- Parent: sf-metadata/SKILL.md -->
   1 # Field-Level Security (FLS) Best Practices
   2 
   3 ## Overview
   4 
   5 Field-Level Security (FLS) controls which users can view and edit specific fields on records. Proper FLS configuration is essential for data security and compliance.
   6 
   7 ---
   8 
   9 ## Understanding FLS
  10 
  11 ### Two Levels of Field Access
  12 1. **Readable**: User can see the field value
  13 2. **Editable**: User can modify the field value (implies readable)
  14 
  15 ### FLS vs Object Permissions
  16 ```
  17 User Access = Object Permissions + Field-Level Security + Record Access
  18 
  19 Object Permissions: Can user access the object at all?
  20 FLS: Can user see/edit specific fields?
  21 Record Access: Can user access specific records?
  22 ```
  23 
  24 ### Where FLS is Configured
  25 - Profiles (base access)
  26 - Permission Sets (additive access)
  27 - Permission Set Groups (combined sets)
  28 
  29 ---
  30 
  31 ## Best Practices
  32 
  33 ### 1. Use Permission Sets Over Profiles
  34 
  35 **Why:**
  36 - Profiles are monolithic and hard to maintain
  37 - Permission Sets are additive and composable
  38 - Easier to manage feature-based access
  39 
  40 **Pattern:**
  41 ```
  42 Profile: Base access (read-only on most fields)
  43 Permission Set: Feature-specific edit access
  44 ```
  45 
  46 **Example:**
  47 ```xml
  48 <!-- Permission Set for Invoice Editors -->
  49 <PermissionSet>
  50     <label>Invoice Editor</label>
  51     <fieldPermissions>
  52         <editable>true</editable>
  53         <field>Invoice__c.Amount__c</field>
  54         <readable>true</readable>
  55     </fieldPermissions>
  56     <fieldPermissions>
  57         <editable>true</editable>
  58         <field>Invoice__c.Status__c</field>
  59         <readable>true</readable>
  60     </fieldPermissions>
  61 </PermissionSet>
  62 ```
  63 
  64 ---
  65 
  66 ### 2. Principle of Least Privilege
  67 
  68 **Rule:** Grant minimum access needed for the job function
  69 
  70 **Steps:**
  71 1. Start with no access
  72 2. Add read access where needed
  73 3. Add edit access only where required
  74 4. Review periodically
  75 
  76 **Anti-Pattern:**
  77 ```xml
  78 <!-- DON'T: Grant edit on everything -->
  79 <fieldPermissions>
  80     <editable>true</editable>
  81     <field>Account.AnnualRevenue</field>
  82     <readable>true</readable>
  83 </fieldPermissions>
  84 ```
  85 
  86 **Better:**
  87 ```xml
  88 <!-- DO: Grant read-only unless edit is required -->
  89 <fieldPermissions>
  90     <editable>false</editable>
  91     <field>Account.AnnualRevenue</field>
  92     <readable>true</readable>
  93 </fieldPermissions>
  94 ```
  95 
  96 ---
  97 
  98 ### 3. Protect Sensitive Fields
  99 
 100 #### Identify Sensitive Fields
 101 | Category | Examples |
 102 |----------|----------|
 103 | PII | SSN, Date of Birth, Driver's License |
 104 | Financial | Bank Account, Credit Card, Salary |
 105 | Health | Medical conditions, Insurance |
 106 | Security | Password, Token, API Key |
 107 | Business | Trade secrets, Pricing formulas |
 108 
 109 #### Protection Strategies
 110 
 111 1. **Restrict to Specific Permission Sets**
 112 ```xml
 113 <PermissionSet>
 114     <label>PII_Access</label>
 115     <description>Access to sensitive PII fields</description>
 116     <fieldPermissions>
 117         <editable>false</editable>
 118         <field>Contact.SSN__c</field>
 119         <readable>true</readable>
 120     </fieldPermissions>
 121 </PermissionSet>
 122 ```
 123 
 124 2. **Use Shield Platform Encryption**
 125 - Encrypts data at rest
 126 - Searchable with deterministic encryption
 127 - Requires Shield license
 128 
 129 3. **Use Classic Encryption (Encrypted Text Field)**
 130 - Masks display (shows last 4 characters)
 131 - Limited functionality
 132 - No additional license needed
 133 
 134 ---
 135 
 136 ### 4. FLS in Apex Code
 137 
 138 #### Always Check FLS in Apex
 139 
 140 **With SOQL:**
 141 ```apex
 142 // Good: Respects FLS
 143 List<Account> accounts = [
 144     SELECT Name, Industry
 145     FROM Account
 146     WITH USER_MODE
 147 ];
 148 
 149 // Alternative: Security.stripInaccessible
 150 List<Account> accounts = [SELECT Name, Industry, Revenue FROM Account];
 151 SObjectAccessDecision decision = Security.stripInaccessible(
 152     AccessType.READABLE,
 153     accounts
 154 );
 155 List<Account> safeAccounts = decision.getRecords();
 156 ```
 157 
 158 **With DML:**
 159 ```apex
 160 // Good: Respects FLS
 161 Database.insert(accounts, AccessLevel.USER_MODE);
 162 
 163 // Alternative: Check before DML
 164 if (Schema.sObjectType.Account.fields.Industry.isUpdateable()) {
 165     account.Industry = 'Technology';
 166 }
 167 ```
 168 
 169 ---
 170 
 171 ### 5. Organize Permission Sets by Function
 172 
 173 **Pattern:**
 174 ```
 175 [Object]_[AccessLevel]
 176 [Feature]_[Role]
 177 [Integration]_Access
 178 ```
 179 
 180 **Example Structure:**
 181 ```
 182 Permission Sets/
 183 ├── Account_Read_Only.permissionset-meta.xml
 184 ├── Account_Full_Access.permissionset-meta.xml
 185 ├── Invoice_Approver.permissionset-meta.xml
 186 ├── Invoice_Creator.permissionset-meta.xml
 187 ├── ERP_Integration_Access.permissionset-meta.xml
 188 └── Reports_Power_User.permissionset-meta.xml
 189 ```
 190 
 191 ---
 192 
 193 ### 6. Use Permission Set Groups
 194 
 195 **Why:**
 196 - Combine related permission sets
 197 - Easier role-based assignment
 198 - Single assignment per user role
 199 
 200 **Example:**
 201 ```
 202 Permission Set Group: Sales_Representative
 203 ├── Account_Full_Access
 204 ├── Contact_Full_Access
 205 ├── Opportunity_Full_Access
 206 ├── Quote_Creator
 207 └── Reports_Basic
 208 ```
 209 
 210 ---
 211 
 212 ### 7. Handle Formula Fields Correctly
 213 
 214 **Important:** Formula fields inherit FLS from referenced fields
 215 
 216 ```
 217 Formula: Account.Owner.Manager.Name
 218 
 219 User needs READ access to:
 220 - Account.OwnerId
 221 - User.ManagerId
 222 - User.Name (on Manager)
 223 ```
 224 
 225 **Best Practice:** Test formulas with different user profiles
 226 
 227 ---
 228 
 229 ### 8. Document FLS Decisions
 230 
 231 **For each sensitive field, document:**
 232 - Why it exists
 233 - Who should have access
 234 - Which permission sets grant access
 235 - Review date
 236 
 237 **Example:**
 238 ```xml
 239 <CustomField>
 240     <fullName>SSN__c</fullName>
 241     <description>
 242         Social Security Number - SENSITIVE
 243         Access: HR_PII_Access permission set only
 244         Review: Quarterly by Security team
 245     </description>
 246 </CustomField>
 247 ```
 248 
 249 ---
 250 
 251 ## Common Mistakes
 252 
 253 ### 1. Relying on Page Layout for Security
 254 ```
 255 ❌ "Users can't see it because it's not on the layout"
 256 ✅ FLS controls true visibility; layouts are UX only
 257 ```
 258 
 259 ### 2. Granting Edit Without Business Need
 260 ```
 261 ❌ "Give them edit just in case they need it"
 262 ✅ Start read-only, add edit when requested
 263 ```
 264 
 265 ### 3. Not Checking FLS in Apex
 266 ```
 267 ❌ Assuming controller/trigger runs as system
 268 ✅ Always use WITH USER_MODE or Security.stripInaccessible
 269 ```
 270 
 271 ### 4. Over-Using System Administrator
 272 ```
 273 ❌ "Just use System Admin profile"
 274 ✅ Create specific permission sets for each function
 275 ```
 276 
 277 ### 5. Not Testing FLS Changes
 278 ```
 279 ❌ Deploy FLS changes without testing
 280 ✅ Test with actual user profiles before deploy
 281 ```
 282 
 283 ---
 284 
 285 ## FLS Audit Checklist
 286 
 287 ### For Each Object
 288 
 289 - [ ] All fields reviewed for sensitivity
 290 - [ ] Sensitive fields have restricted access
 291 - [ ] Permission Sets exist for each access pattern
 292 - [ ] No unnecessary edit permissions
 293 - [ ] Formula fields tested with limited users
 294 - [ ] Integration users have minimal required access
 295 
 296 ### For Apex Code
 297 
 298 - [ ] All SOQL uses WITH USER_MODE or stripInaccessible
 299 - [ ] All DML uses USER_MODE or checks isUpdateable()
 300 - [ ] Tests verify FLS enforcement
 301 - [ ] No hardcoded field access bypass
 302 
 303 ### For Deployment
 304 
 305 - [ ] FLS changes reviewed by security team
 306 - [ ] Changes tested with representative users
 307 - [ ] Rollback plan exists
 308 - [ ] Documentation updated
 309 
 310 ---
 311 
 312 ## Quick Reference
 313 
 314 ### SOQL FLS Modes
 315 | Mode | Behavior |
 316 |------|----------|
 317 | `WITH USER_MODE` | Enforces FLS and sharing |
 318 | `WITH SYSTEM_MODE` | Bypasses FLS (use carefully) |
 319 | Default (no mode) | Depends on context |
 320 
 321 ### Schema Methods
 322 | Method | Purpose |
 323 |--------|---------|
 324 | `isAccessible()` | Can user read field? |
 325 | `isUpdateable()` | Can user edit field? |
 326 | `isCreateable()` | Can user set on create? |
 327 
 328 ### Security.stripInaccessible
 329 | AccessType | Strips Fields Not... |
 330 |------------|----------------------|
 331 | `READABLE` | Readable by user |
 332 | `CREATABLE` | Creatable by user |
 333 | `UPDATABLE` | Updatable by user |
 334 | `UPSERTABLE` | Creatable or updatable |
