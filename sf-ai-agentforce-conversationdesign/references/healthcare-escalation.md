<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->
   1 # Escalation Matrix
   2 
   3 ## Agent Overview
   4 
   5 **Agent Name:** MediSchedule
   6 **Escalation Channel:** Omni-Channel (Salesforce Service Cloud)
   7 **Default Queue:** Patient Support Queue
   8 **Fallback Queue:** General Triage Queue
   9 
  10 ## Trigger Conditions
  11 
  12 | Trigger Type | Condition | Priority | Routing Rule | Estimated Volume |
  13 |--------------|-----------|----------|--------------|------------------|
  14 | Medical Emergency | User mentions chest pain, difficulty breathing, severe bleeding, suicidal ideation | P1 (Immediate) | Emergency Nurse Queue | 5-10/day |
  15 | Prescription Questions | Requests about medication dosage, side effects, drug interactions | P2 (Urgent) | Pharmacist Queue | 40-60/day |
  16 | Insurance Disputes | Billing errors, denied claims, coverage questions requiring review | P2 (Urgent) | Billing Specialist Queue | 80-100/day |
  17 | HIPAA-Sensitive Requests | Requests to access/modify protected health information, medical records | P2 (Urgent) | Privacy Officer Queue | 15-25/day |
  18 | Patient Complaints | Dissatisfaction with care quality, provider behavior, facility conditions | P3 (Normal) | Patient Relations Queue | 30-50/day |
  19 | Complex Scheduling | Multi-provider coordination, surgery scheduling, specialist referrals | P3 (Normal) | Scheduling Coordinator Queue | 60-80/day |
  20 | Explicit Request | User directly asks for human agent | P3 (Normal) | Patient Support Queue | 100-150/day |
  21 | Stalled Conversation | >5 turns without resolution or repeated clarification requests | P4 (Low) | Patient Support Queue | 20-30/day |
  22 
  23 ## Context Handoff Specification
  24 
  25 ### Trigger: Medical Emergency
  26 
  27 **Data to Pass:**
  28 - Patient Name (if authenticated)
  29 - Callback Phone Number (collected immediately if not in system)
  30 - Emergency Description (verbatim user input)
  31 - Location (if provided - helps dispatch EMS if needed)
  32 - Timestamp of escalation
  33 
  34 **Conversation Summary:**
  35 ```
  36 URGENT - MEDICAL EMERGENCY
  37 Patient: [Name or "Guest User"]
  38 Phone: [Number]
  39 Emergency: [User's description]
  40 Initiated at: [Timestamp]
  41 Location: [If provided]
  42 
  43 Immediate action required. Agent advised patient to call 911 if life-threatening.
  44 ```
  45 
  46 **Omni-Channel Work Item Fields:**
  47 - `Subject`: URGENT: Medical Emergency - [Emergency Type]
  48 - `Priority`: Highest
  49 - `Skill Requirements`: Emergency Triage (Required), Nursing (Required)
  50 - `Custom Field Emergency_Type__c`: [Chest Pain|Breathing|Bleeding|Mental Health|Other]
  51 
  52 ---
  53 
  54 ### Trigger: Prescription Questions
  55 
  56 **Data to Pass:**
  57 - Patient Name and MRN (Medical Record Number)
  58 - Medication Name (if mentioned)
  59 - Question Type (dosage, side effects, interaction, refill)
  60 - Current Medications (from patient record, if available)
  61 - Prescribing Provider (if known)
  62 
  63 **Conversation Summary:**
  64 ```
  65 PRESCRIPTION INQUIRY
  66 Patient: [Name] (MRN: [Number])
  67 Question: [User's question]
  68 Medication: [Name, if mentioned]
  69 Current Rx List: [Yes/No - available in chart]
  70 Agent Action: Advised patient that licensed pharmacist will respond within 2 hours.
  71 ```
  72 
  73 **Omni-Channel Work Item Fields:**
  74 - `Subject`: Rx Question: [Medication] - [Patient Name]
  75 - `Priority`: High
  76 - `Skill Requirements`: Pharmacy (Required)
  77 - `Custom Field Medication_Name__c`: [Medication]
  78 
  79 ---
  80 
  81 ### Trigger: Insurance Disputes
  82 
  83 **Data to Pass:**
  84 - Patient Name, DOB, Insurance ID
  85 - Claim Number or Date of Service
  86 - Dispute Reason (denied claim, incorrect billing, coverage question)
  87 - Amount in Question (if applicable)
  88 - Previous Correspondence (if any)
  89 
  90 **Conversation Summary:**
  91 ```
  92 INSURANCE DISPUTE
  93 Patient: [Name] (DOB: [Date], Insurance ID: [ID])
  94 Issue: [Denied claim / Incorrect charge / Coverage question]
  95 Claim: [Number] from [Date of Service]
  96 Amount: [Dollar amount]
  97 Patient States: [Verbatim user description]
  98 Agent Action: Escalated to billing specialist. Patient expects callback within 4 hours.
  99 ```
 100 
 101 **Omni-Channel Work Item Fields:**
 102 - `Subject`: Insurance Dispute - [Claim Number] - [Patient Name]
 103 - `Priority`: High
 104 - `Skill Requirements`: Billing (Expert), Insurance Verification (Required)
 105 - `Custom Field Claim_Number__c`: [Claim #]
 106 
 107 ---
 108 
 109 ### Trigger: HIPAA-Sensitive Requests
 110 
 111 **Data to Pass:**
 112 - Patient Name and DOB (for identity verification)
 113 - Request Type (access records, amend records, restrict disclosure, accounting of disclosures)
 114 - Verification Status (authenticated via portal vs. guest)
 115 - Records Requested (date range, provider, record type)
 116 
 117 **Conversation Summary:**
 118 ```
 119 HIPAA REQUEST - PRIVACY OFFICER REVIEW
 120 Patient: [Name] (DOB: [Date])
 121 Request: [Access|Amend|Restrict|Accounting] of health records
 122 Records: [Specific request details]
 123 Verification: [Authenticated via patient portal / Not authenticated - requires ID verification]
 124 Agent Action: Informed patient that Privacy Officer will contact within 24 hours per HIPAA regulations.
 125 ```
 126 
 127 **Omni-Channel Work Item Fields:**
 128 - `Subject`: HIPAA Request: [Request Type] - [Patient Name]
 129 - `Priority`: High
 130 - `Skill Requirements`: Privacy Officer (Required), HIPAA Compliance (Required)
 131 - `Custom Field HIPAA_Request_Type__c`: [Access|Amend|Restrict|Accounting]
 132 
 133 ---
 134 
 135 ### Trigger: Patient Complaints
 136 
 137 **Data to Pass:**
 138 - Patient Name and MRN
 139 - Complaint Category (provider behavior, wait times, facility, care quality)
 140 - Date/Time of Incident
 141 - Provider or Staff Involved (if mentioned)
 142 - Verbatim Complaint Description
 143 
 144 **Conversation Summary:**
 145 ```
 146 PATIENT COMPLAINT
 147 Patient: [Name] (MRN: [Number])
 148 Category: [Provider|Facility|Wait Time|Care Quality]
 149 Incident Date: [Date]
 150 Provider: [Name, if mentioned]
 151 Complaint: [User's description]
 152 Agent Action: Apologized, validated concern, escalated to Patient Relations for formal review.
 153 Patient Sentiment: [Frustrated|Angry|Disappointed|Calm]
 154 ```
 155 
 156 **Omni-Channel Work Item Fields:**
 157 - `Subject`: Patient Complaint: [Category] - [Patient Name]
 158 - `Priority`: Normal
 159 - `Skill Requirements`: Patient Relations (Required), Conflict Resolution (Preferred)
 160 - `Custom Field Complaint_Category__c`: [Provider|Facility|Wait Time|Care Quality]
 161 
 162 ---
 163 
 164 ### Trigger: Complex Scheduling
 165 
 166 **Data to Pass:**
 167 - Patient Name and MRN
 168 - Scheduling Need (surgery, multi-provider coordination, specialist referral)
 169 - Preferred Dates/Times (if mentioned)
 170 - Referring Provider (if applicable)
 171 - Insurance Pre-Authorization Status (if known)
 172 
 173 **Conversation Summary:**
 174 ```
 175 COMPLEX SCHEDULING REQUEST
 176 Patient: [Name] (MRN: [Number])
 177 Need: [Surgery|Multi-Provider|Specialist Referral]
 178 Details: [User's request]
 179 Preferred Times: [If mentioned]
 180 Referring Provider: [Name, if applicable]
 181 Agent Action: Routed to scheduling coordinator for manual coordination. Patient expects callback within 24 hours.
 182 ```
 183 
 184 **Omni-Channel Work Item Fields:**
 185 - `Subject`: Complex Scheduling: [Type] - [Patient Name]
 186 - `Priority`: Normal
 187 - `Skill Requirements`: Advanced Scheduling (Required)
 188 - `Custom Field Scheduling_Type__c`: [Surgery|Multi-Provider|Specialist]
 189 
 190 ---
 191 
 192 ## Omni-Channel Configuration
 193 
 194 ### Queue: Emergency Nurse Queue
 195 
 196 **Purpose:** Handle medical emergencies requiring immediate clinical triage
 197 
 198 **Routing Model:** Most Available (fastest response)
 199 
 200 **Skills Required:**
 201 - Emergency Triage: Expert
 202 - Nursing: Required
 203 
 204 **Service Level Agreement:**
 205 - Target Response Time: <1 minute
 206 - Escalation Path: If no nurse available in 1 min → Page on-call physician
 207 
 208 **Agent Capacity:**
 209 - Max Concurrent Chats: 2 (emergencies require focus)
 210 - Overflow Queue: On-Call Physician Queue
 211 
 212 ---
 213 
 214 ### Queue: Pharmacist Queue
 215 
 216 **Purpose:** Answer medication-related questions requiring licensed pharmacist
 217 
 218 **Routing Model:** Least Active (balance workload among pharmacists)
 219 
 220 **Skills Required:**
 221 - Pharmacy: Required
 222 
 223 **Service Level Agreement:**
 224 - Target Response Time: <2 hours
 225 - Escalation Path: If no response in 2 hours → Email pharmacist supervisor
 226 
 227 **Agent Capacity:**
 228 - Max Concurrent Chats: 5
 229 - Overflow Queue: Pharmacy Supervisor Queue
 230 
 231 ---
 232 
 233 ### Queue: Billing Specialist Queue
 234 
 235 **Purpose:** Resolve insurance disputes, billing errors, and coverage questions
 236 
 237 **Routing Model:** External Routing (uses round-robin among billing team)
 238 
 239 **Skills Required:**
 240 - Billing: Expert
 241 - Insurance Verification: Required
 242 
 243 **Service Level Agreement:**
 244 - Target Response Time: <4 hours during business hours
 245 - Escalation Path: If >1 business day unresolved → Escalate to Billing Manager
 246 
 247 **Agent Capacity:**
 248 - Max Concurrent Chats: 8
 249 - Overflow Queue: Billing Manager Queue
 250 
 251 ---
 252 
 253 ### Queue: Privacy Officer Queue
 254 
 255 **Purpose:** Handle HIPAA-sensitive requests for medical record access/amendment
 256 
 257 **Routing Model:** Most Available (limited staff, urgent compliance timelines)
 258 
 259 **Skills Required:**
 260 - Privacy Officer: Required
 261 - HIPAA Compliance: Required
 262 
 263 **Service Level Agreement:**
 264 - Target Response Time: <24 hours (HIPAA requirement: 30 days for access, but we target faster)
 265 - Escalation Path: If complex legal issue → Consult with Legal Counsel
 266 
 267 **Agent Capacity:**
 268 - Max Concurrent Chats: 3
 269 - Overflow Queue: Chief Privacy Officer
 270 
 271 ---
 272 
 273 ### Queue: Patient Relations Queue
 274 
 275 **Purpose:** Address patient complaints and care quality concerns
 276 
 277 **Routing Model:** Least Active
 278 
 279 **Skills Required:**
 280 - Patient Relations: Required
 281 - Conflict Resolution: Preferred
 282 
 283 **Service Level Agreement:**
 284 - Target Response Time: <4 business hours
 285 - Escalation Path: If formal grievance → Route to Grievance Committee per policy
 286 
 287 **Agent Capacity:**
 288 - Max Concurrent Chats: 6
 289 - Overflow Queue: Patient Experience Manager
 290 
 291 ---
 292 
 293 ### Queue: Scheduling Coordinator Queue
 294 
 295 **Purpose:** Coordinate complex, multi-step scheduling requiring human judgment
 296 
 297 **Routing Model:** External Routing
 298 
 299 **Skills Required:**
 300 - Advanced Scheduling: Required
 301 
 302 **Service Level Agreement:**
 303 - Target Response Time: <24 hours
 304 - Escalation Path: If surgery scheduling → Coordinate with Surgery Scheduler
 305 
 306 **Agent Capacity:**
 307 - Max Concurrent Chats: 10
 308 - Overflow Queue: Scheduling Supervisor Queue
 309 
 310 ---
 311 
 312 ## Escalation Messages
 313 
 314 ### Pre-Escalation (Before Handoff)
 315 
 316 **Default Message:**
 317 ```
 318 I'm going to connect you with a specialist who can help with this right away. You should see them join in just a moment. They'll have all the information from our conversation so you won't need to repeat yourself.
 319 ```
 320 
 321 **Frustrated User Variant:**
 322 ```
 323 I completely understand your frustration, and I'm sorry for the inconvenience. I'm connecting you with a specialist right now who has the tools to resolve this. They'll be with you shortly and will have full context of your situation.
 324 ```
 325 
 326 **High-Priority Variant (Emergency):**
 327 ```
 328 I'm immediately connecting you with our emergency nurse. They'll be with you in less than 60 seconds.
 329 
 330 IMPORTANT: If you're experiencing a life-threatening emergency, please hang up and call 911 or go to your nearest emergency room right away.
 331 ```
 332 
 333 ### During Handoff (Wait State)
 334 
 335 **Initial Wait Message:**
 336 ```
 337 Your specialist is being notified now. Typical wait time is [X minutes]. I'll stay here with you until they arrive.
 338 ```
 339 
 340 **Extended Wait Message (if >2 minutes for urgent, >5 minutes for normal):**
 341 ```
 342 I'm sorry for the wait. I'm actively monitoring for your specialist to join. If you'd prefer, I can have them call you at [phone number] instead, or you can continue waiting here. What works better for you?
 343 ```
 344 
 345 ### Post-Escalation (Human Takes Over)
 346 
 347 **Human Agent Greeting Template:**
 348 ```
 349 Hi [Patient Name], this is [Agent Name], [Title]. I've reviewed your conversation with our virtual assistant and I'm here to help with [specific issue]. [Personalized response based on context summary]
 350 ```
 351 
 352 **Context Summary for Human:**
 353 ```
 354 Agent attempted: [List of actions taken - e.g., "Searched for appointments on 3/15, no availability found"]
 355 User's goal: [e.g., "Schedule annual physical with Dr. Smith in next 2 weeks"]
 356 Escalation reason: [e.g., "Complex scheduling - requires coordination between 3 providers"]
 357 Relevant data:
 358   - Patient: [Name], MRN [Number], DOB [Date]
 359   - Insurance: [Plan name], ID [Number]
 360   - Last Visit: [Date] with [Provider]
 361   - Preferred Times: [If mentioned]
 362 Patient Sentiment: [Calm|Frustrated|Angry|Anxious]
 363 ```
 364 
 365 ## Post-Escalation Workflow
 366 
 367 ### Agent Behavior After Handoff
 368 
 369 - [✓] Agent remains in conversation: Yes (stays silent unless human agent requests assistance)
 370 - [✓] Agent monitors for human agent join: Yes (auto-notifies user when human joins)
 371 - [✓] Agent logs escalation reason: Yes (creates Case record with escalation category)
 372 - [✓] Agent creates follow-up task: Yes (if human agent doesn't join within SLA)
 373 
 374 **If Human Agent Unavailable:**
 375 Attempt 1: Wait 30 seconds, retry queue assignment
 376 Attempt 2: Route to overflow queue
 377 Attempt 3: Create high-priority Case, offer callback scheduling
 378 Message: "I apologize—our specialists are all assisting other patients right now. I've created a priority case (#[CASE_NUMBER]) and [Specialist Type] will call you at [PHONE] within [SLA]. You'll also receive an email confirmation. Is there anything else I can help with while you wait?"
 379 
 380 ### Escalation Metrics
 381 
 382 **Success Criteria:**
 383 - First Contact Resolution (FCR) after escalation: >75%
 384 - Human agent accepts transfer within: SLA time (varies by priority - see queue configs)
 385 - User satisfaction (CSAT) for escalated conversations: >4.0/5.0
 386 
 387 **Monitoring:**
 388 - Daily escalation rate: Target <20% of total conversations
 389 - Top escalation reasons (weekly review): Insurance (28%), Complex Scheduling (22%), Prescription Qs (18%), Complaints (12%), HIPAA (10%), Emergency (8%), Other (2%)
 390 - Escalation trend threshold: Alert if rate exceeds 25% for 3 consecutive days
 391 
 392 ## De-Escalation Strategies
 393 
 394 ### Before Triggering Escalation
 395 
 396 **Attempt:**
 397 1. **Rephrase and clarify intent**: If user request is ambiguous, ask specific questions to understand the need before assuming escalation is required.
 398 2. **Offer self-service alternative**: "I can send you a link to view your test results in the patient portal—would that work, or do you need to speak with someone?"
 399 3. **Break complex requests into simple steps**: For multi-part requests, handle what's possible via automation first (e.g., schedule simple appointment, then escalate for complex referral).
 400 
 401 **If De-Escalation Succeeds:**
 402 Continue conversation flow, mark in logs as "Near-Escalation Avoided" for analysis to improve agent capabilities.
 403 
 404 **If De-Escalation Fails:**
 405 Proceed with escalation, but log the attempted de-escalation strategies for training purposes.
 406 
 407 ## Edge Cases
 408 
 409 ### Edge Case 1: User Refuses to Call 911 for Medical Emergency
 410 
 411 **Scenario:** User describes chest pain or severe symptoms but insists on handling via chat instead of calling emergency services.
 412 
 413 **Escalation Decision:** Escalate to Emergency Nurse Queue AND provide strong 911 recommendation.
 414 
 415 **Rationale:** Agent cannot force user to call 911, but can escalate to clinical staff who may have more influence. Document in case notes that patient was advised to call 911 but declined.
 416 
 417 ---
 418 
 419 ### Edge Case 2: Minor Requests Escalation to Avoid Agent
 420 
 421 **Scenario:** User requests human agent for simple tasks like "what time are you open?" to avoid interacting with bot.
 422 
 423 **Escalation Decision:** De-escalate by providing the information directly, then asking "Is there anything else I can help with, or would you still prefer to speak with someone?"
 424 
 425 **Rationale:** Reduces unnecessary escalation volume. Most users accept answer once provided. If user insists on human after receiving answer, honor request but route to low-priority queue.
 426 
 427 ---
 428 
 429 ### Edge Case 3: User Becomes Abusive or Threatens Staff
 430 
 431 **Scenario:** User uses profanity, makes threats, or harasses agent.
 432 
 433 **Escalation Decision:** Provide one warning: "I'm here to help, but I need to ask that we keep our conversation respectful. Continued abusive language may result in ending this chat." If continues, escalate to Security Queue with full transcript.
 434 
 435 **Rationale:** Patient safety and staff protection. Security team can assess threat level and flag patient record if needed.
 436 
 437 ---
 438 
 439 ### Edge Case 4: User Requests Controlled Substance Prescription Refill
 440 
 441 **Scenario:** User asks to refill opioid or other controlled medication.
 442 
 443 **Escalation Decision:** Escalate to Pharmacist Queue with note: "Controlled substance refill request - requires provider authorization per DEA regulations."
 444 
 445 **Rationale:** Legal requirement that controlled substances require provider verification. Pharmacist will coordinate with prescriber.
 446 
 447 ---
 448 
 449 ### Edge Case 5: After-Hours Emergency (No Clinical Staff Available)
 450 
 451 **Scenario:** Medical emergency escalation triggered at 2am when Emergency Nurse Queue has no available agents.
 452 
 453 **Escalation Decision:** Display message: "URGENT: Please call 911 immediately or go to your nearest emergency room. This is a potential medical emergency that requires immediate in-person evaluation. Our clinical staff will follow up within 24 hours." Create high-priority Case for morning triage.
 454 
 455 **Rationale:** Cannot leave patient without guidance during true emergency. Direct to appropriate emergency care, document for follow-up.
 456 
 457 ---
 458 
 459 ## Version Control
 460 
 461 **Version:** 1.2.0
 462 **Last Updated:** 2026-02-07
 463 **Author:** Clinical Operations Team & IT
 464 **Approved By:** Dr. Sarah Mitchell (CMO), David Park (VP Patient Experience)
 465 **Next Review:** 2026-03-07 (30-day review post-implementation)
 466 
 467 ## Notes and Assumptions
 468 
 469 **Dependencies:**
 470 - Omni-Channel setup complete with all queues configured
 471 - Skills (Emergency Triage, Pharmacy, Billing, etc.) assigned to appropriate staff in Salesforce
 472 - Case Management workflow triggers set up for escalation logging
 473 - After-hours coverage plan confirmed with clinical leadership
 474 
 475 **Compliance Considerations:**
 476 - All escalations involving PHI must be logged per HIPAA audit requirements
 477 - 30-day SLA for HIPAA access requests per 45 CFR § 164.524
 478 - Controlled substance prescriptions subject to DEA regulations
 479 
 480 **Capacity Planning:**
 481 - Emergency Nurse Queue: 2 RNs on duty 24/7 (covers 10-15 emergencies/day)
 482 - Pharmacist Queue: 3 pharmacists 8am-8pm, 1 on-call 8pm-8am
 483 - Billing Queue: 6 specialists 8am-6pm weekdays
 484 - Patient Relations: 4 staff 8am-5pm weekdays
