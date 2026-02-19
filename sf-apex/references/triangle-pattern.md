<!-- Parent: sf-apex/SKILL.md -->
   1 # Flow-LWC-Apex Triangle: Apex Perspective
   2 
   3 The **Triangle Architecture** is a foundational Salesforce pattern where Flow, LWC, and Apex work together. This guide focuses on the **Apex role** in this architecture.
   4 
   5 ---
   6 
   7 ## Architecture Overview
   8 
   9 ```
  10                          ┌─────────────────────────────────────┐
  11                          │              FLOW                   │
  12                          │         (Orchestrator)              │
  13                          └───────────────┬─────────────────────┘
  14                                          │
  15               ┌──────────────────────────┼──────────────────────────┐
  16               │                          │                          │
  17               │ screens                  │ actionCalls              │
  18               │ <componentInstance>      │ actionType="apex"        │
  19               │                          │                          │
  20               ▼                          ▼                          ▲
  21 ┌─────────────────────────┐    ┌─────────────────────────┐         │
  22 │          LWC            │    │         APEX            │         │
  23 │     (UI Component)      │───▶│   (Business Logic)      │─────────┘
  24 │                         │    │                         │
  25 │ • Rich UI/UX            │    │ • @InvocableMethod  ◀── YOU ARE HERE
  26 │ • User Interaction      │    │ • @AuraEnabled          │
  27 │                         │    │ • Complex Logic         │
  28 │                         │    │ • DML Operations        │
  29 │                         │    │ • Integration           │
  30 └─────────────────────────┘    └─────────────────────────┘
  31               │                          ▲
  32               │      @AuraEnabled        │
  33               │      wire / imperative   │
  34               └──────────────────────────┘
  35 ```
  36 
  37 ---
  38 
  39 ## Apex's Role in the Triangle
  40 
  41 | Communication Path | Apex Annotation | Direction |
  42 |-------------------|-----------------|-----------|
  43 | Flow → Apex | `@InvocableMethod` | Request/Response |
  44 | Apex → Flow | `@InvocableVariable` | Return values |
  45 | LWC → Apex | `@AuraEnabled` | Async call |
  46 | Apex → LWC | Return value | Response |
  47 
  48 ---
  49 
  50 ## Pattern 1: @InvocableMethod for Flow
  51 
  52 **Use Case**: Complex business logic, DML, or external integrations called from Flow.
  53 
  54 ```
  55 ┌─────────┐   actionCalls    ┌─────────┐
  56 │  FLOW   │ ───────────────▶ │  APEX   │
  57 │ Auto-   │   List<Request>  │Invocable│
  58 │ mation  │ ◀─────────────── │ Method  │
  59 │         │   List<Response> │         │
  60 └─────────┘                  └─────────┘
  61 ```
  62 
  63 ### Apex Class Pattern
  64 
  65 ```apex
  66 public with sharing class RecordProcessor {
  67 
  68     @InvocableMethod(label='Process Record' category='Custom')
  69     public static List<Response> execute(List<Request> requests) {
  70         List<Response> responses = new List<Response>();
  71 
  72         for (Request req : requests) {
  73             Response res = new Response();
  74             try {
  75                 // Business logic here
  76                 res.isSuccess = true;
  77                 res.processedId = req.recordId;
  78             } catch (Exception e) {
  79                 res.isSuccess = false;
  80                 res.errorMessage = e.getMessage();
  81             }
  82             responses.add(res);
  83         }
  84         return responses;
  85     }
  86 
  87     public class Request {
  88         @InvocableVariable(required=true)
  89         public Id recordId;
  90     }
  91 
  92     public class Response {
  93         @InvocableVariable
  94         public Boolean isSuccess;
  95         @InvocableVariable
  96         public Id processedId;
  97         @InvocableVariable
  98         public String errorMessage;
  99     }
 100 }
 101 ```
 102 
 103 ### Corresponding Flow XML
 104 
 105 ```xml
 106 <actionCalls>
 107     <name>Process_Records</name>
 108     <actionName>RecordProcessor</actionName>
 109     <actionType>apex</actionType>
 110     <inputParameters>
 111         <name>recordId</name>
 112         <value><elementReference>var_RecordId</elementReference></value>
 113     </inputParameters>
 114     <outputParameters>
 115         <assignToReference>var_IsSuccess</assignToReference>
 116         <name>isSuccess</name>
 117     </outputParameters>
 118     <faultConnector>
 119         <targetReference>Handle_Error</targetReference>
 120     </faultConnector>
 121 </actionCalls>
 122 ```
 123 
 124 ---
 125 
 126 ## Pattern 2: @AuraEnabled for LWC
 127 
 128 **Use Case**: LWC needs data or operations beyond Flow context.
 129 
 130 ```
 131 ┌─────────┐     @wire         ┌─────────┐
 132 │   LWC   │ ────────────────▶ │  APEX   │
 133 │         │    imperative     │@Aura    │
 134 │         │ ◀──────────────── │Enabled  │
 135 │         │   Promise/data    │         │
 136 └─────────┘                   └─────────┘
 137 ```
 138 
 139 ### Apex Controller
 140 
 141 ```apex
 142 public with sharing class RecordController {
 143 
 144     @AuraEnabled(cacheable=true)
 145     public static List<Record__c> getRecords(Id parentId) {
 146         return [
 147             SELECT Id, Name, Status__c
 148             FROM Record__c
 149             WHERE Parent__c = :parentId
 150             WITH USER_MODE
 151         ];
 152     }
 153 
 154     @AuraEnabled
 155     public static Map<String, Object> processRecord(Id recordId) {
 156         // Process logic (DML operations)
 157         return new Map<String, Object>{
 158             'isSuccess' => true,
 159             'recordId' => recordId
 160         };
 161     }
 162 }
 163 ```
 164 
 165 ### Key Differences
 166 
 167 | Annotation | Cacheable | Use For |
 168 |------------|-----------|---------|
 169 | `@AuraEnabled(cacheable=true)` | Yes | Read-only queries (SOQL) |
 170 | `@AuraEnabled` | No | DML operations, mutations |
 171 
 172 ---
 173 
 174 ## Testing @InvocableMethod
 175 
 176 ```apex
 177 @isTest
 178 private class RecordProcessorTest {
 179     @isTest
 180     static void testProcessRecords() {
 181         Account acc = new Account(Name = 'Test');
 182         insert acc;
 183 
 184         RecordProcessor.Request req = new RecordProcessor.Request();
 185         req.recordId = acc.Id;
 186 
 187         Test.startTest();
 188         List<RecordProcessor.Response> responses =
 189             RecordProcessor.execute(new List<RecordProcessor.Request>{ req });
 190         Test.stopTest();
 191 
 192         System.assertEquals(true, responses[0].isSuccess);
 193         System.assertEquals(acc.Id, responses[0].processedId);
 194     }
 195 
 196     @isTest
 197     static void testBulkProcessing() {
 198         // Test with 200+ records for bulkification
 199         List<Account> accounts = new List<Account>();
 200         for (Integer i = 0; i < 251; i++) {
 201             accounts.add(new Account(Name = 'Test ' + i));
 202         }
 203         insert accounts;
 204 
 205         List<RecordProcessor.Request> requests = new List<RecordProcessor.Request>();
 206         for (Account acc : accounts) {
 207             RecordProcessor.Request req = new RecordProcessor.Request();
 208             req.recordId = acc.Id;
 209             requests.add(req);
 210         }
 211 
 212         Test.startTest();
 213         List<RecordProcessor.Response> responses = RecordProcessor.execute(requests);
 214         Test.stopTest();
 215 
 216         System.assertEquals(251, responses.size());
 217     }
 218 }
 219 ```
 220 
 221 ---
 222 
 223 ## Deployment Order
 224 
 225 When deploying integrated triangle solutions:
 226 
 227 ```
 228 1. APEX CLASSES         ← Deploy FIRST
 229    └── @InvocableMethod classes
 230    └── @AuraEnabled controllers
 231 
 232 2. LWC COMPONENTS
 233    └── Depend on Apex controllers
 234 
 235 3. FLOWS
 236    └── Reference deployed Apex classes
 237    └── Reference deployed LWC components
 238 ```
 239 
 240 ---
 241 
 242 ## Common Anti-Patterns
 243 
 244 | Anti-Pattern | Problem | Solution |
 245 |--------------|---------|----------|
 246 | Non-bulkified Invocable | Fails for multi-record Flows | Use `List<Request>` → `List<Response>` |
 247 | Missing faultConnector handling | Exceptions crash Flow | Return error in Response, add fault path |
 248 | Cacheable method with DML | Runtime error | Remove `cacheable=true` for mutations |
 249 | Mixing concerns | Hard to test | Separate controller (LWC) from service (Flow) classes |
 250 
 251 ---
 252 
 253 ## Decision Matrix
 254 
 255 | Scenario | Use @InvocableMethod | Use @AuraEnabled |
 256 |----------|---------------------|------------------|
 257 | Called from Flow | ✅ | ❌ |
 258 | Called from LWC | ❌ | ✅ |
 259 | Needs bulkification | ✅ (always bulk) | Optional |
 260 | Read-only query | Either | ✅ (cacheable) |
 261 | DML operations | ✅ | ✅ |
 262 | External callout | ✅ | ✅ |
 263 
 264 ---
 265 
 266 ## Related Documentation
 267 
 268 | Topic | Location |
 269 |-------|----------|
 270 | @InvocableMethod templates | `sf-apex/assets/invocable-method.cls` |
 271 | Flow integration guide | `sf-apex/references/flow-integration.md` |
 272 | LWC triangle perspective | `sf-lwc/references/triangle-pattern.md` |
 273 | Flow triangle perspective | `sf-flow/references/triangle-pattern.md` |
