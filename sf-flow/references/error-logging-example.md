<!-- Parent: sf-flow/SKILL.md -->
   1 # Error Logging Pattern Example
   2 
   3 ## Overview
   4 
   5 This example demonstrates how to use the **Sub_LogError** reusable subflow to implement structured error logging in your flows. Structured error logging provides visibility into flow failures and accelerates debugging in production environments.
   6 
   7 ## Prerequisites
   8 
   9 1. **Deploy the Sub_LogError subflow** from `assets/subflows/subflow-error-logger.xml`
  10 2. **Create the Flow_Error_Log__c custom object** with these fields:
  11    - `Flow_Name__c` (Text, 255)
  12    - `Record_Id__c` (Text, 18)
  13    - `Error_Message__c` (Long Text Area, 32,768)
  14 
  15 ## Use Case
  16 
  17 You have a Record-Triggered Flow on Account that updates related Contacts. If the Contact update fails, you want to log the error with context for troubleshooting.
  18 
  19 ## Implementation Pattern
  20 
  21 ###  1. Main Flow with Fault Path
  22 
  23 ```xml
  24 <recordUpdates>
  25     <name>Update_Related_Contacts</name>
  26     <label>Update Related Contacts</label>
  27     <locationX>0</locationX>
  28     <locationY>0</locationY>
  29     <!-- Fault connector to error handler -->
  30     <faultConnector>
  31         <targetReference>Call_Error_Logger</targetReference>
  32     </faultConnector>
  33     <filters>
  34         <field>AccountId</field>
  35         <operator>EqualTo</operator>
  36         <value>
  37             <elementReference>$Record.Id</elementReference>
  38         </value>
  39     </filters>
  40     <inputAssignments>
  41         <field>Industry</field>
  42         <value>
  43             <elementReference>$Record.Industry</elementReference>
  44         </value>
  45     </inputAssignments>
  46     <object>Contact</object>
  47 </recordUpdates>
  48 ```
  49 
  50 ### 2. Call Sub_LogError Subflow
  51 
  52 ```xml
  53 <subflows>
  54     <name>Call_Error_Logger</name>
  55     <label>Call Error Logger</label>
  56     <locationX>0</locationX>
  57     <locationY>0</locationY>
  58     <flowName>Sub_LogError</flowName>
  59     <inputAssignments>
  60         <name>varFlowName</name>
  61         <value>
  62             <stringValue>RTF_Account_UpdateContacts</stringValue>
  63         </value>
  64     </inputAssignments>
  65     <inputAssignments>
  66         <name>varRecordId</name>
  67         <value>
  68             <elementReference>$Record.Id</elementReference>
  69         </value>
  70     </inputAssignments>
  71     <inputAssignments>
  72         <name>varErrorMessage</name>
  73         <value>
  74             <elementReference>$Flow.FaultMessage</elementReference>
  75         </value>
  76     </inputAssignments>
  77 </subflows>
  78 ```
  79 
  80 ## Benefits
  81 
  82 ### ✅ Structured Data Capture
  83 - **Flow Name**: Identifies which flow failed
  84 - **Record ID**: Links error to specific record for investigation
  85 - **Error Message**: Captures the system fault message
  86 - **Timestamp**: Auto-captured by Flow_Error_Log__c created date
  87 
  88 ### ✅ Centralized Error Tracking
  89 Query all flow errors in one place:
  90 ```sql
  91 SELECT Flow_Name__c, Record_Id__c, Error_Message__c, CreatedDate
  92 FROM Flow_Error_Log__c
  93 WHERE CreatedDate = TODAY
  94 ORDER BY CreatedDate DESC
  95 ```
  96 
  97 ### ✅ Debugging Efficiency
  98 1. User reports: "Account update failed"
  99 2. Query Flow_Error_Log__c for that Account ID
 100 3. See exact error message and flow name
 101 4. Debug with full context—no need to enable debug logs first
 102 
 103 ### ✅ Production Monitoring
 104 Create a dashboard showing:
 105 - Error count by flow name
 106 - Error trends over time
 107 - Most common error messages
 108 
 109 ## Advanced Patterns
 110 
 111 ### Pattern 1: Add Alert Email
 112 
 113 Extend Sub_LogError to send email alerts for critical errors:
 114 
 115 ```xml
 116 <actionCalls>
 117     <name>Send_Error_Alert</name>
 118     <label>Send Error Alert</label>
 119     <locationX>0</locationX>
 120     <locationY>0</locationY>
 121     <actionName>emailSimple</actionName>
 122     <actionType>emailSimple</actionType>
 123     <inputParameters>
 124         <name>emailAddresses</name>
 125         <value>
 126             <stringValue>admin@company.com</stringValue>
 127         </value>
 128     </inputParameters>
 129     <inputParameters>
 130         <name>emailSubject</name>
 131         <value>
 132             <stringValue>Flow Error: {!varFlowName}</stringValue>
 133         </value>
 134     </inputParameters>
 135     <inputParameters>
 136         <name>emailBody</name>
 137         <value>
 138             <stringValue>Error occurred in flow: {!varFlowName}
 139 Record ID: {!varRecordId}
 140 Error Message: {!varErrorMessage}</stringValue>
 141         </value>
 142     </inputParameters>
 143 </actionCalls>
 144 ```
 145 
 146 ### Pattern 2: Integration with Platform Events
 147 
 148 For real-time error monitoring, publish a Platform Event instead of creating a record:
 149 
 150 ```xml
 151 <recordCreates>
 152     <name>Publish_Error_Event</name>
 153     <object>Flow_Error__e</object>
 154     <inputAssignments>
 155         <field>Flow_Name__c</field>
 156         <value>
 157             <elementReference>varFlowName</elementReference>
 158         </value>
 159     </inputAssignments>
 160     <!-- ... other fields ... -->
 161 </recordCreates>
 162 ```
 163 
 164 ## Testing Your Error Logger
 165 
 166 ### 1. Deploy Sub_LogError
 167 ```bash
 168 sf project deploy start --source-dir assets/subflows/ --target-org myorg
 169 ```
 170 
 171 ### 2. Create Test Flow with Intentional Error
 172 Create a flow that attempts to update a field that doesn't exist, then check Flow_Error_Log__c.
 173 
 174 ### 3. Verify Error Capture
 175 ```bash
 176 sf data query --query "SELECT Flow_Name__c, Error_Message__c FROM Flow_Error_Log__c ORDER BY CreatedDate DESC LIMIT 1" --target-org myorg
 177 ```
 178 
 179 ## Best Practices
 180 
 181 ✅ **DO**:
 182 - Use Sub_LogError in all fault paths
 183 - Pass meaningful flow names (use naming conventions like RTF_, Auto_, etc.)
 184 - Include record ID whenever available for context
 185 - Review error logs regularly to identify patterns
 186 
 187 ❌ **DON'T**:
 188 - Skip fault paths on DML operations
 189 - Hardcode error messages (use $Flow.FaultMessage)
 190 - Ignore error logs—they're your production monitoring
 191 
 192 ## Related Documentation
 193 
 194 - [Subflow Library](../references/subflow-library.md) - All reusable subflows
 195 - [Orchestration Patterns](../references/orchestration-guide.md) - Parent-child flow architecture
 196 - [Flow Best Practices](../references/flow-best-practices.md) - Running mode and permissions
 197 
 198 ## Questions?
 199 
 200 For issues or questions:
 201 1. Check the troubleshooting section in README.md
 202 2. Review the skill.md for detailed workflow
 203 3. Test with the Sub_LogError template first before customizing
