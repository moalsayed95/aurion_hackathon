# ── Stage 1: Build ──────────────────────────────────────────
# Build context is the workspace root (set by Foundry extension).
#   docker build -f app/aurion-hosted-agent/Dockerfile -t aurion-claim-agent .
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /opt/app

# Install dependencies first (cached unless lock changes)
COPY app/aurion-hosted-agent/pyproject.toml app/aurion-hosted-agent/.python-version ./
RUN uv sync --frozen --no-dev --no-install-project || uv sync --no-dev --no-install-project

# Copy application source and finalise install
COPY app/aurion-hosted-agent/ .
RUN uv sync --frozen --no-dev || uv sync --no-dev

# ── Stage 2: Runtime ────────────────────────────────────────
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/app

# Copy installed packages from builder venv
COPY --from=builder /opt/app/.venv/lib/python3.13/site-packages \
                    /usr/local/lib/python3.13/site-packages

# Copy application source
COPY --from=builder /opt/app /opt/app

EXPOSE 8088

CMD ["python", "main.py"]
