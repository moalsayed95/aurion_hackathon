"""Shared configuration — environment variables, Azure client factory."""

import os

from dotenv import load_dotenv

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

load_dotenv()


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
    deployment = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")

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
