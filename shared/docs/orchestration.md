# Multi-Skill Orchestration Order

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CORRECT MULTI-SKILL ORCHESTRATION ORDER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. sf-metadata  → Create object/field definitions (LOCAL files)            │
│  2. sf-flow      → Create flow definitions (LOCAL files)                    │
│  3. sf-deploy    → Deploy all metadata to org (REMOTE)                      │
│  4. sf-data      → Create test data (REMOTE - objects must exist!)          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Why Order Matters

| Step | Depends On | Fails If Wrong Order |
|------|------------|---------------------|
| sf-flow | sf-metadata | Flow references non-existent field |
| sf-deploy | sf-metadata, sf-flow | Nothing to deploy |
| sf-data | sf-deploy | `SObject type 'X' not supported` |

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `SObject type 'X' not supported` | Object not deployed | Run sf-deploy first |
| `Field does not exist` | FLS or missing field | Deploy field + Permission Set |
| `Flow is invalid` | Missing object reference | Deploy objects BEFORE flows |

---

## Integration + Agentforce Orchestration

When building agents with external API integrations, follow this extended order:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INTEGRATION + AGENTFORCE ORCHESTRATION ORDER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. sf-connected-apps  → Create Connected App (if OAuth needed)             │
│  2. sf-integration     → Create Named Credential + External Service         │
│  3. sf-apex            → Create @InvocableMethod (if custom logic needed)   │
│  4. sf-flow            → Create Flow wrapper (HTTP Callout or Apex wrapper) │
│  5. sf-deploy          → Deploy all metadata to org                         │
│  6. sf-ai-agentforce   → Create agent with flow:// target                   │
│  7. sf-deploy          → Publish agent (sf agent publish)                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Integration Order Details

| Step | Skill | Purpose |
|------|-------|---------|
| 1 | sf-connected-apps | OAuth Connected App for API authentication |
| 2 | sf-integration | Named Credential (references Connected App), External Service |
| 3 | sf-apex | Business logic with @InvocableMethod |
| 4 | sf-flow | HTTP Callout Flow or Apex wrapper Flow |
| 5 | sf-deploy | Deploy all metadata |
| 6 | sf-ai-agentforce | Agent Script with flow:// action targets |
| 7 | sf-deploy | sf agent publish to activate |

### Why Integration Order Matters

| Step | Depends On | Fails If Wrong Order |
|------|------------|---------------------|
| sf-integration | sf-connected-apps | Named Credential can't reference OAuth app |
| sf-flow (HTTP) | sf-integration | Flow can't find Named Credential |
| sf-ai-agentforce | sf-flow | Agent can't find flow:// target |
| sf agent publish | All above | Agent actions fail at runtime |

### Integration Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoded API keys | Security risk, not deployable | Use Named Credentials |
| apex:// in Agent Script | Doesn't work reliably | Use GenAiFunction metadata |
| Direct callouts in triggers | Governor limits | Use Queueable + Platform Events |
| Deploying agent before flows | Actions fail | Deploy dependencies first |
