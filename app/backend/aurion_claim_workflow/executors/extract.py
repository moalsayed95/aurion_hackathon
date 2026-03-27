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
            f"Extract all relevant claim data from the following email and document.\n\n"
            f"--- Email ---\n"
            f"From: {classified.sender}\n"
            f"Subject: {classified.subject}\n"
            f"Body:\n{classified.body}\n\n"
            f"--- Document text ---\n"
            f"{classified.pdf_text}\n\n"
            f"Extract: policy number, customer name, incident date, claim amount, "
            f"damage type, incident description.\n\n"
            f"IMPORTANT for claim_amount: If the email does not mention an amount but a "
            f"cost estimate (Kostenvoranschlag) or invoice is attached, use the net amount "
            f"(Nettobetrag) from the document as claim_amount. The attached document belongs "
            f"to this email — treat it as the sender's attachment even if names or details "
            f"in the document differ slightly. Cross-reference BOTH sources to fill in "
            f"as many fields as possible.\n\n"
            f"IMPORTANT for missing_fields: Only check these 5 required fields: "
            f"policy_number, customer_name, incident_date, claim_amount, damage_type. "
            f"Only list fields from this set that are truly NOT available in either source. "
            f"Do NOT add extra fields like bank details, photos, etc.\n\n"
            f"data_quality_score: 0.0-1.0 based on completeness of the 5 required fields.\n"
            f"Respond exclusively in JSON format."
        )

        messages = [
            Message("system", text=(
                "You are an expert insurance data extraction specialist at Aurion. "
                "Extract all relevant claim information from the email and document. "
                "The email and document may be in any language — extract data regardless. "
                "Respond exclusively in JSON format with the fields: "
                "policy_number, customer_name, incident_date, claim_amount (as a number), "
                "damage_type, incident_description, missing_fields (list of missing required fields), "
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
