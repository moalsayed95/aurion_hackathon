// --- Request ---

export interface ClaimRequest {
  sender: string;
  subject: string;
  body: string;
  pdf_path?: string;
}

// --- SSE event payloads ---

export interface ClassificationResult {
  document_type: string;
  urgency: string;
  confidence: number;
  reasoning: string;
}

export interface ExtractionResult {
  policy_number: string | null;
  customer_name: string | null;
  incident_date: string | null;
  claim_amount: number | null;
  damage_type: string | null;
  incident_description: string | null;
  missing_fields: string[];
  data_quality_score: number;
}

export interface DecisionResult {
  action: "auto_process" | "escalate" | "request_more_info";
  reasoning: string;
  priority: string;
}

export interface WorkflowOutputPayload {
  action: string;
  priority: string;
  customer_name: string | null;
  claim_amount: number | null;
  damage_type: string | null;
  classification_type: string;
  confidence: number;
  drafted_response: string;
}

// --- Pipeline state ---

export type ExecutorStatus = "pending" | "active" | "completed" | "failed";

export interface ExecutorState {
  id: string;
  label: string;
  status: ExecutorStatus;
}

export type WorkflowStatus = "idle" | "running" | "completed" | "failed";

export interface WorkflowState {
  status: WorkflowStatus;
  activeExecutor: string | null;
  executors: Record<string, ExecutorState>;
  classification: ClassificationResult | null;
  extraction: ExtractionResult | null;
  decision: DecisionResult | null;
  draftedResponse: string;
  agentName: string;
  error: string | null;
}

// --- Reducer actions ---

export type WorkflowAction =
  | { type: "RESET" }
  | { type: "WORKFLOW_STARTED" }
  | { type: "EXECUTOR_INVOKED"; executor_id: string }
  | { type: "EXECUTOR_COMPLETED"; executor_id: string }
  | { type: "CLASSIFICATION_RECEIVED"; data: ClassificationResult }
  | { type: "EXTRACTION_RECEIVED"; data: ExtractionResult }
  | { type: "DECISION_RECEIVED"; data: DecisionResult }
  | { type: "AGENT_STREAMING"; agent_name: string; text_delta: string }
  | { type: "WORKFLOW_COMPLETED"; data: WorkflowOutputPayload }
  | { type: "WORKFLOW_FAILED"; error: string };

// --- Scenario presets ---

export interface ScenarioPreset {
  id: string;
  label: string;
  description: string;
  data: ClaimRequest;
}

// --- Live Mailbox ---

export type AppMode = "sample" | "live";

export interface MailboxEmail {
  id: string;
  subject: string;
  sender: string;
  sender_name: string;
  received: string;
  has_attachments: boolean;
  preview: string;
}

export interface MailboxStatus {
  configured: boolean;
  mailbox: string | null;
}
