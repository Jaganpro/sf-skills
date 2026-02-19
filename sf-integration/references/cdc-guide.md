<!-- Parent: sf-integration/SKILL.md -->
   1 # Change Data Capture (CDC) Guide
   2 
   3 ## Overview
   4 
   5 Change Data Capture publishes change events for Salesforce records, enabling near real-time data synchronization with external systems.
   6 
   7 ## How CDC Works
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────┐
  11 │  CHANGE DATA CAPTURE FLOW                                       │
  12 ├─────────────────────────────────────────────────────────────────┤
  13 │                                                                 │
  14 │  1. Record Created/Updated/Deleted in Salesforce                │
  15 │     ↓                                                           │
  16 │  2. Salesforce generates Change Event                           │
  17 │     ↓                                                           │
  18 │  3. Event published to {{Object}}ChangeEvent channel            │
  19 │     ↓                                                           │
  20 │  4. Apex Trigger or External Subscriber receives event          │
  21 │     ↓                                                           │
  22 │  5. Process event (sync, audit, notify)                         │
  23 │                                                                 │
  24 └─────────────────────────────────────────────────────────────────┘
  25 ```
  26 
  27 ## CDC vs Platform Events
  28 
  29 | Feature | CDC | Platform Events |
  30 |---------|-----|-----------------|
  31 | Trigger | Automatic on DML | Manual publish |
  32 | Schema | Predefined (object fields) | Custom defined |
  33 | Use Case | Data sync/replication | Custom messaging |
  34 | Control | Limited | Full control |
  35 
  36 ## Enabling CDC
  37 
  38 ### Via Setup
  39 
  40 1. Go to **Setup → Integrations → Change Data Capture**
  41 2. Select objects to enable
  42 3. Save
  43 
  44 ### Supported Objects
  45 
  46 - Most Standard objects (Account, Contact, Opportunity, etc.)
  47 - Custom objects
  48 - Some system objects (User, Group, etc.)
  49 
  50 ## Event Channel Names
  51 
  52 | Object Type | Channel Name |
  53 |-------------|--------------|
  54 | Standard | `AccountChangeEvent`, `ContactChangeEvent` |
  55 | Custom | `My_Object__ChangeEvent` (append ChangeEvent) |
  56 
  57 ## Change Event Structure
  58 
  59 ### ChangeEventHeader
  60 
  61 ```apex
  62 EventBus.ChangeEventHeader header = event.ChangeEventHeader;
  63 
  64 // Available methods
  65 header.getChangeType();       // CREATE, UPDATE, DELETE, UNDELETE
  66 header.getChangedFields();    // List of changed field API names
  67 header.getRecordIds();        // Affected record IDs
  68 header.getEntityName();       // Object API name
  69 header.getCommitNumber();     // Transaction sequence
  70 header.getCommitTimestamp();  // When change occurred
  71 header.getTransactionKey();   // Unique transaction ID
  72 ```
  73 
  74 ### Change Types
  75 
  76 | Type | Description | Event Contains |
  77 |------|-------------|----------------|
  78 | CREATE | New record | All field values |
  79 | UPDATE | Record modified | Changed field values only |
  80 | DELETE | Record deleted | Record IDs only |
  81 | UNDELETE | Restored from bin | All field values |
  82 | GAP_* | Events missed | Affected record IDs |
  83 | GAP_OVERFLOW | Too many changes | Entity name |
  84 
  85 ### Field Values
  86 
  87 - **Changed fields**: Contain new values
  88 - **Unchanged fields**: Null
  89 - Use `getChangedFields()` to know what changed
  90 
  91 ## Subscribing to CDC
  92 
  93 ### Apex Trigger
  94 
  95 ```apex
  96 trigger AccountCDC on AccountChangeEvent (after insert) {
  97     for (AccountChangeEvent event : Trigger.new) {
  98         EventBus.ChangeEventHeader header = event.ChangeEventHeader;
  99 
 100         String changeType = header.getChangeType();
 101         List<String> changedFields = header.getChangedFields();
 102         List<String> recordIds = header.getRecordIds();
 103 
 104         switch on changeType {
 105             when 'CREATE' {
 106                 // Handle new records
 107             }
 108             when 'UPDATE' {
 109                 // Handle updates
 110             }
 111             when 'DELETE' {
 112                 // Handle deletions
 113             }
 114         }
 115     }
 116 
 117     // Set checkpoint
 118     EventBus.TriggerContext.currentContext().setResumeCheckpoint(
 119         Trigger.new[Trigger.new.size()-1].ReplayId
 120     );
 121 }
 122 ```
 123 
 124 ### External (CometD)
 125 
 126 ```
 127 Channel: /data/AccountChangeEvent
 128 ```
 129 
 130 ## Handling Specific Changes
 131 
 132 ### Filter by Changed Fields
 133 
 134 ```apex
 135 // Only process if important fields changed
 136 Set<String> importantFields = new Set<String>{'Status__c', 'Amount__c'};
 137 List<String> changedFields = header.getChangedFields();
 138 
 139 Boolean relevant = false;
 140 for (String field : changedFields) {
 141     if (importantFields.contains(field)) {
 142         relevant = true;
 143         break;
 144     }
 145 }
 146 
 147 if (!relevant) return;
 148 ```
 149 
 150 ### Get New Values
 151 
 152 ```apex
 153 // Access field values from event (UPDATE: only changed fields have values)
 154 if (changedFields.contains('Status__c')) {
 155     String newStatus = event.Status__c;
 156     // Process status change
 157 }
 158 ```
 159 
 160 ## Gap Events
 161 
 162 Gap events indicate missed events:
 163 
 164 ### Types
 165 
 166 | Event | Meaning | Action |
 167 |-------|---------|--------|
 168 | GAP_CREATE | Missed creates | Query and sync records |
 169 | GAP_UPDATE | Missed updates | Query current state |
 170 | GAP_DELETE | Missed deletes | Reconcile with source |
 171 | GAP_UNDELETE | Missed restores | Query and sync |
 172 | GAP_OVERFLOW | Too many changes | Full sync required |
 173 
 174 ### Handling Gaps
 175 
 176 ```apex
 177 when 'GAP_CREATE', 'GAP_UPDATE', 'GAP_DELETE', 'GAP_UNDELETE' {
 178     // Query current state and sync
 179     List<Account> records = [
 180         SELECT Id, Name, Status__c
 181         FROM Account
 182         WHERE Id IN :header.getRecordIds()
 183     ];
 184     syncToExternalSystem(records);
 185 }
 186 when 'GAP_OVERFLOW' {
 187     // Trigger full sync batch job
 188     Database.executeBatch(new FullSyncBatch());
 189 }
 190 ```
 191 
 192 ## Replay and Durability
 193 
 194 ### Retention
 195 
 196 CDC events retained for **3 days** (72 hours).
 197 
 198 ### Replay ID
 199 
 200 Each event has unique ReplayId for tracking:
 201 
 202 ```apex
 203 String replayId = event.ReplayId;
 204 ```
 205 
 206 ### Resume Checkpoint
 207 
 208 Critical for durability:
 209 
 210 ```apex
 211 // Always set checkpoint at end of trigger
 212 EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastReplayId);
 213 ```
 214 
 215 If trigger fails after checkpoint, processing resumes from that point.
 216 
 217 ## External Sync Pattern
 218 
 219 ```apex
 220 public class AccountCDCHandler {
 221 
 222     public static void syncToExternal(AccountChangeEvent event) {
 223         EventBus.ChangeEventHeader header = event.ChangeEventHeader;
 224 
 225         Map<String, Object> payload = new Map<String, Object>{
 226             'recordIds' => header.getRecordIds(),
 227             'operation' => header.getChangeType(),
 228             'timestamp' => header.getCommitTimestamp(),
 229             'changedFields' => header.getChangedFields()
 230         };
 231 
 232         // Add field values for CREATE/UPDATE
 233         if (header.getChangeType() != 'DELETE') {
 234             payload.put('name', event.Name);
 235             payload.put('accountNumber', event.AccountNumber);
 236             // Add relevant fields
 237         }
 238 
 239         // Queue async callout
 240         System.enqueueJob(new ExternalSyncJob(payload));
 241     }
 242 }
 243 ```
 244 
 245 ## Best Practices
 246 
 247 ### DO
 248 
 249 1. **Set resume checkpoint** in every trigger
 250 2. **Filter by relevant fields** to reduce noise
 251 3. **Handle all change types** including GAPs
 252 4. **Process idempotently** (events may replay)
 253 5. **Use async** for external callouts
 254 6. **Log changes** for debugging
 255 
 256 ### DON'T
 257 
 258 1. **Don't throw exceptions** - catch and log
 259 2. **Don't ignore GAP events** - they indicate data loss
 260 3. **Don't assume single record** - batch DML creates multi-record events
 261 4. **Don't block on external calls** - use Queueable
 262 
 263 ## Monitoring
 264 
 265 ### Event Delivery
 266 
 267 Check for failures in:
 268 - Setup → Platform Events → Monitor
 269 - Debug logs for triggers
 270 
 271 ### Common Issues
 272 
 273 | Issue | Cause | Solution |
 274 |-------|-------|----------|
 275 | Missing events | No CDC enabled | Enable in Setup |
 276 | Duplicate processing | No idempotency | Check transactionKey |
 277 | GAP events | Processing too slow | Optimize trigger, scale out |
 278 | Timeout | Heavy processing | Move to async |
 279 
 280 ## Limits
 281 
 282 | Limit | Value |
 283 |-------|-------|
 284 | Objects per org | 100 |
 285 | Events per 15 minutes | Varies by edition |
 286 | Event retention | 3 days (72 hours) |
 287 | Replay window | 3 days |
