# Agentforce Mobile SDK & Web Chat Reference

Integration guides for embedding Agentforce agents in native mobile apps, React Native, and web chat.

> Official docs: [Agentforce Mobile SDK](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk.html)

## Overview

The Agentforce Mobile SDK provides native UI components for iOS, Android, and React Native to embed agent conversations in mobile apps. It supports two agent modes:

| Mode | Auth | Use Case |
|------|------|----------|
| **Service Agent** | None (anonymous) | Customer-facing support |
| **Employee Agent** | OAuth via Salesforce Mobile SDK | Internal/authenticated use |

---

## Platform SDKs

### iOS
- Package: [AgentforceMobileSDK-iOS](https://github.com/salesforce/AgentforceMobileSDK-iOS) (CocoaPods)
- Guide: [iOS Integration Guide](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-ios-integration-overview.html)
- Quick Start: [iOS Quick Start](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-ios-quick-start.html)

### Android
- Package: [AgentforceMobileSDK-Android](https://github.com/salesforce/AgentforceMobileSDK-Android) (Maven)
- Guide: [Android Integration Guide](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-android-integration-overview.html)
- Quick Start: [Android Quick Start](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-android-quick-start.html)

### React Native
- Bridge to native iOS/Android SDKs with JavaScript API
- Guide: [React Native Integration Guide](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-integration-overview.html)
- Quick Start: [React Native Quick Start](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-quick-start.html)

---

## Org Values by Agent Type

### Service Agent
Gather from Salesforce Setup:

| Value | Location |
|-------|----------|
| Service API URL | Setup → Embedded Service Deployments → your deployment → Settings |
| Organization ID | Setup → Company Information |
| ES Developer Name | Setup → Embedded Service Deployments → Developer Name |

### Employee Agent
Gather from Salesforce Setup:

| Value | Location |
|-------|----------|
| Agent ID | Agent Details page URL (18-char ID at end) |
| User ID | User profile page. See [Find User ID](https://help.salesforce.com/s/articleView?id=000381643&type=1) |
| Salesforce Domain | Setup → My Domain → Current My Domain URL |

---

## React Native Quick Start (Service Agent)

### Prerequisites
- Salesforce org with Agentforce enabled
- Service Agent configured (Setup → Embedded Service Deployments)
- Service API URL, Organization ID, and ES Developer Name from org

### 1. Install

```bash
npm install @salesforce/react-native-agentforce
```

### 2. iOS Setup

In `ios/Podfile`, add the bridge pod then install:

```bash
cd ios && pod install
```

### 3. Android Setup

In `android/app/build.gradle`, add Maven repositories for the SDK.

Register the native package in `MainApplication.kt`.

Add the conversation activity to `AndroidManifest.xml`.

### 4. Minimal Service Agent Component

```tsx
import { AgentforceSDK } from '@salesforce/react-native-agentforce';

function ChatButton() {
  const startChat = async () => {
    // Configure with org values
    AgentforceSDK.configure({
      serviceApiUrl: 'YOUR_SERVICE_API_URL',
      organizationId: 'YOUR_ORG_ID',
      esDeveloperName: 'YOUR_ES_DEVELOPER_NAME',
    });
    // Launch full-screen conversation UI
    AgentforceSDK.startConversation();
  };

  return <Button title="Chat with Agent" onPress={startChat} />;
}
```

When tapped: SDK configures with org details → full-screen conversation UI → user chats with agent.

### React Native Features

| Feature | Description |
|---------|-------------|
| Feature Flags | Toggle multi-agent, voice, camera, PDF upload |
| Hidden Prechat Fields | Pre-populate form data for Service Agent sessions |
| Additional Context | Pass contextual variables to personalize responses |
| Delegates | Logger, navigation, and custom view provider callbacks |

### Key React Native Topics
- [Requirements](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-requirements.html)
- [Installation](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-install.html)
- [Configuration](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-integration.html)
- [Conversations](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-conversations.html)
- [Delegates](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-delegates.html)
- [Employee Auth](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-employee-auth.html)
- [Limitations](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-limitations.html)
- [Troubleshooting](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-sdk-react-native-troubleshooting.html)

---

## Enhanced Chat v2 (Web)

> Official docs: [Get Started with Enhanced Chat v2](https://developer.salesforce.com/docs/ai/agentforce/guide/get-started-enhanced-chat.html)

Enhanced Chat v2 is a customer interface for deploying Service agents to external web chat channels.

**Key features:**
- Customizable UI via [Lightning Types](https://developer.salesforce.com/docs/ai/agentforce/guide/enhanced-chat-lightning-types.html)
- Context passing via `utilAPI.setSessionContext()`
- Human-in-the-loop escalation from agent to human rep
- Two display modes: floating (default) and inline

**Not the same as** Enhanced Web Chat (the predecessor).

### Setup

1. Setup → Embedded Service Deployments → select deployment
2. Click **Code Snippet**
3. Add snippet to your web page

### Inline Mode

Renders the chat client directly within a `<div>` instead of a floating button. The chat fills the target element entirely.

```javascript
// Enable inline mode
embeddedservice_bootstrap.settings.displayMode = 'inline';

// Specify target container
embeddedservice_bootstrap.settings.targetElement = document.getElementById('chat-container');
```

**Configuration rules:**
- `displayMode = 'inline'` requires a custom `targetElement` (not `document.body`)
- If `targetElement` is set but `displayMode` is not `'inline'`, the chat button floats within that container
- Header can be toggled on/off in inline mode

**Console warnings:**
| Warning | Fix |
|---------|-----|
| `displayMode is set to "inline" but targetElement is using the default` | Set `targetElement` to a custom container |
| `targetElement is set to a custom element but displayMode is not set to "inline"` | Either set `displayMode = 'inline'` or remove custom `targetElement` |

### Context Events

Pass context to the agent via the `setSessionContext` method on `utilAPI`:

```javascript
embeddedservice_bootstrap.utilAPI.setSessionContext({
  key: 'value'
});
```

See the [Enhanced Chat Developer Guide](https://developer.salesforce.com/docs/ai/agentforce/guide/get-started-enhanced-chat.html) and [Enhanced Chat Reference](https://developer.salesforce.com/docs/ai/agentforce/references/enhanced-chat) for full API.

---

## Enhanced In-App Chat SDK

For Service Cloud in-app mobile chat:
- [Documentation](https://developer.salesforce.com/docs/service/messaging-in-app/guide/introduction.html)
- Customizable messaging inside native apps
- Seamless escalation with full conversation context
