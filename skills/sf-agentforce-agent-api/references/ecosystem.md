# Agentforce Developer Ecosystem

Quick-reference map of all Agentforce APIs, SDKs, and developer tools.

> Official docs: [Get Started with Agentforce APIs and SDKs](https://developer.salesforce.com/docs/ai/agentforce/guide/get-started-agents.html)

## Tools at a Glance

| Tool | What It Does | Access |
|------|-------------|--------|
| [Agent API](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-api-get-started.html) | Chat with agents via REST — sessions, messages, streaming | REST API |
| [Agent Script](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-script.html) | Build agents with natural language + programmatic expressions | Agentforce Builder |
| [Agentforce DX](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx.html) | Pro-code CLI/VS Code tools for agents | SF CLI |
| [Python SDK](https://github.com/salesforce/agent-sdk/tree/main) | Programmatic agent creation and management | Python |
| [Testing API](https://developer.salesforce.com/docs/ai/agentforce/guide/testing-api-get-started.html) | Automated test evaluation at scale | REST/Metadata API |
| [Mobile SDK](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk.html) | Native agent UI for iOS, Android, React Native | SDK |
| [Enhanced Chat v2](https://developer.salesforce.com/docs/ai/agentforce/guide/get-started-enhanced-chat.html) | Web chat for Service Cloud | JavaScript |
| [In-App Chat SDK](https://developer.salesforce.com/docs/service/messaging-in-app/guide/introduction.html) | Mobile chat for Service Cloud | SDK |

## Build vs Test vs Use

| Tool | Build | Test | Use |
|------|-------|------|-----|
| Agent Script | Yes | | |
| Agentforce DX | Yes | Yes | Yes (preview) |
| Python SDK | Yes | | |
| Testing API | | Yes | |
| Agent API | | | Yes |
| Mobile SDK | | | Yes |
| Enhanced Chat v2 | | | Yes |
| In-App Chat SDK | | | Yes |

## Agent Builders

Salesforce has two agent builders:

**New Agentforce Builder** (Canvas/Script view):
- Access: App Launcher → Agentforce Studio
- Features: AI assistance, Agent Script support, configurable canvas
- Agent ID: Query `BotDefinition` via SOQL

**Legacy Agentforce Builder** (visual topic editor):
- Access: Setup → Agentforce Agents
- Agent ID: 18-char ID from URL

## Building Actions

Actions are the building blocks for agent capabilities:
- [Build and Enhance Agentforce Actions](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-actions.html)
- Call agents from Flows or Apex via invocable actions

## Learning Resources

- [Trailhead: Agents and Agentforce Basics](https://trailhead.salesforce.com/)
- [Salesforce Help: Agentforce Agents](https://help.salesforce.com/s/articleView?id=ai.copilot_intro.htm)
- [YouTube: Integrate Agentforce with Microsoft Teams](https://www.youtube.com/watch?v=cbIOq_rQang)
- [Postman Collection](https://www.postman.com/salesforce-developers/salesforce-developers/collection/gwv9bjy/agent-api)
