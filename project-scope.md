# Aurion Hackathon — Project Scope

## The Problem

Aurion receives a high volume of customer emails with attached documents (PDFs, scanned forms, invoices, medical reports, etc.). Today, a human agent must:

1. Open the email
2. Read the email body to understand the intent
3. Open and read the PDF attachment
4. Manually classify what type of request it is
5. Extract relevant data (policy number, claim details, amounts, dates)
6. Decide what to do next (process, escalate, request more info)
7. Draft a response to the customer

This is time-consuming, repetitive, and error-prone — especially under volume.

## The Solution

An agentic workflow powered by the Microsoft Agent Framework that automates this end-to-end process. When an email arrives, the system takes over.

## The Flow

```
  Customer sends email
  (with PDF attachment)
         │
         ▼
┌──────────────────────┐
│  1. EMAIL INTAKE     │
│                      │
│  • Retrieve email    │
│    body + metadata   │
│  • Detect & extract  │
│    PDF attachment    │
│  • Pass both to the  │
│    next step         │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  2. DOCUMENT         │
│     UNDERSTANDING    │
│                      │
│  • Azure Document    │
│    Intelligence      │
│    extracts text,    │
│    tables, structure │
│    from the PDF      │
│  • Combines email    │
│    body + extracted  │
│    PDF content into  │
│    a unified context │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  3. CLASSIFICATION   │
│                      │
│  • What type of      │
│    request is this?  │
│    - New claim       │
│    - Claim status    │
│    - Policy inquiry  │
│    - Invoice/billing │
│    - Complaint       │
│    - General question│
│  • How urgent is it? │
│  • Confidence score  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  4. DATA EXTRACTION  │
│                      │
│  • Extract structured│
│    fields depending  │
│    on the category:  │
│    - Policy number   │
│    - Customer name   │
│    - Date of incident│
│    - Claim amount    │
│    - Damage type     │
│    - Supporting docs │
│  • Validate: are all │
│    required fields   │
│    present?          │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  5. DECISION &       │
│     ROUTING          │
│                      │
│  Based on category,  │
│  urgency, and data   │
│  completeness:       │
│                      │
│  → Auto-process      │
│    (small/simple     │
│     claims)          │
│                      │
│  → Escalate to human │
│    (high value,      │
│     complex, or low  │
│     confidence)      │
│                      │
│  → Request more info │
│    (missing docs or  │
│     unclear details) │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  6. RESPONSE         │
│     GENERATION       │
│                      │
│  • Draft a reply     │
│    email in German   │
│  • Tone: professional│
│    and empathetic    │
│  • Content depends   │
│    on the decision:  │
│    - Confirmation    │
│    - Status update   │
│    - Request for     │
│      missing docs    │
│    - Escalation      │
│      acknowledgment  │
└──────────────────────┘
```

## Example Scenario

> **Email from:** maria.huber@gmail.com
> **Subject:** Wasserschaden in meiner Wohnung
> **Body:** "Sehr geehrte Damen und Herren, am 15. März ist in meiner Wohnung ein Wasserschaden entstanden. Anbei finden Sie die Fotos und den Kostenvoranschlag. Meine Polizzennummer ist HV-2024-38291. Bitte um rasche Bearbeitung. Mit freundlichen Grüßen, Maria Huber"
> **Attachment:** kostenvoranschlag_wasserschaden.pdf

**What the workflow does:**

1. **Email Intake** — Extracts the email body, detects the PDF attachment, pulls metadata (sender, subject, date)
2. **Document Understanding** — Azure Document Intelligence processes the PDF (cost estimate), extracts line items, amounts, contractor details
3. **Classification** — Identifies this as a **new property damage claim**, urgency: **normal**
4. **Data Extraction** — Pulls: policy number (HV-2024-38291), customer (Maria Huber), incident date (March 15), damage type (water damage), estimated cost (from PDF)
5. **Decision** — Estimated cost is under threshold → **auto-process** path. All required fields present. Route to claims processing.
6. **Response** — Drafts a German reply confirming receipt, citing her policy number, stating the claim is being processed, and providing a reference number + expected timeline.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | Microsoft Agent Framework (Python SDK) |
| LLM | Azure OpenAI (GPT-4o) |
| Document extraction | Azure Document Intelligence |
| Email access | Simulated for hackathon (real: Microsoft Graph API) |
| Language | Python |

## What We Build vs. What We Simulate

| Built for real | Simulated |
|---------------|-----------|
| Full agent workflow (all 6 steps) | Email trigger (we provide sample emails + PDFs as input) |
| Document Intelligence integration | Backend systems (policy lookup, claim submission) |
| LLM-powered classification, extraction, response drafting | — |
| Conditional routing logic | — |
| Human-in-the-loop for escalation | — |
| German language responses | — |

## Success Criteria

- End-to-end demo: feed in a sample email + PDF, get a drafted response out
- Correct classification of at least 3 different document types
- Structured data extraction with validation
- Conditional routing (auto-process vs. escalate vs. request info)
- Professional German-language response generation
- Clean, extensible code that Aurion can build on after the hackathon
