<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Analysis Examples
   2 
   3 Examples for analyzing extracted STDM data with Polars and the CLI.
   4 
   5 ---
   6 
   7 ## CLI Analysis Commands
   8 
   9 ### Summary Statistics
  10 
  11 Get high-level overview of extracted data:
  12 
  13 ```bash
  14 stdm-extract analyze --data-dir ./stdm_data
  15 ```
  16 
  17 **Output:**
  18 ```
  19 📊 SESSION SUMMARY
  20 ═══════════════════════════════════════════════════════════
  21 
  22 Agent                        Sessions  Completed  Escalated  Completion %
  23 ───────────────────────────────────────────────────────────────────────────
  24 Customer_Support_Agent           450        382         45        84.9%
  25 Order_Tracking_Agent             312        298          8        95.5%
  26 FAQ_Agent                        156        152          2        97.4%
  27 ───────────────────────────────────────────────────────────────────────────
  28 TOTAL                            918        832         55        90.6%
  29 ```
  30 
  31 ### Topic Analysis
  32 
  33 See which topics handle the most turns:
  34 
  35 ```bash
  36 stdm-extract topics --data-dir ./stdm_data
  37 ```
  38 
  39 **Output:**
  40 ```
  41 📊 TOPIC ROUTING
  42 ═══════════════════════════════════════════════════════════
  43 
  44 Topic                        Turns  Sessions  Avg Turns/Session
  45 ───────────────────────────────────────────────────────────────
  46 Order_Status                  1234       312              4.0
  47 Return_Policy                  856       245              3.5
  48 Account_Help                   654       198              3.3
  49 General_FAQ                    432       156              2.8
  50 ```
  51 
  52 ### Action Analysis
  53 
  54 See which actions are invoked most:
  55 
  56 ```bash
  57 stdm-extract actions --data-dir ./stdm_data
  58 ```
  59 
  60 **Output:**
  61 ```
  62 📊 ACTION INVOCATIONS
  63 ═══════════════════════════════════════════════════════════
  64 
  65 Action                       Count  Avg/Session
  66 ─────────────────────────────────────────────────
  67 Get_Order_Status              1856         2.0
  68 Search_Knowledge_Base         1245         1.4
  69 Create_Case                    567         0.6
  70 Update_Contact                 234         0.3
  71 ```
  72 
  73 ---
  74 
  75 ## Python Analysis
  76 
  77 ### Setup
  78 
  79 ```python
  80 import polars as pl
  81 from pathlib import Path
  82 
  83 data_dir = Path("./stdm_data")
  84 
  85 # Lazy loading (memory efficient)
  86 sessions = pl.scan_parquet(data_dir / "sessions" / "**/*.parquet")
  87 interactions = pl.scan_parquet(data_dir / "interactions" / "**/*.parquet")
  88 steps = pl.scan_parquet(data_dir / "steps" / "**/*.parquet")
  89 messages = pl.scan_parquet(data_dir / "messages" / "**/*.parquet")
  90 ```
  91 
  92 ### Session Analysis
  93 
  94 **Sessions by End Type:**
  95 ```python
  96 sessions.group_by("ssot__AiAgentSessionEndType__c").agg(
  97     pl.count().alias("count")
  98 ).sort("count", descending=True).collect()
  99 ```
 100 
 101 **Daily Session Trend:**
 102 ```python
 103 sessions.with_columns(
 104     pl.col("ssot__StartTimestamp__c").str.slice(0, 10).alias("date")
 105 ).group_by("date").agg(
 106     pl.count().alias("sessions")
 107 ).sort("date").collect()
 108 ```
 109 
 110 **Hourly Distribution:**
 111 ```python
 112 sessions.with_columns(
 113     pl.col("ssot__StartTimestamp__c").str.slice(11, 2).alias("hour")
 114 ).group_by("hour").agg(
 115     pl.count().alias("sessions")
 116 ).sort("hour").collect()
 117 ```
 118 
 119 ### Turn Analysis
 120 
 121 **Turns Per Session:**
 122 ```python
 123 turns_per_session = (
 124     interactions
 125     .filter(pl.col("ssot__AiAgentInteractionType__c") == "TURN")
 126     .group_by("ssot__AiAgentSessionId__c")
 127     .agg(pl.count().alias("turns"))
 128 )
 129 
 130 # Distribution
 131 turns_per_session.group_by("turns").agg(
 132     pl.count().alias("sessions")
 133 ).sort("turns").collect()
 134 ```
 135 
 136 **Multi-Topic Sessions (Topic Switches):**
 137 ```python
 138 topic_counts = (
 139     interactions
 140     .filter(pl.col("ssot__AiAgentInteractionType__c") == "TURN")
 141     .group_by("ssot__AiAgentSessionId__c")
 142     .agg(pl.col("ssot__TopicApiName__c").n_unique().alias("topics"))
 143 )
 144 
 145 # Sessions with 2+ topics
 146 topic_counts.filter(pl.col("topics") > 1).collect()
 147 ```
 148 
 149 ### Step Analysis
 150 
 151 **LLM vs Action Ratio:**
 152 ```python
 153 steps.group_by("ssot__AiAgentInteractionStepType__c").agg(
 154     pl.count().alias("count")
 155 ).with_columns(
 156     (pl.col("count") / pl.col("count").sum() * 100).round(1).alias("percent")
 157 ).collect()
 158 ```
 159 
 160 **Most Used Actions:**
 161 ```python
 162 steps.filter(
 163     pl.col("ssot__AiAgentInteractionStepType__c") == "ACTION_STEP"
 164 ).group_by("ssot__Name__c").agg(
 165     pl.count().alias("invocations")
 166 ).sort("invocations", descending=True).head(10).collect()
 167 ```
 168 
 169 **Steps Per Turn:**
 170 ```python
 171 steps.group_by("ssot__AiAgentInteractionId__c").agg(
 172     pl.count().alias("steps")
 173 ).group_by("steps").agg(
 174     pl.count().alias("turns")
 175 ).sort("steps").collect()
 176 ```
 177 
 178 ### Message Analysis
 179 
 180 **Average Message Length by Type:**
 181 ```python
 182 messages.with_columns(
 183     pl.col("ssot__ContentText__c").str.len_chars().alias("length")
 184 ).group_by("ssot__AiAgentInteractionMessageType__c").agg([
 185     pl.col("length").mean().round(0).alias("avg_length"),
 186     pl.col("length").max().alias("max_length"),
 187 ]).collect()
 188 ```
 189 
 190 **Common User Phrases:**
 191 ```python
 192 user_msgs = messages.filter(
 193     pl.col("ssot__AiAgentInteractionMessageType__c") == "INPUT"
 194 ).select("ssot__ContentText__c").collect()
 195 
 196 from collections import Counter
 197 words = Counter()
 198 for row in user_msgs.iter_rows(named=True):
 199     text = row["ssot__ContentText__c"] or ""
 200     words.update(text.lower().split())
 201 
 202 print(words.most_common(20))
 203 ```
 204 
 205 ---
 206 
 207 ## Using the Analyzer Class
 208 
 209 The skill includes a helper class for common analyses:
 210 
 211 ```python
 212 from scripts.analyzer import STDMAnalyzer
 213 
 214 analyzer = STDMAnalyzer(Path("./stdm_data"))
 215 
 216 # Quick summary
 217 summary = analyzer.session_summary()
 218 print(summary)
 219 
 220 # Step breakdown
 221 steps_df = analyzer.step_distribution()
 222 print(steps_df)
 223 
 224 # Topic patterns
 225 topics_df = analyzer.topic_analysis()
 226 print(topics_df)
 227 
 228 # Find failed sessions
 229 failed = analyzer.find_failed_sessions(limit=10)
 230 print(failed)
 231 ```
 232 
 233 ---
 234 
 235 ## Exporting Results
 236 
 237 ### To CSV
 238 ```python
 239 result = sessions.group_by(...).agg(...).collect()
 240 result.write_csv("output.csv")
 241 ```
 242 
 243 ### To JSON
 244 ```python
 245 result.write_json("output.json")
 246 ```
 247 
 248 ### To Parquet (for further analysis)
 249 ```python
 250 result.write_parquet("output.parquet")
 251 ```
 252 
 253 ---
 254 
 255 ## Visualization (with Matplotlib)
 256 
 257 ```python
 258 import matplotlib.pyplot as plt
 259 
 260 # Daily trend
 261 daily = sessions.with_columns(
 262     pl.col("ssot__StartTimestamp__c").str.slice(0, 10).alias("date")
 263 ).group_by("date").agg(
 264     pl.count().alias("sessions")
 265 ).sort("date").collect()
 266 
 267 plt.figure(figsize=(12, 4))
 268 plt.bar(daily["date"], daily["sessions"])
 269 plt.xticks(rotation=45)
 270 plt.title("Sessions per Day")
 271 plt.tight_layout()
 272 plt.savefig("daily_trend.png")
 273 ```
 274 
 275 ---
 276 
 277 ## See Also
 278 
 279 - [Polars Cheatsheet](../references/polars-cheatsheet.md) - Quick reference
 280 - [Analysis Cookbook](../references/analysis-cookbook.md) - More recipes
 281 - [Debugging Sessions](debugging-sessions.md) - Session-level debugging
