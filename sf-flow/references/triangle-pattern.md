<!-- Parent: sf-flow/SKILL.md -->
   1 # Flow-LWC-Apex Triangle: Flow Perspective
   2 
   3 The **Triangle Architecture** is a foundational Salesforce pattern where Flow, LWC, and Apex work together. This guide focuses on the **Flow role** as the orchestrator.
   4 
   5 ---
   6 
   7 ## Architecture Overview
   8 
   9 ```
  10                          ┌─────────────────────────────────────┐
  11                          │              FLOW              ◀── YOU ARE HERE
  12                          │         (Orchestrator)              │
  13                          │                                     │
  14                          │  • Process Logic                    │
  15                          │  • User Experience                  │
  16                          │  • Variable Management              │
  17                          └───────────────┬─────────────────────┘
  18                                          │
  19               ┌──────────────────────────┼──────────────────────────┐
  20               │                          │                          │
  21               │ screens                  │ actionCalls              │
  22               │ <componentInstance>      │ actionType="apex"        │
  23               │                          │                          │
  24               ▼                          ▼                          ▲
  25 ┌─────────────────────────┐    ┌─────────────────────────┐         │
  26 │          LWC            │    │         APEX            │         │
  27 │     (UI Component)      │───▶│   (Business Logic)      │─────────┘
  28 │                         │    │                         │
  29 │ • Rich UI/UX            │    │ • @InvocableMethod      │
  30 │ • User Interaction      │    │ • @AuraEnabled          │
  31 │ • FlowAttribute         │    │ • Complex Logic         │
  32 │   ChangeEvent           │    │ • DML Operations        │
  33 │ • FlowNavigation        │    │ • Integration           │
  34 │   FinishEvent           │    │                         │
  35 └─────────────────────────┘    └─────────────────────────┘
  36 ```
  37 
  38 ---
  39 
  40 ## Flow's Role in the Triangle
  41 
  42 | Communication Path | Flow XML Element | Direction |
  43 |-------------------|------------------|-----------|
  44 | Flow → LWC | `inputParameters` in `<screens>` | Push data to component |
  45 | LWC → Flow | `outputParameters` in `<screens>` | Receive from component |
  46 | Flow → Apex | `actionCalls` with `actionType="apex"` | Call Invocable |
  47 | Apex → Flow | `outputParameters` in `<actionCalls>` | Receive results |
  48 
  49 ---
  50 
  51 ## Pattern 1: Flow Embedding LWC Screen Component
  52 
  53 **Use Case**: Custom UI component for user selection within a guided Flow.
  54 
  55 ```
  56 ┌─────────┐     inputParameters     ┌─────────┐
  57 │  FLOW   │ ─────────────────────▶  │   LWC   │
  58 │ Screen  │                         │Component│
  59 │         │ ◀─────────────────────  │         │
  60 │         │    outputParameters     │         │
  61 └─────────┘                         └─────────┘
  62 ```
  63 
  64 ### Flow XML
  65 
  66 ```xml
  67 <screens>
  68     <name>Select_Record_Screen</name>
  69     <label>Select Record</label>
  70     <locationX>264</locationX>
  71     <locationY>398</locationY>
  72     <allowBack>true</allowBack>
  73     <allowFinish>true</allowFinish>
  74     <allowPause>false</allowPause>
  75     <connector>
  76         <targetReference>Process_Selection</targetReference>
  77     </connector>
  78     <fields>
  79         <name>recordSelectorComponent</name>
  80         <extensionName>c:recordSelector</extensionName>
  81         <fieldType>ComponentInstance</fieldType>
  82         <inputParameters>
  83             <name>recordId</name>
  84             <value>
  85                 <elementReference>var_ParentRecordId</elementReference>
  86             </value>
  87         </inputParameters>
  88         <outputParameters>
  89             <assignToReference>var_SelectedRecordId</assignToReference>
  90             <name>selectedRecordId</name>
  91         </outputParameters>
  92     </fields>
  93 </screens>
  94 ```
  95 
  96 ### Variable Definitions
  97 
  98 ```xml
  99 <variables>
 100     <name>var_ParentRecordId</name>
 101     <dataType>String</dataType>
 102     <isCollection>false</isCollection>
 103     <isInput>true</isInput>
 104     <isOutput>false</isOutput>
 105 </variables>
 106 <variables>
 107     <name>var_SelectedRecordId</name>
 108     <dataType>String</dataType>
 109     <isCollection>false</isCollection>
 110     <isInput>false</isInput>
 111     <isOutput>true</isOutput>
 112 </variables>
 113 ```
 114 
 115 ---
 116 
 117 ## Pattern 2: Flow Calling Apex Invocable
 118 
 119 **Use Case**: Complex business logic, DML, or external integrations.
 120 
 121 ```
 122 ┌─────────┐   actionCalls    ┌─────────┐
 123 │  FLOW   │ ───────────────▶ │  APEX   │
 124 │         │   inputParams    │@Invocable│
 125 │         │ ◀─────────────── │ Method   │
 126 │         │   outputParams   │          │
 127 └─────────┘                  └─────────┘
 128 ```
 129 
 130 ### Flow XML
 131 
 132 ```xml
 133 <actionCalls>
 134     <name>Process_Records</name>
 135     <label>Process Records</label>
 136     <locationX>440</locationX>
 137     <locationY>518</locationY>
 138     <actionName>RecordProcessor</actionName>
 139     <actionType>apex</actionType>
 140     <connector>
 141         <targetReference>Show_Success</targetReference>
 142     </connector>
 143     <faultConnector>
 144         <targetReference>Handle_Error</targetReference>
 145     </faultConnector>
 146     <inputParameters>
 147         <name>recordId</name>
 148         <value>
 149             <elementReference>var_RecordId</elementReference>
 150         </value>
 151     </inputParameters>
 152     <inputParameters>
 153         <name>processType</name>
 154         <value>
 155             <stringValue>FULL</stringValue>
 156         </value>
 157     </inputParameters>
 158     <outputParameters>
 159         <assignToReference>var_IsSuccess</assignToReference>
 160         <name>isSuccess</name>
 161     </outputParameters>
 162     <outputParameters>
 163         <assignToReference>var_ProcessedId</assignToReference>
 164         <name>processedId</name>
 165     </outputParameters>
 166     <outputParameters>
 167         <assignToReference>var_ErrorMessage</assignToReference>
 168         <name>errorMessage</name>
 169     </outputParameters>
 170     <storeOutputAutomatically>false</storeOutputAutomatically>
 171 </actionCalls>
 172 ```
 173 
 174 ### Fault Handling
 175 
 176 ```xml
 177 <screens>
 178     <name>Handle_Error</name>
 179     <label>Error</label>
 180     <locationX>660</locationX>
 181     <locationY>638</locationY>
 182     <fields>
 183         <name>ErrorDisplay</name>
 184         <fieldText>&lt;p&gt;&lt;strong&gt;An error occurred:&lt;/strong&gt;&lt;/p&gt;&lt;p&gt;{!$Flow.FaultMessage}&lt;/p&gt;</fieldText>
 185         <fieldType>DisplayText</fieldType>
 186     </fields>
 187 </screens>
 188 ```
 189 
 190 ---
 191 
 192 ## Pattern 3: Full Triangle Flow
 193 
 194 **Use Case**: Complete solution combining LWC screens and Apex actions.
 195 
 196 ```xml
 197 <?xml version="1.0" encoding="UTF-8"?>
 198 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
 199     <apiVersion>65.0</apiVersion>
 200     <label>Quote Builder Flow</label>
 201     <processType>Flow</processType>
 202     <status>Active</status>
 203     <interviewLabel>Quote Builder {!$Flow.CurrentDateTime}</interviewLabel>
 204 
 205     <!-- Start -->
 206     <start>
 207         <locationX>50</locationX>
 208         <locationY>0</locationY>
 209         <connector>
 210             <targetReference>Select_Products_Screen</targetReference>
 211         </connector>
 212     </start>
 213 
 214     <!-- LWC Screen: Product Selection -->
 215     <screens>
 216         <name>Select_Products_Screen</name>
 217         <label>Select Products</label>
 218         <connector>
 219             <targetReference>Calculate_Pricing_Apex</targetReference>
 220         </connector>
 221         <fields>
 222             <name>productSelectorLWC</name>
 223             <extensionName>c:productSelector</extensionName>
 224             <fieldType>ComponentInstance</fieldType>
 225             <inputParameters>
 226                 <name>accountId</name>
 227                 <value><elementReference>var_AccountId</elementReference></value>
 228             </inputParameters>
 229             <outputParameters>
 230                 <assignToReference>var_SelectedProductIds</assignToReference>
 231                 <name>selectedProducts</name>
 232             </outputParameters>
 233         </fields>
 234     </screens>
 235 
 236     <!-- Apex Action: Calculate Pricing -->
 237     <actionCalls>
 238         <name>Calculate_Pricing_Apex</name>
 239         <actionName>PricingCalculator</actionName>
 240         <actionType>apex</actionType>
 241         <connector>
 242             <targetReference>Review_Quote_Screen</targetReference>
 243         </connector>
 244         <faultConnector>
 245             <targetReference>Pricing_Error_Screen</targetReference>
 246         </faultConnector>
 247         <inputParameters>
 248             <name>productIds</name>
 249             <value><elementReference>var_SelectedProductIds</elementReference></value>
 250         </inputParameters>
 251         <inputParameters>
 252             <name>accountId</name>
 253             <value><elementReference>var_AccountId</elementReference></value>
 254         </inputParameters>
 255         <outputParameters>
 256             <assignToReference>var_QuoteLineItems</assignToReference>
 257             <name>lineItems</name>
 258         </outputParameters>
 259         <outputParameters>
 260             <assignToReference>var_TotalPrice</assignToReference>
 261             <name>totalPrice</name>
 262         </outputParameters>
 263     </actionCalls>
 264 
 265     <!-- LWC Screen: Review Quote -->
 266     <screens>
 267         <name>Review_Quote_Screen</name>
 268         <label>Review Quote</label>
 269         <connector>
 270             <targetReference>Create_Quote_Record</targetReference>
 271         </connector>
 272         <fields>
 273             <name>quoteReviewLWC</name>
 274             <extensionName>c:quoteReview</extensionName>
 275             <fieldType>ComponentInstance</fieldType>
 276             <inputParameters>
 277                 <name>lineItems</name>
 278                 <value><elementReference>var_QuoteLineItems</elementReference></value>
 279             </inputParameters>
 280             <inputParameters>
 281                 <name>totalPrice</name>
 282                 <value><elementReference>var_TotalPrice</elementReference></value>
 283             </inputParameters>
 284             <outputParameters>
 285                 <assignToReference>var_ApprovedForSubmit</assignToReference>
 286                 <name>isApproved</name>
 287             </outputParameters>
 288         </fields>
 289     </screens>
 290 
 291     <!-- Variables -->
 292     <variables>
 293         <name>var_AccountId</name>
 294         <dataType>String</dataType>
 295         <isInput>true</isInput>
 296     </variables>
 297     <variables>
 298         <name>var_SelectedProductIds</name>
 299         <dataType>String</dataType>
 300         <isCollection>true</isCollection>
 301     </variables>
 302     <variables>
 303         <name>var_QuoteLineItems</name>
 304         <dataType>Apex</dataType>
 305         <apexClass>QuoteLineItemWrapper</apexClass>
 306         <isCollection>true</isCollection>
 307     </variables>
 308     <variables>
 309         <name>var_TotalPrice</name>
 310         <dataType>Currency</dataType>
 311     </variables>
 312 </Flow>
 313 ```
 314 
 315 ---
 316 
 317 ## Testing Flow with Apex
 318 
 319 ```apex
 320 @isTest
 321 private class QuoteBuilderFlowTest {
 322     @isTest
 323     static void testFlowWithApexIntegration() {
 324         // Setup test data
 325         Account acc = new Account(Name = 'Test Account');
 326         insert acc;
 327 
 328         Product2 prod = new Product2(Name = 'Test Product', IsActive = true);
 329         insert prod;
 330 
 331         // Flow inputs
 332         Map<String, Object> inputs = new Map<String, Object>{
 333             'var_AccountId' => acc.Id
 334         };
 335 
 336         Test.startTest();
 337         // Create and run Flow interview
 338         Flow.Interview flow = Flow.Interview.createInterview(
 339             'Quote_Builder_Flow',
 340             inputs
 341         );
 342         flow.start();
 343         Test.stopTest();
 344 
 345         // Verify Flow outputs
 346         Object totalPrice = flow.getVariableValue('var_TotalPrice');
 347         System.assertNotEquals(null, totalPrice, 'Total price should be calculated');
 348     }
 349 }
 350 ```
 351 
 352 ---
 353 
 354 ## Deployment Order
 355 
 356 When deploying integrated triangle solutions:
 357 
 358 ```
 359 1. APEX CLASSES
 360    └── @InvocableMethod classes
 361    └── @AuraEnabled controllers
 362 
 363 2. LWC COMPONENTS
 364    └── meta.xml with targets
 365    └── JavaScript with Flow imports
 366 
 367 3. FLOWS                ← Deploy LAST
 368    └── Reference deployed Apex classes
 369    └── Reference deployed LWC components
 370 ```
 371 
 372 ---
 373 
 374 ## Decision Matrix: When to Use Each Approach
 375 
 376 | Scenario | Primary | Supporting | Why |
 377 |----------|---------|------------|-----|
 378 | Simple record selection | LWC | - | Rich UI, immediate feedback |
 379 | Complex multi-step process | **Flow** | Apex, LWC | Orchestration strength |
 380 | Bulk data processing | Apex | - | Governor limit handling |
 381 | Custom UI in guided process | **Flow** | LWC | Best of both |
 382 | External API integration | Apex | Flow wrapper | Authentication, callouts |
 383 | Admin-maintainable logic | **Flow** | Apex for complex ops | Low-code primary |
 384 | User-facing wizard | **Flow** + LWC | Apex | Complete solution |
 385 
 386 ---
 387 
 388 ## Common Anti-Patterns
 389 
 390 | Anti-Pattern | Problem | Solution |
 391 |--------------|---------|----------|
 392 | No faultConnector on Apex actions | Unhandled exceptions crash Flow | Always add fault path |
 393 | Hardcoded IDs in Flow | Environment-specific failures | Use Custom Metadata or variables |
 394 | Missing outputParameters | Apex results not available | Map all needed outputs |
 395 | LWC without outputParameters | Component outputs ignored | Add outputParameters mapping |
 396 | Skipping validation before Apex | Invalid data causes errors | Add decision elements |
 397 
 398 ---
 399 
 400 ## Related Documentation
 401 
 402 | Topic | Location |
 403 |-------|----------|
 404 | Apex action template | `sf-flow/assets/apex-action-template.xml` |
 405 | Screen Flow with LWC | `sf-flow/assets/screen-flow-with-lwc.xml` |
 406 | LWC integration guide | `sf-flow/references/lwc-integration-guide.md` |
 407 | Apex triangle perspective | `sf-apex/references/triangle-pattern.md` |
 408 | LWC triangle perspective | `sf-lwc/references/triangle-pattern.md` |
