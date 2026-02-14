# Known Issues Tracker

> Unresolved platform bugs, limitations, and edge cases that affect Agent Script development. Unlike the "Common Issues & Fixes" table in SKILL.md (which covers resolved troubleshooting), this file tracks **open platform issues** where the root cause is in Salesforce, not in user code.

---

## Issue Template

```markdown
## Issue N: [Title]
- **Status**: OPEN | RESOLVED | WORKAROUND
- **Date Discovered**: YYYY-MM-DD
- **Affects**: [Component/workflow affected]
- **Symptom**: What the user sees
- **Root Cause**: Why it happens (if known)
- **Workaround**: How to get around it
- **Open Questions**: What we still don't know
- **References**: Links to related docs, issues, or discussions
```

---

## Open Issues

### Issue 1: Agent test files block `force-app` deployment
- **Status**: WORKAROUND
- **Date Discovered**: 2026-01-20
- **Affects**: `sf project deploy start --source-dir force-app`
- **Symptom**: Deployment hangs for 2+ minutes or times out when `AiEvaluationDefinition` metadata files exist under `force-app/`. The deploy may eventually succeed but with excessive wait times.
- **Root Cause**: `AiEvaluationDefinition` metadata type triggers server-side processing that blocks the deployment pipeline. The metadata type is not well-suited for source-dir deploys.
- **Workaround**: Move test definitions to a separate directory outside the main deploy path, or use `--metadata` flag to deploy specific types instead of `--source-dir`.
  ```bash
  # Instead of:
  sf project deploy start --source-dir force-app -o TARGET_ORG

  # Use targeted deployment:
  sf project deploy start --metadata AiAuthoringBundle:MyAgent -o TARGET_ORG
  ```
- **Open Questions**: Will Salesforce optimize `AiEvaluationDefinition` deploy performance in a future release?

---

### Issue 2: `sf agent publish` fails with namespace prefix on `apex://` targets
- **Status**: OPEN
- **Date Discovered**: 2026-02-01
- **Affects**: Namespaced orgs using `apex://` action targets
- **Symptom**: `sf agent publish authoring-bundle` fails with "invocable action does not exist" error, despite the Apex class being deployed and confirmed via SOQL query.
- **Root Cause**: Unknown. Unclear whether `apex://ClassName` or `apex://ns__ClassName` is the correct format in namespaced orgs. The publish step may not resolve namespace prefixes the same way as standard metadata deployment.
- **Workaround**: None confirmed. Potential approaches to try:
  1. Use `apex://ns__ClassName` format
  2. Use unmanaged classes (no namespace)
  3. Wrap Apex in a Flow and use `flow://` target instead
- **Open Questions**:
  - Does `apex://ns__ClassName` work?
  - Is this a bug or by-design limitation?
  - Does the same issue affect `flow://` targets with namespaced Flows?

---

### Issue 3: Agent packaging workflow unclear
- **Status**: OPEN
- **Date Discovered**: 2026-02-05
- **Affects**: ISV partners, AppExchange distribution
- **Symptom**: No documented way to package Agent Script agents for distribution. The `AiAuthoringBundle` metadata type has no known packaging equivalent to `BotTemplate`.
- **Root Cause**: Agent Script is newer than the packaging system. Salesforce has not published ISV packaging guidance for `.agent` files.
- **Workaround**: None. Current options:
  1. Distribute as source code (customer deploys manually)
  2. Use unlocked packages (may include `.agent` files but subscriber customization is untested)
  3. Convert to Agent Builder UI (GenAiPlannerBundle) for packaging — loses Agent Script benefits
- **Open Questions**:
  - Will `AiAuthoringBundle` be supported in 2GP managed packages?
  - Can subscribers modify `.agent` files post-install?
  - Is there a roadmap item for Agent Script packaging?

---

### Issue 4: Legacy `sf bot` CLI commands incompatible with Agent Script
- **Status**: OPEN
- **Date Discovered**: 2026-01-25
- **Affects**: Users migrating from Einstein Bots to Agent Script
- **Symptom**: Old `sf bot` and `sf bot version` commands were removed in sf CLI v2 — these commands no longer exist, not just "don't recognize Agent Script". Running any `sf bot` command returns "Command not found".
- **Root Cause**: The `sf bot` command family was deprecated and removed in sf CLI v2. It targeted `BotDefinition`/`BotVersion` metadata types. Agent Script uses `AiAuthoringBundle`, a completely separate metadata structure.
- **Workaround**: Use `sf agent` commands exclusively for Agent Script:
  ```bash
  # ❌ Old commands (don't work with Agent Script):
  sf bot list
  sf bot version list

  # ✅ New commands (for Agent Script):
  sf project retrieve start --metadata Agent:MyAgent
  sf agent validate authoring-bundle --api-name MyAgent
  sf agent publish authoring-bundle --api-name MyAgent
  ```
- **Open Questions**: Will Salesforce unify the `sf bot` and `sf agent` command families?

---

### Issue 5: Agent tests cannot be deployed/retrieved for source control
- **Status**: OPEN
- **Date Discovered**: 2026-02-06
- **Affects**: CI/CD pipelines, test version control
- **Symptom**: Tests created in the Agent Testing Center UI cannot be retrieved via `sf project retrieve start`. Old test XML format references `bot`/`version` fields that don't exist in Agent Script. No metadata type or CLI command exists for new-style agent tests.
- **Root Cause**: The Agent Testing Center was originally built for Einstein Bots. The test metadata schema hasn't been updated for Agent Script's `AiAuthoringBundle` structure. The `AiEvaluationDefinition` type exists but doesn't correspond to the Testing Center's UI-created tests.
- **Workaround**:
  1. Use YAML test spec files managed in source control (see `/sf-ai-agentforce-testing` skill)
  2. Treat UI-created tests as ephemeral / org-specific
  3. Use the Connect API directly to run tests programmatically
- **Open Questions**:
  - Will a new metadata type be introduced for Agent Script tests?
  - Can `AiEvaluationDefinition` be used with Agent Script agents?
  - Is there a roadmap for test portability?
- **References**: See `resources/custom-eval-investigation.md` in `sf-ai-agentforce-testing` for related findings on custom evaluation data structure issues.

---

## Resolved Issues

*(Move issues here when they are fixed by Salesforce or a confirmed workaround is validated.)*

---

## Contributing

When you discover a new platform issue during an Agent Script session:

1. Add it to the **Open Issues** section using the template above
2. Assign the next sequential issue number
3. Set status to `OPEN` or `WORKAROUND`
4. Include the date discovered
5. Be specific about the symptom and any error messages
6. Note what you've tried so far under "Workaround"

When an issue is resolved:
1. Update the status to `RESOLVED`
2. Add the resolution date and what fixed it (e.g., "Fixed in Spring '26 release")
3. Move the issue to the **Resolved Issues** section

---

*Last updated: 2026-02-12*
