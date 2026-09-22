# Feasibility requirements

1. Only loopback Ollama inference; no external inference provider or paid service.
2. No model-generated Python execution on the host.
3. Containers use an existing pinned image, no network, read-only root, non-root UID, dropped capabilities, no-new-privileges, 256 MiB memory, one CPU, 64 PID limit, and a wall timeout.
4. Agent cannot see hidden graders or alter grader code; file operations reject traversal and oversized payloads.
5. Every attempted episode and transport failure is persisted. Outputs are bounded.
6. Baseline, oracle, and Qwen use the same task definitions and grader.
7. No broad software-engineering/generalization claims from authored fixtures.
8. Gate status must distinguish completed harness checks from missing research evidence.
