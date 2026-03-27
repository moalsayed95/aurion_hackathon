"""Claim Classification Executor — single-node demo for hosted agent pattern."""

import logging
from typing import Literal

from pydantic import BaseModel

from agent_framework import Executor, Message, WorkflowContext, handler

logger = logging.getLogger(__name__)


# --- Input / Output models ---

class ClaimInput(BaseModel):
    sender: str
    subject: str
    body: str


class ClassificationResult(BaseModel):
    document_type: Literal[
        "new_claim", "claim_status", "policy_inquiry", "invoice", "complaint", "general"
    ]
    urgency: Literal["low", "normal", "high", "critical"]
    confidence: float
    reasoning: str


# --- Executor ---

class ClassificationExecutor(Executor):
    """Uses LLM to classify an incoming insurance email."""

    def __init__(self, client, id: str = "classify"):
        self._client = client
        super().__init__(id=id)

    @handler
    async def run(self, claim: ClaimInput, ctx: WorkflowContext[ClassificationResult]) -> None:
        logger.info("Classifying claim from %s...", claim.sender)

        messages = [
            Message("system", text=(
                "Du bist ein Experte für die Klassifikation von Versicherungsdokumenten bei Aurion. "
                "Analysiere die E-Mail und klassifiziere sie. "
                "Antworte ausschließlich im JSON-Format mit den Feldern: "
                "document_type (new_claim|claim_status|policy_inquiry|invoice|complaint|general), "
                "urgency (low|normal|high|critical), confidence (0.0-1.0), reasoning (string)."
            )),
            Message("user", text=(
                f"Von: {claim.sender}\n"
                f"Betreff: {claim.subject}\n"
                f"Inhalt:\n{claim.body}"
            )),
        ]

        response = await self._client.get_response(
            messages=messages,
            options={"response_format": ClassificationResult},
        )
        result = ClassificationResult.model_validate_json(response.messages[-1].text)

        logger.info("Type: %s, Urgency: %s, Confidence: %.0f%%",
                     result.document_type, result.urgency, result.confidence * 100)

        await ctx.send_message(result)
