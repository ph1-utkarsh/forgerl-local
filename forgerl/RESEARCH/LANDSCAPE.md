# ForgeRL landscape — 2026-09-20

## Primary references

| Reference | Contribution/method | Result and limitation | Reproduce / do not copy blindly |
|---|---|---|---|
| [SWE-smith](https://arxiv.org/abs/2504.21798) | Generate executable software tasks from repository mutations, collect agent trajectories, then fine-tune | Paper reports 40.2% SWE-bench Verified pass@1 with a 32B agent; this compute/model scale is not our setting | Reproduce test-validated task generation and trajectory provenance; do not transfer its score or scale assumptions |
| [DeepSeekMath](https://arxiv.org/abs/2402.03300) | Group-relative policy optimization uses grouped rewards without a separate value model | Mathematical reasoning setting; sparse repository rewards and tool trajectories differ | Reproduce grouped reward normalization and fixed-reference comparisons; do not assume mathematics results transfer |
| [DPO](https://arxiv.org/abs/2305.18290) | Preference optimization through chosen/rejected likelihood ratios relative to a reference policy | Preference pair quality matters; no guarantee that offline preferences improve tool recovery | Reproduce reference-relative objective and sequence masking after a valid trainable checkpoint is available |
| [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | Open 4B instruction model; Apache-2.0 model card | Existing local Q4_K_M conversion differs from full-precision published evaluations | Measure the exact local digest and settings; do not cite model-card scores as local results |
| [Ollama chat API](https://docs.ollama.com/api/chat) | Local messages, structured output, generation settings, usage/duration reporting | Serving interface; does not provide an optimizer/training path | Use deterministic settings, explicit context/output caps, response metadata; do not equate serving with training |

## Taxonomy and gap

Separate task construction, execution/grading, agent scaffold, trajectory selection, weight optimization, and evaluation. Executable repair tasks and standard SFT/preference/RL algorithms are established. The candidate contribution is a controlled comparison of failure-targeted vs random curricula under a small local compute budget. Novelty remains provisional pending closer comparison with contemporary SWE post-training work; this document is a feasibility survey, not an exhaustive state-of-the-art claim.

## Baselines and differentiation

Start with buggy repository, hand-verified oracle repair, and untrained local Qwen using identical tools and budgets. Later compare SFT, random-curriculum post-training, targeted curriculum, reward ablations, and matched inference compute. Tiny authored fixtures validate machinery only; success on them cannot establish unseen-repository generalization.

## Current nearest work and platform audit

| Reference | Relevant evidence | Consequence for ForgeRL |
|---|---|---|
| [SWE-Master, v2](https://arxiv.org/abs/2602.03411v2) | Complete SFT/RL/trajectory pipeline on Qwen2.5-Coder-32B; reported 61.4% resolved under its setup | A complete pipeline alone is not a new research contribution. Isolate the curriculum comparison, especially under the 4B/local budget. Its published score is not a fair direct baseline on different hardware/tasks. |
| [ScaleSWE](https://arxiv.org/abs/2602.09892) | Automated sandboxed construction of SWE training data | Synthetic repository generation is established. We need contamination controls and targeted-vs-random causal evidence, not a novelty claim from generation alone. |
| [SWE-smith repository](https://github.com/SWE-bench/SWE-smith/blob/main/README.md) | MIT toolkit; documentation states Ubuntu development/testing and no planned macOS support | Do not assume the standard harness works on this host. Test Linux ARM container compatibility on one selected repo before adopting the corpus. Underlying repository licenses remain separate from the toolkit license. |
| [BugsInPy](https://github.com/soarsmu/BugsInPy/blob/master/README.md) | Real Python bugs with checkout/compile/test tooling and Docker instructions | Candidate external sanity set. Audit interpreter versions, per-repository licensing, dependency reproducibility, and platform compatibility before freezing any tasks. |

Platform decision: keep the six authored tasks strictly for protocol qualification. Prefer a small audited set of real pure-Python repositories with deterministic tests for the first research feasibility cohort. Selecting by compatibility must happen before observing model outcomes, with every excluded repository/reason recorded. Final corpus selection is still open; no benchmark is silently substituted.

## Gate decision

Gate 1: PARTIAL. Sufficient references and baseline choices for an explicitly labeled feasibility spike; insufficient evidence to claim research novelty or finalize the research benchmark. Do not advance the research stage or train on held-out fixtures.
