# Experiments

## EXP-FRL-000: qualification controls

Question: can the runner reject buggy patches and accept correct patches without exposing the host or grader?

Independent variable: buggy vs oracle source. Controls: task, tests, image, resource limits. Run all six fixtures. Acceptance: all oracle suites pass, every buggy hidden suite fails. Preserve stdout, return codes, source hash and image ID.

## EXP-FRL-001: local Qwen feasibility

Question: can the installed quantized model perform valid bounded repair interactions?

Run six qualification tasks with three seeds. Record all actions and final hidden outcome, including failures. This measures protocol feasibility and local cost/latency only. It cannot test failure-driven post-training.

## EXP-FRL-002: training feasibility (not yet run)

Inventory local trainable checkpoints and supported backends. Determine whether existing quantized model can support a differentiable adapter training path without paid services. A valid weight update and before/after checkpoint comparison is required. A prompt or memory modification does not count as post-training. If infeasible, record exact blocker and available free alternatives before changing thesis.
