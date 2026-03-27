# Playground

Standalone scripts to test the Aurion claim intake workflow agents directly.

## Run scenarios

```bash
# From app/backend/
uv run python playground/run_scenarios.py        # all 3 scenarios
uv run python playground/run_scenarios.py 1      # Maria Huber (auto-process)
uv run python playground/run_scenarios.py 2      # Thomas Wagner (escalate)
uv run python playground/run_scenarios.py 3      # Anna Berger (request info)
```

## Regenerate sample PDF

```bash
uv run python -m playground.sample_data.generate_sample_pdf
```
