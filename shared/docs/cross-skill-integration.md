# Cross-Skill Integration Reference

## Quick Reference Table

| From Skill | To Skill | When | Example |
|------------|----------|------|---------|
| sf-apex | sf-metadata | Discover object/fields before coding | "Describe Invoice__c" |
| sf-apex | sf-data | Generate test records (251+) | "Create 251 Accounts for bulk testing" |
| sf-apex | sf-deploy | Deploy and run tests | "Deploy with RunLocalTests" |
| sf-flow | sf-metadata | Verify object structure | "Describe Invoice__c fields" |
| sf-flow | sf-data | Generate trigger test data | "Create 200 Accounts with criteria X" |
| sf-flow | sf-deploy | Deploy and activate | "Deploy flow with --dry-run" |
| sf-data | sf-metadata | Discover object structure | "Describe Custom_Object__c fields" |
| sf-metadata | sf-deploy | Deploy metadata to org | "Deploy objects with --dry-run" |
| sf-ai-agentforce | sf-integration | External API actions for agents | "Create Named Credential for agent" |
| sf-ai-agentforce | sf-flow | Flow wrappers for HTTP/Apex | "Create HTTP Callout Flow" |
| sf-ai-agentforce | sf-apex | Business logic @InvocableMethod | "Create Apex for case creation" |
| sf-ai-agentforce | sf-deploy | Deploy and publish agent | "sf agent publish" |
| sf-integration | sf-connected-apps | OAuth Connected App | "Create Connected App for Named Credential" |
| sf-integration | sf-apex | Custom callout service | "Create Queueable callout class" |
| sf-integration | sf-deploy | Deploy integration metadata | "Deploy Named Credential + External Service" |
| sf-connected-apps | sf-deploy | Deploy auth config | "Deploy Connected App + Permission Set" |

## Installation

All skills are optional and independent. Install as needed:
```
/plugin install github:Jaganpro/sf-skills/sf-deploy
/plugin install github:Jaganpro/sf-skills/sf-metadata
/plugin install github:Jaganpro/sf-skills/sf-data
/plugin install github:Jaganpro/sf-skills/sf-apex
/plugin install github:Jaganpro/sf-skills/sf-flow
/plugin install github:Jaganpro/sf-skills/sf-ai-agentforce
/plugin install github:Jaganpro/sf-skills/sf-integration
/plugin install github:Jaganpro/sf-skills/sf-connected-apps
```

## Invocation Pattern

```
Skill(skill="sf-[name]")
Request: "[your request]"
```

---

## Integration Skill Chain Examples

### Example 1: Agent with External API

User request: "Create an agent that can look up customer data from our CRM API"

```
Skill Chain:
1. sf-connected-apps → Create OAuth Connected App
2. sf-integration    → Create Named Credential for CRM API
3. sf-flow           → Create HTTP Callout Flow
4. sf-ai-agentforce  → Create Agent Script with flow:// action
5. sf-deploy         → Deploy all + sf agent publish
```

### Example 2: Agent with Complex Business Logic

User request: "Create an agent that calculates pricing with custom discount rules"

```
Skill Chain:
1. sf-apex           → Create @InvocableMethod with logic
2. sf-ai-agentforce  → Create GenAiFunction metadata
3. sf-deploy         → Deploy Apex + GenAiFunction
4. Add to agent topic via Agent Builder UI
```

### Example 3: Integration with Platform Events

User request: "Sync order data from external system via webhook"

```
Skill Chain:
1. sf-connected-apps → Create Connected App for webhook auth
2. sf-integration    → Create Platform Event definition
3. sf-apex           → Create event subscriber trigger
4. sf-deploy         → Deploy all metadata
```
