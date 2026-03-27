"""Workflow pipeline — single-node classification workflow for hosted agent demo."""

from agent_framework import WorkflowBuilder

from config import create_client, get_credential
from executor import ClassificationExecutor


def create_workflow():
    """Build a minimal single-node workflow for Foundry hosted agent deployment."""

    credential = get_credential()
    client = create_client(credential=credential)

    classify = ClassificationExecutor(client=client, id="classify")

    builder = WorkflowBuilder(name="aurion_claim_classify", start_executor=classify)

    # Single node — no edges needed

    return builder.build()
