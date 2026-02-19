<!-- Parent: sf-metadata/SKILL.md -->
   1 # Permission Set Example: Invoice Manager
   2 
   3 This example demonstrates creating a comprehensive permission set with object permissions, field-level security, and related access.
   4 
   5 ---
   6 
   7 ## Scenario
   8 
   9 Create a Permission Set for users who manage invoices:
  10 - Full CRUD on Invoice object
  11 - Edit access to specific fields
  12 - Read access to Account (parent)
  13 - Tab visibility
  14 - Custom permission for approvals
  15 
  16 ---
  17 
  18 ## Permission Set Definition
  19 
  20 **File:** `force-app/main/default/permissionsets/Invoice_Manager.permissionset-meta.xml`
  21 
  22 ```xml
  23 <?xml version="1.0" encoding="UTF-8"?>
  24 <PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
  25     <!-- Basic Info -->
  26     <label>Invoice Manager</label>
  27     <description>Full access to manage invoices including creation, editing, and approval. Assign to users responsible for invoice processing.</description>
  28     <hasActivationRequired>false</hasActivationRequired>
  29 
  30     <!--
  31     ═══════════════════════════════════════════════════════════════
  32     OBJECT PERMISSIONS
  33     ═══════════════════════════════════════════════════════════════
  34     -->
  35 
  36     <!-- Invoice Object: Full CRUD -->
  37     <objectPermissions>
  38         <allowCreate>true</allowCreate>
  39         <allowDelete>true</allowDelete>
  40         <allowEdit>true</allowEdit>
  41         <allowRead>true</allowRead>
  42         <modifyAllRecords>false</modifyAllRecords>
  43         <object>Invoice__c</object>
  44         <viewAllRecords>false</viewAllRecords>
  45     </objectPermissions>
  46 
  47     <!-- Invoice Line Item: Full CRUD (child object) -->
  48     <objectPermissions>
  49         <allowCreate>true</allowCreate>
  50         <allowDelete>true</allowDelete>
  51         <allowEdit>true</allowEdit>
  52         <allowRead>true</allowRead>
  53         <modifyAllRecords>false</modifyAllRecords>
  54         <object>Invoice_Line_Item__c</object>
  55         <viewAllRecords>false</viewAllRecords>
  56     </objectPermissions>
  57 
  58     <!-- Account: Read Only (for invoice lookups) -->
  59     <objectPermissions>
  60         <allowCreate>false</allowCreate>
  61         <allowDelete>false</allowDelete>
  62         <allowEdit>false</allowEdit>
  63         <allowRead>true</allowRead>
  64         <modifyAllRecords>false</modifyAllRecords>
  65         <object>Account</object>
  66         <viewAllRecords>false</viewAllRecords>
  67     </objectPermissions>
  68 
  69     <!--
  70     ═══════════════════════════════════════════════════════════════
  71     FIELD PERMISSIONS - Invoice__c
  72     ═══════════════════════════════════════════════════════════════
  73     -->
  74 
  75     <!-- Account lookup: Read + Edit -->
  76     <fieldPermissions>
  77         <editable>true</editable>
  78         <field>Invoice__c.Account__c</field>
  79         <readable>true</readable>
  80     </fieldPermissions>
  81 
  82     <!-- Status: Read + Edit -->
  83     <fieldPermissions>
  84         <editable>true</editable>
  85         <field>Invoice__c.Status__c</field>
  86         <readable>true</readable>
  87     </fieldPermissions>
  88 
  89     <!-- Invoice Date: Read + Edit -->
  90     <fieldPermissions>
  91         <editable>true</editable>
  92         <field>Invoice__c.Invoice_Date__c</field>
  93         <readable>true</readable>
  94     </fieldPermissions>
  95 
  96     <!-- Due Date: Read + Edit -->
  97     <fieldPermissions>
  98         <editable>true</editable>
  99         <field>Invoice__c.Due_Date__c</field>
 100         <readable>true</readable>
 101     </fieldPermissions>
 102 
 103     <!-- Total Amount: Read Only (calculated) -->
 104     <fieldPermissions>
 105         <editable>false</editable>
 106         <field>Invoice__c.Total_Amount__c</field>
 107         <readable>true</readable>
 108     </fieldPermissions>
 109 
 110     <!-- Payment Date: Read + Edit -->
 111     <fieldPermissions>
 112         <editable>true</editable>
 113         <field>Invoice__c.Payment_Date__c</field>
 114         <readable>true</readable>
 115     </fieldPermissions>
 116 
 117     <!-- Days Overdue: Read Only (formula) -->
 118     <fieldPermissions>
 119         <editable>false</editable>
 120         <field>Invoice__c.Days_Overdue__c</field>
 121         <readable>true</readable>
 122     </fieldPermissions>
 123 
 124     <!-- Internal Notes: Read + Edit -->
 125     <fieldPermissions>
 126         <editable>true</editable>
 127         <field>Invoice__c.Internal_Notes__c</field>
 128         <readable>true</readable>
 129     </fieldPermissions>
 130 
 131     <!--
 132     ═══════════════════════════════════════════════════════════════
 133     FIELD PERMISSIONS - Invoice_Line_Item__c
 134     ═══════════════════════════════════════════════════════════════
 135     -->
 136 
 137     <fieldPermissions>
 138         <editable>true</editable>
 139         <field>Invoice_Line_Item__c.Product__c</field>
 140         <readable>true</readable>
 141     </fieldPermissions>
 142 
 143     <fieldPermissions>
 144         <editable>true</editable>
 145         <field>Invoice_Line_Item__c.Quantity__c</field>
 146         <readable>true</readable>
 147     </fieldPermissions>
 148 
 149     <fieldPermissions>
 150         <editable>true</editable>
 151         <field>Invoice_Line_Item__c.Unit_Price__c</field>
 152         <readable>true</readable>
 153     </fieldPermissions>
 154 
 155     <fieldPermissions>
 156         <editable>false</editable>
 157         <field>Invoice_Line_Item__c.Line_Total__c</field>
 158         <readable>true</readable>
 159     </fieldPermissions>
 160 
 161     <!--
 162     ═══════════════════════════════════════════════════════════════
 163     TAB SETTINGS
 164     ═══════════════════════════════════════════════════════════════
 165     -->
 166 
 167     <tabSettings>
 168         <tab>Invoice__c</tab>
 169         <visibility>Visible</visibility>
 170     </tabSettings>
 171 
 172     <tabSettings>
 173         <tab>Invoice_Line_Item__c</tab>
 174         <visibility>Visible</visibility>
 175     </tabSettings>
 176 
 177     <!--
 178     ═══════════════════════════════════════════════════════════════
 179     RECORD TYPE ACCESS
 180     ═══════════════════════════════════════════════════════════════
 181     -->
 182 
 183     <recordTypeVisibilities>
 184         <recordType>Invoice__c.Standard_Invoice</recordType>
 185         <visible>true</visible>
 186     </recordTypeVisibilities>
 187 
 188     <recordTypeVisibilities>
 189         <recordType>Invoice__c.Credit_Note</recordType>
 190         <visible>true</visible>
 191     </recordTypeVisibilities>
 192 
 193     <!--
 194     ═══════════════════════════════════════════════════════════════
 195     CUSTOM PERMISSIONS
 196     ═══════════════════════════════════════════════════════════════
 197     -->
 198 
 199     <!-- Permission to approve invoices over threshold -->
 200     <customPermissions>
 201         <enabled>true</enabled>
 202         <name>Invoice_Approval</name>
 203     </customPermissions>
 204 
 205     <!-- Permission to bypass validation rules -->
 206     <customPermissions>
 207         <enabled>false</enabled>
 208         <name>Bypass_Validation</name>
 209     </customPermissions>
 210 
 211     <!--
 212     ═══════════════════════════════════════════════════════════════
 213     APEX CLASS ACCESS
 214     ═══════════════════════════════════════════════════════════════
 215     -->
 216 
 217     <classAccesses>
 218         <apexClass>InvoiceController</apexClass>
 219         <enabled>true</enabled>
 220     </classAccesses>
 221 
 222     <classAccesses>
 223         <apexClass>InvoicePDFGenerator</apexClass>
 224         <enabled>true</enabled>
 225     </classAccesses>
 226 
 227     <!--
 228     ═══════════════════════════════════════════════════════════════
 229     PAGE ACCESS (Visualforce/LWC)
 230     ═══════════════════════════════════════════════════════════════
 231     -->
 232 
 233     <pageAccesses>
 234         <apexPage>InvoicePDF</apexPage>
 235         <enabled>true</enabled>
 236     </pageAccesses>
 237 
 238 </PermissionSet>
 239 ```
 240 
 241 ---
 242 
 243 ## Related Custom Permission
 244 
 245 **File:** `force-app/main/default/customPermissions/Invoice_Approval.customPermission-meta.xml`
 246 
 247 ```xml
 248 <?xml version="1.0" encoding="UTF-8"?>
 249 <CustomPermission xmlns="http://soap.sforce.com/2006/04/metadata">
 250     <label>Invoice Approval</label>
 251     <description>Allows user to approve invoices over the standard threshold. Check this permission in Apex using FeatureManagement.checkPermission('Invoice_Approval').</description>
 252     <isLicensed>false</isLicensed>
 253 </CustomPermission>
 254 ```
 255 
 256 ---
 257 
 258 ## Read-Only Permission Set Variant
 259 
 260 **File:** `force-app/main/default/permissionsets/Invoice_Viewer.permissionset-meta.xml`
 261 
 262 ```xml
 263 <?xml version="1.0" encoding="UTF-8"?>
 264 <PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
 265     <label>Invoice Viewer</label>
 266     <description>Read-only access to invoices. For users who need to view but not modify invoice data.</description>
 267     <hasActivationRequired>false</hasActivationRequired>
 268 
 269     <!-- Invoice: Read Only -->
 270     <objectPermissions>
 271         <allowCreate>false</allowCreate>
 272         <allowDelete>false</allowDelete>
 273         <allowEdit>false</allowEdit>
 274         <allowRead>true</allowRead>
 275         <modifyAllRecords>false</modifyAllRecords>
 276         <object>Invoice__c</object>
 277         <viewAllRecords>false</viewAllRecords>
 278     </objectPermissions>
 279 
 280     <!-- All fields: Read Only -->
 281     <fieldPermissions>
 282         <editable>false</editable>
 283         <field>Invoice__c.Account__c</field>
 284         <readable>true</readable>
 285     </fieldPermissions>
 286 
 287     <fieldPermissions>
 288         <editable>false</editable>
 289         <field>Invoice__c.Status__c</field>
 290         <readable>true</readable>
 291     </fieldPermissions>
 292 
 293     <fieldPermissions>
 294         <editable>false</editable>
 295         <field>Invoice__c.Total_Amount__c</field>
 296         <readable>true</readable>
 297     </fieldPermissions>
 298 
 299     <!-- Tab: Visible -->
 300     <tabSettings>
 301         <tab>Invoice__c</tab>
 302         <visibility>Visible</visibility>
 303     </tabSettings>
 304 </PermissionSet>
 305 ```
 306 
 307 ---
 308 
 309 ## Permission Set Group
 310 
 311 **File:** `force-app/main/default/permissionsetgroups/Finance_Team.permissionsetgroup-meta.xml`
 312 
 313 ```xml
 314 <?xml version="1.0" encoding="UTF-8"?>
 315 <PermissionSetGroup xmlns="http://soap.sforce.com/2006/04/metadata">
 316     <label>Finance Team</label>
 317     <description>Combined permissions for Finance team members including invoice management and reporting.</description>
 318     <permissionSets>
 319         <permissionSet>Invoice_Manager</permissionSet>
 320         <permissionSet>Report_Builder</permissionSet>
 321         <permissionSet>Dashboard_Viewer</permissionSet>
 322     </permissionSets>
 323     <status>Enabled</status>
 324 </PermissionSetGroup>
 325 ```
 326 
 327 ---
 328 
 329 ## Using Custom Permission in Apex
 330 
 331 ```apex
 332 public class InvoiceService {
 333 
 334     public static void approveInvoice(Invoice__c invoice) {
 335         // Check custom permission
 336         if (invoice.Total_Amount__c > 10000 &&
 337             !FeatureManagement.checkPermission('Invoice_Approval')) {
 338             throw new InsufficientPermissionException(
 339                 'You do not have permission to approve invoices over $10,000'
 340             );
 341         }
 342 
 343         invoice.Status__c = 'Approved';
 344         update invoice;
 345     }
 346 
 347     public class InsufficientPermissionException extends Exception {}
 348 }
 349 ```
 350 
 351 ---
 352 
 353 ## Directory Structure
 354 
 355 ```
 356 force-app/main/default/
 357 ├── permissionsets/
 358 │   ├── Invoice_Manager.permissionset-meta.xml
 359 │   └── Invoice_Viewer.permissionset-meta.xml
 360 ├── permissionsetgroups/
 361 │   └── Finance_Team.permissionsetgroup-meta.xml
 362 └── customPermissions/
 363     └── Invoice_Approval.customPermission-meta.xml
 364 ```
 365 
 366 ---
 367 
 368 ## Deployment
 369 
 370 ```bash
 371 # Deploy permission set
 372 sf project deploy start \
 373   --source-dir force-app/main/default/permissionsets/Invoice_Manager.permissionset-meta.xml \
 374   --target-org myorg
 375 
 376 # Deploy all security metadata
 377 sf project deploy start \
 378   --source-dir force-app/main/default/permissionsets \
 379   --source-dir force-app/main/default/permissionsetgroups \
 380   --source-dir force-app/main/default/customPermissions \
 381   --target-org myorg
 382 ```
 383 
 384 ---
 385 
 386 ## Assignment
 387 
 388 ```bash
 389 # Assign permission set to user
 390 sf org assign permset --name Invoice_Manager --target-org myorg --on-behalf-of user@example.com
 391 
 392 # Assign permission set group
 393 sf org assign permset --name Finance_Team --target-org myorg --on-behalf-of user@example.com
 394 ```
 395 
 396 ---
 397 
 398 ## Best Practices Summary
 399 
 400 1. **Name by function**: `Invoice_Manager`, not `Finance_PS_1`
 401 2. **Document purpose**: Clear description for each permission set
 402 3. **Least privilege**: Only grant what's needed
 403 4. **Group related sets**: Use Permission Set Groups for roles
 404 5. **Use Custom Permissions**: For feature flags in Apex
 405 6. **Separate read/write**: Create viewer variants for read-only users
