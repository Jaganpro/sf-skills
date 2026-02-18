<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->

# Analysis Examples

## Session Summary

```
📊 SESSION SUMMARY
════════════════════════════════════════════════════════════════

Period: 2026-01-21 to 2026-01-28
Total Sessions: 15,234
Unique Agents: 3

SESSIONS BY AGENT
────────────────────────────────────────────────────────────────
Agent                          │ Sessions │ Avg Turns │ Avg Duration
───────────────────────────────┼──────────┼───────────┼─────────────
Customer_Support_Agent         │   8,502  │    4.2    │     3m 15s
Order_Tracking_Agent           │   4,128  │    2.8    │     1m 45s
Product_FAQ_Agent              │   2,604  │    1.9    │       45s

END TYPE DISTRIBUTION
────────────────────────────────────────────────────────────────
✅ Completed:    12,890 (84.6%)
🔄 Escalated:     1,523 (10.0%)
❌ Abandoned:       821 (5.4%)
```

## Debug Session Timeline

```
🔍 SESSION DEBUG: a0x1234567890ABC
════════════════════════════════════════════════════════════════

Agent: Customer_Support_Agent
Started: 2026-01-28 10:15:23 UTC
Duration: 4m 32s
End Type: Completed
Turns: 5

TIMELINE
────────────────────────────────────────────────────────────────
10:15:23 │ [INPUT]  "I need help with my order #12345"
10:15:24 │ [TOPIC]  → Order_Tracking (confidence: 0.95)
10:15:24 │ [STEP]   LLM_STEP: Identify intent
10:15:25 │ [STEP]   ACTION_STEP: Get_Order_Status
         │          Input: {"orderId": "12345"}
         │          Output: {"status": "Shipped", "eta": "2026-01-30"}
10:15:26 │ [OUTPUT] "Your order #12345 has shipped and will arrive by Jan 30."

10:16:01 │ [INPUT]  "Can I change the delivery address?"
10:16:02 │ [TOPIC]  → Order_Tracking (same topic)
10:16:02 │ [STEP]   LLM_STEP: Clarify request
10:16:03 │ [STEP]   ACTION_STEP: Check_Modification_Eligibility
         │          Input: {"orderId": "12345", "type": "address_change"}
         │          Output: {"eligible": false, "reason": "Already shipped"}
10:16:04 │ [OUTPUT] "I'm sorry, the order has already shipped..."
```
