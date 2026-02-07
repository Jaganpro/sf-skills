# Escalation Matrix

## Agent Overview

**Agent Name:** MediSchedule
**Escalation Channel:** Omni-Channel (Salesforce Service Cloud)
**Default Queue:** Patient Support Queue
**Fallback Queue:** General Triage Queue

## Trigger Conditions

| Trigger Type | Condition | Priority | Routing Rule | Estimated Volume |
|--------------|-----------|----------|--------------|------------------|
| Medical Emergency | User mentions chest pain, difficulty breathing, severe bleeding, suicidal ideation | P1 (Immediate) | Emergency Nurse Queue | 5-10/day |
| Prescription Questions | Requests about medication dosage, side effects, drug interactions | P2 (Urgent) | Pharmacist Queue | 40-60/day |
| Insurance Disputes | Billing errors, denied claims, coverage questions requiring review | P2 (Urgent) | Billing Specialist Queue | 80-100/day |
| HIPAA-Sensitive Requests | Requests to access/modify protected health information, medical records | P2 (Urgent) | Privacy Officer Queue | 15-25/day |
| Patient Complaints | Dissatisfaction with care quality, provider behavior, facility conditions | P3 (Normal) | Patient Relations Queue | 30-50/day |
| Complex Scheduling | Multi-provider coordination, surgery scheduling, specialist referrals | P3 (Normal) | Scheduling Coordinator Queue | 60-80/day |
| Explicit Request | User directly asks for human agent | P3 (Normal) | Patient Support Queue | 100-150/day |
| Stalled Conversation | >5 turns without resolution or repeated clarification requests | P4 (Low) | Patient Support Queue | 20-30/day |

## Context Handoff Specification

### Trigger: Medical Emergency

**Data to Pass:**
- Patient Name (if authenticated)
- Callback Phone Number (collected immediately if not in system)
- Emergency Description (verbatim user input)
- Location (if provided - helps dispatch EMS if needed)
- Timestamp of escalation

**Conversation Summary:**
```
URGENT - MEDICAL EMERGENCY
Patient: [Name or "Guest User"]
Phone: [Number]
Emergency: [User's description]
Initiated at: [Timestamp]
Location: [If provided]

Immediate action required. Agent advised patient to call 911 if life-threatening.
```

**Omni-Channel Work Item Fields:**
- `Subject`: URGENT: Medical Emergency - [Emergency Type]
- `Priority`: Highest
- `Skill Requirements`: Emergency Triage (Required), Nursing (Required)
- `Custom Field Emergency_Type__c`: [Chest Pain|Breathing|Bleeding|Mental Health|Other]

---

### Trigger: Prescription Questions

**Data to Pass:**
- Patient Name and MRN (Medical Record Number)
- Medication Name (if mentioned)
- Question Type (dosage, side effects, interaction, refill)
- Current Medications (from patient record, if available)
- Prescribing Provider (if known)

**Conversation Summary:**
```
PRESCRIPTION INQUIRY
Patient: [Name] (MRN: [Number])
Question: [User's question]
Medication: [Name, if mentioned]
Current Rx List: [Yes/No - available in chart]
Agent Action: Advised patient that licensed pharmacist will respond within 2 hours.
```

**Omni-Channel Work Item Fields:**
- `Subject`: Rx Question: [Medication] - [Patient Name]
- `Priority`: High
- `Skill Requirements`: Pharmacy (Required)
- `Custom Field Medication_Name__c`: [Medication]

---

### Trigger: Insurance Disputes

**Data to Pass:**
- Patient Name, DOB, Insurance ID
- Claim Number or Date of Service
- Dispute Reason (denied claim, incorrect billing, coverage question)
- Amount in Question (if applicable)
- Previous Correspondence (if any)

**Conversation Summary:**
```
INSURANCE DISPUTE
Patient: [Name] (DOB: [Date], Insurance ID: [ID])
Issue: [Denied claim / Incorrect charge / Coverage question]
Claim: [Number] from [Date of Service]
Amount: [Dollar amount]
Patient States: [Verbatim user description]
Agent Action: Escalated to billing specialist. Patient expects callback within 4 hours.
```

**Omni-Channel Work Item Fields:**
- `Subject`: Insurance Dispute - [Claim Number] - [Patient Name]
- `Priority`: High
- `Skill Requirements`: Billing (Expert), Insurance Verification (Required)
- `Custom Field Claim_Number__c`: [Claim #]

---

### Trigger: HIPAA-Sensitive Requests

**Data to Pass:**
- Patient Name and DOB (for identity verification)
- Request Type (access records, amend records, restrict disclosure, accounting of disclosures)
- Verification Status (authenticated via portal vs. guest)
- Records Requested (date range, provider, record type)

**Conversation Summary:**
```
HIPAA REQUEST - PRIVACY OFFICER REVIEW
Patient: [Name] (DOB: [Date])
Request: [Access|Amend|Restrict|Accounting] of health records
Records: [Specific request details]
Verification: [Authenticated via patient portal / Not authenticated - requires ID verification]
Agent Action: Informed patient that Privacy Officer will contact within 24 hours per HIPAA regulations.
```

**Omni-Channel Work Item Fields:**
- `Subject`: HIPAA Request: [Request Type] - [Patient Name]
- `Priority`: High
- `Skill Requirements`: Privacy Officer (Required), HIPAA Compliance (Required)
- `Custom Field HIPAA_Request_Type__c`: [Access|Amend|Restrict|Accounting]

---

### Trigger: Patient Complaints

**Data to Pass:**
- Patient Name and MRN
- Complaint Category (provider behavior, wait times, facility, care quality)
- Date/Time of Incident
- Provider or Staff Involved (if mentioned)
- Verbatim Complaint Description

**Conversation Summary:**
```
PATIENT COMPLAINT
Patient: [Name] (MRN: [Number])
Category: [Provider|Facility|Wait Time|Care Quality]
Incident Date: [Date]
Provider: [Name, if mentioned]
Complaint: [User's description]
Agent Action: Apologized, validated concern, escalated to Patient Relations for formal review.
Patient Sentiment: [Frustrated|Angry|Disappointed|Calm]
```

**Omni-Channel Work Item Fields:**
- `Subject`: Patient Complaint: [Category] - [Patient Name]
- `Priority`: Normal
- `Skill Requirements`: Patient Relations (Required), Conflict Resolution (Preferred)
- `Custom Field Complaint_Category__c`: [Provider|Facility|Wait Time|Care Quality]

---

### Trigger: Complex Scheduling

**Data to Pass:**
- Patient Name and MRN
- Scheduling Need (surgery, multi-provider coordination, specialist referral)
- Preferred Dates/Times (if mentioned)
- Referring Provider (if applicable)
- Insurance Pre-Authorization Status (if known)

**Conversation Summary:**
```
COMPLEX SCHEDULING REQUEST
Patient: [Name] (MRN: [Number])
Need: [Surgery|Multi-Provider|Specialist Referral]
Details: [User's request]
Preferred Times: [If mentioned]
Referring Provider: [Name, if applicable]
Agent Action: Routed to scheduling coordinator for manual coordination. Patient expects callback within 24 hours.
```

**Omni-Channel Work Item Fields:**
- `Subject`: Complex Scheduling: [Type] - [Patient Name]
- `Priority`: Normal
- `Skill Requirements`: Advanced Scheduling (Required)
- `Custom Field Scheduling_Type__c`: [Surgery|Multi-Provider|Specialist]

---

## Omni-Channel Configuration

### Queue: Emergency Nurse Queue

**Purpose:** Handle medical emergencies requiring immediate clinical triage

**Routing Model:** Most Available (fastest response)

**Skills Required:**
- Emergency Triage: Expert
- Nursing: Required

**Service Level Agreement:**
- Target Response Time: <1 minute
- Escalation Path: If no nurse available in 1 min → Page on-call physician

**Agent Capacity:**
- Max Concurrent Chats: 2 (emergencies require focus)
- Overflow Queue: On-Call Physician Queue

---

### Queue: Pharmacist Queue

**Purpose:** Answer medication-related questions requiring licensed pharmacist

**Routing Model:** Least Active (balance workload among pharmacists)

**Skills Required:**
- Pharmacy: Required

**Service Level Agreement:**
- Target Response Time: <2 hours
- Escalation Path: If no response in 2 hours → Email pharmacist supervisor

**Agent Capacity:**
- Max Concurrent Chats: 5
- Overflow Queue: Pharmacy Supervisor Queue

---

### Queue: Billing Specialist Queue

**Purpose:** Resolve insurance disputes, billing errors, and coverage questions

**Routing Model:** External Routing (uses round-robin among billing team)

**Skills Required:**
- Billing: Expert
- Insurance Verification: Required

**Service Level Agreement:**
- Target Response Time: <4 hours during business hours
- Escalation Path: If >1 business day unresolved → Escalate to Billing Manager

**Agent Capacity:**
- Max Concurrent Chats: 8
- Overflow Queue: Billing Manager Queue

---

### Queue: Privacy Officer Queue

**Purpose:** Handle HIPAA-sensitive requests for medical record access/amendment

**Routing Model:** Most Available (limited staff, urgent compliance timelines)

**Skills Required:**
- Privacy Officer: Required
- HIPAA Compliance: Required

**Service Level Agreement:**
- Target Response Time: <24 hours (HIPAA requirement: 30 days for access, but we target faster)
- Escalation Path: If complex legal issue → Consult with Legal Counsel

**Agent Capacity:**
- Max Concurrent Chats: 3
- Overflow Queue: Chief Privacy Officer

---

### Queue: Patient Relations Queue

**Purpose:** Address patient complaints and care quality concerns

**Routing Model:** Least Active

**Skills Required:**
- Patient Relations: Required
- Conflict Resolution: Preferred

**Service Level Agreement:**
- Target Response Time: <4 business hours
- Escalation Path: If formal grievance → Route to Grievance Committee per policy

**Agent Capacity:**
- Max Concurrent Chats: 6
- Overflow Queue: Patient Experience Manager

---

### Queue: Scheduling Coordinator Queue

**Purpose:** Coordinate complex, multi-step scheduling requiring human judgment

**Routing Model:** External Routing

**Skills Required:**
- Advanced Scheduling: Required

**Service Level Agreement:**
- Target Response Time: <24 hours
- Escalation Path: If surgery scheduling → Coordinate with Surgery Scheduler

**Agent Capacity:**
- Max Concurrent Chats: 10
- Overflow Queue: Scheduling Supervisor Queue

---

## Escalation Messages

### Pre-Escalation (Before Handoff)

**Default Message:**
```
I'm going to connect you with a specialist who can help with this right away. You should see them join in just a moment. They'll have all the information from our conversation so you won't need to repeat yourself.
```

**Frustrated User Variant:**
```
I completely understand your frustration, and I'm sorry for the inconvenience. I'm connecting you with a specialist right now who has the tools to resolve this. They'll be with you shortly and will have full context of your situation.
```

**High-Priority Variant (Emergency):**
```
I'm immediately connecting you with our emergency nurse. They'll be with you in less than 60 seconds.

IMPORTANT: If you're experiencing a life-threatening emergency, please hang up and call 911 or go to your nearest emergency room right away.
```

### During Handoff (Wait State)

**Initial Wait Message:**
```
Your specialist is being notified now. Typical wait time is [X minutes]. I'll stay here with you until they arrive.
```

**Extended Wait Message (if >2 minutes for urgent, >5 minutes for normal):**
```
I'm sorry for the wait. I'm actively monitoring for your specialist to join. If you'd prefer, I can have them call you at [phone number] instead, or you can continue waiting here. What works better for you?
```

### Post-Escalation (Human Takes Over)

**Human Agent Greeting Template:**
```
Hi [Patient Name], this is [Agent Name], [Title]. I've reviewed your conversation with our virtual assistant and I'm here to help with [specific issue]. [Personalized response based on context summary]
```

**Context Summary for Human:**
```
Agent attempted: [List of actions taken - e.g., "Searched for appointments on 3/15, no availability found"]
User's goal: [e.g., "Schedule annual physical with Dr. Smith in next 2 weeks"]
Escalation reason: [e.g., "Complex scheduling - requires coordination between 3 providers"]
Relevant data:
  - Patient: [Name], MRN [Number], DOB [Date]
  - Insurance: [Plan name], ID [Number]
  - Last Visit: [Date] with [Provider]
  - Preferred Times: [If mentioned]
Patient Sentiment: [Calm|Frustrated|Angry|Anxious]
```

## Post-Escalation Workflow

### Agent Behavior After Handoff

- [✓] Agent remains in conversation: Yes (stays silent unless human agent requests assistance)
- [✓] Agent monitors for human agent join: Yes (auto-notifies user when human joins)
- [✓] Agent logs escalation reason: Yes (creates Case record with escalation category)
- [✓] Agent creates follow-up task: Yes (if human agent doesn't join within SLA)

**If Human Agent Unavailable:**
Attempt 1: Wait 30 seconds, retry queue assignment
Attempt 2: Route to overflow queue
Attempt 3: Create high-priority Case, offer callback scheduling
Message: "I apologize—our specialists are all assisting other patients right now. I've created a priority case (#[CASE_NUMBER]) and [Specialist Type] will call you at [PHONE] within [SLA]. You'll also receive an email confirmation. Is there anything else I can help with while you wait?"

### Escalation Metrics

**Success Criteria:**
- First Contact Resolution (FCR) after escalation: >75%
- Human agent accepts transfer within: SLA time (varies by priority - see queue configs)
- User satisfaction (CSAT) for escalated conversations: >4.0/5.0

**Monitoring:**
- Daily escalation rate: Target <20% of total conversations
- Top escalation reasons (weekly review): Insurance (28%), Complex Scheduling (22%), Prescription Qs (18%), Complaints (12%), HIPAA (10%), Emergency (8%), Other (2%)
- Escalation trend threshold: Alert if rate exceeds 25% for 3 consecutive days

## De-Escalation Strategies

### Before Triggering Escalation

**Attempt:**
1. **Rephrase and clarify intent**: If user request is ambiguous, ask specific questions to understand the need before assuming escalation is required.
2. **Offer self-service alternative**: "I can send you a link to view your test results in the patient portal—would that work, or do you need to speak with someone?"
3. **Break complex requests into simple steps**: For multi-part requests, handle what's possible via automation first (e.g., schedule simple appointment, then escalate for complex referral).

**If De-Escalation Succeeds:**
Continue conversation flow, mark in logs as "Near-Escalation Avoided" for analysis to improve agent capabilities.

**If De-Escalation Fails:**
Proceed with escalation, but log the attempted de-escalation strategies for training purposes.

## Edge Cases

### Edge Case 1: User Refuses to Call 911 for Medical Emergency

**Scenario:** User describes chest pain or severe symptoms but insists on handling via chat instead of calling emergency services.

**Escalation Decision:** Escalate to Emergency Nurse Queue AND provide strong 911 recommendation.

**Rationale:** Agent cannot force user to call 911, but can escalate to clinical staff who may have more influence. Document in case notes that patient was advised to call 911 but declined.

---

### Edge Case 2: Minor Requests Escalation to Avoid Agent

**Scenario:** User requests human agent for simple tasks like "what time are you open?" to avoid interacting with bot.

**Escalation Decision:** De-escalate by providing the information directly, then asking "Is there anything else I can help with, or would you still prefer to speak with someone?"

**Rationale:** Reduces unnecessary escalation volume. Most users accept answer once provided. If user insists on human after receiving answer, honor request but route to low-priority queue.

---

### Edge Case 3: User Becomes Abusive or Threatens Staff

**Scenario:** User uses profanity, makes threats, or harasses agent.

**Escalation Decision:** Provide one warning: "I'm here to help, but I need to ask that we keep our conversation respectful. Continued abusive language may result in ending this chat." If continues, escalate to Security Queue with full transcript.

**Rationale:** Patient safety and staff protection. Security team can assess threat level and flag patient record if needed.

---

### Edge Case 4: User Requests Controlled Substance Prescription Refill

**Scenario:** User asks to refill opioid or other controlled medication.

**Escalation Decision:** Escalate to Pharmacist Queue with note: "Controlled substance refill request - requires provider authorization per DEA regulations."

**Rationale:** Legal requirement that controlled substances require provider verification. Pharmacist will coordinate with prescriber.

---

### Edge Case 5: After-Hours Emergency (No Clinical Staff Available)

**Scenario:** Medical emergency escalation triggered at 2am when Emergency Nurse Queue has no available agents.

**Escalation Decision:** Display message: "URGENT: Please call 911 immediately or go to your nearest emergency room. This is a potential medical emergency that requires immediate in-person evaluation. Our clinical staff will follow up within 24 hours." Create high-priority Case for morning triage.

**Rationale:** Cannot leave patient without guidance during true emergency. Direct to appropriate emergency care, document for follow-up.

---

## Version Control

**Version:** 1.2.0
**Last Updated:** 2026-02-07
**Author:** Clinical Operations Team & IT
**Approved By:** Dr. Sarah Mitchell (CMO), David Park (VP Patient Experience)
**Next Review:** 2026-03-07 (30-day review post-implementation)

## Notes and Assumptions

**Dependencies:**
- Omni-Channel setup complete with all queues configured
- Skills (Emergency Triage, Pharmacy, Billing, etc.) assigned to appropriate staff in Salesforce
- Case Management workflow triggers set up for escalation logging
- After-hours coverage plan confirmed with clinical leadership

**Compliance Considerations:**
- All escalations involving PHI must be logged per HIPAA audit requirements
- 30-day SLA for HIPAA access requests per 45 CFR § 164.524
- Controlled substance prescriptions subject to DEA regulations

**Capacity Planning:**
- Emergency Nurse Queue: 2 RNs on duty 24/7 (covers 10-15 emergencies/day)
- Pharmacist Queue: 3 pharmacists 8am-8pm, 1 on-call 8pm-8am
- Billing Queue: 6 specialists 8am-6pm weekdays
- Patient Relations: 4 staff 8am-5pm weekdays
