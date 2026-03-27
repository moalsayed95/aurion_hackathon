"""Aurion Hosted Agent — simplified single-node claim classification

Modes:
  • Hosted Agent mode:  python main.py           (default, Foundry Agent Server protocol)
  • DevUI mode:         python main.py devui      (local development with Agent Framework DevUI)
"""

import os
import sys

from workflow import create_workflow


# ---------------------------------------------------------------------------
# Hosted Agent mode  (python main.py)
# ---------------------------------------------------------------------------

def run_hosted_agent() -> None:
    """Start the workflow as a Foundry hosted agent.

    Uses ``from_agent_framework`` to wrap the workflow so it is served via
    the Azure Agent Server protocol (POST /runs, /responses).
    """
    from azure.ai.agentserver.agentframework import from_agent_framework

    server = from_agent_framework(lambda: create_workflow())

    port = int(os.environ.get("PORT", os.environ.get("DEFAULT_AD_PORT", "8088")))
    print(f"[hosted-agent] Starting Aurion claim classification agent on port {port}")
    server.run(port=port)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mode = os.environ.get("MODE") or (sys.argv[1] if len(sys.argv) > 1 else "agent")
    mode = mode.lower()

    if mode == "devui":
        from agent_framework_devui import serve
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("[devui] Starting Aurion claim classification agent in DevUI mode")
        workflow = create_workflow()
        serve([workflow], ui_enabled=True, instrumentation_enabled=True)
    else:
        run_hosted_agent()
