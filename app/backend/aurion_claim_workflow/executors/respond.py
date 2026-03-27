"""Response Executors — LLM-powered German email drafting for each routing branch."""

import logging
from typing import Any

from typing_extensions import Never

from agent_framework import Executor, Message, WorkflowContext, handler

from ..models import DecidedEmail, WorkflowOutput

logger = logging.getLogger(__name__)


# --- Routing condition helper (used by workflow switch-case) ---

def get_route(expected_action: str):
    def condition(message: Any) -> bool:
        return isinstance(message, DecidedEmail) and message.decision.action == expected_action
    return condition


# === Auto-process branch ===

class AutoResponseExecutor(Executor):
    """Drafts a confirmation email for automatically processed claims."""

    def __init__(self, client, id: str = "auto_response"):
        self._client = client
        super().__init__(id=id)

    @handler
    async def run(self, decided: DecidedEmail, ctx: WorkflowContext[Never, WorkflowOutput]) -> None:
        logger.info("Drafting auto-process response via LLM...")

        data = decided.extracted_data
        prompt = (
            f"Verfasse eine professionelle Bestätigungs-E-Mail auf Deutsch (österreichisches Deutsch, Sie-Form) "
            f"an den Kunden {data.customer_name}.\n\n"
            f"Der Schadensfall wurde automatisch erfasst:\n"
            f"- Polizzennummer: {data.policy_number}\n"
            f"- Schadensart: {data.damage_type}\n"
            f"- Schadenshöhe: EUR {data.claim_amount:,.2f}\n"
            f"- Schadensdatum: {data.incident_date}\n\n"
            f"Bestätige den Eingang, nenne die Polizzennummer, und gib einen Bearbeitungszeitraum "
            f"von 5-10 Werktagen an. Ton: professionell, empathisch, sachlich.\n"
            f"Antworte nur mit dem E-Mail-Text (kein JSON)."
        )

        messages = [
            Message("system", text=(
                "Du bist ein Kundenservice-Spezialist bei Aurion. "
                "Verfasse professionelle, empathische Antwort-E-Mails auf österreichischem Deutsch in der Sie-Form. "
                "Antworte nur mit dem E-Mail-Text."
            )),
            Message("user", text=prompt),
        ]

        response = await self._client.get_response(messages=messages)
        drafted = response.messages[-1].text if response.messages else ""

        logger.info("Auto-process response drafted (%d chars)", len(drafted))

        output = WorkflowOutput(
            decision=decided.decision,
            extracted_data=decided.extracted_data,
            classification=decided.classification,
            drafted_response=drafted,
        )
        await ctx.yield_output(output)


# === Escalate branch ===

class EscalateResponseExecutor(Executor):
    """Drafts a specialist referral email for escalated claims."""

    def __init__(self, client, id: str = "escalate_response"):
        self._client = client
        super().__init__(id=id)

    @handler
    async def run(self, decided: DecidedEmail, ctx: WorkflowContext[Never, WorkflowOutput]) -> None:
        logger.info("Drafting escalation response via LLM...")

        data = decided.extracted_data
        prompt = (
            f"Verfasse eine professionelle E-Mail auf Deutsch (österreichisches Deutsch, Sie-Form) "
            f"an den Kunden {data.customer_name}.\n\n"
            f"Der Schadensfall wird an einen Spezialisten weitergeleitet:\n"
            f"- Polizzennummer: {data.policy_number}\n"
            f"- Schadensart: {data.damage_type}\n"
            f"- Schadenshöhe: EUR {data.claim_amount:,.2f}\n"
            f"- Begründung Eskalation: {decided.decision.reasoning}\n\n"
            f"Bestätige den Eingang, erkläre dass ein Spezialist den Fall mit Priorität prüft, "
            f"und nenne einen beschleunigten Bearbeitungszeitraum von 2-3 Werktagen. "
            f"Ton: professionell, empathisch, verständnisvoll.\n"
            f"Antworte nur mit dem E-Mail-Text (kein JSON)."
        )

        messages = [
            Message("system", text=(
                "Du bist ein Senior Kundenservice-Spezialist bei Aurion für eskalierte Fälle. "
                "Verfasse professionelle, verständnisvolle Antwort-E-Mails auf österreichischem Deutsch in der Sie-Form. "
                "Zeige Verständnis für die Dringlichkeit. Antworte nur mit dem E-Mail-Text."
            )),
            Message("user", text=prompt),
        ]

        response = await self._client.get_response(messages=messages)
        drafted = response.messages[-1].text if response.messages else ""

        logger.info("Escalation response drafted (%d chars)", len(drafted))

        output = WorkflowOutput(
            decision=decided.decision,
            extracted_data=decided.extracted_data,
            classification=decided.classification,
            drafted_response=drafted,
        )
        await ctx.yield_output(output)


# === Request more info branch ===

class MissingInfoResponseExecutor(Executor):
    """Drafts a polite information request email when data is incomplete."""

    def __init__(self, client, id: str = "missing_info_response"):
        self._client = client
        super().__init__(id=id)

    @handler
    async def run(self, decided: DecidedEmail, ctx: WorkflowContext[Never, WorkflowOutput]) -> None:
        logger.info("Drafting missing-info request via LLM...")

        data = decided.extracted_data
        missing = ", ".join(data.missing_fields) if data.missing_fields else "diverse Angaben"
        prompt = (
            f"Verfasse eine freundliche E-Mail auf Deutsch (österreichisches Deutsch, Sie-Form) "
            f"an den Kunden (Absender: {decided.sender}).\n\n"
            f"Es fehlen folgende Informationen zur Bearbeitung des Schadensfalls:\n"
            f"- Fehlende Felder: {missing}\n"
            f"- Bekannte Infos: Schadensart={data.damage_type or 'unbekannt'}, "
            f"Name={data.customer_name or 'unbekannt'}\n\n"
            f"Bitte den Kunden höflich, die fehlenden Informationen nachzureichen. "
            f"Erkläre warum diese Angaben benötigt werden. "
            f"Ton: freundlich, hilfsbereit, geduldig.\n"
            f"Antworte nur mit dem E-Mail-Text (kein JSON)."
        )

        messages = [
            Message("system", text=(
                "Du bist ein freundlicher Kundenservice-Mitarbeiter bei Aurion. "
                "Verfasse höfliche Nachfrage-E-Mails auf österreichischem Deutsch in der Sie-Form. "
                "Erkläre klar welche Informationen fehlen und warum sie benötigt werden. "
                "Antworte nur mit dem E-Mail-Text."
            )),
            Message("user", text=prompt),
        ]

        response = await self._client.get_response(messages=messages)
        drafted = response.messages[-1].text if response.messages else ""

        logger.info("Missing-info response drafted (%d chars)", len(drafted))

        output = WorkflowOutput(
            decision=decided.decision,
            extracted_data=decided.extracted_data,
            classification=decided.classification,
            drafted_response=drafted,
        )
        await ctx.yield_output(output)
