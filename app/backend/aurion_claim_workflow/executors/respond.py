"""Response Executors — LLM-powered email drafting for each routing branch."""

import logging
from typing import Any

from typing_extensions import Never

from agent_framework import Executor, Message, WorkflowContext, handler

from ..models import DecidedEmail, WorkflowOutput

logger = logging.getLogger(__name__)

_LANGUAGE_INSTRUCTION = (
    "IMPORTANT: Detect the language of the original customer email below and reply "
    "in the SAME language. If the customer wrote in German, reply in German "
    "(Austrian German, formal Sie-Form). If they wrote in English, reply in English. "
    "Match the customer's language exactly."
)


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
            f"Draft a professional confirmation email to the customer {data.customer_name}.\n\n"
            f"The claim has been automatically registered:\n"
            f"- Policy number: {data.policy_number}\n"
            f"- Damage type: {data.damage_type}\n"
            f"- Claim amount: EUR {data.claim_amount:,.2f}\n"
            f"- Incident date: {data.incident_date}\n\n"
            f"Confirm receipt, reference the policy number, and state an expected "
            f"processing time of 5-10 business days. Tone: professional, empathetic, factual.\n\n"
            f"{_LANGUAGE_INSTRUCTION}\n\n"
            f"Original customer email:\n{decided.body}\n\n"
            f"Respond with the email text only (no JSON)."
        )

        messages = [
            Message("system", text=(
                "You are a customer service specialist at Aurion insurance. "
                "Draft professional, empathetic response emails. "
                "Respond with the email text only."
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
            f"Draft a professional email to the customer {data.customer_name}.\n\n"
            f"The case is being escalated to a specialist:\n"
            f"- Policy number: {data.policy_number}\n"
            f"- Damage type: {data.damage_type}\n"
            f"- Claim amount: EUR {data.claim_amount:,.2f}\n"
            f"- Escalation reason: {decided.decision.reasoning}\n\n"
            f"Confirm receipt, explain that a specialist will review the case with priority, "
            f"and state an expedited processing time of 2-3 business days. "
            f"Tone: professional, empathetic, understanding.\n\n"
            f"{_LANGUAGE_INSTRUCTION}\n\n"
            f"Original customer email:\n{decided.body}\n\n"
            f"Respond with the email text only (no JSON)."
        )

        messages = [
            Message("system", text=(
                "You are a senior customer service specialist at Aurion insurance for escalated cases. "
                "Draft professional, understanding response emails. "
                "Show understanding for the urgency. Respond with the email text only."
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
        missing = ", ".join(data.missing_fields) if data.missing_fields else "various details"
        prompt = (
            f"Draft a friendly email to the customer (sender: {decided.sender}).\n\n"
            f"The following information is missing to process the claim:\n"
            f"- Missing fields: {missing}\n"
            f"- Known info: damage type={data.damage_type or 'unknown'}, "
            f"name={data.customer_name or 'unknown'}\n\n"
            f"Politely ask the customer to provide the missing information. "
            f"Explain why each piece of information is needed. "
            f"Tone: friendly, helpful, patient.\n\n"
            f"{_LANGUAGE_INSTRUCTION}\n\n"
            f"Original customer email:\n{decided.body}\n\n"
            f"Respond with the email text only (no JSON)."
        )

        messages = [
            Message("system", text=(
                "You are a friendly customer service representative at Aurion insurance. "
                "Draft polite follow-up emails requesting missing information. "
                "Clearly explain what information is missing and why it is needed. "
                "Respond with the email text only."
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
