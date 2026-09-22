# Project State

- Objective: test whether failure-driven post-training improves small coding agents on repository-disjoint tasks under matched compute.
- Current stage: Stage 1, `IN_PROGRESS` (2026-09-20).
- Architecture: intentionally undefined until baseline and spikes justify it.
- Verified environment: M1 Pro, 16 GB unified memory, no CUDA GPU.
- Key decision: use installed Qwen3 4B Instruct Q4_K_M through Ollama; zero paid calls.
- Constraints: local only, original/permissive artifacts, asynchronous engineering. Only feasibility adapter updates have run; no research training claim.
- Implemented qualification substrate: five JSON actions, Docker execution, host semantic checks, bounded trajectories, immutable runs.
- Evidence: 6/6 corrected buggy/oracle controls and 10 regression tests pass. Strict-schema Qwen completes 3/18 qualification episodes with 93/93 valid actions; replay preserves outcomes.
- Failure: original exit-code grader accepted premature process exit; fixed by host semantic comparison. Original runs retained and flagged.
- EXP-FRL-003 updated 40,960 adapter parameters with unchanged base hashes and exact reload logits. However, EXP-FRL-004 then failed 0/3 inference sanity checks: this pilot is mechanics evidence only, not valid model training.
- Independent gguf 0.19.0 agrees with sampled F32/Q6_K tensors but disagrees with all sampled Q4_K tensors decoded by MLX 0.32.2. Replacement decoder matches Ollama on 3/3 short prompts (EXP-FRL-005). Corrected five-step adapter pilot passes with unchanged base hashes and exact reload (EXP-FRL-006); peak allocation 10.754 GB. Not full parity or capability evidence.
- First real BugsInPy task is qualified: pinned youtube-dl buggy source fails and upstream fix passes the identical frozen regression test in the Docker sandbox (EXP-FRL-007C). Local Qwen baseline is 0/3 after a forced initial read (EXP-FRL-008B); failure traces show missing-key semantic errors and destructive recovery.
- Three repository-disjoint pilot tasks now discriminate buggy/fixed revisions: youtube-dl, Tornado, and PySnooper. `RESEARCH/pilot_manifest.json` freezes train/development/test identities. One task per split is explicitly underpowered and cannot test the charter's five-point hypothesis.
- Failure-derived SFT LoRA mechanics pass (EXP-FRL-011), but strict base-versus-adapter evaluation is 0/3 versus 0/3 (EXP-FRL-012). Training loss is not capability.
- Local DPO and two-candidate clipped GRPO-surrogate runs (EXP-FRL-013/014) improve the single observed preference margin with frozen base weights and exact adapter reload. Frozen evaluation (EXP-FRL-015/016) is base 0/3, DPO 0/3, and GRPO 0/3; DPO also emits one malformed long response. The original five-point/multi-seed hypothesis remains underpowered and unsupported.
- Unresolved: repository-disjoint benchmark, statistical power, research training and original thesis evidence. Helix Metal/CUDA scope decision awaits user. None of the three projects is complete.
