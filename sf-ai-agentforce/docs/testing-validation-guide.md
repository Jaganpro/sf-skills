# Testing & Validation Guide

This guide documents tested Agent Script patterns and common deployment issues based on systematic validation testing (December 2025).

## Deployment Methods

There are **two ways** to deploy Agentforce agents:

### 1. Metadata API (GenAiPlannerBundle)

Uses standard `sf project deploy start` with `genAiPlannerBundles/` directory:

```
force-app/main/default/genAiPlannerBundles/
└── My_Agent/
    ├── My_Agent.genAiPlannerBundle           # XML manifest
    └── agentScript/
        └── My_Agent_definition.agent         # Agent Script file
```

**Requirements:**
- `sourceApiVersion: "65.0"` in sfdx-project.json (v65+ required!)
- XML bundle file + Agent Script file in `agentScript/` subfolder

### 2. Agent Builder DX (authoring-bundle)

Uses `sf agent publish authoring-bundle` with `aiAuthoringBundles/` directory:

```
force-app/main/default/aiAuthoringBundles/
└── My_Agent/
    ├── My_Agent.bundle-meta.xml
    └── My_Agent.agent
```

---

## Test Matrix

| Level | Complexity | Features Tested | Status |
|-------|------------|-----------------|--------|
| 1 | Basic | system, config, single start_agent topic | ✅ Verified |
| 2 | Multi-topic | Multiple topics, @utils.transition routing | ✅ Verified |
| 3 | Variables | linked, mutable, language block, variable templates | ✅ Verified |
| 4 | Flow Actions | flow:// targets, inputs/outputs, @actions.* | ✅ Verified |
| 5 | Complex | All features + @utils.escalate, multi-action topics | ✅ Verified |

---

## Validated Working Syntax

### Minimal Working Agent (Level 1)

The simplest deployable agent - no variables, no actions:

```agentscript
system:
    instructions: "You are a friendly greeting agent. Keep responses short and helpful."
    messages:
        welcome: "Hello! How can I help you today?"
        error: "Sorry, I encountered an error."

config:
    developer_name: "Level1_SimpleAgent"
    default_agent_user: "user@example.com"
    agent_label: "Level 1 - Simple Agent"
    description: "Simplest agent test - single topic with greeting"

start_agent greeting:
    label: "Greeting"
    description: "Greets users and offers assistance"
    reasoning:
        instructions: ->
            | Greet the user warmly.
            | Ask how you can help them today.
```

### Agent with Multiple Topics (Level 2)

```agentscript
start_agent topic_selector:
    label: "Topic Selector"
    description: "Routes to topics"
    reasoning:
        instructions: ->
            | Determine what the user needs.
        actions:
            go_sales: @utils.transition to @topic.sales
            go_support: @utils.transition to @topic.support

topic sales:
    label: "Sales"
    description: "Handles sales inquiries"
    reasoning:
        instructions: ->
            | Answer sales-related questions.
        actions:
            go_support: @utils.transition to @topic.support

topic support:
    label: "Support"
    description: "Handles support inquiries"
    reasoning:
        instructions: ->
            | Answer support-related questions.
        actions:
            go_sales: @utils.transition to @topic.sales
```

### Agent with Variables (Level 3)

```agentscript
variables:
    # Linked variables (read-only from Salesforce context)
    EndUserId: linked string
        source: @MessagingSession.MessagingEndUserId
        description: "Messaging End User ID"
    RoutableId: linked string
        source: @MessagingSession.Id
        description: "Messaging Session ID"
    ContactId: linked string
        source: @MessagingEndUser.ContactId
        description: "Contact ID"

    # Mutable variables (can be modified by agent)
    user_name: mutable string
        description: "User's name"
    preference_count: mutable number
        description: "Number of preferences"
    has_preferences: mutable boolean
        description: "Whether user has preferences"

language:
    default_locale: "en_US"
    additional_locales: ""
    all_additional_locales: False
```

**Using Variables in Instructions:**
```agentscript
reasoning:
    instructions: ->
        | Greet the user by name: {!@variables.user_name}
        | Check their preference count: {!@variables.preference_count}
```

### Agent with Flow Action (Level 4)

```agentscript
topic account_lookup:
    label: "Account Lookup"
    description: "Looks up account information using Flow"

    actions:
        get_account:
            description: "Retrieves account information by ID"
            inputs:
                inp_AccountId: string
                    description: "The Salesforce Account ID to look up"
            outputs:
                out_AccountName: string
                    description: "The account name"
                out_Industry: string
                    description: "The account industry"
                out_IsFound: boolean
                    description: "Whether the account was found"
            target: "flow://Get_Account_Info"

    reasoning:
        instructions: ->
            | Ask the user for an Account ID if not provided.
            | Call the get_account action to look up the account.
            | Report the results to the user.
            | If not found, let them know and offer to try again.
        actions:
            lookup_account: @actions.get_account
                with inp_AccountId=...
                set @variables.account_name = @outputs.out_AccountName
                set @variables.account_industry = @outputs.out_Industry
                set @variables.account_found = @outputs.out_IsFound
```

### Complex Agent with Escalation (Level 5)

```agentscript
start_agent router:
    label: "Router"
    description: "Entry point that determines user intent and routes appropriately"
    reasoning:
        instructions: ->
            | Greet the user and determine their needs.
            | If they want to look up an account, go to account lookup.
            | If they have general questions, go to FAQ.
            | If they need a human, escalate.
        actions:
            go_account_lookup: @utils.transition to @topic.account_lookup
            go_faq: @utils.transition to @topic.faq
            escalate_human: @utils.escalate with reason="Customer requested human agent"

topic account_lookup:
    label: "Account Lookup"
    description: "Helps users find and view account information"

    actions:
        get_account:
            description: "Retrieves account information by ID"
            inputs:
                inp_AccountId: string
                    description: "The Salesforce Account ID to look up"
            outputs:
                out_AccountName: string
                    description: "The account name"
                out_Industry: string
                    description: "The account industry"
                out_IsFound: boolean
                    description: "Whether the account was found"
            target: "flow://Get_Account_Info"

    reasoning:
        instructions: ->
            | Ask for an Account ID if the user hasn't provided one.
            | Look up the account using the get_account action.
            | Share the results with the user.
            | Store the account name: {!@variables.account_name}
            | If they need help with something else, route them.
        actions:
            lookup: @actions.get_account
                with inp_AccountId=...
                set @variables.account_name = @outputs.out_AccountName
                set @variables.account_industry = @outputs.out_Industry
                set @variables.account_found = @outputs.out_IsFound
            go_faq: @utils.transition to @topic.faq
            go_router: @utils.transition to @topic.router
            escalate: @utils.escalate with reason="Customer needs account specialist"

topic faq:
    label: "FAQ"
    description: "Answers frequently asked questions"
    reasoning:
        instructions: ->
            | Answer common questions about accounts and services.
            | Use the customer's name if available: {!@variables.customer_name}
            | If they need account lookup, route to that topic.
            | If you cannot help, escalate to a human.
        actions:
            go_account_lookup: @utils.transition to @topic.account_lookup
            go_router: @utils.transition to @topic.router
            escalate: @utils.escalate with reason="Question requires human expertise"
```

---

## Common Deployment Errors & Solutions

### Error: "Internal Error, try again later"

**Causes:**
1. Invalid `default_agent_user` - user doesn't exist in org
2. User lacks Agentforce permissions
3. Flow referenced by `flow://` not deployed to org
4. Transient server issue

**Solutions:**
```bash
# Verify user exists
sf data query --query "SELECT Id, Username FROM User WHERE Username = 'user@example.com'" --target-org [alias]

# Deploy flows first
sf project deploy start --metadata Flow --target-org [alias]

# Then publish agent
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

### Error: "SyntaxError: Invalid system instructions"

**Cause:** Using pipe `|` syntax in `system.instructions`

**Wrong:**
```agentscript
system:
    instructions:
        | You are helpful.
```

**Correct:**
```agentscript
system:
    instructions: "You are helpful."
```

### Error: "Unexpected 'actions'"

**Cause:** Defining actions at top level instead of inside topics

**Wrong:**
```agentscript
actions:
    my_action:
        target: "flow://MyFlow"

topic my_topic:
    ...
```

**Correct:**
```agentscript
topic my_topic:
    actions:
        my_action:
            target: "flow://MyFlow"
    ...
```

### Error: "ValidationError: default agent user is required"

**Cause:** Missing `default_agent_user` field in config

**Solution:** Add the field:
```agentscript
config:
    developer_name: "My_Agent"
    default_agent_user: "user@example.com"  # Required!
    agent_label: "My Agent"
    description: "Description"
```

### Error: Reserved word conflict

**Cause:** Using reserved words as input/output parameter names

**Reserved Words:**
- `description`
- `inputs`
- `outputs`
- `target`
- `label`
- `source`

**Solution:** Use prefixed alternatives:
```agentscript
# Wrong
inputs:
    description: string

# Correct
inputs:
    case_description: string
```

---

## Deployment Checklist

Before running `sf agent publish authoring-bundle`:

### Files (Metadata API - GenAiPlannerBundle)
- [ ] `.genAiPlannerBundle` XML file exists
- [ ] `.agent` file in `agentScript/` subfolder
- [ ] Both in `force-app/main/default/genAiPlannerBundles/[AgentName]/`
- [ ] `sourceApiVersion: "65.0"` or higher in sfdx-project.json

### Files (Agent Builder DX - authoring-bundle)
- [ ] `.bundle-meta.xml` file exists alongside `.agent`
- [ ] Both in `force-app/main/default/aiAuthoringBundles/[AgentName]/`

### Syntax
- [ ] 4-space indentation (not tabs, not 3 spaces)
- [ ] `developer_name` in config (not `agent_name`)
- [ ] `default_agent_user` set to valid org user
- [ ] `system.instructions` is single quoted string
- [ ] All topics have `label:` and `description:`
- [ ] `instructions: ->` has space before arrow
- [ ] No reserved words as input/output names

### Dependencies
- [ ] Target org has API v64.0+ (v65.0+ for GenAiPlannerBundle deploy)
- [ ] All Flows referenced by `flow://` are deployed
- [ ] All Apex classes referenced by Flows are deployed
- [ ] `default_agent_user` exists in org with Agentforce permissions

### Blocks Present
- [ ] `system:` block (first)
- [ ] `config:` block
- [ ] `variables:` block with linked variables
- [ ] `language:` block
- [ ] `start_agent topic_selector:` entry point
- [ ] At least one additional `topic:`

---

## CLI Commands Quick Reference

### Metadata API Deployment (GenAiPlannerBundle)

```bash
# Deploy agent using standard metadata deploy
sf project deploy start --source-dir force-app/main/default/genAiPlannerBundles/[AgentName] --target-org [alias]

# Deploy all agent bundles
sf project deploy start --metadata GenAiPlannerBundle --target-org [alias]

# Retrieve agent from org
sf project retrieve start --metadata "GenAiPlannerBundle:[AgentName]" --target-org [alias]
```

### Agent Builder DX (authoring-bundle)

```bash
# Validate before publish (optional)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# Publish agent
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]

# Open in Agentforce Studio
sf org open agent --api-name [AgentName] --target-org [alias]

# Activate agent
sf agent activate --api-name [AgentName] --target-org [alias]
```

### Common Commands

```bash
# Deploy dependencies first
sf project deploy start --metadata Flow --target-org [alias]
sf project deploy start --metadata ApexClass --target-org [alias]

# List agents in org
sf org list metadata --metadata-type GenAiPlannerBundle --target-org [alias]
```

---

## Testing Best Practices

1. **Start Simple**: Begin with Level 1 (no actions) to verify basic syntax
2. **Deploy Dependencies First**: Flows and Apex must exist in org before agent publish
3. **Validate Incrementally**: Test each feature addition before combining
4. **Check User Permissions**: Ensure `default_agent_user` has Agentforce permissions
5. **Use Explicit Errors**: If publish fails with "Internal Error", check dependencies first

---

*Last Updated: December 2025*
*Based on systematic testing with SF CLI v2.115.15 and API v65.0*
