# Dataset acceptance before research training

The qualification cohort must never become the evidence for unseen-repository capability. Before approving a research dataset, create a pinned manifest and satisfy:

1. Source repository URL, immutable commit, license text/hash, task origin, mutation or issue identifier, and environment image digest exist for every task.
2. Original bug fails at least one protected outcome check; trusted repair passes it. Record broken environments separately from agent failures.
3. Public and hidden check definitions are separated, and agent-visible checkout excludes hidden data, solutions, and grading credentials.
4. Train/development/test repository identities are disjoint. Forks, vendored code, duplicated functions, generated variants, and issue/solution near-duplicates are grouped before splitting.
5. Compatibility selection uses fixed environment criteria, not observed model success. Keep the exclusion registry.
6. Baselines use identical model representations, prompt templates, action budgets, context limits, decoding settings, and test availability.
7. Development failures alone may drive targeted curriculum generation. Hidden evaluation failures cannot be recycled into training.
8. Freeze test tasks before optimization and publish their manifest hash. Keep a final untouched confirmation set for model/protocol selection bias.

## Statistical design still required

The unit of generalization is the repository/task, not repeated decoding seed. Plan paired comparisons on the same held-out tasks with uncertainty accounting for repository clustering and training seed. Use pilot *development* success/disagreement rates to calculate how many tasks and repetitions are needed to distinguish the charter's five-point effect; if the zero-spend runtime budget cannot support that sample, report the study as underpowered rather than relaxing the threshold after results.

## Minimal dataset feasibility experiment

Bring up one real repository inside a Linux ARM container, pin all dependencies, prove buggy/oracle discrimination and clean reset, then run the untrained model. This may expose environment work before the full benchmark is selected. Do not run a large training study on a corpus whose graders have not been qualified.
