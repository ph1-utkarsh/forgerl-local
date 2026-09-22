# Reproducibility status

The qualification runner and tests use Python's standard library, Docker, and an existing Ollama model. MLX is a separate feasibility dependency; it is not required for baseline inference.

Each new run records the Docker image ID, Ollama model metadata/digest, Ollama version, Python/platform, seeds, generation limits, source hashes, and source snapshots. Raw API responses retain timing/token counts. Research software locks and clean-machine reproduction remain incomplete.

The first historical EXP-FRL-000/001 runs predate source snapshots and use a flawed exit-code grader. Their hashes and trajectories are retained, but they are not a reproducible research baseline and must not be used as valid reward evidence.

Run the commands in README with a fresh run ID. Because model inference is stochastic and depends on Ollama/hardware versions, identical seeds do not promise bitwise-identical outputs. Compare full cohorts, not selected episodes. Some initial runs overlapped and their latency is not a controlled performance comparison.
