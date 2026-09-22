# Failure analysis

## FRL-FAIL-001 — Exit-code-only grader can be bypassed

Found during qualification on 2026-09-20. A candidate containing `os._exit(0)` caused the original in-process test runner to report a pass without executing assertions. Reproduction returned `passed: true` and empty output. Severity: invalid reward signal, blocks training.

Intervention: candidate executes in a separate Docker worker that receives function inputs only. Trusted host compares returned JSON values to expected values. Hidden tests and expected outputs are never mounted. Empty/invalid/incorrect-length responses fail even when exit code is zero. Regression test covers early exit and fake boolean pass output. Input mutation/alias metadata remains self-reported by the worker and is not adversarially trustworthy; semantic output comparisons are independently checked.

EXP-FRL-000 and EXP-FRL-001 used the original grader and are retained as historical evidence. Rerun controls and model cohort with the corrected grader before citing scores.

## FRL-FAIL-002 — Weak schema allowed invalid write actions

EXP-FRL-001B produced 66 invalid actions out of 125 and no successful episodes. The model placed JSON-like text into a path string. Requiring all fields and fixing the path enum yielded zero invalid actions in 93 observed actions (EXP-FRL-001C). This is a scaffold change, not model post-training.

## FRL-FAIL-003 — Passing public examples led to incomplete repair

The revised cohort had 14 incorrect finished patches and one unfinished episode. All three successes were interval repair. Example: chunk repair added nonpositive-size validation but retained the old range endpoint, still dropping partial chunks. Public examples did not exercise this requirement. Follow-up: build evaluation tasks with richer public feedback and measure recovery separately from hidden outcome; do not reveal hidden tests during tuning.

## FRL-FAIL-004 — Cleanup timeout under output flooding

A rerun exposed a timeout in `docker rm -f` while the candidate flooded stdout. The Docker client pipe was still attached and unread during cleanup. Close/kill the attached client before container removal; bounded cleanup timeout is now recorded as a failure. The existing output-flood regression then passed in the full 10-test run.

## Limits

The six authored fixtures are small function repairs, not multi-file real repositories. No empirical research claim about long-horizon coding, post-training, or generalization follows from passing them.
