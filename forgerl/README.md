# ForgeRL

Research status: incomplete. The thesis is failure-driven post-training on unseen repositories. The current implementation qualifies local tool interactions and graders on six original function-repair fixtures. No weights have been trained and no held-out repository result is claimed.

## Run locally

From the portfolio root, with Docker running and the installed Ollama model available:

```sh
python3 -m unittest discover -s forgerl -p 'test*.py' -v
python3 forgerl/runner.py controls --run-id CONTROL-NEW
python3 forgerl/runner.py baseline --run-id BASELINE-NEW --format schema
python3 forgerl/analyze.py forgerl/experiments/BASELINE-NEW
```

Run IDs cannot be reused. The runner requires existing `python:3.12-slim` and pins its local image ID. It never pulls an image or calls a paid inference endpoint.

## Evidence and limitations

See `experiments/`, `FAILURE_ANALYSIS.md`, `EVAL_PLAN.md`, and `.state/CURRENT_STAGE.md`. Candidate code runs in a network-disabled, read-only, resource-limited Docker container. Expected outputs remain with the host grader. The fixture cohort is not representative of real repository engineering, and mutation/alias checks depend on untrusted worker metadata.

## Next research gate

Establish a viable local training backend, finish the landscape comparison, select a licensed repository-disjoint benchmark, and freeze a statistically meaningful evaluation before post-training.
