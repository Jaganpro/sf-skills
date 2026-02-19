<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Debugging Sessions
   2 
   3 Examples for debugging specific agent sessions using STDM data.
   4 
   5 ---
   6 
   7 ## Finding Sessions to Debug
   8 
   9 ### List Failed/Escalated Sessions
  10 
  11 ```bash
  12 stdm-extract debug-session --data-dir ./stdm_data --list-failed
  13 ```
  14 
  15 **Output:**
  16 ```
  17 Failed/Escalated Sessions (last 10)
  18 ═══════════════════════════════════════════════════════════
  19 
  20 🔄 a0x001 | Customer_Support_Agent | Escalated | 2026-01-28T10:15
  21 ❌ a0x002 | Order_Tracking_Agent   | Failed    | 2026-01-28T09:45
  22 🔄 a0x003 | Customer_Support_Agent | Escalated | 2026-01-28T08:30
  23 ...
  24 
  25 To debug a session, run:
  26   stdm-extract debug-session --data-dir ./stdm_data --session-id <ID>
  27 ```
  28 
  29 ### Find via Python
  30 
  31 ```python
  32 import polars as pl
  33 from pathlib import Path
  34 
  35 sessions = pl.scan_parquet(Path("./stdm_data/sessions/**/*.parquet"))
  36 
  37 # Failed/escalated sessions
  38 failed = sessions.filter(
  39     pl.col("ssot__AiAgentSessionEndType__c").is_in(["Escalated", "Failed", "Abandoned"])
  40 ).sort("ssot__StartTimestamp__c", descending=True).head(10).collect()
  41 
  42 for row in failed.iter_rows(named=True):
  43     print(f"{row['ssot__Id__c']} | {row['ssot__AiAgentApiName__c']} | {row['ssot__AiAgentSessionEndType__c']}")
  44 ```
  45 
  46 ---
  47 
  48 ## Debug a Specific Session
  49 
  50 ### Basic Timeline
  51 
  52 ```bash
  53 stdm-extract debug-session --data-dir ./stdm_data --session-id "a0x001"
  54 ```
  55 
  56 **Output:**
  57 ```
  58 🔍 SESSION TIMELINE
  59 ══════════════════════════════════════════════════════════════════════
  60 
  61 Session: a0x001
  62 Agent: Customer_Support_Agent
  63 Started: 2026-01-28T10:15:23.000Z
  64 Ended: 2026-01-28T10:19:55.000Z
  65 End Type: Escalated
  66 
  67 ──────────────────────────────────────────────────────────────────────
  68 Timeline
  69 ──────────────────────────────────────────────────────────────────────
  70 
  71 ═══ Topic: Order_Status ═══
  72 
  73 2026-01-28T10:15:23 → [INPUT]
  74    Where is my order #12345?
  75 
  76 2026-01-28T10:15:26 ← [OUTPUT]
  77    I can help you track your order. Let me look that up for you.
  78    Your order #12345 was shipped on January 25th and is expected...
  79 
  80 ═══ Topic: Return_Policy ═══
  81 
  82 2026-01-28T10:16:45 → [INPUT]
  83    I want to return it, it's damaged
  84 
  85 2026-01-28T10:16:48 ← [OUTPUT]
  86    I'm sorry to hear that. I can help you start a return. However, I
  87    need to transfer you to a specialist for damaged items...
  88 
  89 ═══ Topic: Escalation ═══
  90 
  91 2026-01-28T10:17:02 → [INPUT]
  92    Yes, please transfer me
  93 
  94 2026-01-28T10:17:05 ← [OUTPUT]
  95    I'm transferring you to a customer service representative now.
  96 ```
  97 
  98 ### Verbose Mode (Show Steps)
  99 
 100 See LLM reasoning and action details:
 101 
 102 ```bash
 103 stdm-extract debug-session --data-dir ./stdm_data --session-id "a0x001" --verbose
 104 ```
 105 
 106 **Output (with steps):**
 107 ```
 108 2026-01-28T10:15:23 → [INPUT]
 109    Where is my order #12345?
 110 
 111          🧠 [LLM_STEP] Intent Detection
 112          ⚡ [ACTION_STEP] Get_Order_Status
 113             Input: {"orderId": "12345"}
 114             Output: {"status": "Shipped", "carrier": "UPS", "tracking": "1Z..."}
 115          🧠 [LLM_STEP] Response Generation
 116 
 117 2026-01-28T10:15:26 ← [OUTPUT]
 118    I can help you track your order...
 119 ```
 120 
 121 ### Export to JSON
 122 
 123 For sharing or further analysis:
 124 
 125 ```bash
 126 stdm-extract debug-session --data-dir ./stdm_data \
 127     --session-id "a0x001" \
 128     --verbose \
 129     --output ./debug/session_a0x001.json
 130 ```
 131 
 132 **JSON structure:**
 133 ```json
 134 {
 135   "session": {
 136     "id": "a0x001",
 137     "agent": "Customer_Support_Agent",
 138     "start": "2026-01-28T10:15:23.000Z",
 139     "end": "2026-01-28T10:19:55.000Z",
 140     "end_type": "Escalated"
 141   },
 142   "timeline": [
 143     {
 144       "type": "interaction",
 145       "timestamp": "2026-01-28T10:15:23.000Z",
 146       "interaction_id": "a0y001",
 147       "topic": "Order_Status"
 148     },
 149     {
 150       "type": "message",
 151       "timestamp": "2026-01-28T10:15:23.000Z",
 152       "message_type": "INPUT",
 153       "content": "Where is my order #12345?"
 154     },
 155     {
 156       "type": "step",
 157       "step_type": "ACTION_STEP",
 158       "name": "Get_Order_Status",
 159       "input": "{\"orderId\": \"12345\"}",
 160       "output": "{\"status\": \"Shipped\"...}"
 161     }
 162   ]
 163 }
 164 ```
 165 
 166 ---
 167 
 168 ## Using the Python Template
 169 
 170 For custom timeline analysis:
 171 
 172 ```bash
 173 python3 assets/analysis/message-timeline.py \
 174     --data-dir ./stdm_data \
 175     --session-id "a0x001" \
 176     --verbose
 177 ```
 178 
 179 ---
 180 
 181 ## Debug Patterns
 182 
 183 ### Pattern 1: Why Did It Escalate?
 184 
 185 Look for:
 186 1. **Topic switches** - Did topics change unexpectedly?
 187 2. **Action failures** - Did an action return an error?
 188 3. **User frustration** - Repeated similar inputs?
 189 
 190 ```python
 191 # Find the last few messages before escalation
 192 timeline = analyzer.message_timeline("a0x001")
 193 print(timeline.tail(10))
 194 ```
 195 
 196 ### Pattern 2: Action Failure Analysis
 197 
 198 ```python
 199 # Find action steps with error outputs
 200 steps = pl.read_parquet("./stdm_data/steps/data.parquet")
 201 
 202 failed_actions = steps.filter(
 203     (pl.col("ssot__AiAgentInteractionStepType__c") == "ACTION_STEP") &
 204     (pl.col("ssot__OutputValueText__c").str.contains("error|Error|ERROR"))
 205 )
 206 
 207 print(failed_actions.select(["ssot__Name__c", "ssot__OutputValueText__c"]))
 208 ```
 209 
 210 ### Pattern 3: Long Sessions
 211 
 212 Sessions with many turns often indicate problems:
 213 
 214 ```python
 215 interactions = pl.read_parquet("./stdm_data/interactions/data.parquet")
 216 
 217 long_sessions = interactions.filter(
 218     pl.col("ssot__AiAgentInteractionType__c") == "TURN"
 219 ).group_by("ssot__AiAgentSessionId__c").agg(
 220     pl.count().alias("turns")
 221 ).filter(pl.col("turns") > 10).collect()
 222 
 223 print(f"Sessions with 10+ turns: {len(long_sessions)}")
 224 ```
 225 
 226 ### Pattern 4: Compare Successful vs Failed
 227 
 228 ```python
 229 sessions = pl.read_parquet("./stdm_data/sessions/data.parquet")
 230 interactions = pl.read_parquet("./stdm_data/interactions/data.parquet")
 231 
 232 # Join and compare
 233 joined = sessions.join(
 234     interactions.group_by("ssot__AiAgentSessionId__c").agg(
 235         pl.count().alias("turns")
 236     ),
 237     left_on="ssot__Id__c",
 238     right_on="ssot__AiAgentSessionId__c"
 239 )
 240 
 241 print(joined.group_by("ssot__AiAgentSessionEndType__c").agg([
 242     pl.col("turns").mean().alias("avg_turns"),
 243     pl.count().alias("sessions")
 244 ]))
 245 ```
 246 
 247 ---
 248 
 249 ## Bulk Session Debug
 250 
 251 ### Export Multiple Sessions
 252 
 253 ```python
 254 from pathlib import Path
 255 import json
 256 
 257 session_ids = ["a0x001", "a0x002", "a0x003"]
 258 output_dir = Path("./debug")
 259 output_dir.mkdir(exist_ok=True)
 260 
 261 for sid in session_ids:
 262     timeline = get_timeline(data, sid)
 263     session_info = get_session_info(data, sid)
 264 
 265     with open(output_dir / f"{sid}.json", "w") as f:
 266         json.dump({
 267             "session": session_info,
 268             "timeline": timeline
 269         }, f, indent=2)
 270 
 271     print(f"Exported {sid}")
 272 ```
 273 
 274 ---
 275 
 276 ## Tips
 277 
 278 1. **Start with list-failed**: Find problem sessions quickly
 279 2. **Use verbose mode**: Steps reveal why the agent took certain actions
 280 3. **Export to JSON**: For sharing with team or deeper analysis
 281 4. **Look at topic switches**: Unexpected changes often indicate confusion
 282 5. **Check action outputs**: Failed actions are a common escalation cause
 283 
 284 ---
 285 
 286 ## See Also
 287 
 288 - [Analysis Examples](analysis-examples.md) - Aggregate analysis
 289 - [Troubleshooting](../references/troubleshooting.md) - Common issues
 290 - [Data Model Reference](../references/data-model-reference.md) - STDM schema
