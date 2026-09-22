# ForgeRL

[![tests](https://github.com/ph1-utkarsh/forgerl-local/actions/workflows/tests.yml/badge.svg)](https://github.com/ph1-utkarsh/forgerl-local/actions/workflows/tests.yml) [![license: MIT](https://img.shields.io/badge/license-MIT-c9ff3d.svg)](LICENSE)

**Failure-driven post-training for repository repair, built and measured locally.**

ForgeRL is an evidence-first coding-agent research system. It combines constrained JSON actions, network-disabled Docker execution, host-held semantic graders, replayable trajectories, a corrected GGUF-to-MLX loader, and real LoRA updates using SFT, DPO, and a verifier-reward GRPO surrogate.

The most important result is negative and reproducible: all trained adapters improved their local training objectives, but none solved the frozen three-repository exact-repair benchmark.

| Condition | Exact repairs |
|---|---:|
| Frozen Qwen base | 0 / 3 |
| Failure-derived SFT | 0 / 3 |
| DPO | 0 / 3 |
| GRPO surrogate | 0 / 3 |

DPO increased the observed chosen-vs-rejected margin from **0.382 to 4.684**. The GRPO surrogate increased it to **1.220**. Both changed only **40,960 LoRA parameters**, preserved the frozen base, and reproduced their margin after reload. That optimizer success did not transfer into exact repository repair—precisely the distinction this project is designed to expose.

## What is implemented

- Five bounded coding-agent actions with strict schemas
- Read-only, network-disabled and resource-limited Docker grading
- Host-held expected outputs and semantic graders
- Immutable trajectories, replay and failure classification
- Three pinned BugsInPy repositories: youtube-dl, Tornado and PySnooper
- Corrected Q4_K GGUF decoding validated against local Ollama outputs
- Local MLX LoRA training for SFT, DPO and a clipped two-candidate GRPO surrogate
- Base-vs-adapter evaluation with repository-disjoint train/development/test blocks
- Preserved invalid and negative experiments instead of overwritten results

## Architecture

```text
local Qwen model
      │ strict JSON action
      ▼
bounded agent loop ──► host validator ──► isolated Docker worker
      │                                      │
      └──────── immutable trajectory ◄──── semantic grader
                         │
                         ▼
               SFT / DPO / GRPO LoRA
                         │
                         ▼
               frozen exact-repair eval
```

## Reproduce

Requirements: macOS Apple Silicon for the recorded MLX training runs, Python 3.12, Docker, and a locally available Qwen3 4B Instruct Q4_K_M checkpoint. No paid API is used.

```bash
python3 -m unittest discover -s forgerl -p 'test*.py' -v
python3 scripts/verify.py
```

Run a fresh bounded qualification cohort after starting Ollama and preloading `python:3.12-slim`:

```bash
python3 forgerl/runner.py controls --run-id CONTROL-LOCAL
python3 forgerl/runner.py baseline --run-id BASELINE-LOCAL --format schema
python3 forgerl/analyze.py forgerl/experiments/BASELINE-LOCAL
```

Training entry points are `forgerl/adapter_pilot.py` and `forgerl/alignment_pilot.py`. Run IDs are immutable and cannot be reused.

## Evidence map

- `EXP-FRL-011`: failure-derived SFT LoRA mechanics
- `EXP-FRL-012`: frozen base vs SFT evaluation
- `EXP-FRL-013`: DPO update and reload evidence
- `EXP-FRL-014`: GRPO-surrogate update and reload evidence
- `EXP-FRL-015/016`: DPO and GRPO exact-repair evaluations
- `forgerl/FINAL_REPORT.md`: scoped conclusion and limitations
- `forgerl/FAILURE_ANALYSIS.md`: preserved failure taxonomy

Large model files and generated adapter weights are intentionally excluded from Git. `scripts/verify.py` validates the publishable evidence without those binaries; `scripts/verify_runs.py` performs the stricter audit when locally generated adapters are present. Metrics, configurations, source snapshots, responses, hashes and failure notes remain versioned.

## Scope

This is a bounded feasibility study, not evidence that failure-driven post-training succeeds or fails at scale. One task per repository split is underpowered. The defensible finding is narrower: real local preference optimization can succeed mechanically while producing no exact repair improvement.

## License

Original ForgeRL code is MIT licensed. Third-party repository snapshots and patches retain the licenses stored beside their experiment artifacts.
