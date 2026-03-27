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

        tables_text = "\n\n".join(doc.pdf_tables) if doc.pdf_tables else "(keine Tabellen)"
        prompt = (
            f"Analysiere die folgende Versicherungs-E-Mail und das beigefügte Dokument.\n\n"
            f"--- E-Mail ---\n"
            f"Von: {doc.sender}\n"
            f"Betreff: {doc.subject}\n"
            f"Inhalt:\n{doc.body}\n\n"
            f"--- Beigefügtes Dokument (extrahierter Text) ---\n"
            f"{doc.pdf_text}\n\n"
            f"--- Tabellen aus dem Dokument ---\n"
            f"{tables_text}\n\n"
            f"Klassifiziere diese E-Mail. Antworte ausschließlich im JSON-Format."
        )

        messages = [
            Message("system", text=(
                "Du bist ein Experte für die Klassifikation von Versicherungsdokumenten bei Aurion. "
                "Analysiere die E-Mail und das beigefügte Dokument und klassifiziere sie. "
                "Antworte ausschließlich im JSON-Format mit den Feldern: "
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
