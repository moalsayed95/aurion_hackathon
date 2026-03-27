# Aurion Hosted Agent — Reference

Simplified single-node claim classification agent demonstrating how to deploy a
Microsoft Agent Framework workflow as a **Foundry hosted agent**.

## What This Is

A minimal reference implementation showing the hosted agent deployment pattern:

- **`agent.yaml`** — Foundry agent manifest (name, model binding, env vars)
- **`Dockerfile`** — Multi-stage build for deployment to Foundry Agent Service
- **`main.py`** — Entry point with hosted-agent mode (`from_agent_framework`) and DevUI mode
- **`config.py`** — Azure credential + client factory (Managed Identity in Azure, DefaultAzureCredential locally)
- **`executor.py`** — Single `ClassificationExecutor` (Executor + @handler pattern)
- **`workflow.py`** — Single-node workflow assembled via `WorkflowBuilder`
- **`pyproject.toml`** — Dependencies matching the full backend

## Architecture

```
POST /responses  (Agent Server protocol)
      │
      ▼
ClassificationExecutor  ──→  ClassificationResult (JSON)
      │
      ▼
  Response returned via Agent Server protocol
```

The full Aurion backend (`app/backend/`) has the complete multi-node pipeline
(email intake → doc intelligence → classify → extract → decide → respond).
This hosted agent shows how to take any subset and deploy it to Foundry.

## How to Extend

To add more nodes from the full backend pipeline:

1. Copy the executor class(es) from `app/backend/aurion_claim_workflow/executors/`
2. Add them to `workflow.py` with `builder.add_edge(...)` calls
3. Update the input/output types to chain them together

## Local Dev

```bash
# Install dependencies
uv sync

# Run in DevUI mode (local testing with web UI)
python main.py devui

# Run in hosted agent mode (Agent Server protocol)
python main.py
```

## Deploy to Foundry

```bash
# Build Docker image
docker build -t aurion-claim-agent .

# Push to ACR and deploy via Foundry CLI
# (see Microsoft Foundry documentation for full deployment steps)
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AZURE_AI_PROJECT_ENDPOINT` | Foundry project endpoint URL |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | Model deployment name (e.g., `gpt-4o`) |
| `PORT` | Server port (default: 8088) |
