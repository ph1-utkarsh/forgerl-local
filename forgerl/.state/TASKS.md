# Tasks

| ID | Status | Goal | Dependencies | Acceptance / verification | Rollback |
|---|---|---|---|---|---|
| FRL-000 | DONE | Bootstrap portfolio governance | None | Required program documents exist; `python3 ../scripts/validate_bootstrap.py` | Revert bootstrap commit |
| FRL-001 | DONE | Close ForgeRL Gate 0 resource constraints | FRL-000 | Zero paid spend, local Qwen, permissive defaults recorded | Restore prior charter/state |
| FRL-002 | IN_PROGRESS | Conduct primary-source landscape research | FRL-001 | Gate 1 rubric passes with citations and baseline matrix | Preserve versioned survey |
| FRL-003 | TODO | Pre-register requirements and evaluation | FRL-002 | Gate 2 rubric passes; splits and thresholds frozen | Version new plan; retain old |
| FRL-004 | IN_PROGRESS | Qualify local execution/training feasibility | FRL-001 | Docker controls, regressions, model trajectories, device/gradient evidence | Revert code; preserve runs |

Qualification infrastructure is implemented. No research training task is READY until the missing evaluation gates pass.
