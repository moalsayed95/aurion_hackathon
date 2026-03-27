import { useState } from "react";
import type { MailboxEmail, WorkflowStatus } from "../types";
import "./MailboxView.css";

interface Props {
  emails: MailboxEmail[];
  loading: boolean;
  error: string | null;
  mailbox: string | null;
  onRefresh: () => void;
  onProcess: (messageId: string) => void;
  workflowStatus: WorkflowStatus;
}

export function MailboxView({
  emails,
  loading,
  error,
  mailbox,
  onRefresh,
  onProcess,
  workflowStatus,
}: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const isRunning = workflowStatus === "running";

  return (
    <div className="mailbox-view">
      <h2>📬 Live Mailbox</h2>
      {mailbox && <div className="mailbox-address">{mailbox}</div>}

      <button
        className="refresh-btn"
        onClick={onRefresh}
        disabled={loading || isRunning}
      >
        {loading ? "Loading…" : "↻ Refresh Inbox"}
      </button>

      {error && <div className="mailbox-error">{error}</div>}

      {!loading && emails.length === 0 && (
        <div className="mailbox-empty">No unread emails</div>
      )}

      <div className="mailbox-list">
        {emails.map((email) => (
          <div
            key={email.id}
            className={`mailbox-item${selectedId === email.id ? " selected" : ""}`}
            onClick={() => setSelectedId(email.id)}
          >
            <div className="mailbox-item-top">
              <span className="mailbox-item-sender">
                {email.sender_name || email.sender}
              </span>
              {email.has_attachments && (
                <span className="mailbox-attachment-badge" title="Has PDF attachment">📎</span>
              )}
            </div>
            <div className="mailbox-item-subject">{email.subject}</div>
            <div className="mailbox-item-preview">{email.preview}</div>
            <div className="mailbox-item-date">
              {new Date(email.received).toLocaleString()}
            </div>
          </div>
        ))}
      </div>

      {selectedId && (
        <button
          className="process-live-btn"
          onClick={() => onProcess(selectedId)}
          disabled={isRunning}
        >
          {isRunning ? "Processing…" : "▶ Process Selected Email"}
        </button>
      )}
    </div>
  );
}
