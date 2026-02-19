<!-- Parent: sf-apex/SKILL.md -->
   1 # Trigger Actions Framework (TAF) Guide
   2 
   3 ## Overview
   4 
   5 The Trigger Actions Framework provides a metadata-driven approach to trigger management, enabling:
   6 - One trigger per object
   7 - Ordered execution of actions
   8 - Bypass mechanisms (global, transaction, permission-based)
   9 - Support for both Apex and Flow actions
  10 
  11 ## Installation
  12 
  13 Install from: https://github.com/mitchspano/trigger-actions-framework
  14 
  15 ## Basic Setup
  16 
  17 ### 1. Create the Trigger
  18 
  19 One trigger per object, delegating all logic to the framework:
  20 
  21 ```apex
  22 trigger AccountTrigger on Account (
  23     before insert, after insert,
  24     before update, after update,
  25     before delete, after delete,
  26     after undelete
  27 ) {
  28     new MetadataTriggerHandler().run();
  29 }
  30 ```
  31 
  32 ### 2. Enable the Object
  33 
  34 Create an `sObject_Trigger_Setting__mdt` record:
  35 - Label: Account Trigger Setting
  36 - Object API Name: Account
  37 - Bypass Execution: unchecked
  38 
  39 ### 3. Create Action Classes
  40 
  41 Each action class handles one specific behavior:
  42 
  43 ```apex
  44 public class TA_Account_SetDefaults implements TriggerAction.BeforeInsert {
  45     public void beforeInsert(List<Account> newList) {
  46         for (Account acc : newList) {
  47             if (acc.Industry == null) {
  48                 acc.Industry = 'Other';
  49             }
  50         }
  51     }
  52 }
  53 ```
  54 
  55 ### 4. Register the Action
  56 
  57 Create a `Trigger_Action__mdt` record:
  58 - Object: Account
  59 - Apex Class Name: TA_Account_SetDefaults
  60 - Order: 1
  61 - Before Insert: checked
  62 
  63 ---
  64 
  65 ## Action Interfaces
  66 
  67 ### Before Triggers
  68 
  69 ```apex
  70 // Before Insert
  71 public class MyAction implements TriggerAction.BeforeInsert {
  72     public void beforeInsert(List<SObject> newList) { }
  73 }
  74 
  75 // Before Update
  76 public class MyAction implements TriggerAction.BeforeUpdate {
  77     public void beforeUpdate(List<SObject> newList, List<SObject> oldList) { }
  78 }
  79 
  80 // Before Delete
  81 public class MyAction implements TriggerAction.BeforeDelete {
  82     public void beforeDelete(List<SObject> oldList) { }
  83 }
  84 ```
  85 
  86 ### After Triggers
  87 
  88 ```apex
  89 // After Insert
  90 public class MyAction implements TriggerAction.AfterInsert {
  91     public void afterInsert(List<SObject> newList) { }
  92 }
  93 
  94 // After Update
  95 public class MyAction implements TriggerAction.AfterUpdate {
  96     public void afterUpdate(List<SObject> newList, List<SObject> oldList) { }
  97 }
  98 
  99 // After Delete
 100 public class MyAction implements TriggerAction.AfterDelete {
 101     public void afterDelete(List<SObject> oldList) { }
 102 }
 103 
 104 // After Undelete
 105 public class MyAction implements TriggerAction.AfterUndelete {
 106     public void afterUndelete(List<SObject> newList) { }
 107 }
 108 ```
 109 
 110 ---
 111 
 112 ## Common Patterns
 113 
 114 ### Setting Default Values (Before Insert)
 115 
 116 ```apex
 117 public class TA_Account_SetDefaults implements TriggerAction.BeforeInsert {
 118     public void beforeInsert(List<Account> newList) {
 119         for (Account acc : newList) {
 120             acc.Industry = acc.Industry ?? 'Other';
 121             acc.NumberOfEmployees = acc.NumberOfEmployees ?? 0;
 122         }
 123     }
 124 }
 125 ```
 126 
 127 ### Validation (Before Insert/Update)
 128 
 129 ```apex
 130 public class TA_Account_ValidateData implements TriggerAction.BeforeInsert, TriggerAction.BeforeUpdate {
 131 
 132     public void beforeInsert(List<Account> newList) {
 133         validate(newList);
 134     }
 135 
 136     public void beforeUpdate(List<Account> newList, List<Account> oldList) {
 137         validate(newList);
 138     }
 139 
 140     private void validate(List<Account> accounts) {
 141         for (Account acc : accounts) {
 142             if (acc.AnnualRevenue != null && acc.AnnualRevenue < 0) {
 143                 acc.AnnualRevenue.addError('Annual Revenue cannot be negative');
 144             }
 145         }
 146     }
 147 }
 148 ```
 149 
 150 ### Related Record Updates (After Insert/Update)
 151 
 152 ```apex
 153 public class TA_Account_UpdateContacts implements TriggerAction.AfterUpdate {
 154 
 155     public void afterUpdate(List<Account> newList, List<Account> oldList) {
 156         Map<Id, Account> oldMap = new Map<Id, Account>(oldList);
 157         Set<Id> changedAccountIds = new Set<Id>();
 158 
 159         for (Account acc : newList) {
 160             Account oldAcc = oldMap.get(acc.Id);
 161             if (acc.BillingCity != oldAcc.BillingCity) {
 162                 changedAccountIds.add(acc.Id);
 163             }
 164         }
 165 
 166         if (!changedAccountIds.isEmpty()) {
 167             updateContactAddresses(changedAccountIds);
 168         }
 169     }
 170 
 171     private void updateContactAddresses(Set<Id> accountIds) {
 172         List<Contact> contacts = [
 173             SELECT Id, AccountId, MailingCity
 174             FROM Contact
 175             WHERE AccountId IN :accountIds
 176             WITH USER_MODE
 177         ];
 178 
 179         Map<Id, Account> accounts = new Map<Id, Account>([
 180             SELECT Id, BillingCity
 181             FROM Account
 182             WHERE Id IN :accountIds
 183             WITH USER_MODE
 184         ]);
 185 
 186         for (Contact con : contacts) {
 187             con.MailingCity = accounts.get(con.AccountId).BillingCity;
 188         }
 189 
 190         update contacts;
 191     }
 192 }
 193 ```
 194 
 195 ### Async Processing (After Insert/Update)
 196 
 197 ```apex
 198 public class TA_Account_ProcessAsync implements TriggerAction.AfterInsert {
 199 
 200     public void afterInsert(List<Account> newList) {
 201         Set<Id> accountIds = new Map<Id, Account>(newList).keySet();
 202         System.enqueueJob(new AccountProcessingQueueable(accountIds));
 203     }
 204 }
 205 ```
 206 
 207 ---
 208 
 209 ## Bypass Mechanisms
 210 
 211 ### Global Bypass (Metadata)
 212 
 213 In `sObject_Trigger_Setting__mdt`:
 214 - Set `Bypass_Execution__c = true` to disable all triggers for object
 215 
 216 ### Transaction Bypass (Apex)
 217 
 218 ```apex
 219 // Bypass specific object
 220 TriggerBase.bypass(Account.SObjectType);
 221 
 222 // Bypass specific action
 223 MetadataTriggerHandler.bypass('TA_Account_SetDefaults');
 224 
 225 // Clear bypasses
 226 TriggerBase.clearAllBypasses();
 227 MetadataTriggerHandler.clearAllBypasses();
 228 ```
 229 
 230 ### Permission-Based Bypass
 231 
 232 In `Trigger_Action__mdt`:
 233 - `Bypass_Permission__c`: Users with this permission skip the action
 234 - `Required_Permission__c`: Only users with this permission run the action
 235 
 236 ---
 237 
 238 ## Recursion Prevention
 239 
 240 ### Using TriggerBase
 241 
 242 ```apex
 243 public class TA_Account_PreventRecursion implements TriggerAction.AfterUpdate {
 244 
 245     public void afterUpdate(List<Account> newList, List<Account> oldList) {
 246         List<Account> toProcess = new List<Account>();
 247 
 248         for (Account acc : newList) {
 249             // Check if already processed in this transaction
 250             if (!TriggerBase.idToNumberOfTimesSeenAfterUpdate.get(acc.Id).equals(1)) {
 251                 continue;
 252             }
 253             toProcess.add(acc);
 254         }
 255 
 256         if (!toProcess.isEmpty()) {
 257             processAccounts(toProcess);
 258         }
 259     }
 260 }
 261 ```
 262 
 263 ---
 264 
 265 ## Flow Actions
 266 
 267 ### Setup
 268 
 269 1. Create an Autolaunched Flow
 270 2. Add variables:
 271    - `record` (Input, Record type)
 272    - `recordPrior` (Input, Record type, for Update triggers)
 273 
 274 3. Create `Trigger_Action__mdt`:
 275    - Apex Class Name: `TriggerActionFlow`
 276    - Flow Name: `Your_Flow_API_Name`
 277 
 278 ### Entry Criteria
 279 
 280 Define formula criteria to control when the flow executes:
 281 ```
 282 {!record.Status__c} = 'Submitted' && {!recordPrior.Status__c} != 'Submitted'
 283 ```
 284 
 285 ---
 286 
 287 ## Testing
 288 
 289 ### Test Action Classes
 290 
 291 ```apex
 292 @isTest
 293 private class TA_Account_SetDefaultsTest {
 294 
 295     @isTest
 296     static void testBeforeInsert() {
 297         Account acc = new Account(Name = 'Test');
 298 
 299         Test.startTest();
 300         insert acc;
 301         Test.stopTest();
 302 
 303         Account result = [SELECT Industry FROM Account WHERE Id = :acc.Id];
 304         Assert.areEqual('Other', result.Industry, 'Default industry should be set');
 305     }
 306 
 307     @isTest
 308     static void testBulkInsert() {
 309         List<Account> accounts = new List<Account>();
 310         for (Integer i = 0; i < 251; i++) {
 311             accounts.add(new Account(Name = 'Test ' + i));
 312         }
 313 
 314         Test.startTest();
 315         insert accounts;
 316         Test.stopTest();
 317 
 318         List<Account> results = [SELECT Industry FROM Account WHERE Id IN :accounts];
 319         for (Account acc : results) {
 320             Assert.areEqual('Other', acc.Industry);
 321         }
 322     }
 323 }
 324 ```
 325 
 326 ### Test with Bypass
 327 
 328 ```apex
 329 @isTest
 330 static void testWithBypass() {
 331     // Bypass the action
 332     MetadataTriggerHandler.bypass('TA_Account_SetDefaults');
 333 
 334     Account acc = new Account(Name = 'Test');
 335     insert acc;
 336 
 337     Account result = [SELECT Industry FROM Account WHERE Id = :acc.Id];
 338     Assert.isNull(result.Industry, 'Industry should not be set when bypassed');
 339 
 340     // Clear bypass for other tests
 341     MetadataTriggerHandler.clearBypass('TA_Account_SetDefaults');
 342 }
 343 ```
 344 
 345 ---
 346 
 347 ## Naming Convention
 348 
 349 ```
 350 TA_[ObjectName]_[ActionDescription]
 351 
 352 Examples:
 353 - TA_Account_SetDefaults
 354 - TA_Account_ValidateData
 355 - TA_Contact_UpdateAccountRollup
 356 - TA_Opportunity_SendNotification
 357 ```
 358 
 359 ---
 360 
 361 ## Execution Order
 362 
 363 Actions execute in the order defined by the `Order__c` field in `Trigger_Action__mdt`.
 364 
 365 Recommended ordering:
 366 1. Validation (10-20)
 367 2. Default values (30-40)
 368 3. Field calculations (50-60)
 369 4. Related record queries (70-80)
 370 5. Related record updates (90-100)
 371 6. Async/external calls (110+)
