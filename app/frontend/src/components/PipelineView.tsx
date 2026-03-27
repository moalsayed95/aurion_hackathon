import { PIPELINE_STAGES } from "../hooks/useClaimWorkflow";
import type { ExecutorState, DecisionResult } from "../types";
import "./PipelineView.css";

interface Props {
  executors: Record<string, ExecutorState>;
  activeExecutor: string | null;
  decision: DecisionResult | null;
}

export function PipelineView({ executors, activeExecutor, decision }: Props) {
  const getStatus = (stageId: string) =>
    executors[stageId]?.status ?? "pending";

  return (
    <div className="pipeline">
      <div className="pipeline-row pipeline-main">
        {PIPELINE_STAGES.slice(0, 5).map((stage, i) => (
          <div key={stage.id} className="pipeline-node-wrapper">
            <div
              className={`pipeline-node ${getStatus(stage.id)} ${
                activeExecutor === stage.id ? "active" : ""
              }`}
            >
              <span className="pipeline-icon">{stageIcon(stage.id)}</span>
              <span className="pipeline-label">{stage.label}</span>
            </div>
            {i < 4 && <div className={`pipeline-arrow ${getStatus(PIPELINE_STAGES[i + 1].id) !== "pending" ? "done" : ""}`}>→</div>}
          </div>
        ))}
      </div>

      <div className="pipeline-branch">
        <div className="pipeline-branch-arrow">↓</div>
        <div className="pipeline-branches">
          {(["auto_process", "escalate", "request_more_info"] as const).map(
            (action) => {
              const chosen = decision?.action === action;
              const status = chosen
                ? executors["respond"]?.status ?? "pending"
                : "pending";
              return (
                <div
                  key={action}
                  className={`pipeline-node branch-node ${status} ${
                    chosen && activeExecutor === "respond" ? "active" : ""
                  } ${chosen ? "chosen" : ""}`}
                >
                  <span className="pipeline-icon">{branchIcon(action)}</span>
                  <span className="pipeline-label">{branchLabel(action)}</span>
                </div>
              );
            }
          )}
        </div>
      </div>
    </div>
  );
}

function stageIcon(id: string): string {
  switch (id) {
    case "email_intake":
      return "📧";
    case "doc_intelligence":
      return "📄";
    case "classify":
      return "🏷️";
    case "extract":
      return "🔍";
    case "decide":
      return "⚖️";
    default:
      return "⚙️";
  }
}

function branchIcon(action: string): string {
  switch (action) {
    case "auto_process":
      return "✅";
    case "escalate":
      return "🚨";
    case "request_more_info":
      return "❓";
    default:
      return "📨";
  }
}

function branchLabel(action: string): string {
  switch (action) {
    case "auto_process":
      return "Auto-Process";
    case "escalate":
      return "Escalate";
    case "request_more_info":
      return "Request Info";
    default:
      return action;
  }
}
