<!-- Parent: sf-flow/SKILL.md -->
   1 # Salesforce Flow Wait Element Patterns
   2 
   3 Comprehensive guide to using Wait elements in Salesforce Flows for time-based and condition-based pausing.
   4 
   5 ## Flow Type Compatibility
   6 
   7 Wait elements have **strict flow type requirements**:
   8 
   9 | Flow Type | Wait Supported? | Notes |
  10 |-----------|-----------------|-------|
  11 | **Autolaunched Flow** | ✅ Yes | Primary use case |
  12 | **Scheduled Flow** | ✅ Yes | Often combined with scheduling |
  13 | **Orchestration** | ✅ Yes | For complex multi-step processes |
  14 | **Screen Flow** | ❌ No | Cannot pause user sessions |
  15 | **Record-Triggered Flow** | ❌ No | Must complete synchronously |
  16 | **Platform Event Flow** | ❌ No | Event-driven, no waiting |
  17 
  18 **Key Insight**: If you need wait behavior in a Record-Triggered Flow, call an Autolaunched subflow that contains the Wait element.
  19 
  20 ---
  21 
  22 ## Three Wait Element Types
  23 
  24 ### 1. Wait for Amount of Time (Duration-Based)
  25 
  26 Pauses flow execution for a fixed duration.
  27 
  28 **Use Cases:**
  29 - Send follow-up email 24 hours after form submission
  30 - Escalate case if not resolved within 48 hours
  31 - Wait 7 days before survey request
  32 
  33 **XML Structure:**
  34 ```xml
  35 <waits>
  36     <name>Wait_7_Days</name>
  37     <label>Wait 7 Days</label>
  38     <waitEvents>
  39         <name>Duration_Complete</name>
  40         <eventType>AlarmEvent</eventType>
  41         <inputParameters>
  42             <name>AlarmTime</name>
  43             <value>
  44                 <elementReference>$Flow.CurrentDateTime</elementReference>
  45             </value>
  46         </inputParameters>
  47         <inputParameters>
  48             <name>TimeOffset</name>
  49             <value>
  50                 <numberValue>7.0</numberValue>
  51             </value>
  52         </inputParameters>
  53         <inputParameters>
  54             <name>TimeOffsetUnit</name>
  55             <value>
  56                 <stringValue>Days</stringValue>
  57             </value>
  58         </inputParameters>
  59         <connector>
  60             <targetReference>Next_Element</targetReference>
  61         </connector>
  62     </waitEvents>
  63 </waits>
  64 ```
  65 
  66 **TimeOffsetUnit Options:**
  67 - `Minutes`
  68 - `Hours`
  69 - `Days`
  70 - `Months`
  71 
  72 ---
  73 
  74 ### 2. Wait Until Date (Date-Based)
  75 
  76 Pauses until a specific date/time is reached.
  77 
  78 **Use Cases:**
  79 - Resume on contract expiration date
  80 - Notify before subscription renewal
  81 - Trigger on scheduled meeting time
  82 
  83 **XML Structure:**
  84 ```xml
  85 <waits>
  86     <name>Wait_Until_Renewal</name>
  87     <label>Wait Until Renewal Date</label>
  88     <waitEvents>
  89         <name>Date_Reached</name>
  90         <eventType>DateRefAlarmEvent</eventType>
  91         <inputParameters>
  92             <name>DateTime</name>
  93             <value>
  94                 <elementReference>var_RenewalDate</elementReference>
  95             </value>
  96         </inputParameters>
  97         <connector>
  98             <targetReference>Send_Renewal_Reminder</targetReference>
  99         </connector>
 100     </waitEvents>
 101 </waits>
 102 ```
 103 
 104 **Pro Tip:** Use a formula to calculate the target date:
 105 ```xml
 106 <formulas>
 107     <name>formula_RenewalReminder</name>
 108     <dataType>DateTime</dataType>
 109     <!-- 30 days before renewal -->
 110     <expression>{!rec_Contract.EndDate} - 30</expression>
 111 </formulas>
 112 ```
 113 
 114 ---
 115 
 116 ### 3. Wait for Conditions (Condition-Based)
 117 
 118 Pauses until a field meets specified criteria OR timeout expires.
 119 
 120 **Use Cases:**
 121 - Resume when Case Status changes to 'Closed'
 122 - Resume when Approval Status is 'Approved'
 123 - Resume when Payment is 'Received'
 124 
 125 **XML Structure:**
 126 ```xml
 127 <waits>
 128     <name>Wait_For_Approval</name>
 129     <label>Wait for Approval</label>
 130     <defaultConnector>
 131         <targetReference>Handle_Timeout</targetReference>
 132     </defaultConnector>
 133     <defaultConnectorLabel>Max Wait Exceeded</defaultConnectorLabel>
 134     <waitEvents>
 135         <name>Approval_Received</name>
 136         <conditionLogic>and</conditionLogic>
 137         <conditions>
 138             <leftValueReference>rec_Request.Status__c</leftValueReference>
 139             <operator>EqualTo</operator>
 140             <rightValue>
 141                 <stringValue>Approved</stringValue>
 142             </rightValue>
 143         </conditions>
 144         <eventType>AlarmEvent</eventType>
 145         <inputParameters>
 146             <name>AlarmTime</name>
 147             <value>
 148                 <elementReference>$Flow.CurrentDateTime</elementReference>
 149             </value>
 150         </inputParameters>
 151         <inputParameters>
 152             <name>TimeOffset</name>
 153             <value>
 154                 <numberValue>30.0</numberValue>
 155             </value>
 156         </inputParameters>
 157         <inputParameters>
 158             <name>TimeOffsetUnit</name>
 159             <value>
 160                 <stringValue>Days</stringValue>
 161             </value>
 162         </inputParameters>
 163         <connector>
 164             <targetReference>Process_Approved_Request</targetReference>
 165         </connector>
 166         <label>Approved</label>
 167     </waitEvents>
 168 </waits>
 169 ```
 170 
 171 **Warning:** Condition-based waits are complex. Consider Platform Events for simpler event-driven patterns.
 172 
 173 ---
 174 
 175 ## Best Practices
 176 
 177 ### 1. Always Handle Timeout Paths
 178 
 179 ```xml
 180 <waits>
 181     <name>Wait_With_Timeout</name>
 182     <defaultConnector>
 183         <targetReference>Handle_Timeout</targetReference>
 184     </defaultConnector>
 185     <defaultConnectorLabel>Timeout - No Response</defaultConnectorLabel>
 186     <!-- waitEvents... -->
 187 </waits>
 188 ```
 189 
 190 ### 2. Consider Governor Limits
 191 
 192 Waiting flows consume org resources:
 193 - Each paused flow interview counts against limits
 194 - Long waits with many instances can accumulate
 195 - Monitor with Setup → Flows → Paused and Waiting Interviews
 196 
 197 ### 3. Use Variables for Dynamic Durations
 198 
 199 ```xml
 200 <variables>
 201     <name>var_WaitDays</name>
 202     <dataType>Number</dataType>
 203     <value>
 204         <numberValue>7.0</numberValue>
 205     </value>
 206 </variables>
 207 
 208 <!-- Reference in Wait -->
 209 <inputParameters>
 210     <name>TimeOffset</name>
 211     <value>
 212         <elementReference>var_WaitDays</elementReference>
 213     </value>
 214 </inputParameters>
 215 ```
 216 
 217 ### 4. Test with Shorter Durations
 218 
 219 In sandbox environments:
 220 - Use minutes instead of days for testing
 221 - Verify timeout paths work correctly
 222 - Check debug logs for wait behavior
 223 
 224 ### 5. Document Wait Logic
 225 
 226 Add XML comments explaining:
 227 - Why this duration was chosen
 228 - What happens on timeout
 229 - Business context for the wait
 230 
 231 ```xml
 232 <!--
 233     Wait 7 days for customer response.
 234     Business Rule: BR-2024-015 - Follow-up SLA
 235     Timeout Action: Escalate to manager
 236 -->
 237 <waits>
 238     <name>Wait_Customer_Response</name>
 239     <!-- ... -->
 240 </waits>
 241 ```
 242 
 243 ---
 244 
 245 ## Common Patterns
 246 
 247 ### Follow-Up Email Pattern
 248 
 249 ```
 250 Start
 251   ↓
 252 Create Case → Wait 24 Hours → Check Status → (If Open) → Send Follow-Up
 253                                     ↓
 254                             (If Closed) → End
 255 ```
 256 
 257 ### Escalation Ladder Pattern
 258 
 259 ```
 260 Start
 261   ↓
 262 Create Task → Wait 2 Days → Not Complete? → Escalate to Lead
 263                                 ↓
 264                     Wait 2 Days → Not Complete? → Escalate to Manager
 265                                         ↓
 266                             Wait 1 Day → Auto-Close with Note
 267 ```
 268 
 269 ### Approval Wait Pattern
 270 
 271 ```
 272 Start
 273   ↓
 274 Submit for Approval → Wait for Approval (30 day max)
 275                             ↓                    ↓
 276                      (Approved)              (Timeout)
 277                          ↓                       ↓
 278                   Process Request         Notify Submitter
 279 ```
 280 
 281 ---
 282 
 283 ## Platform Events vs. Wait for Conditions
 284 
 285 Consider Platform Events when:
 286 
 287 | Scenario | Use Wait | Use Platform Event |
 288 |----------|----------|-------------------|
 289 | Fixed time delay | ✅ | ❌ |
 290 | Wait for date | ✅ | ❌ |
 291 | External system callback | ❌ | ✅ |
 292 | Real-time field change | ❌ | ✅ |
 293 | Complex event correlation | ❌ | ✅ |
 294 | Simple status check | ✅ | ❌ |
 295 
 296 **Platform Event Advantage:** Immediate response when event fires, no polling delay.
 297 
 298 **Wait Advantage:** Simpler setup, no Platform Event definition required.
 299 
 300 ---
 301 
 302 ## Troubleshooting
 303 
 304 ### Paused Interview Not Resuming
 305 
 306 1. Check interview status in Setup → Flows → Paused and Waiting Interviews
 307 2. Verify target date hasn't passed (for Date-based waits)
 308 3. Check condition field values match expected criteria
 309 4. Review debug logs for errors during resume
 310 
 311 ### Too Many Paused Interviews
 312 
 313 1. Add timeout paths to prevent indefinite waits
 314 2. Consider batch cleanup flow for stale interviews
 315 3. Reduce wait durations where possible
 316 4. Use `Database.deleteAsync()` in Apex for cleanup
 317 
 318 ### Performance Issues
 319 
 320 1. Avoid Wait elements in high-volume flows
 321 2. Consider Platform Events for real-time needs
 322 3. Use Scheduled Flows instead of Wait for batch operations
 323 
 324 ---
 325 
 326 ## Related Templates
 327 
 328 - `sf-flow/assets/wait-template.xml` - All three wait patterns with examples
 329 - `sf-flow/assets/platform-event-flow-template.xml` - Event-driven alternative
 330 - `sf-flow/assets/scheduled-flow-template.xml` - Scheduled batch processing
