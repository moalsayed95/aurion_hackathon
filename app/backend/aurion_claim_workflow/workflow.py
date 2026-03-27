"""Workflow pipeline — assembles the Aurion claim intake executor graph."""

from agent_framework import Case, Default, WorkflowBuilder

from .config import create_client, get_credential
from .executors.classify import ClassificationExecutor
from .executors.decide import DecisionExecutor
from .executors.doc_intelligence import doc_intelligence
from .executors.email_intake import EmailIntakeExecutor
from .executors.extract import ExtractionExecutor
from .executors.respond import (
    AutoResponseExecutor,
    EscalateResponseExecutor,
    MissingInfoResponseExecutor,
    get_route,
)


def build_workflow(sample_pdf: str | None = None):
    """Build the Aurion claim intake workflow with sequential + switch-case routing."""

    # Single shared client for all LLM executors
    credential = get_credential()
    client = create_client(credential=credential)

    # Instantiate executors
    email_intake = EmailIntakeExecutor(sample_pdf=sample_pdf) if sample_pdf else EmailIntakeExecutor()
    classify = ClassificationExecutor(client=client, id="classify")
    extract = ExtractionExecutor(client=client, id="extract")
    decide = DecisionExecutor(client=client, id="decide")
    auto_response = AutoResponseExecutor(client=client, id="auto_response")
    escalate_response = EscalateResponseExecutor(client=client, id="escalate_response")
    missing_info_response = MissingInfoResponseExecutor(client=client, id="missing_info_response")

    # Build the workflow graph
    builder = WorkflowBuilder(name="aurion_claim_intake", start_executor=email_intake)

    # Sequential: intake → doc intelligence → classify → extract → decide
    builder.add_edge(email_intake, doc_intelligence)
    builder.add_edge(doc_intelligence, classify)
    builder.add_edge(classify, extract)
    builder.add_edge(extract, decide)

    # Switch: route based on decision action
    builder.add_switch_case_edge_group(
        decide,
        [
            Case(condition=get_route("auto_process"), target=auto_response),
            Case(condition=get_route("escalate"), target=escalate_response),
            Default(target=missing_info_response),
        ],
    )

    return builder.build()
