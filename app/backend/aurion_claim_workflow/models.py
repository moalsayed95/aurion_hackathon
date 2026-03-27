from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel


# --- Workflow entry point ---

@dataclass
class EmailInput:
    sender: str
    subject: str
    body: str
    pdf_path: str | None = None


# --- Doc Intelligence output ---

@dataclass
class ProcessedDocument:
    sender: str
    subject: str
    body: str
    pdf_text: str
    pdf_tables: list[str] = field(default_factory=list)


# --- LLM structured outputs (Pydantic for response_format) ---

class ClassificationResult(BaseModel):
    document_type: Literal[
        "new_claim", "claim_status", "policy_inquiry", "invoice", "complaint", "general"
    ]
    urgency: Literal["low", "normal", "high", "critical"]
    confidence: float
    reasoning: str


class ExtractedClaimData(BaseModel):
    policy_number: str | None = None
    customer_name: str | None = None
    incident_date: str | None = None
    claim_amount: float | None = None
    damage_type: str | None = None
    incident_description: str | None = None
    missing_fields: list[str] = []
    data_quality_score: float = 0.0


class DecisionResult(BaseModel):
    action: Literal["auto_process", "escalate", "request_more_info"]
    reasoning: str
    priority: Literal["low", "normal", "high", "critical"]


# --- Bridge dataclasses (carry context between stages) ---

@dataclass
class ClassifiedEmail:
    sender: str
    subject: str
    body: str
    pdf_text: str
    classification: ClassificationResult


@dataclass
class ExtractedEmail:
    sender: str
    subject: str
    body: str
    pdf_text: str
    classification: ClassificationResult
    extracted_data: ExtractedClaimData


@dataclass
class DecidedEmail:
    sender: str
    subject: str
    body: str
    classification: ClassificationResult
    extracted_data: ExtractedClaimData
    decision: DecisionResult


# --- Final workflow output ---

@dataclass
class WorkflowOutput:
    decision: DecisionResult
    extracted_data: ExtractedClaimData
    classification: ClassificationResult
    drafted_response: str
