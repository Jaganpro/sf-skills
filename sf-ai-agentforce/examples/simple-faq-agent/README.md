# Simple FAQ Agent Example

A minimal working example of an Agentforce agent using Agent Script.

## Overview

This agent demonstrates the simplest possible Agentforce implementation:
- Pure LLM reasoning (no external actions)
- Single FAQ topic with clear instructions
- Proper topic navigation
- Session state tracking via variables

## Files

```
simple-faq-agent/
├── Simple_FAQ_Agent.agentscript    # The agent definition
└── README.md                        # This file
```

## Key Features

| Feature | Implementation |
|---------|----------------|
| Entry point | `start_agent topic_selector` |
| Main topic | `topic faq_handler` |
| Exit topic | `topic farewell` |
| Variables | `user_question`, `conversation_topic`, `question_count` |
| Actions | Topic transitions only (no external integrations) |

## Agent Structure

```
topic_selector (entry)
    ↓
faq_handler (main)
    ↓         ↓
topic_selector  farewell (exit)
(loop back)
```

## Deployment

### 1. Copy to your Salesforce DX project

```bash
mkdir -p force-app/main/default/aiAuthoringBundles/Simple_FAQ_Agent
cp Simple_FAQ_Agent.agentscript force-app/main/default/aiAuthoringBundles/Simple_FAQ_Agent/
```

### 2. Generate agent version

```bash
sf agent generate version --name Simple_FAQ_Agent --target-org your-org-alias
```

### 3. Preview the agent

```bash
sf agent preview --name Simple_FAQ_Agent --target-org your-org-alias
```

### 4. Activate when ready

```bash
sf agent activate version --name Simple_FAQ_Agent --version-number 1 --target-org your-org-alias
```

## Customization Ideas

### Add specific FAQ topics

```agentscript
variables:
    faq_category: mutable string = ""
        description: "Category of FAQ (shipping, returns, billing)"

start_agent topic_selector:
    reasoning:
        actions:
            shipping_faq: @utils.transition to @topic.shipping_faq
                description: "Shipping questions"
            returns_faq: @utils.transition to @topic.returns_faq
                description: "Return policy questions"
```

### Add an external action

```agentscript
topic order_lookup:
    actions:
        get_order_status:
            description: "Look up order status"
            inputs:
                order_id: string
                    description: "Order ID"
            outputs:
                status: string
                    description: "Current status"
            target: "flow://Get_Order_Status"

    reasoning:
        actions:
            check_order: @actions.get_order_status
                with order_id=...
                set @variables.order_status = @outputs.status
```

## Validation

Run the validator to check the agent:

```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-agentforce/hooks/scripts/validate_agentforce.py Simple_FAQ_Agent.agentscript
```

Expected output:
```
Score: 95/100 ⭐⭐⭐⭐⭐ Excellent
├─ Structure & Syntax: 20/20 (100%)
├─ Topic Design: 20/20 (100%)
├─ Action Integration: 20/20 (100%)
├─ Variable Management: 15/15 (100%)
├─ Instructions Quality: 15/15 (100%)
└─ Security & Guardrails: 5/10 (50%)

Issues:
⚠️ [Security & Guardrails] Consider adding more specific guardrails
```

## Requirements

- API Version: 64.0+ (Summer '25 or later)
- Licenses: Agentforce (Default), Einstein Prompt Templates
