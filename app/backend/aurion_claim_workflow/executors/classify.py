"""Classification Executor — LLM-powered document classification."""

import logging

from agent_framework import Executor, Message, WorkflowContext, handler

from ..models import ClassificationResult, ClassifiedEmail, ProcessedDocument

logger = logging.getLogger(__name__)


class ClassificationExecutor(Executor):
    """Uses LLM to classify the insurance document type, urgency, and confidence."""

    def __init__(self, client, id: str = "classify"):
        self._client = client
        super().__init__(id=id)

    @handler
    async def run(self, doc: ProcessedDocument, ctx: WorkflowContext[ClassifiedEmail]) -> None:
        logger.info("Classifying document via LLM...")

        tables_text = "\n\n".join(doc.pdf_tables) if doc.pdf_tables else "(no tables)"
        prompt = (
            f"Analyze the following insurance email and attached document.\n\n"
            f"--- Email ---\n"
            f"From: {doc.sender}\n"
            f"Subject: {doc.subject}\n"
            f"Body:\n{doc.body}\n\n"
            f"--- Attached document (extracted text) ---\n"
            f"{doc.pdf_text}\n\n"
            f"--- Tables from the document ---\n"
            f"{tables_text}\n\n"
            f"Classify this email. Respond exclusively in JSON format."
        )

        messages = [
            Message("system", text=(
                "You are an expert insurance document classifier at Aurion. "
                "Analyze the email and attached document and classify them. "
                "The email and document may be in any language — classify regardless of language. "
                "Respond exclusively in JSON format with the fields: "
                "document_type (new_claim|claim_status|policy_inquiry|invoice|complaint|general), "
                "urgency (low|normal|high|critical), confidence (0.0-1.0), reasoning (string)."
            )),
            Message("user", text=prompt),
        ]

        response = await self._client.get_response(
            messages=messages,
            options={"response_format": ClassificationResult},
        )
        classification = ClassificationResult.model_validate_json(response.messages[-1].text)

        logger.info("Type: %s, Urgency: %s, Confidence: %.0f%%",
                     classification.document_type, classification.urgency, classification.confidence * 100)

        ctx.set_state("processed_doc", doc)
        result = ClassifiedEmail(
            sender=doc.sender,
            subject=doc.subject,
            body=doc.body,
            pdf_text=doc.pdf_text,
            classification=classification,
        )
        await ctx.send_message(result)
