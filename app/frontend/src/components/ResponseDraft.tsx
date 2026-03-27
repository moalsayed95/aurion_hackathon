import { useEffect, useRef } from "react";
import type { WorkflowStatus } from "../types";
import "./ResponseDraft.css";

interface Props {
  draftedResponse: string;
  agentName: string;
  workflowStatus: WorkflowStatus;
}

export function ResponseDraft({
  draftedResponse,
  agentName,
  workflowStatus,
}: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [draftedResponse]);

  if (!draftedResponse && workflowStatus !== "running") {
    return null;
  }

  const isStreaming = workflowStatus === "running" && draftedResponse.length > 0;

  return (
    <div className="response-draft">
      <div className="response-header">
        <h3>📨 Drafted Response</h3>
        {agentName && (
          <span className="agent-badge">
            {isStreaming && <span className="typing-indicator" />}
            {agentName}
          </span>
        )}
      </div>
      <div className="response-body">
        <pre className="response-text">
          {draftedResponse}
          {isStreaming && <span className="cursor">|</span>}
        </pre>
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
