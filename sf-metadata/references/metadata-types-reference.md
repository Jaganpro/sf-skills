<!-- Parent: sf-metadata/SKILL.md -->
   1 # Salesforce Metadata Types Reference
   2 
   3 ## Overview
   4 
   5 This guide covers the most common Salesforce metadata types, their file locations, and usage patterns.
   6 
   7 ---
   8 
   9 ## Metadata Directory Structure
  10 
  11 ```
  12 force-app/main/default/
  13 ├── objects/
  14 │   ├── Account/
  15 │   │   ├── Account.object-meta.xml          # Object settings (standard)
  16 │   │   ├── fields/
  17 │   │   │   ├── Custom_Field__c.field-meta.xml
  18 │   │   │   └── ...
  19 │   │   ├── validationRules/
  20 │   │   │   └── Rule_Name.validationRule-meta.xml
  21 │   │   ├── recordTypes/
  22 │   │   │   └── Record_Type.recordType-meta.xml
  23 │   │   └── listViews/
  24 │   │       └── All_Accounts.listView-meta.xml
  25 │   └── Custom_Object__c/
  26 │       ├── Custom_Object__c.object-meta.xml  # Full object definition
  27 │       ├── fields/
  28 │       ├── validationRules/
  29 │       └── recordTypes/
  30 ├── profiles/
  31 │   └── Profile_Name.profile-meta.xml
  32 ├── permissionsets/
  33 │   └── Permission_Set.permissionset-meta.xml
  34 ├── layouts/
  35 │   └── Object-Layout_Name.layout-meta.xml
  36 ├── classes/
  37 │   ├── ClassName.cls
  38 │   └── ClassName.cls-meta.xml
  39 ├── triggers/
  40 │   ├── TriggerName.trigger
  41 │   └── TriggerName.trigger-meta.xml
  42 ├── flows/
  43 │   └── Flow_Name.flow-meta.xml
  44 ├── lwc/
  45 │   └── componentName/
  46 │       ├── componentName.html
  47 │       ├── componentName.js
  48 │       └── componentName.js-meta.xml
  49 └── aura/
  50     └── ComponentName/
  51         ├── ComponentName.cmp
  52         └── ComponentName.cmp-meta.xml
  53 ```
  54 
  55 ---
  56 
  57 ## Object Metadata
  58 
  59 ### Custom Object
  60 **Location:** `objects/[ObjectName__c]/[ObjectName__c].object-meta.xml`
  61 
  62 **Contains:**
  63 - Label and plural label
  64 - Name field configuration
  65 - Sharing model
  66 - Feature toggles (history, activities, reports)
  67 - Search layouts
  68 
  69 ```xml
  70 <CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  71     <label>Invoice</label>
  72     <pluralLabel>Invoices</pluralLabel>
  73     <nameField>
  74         <label>Invoice Number</label>
  75         <type>AutoNumber</type>
  76         <displayFormat>INV-{0000}</displayFormat>
  77     </nameField>
  78     <deploymentStatus>Deployed</deploymentStatus>
  79     <sharingModel>Private</sharingModel>
  80 </CustomObject>
  81 ```
  82 
  83 ### Custom Field
  84 **Location:** `objects/[ObjectName]/fields/[FieldName__c].field-meta.xml`
  85 
  86 **Common Types:**
  87 | Type | Element |
  88 |------|---------|
  89 | Text | `<type>Text</type><length>255</length>` |
  90 | Number | `<type>Number</type><precision>18</precision><scale>2</scale>` |
  91 | Currency | `<type>Currency</type>` |
  92 | Date | `<type>Date</type>` |
  93 | Checkbox | `<type>Checkbox</type><defaultValue>false</defaultValue>` |
  94 | Picklist | `<type>Picklist</type><valueSet>...</valueSet>` |
  95 | Lookup | `<type>Lookup</type><referenceTo>Account</referenceTo>` |
  96 | Master-Detail | `<type>MasterDetail</type>` |
  97 | Formula | `<type>Text</type><formula>...</formula>` |
  98 | Roll-Up | `<type>Summary</type>` |
  99 
 100 ---
 101 
 102 ## Security Metadata
 103 
 104 ### Profile
 105 **Location:** `profiles/[ProfileName].profile-meta.xml`
 106 
 107 **Contains:**
 108 - Object permissions
 109 - Field permissions
 110 - Tab visibility
 111 - Record type assignments
 112 - Layout assignments
 113 - User permissions
 114 
 115 ### Permission Set
 116 **Location:** `permissionsets/[PermissionSetName].permissionset-meta.xml`
 117 
 118 **Contains:**
 119 - Object permissions
 120 - Field permissions
 121 - Tab settings
 122 - Apex class access
 123 - Visualforce page access
 124 - Custom permissions
 125 
 126 ### Permission Set Group
 127 **Location:** `permissionsetgroups/[GroupName].permissionsetgroup-meta.xml`
 128 
 129 ```xml
 130 <PermissionSetGroup xmlns="http://soap.sforce.com/2006/04/metadata">
 131     <label>Sales Team</label>
 132     <permissionSets>
 133         <permissionSet>Account_Access</permissionSet>
 134         <permissionSet>Opportunity_Access</permissionSet>
 135     </permissionSets>
 136 </PermissionSetGroup>
 137 ```
 138 
 139 ---
 140 
 141 ## Validation & Business Logic
 142 
 143 ### Validation Rule
 144 **Location:** `objects/[ObjectName]/validationRules/[RuleName].validationRule-meta.xml`
 145 
 146 ```xml
 147 <ValidationRule xmlns="http://soap.sforce.com/2006/04/metadata">
 148     <fullName>Require_Close_Date</fullName>
 149     <active>true</active>
 150     <errorConditionFormula>
 151         AND(
 152             ISPICKVAL(Status__c, 'Closed'),
 153             ISBLANK(Close_Date__c)
 154         )
 155     </errorConditionFormula>
 156     <errorDisplayField>Close_Date__c</errorDisplayField>
 157     <errorMessage>Close Date is required when Status is Closed</errorMessage>
 158 </ValidationRule>
 159 ```
 160 
 161 ### Record Type
 162 **Location:** `objects/[ObjectName]/recordTypes/[RecordTypeName].recordType-meta.xml`
 163 
 164 ```xml
 165 <RecordType xmlns="http://soap.sforce.com/2006/04/metadata">
 166     <fullName>Business_Account</fullName>
 167     <active>true</active>
 168     <label>Business Account</label>
 169     <picklistValues>
 170         <picklist>Type</picklist>
 171         <values>
 172             <fullName>Customer</fullName>
 173             <default>true</default>
 174         </values>
 175     </picklistValues>
 176 </RecordType>
 177 ```
 178 
 179 ---
 180 
 181 ## UI Metadata
 182 
 183 ### Page Layout
 184 **Location:** `layouts/[ObjectName]-[LayoutName].layout-meta.xml`
 185 
 186 **Contains:**
 187 - Section definitions
 188 - Field placements
 189 - Related lists
 190 - Quick actions
 191 - Display options
 192 
 193 ### Lightning Page (FlexiPage)
 194 **Location:** `flexipages/[PageName].flexipage-meta.xml`
 195 
 196 ### List View
 197 **Location:** `objects/[ObjectName]/listViews/[ViewName].listView-meta.xml`
 198 
 199 ```xml
 200 <ListView xmlns="http://soap.sforce.com/2006/04/metadata">
 201     <fullName>All_Active_Accounts</fullName>
 202     <columns>NAME</columns>
 203     <columns>ACCOUNT_TYPE</columns>
 204     <columns>PHONE1</columns>
 205     <filterScope>Everything</filterScope>
 206     <filters>
 207         <field>ACCOUNT.ACTIVE__C</field>
 208         <operation>equals</operation>
 209         <value>1</value>
 210     </filters>
 211     <label>All Active Accounts</label>
 212 </ListView>
 213 ```
 214 
 215 ---
 216 
 217 ## Automation Metadata
 218 
 219 ### Flow
 220 **Location:** `flows/[FlowName].flow-meta.xml`
 221 
 222 ### Apex Class
 223 **Location:** `classes/[ClassName].cls` + `classes/[ClassName].cls-meta.xml`
 224 
 225 ```xml
 226 <!-- Meta file -->
 227 <ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
 228     <apiVersion>65.0</apiVersion>
 229     <status>Active</status>
 230 </ApexClass>
 231 ```
 232 
 233 ### Apex Trigger
 234 **Location:** `triggers/[TriggerName].trigger` + `triggers/[TriggerName].trigger-meta.xml`
 235 
 236 ---
 237 
 238 ## Component Metadata
 239 
 240 ### Lightning Web Component (LWC)
 241 **Location:** `lwc/[componentName]/`
 242 
 243 ```
 244 lwc/myComponent/
 245 ├── myComponent.html
 246 ├── myComponent.js
 247 ├── myComponent.css (optional)
 248 └── myComponent.js-meta.xml
 249 ```
 250 
 251 ### Aura Component
 252 **Location:** `aura/[ComponentName]/`
 253 
 254 ```
 255 aura/MyComponent/
 256 ├── MyComponent.cmp
 257 ├── MyComponentController.js
 258 ├── MyComponentHelper.js
 259 ├── MyComponent.css
 260 └── MyComponent.cmp-meta.xml
 261 ```
 262 
 263 ---
 264 
 265 ## Global Value Sets
 266 
 267 ### Global Value Set
 268 **Location:** `globalValueSets/[SetName].globalValueSet-meta.xml`
 269 
 270 ```xml
 271 <GlobalValueSet xmlns="http://soap.sforce.com/2006/04/metadata">
 272     <masterLabel>Industry Values</masterLabel>
 273     <sorted>false</sorted>
 274     <customValue>
 275         <fullName>Technology</fullName>
 276         <default>false</default>
 277         <label>Technology</label>
 278     </customValue>
 279     <customValue>
 280         <fullName>Finance</fullName>
 281         <default>false</default>
 282         <label>Finance</label>
 283     </customValue>
 284 </GlobalValueSet>
 285 ```
 286 
 287 ---
 288 
 289 ## Custom Metadata Types
 290 
 291 ### Custom Metadata Type Definition
 292 **Location:** `customMetadata/[TypeName].[RecordName].md-meta.xml`
 293 
 294 ```xml
 295 <CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata">
 296     <label>US Config</label>
 297     <values>
 298         <field>Country_Code__c</field>
 299         <value>US</value>
 300     </values>
 301     <values>
 302         <field>Tax_Rate__c</field>
 303         <value>0.08</value>
 304     </values>
 305 </CustomMetadata>
 306 ```
 307 
 308 ---
 309 
 310 ## Quick Reference: File Extensions
 311 
 312 | Metadata Type | Extension |
 313 |---------------|-----------|
 314 | Custom Object | `.object-meta.xml` |
 315 | Custom Field | `.field-meta.xml` |
 316 | Profile | `.profile-meta.xml` |
 317 | Permission Set | `.permissionset-meta.xml` |
 318 | Validation Rule | `.validationRule-meta.xml` |
 319 | Record Type | `.recordType-meta.xml` |
 320 | Page Layout | `.layout-meta.xml` |
 321 | Flow | `.flow-meta.xml` |
 322 | Apex Class | `.cls` + `.cls-meta.xml` |
 323 | Apex Trigger | `.trigger` + `.trigger-meta.xml` |
 324 | LWC | `.js-meta.xml` |
 325 | Aura | `.cmp-meta.xml` |
 326 
 327 ---
 328 
 329 ## sf CLI Metadata Commands
 330 
 331 ```bash
 332 # List metadata types
 333 sf org list metadata-types --target-org [alias]
 334 
 335 # List specific metadata
 336 sf org list metadata --metadata-type CustomObject --target-org [alias]
 337 
 338 # Describe object
 339 sf sobject describe --sobject Account --target-org [alias]
 340 
 341 # Retrieve metadata
 342 sf project retrieve start --metadata CustomObject:Account
 343 
 344 # Deploy metadata
 345 sf project deploy start --source-dir force-app
 346 
 347 # Generate package.xml
 348 sf project generate manifest --source-dir force-app
 349 ```
