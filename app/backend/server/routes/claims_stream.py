import json
import shutil
import tempfile
import time
from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from server.deps import get_workflow
from aurion_claim_workflow.models import (
    ClassifiedEmail,
    DecidedEmail,
    EmailInput,
    ExtractedEmail,
    WorkflowOutput,
)

router = APIRouter(tags=["claims-stream"])


def _sse(event_type: str, data: dict) -> str:
    payload = json.dumps({"type": event_type, **data}, ensure_ascii=False)
    return f"data: {payload}\n\n"


def _preview(obj: object, max_len: int = 120) -> str:
    s = str(obj)
    return s[:max_len] + "..." if len(s) > max_len else s


async def _stream_workflow(email_input: EmailInput) -> AsyncGenerator[str, None]:
    workflow = get_workflow()

    yield _sse("workflow_started", {"timestamp": time.time()})

    try:
        async for event in workflow.run(email_input, stream=True):
            if event.type == "executor_invoked":
                yield _sse("executor_invoked", {
                    "executor_id": event.executor_id,
                    "timestamp": time.time(),
                })

            elif event.type == "executor_completed":
                payload: dict = {
                    "executor_id": event.executor_id,
                    "timestamp": time.time(),
                }

                # Inspect data to emit enriched events for specific stages
                data = event.data
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, ClassifiedEmail):
                            c = item.classification
                            yield _sse("classification_result", {
                                "document_type": c.document_type,
                                "urgency": c.urgency,
                                "confidence": c.confidence,
                                "reasoning": c.reasoning,
                            })
                        elif isinstance(item, ExtractedEmail):
                            e = item.extracted_data
                            yield _sse("extraction_result", {
                                "policy_number": e.policy_number,
                                "customer_name": e.customer_name,
                                "incident_date": e.incident_date,
                                "claim_amount": e.claim_amount,
                                "damage_type": e.damage_type,
                                "incident_description": e.incident_description,
                                "missing_fields": e.missing_fields,
                                "data_quality_score": e.data_quality_score,
                            })
                        elif isinstance(item, DecidedEmail):
                            d = item.decision
                            yield _sse("decision_result", {
                                "action": d.action,
                                "reasoning": d.reasoning,
                                "priority": d.priority,
                            })

                yield _sse("executor_completed", payload)

            elif event.type == "output":
                if isinstance(event.data, WorkflowOutput):
                    out: WorkflowOutput = event.data
                    yield _sse("workflow_output", {
                        "action": out.decision.action,
                        "priority": out.decision.priority,
                        "customer_name": out.extracted_data.customer_name,
                        "claim_amount": out.extracted_data.claim_amount,
                        "damage_type": out.extracted_data.damage_type,
                        "classification_type": out.classification.document_type,
                        "confidence": out.classification.confidence,
                        "drafted_response": out.drafted_response,
                    })

            elif event.type == "failed":
                details = event.details
                yield _sse("workflow_failed", {
                    "error_type": details.error_type if details else "Unknown",
                    "message": details.message if details else "Unknown error",
                    "executor_id": event.executor_id,
                })

    except Exception as exc:
        yield _sse("workflow_failed", {
            "error_type": type(exc).__name__,
            "message": str(exc),
            "executor_id": None,
        })

    yield _sse("workflow_done", {"timestamp": time.time()})


@router.post("/claims/process/stream")
async def process_claim_stream(
    sender: str = Form(""),
    subject: str = Form(""),
    body: str = Form(""),
    pdf_file: UploadFile | None = File(None),
):
    # Resolve PDF path: uploaded file → temp dir, else fallback sample
    tmp_path: Path | None = None
    if pdf_file and pdf_file.filename:
        tmp_dir = Path(tempfile.mkdtemp(prefix="aurion_"))
        tmp_path = tmp_dir / pdf_file.filename
        with tmp_path.open("wb") as f:
            shutil.copyfileobj(pdf_file.file, f)
        pdf_path = str(tmp_path)
    else:
        pdf_path = "playground/sample_data/kostenvoranschlag.pdf"

    email_input = EmailInput(
        sender=sender,
        subject=subject,
        body=body,
        pdf_path=pdf_path,
    )

    async def stream_and_cleanup():
        try:
            async for chunk in _stream_workflow(email_input):
                yield chunk
        finally:
            # Clean up temp file
            if tmp_path and tmp_path.exists():
                shutil.rmtree(tmp_path.parent, ignore_errors=True)

    return StreamingResponse(
        stream_and_cleanup(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
