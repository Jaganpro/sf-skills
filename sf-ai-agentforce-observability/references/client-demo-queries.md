<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # STDM Query Walkthrough - Client Demo
   2 
   3 Step-by-step queries for exploring Session Tracing Data Model in Data Cloud Query Console.
   4 
   5 ## Data Model Hierarchy
   6 
   7 ```
   8 ssot__AIAgentSession__dlm (Session)
   9     └── ssot__AIAgentInteraction__dlm (Turn)
  10             └── ssot__AIAgentInteractionStep__dlm (LLM/Actions)
  11             └── ssot__AIAgentMoment__dlm (Messages)
  12 ```
  13 
  14 ---
  15 
  16 ## Tab S1: All Sessions
  17 
  18 **Purpose**: Overview of all agent sessions
  19 
  20 ```sql
  21 -- S1: All Sessions (Overview)
  22 SELECT
  23     ssot__Id__c AS SessionID,
  24     ssot__StartTimestamp__c AS StartTime,
  25     ssot__EndTimestamp__c AS EndTime,
  26     ssot__RelatedMessagingSessionId__c AS MessagingSessionID,
  27     ssot__AiAgentSessionEndType__c AS EndType
  28 FROM ssot__AIAgentSession__dlm
  29 ORDER BY ssot__StartTimestamp__c DESC
  30 LIMIT 100
  31 ```
  32 
  33 📋 **Copy a `SessionID` for the next query**
  34 
  35 ---
  36 
  37 ## Tab S2: Interactions for Session
  38 
  39 **Purpose**: All turns/interactions within a session
  40 
  41 ```sql
  42 -- S2: Interactions for Session
  43 SELECT
  44     ssot__Id__c AS InteractionID,
  45     ssot__AiAgentSessionId__c AS SessionID,
  46     ssot__AiAgentInteractionType__c AS InteractionType,
  47     ssot__TopicApiName__c AS Topic,
  48     ssot__StartTimestamp__c AS StartTime,
  49     ssot__EndTimestamp__c AS EndTime
  50 FROM ssot__AIAgentInteraction__dlm
  51 WHERE ssot__AiAgentSessionId__c = '{{PASTE_SESSION_ID_HERE}}'
  52 ORDER BY ssot__StartTimestamp__c
  53 ```
  54 
  55 📋 **Copy an `InteractionID` for S3 and S4**
  56 
  57 ---
  58 
  59 ## Tab S3: Steps for Interaction
  60 
  61 **Purpose**: LLM reasoning and action execution within a turn
  62 
  63 ```sql
  64 -- S3: Steps for Interaction
  65 SELECT
  66     ssot__Id__c AS StepID,
  67     ssot__AiAgentInteractionId__c AS InteractionID,
  68     ssot__AiAgentInteractionStepType__c AS StepType,
  69     ssot__Name__c AS ActionName,
  70     ssot__InputValueText__c AS InputJSON,
  71     ssot__OutputValueText__c AS OutputJSON
  72 FROM ssot__AIAgentInteractionStep__dlm
  73 WHERE ssot__AiAgentInteractionId__c = '{{PASTE_INTERACTION_ID_HERE}}'
  74 ```
  75 
  76 **StepType values**: `LLM_STEP`, `ACTION_STEP`
  77 
  78 ---
  79 
  80 ## Tab S4: Messages for Interaction
  81 
  82 **Purpose**: Actual user/agent conversation content
  83 
  84 ```sql
  85 -- S4: Messages for Interaction
  86 SELECT
  87     ssot__Id__c AS MessageID,
  88     ssot__AiAgentInteractionId__c AS InteractionID,
  89     ssot__AiAgentInteractionMessageType__c AS MessageType,
  90     ssot__ContentText__c AS Content,
  91     ssot__MessageSentTimestamp__c AS SentTime
  92 FROM ssot__AIAgentMoment__dlm
  93 WHERE ssot__AiAgentInteractionId__c = '{{PASTE_INTERACTION_ID_HERE}}'
  94 ORDER BY ssot__MessageSentTimestamp__c
  95 ```
  96 
  97 **MessageType values**: `INPUT` (user), `OUTPUT` (agent)
  98 
  99 ---
 100 
 101 ## Tab A1: Session Summary by End Type
 102 
 103 **Purpose**: Aggregate sessions by how they ended
 104 
 105 ```sql
 106 -- A1: Session Summary by End Type
 107 SELECT
 108     ssot__AiAgentSessionEndType__c AS EndType,
 109     COUNT(*) AS SessionCount
 110 FROM ssot__AIAgentSession__dlm
 111 GROUP BY ssot__AiAgentSessionEndType__c
 112 ORDER BY SessionCount DESC
 113 ```
 114 
 115 ---
 116 
 117 ## Tab A2: Topic Usage
 118 
 119 **Purpose**: Which topics handle the most turns
 120 
 121 ```sql
 122 -- A2: Topic Usage Analysis
 123 SELECT
 124     ssot__TopicApiName__c AS Topic,
 125     COUNT(*) AS TurnCount
 126 FROM ssot__AIAgentInteraction__dlm
 127 WHERE ssot__AiAgentInteractionType__c = 'TURN'
 128 GROUP BY ssot__TopicApiName__c
 129 ORDER BY TurnCount DESC
 130 ```
 131 
 132 ---
 133 
 134 ## Tab A3: Action Invocations
 135 
 136 **Purpose**: Which actions are called most frequently
 137 
 138 ```sql
 139 -- A3: Action Invocation Frequency
 140 SELECT
 141     ssot__Name__c AS ActionName,
 142     COUNT(*) AS InvocationCount
 143 FROM ssot__AIAgentInteractionStep__dlm
 144 WHERE ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
 145 GROUP BY ssot__Name__c
 146 ORDER BY InvocationCount DESC
 147 ```
 148 
 149 ---
 150 
 151 ## Demo Flow
 152 
 153 1. **S1**: Run query, pick an interesting session (look for Escalated/Failed in EndType)
 154 2. **S2**: Paste SessionID, see the conversation turns and topics
 155 3. **S3**: Paste InteractionID, see LLM reasoning + action I/O
 156 4. **S4**: Paste InteractionID, read the actual messages
 157 5. **A1-A3**: Show aggregate insights
 158 
 159 ---
 160 
 161 ## Field Reference
 162 
 163 | Friendly Name | Actual Field |
 164 |---------------|--------------|
 165 | SessionID | `ssot__Id__c` |
 166 | StartTime | `ssot__StartTimestamp__c` |
 167 | EndTime | `ssot__EndTimestamp__c` |
 168 | EndType | `ssot__AiAgentSessionEndType__c` |
 169 | InteractionID | `ssot__Id__c` |
 170 | Topic | `ssot__TopicApiName__c` |
 171 | StepType | `ssot__AiAgentInteractionStepType__c` |
 172 | ActionName | `ssot__Name__c` |
 173 | MessageType | `ssot__AiAgentInteractionMessageType__c` |
 174 | Content | `ssot__ContentText__c` |
