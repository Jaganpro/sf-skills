<!-- Parent: sf-metadata/SKILL.md -->
   1 # Field Types Example: Complete Reference
   2 
   3 This example demonstrates all common field types with real-world usage.
   4 
   5 ---
   6 
   7 ## Text Fields
   8 
   9 ### Standard Text
  10 ```xml
  11 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  12     <fullName>Product_SKU__c</fullName>
  13     <label>Product SKU</label>
  14     <type>Text</type>
  15     <length>50</length>
  16     <required>true</required>
  17     <unique>true</unique>
  18     <externalId>true</externalId>
  19     <caseSensitive>false</caseSensitive>
  20     <description>Unique product identifier for inventory</description>
  21     <inlineHelpText>Enter the unique SKU (e.g., SKU-12345)</inlineHelpText>
  22 </CustomField>
  23 ```
  24 
  25 ### Long Text Area
  26 ```xml
  27 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  28     <fullName>Internal_Notes__c</fullName>
  29     <label>Internal Notes</label>
  30     <type>LongTextArea</type>
  31     <length>32000</length>
  32     <visibleLines>6</visibleLines>
  33     <description>Internal team notes (not visible to customers)</description>
  34     <inlineHelpText>Add any internal notes or comments</inlineHelpText>
  35 </CustomField>
  36 ```
  37 
  38 ### Rich Text Area
  39 ```xml
  40 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  41     <fullName>Product_Description__c</fullName>
  42     <label>Product Description</label>
  43     <type>Html</type>
  44     <length>32000</length>
  45     <visibleLines>10</visibleLines>
  46     <description>Rich text product description for marketing</description>
  47     <inlineHelpText>Format description with bold, lists, and images</inlineHelpText>
  48 </CustomField>
  49 ```
  50 
  51 ---
  52 
  53 ## Numeric Fields
  54 
  55 ### Integer (Whole Number)
  56 ```xml
  57 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  58     <fullName>Quantity__c</fullName>
  59     <label>Quantity</label>
  60     <type>Number</type>
  61     <precision>18</precision>
  62     <scale>0</scale>
  63     <required>true</required>
  64     <defaultValue>1</defaultValue>
  65     <description>Number of units ordered</description>
  66     <inlineHelpText>Enter quantity (whole numbers only)</inlineHelpText>
  67 </CustomField>
  68 ```
  69 
  70 ### Decimal
  71 ```xml
  72 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  73     <fullName>Weight_Kg__c</fullName>
  74     <label>Weight (kg)</label>
  75     <type>Number</type>
  76     <precision>10</precision>
  77     <scale>3</scale>
  78     <required>false</required>
  79     <description>Product weight in kilograms</description>
  80     <inlineHelpText>Enter weight with up to 3 decimal places</inlineHelpText>
  81 </CustomField>
  82 ```
  83 
  84 ### Currency
  85 ```xml
  86 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  87     <fullName>Unit_Price__c</fullName>
  88     <label>Unit Price</label>
  89     <type>Currency</type>
  90     <precision>18</precision>
  91     <scale>2</scale>
  92     <required>true</required>
  93     <defaultValue>0</defaultValue>
  94     <description>Price per unit</description>
  95     <inlineHelpText>Enter the price per unit</inlineHelpText>
  96 </CustomField>
  97 ```
  98 
  99 ### Percent
 100 ```xml
 101 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 102     <fullName>Discount_Percent__c</fullName>
 103     <label>Discount %</label>
 104     <type>Percent</type>
 105     <precision>5</precision>
 106     <scale>2</scale>
 107     <required>false</required>
 108     <defaultValue>0</defaultValue>
 109     <description>Discount percentage applied</description>
 110     <inlineHelpText>Enter discount as percentage (e.g., 10 for 10%)</inlineHelpText>
 111 </CustomField>
 112 ```
 113 
 114 ---
 115 
 116 ## Date/Time Fields
 117 
 118 ### Date
 119 ```xml
 120 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 121     <fullName>Contract_Start_Date__c</fullName>
 122     <label>Contract Start Date</label>
 123     <type>Date</type>
 124     <required>true</required>
 125     <defaultValue>TODAY()</defaultValue>
 126     <description>Date the contract becomes effective</description>
 127     <inlineHelpText>When does this contract take effect?</inlineHelpText>
 128 </CustomField>
 129 ```
 130 
 131 ### DateTime
 132 ```xml
 133 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 134     <fullName>Last_Contact_DateTime__c</fullName>
 135     <label>Last Contact Date/Time</label>
 136     <type>DateTime</type>
 137     <required>false</required>
 138     <description>Last time we contacted this customer</description>
 139     <inlineHelpText>Date and time of most recent contact</inlineHelpText>
 140 </CustomField>
 141 ```
 142 
 143 ---
 144 
 145 ## Boolean Field
 146 
 147 ### Checkbox
 148 ```xml
 149 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 150     <fullName>Is_VIP_Customer__c</fullName>
 151     <label>VIP Customer</label>
 152     <type>Checkbox</type>
 153     <defaultValue>false</defaultValue>
 154     <description>Indicates if customer has VIP status</description>
 155     <inlineHelpText>Check if this is a VIP customer</inlineHelpText>
 156 </CustomField>
 157 ```
 158 
 159 ---
 160 
 161 ## Picklist Fields
 162 
 163 ### Single-Select Picklist
 164 ```xml
 165 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 166     <fullName>Priority__c</fullName>
 167     <label>Priority</label>
 168     <type>Picklist</type>
 169     <required>true</required>
 170     <description>Task priority level</description>
 171     <inlineHelpText>Select the priority level</inlineHelpText>
 172     <valueSet>
 173         <restricted>true</restricted>
 174         <valueSetDefinition>
 175             <sorted>false</sorted>
 176             <value>
 177                 <fullName>Low</fullName>
 178                 <default>false</default>
 179                 <label>Low</label>
 180             </value>
 181             <value>
 182                 <fullName>Medium</fullName>
 183                 <default>true</default>
 184                 <label>Medium</label>
 185             </value>
 186             <value>
 187                 <fullName>High</fullName>
 188                 <default>false</default>
 189                 <label>High</label>
 190             </value>
 191             <value>
 192                 <fullName>Critical</fullName>
 193                 <default>false</default>
 194                 <label>Critical</label>
 195             </value>
 196         </valueSetDefinition>
 197     </valueSet>
 198 </CustomField>
 199 ```
 200 
 201 ### Multi-Select Picklist
 202 ```xml
 203 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 204     <fullName>Product_Categories__c</fullName>
 205     <label>Product Categories</label>
 206     <type>MultiselectPicklist</type>
 207     <visibleLines>4</visibleLines>
 208     <required>false</required>
 209     <description>Categories this product belongs to</description>
 210     <inlineHelpText>Select all applicable categories</inlineHelpText>
 211     <valueSet>
 212         <restricted>true</restricted>
 213         <valueSetDefinition>
 214             <sorted>true</sorted>
 215             <value>
 216                 <fullName>Electronics</fullName>
 217                 <label>Electronics</label>
 218             </value>
 219             <value>
 220                 <fullName>Clothing</fullName>
 221                 <label>Clothing</label>
 222             </value>
 223             <value>
 224                 <fullName>Home_Garden</fullName>
 225                 <label>Home &amp; Garden</label>
 226             </value>
 227             <value>
 228                 <fullName>Sports</fullName>
 229                 <label>Sports</label>
 230             </value>
 231         </valueSetDefinition>
 232     </valueSet>
 233 </CustomField>
 234 ```
 235 
 236 ---
 237 
 238 ## Relationship Fields
 239 
 240 ### Lookup
 241 ```xml
 242 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 243     <fullName>Primary_Contact__c</fullName>
 244     <label>Primary Contact</label>
 245     <type>Lookup</type>
 246     <referenceTo>Contact</referenceTo>
 247     <relationshipLabel>Primary For</relationshipLabel>
 248     <relationshipName>Primary_For</relationshipName>
 249     <required>false</required>
 250     <deleteConstraint>SetNull</deleteConstraint>
 251     <description>Main contact person for this account</description>
 252     <inlineHelpText>Select the primary contact</inlineHelpText>
 253     <lookupFilter>
 254         <active>true</active>
 255         <filterItems>
 256             <field>Contact.AccountId</field>
 257             <operation>equals</operation>
 258             <valueField>$Source.AccountId</valueField>
 259         </filterItems>
 260         <isOptional>false</isOptional>
 261     </lookupFilter>
 262 </CustomField>
 263 ```
 264 
 265 ### Master-Detail
 266 ```xml
 267 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 268     <fullName>Order__c</fullName>
 269     <label>Order</label>
 270     <type>MasterDetail</type>
 271     <referenceTo>Order__c</referenceTo>
 272     <relationshipLabel>Line Items</relationshipLabel>
 273     <relationshipName>Line_Items</relationshipName>
 274     <relationshipOrder>0</relationshipOrder>
 275     <reparentableMasterDetail>false</reparentableMasterDetail>
 276     <writeRequiresMasterRead>false</writeRequiresMasterRead>
 277     <description>Parent order for this line item</description>
 278     <inlineHelpText>The order this line item belongs to</inlineHelpText>
 279 </CustomField>
 280 ```
 281 
 282 ---
 283 
 284 ## Special Fields
 285 
 286 ### Email
 287 ```xml
 288 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 289     <fullName>Support_Email__c</fullName>
 290     <label>Support Email</label>
 291     <type>Email</type>
 292     <required>false</required>
 293     <unique>false</unique>
 294     <description>Customer support contact email</description>
 295     <inlineHelpText>Email address for support inquiries</inlineHelpText>
 296 </CustomField>
 297 ```
 298 
 299 ### Phone
 300 ```xml
 301 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 302     <fullName>Mobile_Phone__c</fullName>
 303     <label>Mobile Phone</label>
 304     <type>Phone</type>
 305     <required>false</required>
 306     <description>Mobile phone number</description>
 307     <inlineHelpText>Enter mobile number including country code</inlineHelpText>
 308 </CustomField>
 309 ```
 310 
 311 ### URL
 312 ```xml
 313 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 314     <fullName>LinkedIn_Profile__c</fullName>
 315     <label>LinkedIn Profile</label>
 316     <type>Url</type>
 317     <required>false</required>
 318     <description>LinkedIn profile URL</description>
 319     <inlineHelpText>Enter full LinkedIn URL (https://linkedin.com/in/...)</inlineHelpText>
 320 </CustomField>
 321 ```
 322 
 323 ---
 324 
 325 ## Formula Fields
 326 
 327 ### Text Formula
 328 ```xml
 329 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 330     <fullName>Full_Address__c</fullName>
 331     <label>Full Address</label>
 332     <type>Text</type>
 333     <formula>Street__c &amp; BR() &amp;
 334 City__c &amp; ", " &amp; State__c &amp; " " &amp; Postal_Code__c &amp; BR() &amp;
 335 Country__c</formula>
 336     <description>Formatted complete address</description>
 337 </CustomField>
 338 ```
 339 
 340 ### Number Formula (Calculated)
 341 ```xml
 342 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 343     <fullName>Line_Total__c</fullName>
 344     <label>Line Total</label>
 345     <type>Currency</type>
 346     <precision>18</precision>
 347     <scale>2</scale>
 348     <formula>Quantity__c * Unit_Price__c * (1 - BLANKVALUE(Discount_Percent__c, 0) / 100)</formula>
 349     <formulaTreatBlanksAs>BlankAsZero</formulaTreatBlanksAs>
 350     <description>Calculated line item total with discount</description>
 351 </CustomField>
 352 ```
 353 
 354 ### Checkbox Formula
 355 ```xml
 356 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 357     <fullName>Is_Overdue__c</fullName>
 358     <label>Is Overdue</label>
 359     <type>Checkbox</type>
 360     <formula>AND(
 361     NOT(ISPICKVAL(Status__c, 'Paid')),
 362     NOT(ISPICKVAL(Status__c, 'Cancelled')),
 363     Due_Date__c < TODAY()
 364 )</formula>
 365     <description>True if invoice is past due date and not paid</description>
 366 </CustomField>
 367 ```
 368 
 369 ---
 370 
 371 ## Roll-Up Summary
 372 
 373 ```xml
 374 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 375     <fullName>Total_Line_Items__c</fullName>
 376     <label>Total Line Items</label>
 377     <type>Summary</type>
 378     <summarizedField>Order_Line_Item__c.Line_Total__c</summarizedField>
 379     <summaryForeignKey>Order_Line_Item__c.Order__c</summaryForeignKey>
 380     <summaryOperation>sum</summaryOperation>
 381     <description>Sum of all line item totals</description>
 382 </CustomField>
 383 ```
 384 
 385 ### Roll-Up with Filter
 386 ```xml
 387 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 388     <fullName>Completed_Tasks_Count__c</fullName>
 389     <label>Completed Tasks</label>
 390     <type>Summary</type>
 391     <summaryForeignKey>Project_Task__c.Project__c</summaryForeignKey>
 392     <summaryOperation>count</summaryOperation>
 393     <summaryFilterItems>
 394         <field>Project_Task__c.Status__c</field>
 395         <operation>equals</operation>
 396         <value>Completed</value>
 397     </summaryFilterItems>
 398     <description>Count of completed tasks on this project</description>
 399 </CustomField>
 400 ```
 401 
 402 ---
 403 
 404 ## Summary
 405 
 406 | Field Type | Use Case | Key Settings |
 407 |------------|----------|--------------|
 408 | Text | Short strings | `length` (1-255) |
 409 | LongTextArea | Multi-line text | `length`, `visibleLines` |
 410 | Number | Quantities, rates | `precision`, `scale` |
 411 | Currency | Money | `precision`, `scale` |
 412 | Date | Calendar dates | - |
 413 | DateTime | Timestamps | - |
 414 | Checkbox | True/False | `defaultValue` (required) |
 415 | Picklist | Single choice | `valueSet` |
 416 | MultiselectPicklist | Multiple choices | `valueSet`, `visibleLines` |
 417 | Lookup | Optional relationship | `referenceTo`, `deleteConstraint` |
 418 | MasterDetail | Required relationship | `referenceTo`, `relationshipOrder` |
 419 | Formula | Calculated | `formula`, return type |
 420 | Summary | Aggregation | `summaryOperation`, `summarizedField` |
