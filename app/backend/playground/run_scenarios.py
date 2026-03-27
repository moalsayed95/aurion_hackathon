"""Standalone script to run claim intake scenarios from the playground.

Usage (from app/backend):
    uv run python playground/run_scenarios.py        # all 5 scenarios
    uv run python playground/run_scenarios.py 1      # single scenario
"""

import asyncio
import sys

from playground.sample_data.emails import SCENARIOS
from aurion_claim_workflow.models import WorkflowOutput
from aurion_claim_workflow.workflow import build_workflow


async def run_scenario(scenario_name: str, email_input, workflow) -> None:
    print(f"\n{'='*70}")
    print(f"  Szenario: {scenario_name}")
    print(f"  Von: {email_input.sender}")
    print(f"  Betreff: {email_input.subject}")
    print(f"{'='*70}")

    final_output: WorkflowOutput | None = None

    async for event in workflow.run(email_input, stream=True):
        if event.type == "executor_invoked":
            print(f"\n  [{event.executor_id}] running...", flush=True)
        elif event.type == "executor_completed":
            print(f"  [{event.executor_id}] done.", flush=True)
        elif event.type == "output":
            if isinstance(event.data, WorkflowOutput):
                final_output = event.data

    print()

    if final_output:
        print(f"\n{'-'*70}")
        print(f"  ERGEBNIS")
        print(f"{'-'*70}")
        print(f"  Aktion:    {final_output.decision.action}")
        print(f"  Prioritaet: {final_output.decision.priority}")
        print(f"  Kunde:     {final_output.extracted_data.customer_name}")
        print(f"  Betrag:    {final_output.extracted_data.claim_amount}")
        print(f"\n  --- Entwurf Antwort-E-Mail ---")
        print(f"{final_output.drafted_response}")
        print(f"{'-'*70}")


async def main(scenario_ids: list[str] | None = None) -> None:
    workflow = build_workflow()

    if scenario_ids is None:
        scenario_ids = list(SCENARIOS.keys())

    for sid in scenario_ids:
        if sid not in SCENARIOS:
            print(f"Unbekanntes Szenario: {sid}. Verfuegbar: {', '.join(SCENARIOS.keys())}")
            continue
        name, email_input = SCENARIOS[sid]
        await run_scenario(name, email_input, workflow)


if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else None
    asyncio.run(main(args))
