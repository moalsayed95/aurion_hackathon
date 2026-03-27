# Aurion Claim Intake — Hackathon

An AI-powered insurance claim intake workflow. A customer email arrives with a PDF attachment — the system classifies it, extracts structured data, decides on routing, and drafts a German response. Built with [Microsoft Agent Framework](https://aka.ms/agent-framework) + Azure AI Foundry.

### The Problem

Aurion agents manually open emails, read PDF attachments, classify requests, extract data, decide next steps, and draft replies — repetitive, slow, and error-prone at scale.

### The Solution

A 6-step agentic workflow that automates the entire process:

```
Email + PDF ──▶ Email Intake ──▶ Doc Intelligence ──▶ Classify ──▶ Extract ──▶ Decide ─┐
                                                                                        │
                  auto_process ──▶ Confirmation email (5-10 day timeline)  ◀─────────────┤
                  escalate ──────▶ Specialist referral (priority)         ◀─────────────┤
                  request_info ──▶ Request for missing documents          ◀─────────────┘
```

Each box is an **Executor** (self-contained unit). The **WorkflowBuilder** wires them together with switch-case routing at the `Decide` step.

## Repo Structure

```
app/
├── backend/                   ← Python (FastAPI + Agent Framework)
│   ├── aurion_claim_workflow/  ← Executors, models, config
│   ├── server/                ← REST + SSE streaming API
│   ├── playground/            ← Run scenarios from terminal
│   └── tests/
├── frontend/                  ← React 19 + TypeScript (Vite)
└── aurion-hosted-agent/       ← Hosted agent for Foundry deployment
infra/                         ← Bicep templates for Azure resources
```

## Quick Start

### Prerequisites

- **Python 3.13+** / **uv** (`pip install uv`) / **Node.js 18+** / **Azure CLI**
- Logged in: `az login`

### Setup

```bash
cp .env.example .env   # fill in your endpoints
cd app/backend && uv sync
cd app/frontend && npm install
```

```env
AZURE_AI_PROJECT_ENDPOINT=<your-foundry-project-endpoint>
AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME=gpt-4.1
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=<your-doc-intelligence-endpoint>
```

### Run

**Full stack** (API + dashboard):
```bash
cd app/backend  && uv run uvicorn server.app:app --reload --port 8000
cd app/frontend && npm run dev
```
Open http://localhost:5173 — submit a claim and watch the pipeline in real time. API docs at http://localhost:8000/docs.

**Playground** (terminal only):
```bash
cd app/backend
uv run python playground/run_scenarios.py 1   # Maria Huber — auto_process
uv run python playground/run_scenarios.py 2   # Thomas Wagner — escalate
uv run python playground/run_scenarios.py 3   # Anna Berger — request_more_info
```

**Tests**: `cd app/backend && uv run pytest -v`

## Test Scenarios

| # | Customer | Damage | Amount | Route |
|---|----------|--------|--------|-------|
| 1 | Maria Huber | Water damage (pipe burst) | €3,200 | `auto_process` — all data present, low amount |
| 2 | Thomas Wagner | Fire damage (warehouse) | €85,000 | `escalate` — high amount, critical urgency |
| 3 | Anna Berger | Car damage (vague, no policy #) | unknown | `request_more_info` — missing fields |

### Example Walkthrough (Scenario 1)

> **From:** maria.huber@gmail.com — *"Wasserschaden in meiner Wohnung"*
> Attached: `kostenvoranschlag_wasserschaden.pdf`

1. **Email Intake** — extracts body, metadata, detects PDF
2. **Doc Intelligence** — processes the PDF cost estimate (line items, amounts)
3. **Classify** — new property damage claim, urgency: normal
4. **Extract** — policy HV-2024-38291, Maria Huber, water damage, €3,200
5. **Decide** — under threshold, all fields present → `auto_process`
6. **Respond** — German confirmation email with reference number + timeline

## How It Works

**Executors** (`aurion_claim_workflow/executors/`) each receive typed input, call the LLM with structured output (Pydantic `response_format`), and send typed results downstream:

```python
class ClassificationExecutor(Executor):
    @handler
    async def run(self, doc: ProcessedDocument, ctx: WorkflowContext) -> None:
        response = await self._client.get_response(
            messages=..., options={"response_format": ClassificationResult}
        )
        result = ClassificationResult.model_validate_json(response.messages[-1].text)
        await ctx.send_message(result)
```

**Workflow** (`workflow.py`) wires executors with `WorkflowBuilder` + switch-case routing:

```python
builder.add_switch_case_edge_group(decide, [
    Case(condition=get_route("auto_process"), target=auto_response),
    Case(condition=get_route("escalate"), target=escalate_response),
    Default(target=missing_info_response),
])
```

**Hosted Agent** (`aurion-hosted-agent/`) — minimal version for Azure AI Foundry Agent Service deployment. See its [README](app/aurion-hosted-agent/README.md).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | [Microsoft Agent Framework](https://aka.ms/agent-framework) v1.0.0rc3 |
| LLM | Azure AI Foundry — GPT-4.1 |
| Document Processing | Azure Document Intelligence (prebuilt-layout) |
| Backend | FastAPI + Uvicorn |
| Frontend | React 19 + TypeScript + Vite |
| Structured Output | Pydantic v2 |
| Auth | DefaultAzureCredential (no API keys) |

## What's Real vs. Simulated

| Built | Simulated |
|-------|-----------|
| Full 6-step workflow with conditional routing | Email trigger (sample emails + PDFs as input) |
| Doc Intelligence PDF extraction | Backend systems (policy lookup, claim submission) |
| LLM classification, extraction, response drafting | |
| German-language responses | |
