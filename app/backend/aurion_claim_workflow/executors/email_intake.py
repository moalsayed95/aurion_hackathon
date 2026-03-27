"""Email Intake Executor — accepts EmailInput directly or Message/str from hosted agent adapter."""

import json
import logging
from pathlib import Path

from agent_framework import Executor, Message, WorkflowContext, handler

from ..models import EmailInput

logger = logging.getLogger(__name__)

# Default sample PDF bundled with the hosted agent
_DEFAULT_SAMPLE_PDF = str(
    Path(__file__).resolve().parents[3] / "hosted-agent" / "sample_data" / "kostenvoranschlag.pdf"
)


def _parse_text_to_email(text: str, sample_pdf: str) -> EmailInput:
    """Parse a text string (JSON or plain) into an EmailInput."""
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return EmailInput(
                sender=data.get("sender", "unknown@example.com"),
                subject=data.get("subject", "Schadensmeldung"),
                body=data.get("body", text),
                pdf_path=data.get("pdf_path") or sample_pdf,
            )
    except (json.JSONDecodeError, TypeError):
        pass

    return EmailInput(
        sender="unknown@example.com",
        subject="Schadensmeldung (via Agent Service)",
        body=text,
        pdf_path=sample_pdf,
    )


class EmailIntakeExecutor(Executor):
    """Stores the incoming email in workflow state and passes it downstream.

    Handles multiple input types:
    - EmailInput: direct invocation (local / playground)
    - list[Message]: from the hosted agent adapter (via workflow.as_agent())
    - str: plain text fallback
    - Message: single message
    """

    def __init__(self, sample_pdf: str = _DEFAULT_SAMPLE_PDF):
        super().__init__(id="email_intake")
        self._sample_pdf = sample_pdf

    @handler
    async def handle_email(self, email: EmailInput, ctx: WorkflowContext[EmailInput]) -> None:
        """Direct EmailInput — used when running locally or from playground."""
        ctx.set_state("original_email", email)
        await ctx.send_message(email)

    @handler
    async def handle_messages(self, messages: list[Message], ctx: WorkflowContext[EmailInput]) -> None:
        """list[Message] — sent by the hosted agent adapter."""
        logger.info("handle_messages called with %d messages", len(messages))
        last_message = messages[-1] if messages else None
        if not last_message:
            logger.warning("Empty message list received")
            await ctx.yield_output("Error: No messages found in input.")
            return
        await self.handle_message(last_message, ctx)

    @handler
    async def handle_str(self, text: str, ctx: WorkflowContext[EmailInput]) -> None:
        """Plain string — treat as email body or JSON payload."""
        logger.info("handle_str called with %d chars", len(text))
        email = _parse_text_to_email(text, self._sample_pdf)
        ctx.set_state("original_email", email)
        await ctx.send_message(email)

    @handler
    async def handle_message(self, msg: Message, ctx: WorkflowContext[EmailInput]) -> None:
        """Single Message — extract text and parse."""
        logger.info("handle_message called: role=%s", msg.role)
        user_text = ""
        if msg.contents:
            for content in msg.contents:
                if content.type == "text" and content.text:
                    user_text = content.text
                    break

        if not user_text:
            logger.warning("No text content in message for EmailIntakeExecutor")
            await ctx.yield_output("Error: No text content found in message.")
            return

        email = _parse_text_to_email(user_text, self._sample_pdf)
        ctx.set_state("original_email", email)
        await ctx.send_message(email)
