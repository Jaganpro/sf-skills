<!-- Parent: sf-metadata/SKILL.md -->
   1 # Salesforce Field Types Guide
   2 
   3 ## Overview
   4 
   5 Choosing the right field type is critical for data integrity, user experience, and application performance. This guide helps you select the appropriate field type for your requirements.
   6 
   7 ---
   8 
   9 ## Field Type Decision Tree
  10 
  11 ```
  12 What kind of data?
  13 ├── Text/String
  14 │   ├── Short (≤255 chars) → Text
  15 │   ├── Long (>255 chars)
  16 │   │   ├── Plain text → Long Text Area
  17 │   │   └── Formatted → Rich Text Area
  18 │   ├── Predefined values
  19 │   │   ├── Single select → Picklist
  20 │   │   └── Multiple select → Multi-Select Picklist
  21 │   ├── Email format → Email
  22 │   ├── Phone format → Phone
  23 │   └── URL format → URL
  24 ├── Numeric
  25 │   ├── Whole numbers → Number (scale=0)
  26 │   ├── Decimals → Number (scale>0)
  27 │   ├── Money → Currency
  28 │   └── Percentage → Percent
  29 ├── Date/Time
  30 │   ├── Date only → Date
  31 │   └── Date + Time → DateTime
  32 ├── True/False → Checkbox
  33 ├── Related Record
  34 │   ├── Optional parent → Lookup
  35 │   └── Required parent → Master-Detail
  36 └── Calculated
  37     ├── From same record → Formula
  38     └── From child records → Roll-Up Summary
  39 ```
  40 
  41 ---
  42 
  43 ## Text Fields
  44 
  45 ### Text (Standard)
  46 **Use When:** Short text values up to 255 characters
  47 **Max Length:** 255 characters
  48 **Features:**
  49 - Can be unique
  50 - Can be external ID
  51 - Searchable
  52 - Can be used in filters
  53 
  54 **Examples:** Account codes, serial numbers, short names
  55 
  56 ```xml
  57 <type>Text</type>
  58 <length>80</length>
  59 ```
  60 
  61 ---
  62 
  63 ### Long Text Area
  64 **Use When:** Multi-line text over 255 characters
  65 **Max Length:** 131,072 characters
  66 **Limitations:**
  67 - NOT searchable
  68 - NOT filterable
  69 - Cannot be unique
  70 - Cannot be used in roll-ups
  71 
  72 **Examples:** Descriptions, notes, comments
  73 
  74 ```xml
  75 <type>LongTextArea</type>
  76 <length>32000</length>
  77 <visibleLines>5</visibleLines>
  78 ```
  79 
  80 ---
  81 
  82 ### Rich Text Area
  83 **Use When:** Formatted text with HTML
  84 **Max Length:** 131,072 characters
  85 **Features:**
  86 - Bold, italic, underline
  87 - Lists, links, images
  88 - Same limitations as Long Text Area
  89 
  90 **Examples:** Marketing descriptions, detailed instructions
  91 
  92 ```xml
  93 <type>Html</type>
  94 <length>32000</length>
  95 <visibleLines>10</visibleLines>
  96 ```
  97 
  98 ---
  99 
 100 ## Picklist Fields
 101 
 102 ### Picklist (Single-Select)
 103 **Use When:** Predefined single choice
 104 **Max Values:** 1,000 (recommended < 200)
 105 **Features:**
 106 - Filterable
 107 - Reportable
 108 - Can have default value
 109 - Restricted option available
 110 
 111 **Best Practices:**
 112 - Use Global Value Sets for reusable values
 113 - Enable restricted picklist for data quality
 114 - Consider dependent picklists for hierarchies
 115 
 116 ```xml
 117 <type>Picklist</type>
 118 <valueSet>
 119     <restricted>true</restricted>
 120     <valueSetDefinition>
 121         <sorted>false</sorted>
 122         <value>
 123             <fullName>Option1</fullName>
 124             <label>Option 1</label>
 125             <default>true</default>
 126         </value>
 127     </valueSetDefinition>
 128 </valueSet>
 129 ```
 130 
 131 ---
 132 
 133 ### Multi-Select Picklist
 134 **Use When:** Multiple predefined choices
 135 **Max Values:** 500
 136 **Limitations:**
 137 - Cannot be unique
 138 - Cannot be used in roll-ups
 139 - Stored as semicolon-separated string
 140 
 141 **Formula Access:** Use `INCLUDES()` function
 142 
 143 ```xml
 144 <type>MultiselectPicklist</type>
 145 <visibleLines>4</visibleLines>
 146 ```
 147 
 148 ---
 149 
 150 ## Numeric Fields
 151 
 152 ### Number
 153 **Use When:** Numeric values (integers or decimals)
 154 **Max Precision:** 18 digits total
 155 **Max Scale:** 17 decimal places
 156 
 157 **Configuration:**
 158 - `precision`: Total digits (1-18)
 159 - `scale`: Decimal places (0-17)
 160 
 161 **Examples:**
 162 | Use Case | Precision | Scale |
 163 |----------|-----------|-------|
 164 | Integer | 18 | 0 |
 165 | Two decimals | 18 | 2 |
 166 | Percentage | 5 | 2 |
 167 
 168 ```xml
 169 <type>Number</type>
 170 <precision>18</precision>
 171 <scale>2</scale>
 172 ```
 173 
 174 ---
 175 
 176 ### Currency
 177 **Use When:** Monetary values
 178 **Features:**
 179 - Displays with org currency symbol
 180 - Multi-currency support
 181 - Respects locale formatting
 182 
 183 **Best Practice:** Use precision=18, scale=2 for standard currency
 184 
 185 ```xml
 186 <type>Currency</type>
 187 <precision>18</precision>
 188 <scale>2</scale>
 189 ```
 190 
 191 ---
 192 
 193 ### Percent
 194 **Use When:** Percentage values
 195 **Storage:** Stored as decimal (50 = 50%)
 196 **Display:** Shows with % symbol
 197 
 198 ```xml
 199 <type>Percent</type>
 200 <precision>5</precision>
 201 <scale>2</scale>
 202 ```
 203 
 204 ---
 205 
 206 ## Date/Time Fields
 207 
 208 ### Date
 209 **Use When:** Calendar dates without time
 210 **Format:** YYYY-MM-DD (internal)
 211 **Features:**
 212 - Date picker in UI
 213 - Timezone neutral
 214 - Can use TODAY() in formulas
 215 
 216 ```xml
 217 <type>Date</type>
 218 ```
 219 
 220 ---
 221 
 222 ### DateTime
 223 **Use When:** Timestamps with time component
 224 **Format:** ISO 8601 with timezone
 225 **Features:**
 226 - Date and time picker
 227 - Timezone aware
 228 - Can use NOW() in formulas
 229 
 230 ```xml
 231 <type>DateTime</type>
 232 ```
 233 
 234 ---
 235 
 236 ## Boolean Fields
 237 
 238 ### Checkbox
 239 **Use When:** True/False values
 240 **Features:**
 241 - Always has a value (never null)
 242 - Default value required
 243 - Filterable
 244 
 245 **Best Practice:** Use clear naming (Is_Active, Has_Permission)
 246 
 247 ```xml
 248 <type>Checkbox</type>
 249 <defaultValue>false</defaultValue>
 250 ```
 251 
 252 ---
 253 
 254 ## Relationship Fields
 255 
 256 ### Lookup
 257 **Use When:** Optional relationship to another record
 258 **Features:**
 259 - Can be empty (null)
 260 - No cascade delete (configurable)
 261 - No roll-up summaries
 262 - Can be reparented
 263 
 264 **Delete Constraints:**
 265 | Option | Behavior |
 266 |--------|----------|
 267 | Clear | Sets to null (default) |
 268 | SetNull | Sets to null |
 269 | Restrict | Prevents deletion |
 270 
 271 ```xml
 272 <type>Lookup</type>
 273 <referenceTo>Account</referenceTo>
 274 <relationshipLabel>Related Records</relationshipLabel>
 275 <relationshipName>Related_Records</relationshipName>
 276 <deleteConstraint>SetNull</deleteConstraint>
 277 ```
 278 
 279 ---
 280 
 281 ### Master-Detail
 282 **Use When:** Required parent relationship
 283 **Features:**
 284 - Cannot be empty
 285 - Cascade delete
 286 - Supports roll-up summaries
 287 - Child sharing = parent sharing
 288 
 289 **Limitations:**
 290 - Max 2 per object
 291 - Cannot convert to Lookup after creation
 292 - Child object must be empty to create
 293 
 294 ```xml
 295 <type>MasterDetail</type>
 296 <referenceTo>Account</referenceTo>
 297 <relationshipLabel>Line Items</relationshipLabel>
 298 <relationshipName>Line_Items</relationshipName>
 299 <reparentableMasterDetail>false</reparentableMasterDetail>
 300 ```
 301 
 302 ---
 303 
 304 ## Calculated Fields
 305 
 306 ### Formula
 307 **Use When:** Derived value from same record
 308 **Return Types:** Text, Number, Currency, Percent, Date, DateTime, Checkbox
 309 **Limits:**
 310 - 5,000 compiled character limit
 311 - Can reference up to 10 relationships
 312 
 313 **Examples:**
 314 ```
 315 // Text concatenation
 316 FirstName & " " & LastName
 317 
 318 // Conditional
 319 IF(Amount > 100000, "Large", "Small")
 320 
 321 // Cross-object
 322 Account.Industry
 323 ```
 324 
 325 ```xml
 326 <type>Text</type>  <!-- or Number, Currency, etc. -->
 327 <formula>FirstName__c & " " & LastName__c</formula>
 328 ```
 329 
 330 ---
 331 
 332 ### Roll-Up Summary
 333 **Use When:** Aggregate child records
 334 **Requires:** Master-Detail relationship
 335 **Operations:** COUNT, SUM, MIN, MAX
 336 
 337 **Limitations:**
 338 - Only on Master-Detail parent
 339 - Cannot summarize formula fields
 340 - Cannot summarize Long Text or Multi-Select
 341 
 342 ```xml
 343 <type>Summary</type>
 344 <summaryOperation>sum</summaryOperation>
 345 <summarizedField>Line_Item__c.Amount__c</summarizedField>
 346 <summaryForeignKey>Line_Item__c.Order__c</summaryForeignKey>
 347 ```
 348 
 349 ---
 350 
 351 ## Special Fields
 352 
 353 ### Email
 354 - Max 80 characters
 355 - Format validation
 356 - Click-to-email in Lightning
 357 
 358 ### Phone
 359 - Max 40 characters
 360 - Click-to-dial support
 361 - No format validation
 362 
 363 ### URL
 364 - Max 255 characters
 365 - Clickable link
 366 - Opens in new tab
 367 
 368 ### Geolocation
 369 - Latitude/Longitude
 370 - Distance formulas
 371 - Map integration
 372 
 373 ### Encrypted Text
 374 - PII protection
 375 - Mask characters
 376 - Limited functionality
 377 
 378 ---
 379 
 380 ## Field Type Comparison
 381 
 382 | Feature | Text | Long Text | Picklist | Number | Lookup | Formula |
 383 |---------|------|-----------|----------|--------|--------|---------|
 384 | Searchable | ✅ | ❌ | ✅ | ✅ | ✅ | ✅* |
 385 | Filterable | ✅ | ❌ | ✅ | ✅ | ✅ | ✅* |
 386 | Reportable | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
 387 | Unique | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
 388 | External ID | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
 389 | Roll-up | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
 390 | Editable | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
 391 
 392 *Formula fields inherit searchability/filterability from return type
 393 
 394 ---
 395 
 396 ## Checklist: Choosing a Field Type
 397 
 398 1. **Data Nature**
 399    - [ ] Text, number, date, or boolean?
 400    - [ ] Predefined values or free-form?
 401    - [ ] Single value or relationship?
 402 
 403 2. **Requirements**
 404    - [ ] Required or optional?
 405    - [ ] Unique constraint needed?
 406    - [ ] External ID for integration?
 407 
 408 3. **Usage**
 409    - [ ] Will it be searched?
 410    - [ ] Will it be filtered/reported?
 411    - [ ] Will it be used in formulas?
 412    - [ ] Will it be used in roll-ups?
 413 
 414 4. **Performance**
 415    - [ ] Expected data volume?
 416    - [ ] Index needed?
 417    - [ ] Character limit appropriate?
