"""Decision Executor — LLM-powered routing decision based on business rules."""

import logging

from agent_framework import Executor, Message, WorkflowContext, handler

from ..models import DecidedEmail, DecisionResult, ExtractedEmail

logger = logging.getLogger(__name__)


class DecisionExecutor(Executor):
    """Uses LLM to apply business rules and decide routing: auto_process, escalate, or request_more_info."""

    def __init__(self, client, id: str = "decide"):
        self._client = client
        super().__init__(id=id)

    @handler
    async def run(self, extracted: ExtractedEmail, ctx: WorkflowContext[DecidedEmail]) -> None:
        logger.info("Making routing decision via LLM...")

        data = extracted.extracted_data
        classification = extracted.classification
        prompt = (
            f"Entscheide über die Weiterleitung dieses Versicherungsfalls basierend auf folgenden Daten:\n\n"
            f"Klassifikation: {classification.document_type} (Dringlichkeit: {classification.urgency}, "
            f"Konfidenz: {classification.confidence})\n\n"
            f"Extrahierte Daten:\n"
            f"- Polizzennummer: {data.policy_number or 'FEHLT'}\n"
            f"- Kunde: {data.customer_name or 'FEHLT'}\n"
            f"- Schadensdatum: {data.incident_date or 'FEHLT'}\n"
            f"- Schadenshöhe: {data.claim_amount or 'FEHLT'}\n"
            f"- Schadensart: {data.damage_type or 'FEHLT'}\n"
            f"- Fehlende Felder: {', '.join(data.missing_fields) if data.missing_fields else 'keine'}\n"
            f"- Datenqualität: {data.data_quality_score}\n\n"
            f"Geschäftsregeln:\n"
            f"- auto_process: Alle Pflichtfelder vorhanden, Betrag < 5.000 EUR, normale Dringlichkeit\n"
            f"- escalate: Betrag > 10.000 EUR, kritische Dringlichkeit, Beschwerde, oder niedrige Konfidenz (<0.7)\n"
            f"- request_more_info: Fehlende Pflichtfelder oder niedrige Datenqualität (<0.6)\n\n"
            f"Antworte ausschließlich im JSON-Format."
        )

        messages = [
            Message("system", text=(
                "Du bist ein Entscheidungsassistent für Versicherungsschadensfälle bei Aurion. "
                "Wende die Geschäftsregeln an und entscheide über die Weiterleitung. "
                "Antworte ausschließlich im JSON-Format mit den Feldern: "
                "action (auto_process|escalate|request_more_info), reasoning (string), "
                "priority (low|normal|high|critical)."
            )),
            Message("user", text=prompt),
        ]

        response = await self._client.get_response(
            messages=messages,
            options={"response_format": DecisionResult},
        )
        decision = DecisionResult.model_validate_json(response.messages[-1].text)

        logger.info("Action: %s, Priority: %s", decision.action, decision.priority)
        logger.info("Reasoning: %s", decision.reasoning)

        result = DecidedEmail(
            sender=extracted.sender,
            subject=extracted.subject,
            body=extracted.body,
            classification=extracted.classification,
            extracted_data=extracted.extracted_data,
            decision=decision,
        )
        await ctx.send_message(result)
