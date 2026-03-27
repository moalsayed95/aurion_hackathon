# Aurion Claim Intake — Hackathon Starter

An AI-powered insurance claim intake system for Aurion. A customer sends an email with a PDF attachment — the system automatically classifies it, extracts key data, decides what to do, and drafts a German response. All powered by [Microsoft Agent Framework](https://aka.ms/agent-framework) + Azure AI Foundry.

## What It Does (30-second version)

```
Customer email + PDF
        │
        ▼
  ┌─────────────┐     ┌──────────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
  │ Email Intake │────▶│ Document AI  │────▶│ Classify  │────▶│ Extract  │────▶│  Decide  │
  └─────────────┘     └──────────────┘     └───────────┘     └──────────┘     └────┬─────┘
                                                                                   │
                       ┌───────────────────────────────────────────────────────────┐│
                       │                  ROUTING                                  ││
                       │  auto_process ──▶ Confirmation email (5-10 day timeline) ◀┤│
                       │  escalate ──────▶ Specialist referral (priority)         ◀┤│
                       │  request_info ──▶ Polite request for missing fields      ◀┘│
                       └────────────────────────────────────────────────────────────┘
```

Each box is an **Executor** — a self-contained unit that does one job. The **WorkflowBuilder** wires them together. The `Decide` step uses **switch-case routing** to pick the right response branch.

## Repo Structure

```
app/
├── backend/                  ← Python backend (FastAPI + Agent Framework)
│   ├── aurion_claim_workflow/ ← The workflow: executors, models, config
│   ├── server/               ← FastAPI API (REST + SSE streaming)
│   ├── playground/           ← Run scenarios from the terminal
│   └── tests/
├── frontend/                 ← React + TypeScript dashboard (Vite)
└── aurion-hosted-agent/       ← Simplified hosted agent for Foundry deployment
```

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.13+ | [python.org](https://www.python.org/) |
| uv | latest | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Azure CLI | latest | [aka.ms/installAzureCli](https://aka.ms/installAzureCli) |

You need to be logged in to Azure:

```bash
az login
```

## Setup

### 1. Environment Variables

Copy the example and fill in your values:

```bash
cp .env.example .env
```

```env
AZURE_AI_PROJECT_ENDPOINT=<your-foundry-project-endpoint>
AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME=gpt-4.1
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=<your-doc-intelligence-endpoint>
```

### 2. Backend

```bash
cd app/backend
uv sync
```

### 3. Frontend

```bash
cd app/frontend
npm install
```

## Run

### Option A: Full Stack (API + Dashboard)

Terminal 1 — backend:
```bash
cd app/backend
uv run uvicorn server.app:app --reload --port 8000
```

Terminal 2 — frontend:
```bash
cd app/frontend
npm run dev
```

Open http://localhost:5173 — submit a claim and watch the pipeline steps light up in real time.

API docs at http://localhost:8000/docs.

### Option B: Playground (terminal only, no server needed)

```bash
cd app/backend
uv run python playground/run_scenarios.py 1   # Maria Huber — auto_process
uv run python playground/run_scenarios.py 2   # Thomas Wagner — escalate
uv run python playground/run_scenarios.py 3   # Anna Berger — request_more_info
```

### Tests

```bash
cd app/backend
uv run pytest -v
```

## Test Scenarios

| # | Customer | Damage | Amount | Route |
|---|----------|--------|--------|-------|
| 1 | Maria Huber | Water damage (pipe burst) | €3,200 | `auto_process` — all data present, low amount |
| 2 | Thomas Wagner | Fire damage (warehouse) | €85,000 | `escalate` — high amount, critical urgency |
| 3 | Anna Berger | Car damage (vague, no policy #) | unknown | `request_more_info` — missing fields |

## How the Code Works

### Executors (`aurion_claim_workflow/executors/`)

Each executor is a class that extends `Executor` and has a `@handler` method:

```python
class ClassificationExecutor(Executor):
    def __init__(self, client, id="classify"):
        self._client = client
        super().__init__(id=id)

    @handler
    async def run(self, doc: ProcessedDocument, ctx: WorkflowContext[ClassifiedEmail]) -> None:
        response = await self._client.get_response(messages=..., options={"response_format": ClassificationResult})
        result = ClassificationResult.model_validate_json(response.messages[-1].text)
        await ctx.send_message(result)
```

Key pattern: **receive typed input → call LLM with structured output → send typed result to next executor**.

### Workflow (`aurion_claim_workflow/workflow.py`)

Executors are wired together with `WorkflowBuilder`:

```python
builder = WorkflowBuilder(name="aurion_claim_intake", start_executor=email_intake)
builder.add_edge(email_intake, doc_intelligence)
builder.add_edge(doc_intelligence, classify)
# ... more edges ...
builder.add_switch_case_edge_group(decide, [
    Case(condition=get_route("auto_process"), target=auto_response),
    Case(condition=get_route("escalate"), target=escalate_response),
    Default(target=missing_info_response),
])
```

### Hosted Agent (`aurion-hosted-agent/`)

A minimal single-node version showing how to deploy a workflow to **Azure AI Foundry Agent Service**. Contains `agent.yaml`, `Dockerfile`, and one executor. See its [README](app/aurion-hosted-agent/README.md) for details.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Orchestration | [Microsoft Agent Framework](https://aka.ms/agent-framework) v1.0.0rc3 |
| LLM | Azure AI Foundry — GPT-4.1 |
| Document Processing | Azure Document Intelligence (prebuilt-layout) |
| Backend | FastAPI + Uvicorn |
| Frontend | React 19 + TypeScript + Vite |
| Structured Output | Pydantic v2 (response_format) |
| Auth | Azure CLI credential (no API keys) |
| Package Manager | uv (Python) / npm (frontend) |

## Azure Resources

| Resource | Value |
|----------|-------|
| AI Foundry Project | `<your-foundry-project>` |
| Resource Group | `<your-resource-group>` |
| Model Deployment | `gpt-4.1` |
| Document Intelligence | `<your-doc-intelligence>` |
