<!-- Parent: sf-deploy/SKILL.md -->
   1 # Agentforce Agent Deployment Guide
   2 
   3 > Complete DevOps guide for deploying Agentforce agents using SF CLI
   4 
   5 ## Overview
   6 
   7 This guide covers the complete deployment lifecycle for Agentforce agents, including:
   8 - Agent metadata types and pseudo metadata
   9 - Sync operations (retrieve/deploy)
  10 - Lifecycle management (activate/deactivate)
  11 - Full deployment workflows
  12 
  13 **Related Skills:**
  14 - `sf-ai-agentscript` - Agent Script authoring and publishing (recommended for new agents)
  15 - `sf-ai-agentforce` - Agentforce platform setup (Agent Builder, PromptTemplate, Models API)
  16 - `sf-deploy` - This skill - deployment orchestration
  17 
  18 ---
  19 
  20 ## Agent Metadata Types
  21 
  22 Agentforce agents consist of multiple metadata components:
  23 
  24 | Metadata Type | Description | Example API Name |
  25 |---------------|-------------|------------------|
  26 | `Bot` | Top-level chatbot definition | `Customer_Support_Agent` |
  27 | `BotVersion` | Version configuration | `Customer_Support_Agent.v1` |
  28 | `GenAiPlannerBundle` | Reasoning engine (LLM config) | `Customer_Support_Agent_Planner` |
  29 | `GenAiPlugin` | Topic definition | `Order_Management_Plugin` |
  30 | `GenAiFunction` | Action definition | `Get_Order_Status_Function` |
  31 
  32 ### Metadata Hierarchy
  33 
  34 ```
  35 Bot (Agent Definition)
  36 └── BotVersion (Version Config)
  37     └── GenAiPlannerBundle (Reasoning Engine)
  38         ├── GenAiPlugin (Topic 1)
  39         │   ├── GenAiFunction (Action 1)
  40         │   └── GenAiFunction (Action 2)
  41         └── GenAiPlugin (Topic 2)
  42             └── GenAiFunction (Action 3)
  43 ```
  44 
  45 ---
  46 
  47 ## Agent Pseudo Metadata Type
  48 
  49 The `Agent` pseudo metadata type is a convenience wrapper that retrieves or deploys all agent-related components at once.
  50 
  51 ### Using the Agent Pseudo Type
  52 
  53 ```bash
  54 # Retrieve agent + all dependencies from org
  55 sf project retrieve start --metadata Agent:[AgentName] --target-org [alias]
  56 
  57 # Deploy agent metadata to org
  58 sf project deploy start --metadata Agent:[AgentName] --target-org [alias]
  59 ```
  60 
  61 ### What Gets Synced
  62 
  63 When using `--metadata Agent:[Name]`:
  64 
  65 **Retrieved/Deployed:**
  66 - `Bot` - Top-level chatbot
  67 - `BotVersion` - Version configuration
  68 - `GenAiPlannerBundle` - Reasoning engine
  69 - `GenAiPlugin` - All topics
  70 - `GenAiFunction` - All actions
  71 
  72 **NOT Included:**
  73 - Apex classes (deploy separately)
  74 - Flows (deploy separately)
  75 - Named Credentials (deploy separately)
  76 
  77 ---
  78 
  79 ## Sync Operations
  80 
  81 ### Retrieving Agents from Org
  82 
  83 ```bash
  84 # Retrieve agent using pseudo metadata type
  85 sf project retrieve start --metadata Agent:Customer_Support_Agent --target-org myorg
  86 
  87 # Retrieve to specific output directory
  88 sf project retrieve start --metadata Agent:Customer_Support_Agent --output-dir ./retrieved --target-org myorg
  89 
  90 # Retrieve multiple agents
  91 sf project retrieve start --metadata Agent:Support_Agent,Agent:Sales_Agent --target-org myorg
  92 ```
  93 
  94 ### Retrieving Specific Components
  95 
  96 ```bash
  97 # Retrieve just the bot definition
  98 sf project retrieve start --metadata Bot:Customer_Support_Agent --target-org myorg
  99 
 100 # Retrieve just the planner bundle
 101 sf project retrieve start --metadata GenAiPlannerBundle:Customer_Support_Agent_Planner --target-org myorg
 102 
 103 # Retrieve all plugins (topics)
 104 sf project retrieve start --metadata GenAiPlugin --target-org myorg
 105 
 106 # Retrieve all functions (actions)
 107 sf project retrieve start --metadata GenAiFunction --target-org myorg
 108 ```
 109 
 110 ### Deploying Agents to Org
 111 
 112 ```bash
 113 # Deploy agent using pseudo metadata type
 114 sf project deploy start --metadata Agent:Customer_Support_Agent --target-org myorg
 115 
 116 # Deploy with validation only (dry run)
 117 sf project deploy start --metadata Agent:Customer_Support_Agent --dry-run --target-org myorg
 118 
 119 # Deploy multiple agents
 120 sf project deploy start --metadata Agent:Support_Agent,Agent:Sales_Agent --target-org myorg
 121 ```
 122 
 123 ---
 124 
 125 ## Agent Lifecycle Management
 126 
 127 ### Activate Agent
 128 
 129 Makes an agent available to users.
 130 
 131 ```bash
 132 sf agent activate --api-name [AgentName] --target-org [alias]
 133 ```
 134 
 135 **Requirements:**
 136 - Agent must be published first (`sf agent publish authoring-bundle`)
 137 - All Apex classes and Flows must be deployed
 138 - `default_agent_user` must be a valid org user with Agentforce permissions
 139 
 140 **Post-Activation:**
 141 - Agent is immediately available to users
 142 - Preview command can be used for testing
 143 - Changes require deactivation first
 144 
 145 ### Deactivate Agent
 146 
 147 Deactivates an agent for modifications. **Required before making changes.**
 148 
 149 ```bash
 150 sf agent deactivate --api-name [AgentName] --target-org [alias]
 151 ```
 152 
 153 **When Deactivation is Required:**
 154 - Adding or removing topics
 155 - Modifying action configurations
 156 - Changing system instructions
 157 - Updating variable definitions
 158 
 159 ### Modification Workflow
 160 
 161 ```bash
 162 # 1. Deactivate agent
 163 sf agent deactivate --api-name Customer_Support_Agent --target-org myorg
 164 
 165 # 2. Make changes to Agent Script
 166 
 167 # 3. Re-publish
 168 sf agent publish authoring-bundle --api-name Customer_Support_Agent --target-org myorg
 169 
 170 # 4. Re-activate
 171 sf agent activate --api-name Customer_Support_Agent --target-org myorg
 172 ```
 173 
 174 ---
 175 
 176 ## Agent Preview
 177 
 178 Preview allows testing agent behavior before production deployment.
 179 
 180 ### Preview Modes
 181 
 182 | Mode | Command | Use When |
 183 |------|---------|----------|
 184 | **Simulated** | `sf agent preview --api-name X` | Testing logic, Apex/Flows not ready |
 185 | **Live** | `sf agent preview --api-name X --use-live-actions` | Integration testing with real data |
 186 
 187 ### Simulated Mode (Default)
 188 
 189 ```bash
 190 sf agent preview --api-name Customer_Support_Agent --target-org myorg
 191 ```
 192 
 193 - LLM simulates action responses
 194 - No actual Apex/Flow execution
 195 - Safe for testing - no data changes
 196 
 197 ### Live Mode
 198 
 199 ```bash
 200 sf agent preview --api-name Customer_Support_Agent --use-live-actions --target-org myorg
 201 ```
 202 
 203 **Requirements:**
 204 - Standard org auth (`sf org login web`)
 205 - Apex classes and Flows deployed
 206 - Agent must be active
 207 
 208 ### Preview with Debug Output
 209 
 210 ```bash
 211 sf agent preview --api-name Customer_Support_Agent --output-dir ./preview-logs --apex-debug --target-org myorg
 212 ```
 213 
 214 > **v2.121.7+**: Live preview no longer requires a Connected App. Standard org auth (`sf org login web`) suffices.
 215 
 216 ---
 217 
 218 ## Full Deployment Workflows
 219 
 220 ### New Agent Deployment
 221 
 222 Complete workflow for deploying a new agent:
 223 
 224 ```bash
 225 # 1. Deploy Apex classes (if any)
 226 sf project deploy start --metadata ApexClass --target-org myorg
 227 
 228 # 2. Deploy Flows
 229 sf project deploy start --metadata Flow --target-org myorg
 230 
 231 # 3. Validate Agent Script
 232 sf agent validate authoring-bundle --api-name Customer_Support_Agent --target-org myorg
 233 
 234 # 4. Publish agent
 235 sf agent publish authoring-bundle --api-name Customer_Support_Agent --target-org myorg
 236 
 237 # 5. Preview (simulated mode)
 238 sf agent preview --api-name Customer_Support_Agent --target-org myorg
 239 
 240 # 6. Activate
 241 sf agent activate --api-name Customer_Support_Agent --target-org myorg
 242 
 243 # 7. Preview (live mode - optional)
 244 sf agent preview --api-name Customer_Support_Agent --use-live-actions --target-org myorg
 245 ```
 246 
 247 ### Update Existing Agent
 248 
 249 ```bash
 250 # 1. Deactivate
 251 sf agent deactivate --api-name Customer_Support_Agent --target-org myorg
 252 
 253 # 2. Deploy updated dependencies (if any)
 254 sf project deploy start --metadata ApexClass,Flow --target-org myorg
 255 
 256 # 3. Validate
 257 sf agent validate authoring-bundle --api-name Customer_Support_Agent --target-org myorg
 258 
 259 # 4. Re-publish
 260 sf agent publish authoring-bundle --api-name Customer_Support_Agent --target-org myorg
 261 
 262 # 5. Preview
 263 sf agent preview --api-name Customer_Support_Agent --target-org myorg
 264 
 265 # 6. Re-activate
 266 sf agent activate --api-name Customer_Support_Agent --target-org myorg
 267 ```
 268 
 269 ### Sync Between Orgs
 270 
 271 ```bash
 272 # 1. Retrieve from source org
 273 sf project retrieve start --metadata Agent:Customer_Support_Agent --target-org source-org
 274 
 275 # 2. Deploy dependencies to target org first
 276 sf project deploy start --source-dir force-app/main/default/classes --target-org target-org
 277 sf project deploy start --source-dir force-app/main/default/flows --target-org target-org
 278 
 279 # 3. Deploy agent metadata
 280 sf project deploy start --metadata Agent:Customer_Support_Agent --target-org target-org
 281 
 282 # 4. Publish agent in target org
 283 sf agent publish authoring-bundle --api-name Customer_Support_Agent --target-org target-org
 284 
 285 # 5. Activate in target org
 286 sf agent activate --api-name Customer_Support_Agent --target-org target-org
 287 ```
 288 
 289 ### CI/CD Pipeline Integration
 290 
 291 Example deployment script for CI/CD:
 292 
 293 ```bash
 294 #!/bin/bash
 295 # deploy-agent.sh
 296 
 297 set -e  # Exit on error
 298 
 299 ORG_ALIAS=$1
 300 AGENT_NAME=$2
 301 
 302 echo "🚀 Deploying agent: $AGENT_NAME to $ORG_ALIAS"
 303 
 304 # Step 1: Deploy dependencies
 305 echo "📦 Deploying Apex classes..."
 306 sf project deploy start --metadata ApexClass --target-org $ORG_ALIAS --wait 10
 307 
 308 echo "📦 Deploying Flows..."
 309 sf project deploy start --metadata Flow --target-org $ORG_ALIAS --wait 10
 310 
 311 # Step 2: Validate agent script
 312 echo "✅ Validating Agent Script..."
 313 sf agent validate authoring-bundle --api-name $AGENT_NAME --target-org $ORG_ALIAS
 314 
 315 # Step 3: Check if agent exists (deactivate if needed)
 316 echo "🔍 Checking agent status..."
 317 if sf agent deactivate --api-name $AGENT_NAME --target-org $ORG_ALIAS 2>/dev/null; then
 318     echo "⏸️ Agent deactivated for update"
 319 fi
 320 
 321 # Step 4: Publish agent (--skip-retrieve skips metadata retrieval, faster in CI)
 322 echo "📤 Publishing agent..."
 323 sf agent publish authoring-bundle --api-name $AGENT_NAME --target-org $ORG_ALIAS --skip-retrieve --wait 10
 324 
 325 # Step 5: Activate agent
 326 echo "▶️ Activating agent..."
 327 sf agent activate --api-name $AGENT_NAME --target-org $ORG_ALIAS
 328 
 329 echo "✅ Agent deployment complete: $AGENT_NAME"
 330 ```
 331 
 332 Usage:
 333 ```bash
 334 ./deploy-agent.sh myorg Customer_Support_Agent
 335 ```
 336 
 337 ---
 338 
 339 ## Dependency Deployment Order
 340 
 341 **Critical:** Dependencies must be deployed BEFORE the agent.
 342 
 343 ```
 344 1. Custom Objects/Fields (sf-metadata)
 345    ↓
 346 2. Apex Classes (sf-apex)
 347    ↓
 348 3. Flows (sf-flow)
 349    ↓
 350 4. Named Credentials (sf-integration, if external APIs)
 351    ↓
 352 5. Agent Metadata (sf-ai-agentscript publish)
 353    ↓
 354 6. Agent Activation
 355 ```
 356 
 357 ### Deployment Commands by Order
 358 
 359 ```bash
 360 # 1. Objects/Fields
 361 sf project deploy start --metadata CustomObject,CustomField --target-org myorg
 362 
 363 # 2. Apex
 364 sf project deploy start --metadata ApexClass --target-org myorg
 365 
 366 # 3. Flows
 367 sf project deploy start --metadata Flow --target-org myorg
 368 
 369 # 4. Named Credentials (if needed)
 370 sf project deploy start --metadata NamedCredential --target-org myorg
 371 
 372 # 5. Publish agent
 373 sf agent publish authoring-bundle --api-name My_Agent --target-org myorg
 374 
 375 # 6. Activate
 376 sf agent activate --api-name My_Agent --target-org myorg
 377 ```
 378 
 379 ---
 380 
 381 ## Post-Deployment Validation for API Access
 382 
 383 After deploying and activating an agent, verify it is accessible via the Agent Runtime API. Missing metadata causes silent 500 errors.
 384 
 385 ### Validation Checklist
 386 
 387 ```bash
 388 # 1. Verify GenAiPlannerBundle has plannerSurfaces
 389 sf project retrieve start --metadata GenAiPlannerBundle --target-org myorg --output-dir ./check
 390 grep -l "plannerSurfaces" ./check/**/*.xml
 391 # If no results → add plannerSurfaces block (see below)
 392 
 393 # 2. Verify BotVersion has surfacesEnabled=true
 394 sf project retrieve start --metadata BotVersion --target-org myorg --output-dir ./check
 395 grep "surfacesEnabled" ./check/**/*.xml
 396 # Should show: <surfacesEnabled>true</surfacesEnabled>
 397 
 398 # 3. Test API connectivity
 399 curl -s -X POST "https://DOMAIN.my.salesforce.com/services/oauth2/token" \
 400   -d "grant_type=client_credentials&client_id=KEY&client_secret=SECRET" | jq .access_token
 401 ```
 402 
 403 ### Fix: Add Missing plannerSurfaces
 404 
 405 If the GenAiPlannerBundle XML is missing the `plannerSurfaces` block, add `CustomerWebClient`:
 406 
 407 ```xml
 408 <GenAiPlannerBundle xmlns="http://soap.sforce.com/2006/04/metadata">
 409     <!-- existing elements -->
 410     <plannerSurfaces>
 411         <adaptiveResponseAllowed>false</adaptiveResponseAllowed>
 412         <callRecordingAllowed>false</callRecordingAllowed>
 413         <surface>SurfaceAction__CustomerWebClient</surface>
 414         <surfaceType>CustomerWebClient</surfaceType>
 415     </plannerSurfaces>
 416 </GenAiPlannerBundle>
 417 ```
 418 
 419 > **Note**: `EinsteinAgentApiChannel` surfaceType is NOT available on all orgs. Use `CustomerWebClient` instead — it enables both Agent Builder Preview and Agent Runtime API access. See `sf-ai-agentscript` Known Issue 17.
 420 
 421 > **⚠️ Agent Script agents**: `connection messaging:` in the `.agent` DSL ONLY generates a `Messaging` plannerSurface — `CustomerWebClient` is never auto-generated. You must manually patch it after EVERY `sf agent publish authoring-bundle`. See `sf-ai-agentscript` Known Issue 18 for the full 6-step post-publish workflow.
 422 
 423 ### Fix: Add plannerSurfaces when agent is active
 424 
 425 If the agent is active, you must deactivate before deploying:
 426 
 427 ```bash
 428 # Deactivate → Deploy → Activate
 429 sf agent deactivate --api-name AgentName -o TARGET_ORG
 430 sf project deploy start --metadata "GenAiPlannerBundle:AgentName_vNN" -o TARGET_ORG --json
 431 sf agent activate --api-name AgentName -o TARGET_ORG
 432 ```
 433 
 434 ### Fix: Enable surfacesEnabled on BotVersion
 435 
 436 ```xml
 437 <BotVersion xmlns="http://soap.sforce.com/2006/04/metadata">
 438     <!-- existing elements -->
 439     <surfacesEnabled>true</surfacesEnabled>
 440 </BotVersion>
 441 ```
 442 
 443 Then redeploy:
 444 ```bash
 445 sf project deploy start --metadata GenAiPlannerBundle,BotVersion --target-org myorg
 446 ```
 447 
 448 > **Why this matters**: Without `CustomerWebClient` plannerSurface, the Agent Builder Preview shows "Something went wrong" and the Agent Runtime API returns `500 UNKNOWN_EXCEPTION` on session creation.
 449 
 450 ---
 451 
 452 ## Troubleshooting
 453 
 454 ### "Internal Error, try again later"
 455 
 456 **Causes:**
 457 - Invalid `default_agent_user`
 458 - Dependencies not deployed
 459 - Flow/action variable name mismatch
 460 
 461 **Solutions:**
 462 ```bash
 463 # Verify user exists
 464 sf data query --query "SELECT Id, Username FROM User WHERE Username = 'agent@example.com'" --target-org myorg
 465 
 466 # Deploy dependencies first
 467 sf project deploy start --metadata ApexClass,Flow --target-org myorg
 468 ```
 469 
 470 ### "No active agents found"
 471 
 472 **Cause:** Agent not activated
 473 
 474 **Solution:**
 475 ```bash
 476 sf agent activate --api-name My_Agent --target-org myorg
 477 ```
 478 
 479 ### "Agent must be deactivated before changes"
 480 
 481 **Cause:** Trying to modify active agent
 482 
 483 **Solution:**
 484 ```bash
 485 sf agent deactivate --api-name My_Agent --target-org myorg
 486 # Make changes
 487 sf agent publish authoring-bundle --api-name My_Agent --target-org myorg
 488 sf agent activate --api-name My_Agent --target-org myorg
 489 ```
 490 
 491 ### Deployment Fails with Missing Dependencies
 492 
 493 **Cause:** Apex/Flows not deployed before agent
 494 
 495 **Solution:** Follow the dependency deployment order above.
 496 
 497 ---
 498 
 499 ## Cross-Skill Integration
 500 
 501 | From Skill | To Skill | Purpose |
 502 |------------|----------|---------|
 503 | sf-ai-agentscript | sf-deploy | Publish and activate agents |
 504 | sf-apex | sf-deploy | Deploy Apex before agent |
 505 | sf-flow | sf-deploy | Deploy Flows before agent |
 506 | sf-integration | sf-deploy | Deploy Named Credentials for external APIs |
 507 
 508 ### Integration Pattern
 509 
 510 ```bash
 511 # 1. sf-apex creates InvocableMethod class
 512 # 2. sf-flow creates wrapper Flow
 513 # 3. sf-ai-agentscript creates agent with flow:// action
 514 # 4. sf-deploy orchestrates deployment in correct order
 515 ```
 516 
 517 ---
 518 
 519 ## Command Reference
 520 
 521 ### Agent-Specific Commands
 522 
 523 | Command | Description |
 524 |---------|-------------|
 525 | `sf agent publish authoring-bundle --api-name X` | Publish authoring bundle |
 526 | `sf agent publish authoring-bundle --api-name X --skip-retrieve` | Publish without retrieving from org (CI/CD) |
 527 | `sf agent activate --api-name X` | Activate published agent |
 528 | `sf agent deactivate --api-name X` | Deactivate agent for changes |
 529 | `sf agent preview --api-name X` | Preview agent behavior |
 530 | `sf agent validate authoring-bundle --api-name X` | Validate Agent Script syntax |
 531 
 532 ### Metadata Commands with Agent Pseudo Type
 533 
 534 | Command | Description |
 535 |---------|-------------|
 536 | `sf project retrieve start --metadata Agent:X` | Retrieve agent + components |
 537 | `sf project deploy start --metadata Agent:X` | Deploy agent metadata |
 538 | `sf project retrieve start --metadata Bot:X` | Retrieve bot definition only |
 539 | `sf project retrieve start --metadata GenAiPlannerBundle:X` | Retrieve planner bundle |
 540 | `sf project retrieve start --metadata GenAiPlugin` | Retrieve all plugins |
 541 | `sf project retrieve start --metadata GenAiFunction` | Retrieve all functions |
 542 
 543 ### Management Commands
 544 
 545 | Command | Description |
 546 |---------|-------------|
 547 | `sf org open agent --api-name X` | Open agent in Agentforce Builder |
 548 | `sf org open authoring-bundle` | Open Agentforce Studio list view (v2.121.7+) |
 549 | `sf org list metadata --metadata-type Bot` | List bots in org |
 550 | `sf org list metadata --metadata-type GenAiPlannerBundle` | List planner bundles |
 551 
 552 ---
 553 
 554 ## Related Documentation
 555 
 556 - [Agent Script DSL Reference](../../sf-ai-agentscript/SKILL.md)
 557 - [Agent Testing Guide](../../sf-ai-agentforce-testing/SKILL.md)
