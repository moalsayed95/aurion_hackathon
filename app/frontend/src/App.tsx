import { useState } from "react";
import "./App.css";
import { useClaimWorkflow } from "./hooks/useClaimWorkflow";
import { useMailbox } from "./hooks/useMailbox";
import { ClaimForm } from "./components/ClaimForm";
import { MailboxView } from "./components/MailboxView";
import { PipelineView } from "./components/PipelineView";
import { StepDetails } from "./components/StepDetails";
import { ResponseDraft } from "./components/ResponseDraft";
import type { AppMode } from "./types";

function App() {
  const { state, submitClaim, processLiveEmail, reset } = useClaimWorkflow();
  const mailbox = useMailbox();
  const [mode, setMode] = useState<AppMode>("sample");

  const handleToggle = (next: AppMode) => {
    setMode(next);
    if (next === "live" && mailbox.emails.length === 0) {
      mailbox.fetchEmails();
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-brand">
          <span className="header-logo">🛡️</span>
          <h1>Aurion Claim Intake</h1>
          <span className="header-sub">AI Workflow Dashboard</span>
        </div>

        {/* Mode toggle — only show if Graph is configured */}
        {mailbox.status.configured && (
          <div className="mode-toggle">
            <button
              className={`toggle-btn${mode === "sample" ? " active" : ""}`}
              onClick={() => handleToggle("sample")}
            >
              Sample
            </button>
            <button
              className={`toggle-btn${mode === "live" ? " active" : ""}`}
              onClick={() => handleToggle("live")}
            >
              Live
            </button>
          </div>
        )}

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
          {mode === "sample" ? (
            <ClaimForm
              onSubmit={submitClaim}
              workflowStatus={state.status}
              onReset={reset}
            />
          ) : (
            <MailboxView
              emails={mailbox.emails}
              loading={mailbox.loading}
              error={mailbox.error}
              mailbox={mailbox.status.mailbox}
              onRefresh={mailbox.fetchEmails}
              onProcess={processLiveEmail}
              workflowStatus={state.status}
            />
          )}
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
