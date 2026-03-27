import { useCallback, useEffect, useState } from "react";
import type { MailboxEmail, MailboxStatus } from "../types";

export function useMailbox() {
  const [emails, setEmails] = useState<MailboxEmail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<MailboxStatus>({
    configured: false,
    mailbox: null,
  });

  const checkStatus = useCallback(async () => {
    try {
      const resp = await fetch("http://localhost:8000/api/mailbox/status");
      if (resp.ok) {
        setStatus(await resp.json());
      }
    } catch {
      setStatus({ configured: false, mailbox: null });
    }
  }, []);

  // Check status on mount
  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  const fetchEmails = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch("http://localhost:8000/api/mailbox/emails");
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setEmails(data.emails);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch emails");
    } finally {
      setLoading(false);
    }
  }, []);

  return { emails, loading, error, status, checkStatus, fetchEmails };
}
