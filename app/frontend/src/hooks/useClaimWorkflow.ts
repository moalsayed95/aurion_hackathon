import { useCallback, useReducer, useRef } from "react";
import type {
  ClaimRequest,
  ClassificationResult,
  DecisionResult,
  ExtractionResult,
  WorkflowAction,
  WorkflowState,
} from "../types";

// --- Executor → visible pipeline stage mapping ---
// Each backend executor maps directly to one visible stage.
const EXECUTOR_TO_STAGE: Record<string, string> = {
  email_intake: "email_intake",
  doc_intelligence: "doc_intelligence",
  classify: "classify",
  extract: "extract",
  decide: "decide",
  auto_response: "respond",
  escalate_response: "respond",
  missing_info_response: "respond",
};

// The 6 visible stages in pipeline order
export const PIPELINE_STAGES = [
  { id: "email_intake", label: "Email Intake" },
  { id: "doc_intelligence", label: "Document AI" },
  { id: "classify", label: "Classify" },
  { id: "extract", label: "Extract" },
  { id: "decide", label: "Decide" },
  { id: "respond", label: "Response" },
] as const;

function stageForExecutor(executorId: string): string | null {
  return EXECUTOR_TO_STAGE[executorId] ?? null;
}

const initialState: WorkflowState = {
  status: "idle",
  activeExecutor: null,
  executors: {},
  classification: null,
  extraction: null,
  decision: null,
  draftedResponse: "",
  agentName: "",
  error: null,
};

function reducer(state: WorkflowState, action: WorkflowAction): WorkflowState {
  switch (action.type) {
    case "RESET":
      return { ...initialState };

    case "WORKFLOW_STARTED":
      return { ...initialState, status: "running" };

    case "EXECUTOR_INVOKED": {
      const stage = stageForExecutor(action.executor_id);
      if (!stage) return state;
      const executors = { ...state.executors };
      if (!executors[stage] || executors[stage].status !== "completed") {
        executors[stage] = {
          id: stage,
          label: PIPELINE_STAGES.find((s) => s.id === stage)?.label ?? stage,
          status: "active",
        };
      }
      return { ...state, executors, activeExecutor: stage };
    }

    case "EXECUTOR_COMPLETED": {
      const stage = stageForExecutor(action.executor_id);
      if (!stage) return state;
      const executors = { ...state.executors };
      executors[stage] = { ...executors[stage], status: "completed" };
      return { ...state, executors };
    }

    case "CLASSIFICATION_RECEIVED":
      return { ...state, classification: action.data };

    case "EXTRACTION_RECEIVED":
      return { ...state, extraction: action.data };

    case "DECISION_RECEIVED":
      return { ...state, decision: action.data };

    case "AGENT_STREAMING":
      return {
        ...state,
        draftedResponse: state.draftedResponse + action.text_delta,
        agentName: action.agent_name,
      };

    case "WORKFLOW_COMPLETED":
      return {
        ...state,
        status: "completed",
        activeExecutor: null,
        draftedResponse:
          state.draftedResponse || action.data.drafted_response,
      };

    case "WORKFLOW_FAILED":
      return { ...state, status: "failed", error: action.error };

    default:
      return state;
  }
}

export function useClaimWorkflow() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const abortRef = useRef<AbortController | null>(null);

  const submitClaim = useCallback(async (request: ClaimRequest, file?: File) => {
    // Cancel any in-flight request
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    dispatch({ type: "RESET" });
    dispatch({ type: "WORKFLOW_STARTED" });

    try {
      const formData = new FormData();
      formData.append("sender", request.sender);
      formData.append("subject", request.subject);
      formData.append("body", request.body);
      if (request.pdf_path) {
        formData.append("pdf_path", request.pdf_path);
      }
      if (file) {
        formData.append("pdf_file", file);
      }

      const resp = await fetch("http://localhost:8000/api/claims/process/stream", {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      if (!resp.ok || !resp.body) {
        dispatch({ type: "WORKFLOW_FAILED", error: `HTTP ${resp.status}` });
        return;
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const json = line.slice(6);
          if (!json) continue;

          try {
            const evt = JSON.parse(json);
            switch (evt.type) {
              case "executor_invoked":
                dispatch({ type: "EXECUTOR_INVOKED", executor_id: evt.executor_id });
                break;
              case "executor_completed":
                dispatch({ type: "EXECUTOR_COMPLETED", executor_id: evt.executor_id });
                break;
              case "classification_result":
                dispatch({
                  type: "CLASSIFICATION_RECEIVED",
                  data: evt as ClassificationResult,
                });
                break;
              case "extraction_result":
                dispatch({
                  type: "EXTRACTION_RECEIVED",
                  data: evt as ExtractionResult,
                });
                break;
              case "decision_result":
                dispatch({
                  type: "DECISION_RECEIVED",
                  data: evt as DecisionResult,
                });
                break;
              case "agent_streaming":
                dispatch({
                  type: "AGENT_STREAMING",
                  agent_name: evt.agent_name,
                  text_delta: evt.text_delta,
                });
                break;
              case "workflow_output":
                dispatch({ type: "WORKFLOW_COMPLETED", data: evt });
                break;
              case "workflow_failed":
                dispatch({
                  type: "WORKFLOW_FAILED",
                  error: `${evt.error_type}: ${evt.message}`,
                });
                break;
            }
          } catch {
            // skip malformed lines
          }
        }
      }

      // If stream ended without explicit completion
      if (state.status === "running") {
        dispatch({ type: "WORKFLOW_COMPLETED", data: {} as never });
      }
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      dispatch({
        type: "WORKFLOW_FAILED",
        error: err instanceof Error ? err.message : "Unknown error",
      });
    }
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    dispatch({ type: "RESET" });
  }, []);

  return { state, submitClaim, reset };
}
