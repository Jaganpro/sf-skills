<!-- Parent: sf-integration/SKILL.md -->
   1 # Platform Events Guide
   2 
   3 ## Overview
   4 
   5 Platform Events enable event-driven architecture in Salesforce. They provide a scalable, asynchronous messaging system for real-time integrations.
   6 
   7 ## Event Types
   8 
   9 ### Standard Volume
  10 
  11 - Up to ~2,000 events per hour
  12 - Included in all Salesforce editions
  13 - Standard delivery guarantees
  14 
  15 ### High Volume
  16 
  17 - Millions of events per day
  18 - At-least-once delivery
  19 - 24-hour retention for replay
  20 - May require additional entitlement
  21 
  22 ## When to Use Platform Events
  23 
  24 | Scenario | Platform Events | Other Options |
  25 |----------|-----------------|---------------|
  26 | Real-time notifications | ✅ Best choice | - |
  27 | Decoupled integrations | ✅ Best choice | - |
  28 | High-volume streaming | ✅ High Volume | Change Data Capture |
  29 | Simple record sync | Consider | Change Data Capture |
  30 | External system notifications | ✅ Best choice | - |
  31 | Internal process triggers | ✅ Good choice | Process Builder, Flow |
  32 
  33 ## Creating Platform Events
  34 
  35 ### Via Metadata (Recommended)
  36 
  37 ```xml
  38 <?xml version="1.0" encoding="UTF-8"?>
  39 <CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
  40     <deploymentStatus>Deployed</deploymentStatus>
  41     <eventType>HighVolume</eventType>
  42     <label>Order Update Event</label>
  43     <pluralLabel>Order Update Events</pluralLabel>
  44     <publishBehavior>PublishAfterCommit</publishBehavior>
  45     <fields>
  46         <fullName>Order_Id__c</fullName>
  47         <label>Order ID</label>
  48         <type>Text</type>
  49         <length>18</length>
  50     </fields>
  51     <fields>
  52         <fullName>Status__c</fullName>
  53         <label>Status</label>
  54         <type>Text</type>
  55         <length>50</length>
  56     </fields>
  57 </CustomObject>
  58 ```
  59 
  60 ### File Location
  61 
  62 ```
  63 force-app/main/default/objects/Order_Update_Event__e/Order_Update_Event__e.object-meta.xml
  64 ```
  65 
  66 ## Publishing Events
  67 
  68 ### From Apex
  69 
  70 ```apex
  71 // Single event
  72 Order_Update_Event__e event = new Order_Update_Event__e();
  73 event.Order_Id__c = orderId;
  74 event.Status__c = 'Shipped';
  75 
  76 Database.SaveResult result = EventBus.publish(event);
  77 if (result.isSuccess()) {
  78     System.debug('Event published: ' + result.getId());
  79 }
  80 
  81 // Multiple events
  82 List<Order_Update_Event__e> events = new List<Order_Update_Event__e>();
  83 // ... populate events
  84 List<Database.SaveResult> results = EventBus.publish(events);
  85 ```
  86 
  87 ### From Flow
  88 
  89 1. Create Record element
  90 2. Select Platform Event object
  91 3. Map field values
  92 
  93 ### From Process Builder
  94 
  95 1. Add Immediate Action
  96 2. Select "Create a Record"
  97 3. Choose Platform Event
  98 
  99 ## Subscribing to Events
 100 
 101 ### Apex Trigger
 102 
 103 ```apex
 104 trigger OrderUpdateSubscriber on Order_Update_Event__e (after insert) {
 105     for (Order_Update_Event__e event : Trigger.new) {
 106         System.debug('Order ' + event.Order_Id__c + ' is now ' + event.Status__c);
 107         // Process event
 108     }
 109 
 110     // Set checkpoint for durability
 111     EventBus.TriggerContext.currentContext().setResumeCheckpoint(
 112         Trigger.new[Trigger.new.size() - 1].ReplayId
 113     );
 114 }
 115 ```
 116 
 117 ### Flow (Record-Triggered)
 118 
 119 1. Create Platform Event-Triggered Flow
 120 2. Select Platform Event object
 121 3. Build logic with event data
 122 
 123 ### External (CometD)
 124 
 125 External systems can subscribe using CometD streaming:
 126 
 127 ```
 128 /event/Order_Update_Event__e
 129 ```
 130 
 131 ## Publish Behavior
 132 
 133 ### PublishAfterCommit (Default)
 134 
 135 - Event published after transaction commits
 136 - If transaction rolls back, event NOT published
 137 - **Recommended for most cases**
 138 
 139 ### PublishImmediately
 140 
 141 - Event published immediately
 142 - Event still published even if transaction rolls back
 143 - Use when external system must be notified regardless of outcome
 144 
 145 ## Durability & Replay
 146 
 147 ### Replay ID
 148 
 149 Each event has a unique `ReplayId` for tracking and replay:
 150 
 151 ```apex
 152 String replayId = event.ReplayId;
 153 ```
 154 
 155 ### Resume Checkpoint
 156 
 157 Set checkpoint to ensure durability:
 158 
 159 ```apex
 160 // In trigger
 161 EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastReplayId);
 162 ```
 163 
 164 If trigger fails after checkpoint, processing resumes from that point.
 165 
 166 ### Retention
 167 
 168 - High Volume events: 24 hours
 169 - Standard Volume: 24 hours
 170 
 171 ## Best Practices
 172 
 173 ### Publishing
 174 
 175 1. **Batch events** when publishing multiple
 176 2. **Check SaveResults** for publish failures
 177 3. **Use meaningful correlation IDs** for tracking
 178 4. **Include timestamp** for ordering
 179 5. **Keep payloads small** - use IDs, not full records
 180 
 181 ### Subscribing
 182 
 183 1. **Always set resume checkpoint** in triggers
 184 2. **Don't throw exceptions** - catch and log errors
 185 3. **Process idempotently** - events may replay
 186 4. **Keep processing lightweight** - queue heavy work
 187 5. **Handle duplicates** using correlation ID
 188 
 189 ### Design
 190 
 191 1. **Event granularity** - not too fine, not too coarse
 192 2. **Include enough context** but not entire records
 193 3. **Version your events** if schema evolves
 194 4. **Document event contracts** for consumers
 195 
 196 ## Error Handling
 197 
 198 ### Publish Errors
 199 
 200 ```apex
 201 List<Database.SaveResult> results = EventBus.publish(events);
 202 for (Integer i = 0; i < results.size(); i++) {
 203     if (!results[i].isSuccess()) {
 204         for (Database.Error err : results[i].getErrors()) {
 205             System.debug('Publish failed: ' + err.getMessage());
 206         }
 207     }
 208 }
 209 ```
 210 
 211 ### Subscriber Errors
 212 
 213 ```apex
 214 trigger MySubscriber on My_Event__e (after insert) {
 215     for (My_Event__e event : Trigger.new) {
 216         try {
 217             processEvent(event);
 218         } catch (Exception e) {
 219             // Log error, don't throw
 220             System.debug('Error processing ' + event.ReplayId + ': ' + e.getMessage());
 221             // Create error log record
 222         }
 223     }
 224 
 225     // Still set checkpoint even if some failed
 226     EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastReplayId);
 227 }
 228 ```
 229 
 230 ## Monitoring
 231 
 232 ### Setup → Platform Events
 233 
 234 - View event definitions
 235 - Check usage metrics
 236 - Monitor delivery status
 237 
 238 ### Event Delivery Failures
 239 
 240 Check for:
 241 - Unhandled exceptions in triggers
 242 - Apex CPU timeout
 243 - Governor limit errors
 244 
 245 ### Event Publishing
 246 
 247 Query `EventBusSubscriber` for subscription health:
 248 
 249 ```apex
 250 SELECT Id, Position, ExternalId, Name, Status, Tip
 251 FROM EventBusSubscriber
 252 WHERE Topic = 'Order_Update_Event__e'
 253 ```
 254 
 255 ## Limits
 256 
 257 | Limit | Standard Volume | High Volume |
 258 |-------|-----------------|-------------|
 259 | Events per hour | ~2,000 | Millions |
 260 | Retention | 24 hours | 24 hours |
 261 | Max event size | 1 MB | 1 MB |
 262 | Fields per event | 100 | 100 |
 263 
 264 ## External Integration
 265 
 266 ### Subscribe from External System
 267 
 268 Use CometD client to connect to Streaming API:
 269 
 270 ```
 271 Endpoint: /cometd/62.0
 272 Channel: /event/Order_Update_Event__e
 273 ```
 274 
 275 ### Publish from External System
 276 
 277 Use REST API:
 278 
 279 ```http
 280 POST /services/data/v62.0/sobjects/Order_Update_Event__e
 281 Content-Type: application/json
 282 
 283 {
 284     "Order_Id__c": "001xx000003NGSFAA4",
 285     "Status__c": "Shipped"
 286 }
 287 ```
