import type {
  ClassificationResult,
  DecisionResult,
  ExtractionResult,
} from "../types";
import "./StepDetails.css";

interface Props {
  classification: ClassificationResult | null;
  extraction: ExtractionResult | null;
  decision: DecisionResult | null;
}

export function StepDetails({ classification, extraction, decision }: Props) {
  const hasAny = classification || extraction || decision;

  if (!hasAny) {
    return (
      <div className="step-details empty">
        <p className="step-details-placeholder">
          Step details will appear here as the pipeline executes...
        </p>
      </div>
    );
  }

  return (
    <div className="step-details">
      {classification && (
        <div className="step-card">
          <h3>🏷️ Classification</h3>
          <div className="step-fields">
            <Field label="Type" value={formatType(classification.document_type)} />
            <Field
              label="Urgency"
              value={
                <span className={`badge urgency-${classification.urgency}`}>
                  {classification.urgency}
                </span>
              }
            />
            <Field
              label="Confidence"
              value={<ConfidenceBar value={classification.confidence} />}
            />
            <Field label="Reasoning" value={classification.reasoning} span />
          </div>
        </div>
      )}

      {extraction && (
        <div className="step-card">
          <h3>🔍 Extraction</h3>
          <div className="step-fields">
            <Field label="Customer" value={extraction.customer_name ?? "—"} />
            <Field label="Policy #" value={extraction.policy_number ?? "—"} />
            <Field label="Incident Date" value={extraction.incident_date ?? "—"} />
            <Field
              label="Amount"
              value={
                extraction.claim_amount != null
                  ? `EUR ${extraction.claim_amount.toLocaleString("de-AT", { minimumFractionDigits: 2 })}`
                  : "—"
              }
            />
            <Field label="Damage Type" value={extraction.damage_type ?? "—"} />
            <Field
              label="Data Quality"
              value={<ConfidenceBar value={extraction.data_quality_score} />}
            />
            {extraction.missing_fields.length > 0 && (
              <Field
                label="Missing"
                value={
                  <span className="missing-fields">
                    {extraction.missing_fields.join(", ")}
                  </span>
                }
                span
              />
            )}
          </div>
        </div>
      )}

      {decision && (
        <div className="step-card">
          <h3>⚖️ Decision</h3>
          <div className="step-fields">
            <Field
              label="Action"
              value={
                <span className={`badge action-${decision.action}`}>
                  {formatAction(decision.action)}
                </span>
              }
            />
            <Field
              label="Priority"
              value={
                <span className={`badge urgency-${decision.priority}`}>
                  {decision.priority}
                </span>
              }
            />
            <Field label="Reasoning" value={decision.reasoning} span />
          </div>
        </div>
      )}
    </div>
  );
}

function Field({
  label,
  value,
  span,
}: {
  label: string;
  value: React.ReactNode;
  span?: boolean;
}) {
  return (
    <div className={`step-field ${span ? "span-full" : ""}`}>
      <span className="field-label">{label}</span>
      <span className="field-value">{value}</span>
    </div>
  );
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 80 ? "#16a34a" : pct >= 50 ? "#ca8a04" : "#dc2626";
  return (
    <span className="confidence-bar">
      <span className="confidence-track">
        <span
          className="confidence-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </span>
      <span className="confidence-pct">{pct}%</span>
    </span>
  );
}

function formatType(t: string): string {
  return t
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatAction(a: string): string {
  switch (a) {
    case "auto_process":
      return "Auto-Process";
    case "escalate":
      return "Escalate";
    case "request_more_info":
      return "Request Info";
    default:
      return a;
  }
}
