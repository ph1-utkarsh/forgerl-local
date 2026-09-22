# Failure Registry

- FRL-FAIL-001: exit-code-only grader accepted `os._exit(0)`; fixed with host semantic comparisons and regression tests.
- FRL-FAIL-002: generic JSON and optional-field schemas permitted malformed write actions; required-field schema removed invalid actions in the observed cohort.
- FRL-FAIL-003: 14/18 revised-run episodes terminated with incorrect patches despite public checks; one exhausted action budget. This is not evidence for or against post-training, which has not run.

Details: `../FAILURE_ANALYSIS.md`. Original runs retained.

- FRL-FAIL-004: native MLX GGUF backend failed 0/3 inference sanity checks (EXP-FRL-004). Sampled decoder disagreements isolate Q4_K. EXP-FRL-003 is adapter mechanics evidence only. Replacement decoder must qualify before further training.
- FRL-FAIL-005: free checkpoint download stalled/dropped; processes stopped, partial data retained. Existing local GGUF is the alternative under qualification.
- FRL-FAIL-006: initial real-repository probe used a Python 3.11 tar API on host Python 3.9 (EXP-FRL-007). Compatibility fix moved to a new run.
- FRL-FAIL-007: evaluating each commit with its own historical tests failed to expose the youtube-dl bug (EXP-FRL-007B). Freezing the fixed regression test discriminated buggy/fixed correctly (EXP-FRL-007C).
- FRL-FAIL-008: local Qwen invented a nonexistent helper before reading in all three real-repository episodes (EXP-FRL-008). A required-read schema fixed observation access; subsequent cohort still scored 0/3 because patches mishandled missing keys and recovery degraded source syntax (EXP-FRL-008B).
- FRL-FAIL-009: development-only failure-derived LoRA fit its sequence loss but scored 0/3 exact repairs, identical to base (EXP-FRL-012). Its training-task boolean expression remained semantically wrong and it did not transfer. This falsifies a learnable-signal claim for this single-example setup, not the broader curriculum hypothesis.
