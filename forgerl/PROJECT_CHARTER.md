# ForgeRL Project Charter

## Problem and motivation

Small open-weight coding models often fail long-horizon repository tasks through poor diagnosis, invalid tool use, weak recovery, or premature termination. Aggregate success metrics do not reveal whether training on these failures creates transferable capability rather than benchmark memorization. A reproducible, sandboxed testbed can turn those failures into controlled training and evaluation evidence.

## Research question and hypothesis

**Question:** Can failure-driven post-training make a 1B–7B open-weight model substantially better on unseen repositories and failure classes than compute-matched random task sampling?

**Primary hypothesis:** Given the same model, training-token budget, optimizer family, and task-source pool, a curriculum targeted from clustered failures will improve repository-disjoint task success by at least **5 absolute percentage points** over random sampling, with a 95% bootstrap confidence interval excluding zero across at least three seeds.

**Falsifiers:** no practically significant held-out gain; gains disappear on repository-disjoint tests; reward increases without hidden-test success; or gains are explained by extra tokens/inference compute.

## Target users

Post-training researchers, coding-agent researchers, evaluation engineers, and engineers building safe repository-task sandboxes.

## Success criteria

- Deterministic reset/sandbox and executable grading for a frozen, repository-disjoint evaluation set.
- Base, SFT, and selected RL/preference method evaluated using identical scaffolding and inference budgets.
- Primary hypothesis tested with ≥3 seeds or a documented power/cost exception.
- Report success rate, tests passed, valid tool calls, recovery, correct termination, steps, tokens, latency, and compute/cost.
- Ablate curriculum targeting, failed/corrected trajectories, reward components, and inference-time compute.
- Preserve all runs, failure clusters, negative results, configs, versions, and raw metrics.

## Non-goals

- Training a foundation model from scratch.
- Claiming general software-engineering ability from a single benchmark.
- Production autonomous code deployment or execution outside the sandbox.
- Building a general distributed RL platform before single-GPU signal exists.
- Optimizing leaderboard position through test contamination.

## Constraints

- Local M1 Pro/16 GB supports development and small inference, not credible 1B–7B multi-seed RL.
- Paid/cloud/API budget is exactly zero per user instruction on 2026-09-20. Use local compute and installed Qwen in Ollama.
- Initial baseline is installed Qwen3 4B Instruct Q4_K_M. A differentiable local training backend must be demonstrated before post-training runs.
- Only permissively usable models, code, and repository tasks; licenses must be recorded.
- Target duration is ten weeks alongside professional commitments.

## Risks

Reward hacking, grader leakage, repository contamination, sparse RL signal, unstable multi-seed training, unsafe code execution, synthetic-task artifacts, and compute-driven scope collapse. Controls are specified in the program risk register and will be made concrete in the evaluation plan.

## Kill or redesign criteria

- No reliable grader/sandbox can be built for a meaningful task subset.
- The minimum three-seed decision experiment exceeds the approved budget after model/task downsizing.
- Failure-targeted tasks cannot be separated from evaluation repositories or leak hidden tests.
- Two well-instrumented pilots show no learnable signal from SFT or verifiable reward.
- Landscape review finds the proposed contribution already demonstrated under equivalent controls; narrow or change the thesis before implementation.

## Stage Gate 0 status

`PASS` as of 2026-09-20 for the resource envelope: local only, zero paid spend, original/permissive artifacts, asynchronous engineering without a required weekly human commitment. This does not establish that the full research target is feasible. See `../LOCAL_EXECUTION.md`. Stage 1 remains in progress; qualification spikes do not close research gates.
