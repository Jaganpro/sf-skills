<!-- Parent: sf-ai-agentscript/SKILL.md -->

# Architecture Patterns

## Pattern 1: Hub and Spoke
Central router (hub) to specialized topics (spokes). Use for multi-purpose agents.
```
       ┌─────────────┐
       │ topic_sel   │
       │   (hub)     │
       └──────┬──────┘
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│refunds │ │ orders │ │support │
└────────┘ └────────┘ └────────┘
```

## Pattern 2: Verification Gate
Security gate before protected topics. Mandatory for sensitive data.
```
┌─────────┐     ┌──────────┐     ┌───────────┐
│  entry  │ ──▶ │ VERIFY   │ ──▶ │ protected │
└─────────┘     │  (GATE)  │     │  topics   │
                └────┬─────┘     └───────────┘
                     │ 3 fails
                     ▼
                ┌──────────┐
                │ lockout  │
                └──────────┘
```

## Pattern 3: Post-Action Loop
Topic re-resolves after action completes - put checks at TOP.
```yaml
topic refund:
  reasoning:
    instructions: ->
      # POST-ACTION CHECK (at TOP - triggers on next loop)
      if @variables.refund_status == "Approved":
        run @actions.create_crm_case
        transition to @topic.success

      # PRE-LLM DATA LOADING
      run @actions.check_churn_risk
      set @variables.risk = @outputs.score

      # DYNAMIC INSTRUCTIONS FOR LLM
      if @variables.risk >= 80:
        | Offer full refund to retain customer.
      else:
        | Offer $10 credit instead.
```
