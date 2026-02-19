<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Polars Cheatsheet
   2 
   3 Quick reference for analyzing STDM data with Polars.
   4 
   5 ## Loading Data
   6 
   7 ```python
   8 import polars as pl
   9 from pathlib import Path
  10 
  11 data_dir = Path("./stdm_data")
  12 
  13 # Lazy loading (recommended for large datasets)
  14 sessions = pl.scan_parquet(data_dir / "sessions" / "**/*.parquet")
  15 interactions = pl.scan_parquet(data_dir / "interactions" / "**/*.parquet")
  16 steps = pl.scan_parquet(data_dir / "steps" / "**/*.parquet")
  17 messages = pl.scan_parquet(data_dir / "messages" / "**/*.parquet")
  18 
  19 # Eager loading (loads everything into memory)
  20 sessions_df = pl.read_parquet(data_dir / "sessions" / "**/*.parquet")
  21 ```
  22 
  23 ---
  24 
  25 ## Basic Operations
  26 
  27 ### Count Records
  28 ```python
  29 sessions.select(pl.count()).collect()
  30 # Or
  31 len(sessions.collect())
  32 ```
  33 
  34 ### View Schema
  35 ```python
  36 sessions.collect_schema()
  37 ```
  38 
  39 ### Preview Data
  40 ```python
  41 sessions.head(5).collect()
  42 sessions.fetch(5)  # Faster, doesn't scan full file
  43 ```
  44 
  45 ### Select Columns
  46 ```python
  47 sessions.select([
  48     "ssot__Id__c",
  49     "ssot__AiAgentApiName__c",
  50     "ssot__AiAgentSessionEndType__c"
  51 ]).collect()
  52 ```
  53 
  54 ---
  55 
  56 ## Filtering
  57 
  58 ### Single Condition
  59 ```python
  60 sessions.filter(pl.col("ssot__AiAgentApiName__c") == "My_Agent")
  61 ```
  62 
  63 ### Multiple Conditions (AND)
  64 ```python
  65 sessions.filter(
  66     (pl.col("ssot__AiAgentApiName__c") == "My_Agent") &
  67     (pl.col("ssot__AiAgentSessionEndType__c") == "Completed")
  68 )
  69 ```
  70 
  71 ### Multiple Conditions (OR)
  72 ```python
  73 sessions.filter(
  74     pl.col("ssot__AiAgentSessionEndType__c").is_in(["Escalated", "Failed"])
  75 )
  76 ```
  77 
  78 ### Null Checks
  79 ```python
  80 sessions.filter(pl.col("ssot__EndTimestamp__c").is_not_null())
  81 sessions.filter(pl.col("ssot__EndTimestamp__c").is_null())
  82 ```
  83 
  84 ### String Contains
  85 ```python
  86 messages.filter(pl.col("ssot__ContentText__c").str.contains("order"))
  87 ```
  88 
  89 ---
  90 
  91 ## Aggregation
  92 
  93 ### Group By with Count
  94 ```python
  95 sessions.group_by("ssot__AiAgentApiName__c").agg(
  96     pl.count().alias("session_count")
  97 ).sort("session_count", descending=True).collect()
  98 ```
  99 
 100 ### Multiple Aggregations
 101 ```python
 102 sessions.group_by("ssot__AiAgentApiName__c").agg([
 103     pl.count().alias("total"),
 104     pl.col("ssot__AiAgentSessionEndType__c")
 105       .filter(pl.col("ssot__AiAgentSessionEndType__c") == "Completed")
 106       .count().alias("completed")
 107 ]).collect()
 108 ```
 109 
 110 ### Unique Count
 111 ```python
 112 interactions.group_by("ssot__AiAgentSessionId__c").agg(
 113     pl.col("ssot__TopicApiName__c").n_unique().alias("topic_count")
 114 ).collect()
 115 ```
 116 
 117 ---
 118 
 119 ## Joins
 120 
 121 ### Inner Join
 122 ```python
 123 sessions.join(
 124     interactions,
 125     left_on="ssot__Id__c",
 126     right_on="ssot__AiAgentSessionId__c",
 127     how="inner"
 128 )
 129 ```
 130 
 131 ### Left Join
 132 ```python
 133 sessions.join(
 134     interactions,
 135     left_on="ssot__Id__c",
 136     right_on="ssot__AiAgentSessionId__c",
 137     how="left"
 138 )
 139 ```
 140 
 141 ---
 142 
 143 ## Date/Time Operations
 144 
 145 ### Parse Timestamp
 146 ```python
 147 sessions.with_columns(
 148     pl.col("ssot__StartTimestamp__c").str.to_datetime().alias("start_dt")
 149 )
 150 ```
 151 
 152 ### Extract Date Parts
 153 ```python
 154 sessions.with_columns([
 155     pl.col("ssot__StartTimestamp__c").str.slice(0, 10).alias("date"),
 156     pl.col("ssot__StartTimestamp__c").str.slice(11, 2).alias("hour"),
 157 ])
 158 ```
 159 
 160 ### Date Filtering
 161 ```python
 162 sessions.filter(
 163     pl.col("ssot__StartTimestamp__c") >= "2026-01-01T00:00:00.000Z"
 164 )
 165 ```
 166 
 167 ---
 168 
 169 ## Computed Columns
 170 
 171 ### Add Column
 172 ```python
 173 sessions.with_columns(
 174     (pl.col("completed") / pl.col("total") * 100).round(1).alias("completion_rate")
 175 )
 176 ```
 177 
 178 ### String Length
 179 ```python
 180 messages.with_columns(
 181     pl.col("ssot__ContentText__c").str.len_chars().alias("msg_length")
 182 )
 183 ```
 184 
 185 ### Conditional Column
 186 ```python
 187 sessions.with_columns(
 188     pl.when(pl.col("ssot__AiAgentSessionEndType__c") == "Completed")
 189       .then(pl.lit("Success"))
 190       .otherwise(pl.lit("Failure"))
 191       .alias("outcome")
 192 )
 193 ```
 194 
 195 ---
 196 
 197 ## Sorting
 198 
 199 ### Single Column
 200 ```python
 201 sessions.sort("ssot__StartTimestamp__c", descending=True)
 202 ```
 203 
 204 ### Multiple Columns
 205 ```python
 206 sessions.sort(["ssot__AiAgentApiName__c", "ssot__StartTimestamp__c"])
 207 ```
 208 
 209 ---
 210 
 211 ## Output
 212 
 213 ### Collect (Execute)
 214 ```python
 215 result = sessions.filter(...).collect()  # Returns DataFrame
 216 ```
 217 
 218 ### Write Parquet
 219 ```python
 220 result.write_parquet("output.parquet")
 221 ```
 222 
 223 ### Write CSV
 224 ```python
 225 result.write_csv("output.csv")
 226 ```
 227 
 228 ### To Python Dict
 229 ```python
 230 result.to_dicts()  # List of dicts
 231 result.row(0, named=True)  # Single row as dict
 232 ```
 233 
 234 ---
 235 
 236 ## Performance Tips
 237 
 238 ### 1. Use Lazy Evaluation
 239 ```python
 240 # Good: Lazy, optimized query plan
 241 result = (
 242     pl.scan_parquet(path)
 243     .filter(...)
 244     .group_by(...)
 245     .agg(...)
 246     .collect()
 247 )
 248 
 249 # Avoid: Eager, loads everything
 250 df = pl.read_parquet(path)
 251 result = df.filter(...)
 252 ```
 253 
 254 ### 2. Select Early
 255 ```python
 256 # Good: Only load needed columns
 257 sessions.select(["ssot__Id__c", "ssot__AiAgentApiName__c"]).filter(...)
 258 
 259 # Avoid: Load all, filter later
 260 sessions.filter(...).select(...)
 261 ```
 262 
 263 ### 3. Filter Before Join
 264 ```python
 265 # Good: Filter before joining
 266 filtered_sessions = sessions.filter(pl.col("ssot__AiAgentApiName__c") == "My_Agent")
 267 filtered_sessions.join(interactions, ...)
 268 
 269 # Avoid: Join everything, then filter
 270 sessions.join(interactions, ...).filter(...)
 271 ```
 272 
 273 ### 4. Use Streaming for Large Results
 274 ```python
 275 # For very large datasets
 276 sessions.collect(streaming=True)
 277 ```
 278 
 279 ---
 280 
 281 ## Common Patterns
 282 
 283 ### Session Statistics
 284 ```python
 285 sessions.group_by("ssot__AiAgentApiName__c").agg([
 286     pl.count().alias("sessions"),
 287     pl.col("ssot__AiAgentSessionEndType__c")
 288       .filter(pl.col("ssot__AiAgentSessionEndType__c") == "Completed")
 289       .count().alias("completed"),
 290     pl.col("ssot__AiAgentSessionEndType__c")
 291       .filter(pl.col("ssot__AiAgentSessionEndType__c") == "Escalated")
 292       .count().alias("escalated"),
 293 ]).collect()
 294 ```
 295 
 296 ### Daily Trend
 297 ```python
 298 sessions.with_columns(
 299     pl.col("ssot__StartTimestamp__c").str.slice(0, 10).alias("date")
 300 ).group_by("date").agg(
 301     pl.count().alias("sessions")
 302 ).sort("date").collect()
 303 ```
 304 
 305 ### Top N Actions
 306 ```python
 307 steps.filter(
 308     pl.col("ssot__AiAgentInteractionStepType__c") == "ACTION_STEP"
 309 ).group_by("ssot__Name__c").agg(
 310     pl.count().alias("invocations")
 311 ).sort("invocations", descending=True).head(10).collect()
 312 ```
 313 
 314 ---
 315 
 316 ## See Also
 317 
 318 - [Analysis Cookbook](../references/analysis-cookbook.md) - Full recipes
 319 - [Polars Documentation](https://docs.pola.rs/)
