<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Conversation Patterns for Agentforce
   2 
   3 This guide maps IBM's Natural Conversation Framework patterns to Salesforce Agentforce implementations. Each pattern represents a fundamental conversation structure that solves specific user needs.
   4 
   5 ---
   6 
   7 ## Pattern 1: Q&A (Question & Answer)
   8 
   9 ### Description
  10 
  11 The simplest conversation pattern—user asks a question, agent provides an answer. Typically one turn, drawing from a knowledge base or deterministic data source.
  12 
  13 **Best for:**
  14 - Knowledge article retrieval
  15 - FAQ responses
  16 - Status lookups (order status, case status)
  17 - Policy/procedure queries
  18 
  19 ### Agentforce Implementation
  20 
  21 **Topic Configuration:**
  22 ```yaml
  23 Topic: Product FAQs
  24 Classification Description: |
  25   Customer asks questions about product features, specifications,
  26   pricing, compatibility, or availability. Includes questions like
  27   "What does X do?", "How much does Y cost?", "Is Z compatible with...?"
  28 
  29 Scope: Questions seeking factual information about products
  30 ```
  31 
  32 **Actions:**
  33 - **Search Knowledge Base** — Salesforce Knowledge article retrieval
  34 - **Get Product Details** — Autolaunched Flow reading Product2/PricebookEntry
  35 - **Check Inventory** — Real-time availability lookup
  36 
  37 **Instructions (Topic-Level):**
  38 ```
  39 Provide direct, concise answers to product questions. If multiple
  40 articles match, offer the top 3 results and ask which is most relevant.
  41 When inventory is low, mention availability without using urgent language.
  42 Always cite the Knowledge article ID when referencing documentation.
  43 ```
  44 
  45 ### Conversation Example
  46 
  47 ```
  48 User: What's the return policy for electronics?
  49 
  50 Agent: Electronics can be returned within 30 days of purchase with original
  51        packaging and receipt. The item must be unused and include all
  52        accessories.
  53 
  54        Refunds are processed within 5-7 business days after we receive
  55        the return.
  56 
  57        [Source: Knowledge Article KA-03482]
  58 
  59        Would you like instructions on how to start a return?
  60 ```
  61 
  62 ### Common Pitfalls
  63 
  64 | Pitfall | Impact | Fix |
  65 |---------|--------|-----|
  66 | **Returning full article text** | Information overload, poor UX | Summarize key points, offer "Would you like more details?" |
  67 | **No follow-up offer** | Missed engagement | End with action-oriented question |
  68 | **Multiple topics for simple FAQs** | Maintenance overhead | Use one "General FAQs" topic with many Knowledge actions |
  69 | **Hard-coded answers in instructions** | Stale data, hard to update | Always use Knowledge actions or Flow data lookups |
  70 
  71 ### Topic Boundaries
  72 
  73 **In Scope:**
  74 - Factual questions with definitive answers
  75 - Single-turn exchanges
  76 - Information retrieval
  77 
  78 **Out of Scope:**
  79 - Multi-step processes (use Information Gathering pattern)
  80 - Troubleshooting requiring diagnosis (use Troubleshooting pattern)
  81 - Requests requiring human judgment (use Handoff pattern)
  82 
  83 ---
  84 
  85 ## Pattern 2: Information Gathering
  86 
  87 ### Description
  88 
  89 Multi-turn conversation collecting data to complete a task. Agent asks questions sequentially, validates responses, and uses collected data to trigger an action (create record, start process, etc.).
  90 
  91 **Best for:**
  92 - Case creation
  93 - Lead qualification
  94 - Survey/feedback collection
  95 - Appointment booking
  96 
  97 ### Agentforce Implementation
  98 
  99 **Topic Configuration:**
 100 ```yaml
 101 Topic: Create Support Case
 102 Classification Description: |
 103   Customer wants to report a problem, open a support ticket, or
 104   request help with an issue. Includes phrases like "I need help",
 105   "Something's wrong", "Create a case", "Report an issue".
 106 
 107 Scope: Requests to document and track a problem requiring support
 108 ```
 109 
 110 **Actions:**
 111 - **Collect Case Details** — Autolaunched Flow with Input Variables (Subject, Description, Priority)
 112 - **Validate Product Serial** — Apex action checking warranty status
 113 - **Create Case Record** — Flow creating Case with gathered data
 114 - **Send Confirmation** — Flow sending email with case number
 115 
 116 **Instructions (Topic-Level):**
 117 ```
 118 Gather case details through natural conversation, not interrogation.
 119 Required fields: Subject (brief description), Description (detailed context),
 120 Product (from picklist), Priority (Low/Medium/High).
 121 
 122 Ask for information you don't have yet, but don't re-ask questions if the
 123 customer already provided the answer earlier in the conversation.
 124 
 125 After creating the case, confirm the case number and set expectations
 126 for response time based on priority.
 127 ```
 128 
 129 **Instructions (Action-Level: Collect Case Details):**
 130 ```
 131 Use this action when you have Subject, Description, Product, and Priority.
 132 Don't call this action multiple times—wait until all required data is collected.
 133 If the customer mentions urgency keywords (down, critical, outage), default
 134 Priority to High.
 135 ```
 136 
 137 ### Conversation Example
 138 
 139 ```
 140 User: I need help, my software keeps crashing.
 141 
 142 Agent: I'm sorry to hear that! I'll create a support case to get this resolved.
 143 
 144        Which product are you experiencing issues with?
 145 
 146 User: The mobile app on iOS.
 147 
 148 Agent: Got it. Can you describe what happens when it crashes? For example,
 149        does it happen when you open the app, or during a specific action?
 150 
 151 User: It crashes whenever I try to upload a photo.
 152 
 153 Agent: Thank you. How urgent is this issue for you—is it blocking your work,
 154        or can you use a workaround for now?
 155 
 156 User: I can use the web version, so it's not blocking me.
 157 
 158 Agent: Perfect. I've created Case #00284731 for this issue: "iOS app crashes
 159        during photo upload". Since you have a workaround, I've set the priority
 160        to Medium—you'll receive a response from our team within 24 hours.
 161 
 162        You'll get an email confirmation shortly. Is there anything else I can
 163        help you with?
 164 ```
 165 
 166 ### Common Pitfalls
 167 
 168 | Pitfall | Impact | Fix |
 169 |---------|--------|-----|
 170 | **Asking all questions upfront** | Feels like a form, not a conversation | Ask one question per turn, adapt based on answers |
 171 | **Repeating questions** | Frustrating user experience | Track context—check previous turns before asking |
 172 | **No validation** | Garbage data in records | Use Flow formulas for email/phone format, Apex for complex rules |
 173 | **Creating record before confirmation** | Hard to undo, no user control | Summarize collected data and ask "Should I create the case?" |
 174 | **Ignoring partial info in first message** | Inefficient, redundant | Parse first message—if user says "My email is X, phone is Y", don't re-ask |
 175 
 176 ### Context Management
 177 
 178 **Critical:** Agentforce maintains conversational context across turns. Design instructions to reference prior turns:
 179 
 180 ```
 181 When the customer provides multiple pieces of information in one message,
 182 acknowledge all of them. For example, if they say "My email is X and my
 183 phone is Y", respond "Got it, I have your email (X) and phone (Y) recorded."
 184 ```
 185 
 186 ### Topic Boundaries
 187 
 188 **In Scope:**
 189 - Collecting 3-8 fields over 3-6 turns
 190 - Linear data collection (no branching logic)
 191 - Creating a single record
 192 
 193 **Out of Scope:**
 194 - Complex branching (use Step-by-Step pattern)
 195 - More than 8 fields (break into multiple topics or use web form)
 196 - Updating existing records (different topic/pattern)
 197 
 198 ---
 199 
 200 ## Pattern 3: Handoff (Escalation to Human)
 201 
 202 ### Description
 203 
 204 Transferring the conversation to a human agent when the AI cannot resolve the issue. Includes context passing, routing, and setting user expectations.
 205 
 206 **Best for:**
 207 - Frustrated/angry customers
 208 - Complex edge cases outside AI scope
 209 - Policy exceptions requiring human judgment
 210 - Explicit requests for human agent
 211 
 212 ### Agentforce Implementation
 213 
 214 **Built-in Mechanism: Escalation Topic**
 215 
 216 Agentforce includes a pre-configured **Escalation Topic** that routes to Omni-Channel. Enable it in Setup → Agentforce Agents → [Your Agent] → Topics → Escalation Topic.
 217 
 218 **Custom Topic Configuration (for domain-specific escalation):**
 219 ```yaml
 220 Topic: Request Account Manager
 221 Classification Description: |
 222   Customer wants to speak with their dedicated account manager,
 223   sales representative, or account executive. Includes requests
 224   like "Connect me with my rep", "I want to talk to sales",
 225   "Who's my account manager?".
 226 
 227 Scope: Requests for personalized human contact in sales context
 228 ```
 229 
 230 **Actions:**
 231 - **Get Account Manager** — Flow querying Account.Owner or custom Account_Manager__c field
 232 - **Check Manager Availability** — Omni-Channel API checking online status
 233 - **Create Omni-Channel Work Item** — Flow creating AgentWork record with context
 234 - **Send Unavailable Message** — Flow triggering email/SMS if manager offline
 235 
 236 **Instructions (Topic-Level):**
 237 ```
 238 When a customer requests their account manager, look up the assigned
 239 representative. If the manager is available via Omni-Channel, route the
 240 conversation immediately with context.
 241 
 242 If the manager is unavailable, provide their contact information (email, phone)
 243 and offer to schedule a callback. Always set the expectation that a human
 244 will reach out.
 245 
 246 Context to pass to human agent: Customer name, Account ID, last purchase date,
 247 open cases count, conversation summary (what the customer needs).
 248 ```
 249 
 250 ### Conversation Example (Explicit Request)
 251 
 252 ```
 253 User: I've been trying to fix this for 20 minutes. Can I just talk to someone?
 254 
 255 Agent: Of course—let me connect you with a specialist who can help right away.
 256 
 257        I'm transferring our conversation now, and they'll have all the details
 258        we've discussed. You should see them join in just a moment.
 259 
 260        [Escalation triggered → Omni-Channel routing → Human agent receives
 261         conversation history + context summary]
 262 ```
 263 
 264 ### Conversation Example (Sentiment-Based Auto-Escalation)
 265 
 266 ```
 267 User: This is ridiculous! The app has been broken for a week and nobody cares!
 268 
 269 Agent: I understand this has been incredibly frustrating, and I'm truly sorry
 270        for the trouble. Let me connect you with a specialist who can prioritize
 271        your case and make sure this gets resolved today.
 272 
 273        Transferring you now—they'll have all the details.
 274 
 275        [Auto-escalation triggered by frustration detection]
 276 ```
 277 
 278 ### Omni-Channel Integration
 279 
 280 **Configuration Steps:**
 281 1. Create Queue (Setup → Queues → New)
 282 2. Add Agent Members to Queue
 283 3. Configure Service Channel (Setup → Service Channels)
 284 4. Create Routing Configuration (Setup → Routing Configurations)
 285 5. Link Escalation Topic to Queue
 286 
 287 **Context Passing (AgentWork Record):**
 288 ```apex
 289 // Example: Custom Apex Action for escalation with context
 290 AgentWork work = new AgentWork(
 291     WorkItemId = chatTranscript.Id,
 292     UserId = assignedAgentId,
 293     ServiceChannelId = channelId,
 294     PriorityGroup = 'High',
 295     CustomContext__c = JSON.serialize(new Map<String, Object>{
 296         'conversation_summary' => 'Customer unable to upload photos in iOS app',
 297         'case_number' => '00284731',
 298         'sentiment' => 'frustrated',
 299         'turns_count' => 8,
 300         'topics_attempted' => 'Technical Support, Troubleshooting'
 301     })
 302 );
 303 insert work;
 304 ```
 305 
 306 ### Common Pitfalls
 307 
 308 | Pitfall | Impact | Fix |
 309 |---------|--------|-----|
 310 | **No human availability check** | User waits indefinitely, no fallback | Always check Omni-Channel status, offer callback if offline |
 311 | **Apologizing excessively** | Sounds insincere, wastes time | One apology + action: "I'm sorry. Let me connect you now." |
 312 | **Not passing context** | Human agent asks same questions | Send conversation summary, key IDs, sentiment |
 313 | **Vague wait times** | Frustration increases | Give specific estimates: "2-3 minutes" not "shortly" |
 314 | **Trying to solve after user asks for human** | Ignoring user preference, bad UX | Immediate escalation when explicitly requested |
 315 
 316 ### Topic Boundaries
 317 
 318 **Trigger Escalation When:**
 319 - User explicitly requests human ("talk to a person", "speak with agent")
 320 - Sentiment analysis detects frustration/anger
 321 - Conversation exceeds 8-10 turns without resolution
 322 - Issue requires policy exception or judgment call
 323 - Technical complexity beyond AI training
 324 
 325 **Don't Escalate When:**
 326 - User is still engaged and making progress
 327 - Issue can be resolved with one more action
 328 - User hasn't indicated frustration
 329 - Human agents are offline AND issue is non-urgent (offer callback instead)
 330 
 331 ---
 332 
 333 ## Pattern 4: Step-by-Step (Guided Workflow)
 334 
 335 ### Description
 336 
 337 Multi-turn conversation guiding a user through a linear or branching process. Agent provides instructions, waits for confirmation, adapts to user's progress.
 338 
 339 **Best for:**
 340 - Troubleshooting guides
 341 - Setup/configuration assistance
 342 - Onboarding flows
 343 - How-to tutorials
 344 
 345 ### Agentforce Implementation
 346 
 347 **Topic Configuration:**
 348 ```yaml
 349 Topic: Password Reset Assistance
 350 Classification Description: |
 351   Customer is unable to log in, forgot their password, or needs help
 352   resetting credentials. Includes phrases like "can't log in",
 353   "forgot password", "reset my password", "locked out".
 354 
 355 Scope: Login/authentication issues requiring password reset guidance
 356 ```
 357 
 358 **Actions:**
 359 - **Check Account Status** — Flow checking User.IsActive, IsPasswordLocked
 360 - **Send Reset Link** — Apex triggering PasswordReset email
 361 - **Verify Identity** — Flow asking security question or MFA code
 362 - **Get Step Instructions** — Knowledge article for each step
 363 - **Confirm Step Complete** — Wait for user confirmation before next step
 364 
 365 **Instructions (Topic-Level):**
 366 ```
 367 Guide the user through password reset step-by-step. Don't provide all
 368 steps at once—give one step, wait for confirmation, then proceed.
 369 
 370 Adapt to the user's technical level. If they say "Done" quickly, they're
 371 confident—move fast. If they ask clarifying questions, slow down and
 372 provide more detail.
 373 
 374 If the user gets stuck on a step, offer to escalate to technical support
 375 rather than repeating the same instruction.
 376 ```
 377 
 378 ### Conversation Example
 379 
 380 ```
 381 User: I forgot my password and can't log in.
 382 
 383 Agent: No problem, I can help you reset it. First, I need to verify your
 384        identity—what's the email address associated with your account?
 385 
 386 User: john@example.com
 387 
 388 Agent: Thanks! I'm sending a password reset link to john@example.com right now.
 389 
 390        It should arrive within 1-2 minutes. Let me know when you see the email.
 391 
 392 User: Got it.
 393 
 394 Agent: Great! Click the "Reset Password" button in that email. It will take you
 395        to a page where you can create a new password.
 396 
 397        Your new password must be at least 8 characters and include one number
 398        and one special character.
 399 
 400        Let me know when you've created the new password.
 401 
 402 User: Done, I set a new password.
 403 
 404 Agent: Perfect! Now try logging in with your email (john@example.com) and the
 405        new password you just created.
 406 
 407        Did the login work?
 408 
 409 User: Yes, I'm in!
 410 
 411 Agent: Excellent! Your password has been successfully reset. Make sure to save
 412        it securely. Is there anything else I can help you with?
 413 ```
 414 
 415 ### Branching Logic Example
 416 
 417 ```
 418 User: The reset link isn't working.
 419 
 420 Agent: Let me check what's happening. When you click the link, what do you see?
 421 
 422        A) An error message (please tell me what it says)
 423        B) A login page (no error)
 424        C) Nothing happens / page doesn't load
 425 
 426 User: It says "This link has expired."
 427 
 428 Agent: That means the reset link was open for too long—they expire after
 429        15 minutes for security.
 430 
 431        I'll send you a fresh link right now. This time, click it as soon as
 432        you receive the email. Ready?
 433 
 434 User: Yes, send it.
 435 
 436 Agent: New link sent to john@example.com. Check your inbox and click the link
 437        within the next 15 minutes.
 438 ```
 439 
 440 ### Agentforce Flow Integration for Steps
 441 
 442 **Pattern: Use Flow Variables for State Tracking**
 443 
 444 ```yaml
 445 Flow: Password Reset Steps
 446 Variables:
 447   - CurrentStep (Text): "verify_identity", "send_link", "create_password", "test_login"
 448   - EmailVerified (Boolean)
 449   - LinkSent (Boolean)
 450   - PasswordCreated (Boolean)
 451 
 452 Decision Element: Next Step Logic
 453   - If CurrentStep = "verify_identity" AND EmailVerified = True → Set CurrentStep = "send_link"
 454   - If CurrentStep = "send_link" AND LinkSent = True → Set CurrentStep = "create_password"
 455   - If CurrentStep = "create_password" AND PasswordCreated = True → Set CurrentStep = "test_login"
 456 ```
 457 
 458 ### Common Pitfalls
 459 
 460 | Pitfall | Impact | Fix |
 461 |---------|--------|-----|
 462 | **Dumping all steps at once** | Overwhelming, user loses track | One step per turn, wait for confirmation |
 463 | **Not tracking progress** | Repeating completed steps, confusing | Use Flow variables to track current step |
 464 | **Assuming user knows what "Done" means** | Miscommunication, false progress | Be explicit: "Let me know when you've clicked the button" |
 465 | **No error branches** | Dead-end when user hits problem | For every step, anticipate 2-3 common failures |
 466 | **Technical jargon** | User doesn't understand instructions | Use simple language: "click the blue button" not "invoke the CTA element" |
 467 
 468 ### Topic Boundaries
 469 
 470 **In Scope:**
 471 - 5-10 step processes
 472 - 2-3 decision branches per step
 473 - User can complete steps independently
 474 
 475 **Out of Scope:**
 476 - Processes requiring screen sharing (escalate to human)
 477 - More than 15 total steps (break into multiple topics or provide link to docs)
 478 - Steps requiring admin/elevated permissions
 479 
 480 ---
 481 
 482 ## Pattern 5: Troubleshooting (Diagnosis & Resolution)
 483 
 484 ### Description
 485 
 486 Conversational decision tree identifying the root cause of a problem and providing resolution steps. Agent asks diagnostic questions, narrows down possibilities, and recommends fixes.
 487 
 488 **Best for:**
 489 - Technical support
 490 - Error resolution
 491 - Performance issues
 492 - Product malfunctions
 493 
 494 ### Agentforce Implementation
 495 
 496 **Topic Configuration:**
 497 ```yaml
 498 Topic: App Troubleshooting
 499 Classification Description: |
 500   Customer reports the mobile app is not working correctly—crashes,
 501   errors, slow performance, features not loading, or unexpected behavior.
 502   Includes phrases like "app won't open", "keeps crashing", "error message",
 503   "not working", "slow", "frozen".
 504 
 505 Scope: Technical issues with the mobile application requiring diagnosis
 506 ```
 507 
 508 **Actions:**
 509 - **Gather Symptoms** — Flow collecting OS version, app version, error message, reproduction steps
 510 - **Check Service Status** — API call to status.company.com checking outages
 511 - **Query Known Issues** — Knowledge search for error code or symptom pattern
 512 - **Recommend Fix** — Knowledge article for resolution steps
 513 - **Escalate to L2 Support** — Flow creating high-priority case with diagnostics
 514 
 515 **Instructions (Topic-Level):**
 516 ```
 517 Diagnose the issue through targeted questions before recommending solutions.
 518 Don't guess—ask for specific details:
 519 - What exactly happens? (symptom)
 520 - When did it start? (timeline)
 521 - Does it happen every time or intermittently? (pattern)
 522 - What were you trying to do when it happened? (context)
 523 
 524 After gathering symptoms, check for known issues and service outages before
 525 troubleshooting. If a widespread outage exists, inform the customer and
 526 provide status page link.
 527 
 528 Recommend solutions from simplest to most complex. After each solution,
 529 ask "Did that fix the issue?" before proceeding.
 530 ```
 531 
 532 ### Conversation Example
 533 
 534 ```
 535 User: The app keeps crashing on me.
 536 
 537 Agent: I'm sorry to hear that. Let me help you figure out what's causing this.
 538 
 539        When does the crash happen—right when you open the app, or while you're
 540        using a specific feature?
 541 
 542 User: When I try to upload a photo.
 543 
 544 Agent: Got it. A few questions to narrow this down:
 545 
 546        1. What type of phone are you using? (iPhone, Android, other)
 547        2. Do you see an error message, or does the app just close?
 548 
 549 User: iPhone 14, and it just closes—no error message.
 550 
 551 Agent: Thank you. When the app closes, are you able to reopen it right away,
 552        or does it keep crashing when you try to upload again?
 553 
 554 User: It reopens fine, but if I try to upload again, it crashes again.
 555 
 556 Agent: That's helpful. This sounds like a memory issue with large photos.
 557        Let me walk you through a fix:
 558 
 559        **Step 1:** Go to your iPhone Settings → [App Name] → Photos
 560        **Step 2:** Change the setting from "All Photos" to "Selected Photos"
 561        **Step 3:** Reopen the app and try uploading again
 562 
 563        This limits the app's photo library access, which often resolves crash
 564        issues. Let me know if that works.
 565 
 566 User: That fixed it! It's working now.
 567 
 568 Agent: Excellent! The crash was happening because the app was trying to load
 569        thumbnails for your entire photo library. Limiting access reduces memory
 570        usage.
 571 
 572        If you need to upload photos that aren't in your "Selected" list, just
 573        add them in Settings first. Anything else I can help with?
 574 ```
 575 
 576 ### Decision Tree Example (Pseudo-Flow Logic)
 577 
 578 ```
 579 START: App Crashing
 580   ├─ Q: When does it crash?
 581   │    ├─ On launch
 582   │    │    ├─ Q: Recently updated?
 583   │    │    │    ├─ Yes → Solution: Reinstall app
 584   │    │    │    └─ No → Solution: Clear cache
 585   │    │    └─ Next: Test solution
 586   │    ├─ During photo upload
 587   │    │    ├─ Q: Phone type?
 588   │    │    │    ├─ iPhone → Solution: Limit photo access
 589   │    │    │    └─ Android → Solution: Check storage space
 590   │    │    └─ Next: Test solution
 591   │    └─ During specific feature
 592   │         ├─ Check: Service outage for that feature?
 593   │         │    ├─ Yes → Inform: Outage, ETA to fix
 594   │         │    └─ No → Q: Reproduce steps?
 595   │         └─ Escalate: Create case with steps
 596 ```
 597 
 598 ### Common Pitfalls
 599 
 600 | Pitfall | Impact | Fix |
 601 |---------|--------|-----|
 602 | **Jumping to solutions** | Wrong fix, wasted time | Ask 3-5 diagnostic questions first |
 603 | **Yes/no questions only** | Limited information | Mix with open-ended: "What do you see when...?" |
 604 | **Not checking service status** | Troubleshooting during outage | Always check status page first |
 605 | **Giving 5 solutions at once** | Overwhelming, can't track what worked | One solution per turn, wait for result |
 606 | **No escalation path** | User stuck in loop | After 3 failed solutions, escalate to human |
 607 
 608 ### Einstein Trust Layer Considerations
 609 
 610 When troubleshooting involves sensitive data (account numbers, payment info), guide the user WITHOUT asking them to share it:
 611 
 612 ```
 613 ❌ Bad: "What's your credit card number so I can check your account?"
 614 
 615 ✅ Good: "I'll need you to verify your payment method. Can you log into
 616          your account, go to Settings → Billing, and tell me the last
 617          4 digits of the card on file?"
 618 ```
 619 
 620 The Einstein Trust Layer masks PII automatically, but design conversations to avoid soliciting sensitive data in the first place.
 621 
 622 ---
 623 
 624 ## Pattern Selection Guide
 625 
 626 Use this decision tree to choose the right pattern:
 627 
 628 ```
 629 START: What does the user want to accomplish?
 630   │
 631   ├─ Get factual information
 632   │    └─ Q&A Pattern
 633   │
 634   ├─ Create/update a record
 635   │    ├─ Single record, 3-8 fields → Information Gathering
 636   │    └─ Complex, multi-record → Step-by-Step or Handoff
 637   │
 638   ├─ Solve a problem
 639   │    ├─ Known solution (how-to) → Step-by-Step
 640   │    ├─ Unknown cause (diagnosis needed) → Troubleshooting
 641   │    └─ Requires human judgment → Handoff
 642   │
 643   └─ Talk to a human
 644        └─ Handoff Pattern
 645 ```
 646 
 647 ---
 648 
 649 ## Combining Patterns
 650 
 651 Real conversations often blend patterns. For example:
 652 
 653 **Troubleshooting → Information Gathering → Handoff**
 654 ```
 655 1. User reports issue (Troubleshooting)
 656 2. Agent diagnoses problem, but fix requires case creation (Information Gathering)
 657 3. Case created, but issue is complex → escalate to L2 (Handoff)
 658 ```
 659 
 660 **Q&A → Step-by-Step**
 661 ```
 662 1. User asks "How do I reset my password?" (Q&A)
 663 2. Agent provides link, but user says "I can't find it" (Step-by-Step)
 664 3. Agent walks through each step to guide user to reset page
 665 ```
 666 
 667 When blending patterns, use **topic transitions**:
 668 
 669 ```
 670 Agent: I found the answer to your question [Q&A Pattern]. Would you like me
 671        to walk you through the steps to set this up? [Transition to Step-by-Step]
 672 ```
 673 
 674 ---
 675 
 676 ## Summary: Pattern Comparison
 677 
 678 | Pattern | Turns | Complexity | Actions | Best For |
 679 |---------|-------|------------|---------|----------|
 680 | **Q&A** | 1-2 | Low | Knowledge retrieval, data lookup | FAQs, simple queries |
 681 | **Information Gathering** | 3-6 | Medium | Flow with inputs, record creation | Case creation, lead capture |
 682 | **Handoff** | 1-3 | Medium | Omni-Channel routing, context passing | Escalations, human requests |
 683 | **Step-by-Step** | 4-10 | High | Sequential instructions, state tracking | Tutorials, configuration |
 684 | **Troubleshooting** | 4-12 | High | Diagnostic flows, decision trees | Technical support, error resolution |
 685 
 686 Choose simplicity first—if Q&A solves the need, don't over-engineer with Step-by-Step.
