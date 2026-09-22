# Experiment Registry

| ID | Status | Result |
|---|---|---|
| EXP-FRL-000 | SUPERSEDED | 6/6 controls; grader bypass later discovered |
| EXP-FRL-000B | COMPLETE | 6/6 corrected host-grader control pairs |
| EXP-FRL-000C | COMPLETE | 6/6 after strict type comparison and cleanup fix |
| EXP-FRL-001 | HISTORICAL | 0/18 episodes; original grader/protocol |
| EXP-FRL-001B | COMPLETE | 0/18; loose schema, corrected grader |
| EXP-FRL-001C | COMPLETE | 3/18; strict schema, 93/93 valid actions |
| EXP-FRL-002 | PARTIAL | Metal scalar autodiff passes; trainable checkpoint metadata pinned; no LLM training |
| EXP-FRL-003 | MECHANICS ONLY | Adapter update/reload pass; backend later invalidated by EXP-FRL-004 |
| EXP-FRL-004 | FAILED | 0/3 inference sanity; independent decoder disagrees on sampled Q4_K tensors |
| EXP-FRL-005 | COMPLETE | Corrected Q4_K decoder matches Ollama on 3/3 short prompts; not full numerical parity |
| EXP-FRL-006 | COMPLETE | Corrected-backend five-step adapter mechanics pass; loss 7.109→2.212, frozen base unchanged, reload error zero |
| EXP-FRL-007 | FAILED | Host Python 3.9 rejected newer tar extraction API before test execution |
| EXP-FRL-007B | FAILED | Historical buggy test lacked regression assertions; both revisions passed |
| EXP-FRL-007C | COMPLETE | Pinned youtube-dl bug fails and upstream fix passes identical frozen test in Docker |
| EXP-FRL-008 | FAILED | 0/3; model invented edits before reading; all actions rejected |
| EXP-FRL-008B | COMPLETE NEGATIVE | 0/3 real-repository repairs; forced read worked, but fixes broke missing-key semantics and no episode finished |
| EXP-FRL-009 | FAILED | Tornado archive symlink rejected before execution |
| EXP-FRL-009B | COMPLETE | Tornado bug 5 buggy/fixed discrimination under pinned Python 3.8 image |
| EXP-FRL-010 | FAILED | PySnooper dependency image omitted declared runtime requirements |
| EXP-FRL-010B | COMPLETE | PySnooper bug 3 buggy/fixed discrimination under pinned dependency image |
| EXP-FRL-011 | COMPLETE | Failure-derived 20-step LoRA: loss 1.529→0.125, base unchanged, reload exact |
| EXP-FRL-012 | COMPLETE NEGATIVE | Strict exact-repair evaluation: base 0/3, adapter 0/3 across train/dev/test blocks |

Replay `replays/QUAL-REPLAY-001`: 18 saved patches, 3 successes, zero changed outcomes under latest grader, zero model calls.

Artifacts: `../experiments/<ID>/`. These are qualification runs only. No research-generalization experiment is complete. See `../BENCHMARKS.md` and `../FAILURE_ANALYSIS.md` for caveats.
