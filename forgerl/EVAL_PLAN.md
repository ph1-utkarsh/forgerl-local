# Feasibility evaluation protocol v0

This preregistration covers harness qualification only. Research Gate 2 remains open until an external repository-disjoint benchmark and power analysis are defined.

## Fixture cohort

Six original Python repair fixtures: half-open ranges, stable uniqueness, chunk boundary, deep configuration merge, ledger debit, and CSV quoting. Each fixture has a buggy implementation, public tests, hidden tests, and oracle patch. All belong to `qualification`, not train/development/held-out research splits. Never use these scores as evidence for the charter hypothesis.

## Controls and metrics

- Buggy baseline must fail at least one hidden check; oracle must pass public and hidden checks.
- Qwen model: `qwen3:4b-instruct-2507-q4_K_M`, digest recorded from Ollama.
- Seeds: 0, 1, 2; temperature 0.2; context 4096; maximum 512 generated tokens/action and 8 actions/episode.
- Actions: list files, read a file, write a file, run public tests, finish. Paths constrained to an in-memory repository and materialized only by the evaluator.
- Protocol intervention sequence: EXP-FRL-001 generic JSON; 001B optional schema fields; 001C required action/path/content and fixed path. These are development interventions on the same qualification set, not held-out improvements.
- Candidate functions run in fresh, network-disabled Docker containers. The host compares outputs to trusted expected values; hidden test programs and expected values are not mounted. Worker mutation/alias metadata is diagnostic, not an adversarial guarantee.
- Record hidden success, public checks, tool validity, termination, calls, token counts, wall time, raw responses and tool outputs. Timeouts/transport errors are failures, never dropped.
- Primary smoke measure: successful episodes / attempted episodes. Report counts per fixture and seed; do not infer population generalization from six fixtures.
- Immutable run directory must include source hashes, image ID, model digest, environment, config, all episodes, and summary. No overwrites.

## Acceptance

All six buggy/oracle controls behave as expected, safety checks pass, local model completes a bounded episode, and reruns have the same cohort/config. This qualifies infrastructure, not research results.
