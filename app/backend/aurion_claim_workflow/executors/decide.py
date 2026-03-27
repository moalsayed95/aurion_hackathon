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
            f"Decide the routing for this insurance case based on the following data:\n\n"
            f"Classification: {classification.document_type} (urgency: {classification.urgency}, "
            f"confidence: {classification.confidence})\n\n"
            f"Extracted data:\n"
            f"- Policy number: {data.policy_number or 'MISSING'}\n"
            f"- Customer: {data.customer_name or 'MISSING'}\n"
            f"- Incident date: {data.incident_date or 'MISSING'}\n"
            f"- Claim amount: {data.claim_amount or 'MISSING'}\n"
            f"- Damage type: {data.damage_type or 'MISSING'}\n"
            f"- Missing fields: {', '.join(data.missing_fields) if data.missing_fields else 'none'}\n"
            f"- Data quality: {data.data_quality_score}\n\n"
            f"Business rules:\n"
            f"- auto_process: All required fields present, amount < 5,000 EUR, normal urgency\n"
            f"- escalate: Amount > 10,000 EUR, critical urgency, complaint, or low confidence (<0.7)\n"
            f"- request_more_info: Missing required fields or low data quality (<0.6)\n\n"
            f"Respond exclusively in JSON format."
        )

        messages = [
            Message("system", text=(
                "You are a decision assistant for insurance claims at Aurion. "
                "Apply the business rules and decide the routing. "
                "Respond exclusively in JSON format with the fields: "
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
