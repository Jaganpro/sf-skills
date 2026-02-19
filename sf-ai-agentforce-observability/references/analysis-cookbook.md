<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Analysis Cookbook
   2 
   3 Common analysis patterns using Polars for session tracing data.
   4 
   5 ## Getting Started
   6 
   7 ```python
   8 from pathlib import Path
   9 import polars as pl
  10 
  11 # Load data as lazy frames (memory efficient)
  12 data_dir = Path("./stdm_data")
  13 
  14 sessions = pl.scan_parquet(data_dir / "sessions" / "**/*.parquet")
  15 interactions = pl.scan_parquet(data_dir / "interactions" / "**/*.parquet")
  16 steps = pl.scan_parquet(data_dir / "steps" / "**/*.parquet")
  17 messages = pl.scan_parquet(data_dir / "messages" / "**/*.parquet")
  18 ```
  19 
  20 ---
  21 
  22 ## Session Analysis
  23 
  24 ### Basic Statistics
  25 
  26 ```python
  27 # Session count by agent
  28 sessions.group_by("ssot__AiAgentApiName__c").agg(
  29     pl.count().alias("session_count")
  30 ).sort("session_count", descending=True).collect()
  31 ```
  32 
  33 ### Completion Rate by Agent
  34 
  35 ```python
  36 sessions.group_by("ssot__AiAgentApiName__c").agg([
  37     pl.count().alias("total"),
  38     pl.col("ssot__AiAgentSessionEndType__c")
  39       .filter(pl.col("ssot__AiAgentSessionEndType__c") == "Completed")
  40       .count().alias("completed")
  41 ]).with_columns([
  42     (pl.col("completed") / pl.col("total") * 100).round(1).alias("completion_rate")
  43 ]).collect()
  44 ```
  45 
  46 ### Session Duration Analysis
  47 
  48 ```python
  49 # Note: Requires timestamp parsing
  50 sessions.with_columns([
  51     pl.col("ssot__StartTimestamp__c").str.to_datetime().alias("start"),
  52     pl.col("ssot__EndTimestamp__c").str.to_datetime().alias("end"),
  53 ]).with_columns([
  54     (pl.col("end") - pl.col("start")).alias("duration")
  55 ]).group_by("ssot__AiAgentApiName__c").agg([
  56     pl.col("duration").mean().alias("avg_duration"),
  57     pl.col("duration").max().alias("max_duration"),
  58 ]).collect()
  59 ```
  60 
  61 ---
  62 
  63 ## Interaction Analysis
  64 
  65 ### Turns per Session
  66 
  67 ```python
  68 turns_per_session = (
  69     interactions
  70     .filter(pl.col("ssot__AiAgentInteractionType__c") == "TURN")
  71     .group_by("ssot__AiAgentSessionId__c")
  72     .agg(pl.count().alias("turn_count"))
  73 )
  74 
  75 # Distribution
  76 turns_per_session.group_by("turn_count").agg(
  77     pl.count().alias("sessions")
  78 ).sort("turn_count").collect()
  79 ```
  80 
  81 ### Topic Routing
  82 
  83 ```python
  84 # Most common topics
  85 interactions.filter(
  86     pl.col("ssot__AiAgentInteractionType__c") == "TURN"
  87 ).group_by("ssot__TopicApiName__c").agg(
  88     pl.count().alias("turn_count"),
  89     pl.col("ssot__AiAgentSessionId__c").n_unique().alias("session_count")
  90 ).sort("turn_count", descending=True).collect()
  91 ```
  92 
  93 ### Topic Switches (Multi-Topic Sessions)
  94 
  95 ```python
  96 # Sessions that used multiple topics
  97 topic_counts = (
  98     interactions
  99     .filter(pl.col("ssot__AiAgentInteractionType__c") == "TURN")
 100     .group_by("ssot__AiAgentSessionId__c")
 101     .agg(pl.col("ssot__TopicApiName__c").n_unique().alias("topic_count"))
 102 )
 103 
 104 # Sessions with 2+ topics
 105 topic_counts.filter(pl.col("topic_count") > 1).collect()
 106 ```
 107 
 108 ---
 109 
 110 ## Step Analysis
 111 
 112 ### LLM vs Action Ratio
 113 
 114 ```python
 115 steps.group_by("ssot__AiAgentInteractionStepType__c").agg(
 116     pl.count().alias("count")
 117 ).with_columns([
 118     (pl.col("count") / pl.col("count").sum() * 100).round(1).alias("percentage")
 119 ]).collect()
 120 ```
 121 
 122 ### Most Used Actions
 123 
 124 ```python
 125 steps.filter(
 126     pl.col("ssot__AiAgentInteractionStepType__c") == "ACTION_STEP"
 127 ).group_by("ssot__Name__c").agg(
 128     pl.count().alias("invocations")
 129 ).sort("invocations", descending=True).head(20).collect()
 130 ```
 131 
 132 ### Steps per Turn Distribution
 133 
 134 ```python
 135 steps_per_turn = (
 136     steps
 137     .group_by("ssot__AiAgentInteractionId__c")
 138     .agg(pl.count().alias("step_count"))
 139 )
 140 
 141 steps_per_turn.group_by("step_count").agg(
 142     pl.count().alias("turns")
 143 ).sort("step_count").collect()
 144 ```
 145 
 146 ### Action Input/Output Analysis
 147 
 148 ```python
 149 # Parse JSON in action inputs (example for specific action)
 150 action_steps = steps.filter(
 151     (pl.col("ssot__AiAgentInteractionStepType__c") == "ACTION_STEP") &
 152     (pl.col("ssot__Name__c") == "Get_Order_Status")
 153 ).collect()
 154 
 155 # Parse inputs
 156 import json
 157 for row in action_steps.iter_rows(named=True):
 158     input_data = json.loads(row["ssot__InputValueText__c"] or "{}")
 159     output_data = json.loads(row["ssot__OutputValueText__c"] or "{}")
 160     print(f"Input: {input_data}, Output: {output_data}")
 161 ```
 162 
 163 ---
 164 
 165 ## Message Analysis
 166 
 167 ### Message Length Distribution
 168 
 169 ```python
 170 messages.with_columns([
 171     pl.col("ssot__ContentText__c").str.len_chars().alias("length")
 172 ]).group_by("ssot__AiAgentInteractionMessageType__c").agg([
 173     pl.col("length").mean().alias("avg_length"),
 174     pl.col("length").max().alias("max_length"),
 175 ]).collect()
 176 ```
 177 
 178 ### Common User Phrases
 179 
 180 ```python
 181 # Word frequency in user messages (simple)
 182 user_messages = messages.filter(
 183     pl.col("ssot__AiAgentInteractionMessageType__c") == "INPUT"
 184 ).select("ssot__ContentText__c").collect()
 185 
 186 # Count words
 187 from collections import Counter
 188 words = Counter()
 189 for row in user_messages.iter_rows(named=True):
 190     content = row["ssot__ContentText__c"] or ""
 191     words.update(content.lower().split())
 192 
 193 print(words.most_common(20))
 194 ```
 195 
 196 ---
 197 
 198 ## Time-Based Analysis
 199 
 200 ### Sessions by Date
 201 
 202 ```python
 203 sessions.with_columns([
 204     pl.col("ssot__StartTimestamp__c").str.slice(0, 10).alias("date")
 205 ]).group_by("date").agg(
 206     pl.count().alias("sessions")
 207 ).sort("date").collect()
 208 ```
 209 
 210 ### Sessions by Hour
 211 
 212 ```python
 213 sessions.with_columns([
 214     pl.col("ssot__StartTimestamp__c").str.slice(11, 2).alias("hour")
 215 ]).group_by("hour").agg(
 216     pl.count().alias("sessions")
 217 ).sort("hour").collect()
 218 ```
 219 
 220 ### Day of Week Analysis
 221 
 222 ```python
 223 # Requires datetime conversion
 224 sessions.with_columns([
 225     pl.col("ssot__StartTimestamp__c")
 226       .str.to_datetime()
 227       .dt.weekday()
 228       .alias("weekday")
 229 ]).group_by("weekday").agg(
 230     pl.count().alias("sessions")
 231 ).sort("weekday").collect()
 232 ```
 233 
 234 ---
 235 
 236 ## Debugging Patterns
 237 
 238 ### Find Failed Sessions
 239 
 240 ```python
 241 failed = sessions.filter(
 242     pl.col("ssot__AiAgentSessionEndType__c").is_in(["Escalated", "Abandoned", "Failed"])
 243 ).sort("ssot__StartTimestamp__c", descending=True).collect()
 244 
 245 for row in failed.head(5).iter_rows(named=True):
 246     print(f"Session: {row['ssot__Id__c']}")
 247     print(f"  Agent: {row['ssot__AiAgentApiName__c']}")
 248     print(f"  End: {row['ssot__AiAgentSessionEndType__c']}")
 249     print()
 250 ```
 251 
 252 ### Session Timeline Reconstruction
 253 
 254 ```python
 255 def get_timeline(session_id: str) -> pl.DataFrame:
 256     """Reconstruct message timeline for a session."""
 257     # Get interaction IDs
 258     interaction_df = interactions.filter(
 259         pl.col("ssot__AiAgentSessionId__c") == session_id
 260     ).collect()
 261 
 262     interaction_ids = interaction_df["ssot__Id__c"].to_list()
 263 
 264     # Get messages
 265     msg_df = messages.filter(
 266         pl.col("ssot__AiAgentInteractionId__c").is_in(interaction_ids)
 267     ).sort("ssot__MessageSentTimestamp__c").collect()
 268 
 269     return msg_df
 270 
 271 # Usage
 272 timeline = get_timeline("a0x1234567890ABC")
 273 for row in timeline.iter_rows(named=True):
 274     msg_type = row["ssot__AiAgentInteractionMessageType__c"]
 275     content = row["ssot__ContentText__c"]
 276     icon = "→" if msg_type == "INPUT" else "←"
 277     print(f"{icon} {content[:100]}...")
 278 ```
 279 
 280 ---
 281 
 282 ## Performance Tips
 283 
 284 ### Use Lazy Evaluation
 285 
 286 ```python
 287 # Good: Lazy evaluation, deferred execution
 288 result = (
 289     sessions
 290     .filter(pl.col("ssot__AiAgentApiName__c") == "My_Agent")
 291     .group_by("ssot__AiAgentSessionEndType__c")
 292     .agg(pl.count())
 293     .collect()  # Execute here
 294 )
 295 
 296 # Avoid: Eager loading of everything
 297 df = pl.read_parquet(data_dir / "sessions" / "**/*.parquet")  # Loads all data
 298 result = df.filter(...)  # Then filter
 299 ```
 300 
 301 ### Select Only Needed Columns
 302 
 303 ```python
 304 # Good: Select specific columns
 305 sessions.select([
 306     "ssot__Id__c",
 307     "ssot__AiAgentApiName__c",
 308     "ssot__AiAgentSessionEndType__c"
 309 ]).collect()
 310 
 311 # Avoid: Select all columns
 312 sessions.collect()  # Includes all columns
 313 ```
 314 
 315 ### Use Streaming for Large Results
 316 
 317 ```python
 318 # For very large datasets
 319 for batch in sessions.collect(streaming=True):
 320     # Process batch
 321     pass
 322 ```
