<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Session Tracing Data Model (STDM) Reference
   2 
   3 Complete documentation of the Agentforce Session Tracing Data Model stored in Salesforce Data Cloud.
   4 
   5 > **Source**: [Salesforce Help - Data Model for Agentforce Session Tracing](https://help.salesforce.com/s/articleView?id=ai.generative_ai_session_trace_data_model.htm)
   6 
   7 ## T6 Live API Discovery Summary ✅
   8 
   9 **Validated: January 30, 2026** | **24 DMOs Found** | **233+ Test Points**
  10 
  11 | Category | DMOs | Status | Notes |
  12 |----------|------|--------|-------|
  13 | **Session Tracing** | 5 | ✅ All Found | Session, Interaction, Step, Message, Participant |
  14 | **Agent Optimizer** | 6 | ✅ All Found | Moment, Tag system (5 DMOs) |
  15 | **GenAI Audit** | 13 | ✅ All Found | Generation, Quality, Feedback, Gateway |
  16 | **RAG Quality** | 3 | ❌ Not Found | GenAIRetriever* DMOs don't exist |
  17 
  18 **Key Discoveries:**
  19 - Field naming: API uses `AiAgent` (lowercase 'i'), not `AIAgent`
  20 - Agent name location: Stored on `Moment`, not `Session`
  21 - New channel types: `NGC`, `Voice`, `Builder: Voice Preview`
  22 - New agent types: `AgentforceEmployeeAgent`, `AgentforceServiceAgent`
  23 - GenAI detector types: `TOXICITY` (9 categories), `PII` (4 types), `PROMPT_DEFENSE`, `InstructionAdherence`
  24 
  25 ## Overview
  26 
  27 The STDM captures detailed telemetry from Agentforce agent conversations, enabling:
  28 - **Debugging**: Understand why an agent behaved a certain way
  29 - **Analytics**: Measure agent performance and usage patterns
  30 - **Optimization**: Identify bottlenecks and improvement opportunities
  31 
  32 The data model is a collection of DLOs (Data Lake Objects) and DMOs (Data Model Objects) that contain detailed session trace logs of agent behavior. Data is streamed to DLOs in Data 360 and then mapped to the applicable DMOs.
  33 
  34 ## Data Model Hierarchy
  35 
  36 The Agentforce Analytics data model consists of two main components:
  37 1. **Session Tracing Data Model** - Detailed turn-by-turn logs
  38 2. **Optimization Data Model** - Moments and tagging for analytics
  39 
  40 ### Session Tracing Data Model
  41 
  42 ```
  43 ┌─────────────────────────────────────────────────────────────────┐
  44 │                    AIAgentSession (Session)                     │
  45 │  One session = one complete conversation with an agent          │
  46 ├─────────────────────────────────────────────────────────────────┤
  47 │  ssot__Id__c                    Primary key                     │
  48 │  ssot__StartTimestamp__c        When session started            │
  49 │  ssot__EndTimestamp__c          When session ended              │
  50 │  ssot__AiAgentSessionEndType__c How session ended               │
  51 └──────────────────────┬──────────────────────────────────────────┘
  52                        │
  53      ┌─────────────────┼─────────────────┬───────────────────┐
  54      │ 1:N             │ 1:N             │ 1:N               │ 1:N
  55      ▼                 ▼                 ▼                   ▼
  56 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  57 │SessionParti- │ │ Interaction  │ │   Moment     │ │TagAssociation│
  58 │   cipant     │ │   (Turn)     │ │ (Summaries)  │ │    ✅ NEW    │
  59 ├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
  60 │AiAgentType   │ │ TURN /       │ │ Request/resp │ │ Links to     │
  61 │AiAgentApiName│ │ SESSION_END  │ │ summaries    │ │ TagDefinition│
  62 │Role          │ │ Topic routing│ │ Agent API    │ │ & Tag values │
  63 └──────────────┘ └──────┬───────┘ └──────┬───────┘ └──────────────┘
  64                         │                │
  65             ┌───────────┼────────────────┼─────── N:M junction
  66             │ 1:N       │ 1:N            ▼
  67             ▼           ▼         ┌──────────────┐
  68      ┌────────────┐ ┌────────────┐│MomentInter-  │
  69      │ Interaction│ │ Interaction││action ✅ NEW │
  70      │   Message  │ │    Step    │├──────────────┤
  71      ├────────────┤ ├────────────┤│Links Moment ↔│
  72      │ Input/     │ │ LLM_STEP   ││ Interaction  │
  73      │ Output     │ │ ACTION_STEP│└──────────────┘
  74      │ messages   │ │ TOPIC_STEP │
  75      └────────────┘ │ INTERRUPT  │
  76                     │ SESSION_END│
  77                     └─────┬──────┘
  78                           │
  79                           │ links via GenerationId
  80                           ▼
  81                   ┌────────────────┐
  82                   │ GenAIGeneration│
  83                   │ (Trust Layer)  │
  84                   └───────┬────────┘
  85                           │
  86                           ▼
  87                   ┌────────────────┐
  88                   │GenAIContent-   │
  89                   │ Quality        │
  90                   │ (Toxicity etc) │
  91                   └───────┬────────┘
  92                           │
  93                           ▼
  94                   ┌────────────────┐
  95                   │GenAIContent-   │
  96                   │ Category       │
  97                   │ (Detectors)    │
  98                   └────────────────┘
  99 ```
 100 
 101 **Key Relationships:**
 102 - Session has multiple Participants (user, agent, human handoff)
 103 - Session has multiple Interactions (turns)
 104 - Session has multiple Moments (summaries)
 105 - Each Interaction has Messages (actual user/agent text)
 106 - Each Interaction has Steps (processing logic)
 107 - Steps link to GenAIGeneration for quality metrics
 108 
 109 ## Entity Details
 110 
 111 ### AIAgentSession (ssot__AIAgentSession__dlm) ✅ T6 Verified
 112 
 113 Represents an overarching container capturing contiguous interactions with one or more AI agents. A typical session might start when the customer asks their first question and end when the customer closes the agent chat window. Contains **18 fields**.
 114 
 115 | Field API Name | Type | Description | Example |
 116 |----------------|------|-------------|---------|
 117 | `ssot__Id__c` | Text | Primary key - unique session identifier | `01999669-0a54-724f-80d6-9cb495a7cee4` |
 118 | `ssot__StartTimestamp__c` | DateTime | Timestamp when the session began | `2026-01-28T10:15:23.000Z` |
 119 | `ssot__EndTimestamp__c` | DateTime | Timestamp when the session concluded or timed out | `2026-01-28T10:19:55.000Z` |
 120 | `ssot__AiAgentChannelType__c` | Text | Type of communication channel (see table below) | `SCRT2 - EmbeddedMessaging` |
 121 | `ssot__AiAgentSessionEndType__c` | Text | How the session ended | `NOT_SET` |
 122 | `ssot__VariableText__c` | Text | Key-value pairs of contextual session data | `{}` |
 123 | `ssot__SessionOwnerId__c` | Text | ID of the participant who initiated the session | `0051234567890ABC` |
 124 | `ssot__SessionOwnerObject__c` | Text | Name of DMO for Session Owner | `Individual` |
 125 | `ssot__IndividualId__c` | Text (Lookup) | Reference to Individual record | `a0p...` |
 126 | `ssot__PreviousSessionId__c` | Text (Lookup) | Reference to previous session (multi-agent) | `a0x...` |
 127 | `ssot__RelatedMessagingSessionId__c` | Text | ID linking to messaging session origin ✅ | `5701234567890ABC` |
 128 | `ssot__RelatedVoiceCallId__c` | Text | ID linking to voice call origin ✅ | `0Lx...` |
 129 | `ssot__DataSourceId__c` | Text | Data source identifier | `null` |
 130 | `ssot__DataSourceObjectId__c` | Text | Data source object identifier | `...` |
 131 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `null` |
 132 | `KQ_Id__c` | Lookup | Key qualifier for ID | `null` |
 133 | `KQ_IndividualId__c` | Lookup | Key qualifier for Individual | `null` |
 134 | `KQ_PreviousSessionId__c` | Lookup | Key qualifier for PreviousSession | `null` |
 135 
 136 **Session End Types:**
 137 
 138 | Value | Description |
 139 |-------|-------------|
 140 | `Completed` | Session resolved successfully |
 141 | `Escalated` | Transferred to human agent |
 142 | `Abandoned` | User left without resolution |
 143 | `Failed` | Session failed due to error |
 144 | `NOT_SET` | End type not yet determined |
 145 
 146 **Channel Types (Live API Verified - T6 Discovery):**
 147 
 148 | Value | Occurrences | Description |
 149 |-------|-------------|-------------|
 150 | `E & O` | 13,894 | Einstein & Omni-Channel |
 151 | `Builder` | 1,546 | Agent Builder testing |
 152 | `SCRT2 - EmbeddedMessaging` | 957 | Embedded web messaging |
 153 | `LightningDesktopCopilot` | 63 | Desktop copilot integration |
 154 | `Voice` | 41 | Voice/speech channel |
 155 | `PSTN` | 41 | Phone/PSTN channel |
 156 | `Builder: Voice Preview` | 10 | Voice preview in Builder |
 157 | `NGC` | 2 | Next-Gen Cloud (internal) |
 158 
 159 ---
 160 
 161 ### AIAgentSessionParticipant (ssot__AIAgentSessionParticipant__dlm) ✅ Verified
 162 
 163 Represents an entity (human or AI) that takes part in an AIAgentSession.
 164 
 165 | Field API Name | Type | Description | Example |
 166 |----------------|------|-------------|---------|
 167 | `ssot__Id__c` | Text | Primary key | `a0p1234567890ABC` |
 168 | `ssot__AiAgentSessionId__c` | Text (Parent) | Reference to the specific AiAgentSession | `a0x1234567890ABC` |
 169 | `ssot__AiAgentType__c` | Text | Type of AI Agent | `EinsteinServiceAgent` |
 170 | `ssot__AiAgentTemplateApiName__c` | Text | Template used to create the agent | `Service_Agent_Template` |
 171 | `ssot__AiAgentApiName__c` | Text | API name of the AI agent (if participant is AI) | `Customer_Support_Agent` |
 172 | `ssot__AiAgentVersionApiName__c` | Text | API name of the AI agent version (if participant is AI) | `v1.2.3` |
 173 | `ssot__StartTimestamp__c` | DateTime | Timestamp when participant joined the session | `2026-01-28T10:15:23.000Z` |
 174 | `ssot__EndTimestamp__c` | DateTime | Timestamp when participant left/stopped interacting | `2026-01-28T10:19:55.000Z` |
 175 | `ssot__ParticipantId__c` | Text | Reference to the record representing the participant | `0051234567890ABC` |
 176 | `ssot__ParticipantObject__c` | Text | Name of DMO for the Participant record (e.g., `Individual`) | `Individual` |
 177 | `ssot__ParticipantAttributeText__c` | Text | JSON key-value pairs of participant metadata | `{}` |
 178 | `ssot__IndividualId__c` | Text (Lookup) | Reference to Individual if participant DMO is Individual | `a0i...` |
 179 | `ssot__AiAgentSessionParticipantRole__c` | Text | Role of participant within the session | `Owner` |
 180 | `ssot__ExternalSourceId__c` | Text | External system identifier for the participant | `ext-123` |
 181 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `00D...` |
 182 
 183 **AI Agent Types (Live API Verified - T6 Discovery):**
 184 
 185 | Value | Occurrences | Description |
 186 |-------|-------------|-------------|
 187 | `EinsteinServiceAgent` | 32,255 | Einstein Service Agent for customer support |
 188 | `AgentforceEmployeeAgent` | 314 | Agentforce agent for employee-facing use cases |
 189 | `AgentforceServiceAgent` | 171 | Agentforce service agent (newer platform) |
 190 | `Employee` | 84 | Generic employee-type agent |
 191 
 192 **Participant Roles (Live API Verified):**
 193 
 194 | Value | Occurrences | Description |
 195 |-------|-------------|-------------|
 196 | `USER` | 16,431 | End user participating in the session |
 197 | `AGENT` | 16,393 | AI agent participating in the session |
 198 
 199 ---
 200 
 201 ### AIAgentInteraction (ssot__AIAgentInteraction__dlm) ✅ T6 Verified
 202 
 203 Represents a segment within a session. It typically begins with a user's request and ends when the AI agent provides a response to that request. Contains **20 fields**. Discovery shows **3,536 records** in a 30-day window.
 204 
 205 | Field API Name | Type | Description | Example |
 206 |----------------|------|-------------|---------|
 207 | `ssot__Id__c` | Text | Primary key | `a0y1234567890ABC` |
 208 | `ssot__AiAgentSessionId__c` | Text (Parent) | Reference to the parent session | `a0x1234567890ABC` |
 209 | `ssot__AiAgentInteractionType__c` | Text | Interaction type (`TURN`, `SESSION_END`) | `TURN` |
 210 | `ssot__PrevInteractionId__c` | Text (Lookup) | Reference to previous interaction (enables sequencing) | `a0y...` |
 211 | `ssot__StartTimestamp__c` | DateTime | Timestamp when the interaction began | `2026-01-28T10:15:23.000Z` |
 212 | `ssot__EndTimestamp__c` | DateTime | Timestamp when the interaction completed | `2026-01-28T10:15:26.000Z` |
 213 | `ssot__TopicApiName__c` | Text | API name of the topic classified for this interaction | `Order_Tracking` |
 214 | `ssot__AttributeText__c` | Text | JSON key-value pairs of additional metadata | `{"confidence": 0.95}` |
 215 | `ssot__TelemetryTraceId__c` | Text | Identifier for distributed tracing (OpenTelemetry) | `abc123def456...` |
 216 | `ssot__TelemetryTraceSpanId__c` | Text | Span ID within distributed tracing context | `span_xyz...` |
 217 | `ssot__SessionOwnerId__c` | Text | ID of participant who initiated the session | `005...` |
 218 | `ssot__SessionOwnerObject__c` | Text | DMO name for Session Owner | `Individual` |
 219 | `ssot__IndividualId__c` | Text (Lookup) | Reference to Individual record | `a0i...` |
 220 | `ssot__DataSourceId__c` | Text | Data source identifier | `null` |
 221 | `ssot__DataSourceObjectId__c` | Text | Data source object identifier | `...` |
 222 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `null` |
 223 | `KQ_*` | Lookup | Key qualifier fields for relationships | `null` |
 224 
 225 **Interaction Types (Live API Verified):**
 226 
 227 | Value | Description |
 228 |-------|-------------|
 229 | `TURN` | Normal user input → agent response cycle |
 230 | `SESSION_END` | Final interaction marking session close |
 231 
 232 **OpenTelemetry Integration**: The `TelemetryTraceId` and `TelemetryTraceSpanId` fields enable distributed tracing across system components, supporting export to platforms like Datadog, Splunk, and other OTEL-compatible tools.
 233 
 234 ---
 235 
 236 ### AIAgentInteractionMessage (ssot__AiAgentInteractionMessage__dlm) ✅ T6 Verified
 237 
 238 Represents a single communication provided by the user or generated by the AI agent during a session. Contains **21 fields**.
 239 
 240 | Field API Name | Type | Description | Example |
 241 |----------------|------|-------------|---------|
 242 | `ssot__Id__c` | Text | Primary key | `a0i1234567890ABC` |
 243 | `ssot__AiAgentInteractionId__c` | Text (Parent) | Reference to the interaction | `a0y1234567890ABC` |
 244 | `ssot__AiAgentSessionId__c` | Text (Lookup) | Reference to the session | `a0x...` |
 245 | `ssot__AiAgentSessionParticipantId__c` | Text (Lookup) | Participant who sent the message | `a0p...` |
 246 | `ssot__AiAgentInteractionMessageType__c` | Text | Message direction (`Input`/`Output`) | `Input` |
 247 | `ssot__AiAgentInteractionMsgContentType__c` | Text | MIME content type | `text/plain` |
 248 | `ssot__ContentText__c` | Text | Textual content | `What is the status of my order?` |
 249 | `ssot__MessageSentTimestamp__c` | DateTime | Exact time when message was sent | `2026-01-28T10:15:23.000Z` |
 250 | `ssot__ParentMessageId__c` | Text (Lookup) | Parent message (for threads) | `a0i...` |
 251 | `ssot__SessionOwnerId__c` | Text | ID of session owner participant | `005...` |
 252 | `ssot__SessionOwnerObject__c` | Text | DMO name for Session Owner | `Individual` |
 253 | `ssot__IndividualId__c` | Text (Lookup) | Reference to Individual record | `a0i...` |
 254 | `ssot__DataSourceId__c` | Text | Data source identifier | `null` |
 255 | `ssot__DataSourceObjectId__c` | Text | Data source object identifier | `...` |
 256 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `null` |
 257 | `KQ_*` | Lookup | Key qualifier fields | `null` |
 258 
 259 **Message Types (Live API Verified):**
 260 
 261 | Value | Occurrences | Description |
 262 |-------|-------------|-------------|
 263 | `Input` | 16,428 | User message to agent |
 264 | `Output` | 16,390 | Agent response to user |
 265 
 266 **Content Types (Live API Verified):**
 267 
 268 | Value | Description |
 269 |-------|-------------|
 270 | `text/plain` | Plain text message |
 271 | `application/json` | JSON-formatted content |
 272 
 273 **Note:** InteractionMessage differs from Moment:
 274 - **InteractionMessage**: Raw user/agent text per turn with threading support
 275 - **Moment**: Summarized request/response with agent API name
 276 
 277 ---
 278 
 279 ### AIAgentInteractionStep (ssot__AIAgentInteractionStep__dlm) ✅ T6 Verified
 280 
 281 Represents a discrete action or operation performed during an interaction to fulfill the user's request. Contains **23 fields**. Discovery shows **12,318 records** in a 30-day window.
 282 
 283 | Field API Name | Type | Description | Example |
 284 |----------------|------|-------------|---------|
 285 | `ssot__Id__c` | Text | Primary key | `a0z1234567890ABC` |
 286 | `ssot__AiAgentInteractionId__c` | Text (Parent) | Reference to the interaction this step belongs to | `a0y1234567890ABC` |
 287 | `ssot__AiAgentInteractionStepType__c` | Text | Step type (see table below) | `LLM_STEP` |
 288 | `ssot__Name__c` | Text | Name of the step/action performed | `Get_Order_Status` |
 289 | `ssot__PrevStepId__c` | Text (Lookup) | Reference to previous step (linear sequencing) | `a0z...` |
 290 | `ssot__StartTimestamp__c` | DateTime | Timestamp when step execution began | `2026-01-28T10:15:23.000Z` |
 291 | `ssot__EndTimestamp__c` | DateTime | Timestamp when step execution completed | `2026-01-28T10:15:24.000Z` |
 292 | `ssot__InputValueText__c` | Text | Input data provided to the step (JSON) | `{"orderId": "12345"}` |
 293 | `ssot__OutputValueText__c` | Text | Output data resulting from step execution (JSON) | `{"status": "Shipped"}` |
 294 | `ssot__PreStepVariableText__c` | Text | State of variables before step execution | `{"customer_id": "C001"}` |
 295 | `ssot__PostStepVariableText__c` | Text | State of variables after step execution | `{"order_status": "Shipped"}` |
 296 | `ssot__ErrorMessageText__c` | Text | Error details if step encountered issues | `Action timeout after 30s` |
 297 | `ssot__AttributeText__c` | Text | JSON key-value pairs of additional metadata | `{"latency_ms": 150}` |
 298 | `ssot__GenerationId__c` | Text | Reference to GenAIGeneration (LLM steps) | `gen_abc123...` |
 299 | `ssot__GenAiGatewayRequestId__c` | Text | Reference to GenAIGatewayRequest (LLM steps) | `req_xyz...` |
 300 | `ssot__GenAiGatewayResponseId__c` | Text | Reference to GenAIGatewayResponse (LLM steps) | `resp_xyz...` |
 301 | `ssot__TelemetryTraceSpanId__c` | Text | Span ID for distributed tracing (OTEL) | `span_abc...` |
 302 | `ssot__DataSourceId__c` | Text | Data source identifier | `null` |
 303 | `ssot__DataSourceObjectId__c` | Text | Data source object identifier | `...` |
 304 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `null` |
 305 | `KQ_*` | Lookup | Key qualifier fields (Id, InteractionId, PrevStepId) | `null` |
 306 
 307 **Step Types (Live API Verified - T6 Discovery):**
 308 
 309 | Value | Occurrences | Description | When Used |
 310 |-------|-------------|-------------|-----------|
 311 | `LLM_STEP` | 67,163 | LLM call execution | Intent detection, response generation |
 312 | `TOPIC_STEP` | 16,236 | Topic classification/routing | Determining which topic handles the request |
 313 | `SESSION_END` | 14,990 | Session termination | Final step when session closes |
 314 | `ACTION_STEP` | 13,780 | Function/action execution | Calling flows, Apex actions |
 315 | `INTERRUPT_STEP` | 5 | Interrupt processing | Handling interruptions (rare) |
 316 
 317 **Common Step Names (Live API Verified):**
 318 
 319 | Step Name | Step Type | Description |
 320 |-----------|-----------|-------------|
 321 | `AiCopilot__ReactInitialPrompt` | LLM_STEP | Initial planning/reasoning step |
 322 | `AiCopilot__ReactTopicPrompt` | LLM_STEP | Topic classification/routing decision |
 323 | `AiCopilot__ReactValidationPrompt` | LLM_STEP | Response validation (hallucination check) |
 324 | `CLOSED_USER_REQUEST` | SESSION_END | Session termination by user request |
 325 | `flash_agent` | LLM_STEP | Flash agent LLM invocation |
 326 | `{Topic}.{Action}` | ACTION_STEP | Topic-specific actions (e.g., `Order_Status.Get_Order`) |
 327 
 328 **Step Naming Convention:**
 329 - LLM steps use format: `AiCopilot__{PromptName}` or `{agent_name}`
 330 - Action steps use format: `{TopicApiName}.{ActionApiName}`
 331 - Session end steps: `CLOSED_USER_REQUEST`, `ESCALATED`, etc.
 332 
 333 **Note:** Steps use linear sequencing via `PrevStepId`. There is no hierarchical parent-child relationship (no `ParentStepId` field).
 334 
 335 ---
 336 
 337 **GenAI Reference Fields:**
 338 
 339 The Step entity includes references to every LLM call the reasoning engine makes, enabling joins with feedback data or guardrails metrics:
 340 - `GenerationId` → Links to `GenAIGeneration__dlm` for quality analysis
 341 - `GenAiGatewayRequestId` → Links to `GenAIGatewayRequest__dlm` for prompts
 342 - `GenAiGatewayResponseId` → Links to `GenAIGatewayResponse__dlm` for raw responses
 343 
 344 ---
 345 
 346 ### AIAgentMoment (ssot__AiAgentMoment__dlm) ✅ T6 Verified
 347 
 348 Represents summarized request/response pairs for analytics and optimization. Contains **13 fields**. Note: The agent API name is stored here (not on Session).
 349 
 350 | Field API Name | Type | Description | Example |
 351 |----------------|------|-------------|---------|
 352 | `ssot__Id__c` | Text | Primary key | `a0m1234567890ABC` |
 353 | `ssot__AiAgentSessionId__c` | Text (Parent) | FK to parent session | `a0x1234567890ABC` |
 354 | `ssot__AiAgentApiName__c` | Text | API name of the agent | `Customer_Support_Agent` |
 355 | `ssot__AiAgentVersionApiName__c` | Text | Version of the agent | `v1.2.3` |
 356 | `ssot__RequestSummaryText__c` | Text | Summarized user request | `User asked about order status` |
 357 | `ssot__ResponseSummaryText__c` | Text | Summarized agent response | `Provided tracking info` |
 358 | `ssot__StartTimestamp__c` | DateTime | Moment start time | `2026-01-28T10:15:23.000Z` |
 359 | `ssot__EndTimestamp__c` | DateTime | Moment end time | `2026-01-28T10:15:26.000Z` |
 360 | `ssot__DataSourceId__c` | Text | Data source identifier | `null` |
 361 | `ssot__DataSourceObjectId__c` | Text | Data source object identifier | `null` |
 362 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `null` |
 363 | `KQ_*` | Lookup | Key qualifier fields | `null` |
 364 
 365 **Moment vs Message:**
 366 - **Moment**: High-level summaries with agent API name for analytics
 367 - **InteractionMessage**: Raw user/agent text per turn with threading support
 368 
 369 ---
 370 
 371 ### AIAgentMomentInteraction (ssot__AiAgentMomentInteraction__dlm) ✅ NEW
 372 
 373 Junction table linking Moments to Interactions, enabling many-to-many relationships between high-level summaries and detailed interaction data.
 374 
 375 | Field API Name | Type | Description | Example |
 376 |----------------|------|-------------|---------|
 377 | `ssot__Id__c` | Text | Primary key | `a0j1234567890ABC` |
 378 | `ssot__AiAgentMomentId__c` | Text (Lookup) | Reference to the Moment | `a0m...` |
 379 | `ssot__AiAgentInteractionId__c` | Text (Lookup) | Reference to the Interaction | `a0y...` |
 380 | `ssot__StartTimestamp__c` | DateTime | When this relationship was created | `2026-01-28T10:15:23.000Z` |
 381 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `00D...` |
 382 
 383 ---
 384 
 385 ### AIAgentTagDefinition (ssot__AiAgentTagDefinition__dlm) ✅ Verified
 386 
 387 Defines tag metadata and structure for the Agentforce tagging system.
 388 
 389 | Field API Name | Type | Description | Example |
 390 |----------------|------|-------------|---------|
 391 | `ssot__Id__c` | Text | Primary key | `a0t1234567890ABC` |
 392 | `ssot__Name__c` | Text | Display name of the tag definition | `Escalation_Reason` |
 393 | `ssot__DeveloperName__c` | Text | API-safe name of the tag definition | `Escalation_Reason` |
 394 | `ssot__Description__c` | Text | Description of what the tag represents | `Reason for agent escalation` |
 395 | `ssot__DataType__c` | Text | Data type of tag values | `Text` |
 396 | `ssot__SourceType__c` | Text | How the tag is populated | `Generated` |
 397 | `ssot__CreatedDate__c` | DateTime | When the definition was created | `2026-01-15T08:00:00.000Z` |
 398 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `00D...` |
 399 
 400 **SourceType Values (Live API Verified):**
 401 
 402 | Value | Description |
 403 |-------|-------------|
 404 | `Generated` | System-generated tags |
 405 | `Predefined` | Admin-defined tags |
 406 
 407 **DataType Values (Live API Verified):**
 408 
 409 | Value | Description |
 410 |-------|-------------|
 411 | `Text` | Text/string values |
 412 | `Integer` | Numeric values |
 413 
 414 ---
 415 
 416 ### AIAgentTag (ssot__AiAgentTag__dlm) ✅ Verified
 417 
 418 Stores individual tag values associated with tag definitions.
 419 
 420 | Field API Name | Type | Description | Example |
 421 |----------------|------|-------------|---------|
 422 | `ssot__Id__c` | Text | Primary key | `a0u1234567890ABC` |
 423 | `ssot__AiAgentTagDefinitionId__c` | Text (Lookup) | Reference to the tag definition | `a0t...` |
 424 | `ssot__Value__c` | Text | The tag value (e.g., rating, category code) | `5` |
 425 | `ssot__Description__c` | Text | Human-readable description of the tag | `Customer frustrated with wait time` |
 426 | `ssot__IsActive__c` | Boolean | Whether the tag is currently active | `true` |
 427 | `ssot__CreatedDate__c` | DateTime | When the tag was created | `2026-01-28T10:15:23.000Z` |
 428 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `00D...` |
 429 
 430 **Note:** The `Value` field typically contains numeric codes (1-5 for ratings) or short codes, while `Description` contains the human-readable explanation.
 431 
 432 ---
 433 
 434 ### AIAgentTagDefinitionAssociation (ssot__AiAgentTagDefinitionAssociation__dlm) ✅ Verified
 435 
 436 Links tag definitions to specific agents or prompt templates, defining which tags apply to which agent configurations.
 437 
 438 | Field API Name | Type | Description | Example |
 439 |----------------|------|-------------|---------|
 440 | `ssot__Id__c` | Text | Primary key | `a0w1234567890ABC` |
 441 | `ssot__AiAgentTagDefinitionId__c` | Text (Lookup) | Reference to the tag definition | `a0t...` |
 442 | `ssot__AiAgentApiName__c` | Text | API name of the agent this applies to | `Customer_Support_Agent` |
 443 | `ssot__AiPromptTemplateId__c` | Text (Lookup) | Reference to prompt template | `a0p...` |
 444 | `ssot__CreatedDate__c` | DateTime | When the association was created | `2026-01-15T08:00:00.000Z` |
 445 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `00D...` |
 446 
 447 **Use Cases:**
 448 - Define which tags are applicable to specific agents
 449 - Link tagging to prompt templates for automatic tag application
 450 - Configure agent-specific quality metrics
 451 
 452 ---
 453 
 454 ### AIAgentTagAssociation (ssot__AiAgentTagAssociation__dlm) ✅ Verified
 455 
 456 Links tags to sessions and moments, enabling flexible categorization of agent interactions. Contains 15 fields.
 457 
 458 | Field API Name | Type | Description | Example |
 459 |----------------|------|-------------|---------|
 460 | `ssot__Id__c` | Text | Primary key | `a0v1234567890ABC` |
 461 | `ssot__AiAgentSessionId__c` | Text (Lookup) | Reference to the session | `a0x...` |
 462 | `ssot__AiAgentMomentId__c` | Text (Lookup) | Reference to the moment | `a0m...` |
 463 | `ssot__AiAgentTagDefinitionAssociationId__c` | Text (Lookup) | Reference to tag definition association | `a0w...` |
 464 | `ssot__AiAgentTagId__c` | Text (Lookup) | Direct reference to the tag value ✅ NEW | `a0u...` |
 465 | `ssot__AssociationReasonText__c` | Text | Reason/context for the tag association ✅ NEW | `User expressed frustration` |
 466 | `ssot__CreatedDate__c` | DateTime | When the association was created | `2026-01-28T10:15:23.000Z` |
 467 | `ssot__DataSourceId__c` | Text | Data source identifier | `null` |
 468 | `ssot__DataSourceObjectId__c` | Text | Data source object identifier | `null` |
 469 | `ssot__InternalOrganizationId__c` | Text | Internal org identifier | `null` |
 470 | `KQ_*` | Lookup | Key qualifier fields for relationships | `null` |
 471 
 472 **Use Cases:**
 473 - Categorize sessions by customer sentiment
 474 - Tag escalation reasons for analytics
 475 - Apply business-specific labels to conversations
 476 - Track tagging rationale via `AssociationReasonText`
 477 
 478 ---
 479 
 480 ## GenAI Audit & Feedback DMOs ✅ T6 Verified
 481 
 482 The GenAI Trust Layer provides comprehensive tracking of LLM calls, quality metrics, and safety detections.
 483 
 484 ### GenAIGeneration (GenAIGeneration__dlm)
 485 
 486 Records individual LLM generations. Contains 11 fields.
 487 
 488 | Field API Name | Type | Description |
 489 |----------------|------|-------------|
 490 | `generationId__c` | Text | Primary key for joining with Steps |
 491 | `generationResponseId__c` | Text | Response identifier |
 492 | `responseText__c` | Text | Raw LLM response text |
 493 | `maskedResponseText__c` | Text | PII-masked version of response |
 494 | `responseParameters__c` | Text | Model parameters used |
 495 | `feature__c` | Text | Feature that triggered generation |
 496 | `cloud__c` | Text | Cloud identifier |
 497 | `orgId__c` | Text | Organization ID |
 498 | `timestamp__c` | DateTime | Generation timestamp |
 499 
 500 ### GenAIContentQuality (GenAIContentQuality__dlm)
 501 
 502 Quality assessment for each generation. Contains 10 fields.
 503 
 504 | Field API Name | Type | Description |
 505 |----------------|------|-------------|
 506 | `id__c` | Text | Primary key |
 507 | `parent__c` | Text | FK to GenAIGeneration.generationId__c |
 508 | `contentType__c` | Text | Type of content assessed |
 509 | `isToxicityDetected__c` | Boolean | Overall toxicity flag |
 510 | `feature__c` | Text | Feature identifier |
 511 | `cloud__c` | Text | Cloud identifier |
 512 | `orgId__c` | Text | Organization ID |
 513 | `timestamp__c` | DateTime | Assessment timestamp |
 514 
 515 ### GenAIContentCategory (GenAIContentCategory__dlm)
 516 
 517 Detailed detector results per quality assessment. Contains 10 fields.
 518 
 519 | Field API Name | Type | Description |
 520 |----------------|------|-------------|
 521 | `id__c` | Text | Primary key |
 522 | `parent__c` | Text | FK to GenAIContentQuality.id__c |
 523 | `detectorType__c` | Text | Detector type (see table below) |
 524 | `category__c` | Text | Detection category/result |
 525 | `value__c` | Text | Confidence score (0.0-1.0) |
 526 | `cloud__c` | Text | Cloud identifier |
 527 | `orgId__c` | Text | Organization ID |
 528 | `timestamp__c` | DateTime | Detection timestamp |
 529 
 530 **Detector Types (Live API Verified - T6 Discovery):**
 531 
 532 | Detector Type | Occurrences | Categories |
 533 |---------------|-------------|------------|
 534 | `TOXICITY` | 627,603 | `hate`, `identity`, `physical`, `profanity`, `safety_score`, `sexual`, `toxicity`, `violence`, `0` |
 535 | `PROMPT_DEFENSE` | 119,050 | `aggregatePromptAttackScore`, `isPromptAttackDetected`, `0`, `1` |
 536 | `PII` | 27,805 | `CREDIT_CARD`, `EMAIL_ADDRESS`, `PERSON`, `US_PHONE_NUMBER` |
 537 | `InstructionAdherence` | 16,380 | `High`, `Low`, `Uncertain` |
 538 
 539 ### GenAIGatewayRequest (GenAIGatewayRequest__dlm)
 540 
 541 Request details for LLM calls. Contains 30 fields (largest DMO).
 542 
 543 | Field API Name | Type | Description |
 544 |----------------|------|-------------|
 545 | `gatewayRequestId__c` | Text | Primary key |
 546 | `prompt__c` | Text | Full prompt sent to LLM |
 547 | `maskedPrompt__c` | Text | PII-masked prompt |
 548 | `model__c` | Text | Model name (e.g., `gpt-4`) |
 549 | `provider__c` | Text | Model provider |
 550 | `temperature__c` | Number | Temperature parameter |
 551 | `promptTokens__c` | Number | Input token count |
 552 | `completionTokens__c` | Number | Output token count |
 553 | `totalTokens__c` | Number | Total tokens |
 554 | `promptTemplateDevName__c` | Text | Prompt template developer name |
 555 | `promptTemplateVersionNo__c` | Text | Prompt template version |
 556 | `enableInputSafetyScoring__c` | Text | Input safety enabled flag |
 557 | `enableOutputSafetyScoring__c` | Text | Output safety enabled flag |
 558 | `enablePiiMasking__c` | Text | PII masking enabled flag |
 559 | `sessionId__c` | Text | Related session ID |
 560 | `userId__c` | Text | User who triggered request |
 561 | `appType__c` | Text | Application type |
 562 | `feature__c` | Text | Feature identifier |
 563 
 564 ### GenAIGatewayResponse (GenAIGatewayResponse__dlm)
 565 
 566 Response metadata for LLM calls. Contains 8 fields.
 567 
 568 | Field API Name | Type | Description |
 569 |----------------|------|-------------|
 570 | `generationRequestId__c` | Text | FK to GatewayRequest |
 571 | `generationResponseId__c` | Text | Response identifier |
 572 | `parameters__c` | Text | Response parameters JSON |
 573 | `cloud__c` | Text | Cloud identifier |
 574 | `orgId__c` | Text | Organization ID |
 575 | `timestamp__c` | DateTime | Response timestamp |
 576 
 577 ### GenAIFeedback (GenAIFeedback__dlm)
 578 
 579 User feedback on LLM responses. Contains 16 fields.
 580 
 581 | Field API Name | Type | Description |
 582 |----------------|------|-------------|
 583 | `feedbackId__c` | Text | Primary key |
 584 | `generationId__c` | Text | FK to Generation |
 585 | `feedback__c` | Text | Feedback value (e.g., `GOOD`) |
 586 | `action__c` | Text | User action taken |
 587 | `source__c` | Text | Feedback source |
 588 | `userId__c` | Text | User who gave feedback |
 589 | `appType__c` | Text | Application type |
 590 | `feature__c` | Text | Feature identifier |
 591 | `timestamp__c` | DateTime | Feedback timestamp |
 592 
 593 **Feedback Values:**
 594 
 595 | Value | Description |
 596 |-------|-------------|
 597 | `GOOD` | Positive feedback (thumbs up) |
 598 | `BAD` | Negative feedback (thumbs down) |
 599 
 600 ### GenAIFeedbackDetail (GenAIFeedbackDetail__dlm)
 601 
 602 Detailed feedback with free-text comments. Contains 10 fields.
 603 
 604 | Field API Name | Type | Description |
 605 |----------------|------|-------------|
 606 | `feedbackDetailId__c` | Text | Primary key |
 607 | `parent__c` | Text | FK to Feedback |
 608 | `feedbackText__c` | Text | Free-text feedback comment |
 609 | `appFeedback__c` | Text | App-specific feedback |
 610 | `feature__c` | Text | Feature identifier |
 611 
 612 ### Other GenAI DMOs
 613 
 614 | DMO Name | Fields | Description |
 615 |----------|--------|-------------|
 616 | `GenAIAppGeneration__dlm` | 10 | Application-level generation records |
 617 | `GenAIGatewayRequestTag__dlm` | 9 | Tags for gateway requests |
 618 | `GenAIGtwyRequestMetadata__dlm` | 10 | Request metadata (type, JSON) |
 619 | `GenAIGtwyObjRecord__dlm` | 13 | Object record references |
 620 | `GenAIGtwyObjRecCitationRef__dlm` | 9 | Citation references |
 621 | `GenAIGtwyRequestLLM__dlm` | 0 | LLM-specific request data (empty) |
 622 
 623 ### RAG Quality DMOs ❌ NOT FOUND
 624 
 625 The following DMOs were probed but **do not exist** in the live API:
 626 
 627 | DMO Name | Status | Notes |
 628 |----------|--------|-------|
 629 | `GenAIRetrieverResponse__dlm` | ❌ Not Found | Table does not exist |
 630 | `GenAIRetrieverRequest__dlm` | ❌ Not Found | Table does not exist |
 631 | `GenAIRetrieverQualityMetric__dlm` | ❌ Not Found | Table does not exist |
 632 
 633 > **Note:** These DMOs may be available in future API versions or require specific enablement.
 634 
 635 ---
 636 
 637 ## Data Relationships
 638 
 639 ```sql
 640 -- Session → Interactions
 641 SELECT i.*
 642 FROM ssot__AIAgentInteraction__dlm i
 643 WHERE i.ssot__AiAgentSessionId__c = 'SESSION_ID';
 644 
 645 -- Interaction → Steps
 646 SELECT s.*
 647 FROM ssot__AIAgentInteractionStep__dlm s
 648 WHERE s.ssot__AiAgentInteractionId__c = 'INTERACTION_ID';
 649 
 650 -- Interaction → Messages
 651 SELECT m.*
 652 FROM ssot__AIAgentMoment__dlm m
 653 WHERE m.ssot__AiAgentInteractionId__c = 'INTERACTION_ID';
 654 ```
 655 
 656 ---
 657 
 658 ## Data Volume Considerations
 659 
 660 | Scenario | Sessions/Day | Total Records/Day |
 661 |----------|--------------|-------------------|
 662 | Low volume | 100-1K | 10K-100K |
 663 | Medium volume | 1K-10K | 100K-1M |
 664 | High volume | 10K-100K | 1M-10M |
 665 | Enterprise | 100K+ | 10M+ |
 666 
 667 **Estimation Formula:**
 668 ```
 669 Total records ≈ Sessions × Avg turns × (1 + Avg steps + 2)
 670 Example: 10K sessions × 4 turns × 5 = 200K records
 671 ```
 672 
 673 ---
 674 
 675 ## Data Retention
 676 
 677 Session tracing data in Data Cloud follows the org's data retention policy. Default:
 678 - **Production**: 13 months
 679 - **Sandbox**: 30 days
 680 
 681 ---
 682 
 683 ## Enabling Session Tracing
 684 
 685 1. **Setup** → **Agentforce** → **Settings**
 686 2. Enable **Session Tracing**
 687 3. Configure which agents to trace
 688 4. Wait 5-15 minutes for data to appear in Data Cloud
 689 
 690 ---
 691 
 692 ## Related Resources
 693 
 694 - [Query Patterns](query-patterns.md) - Example queries
 695 - [Analysis Cookbook](analysis-cookbook.md) - Common analysis patterns
 696 - [Troubleshooting](troubleshooting.md) - Common issues
