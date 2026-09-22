# Qualification results — 2026-09-20

These are six authored function-repair fixtures, each attempted at seeds 0, 1, and 2 with local Qwen3 4B Instruct Q4_K_M. They are not a benchmark of unseen repositories and do not establish post-training gains.

| Run | Intervention | Successful episodes | Interpretation |
|---|---|---:|---|
| EXP-FRL-000 | Original buggy/oracle controls | 6/6 pairs | Historical; grader later found bypassable |
| EXP-FRL-000B | Host semantic grader controls | 6/6 pairs | All buggy implementations rejected; all oracle implementations accepted |
| EXP-FRL-001 | Generic JSON, original grader | 0/18 | Historical; protocol failure and flawed grader |
| EXP-FRL-001B | Loose schema, corrected grader | 0/18 | 66 invalid actions out of 125; schema allowed malformed paths |
| EXP-FRL-001C | Required fields and fixed path | 3/18 | 0 invalid actions out of 93; all three successes were interval repair |

EXP-FRL-001C used 29,213 reported prompt tokens and 2,753 output tokens. Sum of episode wall times: 91.36 seconds. Some earlier runs overlapped, so no latency speedup claim is valid. Reported prompt tokens include cached token accounting as supplied by Ollama.

14 revised-run episodes finished with an incorrect patch; one exhausted the action/protocol budget. Passing public tests did not imply hidden correctness. All paid inference/cloud spend: zero.

No confidence interval is presented as a generalization estimate: repeated seeds of six hand-authored problems do not provide an independent representative repository sample. Recompute descriptive statistics with `python3 forgerl/analyze.py forgerl/experiments/EXP-FRL-001C`.
