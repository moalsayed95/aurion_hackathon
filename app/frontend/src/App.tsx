import "./App.css";
import { useClaimWorkflow } from "./hooks/useClaimWorkflow";
import { ClaimForm } from "./components/ClaimForm";
import { PipelineView } from "./components/PipelineView";
import { StepDetails } from "./components/StepDetails";
import { ResponseDraft } from "./components/ResponseDraft";

function App() {
  const { state, submitClaim, reset } = useClaimWorkflow();

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-brand">
          <span className="header-logo">🛡️</span>
          <h1>Aurion Claim Intake</h1>
          <span className="header-sub">AI Workflow Dashboard</span>
        </div>
        {state.status !== "idle" && (
          <span className={`status-pill status-${state.status}`}>
            {state.status === "running"
              ? "Processing..."
              : state.status === "completed"
                ? "Completed"
                : state.status === "failed"
                  ? "Failed"
                  : ""}
          </span>
        )}
      </header>

      <main className="app-main">
        <aside className="left-panel">
          <ClaimForm
            onSubmit={submitClaim}
            workflowStatus={state.status}
            onReset={reset}
          />
        </aside>

        <section className="right-panel">
          <PipelineView
            executors={state.executors}
            activeExecutor={state.activeExecutor}
            decision={state.decision}
          />

          <StepDetails
            classification={state.classification}
            extraction={state.extraction}
            decision={state.decision}
          />

          <ResponseDraft
            draftedResponse={state.draftedResponse}
            agentName={state.agentName}
            workflowStatus={state.status}
          />

          {state.error && (
            <div className="error-panel">
              <strong>Error:</strong> {state.error}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
