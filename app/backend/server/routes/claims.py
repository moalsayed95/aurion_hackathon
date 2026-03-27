from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.deps import get_workflow
from aurion_claim_workflow.models import EmailInput, WorkflowOutput

router = APIRouter(tags=["claims"])


class ClaimRequest(BaseModel):
    sender: str
    subject: str
    body: str
    pdf_path: str = "playground/sample_data/kostenvoranschlag.pdf"


class ClaimResponse(BaseModel):
    action: str
    priority: str
    customer_name: str | None
    claim_amount: float | None
    damage_type: str | None
    classification_type: str
    confidence: float
    drafted_response: str


@router.post("/claims/process", response_model=ClaimResponse)
async def process_claim(req: ClaimRequest):
    workflow = get_workflow()
    email_input = EmailInput(
        sender=req.sender,
        subject=req.subject,
        body=req.body,
        pdf_path=req.pdf_path,
    )

    final_output: WorkflowOutput | None = None
    async for event in workflow.run(email_input, stream=True):
        if event.type == "output" and isinstance(event.data, WorkflowOutput):
            final_output = event.data

    if final_output is None:
        raise HTTPException(status_code=500, detail="Workflow produced no output")

    return ClaimResponse(
        action=final_output.decision.action,
        priority=final_output.decision.priority,
        customer_name=final_output.extracted_data.customer_name,
        claim_amount=final_output.extracted_data.claim_amount,
        damage_type=final_output.extracted_data.damage_type,
        classification_type=final_output.classification.document_type,
        confidence=final_output.classification.confidence,
        drafted_response=final_output.drafted_response,
    )
