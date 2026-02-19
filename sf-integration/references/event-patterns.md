<!-- Parent: sf-integration/SKILL.md -->
   1 # Event-Driven Integration Patterns
   2 
   3 This document provides detailed implementation patterns for Platform Events and Change Data Capture (CDC) in Salesforce integrations.
   4 
   5 > **Parent Document**: [sf-integration/SKILL.md](../SKILL.md)
   6 > **Related**: [callout-patterns.md](./callout-patterns.md)
   7 
   8 ---
   9 
  10 ## Table of Contents
  11 
  12 - [Platform Events](#platform-events)
  13   - [Platform Event Definition](#platform-event-definition)
  14   - [Event Publisher](#event-publisher)
  15   - [Event Subscriber Trigger](#event-subscriber-trigger)
  16   - [High-Volume vs Standard-Volume Events](#high-volume-vs-standard-volume-events)
  17 - [Change Data Capture (CDC)](#change-data-capture-cdc)
  18   - [CDC Enablement](#cdc-enablement)
  19   - [CDC Subscriber Trigger](#cdc-subscriber-trigger)
  20   - [CDC Handler Service](#cdc-handler-service)
  21   - [Field-Specific Change Detection](#field-specific-change-detection)
  22 
  23 ---
  24 
  25 ## Platform Events
  26 
  27 Platform Events enable asynchronous, event-driven communication between applications. They provide a publish-subscribe model where publishers fire events and subscribers listen for them.
  28 
  29 ### Platform Event Definition
  30 
  31 **Use Case**: Asynchronous, event-driven communication
  32 
  33 **Template**: `assets/platform-events/platform-event-definition.object-meta.xml`
  34 
  35 #### Standard Volume Event
  36 
  37 Best for moderate event volumes (~2,000 events/hour):
  38 
  39 ```xml
  40 <?xml version="1.0" encoding="UTF-8"?>
  41 <CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  42     <deploymentStatus>Deployed</deploymentStatus>
  43     <eventType>StandardVolume</eventType>
  44     <label>{{EventLabel}}</label>
  45     <pluralLabel>{{EventPluralLabel}}</pluralLabel>
  46     <publishBehavior>PublishAfterCommit</publishBehavior>
  47 
  48     <fields>
  49         <fullName>{{FieldName}}__c</fullName>
  50         <label>{{FieldLabel}}</label>
  51         <type>Text</type>
  52         <length>255</length>
  53     </fields>
  54 
  55     <fields>
  56         <fullName>RecordId__c</fullName>
  57         <label>Record ID</label>
  58         <type>Text</type>
  59         <length>18</length>
  60         <description>Salesforce record ID related to this event</description>
  61     </fields>
  62 
  63     <fields>
  64         <fullName>Timestamp__c</fullName>
  65         <label>Timestamp</label>
  66         <type>DateTime</type>
  67         <description>When the event was triggered</description>
  68     </fields>
  69 </CustomObject>
  70 ```
  71 
  72 #### High-Volume Event
  73 
  74 Best for millions of events per day:
  75 
  76 ```xml
  77 <?xml version="1.0" encoding="UTF-8"?>
  78 <CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  79     <deploymentStatus>Deployed</deploymentStatus>
  80     <eventType>HighVolume</eventType>
  81     <label>{{EventLabel}}</label>
  82     <pluralLabel>{{EventPluralLabel}}</pluralLabel>
  83     <publishBehavior>PublishAfterCommit</publishBehavior>
  84 
  85     <fields>
  86         <fullName>{{FieldName}}__c</fullName>
  87         <label>{{FieldLabel}}</label>
  88         <type>Text</type>
  89         <length>255</length>
  90     </fields>
  91 </CustomObject>
  92 ```
  93 
  94 #### Key Configuration Options
  95 
  96 | Option | Values | Description |
  97 |--------|--------|-------------|
  98 | **eventType** | `StandardVolume`, `HighVolume` | Event throughput capacity |
  99 | **publishBehavior** | `PublishAfterCommit`, `PublishImmediately` | When events are published |
 100 | **deploymentStatus** | `Deployed`, `InDevelopment` | Deployment status |
 101 
 102 **PublishBehavior Details**:
 103 - `PublishAfterCommit`: Event published only if transaction commits (recommended)
 104 - `PublishImmediately`: Event published immediately, even if transaction rolls back
 105 
 106 ---
 107 
 108 ### Event Publisher
 109 
 110 **Template**: `assets/platform-events/event-publisher.cls`
 111 
 112 #### Bulk Event Publisher
 113 
 114 ```apex
 115 public with sharing class {{EventName}}Publisher {
 116 
 117     public static void publishEvents(List<{{EventName}}__e> events) {
 118         if (events == null || events.isEmpty()) {
 119             return;
 120         }
 121 
 122         List<Database.SaveResult> results = EventBus.publish(events);
 123 
 124         for (Integer i = 0; i < results.size(); i++) {
 125             Database.SaveResult sr = results[i];
 126             if (!sr.isSuccess()) {
 127                 for (Database.Error err : sr.getErrors()) {
 128                     System.debug(LoggingLevel.ERROR,
 129                         'Event publish error: ' + err.getStatusCode() + ' - ' + err.getMessage());
 130                 }
 131             }
 132         }
 133     }
 134 
 135     public static void publishSingleEvent(Map<String, Object> eventData) {
 136         {{EventName}}__e event = new {{EventName}}__e();
 137 
 138         // Map fields from eventData
 139         event.{{FieldName}}__c = (String) eventData.get('{{fieldKey}}');
 140         event.RecordId__c = (String) eventData.get('recordId');
 141         event.Timestamp__c = DateTime.now();
 142 
 143         Database.SaveResult sr = EventBus.publish(event);
 144         if (!sr.isSuccess()) {
 145             throw new EventPublishException('Failed to publish event: ' + sr.getErrors());
 146         }
 147     }
 148 
 149     public class EventPublishException extends Exception {}
 150 }
 151 ```
 152 
 153 #### Usage Examples
 154 
 155 **Single Event**:
 156 ```apex
 157 Map<String, Object> eventData = new Map<String, Object>{
 158     'recordId' => '001xx000003DXXXAAA',
 159     'status' => 'Completed',
 160     'amount' => 1000.00
 161 };
 162 OrderStatusPublisher.publishSingleEvent(eventData);
 163 ```
 164 
 165 **Bulk Events**:
 166 ```apex
 167 List<Order_Status__e> events = new List<Order_Status__e>();
 168 
 169 for (Order order : orders) {
 170     Order_Status__e event = new Order_Status__e();
 171     event.RecordId__c = order.Id;
 172     event.Status__c = order.Status;
 173     event.Timestamp__c = DateTime.now();
 174     events.add(event);
 175 }
 176 
 177 OrderStatusPublisher.publishEvents(events);
 178 ```
 179 
 180 #### Best Practices for Publishing
 181 
 182 1. **Batch Events**: Publish up to 2,000 events per transaction (governor limit)
 183 2. **Error Handling**: Always check `Database.SaveResult` for failures
 184 3. **Transaction Context**: Use `PublishAfterCommit` to ensure events only fire on successful transactions
 185 4. **Field Population**: Populate all required fields before publishing
 186 5. **Logging**: Log failed event publishes for debugging
 187 
 188 ---
 189 
 190 ### Event Subscriber Trigger
 191 
 192 **Template**: `assets/platform-events/event-subscriber-trigger.trigger`
 193 
 194 #### Standard Volume Subscriber
 195 
 196 ```apex
 197 trigger {{EventName}}Subscriber on {{EventName}}__e (after insert) {
 198     // Get replay ID for resumption
 199     String lastReplayId = '';
 200 
 201     for ({{EventName}}__e event : Trigger.new) {
 202         // Store replay ID for potential resume
 203         lastReplayId = event.ReplayId;
 204 
 205         try {
 206             // Process event
 207             {{EventName}}Handler.processEvent(event);
 208         } catch (Exception e) {
 209             // Log error but don't throw - allow other events to process
 210             System.debug(LoggingLevel.ERROR,
 211                 'Event processing error: ' + e.getMessage() +
 212                 ' ReplayId: ' + event.ReplayId);
 213         }
 214     }
 215 }
 216 ```
 217 
 218 #### High-Volume Subscriber (with Resume Checkpoint)
 219 
 220 ```apex
 221 trigger {{EventName}}Subscriber on {{EventName}}__e (after insert) {
 222     String lastReplayId = '';
 223 
 224     for ({{EventName}}__e event : Trigger.new) {
 225         lastReplayId = event.ReplayId;
 226 
 227         try {
 228             {{EventName}}Handler.processEvent(event);
 229         } catch (Exception e) {
 230             System.debug(LoggingLevel.ERROR,
 231                 'Event processing error: ' + e.getMessage() +
 232                 ' ReplayId: ' + event.ReplayId);
 233         }
 234     }
 235 
 236     // Set resume checkpoint for high-volume events
 237     // Allows resuming from this point if subscriber fails
 238     EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastReplayId);
 239 }
 240 ```
 241 
 242 #### Event Handler Class
 243 
 244 ```apex
 245 public with sharing class {{EventName}}Handler {
 246 
 247     public static void processEvent({{EventName}}__e event) {
 248         // Extract event data
 249         String recordId = event.RecordId__c;
 250         String status = event.Status__c;
 251         DateTime timestamp = event.Timestamp__c;
 252 
 253         System.debug('Processing event - RecordId: ' + recordId +
 254                      ', Status: ' + status +
 255                      ', ReplayId: ' + event.ReplayId);
 256 
 257         // Business logic
 258         updateRelatedRecords(recordId, status);
 259         syncToExternalSystem(recordId, status);
 260     }
 261 
 262     private static void updateRelatedRecords(String recordId, String status) {
 263         // Update related records based on event
 264         List<Task> tasks = [
 265             SELECT Id, Status
 266             FROM Task
 267             WHERE WhatId = :recordId
 268             WITH USER_MODE
 269         ];
 270 
 271         for (Task t : tasks) {
 272             t.Status = status;
 273         }
 274 
 275         update as user tasks;
 276     }
 277 
 278     private static void syncToExternalSystem(String recordId, String status) {
 279         // Queue async callout
 280         Map<String, Object> payload = new Map<String, Object>{
 281             'recordId' => recordId,
 282             'status' => status
 283         };
 284         System.enqueueJob(new ExternalSyncQueueable(payload));
 285     }
 286 }
 287 ```
 288 
 289 ---
 290 
 291 ### High-Volume vs Standard-Volume Events
 292 
 293 | Feature | Standard-Volume | High-Volume |
 294 |---------|----------------|-------------|
 295 | **Throughput** | ~2,000 events/hour | Millions/day |
 296 | **Delivery** | Exactly-once | At-least-once (may deliver duplicates) |
 297 | **Retention** | 3 days (72 hours) | 24 hours |
 298 | **Replay** | ReplayId from last 3 days | ReplayId from last 24 hours |
 299 | **Use Case** | Low-volume integrations, workflows | IoT, real-time analytics, high-traffic |
 300 | **Cost** | Included in platform | Additional licensing |
 301 
 302 #### When to Use High-Volume Events
 303 
 304 - **IoT Data**: Sensor data, device telemetry
 305 - **Real-Time Analytics**: Clickstream, user behavior tracking
 306 - **High-Traffic Systems**: E-commerce order processing, stock updates
 307 - **Event Sourcing**: Append-only event logs
 308 
 309 #### When to Use Standard-Volume Events
 310 
 311 - **Business Workflows**: Order status updates, approval processes
 312 - **Integration Events**: Sync to external CRM, ERP systems
 313 - **Notifications**: Email triggers, Slack notifications
 314 - **Audit Trails**: Record-level change notifications
 315 
 316 ---
 317 
 318 ## Change Data Capture (CDC)
 319 
 320 Change Data Capture publishes change events whenever records are created, updated, deleted, or undeleted in Salesforce. CDC events are published automatically—no custom code needed.
 321 
 322 ### CDC Enablement
 323 
 324 #### Enable via Setup UI
 325 
 326 1. Navigate to **Setup** → **Integrations** → **Change Data Capture**
 327 2. Select objects to enable (Standard or Custom)
 328 3. Save
 329 
 330 #### Enable via Metadata API
 331 
 332 **File**: `force-app/main/default/changeDataCaptures/AccountChangeEvent.cdc-meta.xml`
 333 
 334 ```xml
 335 <?xml version="1.0" encoding="UTF-8"?>
 336 <ChangeDataCapture xmlns="http://soap.sforce.com/2006/04/metadata">
 337     <entityName>Account</entityName>
 338     <isEnabled>true</isEnabled>
 339 </ChangeDataCapture>
 340 ```
 341 
 342 #### Channel Naming Convention
 343 
 344 CDC channels follow the pattern: `{{ObjectAPIName}}ChangeEvent`
 345 
 346 **Examples**:
 347 - `AccountChangeEvent` (Standard object)
 348 - `Order__ChangeEvent` (Custom object)
 349 - `OpportunityChangeEvent`
 350 - `Contact_Request__ChangeEvent`
 351 
 352 ---
 353 
 354 ### CDC Subscriber Trigger
 355 
 356 **Template**: `assets/cdc/cdc-subscriber-trigger.trigger`
 357 
 358 #### Basic CDC Subscriber
 359 
 360 ```apex
 361 trigger {{ObjectName}}CDCSubscriber on {{ObjectName}}ChangeEvent (after insert) {
 362 
 363     for ({{ObjectName}}ChangeEvent event : Trigger.new) {
 364         // Get change event header
 365         EventBus.ChangeEventHeader header = event.ChangeEventHeader;
 366 
 367         String changeType = header.getChangeType();
 368         List<String> changedFields = header.getChangedFields();
 369         String recordId = header.getRecordIds()[0]; // First record ID
 370 
 371         System.debug('CDC Event - Type: ' + changeType +
 372                      ', RecordId: ' + recordId +
 373                      ', Changed Fields: ' + changedFields);
 374 
 375         // Route based on change type
 376         switch on changeType {
 377             when 'CREATE' {
 378                 // Handle new record
 379                 {{ObjectName}}CDCHandler.handleCreate(event);
 380             }
 381             when 'UPDATE' {
 382                 // Handle update
 383                 {{ObjectName}}CDCHandler.handleUpdate(event, changedFields);
 384             }
 385             when 'DELETE' {
 386                 // Handle delete
 387                 {{ObjectName}}CDCHandler.handleDelete(recordId);
 388             }
 389             when 'UNDELETE' {
 390                 // Handle undelete
 391                 {{ObjectName}}CDCHandler.handleUndelete(event);
 392             }
 393         }
 394     }
 395 }
 396 ```
 397 
 398 #### ChangeEventHeader Fields
 399 
 400 | Field | Type | Description |
 401 |-------|------|-------------|
 402 | `getChangeType()` | String | CREATE, UPDATE, DELETE, UNDELETE |
 403 | `getRecordIds()` | List<String> | Record IDs affected (usually 1, up to 5 for related changes) |
 404 | `getChangedFields()` | List<String> | Field API names that changed (UPDATE only) |
 405 | `getCommitTimestamp()` | Long | Transaction commit timestamp |
 406 | `getCommitUser()` | String | User ID who made the change |
 407 | `getCommitNumber()` | Long | Monotonically increasing commit number |
 408 | `getEntityName()` | String | Object API name |
 409 
 410 ---
 411 
 412 ### CDC Handler Service
 413 
 414 **Template**: `assets/cdc/cdc-handler.cls`
 415 
 416 ```apex
 417 public with sharing class {{ObjectName}}CDCHandler {
 418 
 419     public static void handleCreate({{ObjectName}}ChangeEvent event) {
 420         // Sync to external system on create
 421         Map<String, Object> payload = buildPayload(event);
 422         System.enqueueJob(new ExternalSystemSyncQueueable(payload, 'CREATE'));
 423     }
 424 
 425     public static void handleUpdate({{ObjectName}}ChangeEvent event, List<String> changedFields) {
 426         // Only sync if relevant fields changed
 427         Set<String> fieldsToWatch = new Set<String>{'Name', 'Status__c', 'Amount__c'};
 428 
 429         Boolean relevantChange = false;
 430         for (String field : changedFields) {
 431             if (fieldsToWatch.contains(field)) {
 432                 relevantChange = true;
 433                 break;
 434             }
 435         }
 436 
 437         if (relevantChange) {
 438             Map<String, Object> payload = buildPayload(event);
 439             payload.put('changedFields', changedFields);
 440             System.enqueueJob(new ExternalSystemSyncQueueable(payload, 'UPDATE'));
 441         }
 442     }
 443 
 444     public static void handleDelete(String recordId) {
 445         Map<String, Object> payload = new Map<String, Object>{'recordId' => recordId};
 446         System.enqueueJob(new ExternalSystemSyncQueueable(payload, 'DELETE'));
 447     }
 448 
 449     public static void handleUndelete({{ObjectName}}ChangeEvent event) {
 450         handleCreate(event); // Treat undelete like create
 451     }
 452 
 453     private static Map<String, Object> buildPayload({{ObjectName}}ChangeEvent event) {
 454         return new Map<String, Object>{
 455             'recordId' => event.ChangeEventHeader.getRecordIds()[0],
 456             'commitTimestamp' => event.ChangeEventHeader.getCommitTimestamp(),
 457             'commitUser' => event.ChangeEventHeader.getCommitUser(),
 458             // Add event field values
 459             'name' => event.Name,
 460             'status' => event.Status__c
 461             // Add more fields
 462         };
 463     }
 464 }
 465 ```
 466 
 467 ---
 468 
 469 ### Field-Specific Change Detection
 470 
 471 #### Filtering by Changed Fields
 472 
 473 ```apex
 474 public static void handleUpdate(AccountChangeEvent event, List<String> changedFields) {
 475     // Only process if billing address changed
 476     Set<String> billingFields = new Set<String>{
 477         'BillingStreet',
 478         'BillingCity',
 479         'BillingState',
 480         'BillingPostalCode',
 481         'BillingCountry'
 482     };
 483 
 484     Boolean billingChanged = false;
 485     for (String field : changedFields) {
 486         if (billingFields.contains(field)) {
 487             billingChanged = true;
 488             break;
 489         }
 490     }
 491 
 492     if (billingChanged) {
 493         updateShippingPartner(event);
 494     }
 495 }
 496 ```
 497 
 498 #### Multi-Field Change Logic
 499 
 500 ```apex
 501 public static void handleUpdate(OpportunityChangeEvent event, List<String> changedFields) {
 502     Set<String> changedFieldSet = new Set<String>(changedFields);
 503 
 504     // Check if stage AND amount both changed
 505     if (changedFieldSet.contains('StageName') && changedFieldSet.contains('Amount')) {
 506         // Alert sales ops about significant deal change
 507         sendAlert('Deal stage and amount changed', event);
 508     }
 509 
 510     // Check if close date moved backward
 511     if (changedFieldSet.contains('CloseDate')) {
 512         checkCloseDateRegression(event);
 513     }
 514 }
 515 ```
 516 
 517 ---
 518 
 519 ## CDC vs Platform Events: When to Use Which
 520 
 521 | Use Case | Platform Events | Change Data Capture |
 522 |----------|----------------|---------------------|
 523 | **Custom business events** | **Preferred** | Not applicable |
 524 | **Record change notifications** | Requires custom trigger | **Automatic** (no code) |
 525 | **External system sync** | Both work | **CDC** (lower maintenance) |
 526 | **Custom event fields** | Fully customizable | Limited to object fields |
 527 | **Event filtering** | Filter in publisher code | Filter in subscriber code |
 528 | **Performance overhead** | Manual event creation | Automatic (minimal overhead) |
 529 
 530 ### Decision Matrix
 531 
 532 ```
 533 ┌───────────────────────────────────────────────────────────────────────┐
 534 │  WHEN TO USE PLATFORM EVENTS vs CHANGE DATA CAPTURE                   │
 535 ├───────────────────────────────────────────────────────────────────────┤
 536 │  Use PLATFORM EVENTS when:                                            │
 537 │  • Custom business event (not tied to record changes)                 │
 538 │  • Event needs custom fields not on object                            │
 539 │  • Need to batch/aggregate data before publishing                     │
 540 │  • Publishing from external system to Salesforce                      │
 541 │  • Complex event logic (multi-object aggregation)                     │
 542 │                                                                        │
 543 │  Use CHANGE DATA CAPTURE when:                                        │
 544 │  • Syncing record changes to external system                          │
 545 │  • Audit trail of all record modifications                            │
 546 │  • Real-time replication to data warehouse                            │
 547 │  • Event sourcing from Salesforce objects                             │
 548 │  • Zero-code event publishing required                                │
 549 └───────────────────────────────────────────────────────────────────────┘
 550 ```
 551 
 552 ---
 553 
 554 ## Advanced Patterns
 555 
 556 ### Combining CDC with Callouts
 557 
 558 ```apex
 559 public with sharing class AccountCDCHandler {
 560 
 561     public static void handleUpdate(AccountChangeEvent event, List<String> changedFields) {
 562         // Extract data
 563         String recordId = event.ChangeEventHeader.getRecordIds()[0];
 564         String accountName = event.Name;
 565 
 566         // Queue async callout to external CRM
 567         Map<String, Object> payload = new Map<String, Object>{
 568             'salesforceId' => recordId,
 569             'name' => accountName,
 570             'changedFields' => changedFields,
 571             'timestamp' => event.ChangeEventHeader.getCommitTimestamp()
 572         };
 573 
 574         System.enqueueJob(new CRMSyncQueueable(payload));
 575     }
 576 }
 577 ```
 578 
 579 ### Event Replay with Stored ReplayId
 580 
 581 ```apex
 582 public with sharing class EventReplayService {
 583 
 584     @future(callout=true)
 585     public static void replayFromLastCheckpoint(String eventChannel) {
 586         // Get last stored replay ID
 587         Event_Checkpoint__c checkpoint = [
 588             SELECT ReplayId__c
 589             FROM Event_Checkpoint__c
 590             WHERE Channel__c = :eventChannel
 591             LIMIT 1
 592         ];
 593 
 594         if (checkpoint != null) {
 595             // Use stored replay ID to resume from last successful event
 596             // Note: Replay is typically done via API/streaming API, not Apex
 597             System.debug('Last replay ID: ' + checkpoint.ReplayId__c);
 598         }
 599     }
 600 
 601     public static void storeCheckpoint(String channel, String replayId) {
 602         Event_Checkpoint__c checkpoint = new Event_Checkpoint__c(
 603             Channel__c = channel,
 604             ReplayId__c = replayId,
 605             Last_Updated__c = DateTime.now()
 606         );
 607         upsert checkpoint Channel__c;
 608     }
 609 }
 610 ```
 611 
 612 ### Error Handling with Dead Letter Queue
 613 
 614 ```apex
 615 trigger OrderEventSubscriber on Order_Status__e (after insert) {
 616     for (Order_Status__e event : Trigger.new) {
 617         try {
 618             OrderEventHandler.processEvent(event);
 619         } catch (Exception e) {
 620             // Log to dead letter queue for manual review
 621             Event_Error_Log__c errorLog = new Event_Error_Log__c(
 622                 Event_Type__c = 'Order_Status__e',
 623                 Replay_Id__c = event.ReplayId,
 624                 Error_Message__c = e.getMessage(),
 625                 Event_Payload__c = JSON.serialize(event),
 626                 Occurred_At__c = DateTime.now()
 627             );
 628             insert as user errorLog;
 629         }
 630     }
 631 }
 632 ```
 633 
 634 ---
 635 
 636 ## Best Practices
 637 
 638 ### Platform Events
 639 
 640 1. **Batch Publishing**: Publish events in batches (up to 2,000 per transaction)
 641 2. **Idempotent Subscribers**: Design subscribers to handle duplicate events (especially for high-volume)
 642 3. **ReplayId Tracking**: Store ReplayIds for resume capability
 643 4. **Error Isolation**: Catch exceptions in subscriber loops to process remaining events
 644 5. **Resume Checkpoints**: Use `setResumeCheckpoint()` for high-volume events
 645 
 646 ### Change Data Capture
 647 
 648 1. **Field Filtering**: Only process relevant field changes to reduce processing overhead
 649 2. **Async Processing**: Use Queueable/Future for callouts or long-running operations
 650 3. **ChangeType Routing**: Use switch statements for different change types
 651 4. **RecordIds Array**: Handle multiple RecordIds (CDC can batch related changes)
 652 5. **Commit Metadata**: Use `getCommitTimestamp()` and `getCommitUser()` for audit trails
 653 
 654 ---
 655 
 656 ## Governor Limits
 657 
 658 | Limit | Value | Notes |
 659 |-------|-------|-------|
 660 | Platform Events published/transaction | 2,000 | Both Standard and High-Volume |
 661 | Platform Event delivery | Asynchronous | Delivered to subscribers after commit |
 662 | CDC events/hour (per object) | 250,000 | Auto-throttled if exceeded |
 663 | Event message size | 1 MB | Total size of all fields |
 664 | Event retention (Standard) | 3 days | ReplayId available for 72 hours |
 665 | Event retention (High-Volume) | 24 hours | ReplayId available for 24 hours |
 666 
 667 ---
 668 
 669 ## Testing Event-Driven Integrations
 670 
 671 ### Platform Event Test
 672 
 673 ```apex
 674 @isTest
 675 private class OrderEventTest {
 676 
 677     @isTest
 678     static void testEventPublish() {
 679         Test.startTest();
 680 
 681         Order_Status__e event = new Order_Status__e(
 682             RecordId__c = '006xx000000XXXAAA',
 683             Status__c = 'Completed'
 684         );
 685         Database.SaveResult sr = EventBus.publish(event);
 686 
 687         Test.stopTest();
 688 
 689         System.assert(sr.isSuccess(), 'Event should publish successfully');
 690     }
 691 
 692     @isTest
 693     static void testEventSubscriber() {
 694         // Subscriber triggers execute synchronously in tests
 695         Test.startTest();
 696 
 697         Order_Status__e event = new Order_Status__e(
 698             RecordId__c = '006xx000000XXXAAA',
 699             Status__c = 'Completed'
 700         );
 701         EventBus.publish(event);
 702 
 703         Test.stopTest();
 704 
 705         // Verify subscriber logic executed
 706         // (check that handler updated related records)
 707     }
 708 }
 709 ```
 710 
 711 ### CDC Test
 712 
 713 ```apex
 714 @isTest
 715 private class AccountCDCTest {
 716 
 717     @isTest
 718     static void testAccountUpdate() {
 719         Account acc = new Account(Name = 'Test Account');
 720         insert acc;
 721 
 722         Test.startTest();
 723 
 724         acc.BillingCity = 'San Francisco';
 725         update acc;
 726 
 727         Test.stopTest();
 728 
 729         // CDC events don't fire in test context
 730         // Must test handler methods directly
 731         AccountChangeEvent mockEvent = new AccountChangeEvent();
 732         // Note: Can't instantiate ChangeEvent in Apex
 733         // Test handler logic with mock data instead
 734     }
 735 }
 736 ```
 737 
 738 ---
 739 
 740 ## Related Resources
 741 
 742 - [Callout Patterns](./callout-patterns.md) - REST and SOAP callout implementations
 743 - [Main Skill Documentation](../SKILL.md) - sf-integration overview
 744 - [Platform Event Templates](../assets/platform-events/) - Event definitions and triggers
 745 - [CDC Templates](../assets/cdc/) - Change Data Capture triggers
