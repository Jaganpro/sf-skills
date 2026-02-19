<!-- Parent: sf-metadata/SKILL.md -->
   1 # Custom Object Example: Invoice
   2 
   3 This example demonstrates creating a complete custom object with fields, validation rules, and record types.
   4 
   5 ## Scenario
   6 
   7 Create an Invoice object for tracking customer invoices with:
   8 - Auto-numbered invoice number
   9 - Customer (Account) relationship
  10 - Line items (child object)
  11 - Status tracking
  12 - Validation rules
  13 
  14 ---
  15 
  16 ## Step 1: Create Custom Object
  17 
  18 **File:** `force-app/main/default/objects/Invoice__c/Invoice__c.object-meta.xml`
  19 
  20 ```xml
  21 <?xml version="1.0" encoding="UTF-8"?>
  22 <CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  23     <label>Invoice</label>
  24     <pluralLabel>Invoices</pluralLabel>
  25     <description>Tracks customer invoices and payment status</description>
  26 
  27     <nameField>
  28         <label>Invoice Number</label>
  29         <type>AutoNumber</type>
  30         <displayFormat>INV-{0000000}</displayFormat>
  31         <trackHistory>false</trackHistory>
  32     </nameField>
  33 
  34     <deploymentStatus>Deployed</deploymentStatus>
  35     <sharingModel>Private</sharingModel>
  36 
  37     <enableHistory>true</enableHistory>
  38     <enableActivities>true</enableActivities>
  39     <enableReports>true</enableReports>
  40     <enableSearch>true</enableSearch>
  41     <enableFeeds>false</enableFeeds>
  42     <enableBulkApi>true</enableBulkApi>
  43     <enableSharing>true</enableSharing>
  44     <enableStreamingApi>true</enableStreamingApi>
  45 
  46     <searchLayouts>
  47         <customTabListAdditionalFields>Name</customTabListAdditionalFields>
  48         <customTabListAdditionalFields>Account__c</customTabListAdditionalFields>
  49         <customTabListAdditionalFields>Total_Amount__c</customTabListAdditionalFields>
  50         <customTabListAdditionalFields>Status__c</customTabListAdditionalFields>
  51         <lookupDialogsAdditionalFields>Name</lookupDialogsAdditionalFields>
  52         <lookupDialogsAdditionalFields>Account__c</lookupDialogsAdditionalFields>
  53         <searchResultsAdditionalFields>Name</searchResultsAdditionalFields>
  54         <searchResultsAdditionalFields>Account__c</searchResultsAdditionalFields>
  55         <searchResultsAdditionalFields>Status__c</searchResultsAdditionalFields>
  56     </searchLayouts>
  57 
  58     <compactLayoutAssignment>SYSTEM</compactLayoutAssignment>
  59 </CustomObject>
  60 ```
  61 
  62 ---
  63 
  64 ## Step 2: Create Custom Fields
  65 
  66 ### Account Lookup
  67 **File:** `force-app/main/default/objects/Invoice__c/fields/Account__c.field-meta.xml`
  68 
  69 ```xml
  70 <?xml version="1.0" encoding="UTF-8"?>
  71 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  72     <fullName>Account__c</fullName>
  73     <label>Account</label>
  74     <type>Lookup</type>
  75     <referenceTo>Account</referenceTo>
  76     <relationshipLabel>Invoices</relationshipLabel>
  77     <relationshipName>Invoices</relationshipName>
  78     <required>true</required>
  79     <deleteConstraint>Restrict</deleteConstraint>
  80     <description>The customer account for this invoice</description>
  81     <inlineHelpText>Select the customer account</inlineHelpText>
  82     <trackHistory>true</trackHistory>
  83     <trackTrending>false</trackTrending>
  84 </CustomField>
  85 ```
  86 
  87 ### Status Picklist
  88 **File:** `force-app/main/default/objects/Invoice__c/fields/Status__c.field-meta.xml`
  89 
  90 ```xml
  91 <?xml version="1.0" encoding="UTF-8"?>
  92 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
  93     <fullName>Status__c</fullName>
  94     <label>Status</label>
  95     <type>Picklist</type>
  96     <required>true</required>
  97     <description>Current status of the invoice</description>
  98     <inlineHelpText>Select the invoice status</inlineHelpText>
  99     <trackHistory>true</trackHistory>
 100     <trackTrending>false</trackTrending>
 101     <valueSet>
 102         <restricted>true</restricted>
 103         <valueSetDefinition>
 104             <sorted>false</sorted>
 105             <value>
 106                 <fullName>Draft</fullName>
 107                 <default>true</default>
 108                 <label>Draft</label>
 109             </value>
 110             <value>
 111                 <fullName>Sent</fullName>
 112                 <default>false</default>
 113                 <label>Sent</label>
 114             </value>
 115             <value>
 116                 <fullName>Paid</fullName>
 117                 <default>false</default>
 118                 <label>Paid</label>
 119             </value>
 120             <value>
 121                 <fullName>Overdue</fullName>
 122                 <default>false</default>
 123                 <label>Overdue</label>
 124             </value>
 125             <value>
 126                 <fullName>Cancelled</fullName>
 127                 <default>false</default>
 128                 <label>Cancelled</label>
 129             </value>
 130         </valueSetDefinition>
 131     </valueSet>
 132 </CustomField>
 133 ```
 134 
 135 ### Invoice Date
 136 **File:** `force-app/main/default/objects/Invoice__c/fields/Invoice_Date__c.field-meta.xml`
 137 
 138 ```xml
 139 <?xml version="1.0" encoding="UTF-8"?>
 140 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 141     <fullName>Invoice_Date__c</fullName>
 142     <label>Invoice Date</label>
 143     <type>Date</type>
 144     <required>true</required>
 145     <defaultValue>TODAY()</defaultValue>
 146     <description>Date the invoice was issued</description>
 147     <inlineHelpText>Date the invoice was created</inlineHelpText>
 148     <trackHistory>true</trackHistory>
 149     <trackTrending>false</trackTrending>
 150 </CustomField>
 151 ```
 152 
 153 ### Due Date
 154 **File:** `force-app/main/default/objects/Invoice__c/fields/Due_Date__c.field-meta.xml`
 155 
 156 ```xml
 157 <?xml version="1.0" encoding="UTF-8"?>
 158 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 159     <fullName>Due_Date__c</fullName>
 160     <label>Due Date</label>
 161     <type>Date</type>
 162     <required>true</required>
 163     <defaultValue>TODAY() + 30</defaultValue>
 164     <description>Payment due date</description>
 165     <inlineHelpText>Date payment is due (default: 30 days from today)</inlineHelpText>
 166     <trackHistory>true</trackHistory>
 167     <trackTrending>false</trackTrending>
 168 </CustomField>
 169 ```
 170 
 171 ### Total Amount
 172 **File:** `force-app/main/default/objects/Invoice__c/fields/Total_Amount__c.field-meta.xml`
 173 
 174 ```xml
 175 <?xml version="1.0" encoding="UTF-8"?>
 176 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 177     <fullName>Total_Amount__c</fullName>
 178     <label>Total Amount</label>
 179     <type>Currency</type>
 180     <precision>18</precision>
 181     <scale>2</scale>
 182     <required>false</required>
 183     <defaultValue>0</defaultValue>
 184     <description>Total invoice amount (calculated from line items)</description>
 185     <inlineHelpText>Total amount including all line items</inlineHelpText>
 186     <trackHistory>true</trackHistory>
 187     <trackTrending>false</trackTrending>
 188 </CustomField>
 189 ```
 190 
 191 ### Payment Date
 192 **File:** `force-app/main/default/objects/Invoice__c/fields/Payment_Date__c.field-meta.xml`
 193 
 194 ```xml
 195 <?xml version="1.0" encoding="UTF-8"?>
 196 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 197     <fullName>Payment_Date__c</fullName>
 198     <label>Payment Date</label>
 199     <type>Date</type>
 200     <required>false</required>
 201     <description>Date payment was received</description>
 202     <inlineHelpText>Leave blank until payment is received</inlineHelpText>
 203     <trackHistory>true</trackHistory>
 204     <trackTrending>false</trackTrending>
 205 </CustomField>
 206 ```
 207 
 208 ### Days Overdue (Formula)
 209 **File:** `force-app/main/default/objects/Invoice__c/fields/Days_Overdue__c.field-meta.xml`
 210 
 211 ```xml
 212 <?xml version="1.0" encoding="UTF-8"?>
 213 <CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
 214     <fullName>Days_Overdue__c</fullName>
 215     <label>Days Overdue</label>
 216     <type>Number</type>
 217     <precision>18</precision>
 218     <scale>0</scale>
 219     <formula>IF(
 220     AND(
 221         ISBLANK(Payment_Date__c),
 222         Due_Date__c < TODAY(),
 223         NOT(ISPICKVAL(Status__c, 'Cancelled'))
 224     ),
 225     TODAY() - Due_Date__c,
 226     0
 227 )</formula>
 228     <formulaTreatBlanksAs>BlankAsZero</formulaTreatBlanksAs>
 229     <description>Number of days past due date</description>
 230     <inlineHelpText>Calculated days overdue (0 if paid or not yet due)</inlineHelpText>
 231     <trackHistory>false</trackHistory>
 232     <trackTrending>false</trackTrending>
 233 </CustomField>
 234 ```
 235 
 236 ---
 237 
 238 ## Step 3: Create Validation Rules
 239 
 240 ### Require Payment Date When Paid
 241 **File:** `force-app/main/default/objects/Invoice__c/validationRules/Require_Payment_Date_When_Paid.validationRule-meta.xml`
 242 
 243 ```xml
 244 <?xml version="1.0" encoding="UTF-8"?>
 245 <ValidationRule xmlns="http://soap.sforce.com/2006/04/metadata">
 246     <fullName>Require_Payment_Date_When_Paid</fullName>
 247     <active>true</active>
 248     <description>Ensures Payment Date is filled when Status is set to Paid</description>
 249     <errorConditionFormula>AND(
 250     NOT($Permission.Bypass_Validation__c),
 251     ISPICKVAL(Status__c, 'Paid'),
 252     ISBLANK(Payment_Date__c)
 253 )</errorConditionFormula>
 254     <errorDisplayField>Payment_Date__c</errorDisplayField>
 255     <errorMessage>Payment Date is required when marking an invoice as Paid.</errorMessage>
 256 </ValidationRule>
 257 ```
 258 
 259 ### Due Date After Invoice Date
 260 **File:** `force-app/main/default/objects/Invoice__c/validationRules/Due_Date_After_Invoice_Date.validationRule-meta.xml`
 261 
 262 ```xml
 263 <?xml version="1.0" encoding="UTF-8"?>
 264 <ValidationRule xmlns="http://soap.sforce.com/2006/04/metadata">
 265     <fullName>Due_Date_After_Invoice_Date</fullName>
 266     <active>true</active>
 267     <description>Ensures Due Date is on or after Invoice Date</description>
 268     <errorConditionFormula>AND(
 269     NOT($Permission.Bypass_Validation__c),
 270     Due_Date__c < Invoice_Date__c
 271 )</errorConditionFormula>
 272     <errorDisplayField>Due_Date__c</errorDisplayField>
 273     <errorMessage>Due Date must be on or after the Invoice Date.</errorMessage>
 274 </ValidationRule>
 275 ```
 276 
 277 ---
 278 
 279 ## Step 4: Create Record Type (Optional)
 280 
 281 **File:** `force-app/main/default/objects/Invoice__c/recordTypes/Standard_Invoice.recordType-meta.xml`
 282 
 283 ```xml
 284 <?xml version="1.0" encoding="UTF-8"?>
 285 <RecordType xmlns="http://soap.sforce.com/2006/04/metadata">
 286     <fullName>Standard_Invoice</fullName>
 287     <active>true</active>
 288     <label>Standard Invoice</label>
 289     <description>Standard invoice for regular billing</description>
 290 </RecordType>
 291 ```
 292 
 293 ---
 294 
 295 ## Directory Structure
 296 
 297 ```
 298 force-app/main/default/objects/Invoice__c/
 299 ├── Invoice__c.object-meta.xml
 300 ├── fields/
 301 │   ├── Account__c.field-meta.xml
 302 │   ├── Status__c.field-meta.xml
 303 │   ├── Invoice_Date__c.field-meta.xml
 304 │   ├── Due_Date__c.field-meta.xml
 305 │   ├── Total_Amount__c.field-meta.xml
 306 │   ├── Payment_Date__c.field-meta.xml
 307 │   └── Days_Overdue__c.field-meta.xml
 308 ├── validationRules/
 309 │   ├── Require_Payment_Date_When_Paid.validationRule-meta.xml
 310 │   └── Due_Date_After_Invoice_Date.validationRule-meta.xml
 311 └── recordTypes/
 312     └── Standard_Invoice.recordType-meta.xml
 313 ```
 314 
 315 ---
 316 
 317 ## Deployment
 318 
 319 ```bash
 320 # Validate
 321 sf project deploy start \
 322   --source-dir force-app/main/default/objects/Invoice__c \
 323   --target-org myorg \
 324   --dry-run
 325 
 326 # Deploy
 327 sf project deploy start \
 328   --source-dir force-app/main/default/objects/Invoice__c \
 329   --target-org myorg
 330 ```
 331 
 332 ---
 333 
 334 ## Next Steps
 335 
 336 1. Create Permission Set for Invoice access
 337 2. Create Page Layout
 338 3. Create related Line Item object (Master-Detail)
 339 4. Build Flows for automation
 340 5. Create Reports and Dashboards
