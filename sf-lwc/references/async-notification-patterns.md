<!-- Parent: sf-lwc/SKILL.md -->
   1 # Async Notification Patterns in LWC
   2 
   3 This guide covers real-time notification patterns for Lightning Web Components using Platform Events, Change Data Capture, and the Emp API.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────────┐
  11 │                    ASYNC NOTIFICATION ARCHITECTURE                       │
  12 ├─────────────────────────────────────────────────────────────────────────┤
  13 │                                                                          │
  14 │   ┌──────────────┐        Platform Events        ┌──────────────┐       │
  15 │   │    Apex      │ ─────────────────────────────▶│     LWC      │       │
  16 │   │  Queueable   │    /event/My_Event__e         │  empApi      │       │
  17 │   └──────────────┘                               └──────────────┘       │
  18 │                                                                          │
  19 │   ┌──────────────┐        Change Data Capture    ┌──────────────┐       │
  20 │   │    DML       │ ─────────────────────────────▶│     LWC      │       │
  21 │   │  Operation   │    /data/AccountChangeEvent   │  empApi      │       │
  22 │   └──────────────┘                               └──────────────┘       │
  23 │                                                                          │
  24 │   Use Cases:                                                             │
  25 │   • Queueable/Batch job completion notification                          │
  26 │   • Real-time record updates across users                                │
  27 │   • External system webhook processing notification                      │
  28 │   • Background AI generation completion                                  │
  29 │                                                                          │
  30 └─────────────────────────────────────────────────────────────────────────┘
  31 ```
  32 
  33 ---
  34 
  35 ## Emp API Basics
  36 
  37 The `lightning/empApi` module enables LWC to subscribe to Streaming API channels.
  38 
  39 ### Import and Setup
  40 
  41 ```javascript
  42 import { LightningElement } from 'lwc';
  43 import { subscribe, unsubscribe, onError, setDebugFlag } from 'lightning/empApi';
  44 
  45 export default class NotificationListener extends LightningElement {
  46     subscription = null;
  47     channelName = '/event/Job_Complete__e';
  48 
  49     connectedCallback() {
  50         // Enable debug logging (development only)
  51         setDebugFlag(true);
  52 
  53         // Register global error handler
  54         this.registerErrorListener();
  55 
  56         // Subscribe to channel
  57         this.handleSubscribe();
  58     }
  59 
  60     disconnectedCallback() {
  61         // CRITICAL: Always unsubscribe to prevent memory leaks
  62         this.handleUnsubscribe();
  63     }
  64 }
  65 ```
  66 
  67 ### Subscribe to Platform Events
  68 
  69 ```javascript
  70 async handleSubscribe() {
  71     // Callback invoked when event received
  72     const messageCallback = (response) => {
  73         console.log('Event received:', JSON.stringify(response));
  74         this.handleEvent(response.data.payload);
  75     };
  76 
  77     try {
  78         // Subscribe and store reference
  79         this.subscription = await subscribe(
  80             this.channelName,
  81             -1,  // -1 = all new events, -2 = replay last 24h
  82             messageCallback
  83         );
  84         console.log('Subscribed to:', JSON.stringify(this.subscription));
  85     } catch (error) {
  86         console.error('Subscribe error:', error);
  87     }
  88 }
  89 
  90 handleUnsubscribe() {
  91     if (this.subscription) {
  92         unsubscribe(this.subscription, (response) => {
  93             console.log('Unsubscribed:', JSON.stringify(response));
  94         });
  95     }
  96 }
  97 
  98 registerErrorListener() {
  99     onError((error) => {
 100         console.error('Streaming API error:', JSON.stringify(error));
 101         // Attempt reconnection after delay
 102         setTimeout(() => this.handleSubscribe(), 5000);
 103     });
 104 }
 105 ```
 106 
 107 ---
 108 
 109 ## Pattern 1: Queueable Job Completion
 110 
 111 Notify users when async Apex processing completes.
 112 
 113 ### Platform Event Definition
 114 
 115 ```xml
 116 <!-- force-app/main/default/objects/Job_Complete__e/Job_Complete__e.object-meta.xml -->
 117 <?xml version="1.0" encoding="UTF-8"?>
 118 <CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
 119     <deploymentStatus>Deployed</deploymentStatus>
 120     <eventType>StandardVolume</eventType>
 121     <label>Job Complete</label>
 122     <pluralLabel>Job Complete Events</pluralLabel>
 123     <publishBehavior>PublishAfterCommit</publishBehavior>
 124     <fields>
 125         <fullName>Job_Id__c</fullName>
 126         <label>Job ID</label>
 127         <type>Text</type>
 128         <length>50</length>
 129     </fields>
 130     <fields>
 131         <fullName>User_Id__c</fullName>
 132         <label>User ID</label>
 133         <type>Text</type>
 134         <length>18</length>
 135     </fields>
 136     <fields>
 137         <fullName>Status__c</fullName>
 138         <label>Status</label>
 139         <type>Text</type>
 140         <length>20</length>
 141     </fields>
 142     <fields>
 143         <fullName>Message__c</fullName>
 144         <label>Message</label>
 145         <type>TextArea</type>
 146     </fields>
 147     <fields>
 148         <fullName>Record_Id__c</fullName>
 149         <label>Record ID</label>
 150         <type>Text</type>
 151         <length>18</length>
 152     </fields>
 153 </CustomObject>
 154 ```
 155 
 156 ### Apex Queueable with Event Publishing
 157 
 158 ```apex
 159 public class AIGenerationQueueable implements Queueable, Database.AllowsCallouts {
 160 
 161     private Id recordId;
 162     private Id userId;
 163 
 164     public AIGenerationQueueable(Id recordId, Id userId) {
 165         this.recordId = recordId;
 166         this.userId = userId;
 167     }
 168 
 169     public void execute(QueueableContext context) {
 170         String status;
 171         String message;
 172 
 173         try {
 174             // Perform async work (AI generation, callout, etc.)
 175             performGeneration();
 176             status = 'SUCCESS';
 177             message = 'AI content generated successfully';
 178         } catch (Exception e) {
 179             status = 'ERROR';
 180             message = e.getMessage();
 181         }
 182 
 183         // Publish completion event
 184         publishCompletionEvent(status, message);
 185     }
 186 
 187     private void publishCompletionEvent(String status, String message) {
 188         Job_Complete__e event = new Job_Complete__e();
 189         event.Job_Id__c = 'AI_GEN_' + recordId;
 190         event.User_Id__c = userId;
 191         event.Status__c = status;
 192         event.Message__c = message;
 193         event.Record_Id__c = recordId;
 194 
 195         Database.SaveResult result = EventBus.publish(event);
 196         if (!result.isSuccess()) {
 197             System.debug('Event publish failed: ' + result.getErrors());
 198         }
 199     }
 200 
 201     private void performGeneration() {
 202         // AI generation logic...
 203     }
 204 }
 205 ```
 206 
 207 ### LWC Listener Component
 208 
 209 ```javascript
 210 // jobCompletionListener.js
 211 import { LightningElement, api } from 'lwc';
 212 import { subscribe, unsubscribe, onError } from 'lightning/empApi';
 213 import { ShowToastEvent } from 'lightning/platformShowToastEvent';
 214 import { refreshApex } from '@salesforce/apex';
 215 import userId from '@salesforce/user/Id';
 216 
 217 export default class JobCompletionListener extends LightningElement {
 218     @api recordId;
 219 
 220     subscription = null;
 221     channelName = '/event/Job_Complete__e';
 222 
 223     // Reference to wired data for refresh
 224     wiredResult;
 225 
 226     connectedCallback() {
 227         this.registerErrorListener();
 228         this.subscribeToChannel();
 229     }
 230 
 231     disconnectedCallback() {
 232         this.unsubscribeFromChannel();
 233     }
 234 
 235     async subscribeToChannel() {
 236         if (this.subscription) return;
 237 
 238         try {
 239             this.subscription = await subscribe(
 240                 this.channelName,
 241                 -1,
 242                 (message) => this.handleMessage(message)
 243             );
 244         } catch (error) {
 245             console.error('Subscription error:', error);
 246         }
 247     }
 248 
 249     unsubscribeFromChannel() {
 250         if (this.subscription) {
 251             unsubscribe(this.subscription);
 252             this.subscription = null;
 253         }
 254     }
 255 
 256     handleMessage(message) {
 257         const payload = message.data.payload;
 258 
 259         // Filter: Only process events for current user and record
 260         if (payload.User_Id__c !== userId) return;
 261         if (payload.Record_Id__c !== this.recordId) return;
 262 
 263         // Show toast notification
 264         const variant = payload.Status__c === 'SUCCESS' ? 'success' : 'error';
 265         this.dispatchEvent(new ShowToastEvent({
 266             title: payload.Status__c === 'SUCCESS' ? 'Complete' : 'Error',
 267             message: payload.Message__c,
 268             variant: variant
 269         }));
 270 
 271         // Refresh data if successful
 272         if (payload.Status__c === 'SUCCESS' && this.wiredResult) {
 273             refreshApex(this.wiredResult);
 274         }
 275 
 276         // Dispatch custom event for parent components
 277         this.dispatchEvent(new CustomEvent('jobcomplete', {
 278             detail: {
 279                 jobId: payload.Job_Id__c,
 280                 status: payload.Status__c,
 281                 message: payload.Message__c
 282             }
 283         }));
 284     }
 285 
 286     registerErrorListener() {
 287         onError((error) => {
 288             console.error('EmpApi error:', JSON.stringify(error));
 289             // Reconnect after delay
 290             this.subscription = null;
 291             setTimeout(() => this.subscribeToChannel(), 3000);
 292         });
 293     }
 294 }
 295 ```
 296 
 297 ---
 298 
 299 ## Pattern 2: Real-Time Record Updates (CDC)
 300 
 301 Use Change Data Capture to sync UI when records change.
 302 
 303 ### Enable CDC for Object
 304 
 305 1. Setup → Integrations → Change Data Capture
 306 2. Select objects to track
 307 3. Deploy (or enable via metadata)
 308 
 309 ### CDC Channel Names
 310 
 311 | Object Type | Channel Pattern |
 312 |-------------|-----------------|
 313 | Standard Object | `/data/AccountChangeEvent` |
 314 | Custom Object | `/data/My_Object__ChangeEvent` |
 315 
 316 ### LWC CDC Listener
 317 
 318 ```javascript
 319 // recordChangeListener.js
 320 import { LightningElement, api, wire } from 'lwc';
 321 import { subscribe, unsubscribe, onError } from 'lightning/empApi';
 322 import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
 323 import { refreshApex } from '@salesforce/apex';
 324 
 325 const FIELDS = ['Account.Name', 'Account.Industry', 'Account.AnnualRevenue'];
 326 
 327 export default class RecordChangeListener extends LightningElement {
 328     @api recordId;
 329 
 330     subscription = null;
 331     channelName = '/data/AccountChangeEvent';
 332 
 333     @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
 334     wiredRecord;
 335 
 336     get accountName() {
 337         return getFieldValue(this.wiredRecord.data, 'Account.Name');
 338     }
 339 
 340     connectedCallback() {
 341         this.registerErrorListener();
 342         this.subscribeToChanges();
 343     }
 344 
 345     disconnectedCallback() {
 346         if (this.subscription) {
 347             unsubscribe(this.subscription);
 348         }
 349     }
 350 
 351     async subscribeToChanges() {
 352         try {
 353             this.subscription = await subscribe(
 354                 this.channelName,
 355                 -1,
 356                 (message) => this.handleChange(message)
 357             );
 358         } catch (error) {
 359             console.error('CDC subscription error:', error);
 360         }
 361     }
 362 
 363     handleChange(message) {
 364         const payload = message.data.payload;
 365         const changeType = payload.ChangeEventHeader.changeType;
 366         const recordIds = payload.ChangeEventHeader.recordIds;
 367 
 368         // Only process changes for our record
 369         if (!recordIds.includes(this.recordId)) return;
 370 
 371         console.log(`Record ${changeType}:`, payload);
 372 
 373         // Refresh the wire
 374         if (this.wiredRecord) {
 375             refreshApex(this.wiredRecord);
 376         }
 377 
 378         // Notify parent
 379         this.dispatchEvent(new CustomEvent('recordchange', {
 380             detail: {
 381                 changeType,
 382                 changedFields: payload.ChangeEventHeader.changedFields,
 383                 payload
 384             }
 385         }));
 386     }
 387 
 388     registerErrorListener() {
 389         onError((error) => {
 390             console.error('CDC error:', error);
 391             this.subscription = null;
 392             setTimeout(() => this.subscribeToChanges(), 5000);
 393         });
 394     }
 395 }
 396 ```
 397 
 398 ### CDC Payload Structure
 399 
 400 ```javascript
 401 {
 402     "data": {
 403         "schema": "...",
 404         "payload": {
 405             "ChangeEventHeader": {
 406                 "entityName": "Account",
 407                 "recordIds": ["001xx000003ABCDE"],
 408                 "changeType": "UPDATE",  // CREATE, UPDATE, DELETE, UNDELETE
 409                 "changedFields": ["Name", "Industry"],
 410                 "changeOrigin": "com/salesforce/api/soap/58.0",
 411                 "transactionKey": "...",
 412                 "sequenceNumber": 1,
 413                 "commitTimestamp": 1705612800000,
 414                 "commitUser": "005xx000001AAAAA",
 415                 "commitNumber": 123456789
 416             },
 417             // Changed field values
 418             "Name": "Updated Account Name",
 419             "Industry": "Technology"
 420         }
 421     }
 422 }
 423 ```
 424 
 425 ---
 426 
 427 ## Pattern 3: Multi-User Collaboration
 428 
 429 Notify all users viewing the same record.
 430 
 431 ```javascript
 432 // collaborativeEditor.js
 433 import { LightningElement, api } from 'lwc';
 434 import { subscribe, unsubscribe, onError } from 'lightning/empApi';
 435 import userId from '@salesforce/user/Id';
 436 
 437 export default class CollaborativeEditor extends LightningElement {
 438     @api recordId;
 439 
 440     subscription = null;
 441     channelName = '/event/Edit_Activity__e';
 442     activeEditors = [];
 443 
 444     connectedCallback() {
 445         this.registerErrorListener();
 446         this.subscribeToActivity();
 447         this.announcePresence();
 448     }
 449 
 450     disconnectedCallback() {
 451         this.announceExit();
 452         this.unsubscribe();
 453     }
 454 
 455     async subscribeToActivity() {
 456         this.subscription = await subscribe(
 457             this.channelName,
 458             -1,
 459             (message) => this.handleActivity(message)
 460         );
 461     }
 462 
 463     handleActivity(message) {
 464         const { Record_Id__c, User_Id__c, User_Name__c, Action__c } = message.data.payload;
 465 
 466         // Ignore our own events, only track this record
 467         if (User_Id__c === userId || Record_Id__c !== this.recordId) return;
 468 
 469         if (Action__c === 'JOINED') {
 470             this.addEditor(User_Id__c, User_Name__c);
 471         } else if (Action__c === 'LEFT') {
 472             this.removeEditor(User_Id__c);
 473         } else if (Action__c === 'EDITING') {
 474             this.showEditingIndicator(User_Name__c, message.data.payload.Field__c);
 475         }
 476     }
 477 
 478     addEditor(userId, userName) {
 479         if (!this.activeEditors.find(e => e.id === userId)) {
 480             this.activeEditors = [...this.activeEditors, { id: userId, name: userName }];
 481         }
 482     }
 483 
 484     removeEditor(userId) {
 485         this.activeEditors = this.activeEditors.filter(e => e.id !== userId);
 486     }
 487 
 488     // Call Apex to publish presence event
 489     announcePresence() {
 490         // publishEditActivity({ recordId: this.recordId, action: 'JOINED' });
 491     }
 492 
 493     announceExit() {
 494         // publishEditActivity({ recordId: this.recordId, action: 'LEFT' });
 495     }
 496 
 497     unsubscribe() {
 498         if (this.subscription) {
 499             unsubscribe(this.subscription);
 500         }
 501     }
 502 
 503     registerErrorListener() {
 504         onError((error) => {
 505             console.error('Collaboration error:', error);
 506         });
 507     }
 508 }
 509 ```
 510 
 511 ---
 512 
 513 ## Pattern 4: Polling Fallback
 514 
 515 When empApi isn't available (Communities, some mobile contexts), use polling.
 516 
 517 ```javascript
 518 // pollingFallback.js
 519 import { LightningElement, api } from 'lwc';
 520 import checkJobStatus from '@salesforce/apex/JobStatusController.checkJobStatus';
 521 
 522 export default class PollingFallback extends LightningElement {
 523     @api jobId;
 524 
 525     pollingInterval = null;
 526     pollFrequencyMs = 3000;
 527     maxAttempts = 60;
 528     attemptCount = 0;
 529 
 530     connectedCallback() {
 531         this.startPolling();
 532     }
 533 
 534     disconnectedCallback() {
 535         this.stopPolling();
 536     }
 537 
 538     startPolling() {
 539         this.pollingInterval = setInterval(() => {
 540             this.checkStatus();
 541         }, this.pollFrequencyMs);
 542     }
 543 
 544     stopPolling() {
 545         if (this.pollingInterval) {
 546             clearInterval(this.pollingInterval);
 547             this.pollingInterval = null;
 548         }
 549     }
 550 
 551     async checkStatus() {
 552         this.attemptCount++;
 553 
 554         if (this.attemptCount >= this.maxAttempts) {
 555             this.stopPolling();
 556             this.handleTimeout();
 557             return;
 558         }
 559 
 560         try {
 561             const result = await checkJobStatus({ jobId: this.jobId });
 562 
 563             if (result.status === 'COMPLETE' || result.status === 'ERROR') {
 564                 this.stopPolling();
 565                 this.handleCompletion(result);
 566             }
 567         } catch (error) {
 568             console.error('Polling error:', error);
 569         }
 570     }
 571 
 572     handleCompletion(result) {
 573         this.dispatchEvent(new CustomEvent('complete', { detail: result }));
 574     }
 575 
 576     handleTimeout() {
 577         this.dispatchEvent(new CustomEvent('timeout'));
 578     }
 579 }
 580 ```
 581 
 582 ---
 583 
 584 ## Replay Options
 585 
 586 | Replay ID | Behavior |
 587 |-----------|----------|
 588 | `-1` | Only new events (after subscription) |
 589 | `-2` | All stored events (last 24 hours) + new |
 590 | Specific ID | Events after that replay ID |
 591 
 592 ### Storing Replay Position
 593 
 594 ```javascript
 595 // For durable subscriptions, store last processed replay ID
 596 handleMessage(message) {
 597     const replayId = message.data.event.replayId;
 598 
 599     // Process message...
 600 
 601     // Store replay ID for recovery
 602     this.lastReplayId = replayId;
 603     localStorage.setItem('myapp_replay_id', replayId);
 604 }
 605 
 606 connectedCallback() {
 607     // Recover from stored position
 608     const storedReplayId = localStorage.getItem('myapp_replay_id');
 609     const replayFrom = storedReplayId ? parseInt(storedReplayId, 10) : -1;
 610 
 611     this.subscribeFromReplayId(replayFrom);
 612 }
 613 ```
 614 
 615 ---
 616 
 617 ## Best Practices
 618 
 619 ### DO ✅
 620 
 621 | Practice | Reason |
 622 |----------|--------|
 623 | Always unsubscribe in `disconnectedCallback` | Prevents memory leaks |
 624 | Filter events by user/record ID | Reduces unnecessary processing |
 625 | Register error handler | Enables reconnection on failure |
 626 | Use `refreshApex` after events | Keeps wire data in sync |
 627 | Set reasonable replay ID | `-1` for real-time, `-2` for recovery |
 628 
 629 ### DON'T ❌
 630 
 631 | Anti-Pattern | Problem |
 632 |--------------|---------|
 633 | Subscribe without unsubscribing | Memory leak, duplicate handlers |
 634 | Process all events without filtering | Performance impact |
 635 | Ignore error handler | Silent failures, no reconnection |
 636 | Mutate wire data directly | Breaks reactivity |
 637 | Use CDC for high-frequency updates | Rate limits, performance |
 638 
 639 ---
 640 
 641 ## Troubleshooting
 642 
 643 | Issue | Cause | Solution |
 644 |-------|-------|----------|
 645 | No events received | Subscription failed silently | Check error handler, verify channel name |
 646 | Duplicate processing | Component re-mounted | Track subscription state, dedupe by replay ID |
 647 | Events delayed | High server load | Normal behavior, events are async |
 648 | "Handshake denied" | Missing permissions | Verify Streaming API access in profile |
 649 | Events stop after time | Session expired | Handle error event, resubscribe |
 650 
 651 ---
 652 
 653 ## Cross-Skill References
 654 
 655 | Topic | Resource |
 656 |-------|----------|
 657 | Platform Event definition | [sf-integration/references/platform-events-guide.md](../../sf-integration/references/platform-events-guide.md) |
 658 | Publishing from Apex | [sf-apex/references/best-practices.md](../../sf-apex/references/best-practices.md) |
 659 | State management | [state-management.md](state-management.md) |
 660 | Agentforce Models API | [sf-ai-agentforce/references/models-api.md](../../sf-ai-agentforce/references/models-api.md) |
