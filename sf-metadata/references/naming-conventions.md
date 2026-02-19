<!-- Parent: sf-metadata/SKILL.md -->
   1 # Salesforce Metadata Naming Conventions
   2 
   3 ## Overview
   4 
   5 Consistent naming conventions improve maintainability, discoverability, and team collaboration. Follow these standards for all Salesforce metadata.
   6 
   7 ---
   8 
   9 ## Custom Objects
  10 
  11 ### Format
  12 ```
  13 [BusinessEntity]__c
  14 ```
  15 
  16 ### Rules
  17 - Use PascalCase
  18 - Singular form (not plural)
  19 - Max 40 characters (API name)
  20 - No abbreviations
  21 - Descriptive and business-meaningful
  22 
  23 ### Examples
  24 ✅ Good:
  25 - `Invoice__c`
  26 - `Product_Catalog__c`
  27 - `Service_Request__c`
  28 - `Customer_Feedback__c`
  29 
  30 ❌ Avoid:
  31 - `Invoices__c` (plural)
  32 - `Inv__c` (abbreviated)
  33 - `SvcReq__c` (abbreviated)
  34 - `object1__c` (meaningless)
  35 
  36 ---
  37 
  38 ## Custom Fields
  39 
  40 ### Format
  41 ```
  42 [Descriptive_Name]__c
  43 ```
  44 
  45 ### Rules
  46 - Use PascalCase with underscores
  47 - Indicate purpose, not data type
  48 - Max 40 characters (API name)
  49 - Use standard suffixes for relationships
  50 
  51 ### Standard Suffixes
  52 | Suffix | Use Case |
  53 |--------|----------|
  54 | `_Date` | Date fields (e.g., `Due_Date__c`) |
  55 | `_Amount` | Currency/Number (e.g., `Total_Amount__c`) |
  56 | `_Count` | Counts (e.g., `Line_Item_Count__c`) |
  57 | `_Percent` | Percentages (e.g., `Discount_Percent__c`) |
  58 | `_Flag` | Boolean indicators (e.g., `Is_Active_Flag__c`) |
  59 | `_Code` | Codes/identifiers (e.g., `Region_Code__c`) |
  60 
  61 ### Relationship Fields
  62 ```
  63 [RelatedObject]__c     // Lookup/Master-Detail field
  64 [RelatedObject]__r     // Relationship name (auto-generated)
  65 ```
  66 
  67 ### Examples
  68 ✅ Good:
  69 - `Account_Manager__c` (Lookup to User)
  70 - `Total_Contract_Value__c` (Currency)
  71 - `Expected_Close_Date__c` (Date)
  72 - `Is_Primary_Contact__c` (Checkbox)
  73 
  74 ❌ Avoid:
  75 - `Amt__c` (abbreviated)
  76 - `Field1__c` (meaningless)
  77 - `TCV__c` (acronym without context)
  78 - `contactLookup__c` (inconsistent casing)
  79 
  80 ---
  81 
  82 ## Profiles
  83 
  84 ### Format
  85 ```
  86 [Role/Function] [Level]
  87 ```
  88 
  89 ### Examples
  90 - `Sales Representative`
  91 - `Sales Manager`
  92 - `Marketing User`
  93 - `System Administrator`
  94 - `Integration User`
  95 
  96 ### Notes
  97 - Standard profiles cannot be renamed
  98 - Create custom profiles for specific needs
  99 - Use Permission Sets for granular access
 100 
 101 ---
 102 
 103 ## Permission Sets
 104 
 105 ### Format
 106 ```
 107 [Feature/Capability]_[AccessLevel]
 108 ```
 109 
 110 ### Patterns
 111 | Pattern | Use Case |
 112 |---------|----------|
 113 | `[Object]_Full_Access` | Complete CRUD on object |
 114 | `[Object]_Read_Only` | Read-only access |
 115 | `[Feature]_Manager` | Feature management |
 116 | `[Integration]_API` | Integration access |
 117 
 118 ### Examples
 119 ✅ Good:
 120 - `Invoice_Full_Access`
 121 - `Customer_Portal_User`
 122 - `ERP_Integration_API`
 123 - `Report_Builder_Access`
 124 - `Deal_Approval_Manager`
 125 
 126 ❌ Avoid:
 127 - `PS1` (meaningless)
 128 - `John_Smith_Access` (user-specific)
 129 - `Temp_Access` (ambiguous)
 130 
 131 ---
 132 
 133 ## Validation Rules
 134 
 135 ### Format
 136 ```
 137 [Object]_[Action]_[Condition]
 138 ```
 139 
 140 ### Rules
 141 - Start with object name for organization
 142 - Use verb describing what it prevents/requires
 143 - End with condition being validated
 144 
 145 ### Examples
 146 ✅ Good:
 147 - `Opportunity_Require_Close_Date_When_Closed`
 148 - `Account_Prevent_Type_Change_After_Active`
 149 - `Contact_Require_Email_Or_Phone`
 150 - `Invoice_Amount_Must_Be_Positive`
 151 
 152 ❌ Avoid:
 153 - `VR001` (meaningless)
 154 - `Check1` (undescriptive)
 155 - `Validation` (too generic)
 156 
 157 ---
 158 
 159 ## Record Types
 160 
 161 ### Format
 162 ```
 163 [Category/Type]_[SubCategory]
 164 ```
 165 
 166 ### Examples
 167 ✅ Good:
 168 - `Business_Account`
 169 - `Person_Account`
 170 - `New_Business_Opportunity`
 171 - `Renewal_Opportunity`
 172 - `Support_Case`
 173 - `Billing_Inquiry`
 174 
 175 ❌ Avoid:
 176 - `RT1` (meaningless)
 177 - `Type1` (undescriptive)
 178 
 179 ---
 180 
 181 ## Page Layouts
 182 
 183 ### Format
 184 ```
 185 [Object]-[RecordType] Layout
 186 ```
 187 
 188 ### Examples
 189 - `Account-Business Account Layout`
 190 - `Account-Person Account Layout`
 191 - `Opportunity-New Business Layout`
 192 - `Case-Support Case Layout`
 193 
 194 ---
 195 
 196 ## Quick Reference Table
 197 
 198 | Metadata Type | Pattern | Example |
 199 |---------------|---------|---------|
 200 | Custom Object | `BusinessEntity__c` | `Invoice__c` |
 201 | Custom Field | `Descriptive_Name__c` | `Total_Amount__c` |
 202 | Lookup Field | `RelatedObject__c` | `Primary_Contact__c` |
 203 | Permission Set | `Feature_AccessLevel` | `Invoice_Manager` |
 204 | Validation Rule | `Object_Action_Condition` | `Opp_Require_Amount` |
 205 | Record Type | `Category_SubCategory` | `Business_Account` |
 206 | Page Layout | `Object-RecordType Layout` | `Account-Business Layout` |
 207 
 208 ---
 209 
 210 ## Anti-Patterns to Avoid
 211 
 212 ### Abbreviations
 213 | Instead of | Use |
 214 |------------|-----|
 215 | `Acct__c` | `Account__c` |
 216 | `Opp__c` | `Opportunity__c` |
 217 | `Cont__c` | `Contact__c` |
 218 | `Amt__c` | `Amount__c` |
 219 | `Qty__c` | `Quantity__c` |
 220 
 221 ### Meaningless Names
 222 | Instead of | Use |
 223 |------------|-----|
 224 | `Field1__c` | `Customer_Status__c` |
 225 | `Custom__c` | `Priority_Level__c` |
 226 | `Temp__c` | `Processing_Date__c` |
 227 
 228 ### Inconsistent Casing
 229 | Instead of | Use |
 230 |------------|-----|
 231 | `totalamount__c` | `Total_Amount__c` |
 232 | `TOTAL_AMOUNT__c` | `Total_Amount__c` |
 233 | `TotalAmount__c` | `Total_Amount__c` |
 234 
 235 ---
 236 
 237 ## Checklist
 238 
 239 Before creating metadata, verify:
 240 - [ ] Name is PascalCase with underscores
 241 - [ ] Name describes business purpose
 242 - [ ] No abbreviations used
 243 - [ ] Follows standard suffix patterns
 244 - [ ] Unique within the object/type
 245 - [ ] Max length constraints met
 246 - [ ] Consistent with existing patterns
