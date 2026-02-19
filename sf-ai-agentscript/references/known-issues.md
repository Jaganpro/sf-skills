<!-- Parent: sf-ai-agentscript/SKILL.md -->
   1 # Known Issues Tracker
   2 
   3 > Unresolved platform bugs, limitations, and edge cases that affect Agent Script development. Unlike the "Common Issues & Fixes" table in SKILL.md (which covers resolved troubleshooting), this file tracks **open platform issues** where the root cause is in Salesforce, not in user code.
   4 
   5 ---
   6 
   7 ## Issue Template
   8 
   9 ```markdown
  10 ## Issue N: [Title]
  11 - **Status**: OPEN | RESOLVED | WORKAROUND
  12 - **Date Discovered**: YYYY-MM-DD
  13 - **Affects**: [Component/workflow affected]
  14 - **Symptom**: What the user sees
  15 - **Root Cause**: Why it happens (if known)
  16 - **Workaround**: How to get around it
  17 - **Open Questions**: What we still don't know
  18 - **References**: Links to related docs, issues, or discussions
  19 ```
  20 
  21 ---
  22 
  23 ## Open Issues
  24 
  25 ### Issue 1: Agent test files block `force-app` deployment
  26 - **Status**: WORKAROUND
  27 - **Date Discovered**: 2026-01-20
  28 - **Affects**: `sf project deploy start --source-dir force-app`
  29 - **Symptom**: Deployment hangs for 2+ minutes or times out when `AiEvaluationDefinition` metadata files exist under `force-app/`. The deploy may eventually succeed but with excessive wait times.
  30 - **Root Cause**: `AiEvaluationDefinition` metadata type triggers server-side processing that blocks the deployment pipeline. The metadata type is not well-suited for source-dir deploys.
  31 - **Workaround**: Move test definitions to a separate directory outside the main deploy path, or use `--metadata` flag to deploy specific types instead of `--source-dir`.
  32   ```bash
  33   # Instead of:
  34   sf project deploy start --source-dir force-app -o TARGET_ORG
  35 
  36   # Use targeted deployment:
  37   sf project deploy start --metadata AiAuthoringBundle:MyAgent -o TARGET_ORG
  38   ```
  39 - **Open Questions**: Will Salesforce optimize `AiEvaluationDefinition` deploy performance in a future release?
  40 
  41 ---
  42 
  43 ### Issue 2: `sf agent publish` fails with namespace prefix on `apex://` targets
  44 - **Status**: OPEN
  45 - **Date Discovered**: 2026-02-01
  46 - **Affects**: Namespaced orgs using `apex://` action targets
  47 - **Symptom**: `sf agent publish authoring-bundle` fails with "invocable action does not exist" error, despite the Apex class being deployed and confirmed via SOQL query.
  48 - **Root Cause**: Unknown. Unclear whether `apex://ClassName` or `apex://ns__ClassName` is the correct format in namespaced orgs. The publish step may not resolve namespace prefixes the same way as standard metadata deployment.
  49 - **Workaround**: None confirmed. Potential approaches to try:
  50   1. Use `apex://ns__ClassName` format
  51   2. Use unmanaged classes (no namespace)
  52   3. Wrap Apex in a Flow and use `flow://` target instead
  53 - **Open Questions**:
  54   - Does `apex://ns__ClassName` work?
  55   - Is this a bug or by-design limitation?
  56   - Does the same issue affect `flow://` targets with namespaced Flows?
  57 
  58 ---
  59 
  60 ### Issue 3: Agent packaging workflow unclear
  61 - **Status**: OPEN
  62 - **Date Discovered**: 2026-02-05
  63 - **Affects**: ISV partners, AppExchange distribution
  64 - **Symptom**: No documented way to package Agent Script agents for distribution. The `AiAuthoringBundle` metadata type has no known packaging equivalent to `BotTemplate`.
  65 - **Root Cause**: Agent Script is newer than the packaging system. Salesforce has not published ISV packaging guidance for `.agent` files.
  66 - **Workaround**: None. Current options:
  67   1. Distribute as source code (customer deploys manually)
  68   2. Use unlocked packages (may include `.agent` files but subscriber customization is untested)
  69   3. Convert to Agent Builder UI (GenAiPlannerBundle) for packaging — loses Agent Script benefits
  70 - **Open Questions**:
  71   - Will `AiAuthoringBundle` be supported in 2GP managed packages?
  72   - Can subscribers modify `.agent` files post-install?
  73   - Is there a roadmap item for Agent Script packaging?
  74 
  75 ---
  76 
  77 ### Issue 4: Legacy `sf bot` CLI commands incompatible with Agent Script
  78 - **Status**: OPEN
  79 - **Date Discovered**: 2026-01-25
  80 - **Affects**: Users migrating from Einstein Bots to Agent Script
  81 - **Symptom**: Old `sf bot` and `sf bot version` commands were removed in sf CLI v2 — these commands no longer exist, not just "don't recognize Agent Script". Running any `sf bot` command returns "Command not found".
  82 - **Root Cause**: The `sf bot` command family was deprecated and removed in sf CLI v2. It targeted `BotDefinition`/`BotVersion` metadata types. Agent Script uses `AiAuthoringBundle`, a completely separate metadata structure.
  83 - **Workaround**: Use `sf agent` commands exclusively for Agent Script:
  84   ```bash
  85   # ❌ Old commands (don't work with Agent Script):
  86   sf bot list
  87   sf bot version list
  88 
  89   # ✅ New commands (for Agent Script):
  90   sf project retrieve start --metadata Agent:MyAgent
  91   sf agent validate authoring-bundle --api-name MyAgent
  92   sf agent publish authoring-bundle --api-name MyAgent
  93   ```
  94 - **Open Questions**: Will Salesforce unify the `sf bot` and `sf agent` command families?
  95 
  96 ---
  97 
  98 ### Issue 5: Agent tests cannot be deployed/retrieved for source control
  99 - **Status**: OPEN
 100 - **Date Discovered**: 2026-02-06
 101 - **Affects**: CI/CD pipelines, test version control
 102 - **Symptom**: Tests created in the Agent Testing Center UI cannot be retrieved via `sf project retrieve start`. Old test XML format references `bot`/`version` fields that don't exist in Agent Script. No metadata type or CLI command exists for new-style agent tests.
 103 - **Root Cause**: The Agent Testing Center was originally built for Einstein Bots. The test metadata schema hasn't been updated for Agent Script's `AiAuthoringBundle` structure. The `AiEvaluationDefinition` type exists but doesn't correspond to the Testing Center's UI-created tests.
 104 - **Workaround**:
 105   1. Use YAML test spec files managed in source control (see `/sf-ai-agentforce-testing` skill)
 106   2. Treat UI-created tests as ephemeral / org-specific
 107   3. Use the Connect API directly to run tests programmatically
 108 - **Open Questions**:
 109   - Will a new metadata type be introduced for Agent Script tests?
 110   - Can `AiEvaluationDefinition` be used with Agent Script agents?
 111   - Is there a roadmap for test portability?
 112 - **References**: See `references/custom-eval-investigation.md` in `sf-ai-agentforce-testing` for related findings on custom evaluation data structure issues.
 113 
 114 ---
 115 
 116 ### Issue 6: `require_user_confirmation` does not trigger confirmation dialog
 117 - **Status**: OPEN
 118 - **Date Discovered**: 2026-02-14
 119 - **Date Updated**: 2026-02-17 (TDD v2.2.0 — confirmed compiles on target-backed actions)
 120 - **Affects**: Actions with `require_user_confirmation: True`
 121 - **Symptom**: Setting `require_user_confirmation: True` on an action definition does not produce a user-facing confirmation dialog before execution. The action executes immediately without user confirmation.
 122 - **Root Cause**: The property is parsed and saved without error, but the runtime does not implement the confirmation UX for Agent Script actions. It may only work for GenAiPlannerBundle actions in the Agent Builder UI.
 123 - **TDD Update (v2.2.0)**: Property compiles and publishes successfully on action definitions with `target:` (both `flow://` and `apex://`). Val_Action_Meta_Props confirms compilation. The issue is purely runtime — the confirmation dialog never appears. Property is NOT valid on `@utils.transition` actions (Val_Action_Properties, v1.3.0).
 124 - **Workaround**: Implement confirmation logic manually using a two-step pattern: (1) LLM asks user to confirm, (2) action has `available when @variables.user_confirmed == True` guard.
 125 - **Open Questions**: Will this be implemented for AiAuthoringBundle in a future release?
 126 
 127 ---
 128 
 129 ### Issue 7: OOTB Asset Library actions may ship without proper quote wrapping
 130 - **Status**: WORKAROUND
 131 - **Date Discovered**: 2026-02-14
 132 - **Affects**: Out-of-the-box (OOTB) actions from the Agentforce Asset Library
 133 - **Symptom**: Some pre-built actions from the Asset Library have input parameters that are not properly quote-wrapped, causing parse errors when referenced in Agent Script.
 134 - **Root Cause**: Asset Library actions were designed for the Agent Builder UI path, which handles quoting differently than Agent Script's text-based syntax.
 135 - **Workaround**: When importing Asset Library actions, manually verify all input parameter names in the action definition. If a parameter name contains special characters or colons (e.g., `Input:query`), wrap it in quotes: `with "Input:query" = ...`
 136 - **Open Questions**: Will Salesforce update Asset Library actions for Agent Script compatibility?
 137 
 138 ---
 139 
 140 ### Issue 8: Lightning UI components do not render on new planner
 141 - **Status**: OPEN
 142 - **Date Discovered**: 2026-02-14
 143 - **Affects**: Agents using Lightning Web Components for rich UI rendering
 144 - **Symptom**: Custom Lightning UI components referenced in agent actions do not render in the chat interface when using the newer planner engine. Components that worked with the legacy planner appear as plain text or are silently dropped.
 145 - **Root Cause**: The newer planner (Atlas/Daisy) does not support the same Lightning component rendering pipeline as the legacy Java planner.
 146 - **Workaround**: None for rich UI. Fall back to text-based responses or use the legacy planner if Lightning component rendering is critical.
 147 - **Open Questions**: Is Lightning UI rendering on the roadmap for the new planner?
 148 
 149 ---
 150 
 151 ### Issue 9: Large action responses cause data loss from state
 152 - **Status**: OPEN
 153 - **Date Discovered**: 2026-02-14
 154 - **Affects**: Actions returning large payloads (>50KB response data)
 155 - **Symptom**: When an action returns a large response payload, subsequent variable access may return null or incomplete data. State appears to lose previously stored values.
 156 - **Root Cause**: Action output data accumulates in conversation context without compaction. Very large responses may push earlier state data beyond the context window boundary.
 157 - **Workaround**: Design Flow/Apex actions to return minimal, summarized data. Use `is_displayable: False` on outputs the LLM doesn't need. Avoid `SELECT *` patterns in data retrieval.
 158 - **Open Questions**: Will automatic context compaction be added for action outputs?
 159 
 160 ---
 161 
 162 ### Issue 10: Agent fails if user lacks permission for ANY action
 163 - **Status**: OPEN
 164 - **Date Discovered**: 2026-02-14
 165 - **Affects**: Agents with actions targeting secured resources
 166 - **Symptom**: If the running user (Einstein Agent User or session user) lacks permission to execute ANY action defined in the agent — even actions in other topics — the entire agent may fail with a permission error rather than gracefully skipping the unauthorized action.
 167 - **Root Cause**: The planner appears to validate permissions for all registered actions at startup, not lazily per-topic.
 168 - **Workaround**: Ensure the Einstein Agent User has permissions for ALL actions defined across all topics. Use Permission Sets to grant necessary access. Alternatively, split agents by permission boundary.
 169 - **Open Questions**: Will the planner support lazy permission checking in a future release?
 170 
 171 ---
 172 
 173 ### Issue 11: Dynamic welcome messages broken (`{!userName}` not resolved)
 174 - **Status**: OPEN
 175 - **Date Discovered**: 2026-02-14
 176 - **Affects**: `system.messages.welcome` with variable interpolation
 177 - **Symptom**: Variable references like `{!@variables.customer_name}` or `{!userName}` in the welcome message display as literal text instead of resolved values.
 178 - **Root Cause**: Welcome messages are rendered before the agent runtime initializes variables. Mutable variables have not been set yet, and linked variables may not be resolved at welcome-message time.
 179 - **Workaround**: Use static welcome messages. Personalize greetings in the first topic's instructions instead.
 180 - **Open Questions**: Will welcome message variable resolution be supported in a future release?
 181 
 182 ---
 183 
 184 ### Issue 12: Welcome message line breaks stripped
 185 - **Status**: OPEN
 186 - **Date Discovered**: 2026-02-14
 187 - **Affects**: `system.messages.welcome` with multi-line content
 188 - **Symptom**: Line breaks (`\n`) in welcome messages are stripped, causing multi-line messages to render as a single line.
 189 - **Root Cause**: The welcome message renderer does not preserve newline characters from the Agent Script source.
 190 - **Workaround**: Keep welcome messages as a single line. Use the first topic's instructions with pipe syntax (`|`) for multi-line greetings.
 191 - **Open Questions**: Is this by design or a bug?
 192 
 193 ---
 194 
 195 ### Issue 13: Related agent nodes fail in SOMA configuration
 196 - **Status**: OPEN
 197 - **Date Discovered**: 2026-02-14
 198 - **Affects**: Multi-agent configurations using `related_agent` references
 199 - **Symptom**: SOMA (Same Org Multi-Agent) configurations that reference related agents via node declarations fail with "Node does not have corresponding topic" error at runtime.
 200 - **Root Cause**: The planner resolves agent references at compile time but may not correctly map cross-agent topic references when agents are deployed independently.
 201 - **Workaround**: Use `@topic.X` delegation within the same agent instead of cross-agent references. For true multi-agent scenarios, use the `@utils.escalate` or connection-based handoff patterns.
 202 - **Open Questions**: Will SOMA node resolution be fixed in a future planner update?
 203 
 204 ---
 205 
 206 ### Issue 14: Previously valid OpenAPI schemas now fail validation
 207 - **Status**: OPEN
 208 - **Date Discovered**: 2026-02-14
 209 - **Affects**: External Service actions using OpenAPI 3.0 schemas
 210 - **Symptom**: OpenAPI schemas that previously passed validation and worked with `externalService://` targets now fail with schema validation errors after org upgrades. No changes were made to the schema files.
 211 - **Root Cause**: Salesforce tightened OpenAPI schema validation rules in recent releases. Schemas that were previously accepted with minor deviations (e.g., missing `info.version`, non-standard extensions) are now rejected.
 212 - **Workaround**: Re-validate schemas against strict OpenAPI 3.0 spec. Common fixes: ensure `info.version` is present, remove non-standard `x-` extensions, verify all `$ref` paths resolve correctly.
 213 - **Open Questions**: Will Salesforce publish the exact validation rules that changed?
 214 
 215 ---
 216 
 217 ### Issue 15: Action definitions without `outputs:` block cause "Internal Error" on publish
 218 - **Status**: WORKAROUND
 219 - **Date Discovered**: 2026-02-16
 220 - **Date Updated**: 2026-02-17 (TDD v2.1.0 — clarified outputs specifically required)
 221 - **Affects**: `sf agent publish authoring-bundle` with topic-level action definitions
 222 - **Symptom**: `sf agent publish` returns "Internal Error, try again later" when topic-level action definitions have `target:` but no `outputs:` block. Also triggered when using `inputs:` without `outputs:`. LSP + CLI validation both PASS — error is server-side compilation only.
 223 - **Root Cause**: The server-side compiler needs output type contracts to resolve `flow://` and `apex://` action targets. Without an `outputs:` block, the compiler cannot generate return bindings. The `inputs:` block alone is NOT sufficient — `outputs:` is specifically required.
 224 - **Workaround**: Always include an `outputs:` block in action definitions. The `inputs:` block can be omitted if the target has no required inputs (the LLM will still slot-fill via `with param=...`), but `outputs:` must always be present.
 225 - **TDD Validation**: `Val_No_Outputs` (v2.1.0) confirms inputs-only action definition → "Internal Error". `Val_Partial_Output` confirms declaring a subset of outputs IS valid. `Val_Apex_Bare_Output` confirms bare `@InvocableMethod` without wrapper classes also triggers this error.
 226 - **Open Questions**: Will the compiler be updated to infer I/O schemas from the target's metadata?
 227 
 228 ---
 229 
 230 ### Issue 16: `connections:` (plural) wrapper block not valid — use `connection messaging:` (singular)
 231 - **Status**: RESOLVED
 232 - **Date Discovered**: 2026-02-16
 233 - **Date Resolved**: 2026-02-16
 234 - **Affects**: Agent Script escalation routing configuration
 235 - **Symptom**: CLI validation rejects `connections:` (plural wrapper) block with `SyntaxError: Invalid syntax after conditional statement`.
 236 - **Root Cause**: The correct syntax is `connection messaging:` (singular, standalone top-level block) — NOT the `connections:` plural wrapper shown in some docs and `future_recipes/`. The `connection <channel>:` block is a Beta Feature available on production orgs.
 237 - **Resolution**: Use `connection messaging:` as a standalone block (no wrapper). Both minimal form (`adaptive_response_allowed` only) and full form (with `outbound_route_type`, `outbound_route_name`, `escalation_message`) are validated.
 238 - **CRITICAL**: `outbound_route_name` requires `flow://` prefix — bare API name causes `ERROR_HTTP_404` on publish. Correct format: `"flow://My_Flow_Name"`.
 239 - **All-or-nothing rule**: When `outbound_route_type` is present, all three route properties are required.
 240 - **Validated on**: Vivint-DevInt (Automated_Virtual_Assistant_BETA), 2026-02-16
 241 
 242 ---
 243 
 244 ### Issue 17: `EinsteinAgentApiChannel` surfaceType not available on all orgs
 245 - **Status**: OPEN
 246 - **Date Discovered**: 2026-02-16
 247 - **Affects**: Agent Runtime API channel enablement via `plannerSurfaces` metadata
 248 - **Symptom**: Adding `plannerSurfaces` with `surfaceType: EinsteinAgentApiChannel` causes deployment errors on some orgs. Valid surfaceType values on tested orgs: `Messaging`, `CustomerWebClient`, `Telephony`, `NextGenChat`.
 249 - **Root Cause**: The `EinsteinAgentApiChannel` surfaceType may require specific org features or licenses that are not universally available.
 250 - **Workaround**: Use `CustomerWebClient` for Agent Runtime API / CLI testing. This surfaceType is available on all tested orgs and enables API access.
 251 - **Open Questions**: Is `EinsteinAgentApiChannel` limited to specific editions or feature flags?
 252 
 253 ---
 254 
 255 ### Issue 18: `connection messaging:` only generates `Messaging` plannerSurface — `CustomerWebClient` dropped on every publish
 256 - **Status**: OPEN
 257 - **Date Discovered**: 2026-02-17
 258 - **Affects**: Agent Builder Preview, Agent Runtime API testing, CLI testing (`sf agent test`, `sf agent preview`)
 259 - **Symptom**: After `sf agent publish authoring-bundle`, the compiled GenAiPlannerBundle only contains a `Messaging` plannerSurface. `CustomerWebClient` is never auto-generated. Agent Builder Preview shows "Something went wrong. Refresh and try again." because it requires `CustomerWebClient`.
 260 - **Root Cause**: The `connection messaging:` DSL block only generates a `Messaging` plannerSurface during compilation. There is no `connection customerwebclient:` DSL syntax — attempting it causes `ERROR_HTTP_404` on publish. The compiler has no mechanism to auto-generate `CustomerWebClient`.
 261 - **Impact**: Every publish overwrites the GenAiPlannerBundle, dropping any manually-added `CustomerWebClient` surface. This requires a post-publish patch after EVERY publish.
 262 - **Workaround — 6-Step Post-Publish Patch Workflow:**
 263   1. `sf agent publish authoring-bundle --api-name AgentName -o TARGET_ORG --json` → creates new version (e.g., v22)
 264   2. `sf project retrieve start --metadata "GenAiPlannerBundle:AgentName_vNN" -o TARGET_ORG --json` → retrieve compiled bundle
 265   3. Manually add second `<plannerSurfaces>` block to the XML with `<surfaceType>CustomerWebClient</surfaceType>` (copy the existing `Messaging` block, change surfaceType and surface fields)
 266   4. `sf agent deactivate --api-name AgentName -o TARGET_ORG` → deactivate agent (deploy fails while active)
 267   5. `sf project deploy start --metadata "GenAiPlannerBundle:AgentName_vNN" -o TARGET_ORG --json` → deploy patched bundle
 268   6. `sf agent activate --api-name AgentName -o TARGET_ORG` → reactivate agent
 269 - **Patch XML Example:**
 270   ```xml
 271   <!-- Add this AFTER the existing Messaging plannerSurfaces block -->
 272   <plannerSurfaces>
 273       <adaptiveResponseAllowed>false</adaptiveResponseAllowed>
 274       <callRecordingAllowed>false</callRecordingAllowed>
 275       <outboundRouteConfigs>
 276           <escalationMessage>One moment while I connect you with a support specialist.</escalationMessage>
 277           <outboundRouteName>Route_from_Vivint_Virtual_Support</outboundRouteName>
 278           <outboundRouteType>OmniChannelFlow</outboundRouteType>
 279       </outboundRouteConfigs>
 280       <surface>SurfaceAction__CustomerWebClient</surface>
 281       <surfaceType>CustomerWebClient</surfaceType>
 282   </plannerSurfaces>
 283   ```
 284 - **Note**: The `outboundRouteConfigs` should mirror the Messaging surface config. If no routing is configured, omit `outboundRouteConfigs`.
 285 - **Validated on**: Vivint-DevInt (Automated_Virtual_Assistant_BETA v22), 2026-02-17
 286 
 287 ---
 288 
 289 ## Resolved Issues
 290 
 291 *(Move issues here when they are fixed by Salesforce or a confirmed workaround is validated.)*
 292 
 293 ---
 294 
 295 ## Contributing
 296 
 297 When you discover a new platform issue during an Agent Script session:
 298 
 299 1. Add it to the **Open Issues** section using the template above
 300 2. Assign the next sequential issue number
 301 3. Set status to `OPEN` or `WORKAROUND`
 302 4. Include the date discovered
 303 5. Be specific about the symptom and any error messages
 304 6. Note what you've tried so far under "Workaround"
 305 
 306 When an issue is resolved:
 307 1. Update the status to `RESOLVED`
 308 2. Add the resolution date and what fixed it (e.g., "Fixed in Spring '26 release")
 309 3. Move the issue to the **Resolved Issues** section
 310 
 311 ---
 312 
 313 *Last updated: 2026-02-17*
