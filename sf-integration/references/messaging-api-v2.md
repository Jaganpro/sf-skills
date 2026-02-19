<!-- Parent: sf-integration/SKILL.md -->
   1 # Messaging API v2 Guide (MIAW)
   2 
   3 This guide covers building custom clients for Messaging for In-App and Web (MIAW), enabling Agentforce and Service Cloud conversations outside of Salesforce.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────────┐
  11 │                    MIAW CUSTOM CLIENT ARCHITECTURE                       │
  12 ├─────────────────────────────────────────────────────────────────────────┤
  13 │                                                                          │
  14 │   ┌──────────────┐                              ┌──────────────────┐    │
  15 │   │   Custom     │      REST API v2             │    Salesforce    │    │
  16 │   │   Client     │◀────────────────────────────▶│    MIAW / Agent  │    │
  17 │   │  (React/Vue) │    /iamessage/api/v2/*       │    Service Cloud │    │
  18 │   └──────────────┘                              └──────────────────────┘    │
  19 │                                                                          │
  20 │   Endpoints:                                                             │
  21 │   • POST /authorization           JWT token exchange                     │
  22 │   • POST /conversation            Start conversation                     │
  23 │   • POST /conversation/{id}/message   Send message                       │
  24 │   • GET  /conversation/{id}/messages  Poll for messages (or SSE)         │
  25 │   • POST /conversation/{id}/end       End conversation                   │
  26 │                                                                          │
  27 │   Use Cases:                                                             │
  28 │   • Custom chat widgets on external websites                             │
  29 │   • Mobile app integrations                                              │
  30 │   • Kiosk / in-store experiences                                         │
  31 │   • Third-party platform integrations                                    │
  32 │                                                                          │
  33 └─────────────────────────────────────────────────────────────────────────┘
  34 ```
  35 
  36 ---
  37 
  38 ## Prerequisites
  39 
  40 ### Salesforce Setup
  41 
  42 1. **Messaging for In-App and Web** license
  43 2. **Embedded Service Deployment** created
  44 3. **Agentforce** or **Omni-Channel** routing configured
  45 4. **Connected App** for JWT authentication
  46 
  47 ### Embedded Service Deployment
  48 
  49 ```
  50 Setup → Embedded Service Deployments → New Deployment
  51 ├─ Type: Messaging for In-App and Web
  52 ├─ Channel: Web
  53 └─ API Name: Your_Deployment_API_Name
  54 ```
  55 
  56 Get the **Deployment ID** and **Organization ID** from the deployment settings.
  57 
  58 ---
  59 
  60 ## Authentication
  61 
  62 ### JWT Token Exchange
  63 
  64 MIAW uses JWT bearer tokens for API authentication.
  65 
  66 ```javascript
  67 // Server-side token generation (Node.js example)
  68 import jwt from 'jsonwebtoken';
  69 import fetch from 'node-fetch';
  70 
  71 async function getAccessToken(orgId, deploymentId, privateKey) {
  72     // CRITICAL: OrgId must be 15-character format for JWT
  73     const orgId15 = orgId.substring(0, 15);
  74 
  75     const payload = {
  76         iss: 'YOUR_CONNECTED_APP_CLIENT_ID',
  77         sub: `${orgId15}`,  // 15-char org ID
  78         aud: 'https://login.salesforce.com',
  79         exp: Math.floor(Date.now() / 1000) + 300,  // 5 min expiry
  80         iat: Math.floor(Date.now() / 1000)
  81     };
  82 
  83     const token = jwt.sign(payload, privateKey, { algorithm: 'RS256' });
  84 
  85     // Exchange JWT for access token
  86     const response = await fetch(
  87         'https://login.salesforce.com/services/oauth2/token',
  88         {
  89             method: 'POST',
  90             headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  91             body: new URLSearchParams({
  92                 grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
  93                 assertion: token
  94             })
  95         }
  96     );
  97 
  98     const data = await response.json();
  99     return data.access_token;
 100 }
 101 ```
 102 
 103 ### Authorization Endpoint
 104 
 105 Exchange access token for MIAW-specific authorization:
 106 
 107 ```javascript
 108 async function getMessagingAuth(accessToken, orgDomain, deploymentId) {
 109     const response = await fetch(
 110         `https://${orgDomain}/iamessage/api/v2/authorization`,
 111         {
 112             method: 'POST',
 113             headers: {
 114                 'Authorization': `Bearer ${accessToken}`,
 115                 'Content-Type': 'application/json'
 116             },
 117             body: JSON.stringify({
 118                 orgId: 'YOUR_ORG_ID',
 119                 esDeveloperName: deploymentId,
 120                 capabilitiesVersion: '1',
 121                 platform: 'Web'
 122             })
 123         }
 124     );
 125 
 126     return await response.json();
 127     // Returns: { accessToken, context, ... }
 128 }
 129 ```
 130 
 131 ---
 132 
 133 ## Conversation Lifecycle
 134 
 135 ### Start Conversation
 136 
 137 ```javascript
 138 async function startConversation(messagingAuth, customerName) {
 139     const { accessToken, context } = messagingAuth;
 140 
 141     const response = await fetch(
 142         `https://${context.url}/iamessage/api/v2/conversation`,
 143         {
 144             method: 'POST',
 145             headers: {
 146                 'Authorization': `Bearer ${accessToken}`,
 147                 'Content-Type': 'application/json'
 148             },
 149             body: JSON.stringify({
 150                 esDeveloperName: context.esDeveloperName,
 151                 routingAttributes: {
 152                     // Optional: Pre-chat fields
 153                     customerName: customerName
 154                 },
 155                 // Optional: Context for agent
 156                 contextParameters: {
 157                     recordId: '001xx000003ABC',
 158                     caseReason: 'Technical Support'
 159                 }
 160             })
 161         }
 162     );
 163 
 164     const data = await response.json();
 165     return data.conversationId;
 166 }
 167 ```
 168 
 169 ### Send Message
 170 
 171 ```javascript
 172 async function sendMessage(messagingAuth, conversationId, text) {
 173     const { accessToken, context } = messagingAuth;
 174 
 175     const response = await fetch(
 176         `https://${context.url}/iamessage/api/v2/conversation/${conversationId}/message`,
 177         {
 178             method: 'POST',
 179             headers: {
 180                 'Authorization': `Bearer ${accessToken}`,
 181                 'Content-Type': 'application/json'
 182             },
 183             body: JSON.stringify({
 184                 message: {
 185                     messageType: 'StaticContentMessage',
 186                     staticContent: {
 187                         formatType: 'Text',
 188                         text: text
 189                     }
 190                 }
 191             })
 192         }
 193     );
 194 
 195     return await response.json();
 196 }
 197 ```
 198 
 199 ### Receive Messages
 200 
 201 #### Option 1: Server-Sent Events (SSE)
 202 
 203 SSE provides real-time streaming but may not work on serverless platforms.
 204 
 205 ```javascript
 206 function subscribeToMessages(messagingAuth, conversationId, onMessage) {
 207     const { accessToken, context } = messagingAuth;
 208 
 209     const eventSource = new EventSource(
 210         `https://${context.url}/iamessage/api/v2/conversation/${conversationId}/messages?stream=true`,
 211         {
 212             headers: {
 213                 'Authorization': `Bearer ${accessToken}`
 214             }
 215         }
 216     );
 217 
 218     eventSource.onmessage = (event) => {
 219         const message = JSON.parse(event.data);
 220         onMessage(message);
 221     };
 222 
 223     eventSource.onerror = (error) => {
 224         console.error('SSE error:', error);
 225         // Fallback to polling
 226     };
 227 
 228     return eventSource;
 229 }
 230 ```
 231 
 232 #### Option 2: Polling (Serverless Compatible)
 233 
 234 For Vercel, AWS Lambda, or other serverless environments:
 235 
 236 ```javascript
 237 class MessagePoller {
 238     constructor(messagingAuth, conversationId, onMessage) {
 239         this.messagingAuth = messagingAuth;
 240         this.conversationId = conversationId;
 241         this.onMessage = onMessage;
 242         this.lastMessageId = null;
 243         this.seenMessageIds = new Set();
 244         this.intervalId = null;
 245     }
 246 
 247     start(intervalMs = 2000) {
 248         this.intervalId = setInterval(() => this.poll(), intervalMs);
 249         this.poll(); // Immediate first poll
 250     }
 251 
 252     stop() {
 253         if (this.intervalId) {
 254             clearInterval(this.intervalId);
 255             this.intervalId = null;
 256         }
 257     }
 258 
 259     async poll() {
 260         const { accessToken, context } = this.messagingAuth;
 261 
 262         try {
 263             const url = new URL(
 264                 `https://${context.url}/iamessage/api/v2/conversation/${this.conversationId}/messages`
 265             );
 266             if (this.lastMessageId) {
 267                 url.searchParams.set('after', this.lastMessageId);
 268             }
 269 
 270             const response = await fetch(url, {
 271                 headers: { 'Authorization': `Bearer ${accessToken}` }
 272             });
 273 
 274             const data = await response.json();
 275 
 276             for (const message of data.messages || []) {
 277                 // CRITICAL: Deduplicate messages
 278                 if (!this.seenMessageIds.has(message.id)) {
 279                     this.seenMessageIds.add(message.id);
 280                     this.lastMessageId = message.id;
 281                     this.onMessage(message);
 282                 }
 283             }
 284         } catch (error) {
 285             console.error('Poll error:', error);
 286         }
 287     }
 288 }
 289 ```
 290 
 291 ### End Conversation
 292 
 293 ```javascript
 294 async function endConversation(messagingAuth, conversationId) {
 295     const { accessToken, context } = messagingAuth;
 296 
 297     await fetch(
 298         `https://${context.url}/iamessage/api/v2/conversation/${conversationId}/end`,
 299         {
 300             method: 'POST',
 301             headers: {
 302                 'Authorization': `Bearer ${accessToken}`,
 303                 'Content-Type': 'application/json'
 304             }
 305         }
 306     );
 307 }
 308 ```
 309 
 310 ---
 311 
 312 ## Message Types
 313 
 314 ### Incoming Message Structure
 315 
 316 ```javascript
 317 {
 318     "id": "msg_abc123",
 319     "conversationId": "conv_xyz789",
 320     "messageType": "StaticContentMessage",
 321     "sender": {
 322         "role": "Agent",  // or "EndUser", "Chatbot"
 323         "displayName": "Service Agent"
 324     },
 325     "staticContent": {
 326         "formatType": "Text",
 327         "text": "Hello! How can I help you today?"
 328     },
 329     "timestamp": "2026-01-15T10:30:00.000Z"
 330 }
 331 ```
 332 
 333 ### Rich Message Types
 334 
 335 | Type | Use Case |
 336 |------|----------|
 337 | `StaticContentMessage` | Plain text |
 338 | `RichLinkMessage` | Clickable cards with images |
 339 | `ListPickerMessage` | Selection lists |
 340 | `QuickReplyMessage` | Suggested responses |
 341 | `AttachmentMessage` | File attachments |
 342 
 343 ### Handling Rich Messages
 344 
 345 ```javascript
 346 function renderMessage(message) {
 347     switch (message.messageType) {
 348         case 'StaticContentMessage':
 349             return renderText(message.staticContent.text);
 350 
 351         case 'QuickReplyMessage':
 352             return renderQuickReplies(message.quickReplies);
 353 
 354         case 'ListPickerMessage':
 355             return renderListPicker(message.listPicker);
 356 
 357         case 'RichLinkMessage':
 358             return renderRichLink(message.richLink);
 359 
 360         default:
 361             console.warn('Unknown message type:', message.messageType);
 362             return null;
 363     }
 364 }
 365 
 366 function renderQuickReplies(quickReplies) {
 367     return quickReplies.replies.map(reply => ({
 368         label: reply.title,
 369         value: reply.itemId,
 370         onClick: () => sendQuickReplySelection(reply.itemId)
 371     }));
 372 }
 373 ```
 374 
 375 ---
 376 
 377 ## React Integration Example
 378 
 379 ```jsx
 380 // ChatWidget.jsx
 381 import { useState, useEffect, useRef } from 'react';
 382 
 383 export function ChatWidget({ orgDomain, deploymentId }) {
 384     const [messages, setMessages] = useState([]);
 385     const [inputText, setInputText] = useState('');
 386     const [conversationId, setConversationId] = useState(null);
 387     const [isConnecting, setIsConnecting] = useState(false);
 388     const pollerRef = useRef(null);
 389     const authRef = useRef(null);
 390 
 391     // Initialize conversation
 392     const startChat = async () => {
 393         setIsConnecting(true);
 394         try {
 395             // Get auth from your backend
 396             const authResponse = await fetch('/api/messaging/auth', {
 397                 method: 'POST',
 398                 body: JSON.stringify({ deploymentId })
 399             });
 400             authRef.current = await authResponse.json();
 401 
 402             // Start conversation
 403             const convId = await startConversation(authRef.current, 'Web User');
 404             setConversationId(convId);
 405 
 406             // Start polling for messages
 407             pollerRef.current = new MessagePoller(
 408                 authRef.current,
 409                 convId,
 410                 handleNewMessage
 411             );
 412             pollerRef.current.start();
 413         } catch (error) {
 414             console.error('Failed to start chat:', error);
 415         } finally {
 416             setIsConnecting(false);
 417         }
 418     };
 419 
 420     const handleNewMessage = (message) => {
 421         setMessages(prev => [...prev, message]);
 422     };
 423 
 424     const handleSend = async () => {
 425         if (!inputText.trim() || !conversationId) return;
 426 
 427         // Optimistic update
 428         const localMessage = {
 429             id: `local_${Date.now()}`,
 430             sender: { role: 'EndUser' },
 431             staticContent: { text: inputText },
 432             timestamp: new Date().toISOString()
 433         };
 434         setMessages(prev => [...prev, localMessage]);
 435         setInputText('');
 436 
 437         // Send to server
 438         await sendMessage(authRef.current, conversationId, inputText);
 439     };
 440 
 441     // Cleanup
 442     useEffect(() => {
 443         return () => {
 444             if (pollerRef.current) {
 445                 pollerRef.current.stop();
 446             }
 447         };
 448     }, []);
 449 
 450     return (
 451         <div className="chat-widget">
 452             {!conversationId ? (
 453                 <button onClick={startChat} disabled={isConnecting}>
 454                     {isConnecting ? 'Connecting...' : 'Start Chat'}
 455                 </button>
 456             ) : (
 457                 <>
 458                     <div className="messages">
 459                         {messages.map(msg => (
 460                             <MessageBubble key={msg.id} message={msg} />
 461                         ))}
 462                     </div>
 463                     <input
 464                         value={inputText}
 465                         onChange={(e) => setInputText(e.target.value)}
 466                         onKeyPress={(e) => e.key === 'Enter' && handleSend()}
 467                         placeholder="Type a message..."
 468                     />
 469                     <button onClick={handleSend}>Send</button>
 470                 </>
 471             )}
 472         </div>
 473     );
 474 }
 475 ```
 476 
 477 ---
 478 
 479 ## Common Gotchas
 480 
 481 ### 1. OrgId Format
 482 
 483 ```javascript
 484 // ❌ WRONG: Using 18-character OrgId in JWT
 485 const orgId = '00D5g000004ABCDEFGH'; // 18 chars
 486 
 487 // ✅ CORRECT: Use 15-character format for JWT
 488 const orgId15 = orgId.substring(0, 15); // '00D5g000004ABCD'
 489 ```
 490 
 491 ### 2. Message Deduplication
 492 
 493 Polling can return the same messages multiple times:
 494 
 495 ```javascript
 496 // ❌ WRONG: No deduplication
 497 messages.forEach(msg => onMessage(msg));
 498 
 499 // ✅ CORRECT: Track seen message IDs
 500 if (!this.seenMessageIds.has(message.id)) {
 501     this.seenMessageIds.add(message.id);
 502     onMessage(message);
 503 }
 504 ```
 505 
 506 ### 3. SSE on Serverless
 507 
 508 SSE connections won't work on serverless platforms:
 509 
 510 ```javascript
 511 // ❌ WRONG: SSE on Vercel/Netlify Functions
 512 const eventSource = new EventSource(url); // Connection dies immediately
 513 
 514 // ✅ CORRECT: Use polling fallback
 515 const poller = new MessagePoller(auth, convId, onMessage);
 516 poller.start(2000);
 517 ```
 518 
 519 ### 4. Token Refresh
 520 
 521 Access tokens expire; implement refresh logic:
 522 
 523 ```javascript
 524 class MessagingClient {
 525     constructor() {
 526         this.auth = null;
 527         this.tokenExpiry = null;
 528     }
 529 
 530     async ensureValidToken() {
 531         const now = Date.now();
 532         const buffer = 60000; // 1 minute buffer
 533 
 534         if (!this.auth || now >= this.tokenExpiry - buffer) {
 535             this.auth = await this.refreshAuth();
 536             this.tokenExpiry = now + (this.auth.expiresIn * 1000);
 537         }
 538 
 539         return this.auth;
 540     }
 541 
 542     async sendMessage(conversationId, text) {
 543         const auth = await this.ensureValidToken();
 544         // ... send with valid token
 545     }
 546 }
 547 ```
 548 
 549 ---
 550 
 551 ## Security Best Practices
 552 
 553 | Practice | Implementation |
 554 |----------|----------------|
 555 | Never expose private keys | Keep JWT signing server-side only |
 556 | Use short-lived tokens | 5-15 minute expiry for JWTs |
 557 | Validate conversation ownership | Server tracks user → conversation mapping |
 558 | Rate limit messages | Prevent spam/abuse |
 559 | Sanitize message content | XSS prevention on display |
 560 
 561 ---
 562 
 563 ## Deployment Platforms
 564 
 565 ### Vercel
 566 
 567 ```javascript
 568 // api/messaging/auth.js
 569 export default async function handler(req, res) {
 570     // Server-side auth - never expose keys to client
 571     const auth = await getMessagingAuth(
 572         process.env.SF_ACCESS_TOKEN,
 573         process.env.SF_ORG_DOMAIN,
 574         req.body.deploymentId
 575     );
 576 
 577     res.json(auth);
 578 }
 579 ```
 580 
 581 ### AWS Lambda
 582 
 583 ```javascript
 584 // handler.js
 585 exports.startConversation = async (event) => {
 586     const { deploymentId, customerName } = JSON.parse(event.body);
 587 
 588     const auth = await getMessagingAuth(/* ... */);
 589     const conversationId = await startConversation(auth, customerName);
 590 
 591     return {
 592         statusCode: 200,
 593         body: JSON.stringify({ conversationId })
 594     };
 595 };
 596 ```
 597 
 598 ---
 599 
 600 ## Cross-Skill References
 601 
 602 | Topic | Resource |
 603 |-------|----------|
 604 | Connected Apps setup | [sf-connected-apps skill](../../sf-connected-apps/SKILL.md) |
 605 | Named Credentials | [named-credentials-guide.md](named-credentials-guide.md) |
 606 | Agentforce agents | [sf-ai-agentforce skill](../../sf-ai-agentforce/SKILL.md) |
 607 | Platform Events | [platform-events-guide.md](platform-events-guide.md) |
 608 | REST callout patterns | [rest-callout-patterns.md](rest-callout-patterns.md) |
