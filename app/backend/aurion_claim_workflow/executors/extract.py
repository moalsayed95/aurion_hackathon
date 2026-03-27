"""Extraction Executor — LLM-powered structured data extraction."""

import logging

from agent_framework import Executor, Message, WorkflowContext, handler

from ..models import ClassifiedEmail, ExtractedClaimData, ExtractedEmail

logger = logging.getLogger(__name__)


class ExtractionExecutor(Executor):
    """Uses LLM to extract structured claim data from classified email + document."""

    def __init__(self, client, id: str = "extract"):
        self._client = client
        super().__init__(id=id)

    @handler
    async def run(self, classified: ClassifiedEmail, ctx: WorkflowContext[ExtractedEmail]) -> None:
        logger.info("Extracting claim data via LLM...")

        prompt = (
            f"Extrahiere alle relevanten Schadensdaten aus der folgenden E-Mail und dem Dokument.\n\n"
            f"--- E-Mail ---\n"
            f"Von: {classified.sender}\n"
            f"Betreff: {classified.subject}\n"
            f"Inhalt:\n{classified.body}\n\n"
            f"--- Dokumenttext ---\n"
            f"{classified.pdf_text}\n\n"
            f"Extrahiere: Polizzennummer, Kundenname, Schadensdatum, Schadenshöhe, "
            f"Schadensart, Beschreibung.\n\n"
            f"WICHTIG für missing_fields: NUR die folgenden Pflichtfelder prüfen: "
            f"policy_number, customer_name, incident_date, claim_amount, damage_type. "
            f"Nur Felder aus dieser Liste in missing_fields aufnehmen, die tatsächlich NICHT vorhanden sind. "
            f"Keine zusätzlichen Felder wie Bankverbindung, Fotos etc. einfügen.\n\n"
            f"data_quality_score: 0.0-1.0 basierend auf Vollständigkeit der 5 Pflichtfelder.\n"
            f"Antworte ausschließlich im JSON-Format."
        )

        messages = [
            Message("system", text=(
                "Du bist ein Experte für die Datenextraktion aus Versicherungsdokumenten bei Aurion. "
                "Extrahiere alle relevanten Schadensinformationen aus der E-Mail und dem Dokument. "
                "Antworte ausschließlich im JSON-Format mit den Feldern: "
                "policy_number, customer_name, incident_date, claim_amount (als Zahl), "
                "damage_type, incident_description, missing_fields (Liste fehlender Pflichtfelder), "
                "data_quality_score (0.0-1.0)."
            )),
            Message("user", text=prompt),
        ]

        response = await self._client.get_response(
            messages=messages,
            options={"response_format": ExtractedClaimData},
        )
        extracted = ExtractedClaimData.model_validate_json(response.messages[-1].text)

        missing = ", ".join(extracted.missing_fields) if extracted.missing_fields else "keine"
        logger.info("Customer: %s, Amount: %s, Missing: %s",
                     extracted.customer_name, extracted.claim_amount, missing)

        result = ExtractedEmail(
            sender=classified.sender,
            subject=classified.subject,
            body=classified.body,
            pdf_text=classified.pdf_text,
            classification=classified.classification,
            extracted_data=extracted,
        )
        await ctx.send_message(result)
