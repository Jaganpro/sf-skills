<!-- Parent: sf-ai-agentscript/SKILL.md -->
# Agent User Setup & Permission Model

> Complete provisioning workflow for Einstein Agent Users and permission sets. Validated against ORM1, ORM2, and AutomotiveSupport agents.

---

## Agent Type Decision Matrix

| Aspect | AgentforceServiceAgent | AgentforceEmployeeAgent |
|--------|------------------------|-------------------------|
| **Use Case** | Customer-facing, external users | Internal employees |
| **Runs As** | Dedicated Einstein Agent User | Logged-in user |
| **Einstein Agent User?** | Required | Not needed |
| **System PS (`AgentforceServiceAgentUser`)** | Required | Not needed |
| **Custom PS (`{AgentName}_Access`)** | Assigned to agent user | Assigned to employees |
| **`default_agent_user` in config** | Required | Omit entirely |
| **Respects Sharing Rules** | No (consistent permissions) | Yes (user's data access) |

> **How to check agent type**: Look at the `agent_type` field in the `config:` block of your `.agent` file, or query: `sf data query --query "SELECT DeveloperName, Type FROM BotDefinition WHERE DeveloperName = 'AgentName'" -o TARGET_ORG --json`

---

## Service Agent Setup (6 Steps)

### Step 1: Create Einstein Agent User

Service agents need a dedicated service account with consistent permissions.

**Get Org ID first** (needed for username format):
```bash
sf org display -o TARGET_ORG --json | jq -r '.result.id'
```

**Query existing Einstein Agent Users** (skip creation if one exists):
```bash
sf data query --query "SELECT Id, Username, IsActive FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true" -o TARGET_ORG --json
```

**Create the user** (if none exists):

1. Get the Einstein Agent User profile ID:
   ```bash
   sf data query --query "SELECT Id FROM Profile WHERE Name = 'Einstein Agent User'" -o TARGET_ORG --json
   ```

2. Create a user definition file (`/tmp/agent-user.json`):
   ```json
   {
     "Username": "{agent_name}_agent@{orgId}.ext",
     "LastName": "{AgentName} Agent",
     "Email": "placeholder@example.com",
     "Alias": "agntuser",
     "ProfileId": "<profile-id-from-step-1>",
     "TimeZoneSidKey": "America/Los_Angeles",
     "LocaleSidKey": "en_US",
     "EmailEncodingKey": "UTF-8",
     "LanguageLocaleKey": "en_US"
   }
   ```

3. Create the user:
   ```bash
   sf data create record --sobject User --values "Username='{agent_name}_agent@{orgId}.ext' LastName='{AgentName} Agent' Email='placeholder@example.com' Alias='agntuser' ProfileId='<profile-id>' TimeZoneSidKey='America/Los_Angeles' LocaleSidKey='en_US' EmailEncodingKey='UTF-8' LanguageLocaleKey='en_US'" -o TARGET_ORG --json
   ```

4. Verify creation:
   ```bash
   sf data query --query "SELECT Id, Username, IsActive FROM User WHERE Username = '{agent_name}_agent@{orgId}.ext'" -o TARGET_ORG --json
   ```

> **Username format**: `{agent_name}_agent@{orgId}.ext` (production) or `{agent_name}.{suffix}@{orgfarm}.salesforce.com` (dev/scratch). Always query the target org to confirm the exact format.

---

### Step 2: Assign System Permission Set (`AgentforceServiceAgentUser`)

**CRITICAL**: Must be assigned BEFORE publishing the agent. Without it, publish fails with "Internal Error".

**Via Setup UI:**
1. Setup > Permission Sets > search "AgentforceServiceAgentUser"
2. Manage Assignments > Add Assignments > select the Einstein Agent User > Save

**Via CLI:**
```bash
sf org assign permset --name AgentforceServiceAgentUser --on-behalf-of "{agent_name}_agent@{orgId}.ext" -o TARGET_ORG --json
```

**Verify assignment:**
```bash
sf data query --query "SELECT Id, PermissionSet.Name FROM PermissionSetAssignment WHERE Assignee.Username = '{agent_name}_agent@{orgId}.ext' AND PermissionSet.Name = 'AgentforceServiceAgentUser'" -o TARGET_ORG --json
```

---

### Step 3: Create Custom Permission Set for Apex Classes

The custom PS grants the agent user permission to execute your Apex invocable actions.

**Naming convention**: `{AgentName}_Access` (e.g., `AutomotiveSupport_Access`)

**File**: `force-app/main/default/permissionsets/{AgentName}_Access.permissionset-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Grants access to {AgentName} Agent Apex classes</description>
    <hasActivationRequired>false</hasActivationRequired>
    <label>{AgentName} Access</label>

    <!-- Add one entry per Apex class the agent calls -->
    <classAccesses>
        <apexClass>YourApexClassName</apexClass>
        <enabled>true</enabled>
    </classAccesses>
    <!-- Repeat for ALL Apex classes referenced via apex:// in agent script -->
</PermissionSet>
```

**Key rule**: Include EVERY Apex class referenced via `apex://` in your agent script. Missing even one causes "invocable action does not exist" at runtime.

**Deploy the permission set:**
```bash
sf project deploy start --source-dir force-app/main/default/permissionsets/{AgentName}_Access.permissionset-meta.xml -o TARGET_ORG --json
```

---

### Step 4: Assign Custom Permission Set to Agent User

**Via CLI:**
```bash
sf org assign permset --name {AgentName}_Access --on-behalf-of "{agent_name}_agent@{orgId}.ext" -o TARGET_ORG --json
```

**Verify both permission sets are assigned:**
```bash
sf data query --query "SELECT PermissionSet.Name FROM PermissionSetAssignment WHERE Assignee.Username = '{agent_name}_agent@{orgId}.ext'" -o TARGET_ORG --json
```

Expected output should include both:
- `AgentforceServiceAgentUser` (system)
- `{AgentName}_Access` (custom)

---

### Step 5: Set `default_agent_user` in Agent Config

In your `.agent` file:
```yaml
config:
  developer_name: "AgentName"
  agent_description: "Your agent description"
  agent_type: "AgentforceServiceAgent"
  default_agent_user: "{agent_name}_agent@{orgId}.ext"  # Service agents ONLY
```

---

### Step 6: Publish Agent

```bash
sf agent publish authoring-bundle --api-name AgentName -o TARGET_ORG --json
```

If publish fails with "Internal Error", verify Steps 1-5 using the verification checklist below.

---

## Employee Agent Setup

Employee agents run as the logged-in user. The permission model is simpler.

### What You DO NOT Need

- No Einstein Agent User creation
- No `AgentforceServiceAgentUser` system permission set
- No `default_agent_user` in agent config

### What You DO Need

Custom permission set(s) assigned to **employees** who will use the agent.

### Step 1: Create Custom Permission Set

Same XML template as Step 3 above. Include `<classAccesses>` for all Apex classes the agent calls.

### Step 2: Assign to Employees

Assign the custom PS to employees (not to a service account):

```bash
sf org assign permset --name {AgentName}_Access --on-behalf-of "employee@company.com" -o TARGET_ORG --json
```

Or use Permission Set Groups for role-based access.

### Step 3: Configure Agent Script (No `default_agent_user`)

```yaml
config:
  developer_name: "Employee_Agent"
  agent_description: "Internal employee assistant"
  agent_type: "AgentforceEmployeeAgent"
  # NO default_agent_user — agent runs as logged-in user
```

### Step 4: Publish

```bash
sf agent publish authoring-bundle --api-name Employee_Agent -o TARGET_ORG --json
```

---

## Auto-Generated Permission Set Warning

Salesforce auto-generates `NextGen_{AgentName}_Permissions` when an agent is published. **Do NOT rely on this PS.** It is often incomplete.

**ORM1 testing example:**
- Agent script referenced 4 Apex classes: `OrderManagementVerification`, `FraudRiskCalculator`, `OrderLookupService`, `ShipmentTracker`
- Auto-generated `NextGen_ORM1_Permissions` only included 3 classes (missing `ShipmentTracker`)
- Runtime error: "invocable action track_delivery does not exist"
- Fix: Created custom `ORM1_Access` with all 4 classes — no errors

**Best practice**: Always create your own custom `{AgentName}_Access` PS with explicit `<classAccesses>` for every Apex class. Ignore the auto-generated PS.

---

## End-to-End Verification Checklist

Run this combined query to verify all setup steps for a Service Agent:

```bash
# 1. Einstein Agent User exists and is active
sf data query --query "SELECT Id, Username, IsActive, Profile.Name FROM User WHERE Username = '{agent_name}_agent@{orgId}.ext'" -o TARGET_ORG --json

# 2. System PS assigned
sf data query --query "SELECT PermissionSet.Name FROM PermissionSetAssignment WHERE Assignee.Username = '{agent_name}_agent@{orgId}.ext' AND PermissionSet.Name = 'AgentforceServiceAgentUser'" -o TARGET_ORG --json

# 3. Custom PS assigned
sf data query --query "SELECT PermissionSet.Name FROM PermissionSetAssignment WHERE Assignee.Username = '{agent_name}_agent@{orgId}.ext' AND PermissionSet.Name = '{AgentName}_Access'" -o TARGET_ORG --json

# 4. All permission sets for user (combined view)
sf data query --query "SELECT PermissionSet.Name, PermissionSet.Label FROM PermissionSetAssignment WHERE Assignee.Username = '{agent_name}_agent@{orgId}.ext'" -o TARGET_ORG --json

# 5. Agent config has default_agent_user
# Check your .agent file's config: block

# 6. Agent publishes successfully
sf agent publish authoring-bundle --api-name AgentName -o TARGET_ORG --json
```

**Checklist:**
- [ ] Einstein Agent User created and active (`IsActive = true`)
- [ ] Profile is "Einstein Agent User" (or "Minimum Access - Salesforce")
- [ ] `AgentforceServiceAgentUser` system PS assigned
- [ ] Custom `{AgentName}_Access` PS deployed with ALL Apex classes
- [ ] Custom PS assigned to the agent user
- [ ] `default_agent_user` set in `.agent` config block
- [ ] Agent publishes without error

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| "Internal Error" on publish | `AgentforceServiceAgentUser` PS not assigned to Einstein Agent User | Assign system PS (Step 2), wait 2-3 min, retry publish |
| "Insufficient Privileges" at runtime | Custom PS missing or incomplete `<classAccesses>` | Verify custom PS includes ALL Apex classes, redeploy + reassign |
| "invocable action does not exist" | Apex class not in custom PS (auto-generated PS incomplete) | Create custom `{AgentName}_Access` with all `<classAccesses>` (Step 3) |
| "Invalid default_agent_user" | Username typo or user not active | Query Einstein Agent Users, verify exact username + `IsActive = true` |
| Agent runs but returns wrong data | Employee agent using wrong user context | Verify `agent_type` — Service agents use dedicated user, Employee agents use logged-in user |

---

## Permission Set XML Template (Complete Example)

**AutomotiveSupport agent** (5 Apex classes):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Grants access to Automotive Support Agent Apex classes</description>
    <hasActivationRequired>false</hasActivationRequired>
    <label>Automotive Support Access</label>

    <classAccesses>
        <apexClass>VehicleLookupService</apexClass>
        <enabled>true</enabled>
    </classAccesses>
    <classAccesses>
        <apexClass>ErrorCodeDiagnosticsService</apexClass>
        <enabled>true</enabled>
    </classAccesses>
    <classAccesses>
        <apexClass>CheckEngineDiagnosticsService</apexClass>
        <enabled>true</enabled>
    </classAccesses>
    <classAccesses>
        <apexClass>BehaviorAnalysisService</apexClass>
        <enabled>true</enabled>
    </classAccesses>
    <classAccesses>
        <apexClass>ServiceSchedulerService</apexClass>
        <enabled>true</enabled>
    </classAccesses>
</PermissionSet>
```

---

*Validated against: ORM1, ORM2, AutomotiveSupport agents. Last updated: 2026-03-07.*
