"""Shared configuration — environment variables, Azure client factory."""

import os
from pathlib import Path

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from dotenv import load_dotenv

# Try to load .env from repo root (local dev) or /app/.env (Docker).
_config_file = Path(__file__).resolve()
for depth in (3, 2):  # Try repo root first, then backend/ parent
    try:
        candidate = _config_file.parents[depth] / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            break
    except IndexError:
        continue


def get_credential():
    """Use Managed Identity when running in Azure, otherwise DefaultAzureCredential."""
    return (
        ManagedIdentityCredential()
        if os.getenv("MSI_ENDPOINT") or os.getenv("IDENTITY_ENDPOINT") or os.getenv("AZURE_FEDERATED_TOKEN_FILE")
        else DefaultAzureCredential()
    )


def create_client(credential=None) -> AzureOpenAIResponsesClient:
    """Create the Azure OpenAI Responses client.

    Detects whether the endpoint is a Foundry project URL (project_endpoint)
    or a direct Azure OpenAI URL (endpoint) and configures accordingly.
    """
    cred = credential or get_credential()
    ep = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    deployment = os.environ.get(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME",
        os.environ.get("AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME", ""),
    )

    # Foundry project endpoints contain "/api/projects/"
    if "/api/projects/" in ep:
        return AzureOpenAIResponsesClient(
            project_endpoint=ep,
            credential=cred,
            deployment_name=deployment,
        )
    return AzureOpenAIResponsesClient(
        endpoint=ep,
        credential=cred,
        deployment_name=deployment,
    )
