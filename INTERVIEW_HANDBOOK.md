# ForgeRL — Rigorous Interview Handbook

Repository: <https://github.com/ph1-utkarsh/forgerl-local>

This handbook is an evidence-based preparation guide for discussing ForgeRL in software-engineering, ML-systems, reinforcement-learning, research, architecture, and security interviews. Repository-relative paths refer to the `forgerl-local` repository.

## 0. Evidence legend and audit conclusion

Use these labels when speaking:

- **Implemented** — executable source exists in the repository.
- **Demonstrated** — a versioned artifact records an observed run, and the publishable checks validate its internal consistency.
- **Surrogate or simplified** — real computation is performed, but it is deliberately narrower than the full research method.
- **Proposed** — specified in plans or reports but not demonstrated.
- **Unsupported** — the repository does not justify the claim.

### Executive audit

| Claim | Status | Evidence | Precise interpretation |
|---|---|---|---|
| Bounded JSON coding-agent loop | Implemented and qualification-tested | `forgerl/runner.py`, `forgerl/test_runner.py` | Five actions over one editable file for six authored fixtures. |
| Container isolation controls | Implemented and regression-tested locally | `runner.py:grade`, `test_runner.py:IsolationTests` | Network disabled, read-only mounts/root, non-root UID, capabilities dropped, PID/memory/CPU/output/time bounds. Docker is a control, not a perfect security boundary. |
| Host-held semantic grading | Implemented | `runner.py:grade`, `worker.py`, `cases.py` | Untrusted code receives inputs; expected outputs remain on the host. Some mutation/alias evidence is worker-reported and not adversarially trustworthy. |
| Qualification performance | Demonstrated | `forgerl/BENCHMARKS.md`, `experiments/EXP-FRL-001C` | Qwen solved 3/18 authored fixture episodes after schema correction. This is not a repository benchmark. |
| Three real repository tasks | Demonstrated as environment/evaluation artifacts | `evaluate_failure_adapter.py:TASKS`, `experiments/EXP-FRL-007C`, `009B`, `010B` | youtube-dl, Tornado, and PySnooper tasks are assigned train/development/test labels. One task per block is underpowered. |
| SFT LoRA update | Demonstrated | `adapter_pilot.py`, `EXP-FRL-011/metrics.json` | One failure-derived example, 20 updates, assistant-token loss 1.529 to 0.125, 40,960 trainable parameters, base frozen, exact reload. |
| DPO update | Demonstrated mechanically | `alignment_pilot.py`, `EXP-FRL-013/metrics.json` | One chosen/rejected pair; margin 0.382 to 4.684. This demonstrates objective optimization, not repair capability. |
| GRPO | Simplified verifier-reward surrogate | `alignment_pilot.py`, `alignment_math.py`, `EXP-FRL-014` | Two fixed candidates, rewards represented as advantages `[1,-1]`, clipped ratios; no online group sampling or multi-step policy rollouts. |
| Exact repair improvement | Demonstrated negative result | `EXP-FRL-012`, `015`, `016` | Base, SFT, DPO, and GRPO-surrogate each achieved 0/3 exact block repairs. |
| Full charter hypothesis | Not tested | `PROJECT_CHARTER.md`, `FINAL_REPORT.md` | No statistically meaningful, compute-matched, multi-seed comparison of failure-targeted versus random curricula. |
| Production readiness | Unsupported | repository scope and reports | No distributed rollout system, multi-tenant control plane, production identity/secrets layer, or operational SLO evidence. |

### Documentation discrepancy to disclose

The top-level `README.md` and `forgerl/FINAL_REPORT.md` describe the completed SFT/DPO/GRPO-surrogate pilots. The nested `forgerl/README.md` still says “No weights have been trained” and that research remains incomplete. That nested statement is stale relative to `EXP-FRL-011` through `EXP-FRL-016`. A mature answer is: “The experiment artifacts are the source of truth, but I should update or remove the stale nested README. The broader research thesis is still incomplete even though weights were trained.”

---

# 1. Repository walkthrough

## 1.1 Thirty-second answer

“ForgeRL is a local, evidence-first testbed for studying whether coding-agent failures can become post-training data. A Qwen model emits schema-constrained repair actions; candidate code is evaluated in network-disabled, resource-limited Docker containers; trusted expected outputs remain on the host; and every trajectory is retained. I ran real LoRA updates with SFT and DPO plus a deliberately limited GRPO-style surrogate. The optimizers clearly changed the preference objectives, but base and all adapters still scored zero out of three exact repository repairs. The important result is the separation between training-objective success and actual capability.”

## 1.2 Two-minute answer

“ForgeRL asks a research question: can failures from a small coding agent be converted into training signal that transfers to repository-disjoint repairs? I first built the measurement substrate. The qualification agent has five strict JSON actions—list, read, write, test, and finish—and only `solution.py` is editable. Candidate code never executes directly on the host. The grader launches a fresh Docker container with no network, read-only filesystems, non-root execution, dropped capabilities, and resource and output limits. The worker sees inputs, but the expected outputs and semantic comparison stay on the host.

The project preserved failures while hardening the harness. An early exit-code grader could be bypassed using `os._exit(0)`, and a loose action schema caused 66 invalid actions. After moving semantic comparison to the host and requiring all schema fields with a fixed path, the local Qwen agent produced zero invalid actions and solved 3 of 18 authored qualification episodes.

For post-training, I decoded a pinned local Qwen3 4B Q4_K GGUF into MLX, corrected Q4_K decoding, froze the base, and added rank-4 LoRA adapters to the final layer's attention query and value projections. A 20-step one-example SFT run reduced assistant-token loss from about 1.529 to 0.125. A ten-step DPO run increased a chosen-versus-rejected log-probability margin from 0.382 to 4.684, while a two-candidate clipped GRPO surrogate increased it to 1.220. Each changed only 40,960 adapter parameters and reloaded exactly.

But on the frozen youtube-dl, Tornado, and PySnooper exact-repair blocks, the base, SFT, DPO, and surrogate all scored 0/3. So the defensible conclusion is a negative feasibility pilot: the mechanics worked, but there is no evidence of repair improvement or generalization.”

## 1.3 Ten-minute technical walkthrough

Use this order:

1. **Research framing.** `PROJECT_CHARTER.md` proposes failure-targeted post-training against compute-matched random sampling, with repository-disjoint evaluation and at least three seeds. Say immediately that the final pilot did not reach that statistical design.
2. **Agent protocol.** `runner.py` defines the system prompt, JSON Schema, Ollama loopback API call, bounded step loop, and action validator. The action surface deliberately removes arbitrary shell access.
3. **Grader trust split.** `runner.py:grade` writes only candidate code and a fixed worker into a temporary read-only mount. `worker.py` executes named functions on supplied inputs. `cases.py` and host code retain expected outputs. `same_json` prevents Python’s `True == 1` behavior from incorrectly passing JSON values.
4. **Isolation.** Explain `--network=none`, `--read-only`, `--cap-drop=ALL`, `no-new-privileges`, UID/GID 65534, CPU/memory/PID limits, pinned local image, 64 KiB output cap, and wall-clock timeout. Explain what these controls do not prove: kernel-level isolation, daemon compromise resistance, multi-tenant safety, and worker metadata integrity.
5. **Qualification history.** `FAILURE_ANALYSIS.md` records the exit-code bypass, weak schema, public/hidden mismatch, and output-flood cleanup timeout. `BENCHMARKS.md` shows 0/18 with loose schema versus 3/18 with strict required fields. Treat this as scaffold qualification, not model learning.
6. **Real repository pilot.** The real tasks cover youtube-dl, Tornado, and PySnooper. `evaluate_failure_adapter.py` freezes one exact old/new block per train/development/test label and uses deterministic greedy generation.
7. **GGUF-to-MLX path.** `gguf_backend.py` verifies the source hash, repairs Q4_K decoding using the independent `gguf` implementation, checks Qwen metadata and tokenizer IDs, maps tensor names, and loads weights strictly into MLX. This establishes a differentiable local path; it does not prove bitwise equivalence to Ollama kernels.
8. **SFT.** `adapter_pilot.py` masks prompt tokens by calculating loss only over the assistant response. It freezes the model, injects rank-4 LoRA into `q_proj` and `v_proj` of one layer, verifies zero-initialized adapters preserve logits, trains, hashes parameters, saves adapters, reloads them, and compares logits.
9. **DPO.** `alignment_pilot.py` computes average assistant-token log probabilities for one chosen and one rejected response. It uses a frozen reference margin and minimizes `softplus(-β[(mθ)-(mref)])` with `β=0.2`.
10. **GRPO surrogate.** The same file assigns two candidates fixed advantages `[+1,-1]` and applies a PPO-style clipped ratio objective with clip 0.2. It does not sample a group from the live policy or perform online verifier rollouts; therefore say “GRPO-style surrogate,” never “full GRPO.”
11. **Evaluation and result.** `EXP-FRL-012`, `015`, and `016` compare base and adapters across three exact blocks. Every condition scores 0/3; DPO additionally generates malformed repetition on its training-domain task.
12. **Conclusion.** The contribution is the auditable distinction between optimizer behavior and capability. The next valid study requires more tasks, independent repository units, compute-matched curricula, multiple seeds, richer trajectories, and uncertainty reporting.

## 1.4 Detailed architecture and data flow

```text
                         loopback HTTP
User/task ──► prompt ──► local Ollama/Qwen
                           │ JSON action
                           ▼
                    schema + path validator
                           │
             ┌─────────────┼──────────────┐
             │ list/read    │ write        │ test/finish
             ▼              ▼              ▼
        observation     in-memory code   host orchestrator
                                              │
                                              ▼
                                   fresh Docker container
                                   candidate + fixed worker
                                   inputs, no expected values
                                              │ JSON results
                                              ▼
                                      host semantic grader
                                              │
                                      immutable trajectory
                                              │
                ┌─────────────────────────────┼──────────────────┐
                ▼                             ▼                  ▼
        SFT example                    preference pair    verifier rewards
                │                             │                  │
                ▼                             ▼                  ▼
          LoRA SFT                         LoRA DPO       LoRA clipped surrogate
                └─────────────────────────────┼──────────────────┘
                                              ▼
                               frozen exact-block evaluation
```

### End-to-end control flow

1. `runner.py:main` verifies a run ID, pins the existing Docker image by digest, creates a new run directory with `exist_ok=False`, snapshots relevant source, and records the environment.
2. `episode` sends the system/task messages to Ollama at `127.0.0.1:11434`, with temperature 0.2, a seed, a 4096-token context, and at most 512 output tokens per action.
3. The response is parsed as exactly one JSON object. `action_step` validates the action and restricts file access to `solution.py`.
4. A `test` action invokes `grade` on public cases; `finish` ends the interaction. Regardless of finish quality, final hidden grading occurs.
5. Each action, raw model response, observation, validity flag, tokens, timing, final source, and hidden result is persisted.
6. `analyze.py` aggregates descriptive results. `replay.py` supports trace inspection/replay; reproducibility is artifact-level rather than guaranteed bitwise model determinism.
7. Post-training scripts load the same pinned local checkpoint into a differentiable MLX representation, attach LoRA, train on narrowly selected data, and write immutable experiment artifacts.
8. `evaluate_failure_adapter.py` generates one greedy replacement action for each of three frozen blocks and requires exact equality of the JSON fields and old/new strings.

## 1.5 Important modules

| File | Responsibility | Important invariant | Main failure mode |
|---|---|---|---|
| `forgerl/runner.py` | Qualification orchestration, protocol, Docker grader, persistence | Model code never runs on host; run ID is immutable | Docker/Ollama unavailable; transport failure; stale image; invalid action |
| `forgerl/worker.py` | Execute requested functions inside container and serialize results | Worker receives inputs, not trusted expected outputs | Malicious code can falsify mutation/alias metadata |
| `forgerl/cases.py` | Host-side inputs and expected outputs | Expected values never mounted into candidate container | Hand-authored cases are not representative |
| `forgerl/qualification.py` | Six authored buggy/oracle tasks | Buggy must fail and oracle must pass | Small synthetic-function scope |
| `forgerl/test_runner.py` | Protocol and Docker isolation regressions | Bypass, timeout, output, mount, and network controls fail closed | Requires Docker and local image; not run in portable CI |
| `forgerl/real_repo_agent.py` | Bounded youtube-dl real-repo agent pilot | One target file and exact single replacement | One repository/task; public fixed tests may reveal structure |
| `forgerl/gguf_backend.py` | Verify/decode/map local GGUF into MLX | Hash, metadata, tokenizer, names, dtypes, and strict shapes agree | Hard-coded local source path; high memory; kernel differences |
| `forgerl/training_math.py` | Assistant-only token cross-entropy | Prompt tokens contribute no loss | Average token loss may hide sequence-length effects |
| `forgerl/adapter_pilot.py` | Bounded SFT LoRA mechanics | Only LoRA tensors change; save/reload equivalent | Single example causes memorization and weak transfer |
| `forgerl/alignment_math.py` | Scalar DPO/GRPO/reward reference functions | Objective direction and centered advantages | Reference math is not the whole training system |
| `forgerl/alignment_pilot.py` | One-pair DPO or two-candidate clipped surrogate | Base frozen; margins improve; reload matches | Objective overfits; surrogate is not online GRPO |
| `forgerl/evaluate_failure_adapter.py` | Greedy base/adapter exact-block evaluation | Same prompts and metric for both conditions | Only three tasks; exact string match is brittle |
| `scripts/verify.py` | Validate publishable headline claims | Expected zero repairs and adapter mechanics agree | Checks consistency, not truth or scientific validity |
| `scripts/verify_runs.py` | Audit local full artifacts and hashes | Required binaries, hashes, counts, and snapshots exist | Excluded adapter binaries prevent full GitHub-only audit |

## 1.6 Tests and CI

There are two materially different test tiers:

- `.github/workflows/tests.yml` runs `test_alignment.py` and `compileall` on Python 3.12. This is the portable core and currently covers four scalar alignment checks plus syntax compilation.
- `python3 -m unittest discover -s forgerl -p 'test*.py' -v` can discover protocol/isolation and MLX tests locally, but Docker tests require the pinned image and MLX tests require compatible Apple hardware/dependencies. The repository’s published summary counted 14 local tests.

Do not say “CI tests the complete system.” It does not run Docker/Ollama/MLX integration because those dependencies are unavailable on a generic Ubuntu runner.

## 1.7 Run, verify, debug, extend

```bash
# Portable publishable evidence check
python3 scripts/verify.py

# Portable scalar alignment tests and syntax
python3 -m unittest discover -s forgerl -p 'test_alignment.py' -v
python3 -m compileall -q forgerl

# Full local discovery; requires local dependencies for all tests
python3 -m unittest discover -s forgerl -p 'test*.py' -v

# Fresh qualification controls and cohort; run IDs must be new
python3 forgerl/runner.py controls --run-id CONTROL-NEW
python3 forgerl/runner.py baseline --run-id BASELINE-NEW --format schema
python3 forgerl/analyze.py forgerl/experiments/BASELINE-NEW
```

Debug in this order: validate Docker and the pinned image; validate Ollama/model availability; run controls before a model cohort; inspect the new `config.json`; inspect transport errors separately from model failures; inspect raw trace actions; confirm hidden grading failure reason; never reuse or overwrite a run ID.

---

# 2. Complete concept map

Each entry gives a simple definition, technical meaning, repository connection, rationale, alternatives, risks, and an interview prompt.

## 2.1 Language models, tokens, and decoding

### Causal language model

- **Simple:** predicts the next token from previous tokens.
- **Technical:** factorizes sequence probability as `p(x1:T)=Π_t p(x_t|x_<t)` and learns by minimizing negative log likelihood.
- **ForgeRL:** Qwen generates JSON actions; MLX computes next-token logits in `adapter_pilot.py` and `alignment_pilot.py`.
- **Why:** an instruction-tuned decoder model can combine code context with tool protocol output.
- **Alternatives:** encoder-decoder code models, edit models, retrieval-only systems, larger hosted models.
- **Risks:** invalid JSON, hallucinated substrings, long repetition, limited context, distribution shift.
- **Question:** “Is the model trained to execute tools?” **Answer:** “It predicts serialized actions. The host parses and executes a constrained subset; the model itself has no direct tool authority.”

### Tokenization and context window

- **Simple:** tokenization converts text to integer pieces; the context window bounds how many pieces the model sees.
- **Technical:** the tokenizer must preserve the checkpoint’s token-ID mapping. `gguf_backend.py` checks every vocabulary token against GGUF metadata. Qualification uses `num_ctx=4096`; SFT rejects an unexpected chat layout and sequences longer than 512 tokens.
- **Why:** tokenizer mismatch silently corrupts all logits, and bounded contexts control memory and experiment scope.
- **Alternatives:** byte-level tokenization, different chat templates, longer context with truncation policies.
- **Risks:** truncating the bug or instructions, template mismatch, comparing token-normalized scores across unequal answers.
- **Question:** “Why check token IDs?” **Answer:** “Correct weights with a mismatched vocabulary still produce semantically wrong logits, so tokenizer identity is part of checkpoint integrity.”

### Prompting, sampling, temperature, and greedy decoding

- **Simple:** prompting supplies instructions; temperature controls randomness; greedy decoding selects the highest-probability token.
- **ForgeRL:** qualification uses temperature 0.2 and seeds 0–2; exact-block adapter evaluation uses temperature 0 through MLX sampling utilities.
- **Why:** small stochasticity explores tool behavior in qualification; greedy decoding reduces evaluation variance.
- **Alternatives:** nucleus/top-k sampling, beam search, constrained grammar decoding, pass@k sampling.
- **Risks:** one greedy sample understates possible pass@k performance; seeds do not guarantee cross-version bitwise equivalence.
- **Question:** “Why not compare one stochastic sample?” **Answer:** “It adds sampling noise to a three-task study. Greedy evaluation standardizes conditions, though a stronger benchmark should also report pass@k under a fixed budget.”

## 2.2 SFT and preference learning

### Supervised fine-tuning

- **Simple:** teach the model to imitate a correct answer.
- **Technical:** minimize assistant-token cross-entropy `-mean log pθ(y_t|x,y_<t)` while masking prompt tokens.
- **ForgeRL:** `training_math.py:assistant_token_loss`; `EXP-FRL-011` trains one failure-derived chosen response for 20 steps.
- **Why:** cheapest test that gradients, masking, LoRA, save/reload, and local model conversion work.
- **Alternatives:** full fine-tuning, behavior cloning over many trajectories, rejection sampling, distillation.
- **Risks:** memorization, exposure bias, catastrophic forgetting, no learning from relative preference.
- **Question:** “What did SFT prove?” **Answer:** “The local differentiable path and adapter mechanics worked; it did not prove transferable repair learning.”

### Preference learning and DPO

- **Simple:** increase the probability of a chosen answer relative to a rejected answer.
- **Technical:** with `mθ=logπθ(y+|x)-logπθ(y-|x)` and reference margin `mref`, ForgeRL minimizes `log(1+exp(-β(mθ-mref)))`. The implementation uses average assistant-token log probabilities and `β=0.2`.
- **ForgeRL:** `alignment_pilot.py`; scalar reference in `alignment_math.py`; `EXP-FRL-013`.
- **Why:** DPO avoids fitting a separate reward model and avoids online rollouts for this mechanics pilot.
- **Alternatives:** PPO/RLHF, IPO, ORPO, KTO, reward-weighted SFT.
- **Risks:** pair quality dominates; a single pair overfits; length normalization changes the preference geometry; margin improvement can harm generation.
- **Question:** “Where is the reference policy?” **Answer:** “The unadapted frozen Qwen is evaluated before LoRA insertion; its chosen/rejected log-probability difference becomes `ref_margin`.”

### DPO beta

- **Simple:** controls how strongly relative preference differences affect the loss.
- **Technical:** beta scales the policy-versus-reference margin. Larger beta makes the logistic loss more sensitive and can induce more aggressive movement; effective behavior also depends on learning rate, data, and parameterization.
- **ForgeRL:** hard-coded `beta=.2` in `alignment_pilot.py` and persisted in the experiment config.
- **Risk:** no beta ablation exists, so beta 0.2 is a pilot choice, not an optimized value.

## 2.3 LoRA and parameter efficiency

### LoRA

- **Simple:** train small low-rank matrices instead of the full model.
- **Technical:** replace a frozen linear map `Wx` with `Wx + sBAx`, where rank `r` is much smaller than input/output dimensions. ForgeRL uses rank 4, scale 4, dropout 0, on final-layer `q_proj` and `v_proj`.
- **ForgeRL:** `adapter_pilot.py` and `alignment_pilot.py`; 40,960 trainable parameters across four adapter tensors.
- **Why:** it fits a 16 GB Apple Silicon, preserves the base, saves small artifacts, and makes integrity checks tractable.
- **Alternatives:** full fine-tuning, QLoRA, adapters on more layers, prefix/prompt tuning.
- **Risks:** insufficient capacity, narrow layer coverage, quantized-source/dequantized-training mismatch, brittle hyperparameters.
- **Question:** “Why exactly 40,960?” **Answer:** “For each adapted linear layer, LoRA adds `r(d_in+d_out)` parameters. The repository relies on MLX’s instantiated shapes and sums tensor sizes; two projections in one layer total 40,960. The evidence is the four changed LoRA tensors and reported count.”

### Frozen base and adapter integrity

- **Simple:** base weights must not change.
- **Technical:** `model.freeze()` precedes LoRA insertion; trainable names must end in `lora_a` or `lora_b`; pre/post hashes identify changed tensors; zero initialization preserves initial logits; reload logits/margins must match.
- **Strength:** multiple independent checks reduce the chance of silently fine-tuning the base.
- **Limit:** `frozen_base_unchanged: true` is partly asserted by code, while full hash artifacts and adapter binaries are intentionally not all published. `scripts/verify_runs.py` is the stronger local audit.

## 2.4 RL, policy gradients, and the GRPO surrogate

### Reinforcement learning for language models

- **Simple:** improve a policy using rewards from generated behavior.
- **Technical:** maximize expected return `J(θ)=E_{τ~πθ}[R(τ)]`; the likelihood-ratio gradient is `E[∇θ log πθ(a|s) A(s,a)]`.
- **ForgeRL:** the repository has verifiable repair rewards and a clipped ratio surrogate, but it does not run a complete online RL loop over newly sampled multi-turn trajectories.
- **Correct claim:** “ForgeRL explores RL-style post-training mechanics.”
- **Incorrect claim:** “ForgeRL proves online GRPO improves coding agents.”

### Group-relative advantages

- **Simple:** compare each answer’s reward with others generated for the same prompt.
- **Technical:** `A_i=(r_i-mean(r))/(std(r)+ε)`. `alignment_math.py:grouped_advantages` implements this scalar reference.
- **ForgeRL difference:** the training path uses exactly two predetermined candidates and directly supplies advantages `[1,-1]`; it does not call the helper to normalize a live sampled group.
- **Risk:** with two fixed candidates, “group relative” is a conceptual analogue, not a representative GRPO experiment.

### Clipped policy ratio

- **Simple:** prevent an update from benefiting too much by moving far from the old policy.
- **Technical:** use `r_i(θ)=exp(logπθ-logπold)` and optimize `min(r_i A_i, clip(r_i,1-ε,1+ε)A_i)` with `ε=.2`.
- **ForgeRL:** `alignment_pilot.py:loss_fn`; `alignment_math.py:clipped_grpo_loss`.
- **Risks:** no explicit KL term, stale fixed “old” log probabilities, tiny group, repeated updates on the same pair.

### Reward design

- **Simple:** convert desired behavior into a score.
- **Technical:** `repair_reward` combines test pass `+1`, valid action `+0.1`, finish `+0.1`, and step penalty `-0.01*steps`.
- **Why:** executable verification gives lower ambiguity than an LLM judge.
- **Risk:** shaping rewards can dominate sparse correctness, incentivize premature finish, or be gamed if the grader is weak. The actual two-candidate alignment run effectively uses binary relative rewards, not a large rollout corpus scored by this function.

### Offline/online and on/off-policy

- SFT and DPO here are **offline**: they learn from a fixed example/pair.
- The surrogate is also effectively **offline/repeated-batch**, despite using a policy-ratio objective.
- Full GRPO would be online or iteratively on-policy: sample groups from the current policy, verify them, normalize rewards per prompt, update, and refresh rollouts.
- Reusing fixed samples across many updates creates off-policy drift; clipping limits but does not remove this issue.

### KL regularization and policy drift

- DPO implicitly anchors to a reference through the reference log-ratio.
- The surrogate has no explicit token-level KL penalty; clipping constrains observed candidate ratios only.
- DPO’s malformed repetitive response in `EXP-FRL-015` is evidence consistent with narrow over-optimization, though it does not by itself diagnose the exact cause.

## 2.5 Agents and software repair

### Agent loop, actions, observations, trajectories

- **Agent:** a policy that observes state, chooses an action, receives an observation, and repeats.
- **Action schema:** a machine-checkable contract. ForgeRL’s qualification schema requires `action`, `path`, and `content` and disallows extra fields.
- **Observation:** list/read content, write acknowledgment, public test result, finish acknowledgment, or structured error.
- **Trajectory:** the entire ordered prompt/action/observation history plus final state and outcome.
- **Why preserve it:** debugging, failure classification, later SFT/preference extraction, and auditability.
- **Risk:** traces can contain large or sensitive content in real deployments; immutable does not mean automatically trustworthy.

### Patch generation and exact repair

- Qualification rewrites a complete single file in memory. The real pilot emits an exact old/new replacement JSON object.
- Exact matching provides a deterministic high-precision metric but rejects semantically equivalent fixes.
- A production benchmark should apply the candidate patch to a clean checkout and run public plus hidden regression tests, while separately tracking applicability, test pass rate, scope, and patch quality.

## 2.6 Security and sandboxing

### Threat model

The candidate program is untrusted and may try to read graders, mutate mounts, use the network, fork processes, flood output, hang, or fake success. The host orchestration and expected outputs are trusted. Docker daemon and host kernel are trusted in this prototype.

### Defense in depth

- No arbitrary shell action in the agent protocol.
- Path allowlist and payload-size bound.
- Fresh container per grade.
- No network.
- Read-only root and bind mount.
- Non-root user, dropped capabilities, no-new-privileges.
- CPU, memory, swap, PID, wall-time, and output limits.
- Host semantic comparison and response-shape validation.
- Pinned local image ID and no pulls.
- Regression tests for early exit, fake boolean pass, timeout, flooding, hidden-file absence, write denial, and network denial.

### Residual risks

- Shared-kernel container escape vulnerabilities.
- Docker daemon/configuration compromise.
- Side channels and resource-exhaustion variants.
- Dependency/supply-chain risk in the base image.
- Worker-reported mutation and alias flags can be falsified.
- The real-repository test runner is not identical to the stronger host-semantic function grader.
- No seccomp profile, microVM, eBPF audit, filesystem quota, per-tenant identity, or secrets system is demonstrated.

## 2.7 Reproducibility, leakage, and statistics

### Determinism and replay

- Seeds, model metadata, source hashes, image ID, raw responses, token counts, and configs are recorded.
- `exist_ok=False` prevents reusing a run directory.
- Stochastic kernels, model/runtime versions, hardware, and Ollama behavior mean equal seeds do not guarantee bitwise identical generations.
- Replay means reconstructing or inspecting recorded interaction evidence; it is not a proof that a future generation will match.

### Repository-disjoint evaluation and leakage

- Repository-disjoint means training and evaluation units come from different repositories, reducing near-duplicate and project-specific leakage.
- ForgeRL labels youtube-dl as train, Tornado as development, and PySnooper as test.
- With exactly one task per repository/block, the design illustrates separation but cannot estimate a population effect.
- Foundation-model pretraining contamination is not measured; historical GitHub code may already have been seen by Qwen.

### Exact repair, pass@k, and uncertainty

- Exact repair rate is `successes/attempts` under the frozen exact metric.
- For 0 successes out of 3 independent tasks, the point estimate is 0, but uncertainty is enormous. The rule-of-three approximate 95% upper bound is `3/n=1`, which is uninformative at `n=3`. A Clopper–Pearson interval likewise has a high upper limit.
- Do not treat three decoding samples as three independent repository units if they share the same task.
- `pass@k` asks whether at least one of `k` candidates succeeds. With `n` sampled candidates and `c` correct, the common unbiased estimator is `1 - C(n-c,k)/C(n,k)` when `n-c >= k`.
- ForgeRL reports greedy pass@1-like exact results, not a proper pass@k study.

## 2.8 Software engineering practices

- **Modularity:** orchestration, worker, cases, training math, backend conversion, and evaluation are separated.
- **Typing:** limited; most modules lack type annotations. Production work should add typed dataclasses/protocols and schema models.
- **Error handling:** invalid actions fail closed; infrastructure failure is recorded; some dense one-line scripts reduce maintainability.
- **Configuration:** many hyperparameters are hard-coded, which helps freeze a pilot but hinders systematic experiments.
- **Logging:** JSON artifacts are useful; structured event logging and correlation IDs are absent.
- **Testing:** strong targeted regressions for discovered sandbox bugs; CI covers only a portable subset.
- **Documentation:** strong evidence maps and failure notes; nested README is stale and must be fixed.

---

# 3. Engineering decisions and cross-questions

| Decision | Why selected | Alternatives | Risk/limitation | Evidence | Interview line | Cross-question and answer |
|---|---|---|---|---|---|---|
| Strict JSON schemas | Makes actions parseable, bounded, and auditable | Free-form ReAct, function-calling API, grammar decoder | Valid JSON can still be semantically wrong; schema became scaffold intervention | `runner.py:ACTION_SCHEMA`, `BENCHMARKS.md` | “The schema reduced protocol failures from 66 invalid actions to zero in the revised cohort, but that was a harness change, not learning.” | **Did you bias the benchmark?** “Yes, changing the scaffold changes the system. I report it as qualification, never as a model-training gain.” |
| Docker execution | Cheap local process/resource isolation | subprocess, VM, microVM, gVisor, hosted sandbox | Shared kernel; not a sufficient hostile multi-tenant boundary | `runner.py:grade`, isolation tests | “Docker was proportional for a local pilot and was hardened with multiple controls.” | **Why trust Docker?** “I do not claim perfect trust. Production should add stronger isolation such as microVMs and host hardening.” |
| Host-held expected outputs | Prevent candidate code from reading or changing the answer | Tests mounted in container, LLM judge, remote evaluator | Host logic becomes trusted computing base; worker metadata remains spoofable | `grade`, `cases.py`, `worker.py` | “The container returns results; the host decides correctness.” | **Can it fake JSON?** “It can emit arbitrary JSON, so the host validates shape, length, types, values, and expected exceptions. Mutation/alias flags are still weaker.” |
| Repository-disjoint split | Tests transfer across codebases | Random task split, temporal split, file split | Only one task per split; pretraining contamination remains | `evaluate_failure_adapter.py:TASKS` | “The split direction is right, but the sample is too small to support generalization.” | **Is PySnooper truly unseen?** “Unseen to this fine-tuning data, not proven unseen to foundation pretraining.” |
| LoRA | Fits local memory and gives auditable parameter isolation | Full fine-tuning, QLoRA, prompt tuning | Low capacity and one-layer targeting may underfit | training scripts, metrics | “LoRA made the zero-budget mechanics test possible.” | **Could LoRA explain failure?** “Yes. Adapter placement and rank are plausible bottlenecks and need ablation.” |
| SFT/DPO/surrogate comparison | Exercises imitation, preference, and reward-style objectives | Only SFT; PPO; rejection sampling | Each uses essentially one pair/example; not a fair method benchmark | `EXP-FRL-011`–`016` | “It is a mechanics comparison, not evidence ranking the algorithms.” | **Which method won?** “None on repair. DPO moved its proxy margin most, but proxy movement is not capability.” |
| Exact graders | Objective, reproducible, no judge model cost | LLM judge, human review, CodeBLEU | Exact string equality rejects equivalent patches | `evaluate_failure_adapter.py:score` | “Exactness gave a conservative pilot metric.” | **Would tests be better?** “For a full benchmark, yes: patch apply plus hidden regression tests should be primary, with exact-match as a diagnostic.” |
| Immutable trajectories | Enables audits, failure mining, reproducibility | Aggregate metrics only, mutable experiment DB | Storage/privacy; source snapshot does not guarantee future runtime equivalence | `runner.py`, `REPRODUCIBILITY.md` | “I preserve failures rather than silently rerun them away.” | **Are artifacts tamper-proof?** “No cryptographic append-only store is implemented; hashes and immutable run paths detect some changes, not malicious host tampering.” |
| Local-only execution | Zero monetary cost, privacy, reproducibility on owned hardware | Hosted APIs/GPUs | Slower, smaller sample, Apple-specific MLX path | charter, configs, `paid_spend:0` | “Local constraints shaped the study into an honest feasibility pilot.” | **Was the result compute-limited?** “Likely, but that is a hypothesis. The data cannot separate compute, data, method, and capacity limitations.” |
| Preserve 0/3 result | Prevents publication bias and distinguishes objectives from outcomes | Discard run, tune on test set | Small result can be misread as universal failure | final report, failure notes | “A negative result is useful because it invalidates the inference that lower training loss means better repair.” | **Did the project fail?** “The capability hypothesis was not supported; the measurement and mechanics goals succeeded. I separate those outcomes.” |
| Correct Q4_K decoding | Needed a differentiable representation from the installed local model | Download another checkpoint, train through llama.cpp, dequantize externally | Hard-coded path; dequantized MLX may differ from Ollama | `gguf_backend.py`, `EXP-FRL-004` | “I detected backend disagreement and replaced affected tensor decoding with an independent implementation.” | **Same model?** “Same pinned source weights and tokenizer mapping, but not identical runtime kernels; I avoid claiming bitwise backend equivalence.” |

---

# 4. Mathematical preparation

## 4.1 Cross-entropy and causal loss

For prompt `x` and assistant response tokens `y1:T`:

`L_SFT(θ) = -(1/T) Σ_t log pθ(y_t | x, y_<t)`

If the correct token has probability 0.8, its contribution is `-ln(0.8)=0.223`; at probability 0.1 it is `2.303`. Minimizing loss moves mass toward the demonstrated token. `assistant_token_loss` computes unreduced cross-entropy then averages only positions at or after `assistant_start`. `test_prompt_tokens_do_not_contribute` verifies prompt-logit changes do not alter the loss.

Repository result: sequence loss fell from `1.5285` before the first update to `0.1253` after 20 steps. This is strong evidence of fitting the one training sequence, not of repair generalization.

## 4.2 LoRA

For a frozen matrix `W ∈ R^(d_out×d_in)`:

`h = Wx + sBAx`, with `A ∈ R^(r×d_in)`, `B ∈ R^(d_out×r)`.

Trainable count per adapted matrix is `r(d_in+d_out)` (bias excluded). Rank 4 is much smaller than a full `d_out*d_in` update. ForgeRL adapts Q and V projections in one layer and reports 40,960 total trainable values. The base is checked through freezing, trainable-name allowlisting, hashes, zero-init logit equality, and reload equality.

## 4.3 DPO derivation and numerical intuition

Define average response log probabilities:

`cθ = log πθ(y+|x)`, `rθ = log πθ(y-|x)`, `mθ=cθ-rθ`.

With reference margin `mref`, ForgeRL uses:

`L_DPO = log(1 + exp(-β(mθ-mref)))`.

At initialization `mθ=mref`, so the loss is `log 2≈0.693`, exactly matching the first recorded loss. With `β=.2`, `mref=.382`, and final `mθ=4.684`, the logit is `.2*(4.684-.382)=.8604`; the corresponding loss is approximately `log(1+e^-.8604)=.353`. The last pre-update recorded loss is about .399; the exact comparison differs because metrics record losses before each update and final margin after the last update.

Interpretation: the trained adapter made the chosen completion much more likely relative to the rejected completion than the reference did. It does not establish that either completion is globally correct or that decoding will yield the chosen response.

## 4.4 Policy-gradient intuition

For trajectory `τ` with return `R(τ)`:

`J(θ)=E_{τ~πθ}[R(τ)]`

`∇J(θ)=E[Σ_t ∇logπθ(a_t|s_t) A_t]`.

Positive advantage increases the probability of sampled actions; negative advantage decreases it. A baseline reduces variance without changing the expectation when correctly constructed.

ForgeRL does not estimate this expectation over a meaningful rollout distribution. It applies the intuition to two fixed response sequences.

## 4.5 Group normalization and clipped surrogate

For rewards `[1,0]`, mean is `.5`, population standard deviation is `.5`, yielding advantages approximately `[+1,-1]`. This is why the fixed advantages in `alignment_pilot.py` correspond to a two-member binary-reward group.

Probability ratio: `ρ_i=exp(logπθ(y_i|x)-logπold(y_i|x))`.

Clipped loss:

`L = -mean[min(ρ_i A_i, clip(ρ_i,1-ε,1+ε) A_i)]`.

With `ε=.2`, a positive-advantage candidate at ratio 1.5 is capped at 1.2 for the objective. For a negative advantage, the `min` construction penalizes movement in the wrong direction. The observed loss reaches about `-0.2` then reverses somewhat, illustrating clipping and interacting candidate ratios; it is not a monotonic capability score.

## 4.6 KL regularization

`D_KL(πθ || πref)=E_{y~πθ}[logπθ(y|x)-logπref(y|x)]`.

Explicit KL penalties discourage policy drift across the distribution. DPO incorporates a reference comparison through log-ratios. ForgeRL’s surrogate lacks an explicit distributional KL term and only constrains ratios on its two stored responses, leaving unconstrained behavior elsewhere.

## 4.7 Expected return and sparse reward

If exact repair gives reward 1 and failure 0, expected return under a one-step task is the success probability. With observed `0/3`, the empirical mean is zero, but the sample is too small to estimate the true probability tightly. Shaping rewards make learning denser but risk optimizing validity or termination instead of correctness.

## 4.8 Pass@k

Given `n` generated samples of which `c` are correct, an estimator is:

`pass@k = 1 - C(n-c,k)/C(n,k)`.

Example: 2 correct among 10 candidates and `k=3` gives `1-C(8,3)/C(10,3)=1-56/120≈0.533`. This assumes the evaluated candidate set represents the sampling procedure. ForgeRL did not run this experiment.

## 4.9 Confidence intervals at tiny n

For 0/3, never say the true rate is zero. A Bayesian interval depends heavily on the prior; an exact frequentist interval is very wide. The “rule of three” gives only an approximate 95% upper bound `3/n`, which is 1.0 here. The correct conclusion is simply that no success was observed under this frozen three-task pilot.

---

# 5. Exhaustive question bank

Each question includes a spoken answer, deeper answer, evidence, trap, and likely follow-up.

## 5.1 Beginner and screening

### Q1. What problem does ForgeRL solve?

**Spoken:** “It creates a controlled local loop for collecting coding-agent failures, converting them into post-training examples, and checking whether objective improvements transfer to real repairs.”  
**Deep:** The research thesis compares failure-targeted curricula with compute-matched random sampling on repository-disjoint tasks, but the repository completes only a bounded feasibility pilot.  
**Evidence:** `PROJECT_CHARTER.md`, top-level `README.md`.  
**Avoid:** Saying the thesis was proven.  
**Follow-up:** What remains to test the thesis?

### Q2. What did you personally build?

**Spoken:** “The repository demonstrates an agent protocol, hardened grader, Docker isolation, experiment persistence, local GGUF-to-MLX loading, LoRA training objectives, evaluation, tests, and reports.”  
**Deep:** Be ready to open `runner.py`, `gguf_backend.py`, `adapter_pilot.py`, and `alignment_pilot.py` and explain a concrete invariant in each. State your actual authorship honestly; repository presence alone cannot prove who typed each line.  
**Evidence:** named files and Git history.  
**Avoid:** Claiming solo authorship if tools or collaborators contributed.  
**Follow-up:** Which bug required the most reasoning?

### Q3. What is the model?

**Spoken:** “A locally installed Qwen3 4B Instruct Q4_K_M model.”  
**Deep:** Qualification calls Ollama; differentiable training verifies and decodes the pinned GGUF into MLX.  
**Evidence:** `runner.py:MODEL`, `gguf_backend.py:SOURCE_SHA256`.  
**Avoid:** Calling it a model trained from scratch.  
**Follow-up:** Why might Ollama and MLX outputs differ?

### Q4. What are the five tools?

**Spoken:** “List, read, write, test, and finish.”  
**Deep:** They are serialized JSON actions; only `solution.py` is valid in the qualification environment, and fields are mandatory.  
**Evidence:** `runner.py:SYSTEM`, `ACTION_SCHEMA`, `action_step`.  
**Avoid:** Saying the agent has shell access.  
**Follow-up:** How would you add a safe search tool?

### Q5. What is the main result?

**Spoken:** “Training objectives improved, but exact repair did not: every base or adapter condition scored 0/3.”  
**Deep:** SFT fit its sequence; DPO and the surrogate moved their pairwise margins; none transferred to three exact blocks.  
**Evidence:** `EXP-FRL-011`–`016`.  
**Avoid:** Calling DPO the winner.  
**Follow-up:** Why is that result useful?

### Q6. Did it cost money?

**Spoken:** “Recorded paid API and cloud spend was zero; it used owned local hardware and an installed model.”  
**Deep:** Zero paid spend is not zero economic cost: electricity, hardware depreciation, and engineering time remain.  
**Evidence:** configs/metrics `paid_spend: 0`, charter.  
**Avoid:** “It cost nothing.”  
**Follow-up:** How would you estimate total cost of ownership?

### Q7. Is ForgeRL production-ready?

**Spoken:** “No. It is a bounded research prototype with deliberately narrow tasks and local infrastructure.”  
**Deep:** It lacks distributed workers, tenant isolation, operational SLOs, secrets, production observability, deployment gates, and statistically strong evaluation.  
**Evidence:** scope sections and code.  
**Avoid:** Presenting Docker flags as a complete platform.  
**Follow-up:** What is the first production milestone?

### Q8. Why is it called evidence-first?

**Spoken:** “Because it versions configs, traces, metrics, source snapshots, hashes, negative runs, and failure explanations.”  
**Deep:** `scripts/verify.py` validates headline artifact consistency, while `verify_runs.py` performs stronger local checks when excluded binaries exist.  
**Evidence:** scripts and experiment directories.  
**Avoid:** Equating internal consistency with scientific truth.  
**Follow-up:** How could artifacts still be falsified?

## 5.2 Agent and software-engineering questions

### Q9. Why not accept free-form text?

**Spoken:** “A strict schema reduces parsing ambiguity and narrows authority.”  
**Deep:** The loose-schema run had 66 invalid actions; required fields and a path enum produced zero invalid actions in the revised cohort.  
**Evidence:** `FAILURE_ANALYSIS.md`, `BENCHMARKS.md`.  
**Avoid:** Claiming schema alone guarantees safety.  
**Follow-up:** Is the improvement a model gain?

### Q10. What is an invariant in the action layer?

**Spoken:** “Only the exact relative path `solution.py` is accessible.”  
**Deep:** `valid_path` rejects absolute paths, traversal, `./solution.py`, nonstrings, and other targets; writes are bounded to 16,000 bytes.  
**Evidence:** `runner.py:valid_path`, `test_runner.py:test_paths`.  
**Avoid:** Assuming `PurePosixPath` validation alone covers symlink attacks in a broader filesystem.  
**Follow-up:** How would this change for a multi-file repository?

### Q11. Why is `True == 1` relevant?

**Spoken:** “Python equality would let a boolean pass when an integer is expected, so the grader compares JSON types exactly.”  
**Deep:** `same_json` first checks `type(actual) is type(expected)` and recursively compares lists/dicts.  
**Evidence:** `runner.py:same_json`, protocol test.  
**Avoid:** Using plain `==` for typed semantic grading.  
**Follow-up:** What about float tolerance?

### Q12. Why immutable run IDs?

**Spoken:** “They prevent accidental overwriting and retrospective cleanup of failed experiments.”  
**Deep:** output directories are created with `exist_ok=False`; configs snapshot hashes and relevant sources.  
**Evidence:** `runner.py:main`, training scripts.  
**Avoid:** Calling this cryptographic immutability.  
**Follow-up:** How would you make it tamper-evident?

### Q13. How are transport failures treated?

**Spoken:** “They are retained as failed attempts rather than silently excluded.”  
**Deep:** generic exceptions set `transport_failure`, append the record, and end the episode; hidden grader infrastructure failures also return an explicit failure object.  
**Evidence:** `runner.py:episode`.  
**Avoid:** Mixing infrastructure reliability with policy quality without stratification.  
**Follow-up:** How would you report both metrics?

### Q14. Why pin Docker image IDs?

**Spoken:** “A tag can move; a digest records the exact local image used.”  
**Deep:** `pinned_image` requires a `sha256:` ID and Docker runs with `--pull=never`.  
**Evidence:** `runner.py:pinned_image`, `grade`.  
**Avoid:** Saying an image digest pins the host kernel or Docker version.  
**Follow-up:** What else belongs in a provenance record?

### Q15. What is replay?

**Spoken:** “Re-examining recorded actions and observations to reproduce analysis or debug failure.”  
**Deep:** Versioned trace files allow deterministic inspection even if stochastic generation cannot be recreated bitwise.  
**Evidence:** `replay.py`, `replays/`, `REPRODUCIBILITY.md`.  
**Avoid:** Promising identical future generations.  
**Follow-up:** What must be captured for stronger replay?

### Q16. How would you add a new tool safely?

**Spoken:** “Start with the narrowest schema and authority, validate all inputs on the host, execute in the sandbox, cap outputs/time, and add abuse tests.”  
**Deep:** Define its state transition, allowlisted paths, payload/output budgets, observation schema, logging, and failure semantics before exposing it.  
**Evidence:** patterns in `ACTION_SCHEMA`, `action_step`, isolation tests.  
**Avoid:** Passing model-provided strings to a host shell.  
**Follow-up:** Design a grep/search tool without shell injection.

## 5.3 Security questions

### Q17. What was the worst grader vulnerability?

**Spoken:** “The original in-process, exit-code-based grader could be bypassed with `os._exit(0)`.”  
**Deep:** A zero exit occurred without assertions, creating false positive reward. The fix moved execution into a worker container and correctness comparison to the host.  
**Evidence:** `FAILURE_ANALYSIS.md:FRL-FAIL-001`, regression test.  
**Avoid:** Hiding that historical runs became invalid evidence.  
**Follow-up:** Which runs must not be cited?

### Q18. Why keep expected outputs on the host?

**Spoken:** “To prevent the candidate from reading or rewriting the success condition.”  
**Deep:** Only input rows enter the container; returned rows are structurally and semantically checked against host-held cases.  
**Evidence:** `runner.py:grade`, `cases.py`.  
**Avoid:** Claiming hidden inputs are also always secret—the worker receives test inputs.  
**Follow-up:** Could input visibility itself cause leakage?

### Q19. What does `--network=none` protect?

**Spoken:** “It blocks ordinary container network access, limiting exfiltration and dependency downloads.”  
**Deep:** A regression test attempts a connection to `1.1.1.1:443` and expects failure. It does not prove absence of all host/kernel side channels.  
**Evidence:** `grade` command, `test_network_denied`.  
**Avoid:** “The container is unhackable.”  
**Follow-up:** What stronger production controls would you add?

### Q20. Why read-only root and mounts?

**Spoken:** “They prevent candidate persistence and grader/test mutation.”  
**Deep:** the container root is read-only; `/work` is a read-only bind; Python bytecode writing is disabled.  
**Evidence:** Docker command and `test_write_mount_denied`.  
**Avoid:** Ignoring writable virtual filesystems or kernel interfaces in a full threat model.  
**Follow-up:** Would you add a controlled scratch filesystem?

### Q21. How is denial of service bounded?

**Spoken:** “Wall time, CPU, memory, swap, PID, and output limits bound common abuse.”  
**Deep:** the host reads stdout incrementally, kills at 64 KiB or timeout, closes the pipe, and bounds cleanup. A prior output flood exposed cleanup blocking.  
**Evidence:** `runner.py:grade`, `FRL-FAIL-004`.  
**Avoid:** Claiming all resource attacks are solved.  
**Follow-up:** Why close stdout before `docker rm -f`?

### Q22. What security signal remains untrusted?

**Spoken:** “Mutation and alias metadata are reported by the worker and can be falsified by adversarial candidate code.”  
**Deep:** semantic outputs are independently checked, but those behavioral properties need host-observable techniques such as serialization snapshots or a more isolated instrumentation layer.  
**Evidence:** `FAILURE_ANALYSIS.md`, `REQUIREMENTS.md`.  
**Avoid:** Saying all grader signals are host-authenticated.  
**Follow-up:** How would you repair that gap?

### Q23. Why is Docker insufficient for multi-tenancy?

**Spoken:** “Containers share the host kernel and Docker daemon is highly privileged.”  
**Deep:** production untrusted-code execution should consider microVMs, hardened kernels, seccomp/AppArmor, isolated worker hosts, minimal images, egress proxies, quotas, and rapid patching.  
**Evidence:** absence of these layers; documented bounded scope.  
**Avoid:** Treating more flags as a formal proof.  
**Follow-up:** Compare Firecracker, gVisor, and Docker.

## 5.4 ML and SFT questions

### Q24. Why mask prompt tokens?

**Spoken:** “The training target is the assistant action, not reproducing the user prompt.”  
**Deep:** assistant-only loss avoids spending gradient capacity on fixed instructions and mirrors response fine-tuning.  
**Evidence:** `assistant_token_loss`, its numerical test.  
**Avoid:** Saying prompt masking is always optimal; some objectives train the full sequence.  
**Follow-up:** What off-by-one error could occur?

### Q25. What did the SFT loss curve show?

**Spoken:** “The model rapidly fit the single response: roughly 1.529 to 0.125.”  
**Deep:** monotonic-ish training loss and exact adapter reload validate mechanics; they mostly show memorization capacity at this scale.  
**Evidence:** `EXP-FRL-011/metrics.json`.  
**Avoid:** Calling it validation loss.  
**Follow-up:** Where is the held-out SFT loss?

### Q26. Why adapt only Q and V in one layer?

**Spoken:** “It minimized memory and made the local feasibility test affordable.”  
**Deep:** attention query/value adapters are a common PEFT target, but final-layer-only rank 4 is an intentionally tiny capacity choice with no ablation.  
**Evidence:** adapter config in training scripts.  
**Avoid:** Saying this was empirically optimal.  
**Follow-up:** What adapter ablation would you run?

### Q27. How did you prove the base was frozen?

**Spoken:** “I froze it, allowlisted trainable tensor names, hashed parameters, verified zero-init logit equality, and checked exact reload.”  
**Deep:** only four `.lora_a/.lora_b` tensors changed; base logits initially changed by exactly zero and restored logits matched trained logits in the SFT artifact.  
**Evidence:** `adapter_pilot.py`, `EXP-FRL-011`.  
**Avoid:** Relying only on the library’s `freeze()` call.  
**Follow-up:** Why can hash comparison be expensive?

### Q28. What is catastrophic forgetting here?

**Spoken:** “Narrow updates can damage previously useful behavior outside the training example.”  
**Deep:** DPO’s malformed repetition is compatible with narrow behavior distortion, but the repository lacks a broad pre/post capability suite needed to quantify forgetting.  
**Evidence:** `EXP-FRL-015`.  
**Avoid:** Diagnosing repetition conclusively as catastrophic forgetting.  
**Follow-up:** What regression suite would detect it?

### Q29. Why not full fine-tuning?

**Spoken:** “It exceeded the practical local memory/compute envelope and would make parameter-isolation auditing harder.”  
**Deep:** LoRA trades capacity for affordability and recoverability. Full tuning could improve capacity but increases optimizer state, checkpoint size, risk, and experiment cost.  
**Evidence:** charter constraints and adapter configs.  
**Avoid:** Saying LoRA always matches full tuning.  
**Follow-up:** Would QLoRA help if the source is already Q4?

## 5.5 DPO and GRPO questions

### Q30. Explain DPO without equations.

**Spoken:** “DPO teaches a model to prefer a chosen response over a rejected one while comparing the change with a frozen reference model.”  
**Deep:** It directly optimizes a logistic objective on policy/reference log-ratios, avoiding a separately trained reward model.  
**Evidence:** `alignment_pilot.py`.  
**Avoid:** Calling DPO ordinary supervised learning or online RL.  
**Follow-up:** Why does the reference matter?

### Q31. What was chosen and rejected?

**Spoken:** “A failure-derived youtube-dl repair action served as the chosen response and a known incorrect alternative as rejected.”  
**Deep:** Both are fixed completions under the same prompt; their assistant-token average log probabilities define the margin.  
**Evidence:** `training/youtube_failure_example.json`, `alignment_pilot.py:REJECTED`.  
**Avoid:** Claiming a human preference dataset.  
**Follow-up:** How would you validate pair quality?

### Q32. Why average token log probability?

**Spoken:** “It reduces raw length bias between responses.”  
**Deep:** summing log probabilities systematically penalizes longer completions; averaging normalizes by assistant-token count, but changes the standard sequence-level DPO geometry and may overweight tokenwise ease.  
**Evidence:** `lp` returns negative mean assistant loss.  
**Avoid:** Calling it canonical DPO without qualification.  
**Follow-up:** Compare sum, mean, and length-penalized scoring.

### Q33. What does the 0.382-to-4.684 margin mean?

**Spoken:** “The adapter became much more favorable to the chosen completion relative to the rejected one.”  
**Deep:** it is an average-token log-probability difference on one stored pair. It is not a 4.3-point repair improvement and not a calibrated probability of success.  
**Evidence:** `EXP-FRL-013/metrics.json`.  
**Avoid:** Converting it into percentage accuracy.  
**Follow-up:** Why might decoding still fail?

### Q34. Is DPO reinforcement learning?

**Spoken:** “It is a preference-optimization method derived from RLHF assumptions, but this implementation is offline direct optimization, not an online environment-interaction loop.”  
**Deep:** taxonomy varies; the precise statement is more valuable than arguing labels.  
**Evidence:** fixed pair and no rollout refresh in `alignment_pilot.py`.  
**Avoid:** Overstating on-policy learning.  
**Follow-up:** What would online DPO-like iteration require?

### Q35. What is GRPO?

**Spoken:** “A policy-optimization approach that compares rewards among multiple completions for the same prompt and updates using relative advantages, commonly with policy-ratio clipping and regularization.”  
**Deep:** full systems sample groups from the policy, score them, normalize within group, and train across many prompts with refreshed rollouts.  
**Evidence:** surrounding theory; scalar helper functions.  
**Avoid:** Equating ForgeRL’s two fixed candidates with a full implementation.  
**Follow-up:** Why group-relative rather than a learned critic?

### Q36. Exactly how is ForgeRL’s GRPO different?

**Spoken:** “It is a two-candidate clipped verifier-reward surrogate with fixed completions and fixed advantages.”  
**Deep:** no live group sampling, no repeated environment rollouts, no multi-turn credit assignment, no learned value function, and no explicit KL term.  
**Evidence:** `alignment_pilot.py:loss_fn`.  
**Avoid:** Saying “we trained with GRPO” without “surrogate.”  
**Follow-up:** What minimum changes make it closer to GRPO?

### Q37. Why did the surrogate margin move less than DPO?

**Spoken:** “The objectives and clipping differ, so their numeric margins are not directly comparable as capability measures.”  
**Deep:** the clipped ratio saturates contributions and the two sequence ratios interact; DPO directly drives the relative margin through a logistic loss. No hyperparameter sweep makes this a fair algorithm comparison.  
**Evidence:** `EXP-FRL-013/014`, configs.  
**Avoid:** Concluding DPO is universally stronger.  
**Follow-up:** How would you compare them fairly?

### Q38. Where is reward hacking possible?

**Spoken:** “Anywhere a proxy can be satisfied without a correct repair: fake pass signals, premature finish, valid JSON without semantics, or grader leakage.”  
**Deep:** the project directly discovered an exit-code exploit, showing why reward-channel security is part of ML correctness.  
**Evidence:** `FAILURE_ANALYSIS.md`.  
**Avoid:** Treating reward design separately from systems security.  
**Follow-up:** What adversarial evaluation would you add?

### Q39. What is credit assignment?

**Spoken:** “Determining which actions in a trajectory caused the final reward.”  
**Deep:** exact repair is sparse and delayed; ForgeRL’s fixed completion objectives largely avoid multi-step credit assignment rather than solve it. Process rewards or per-action verifier feedback could help but introduce proxy risks.  
**Evidence:** bounded trajectories versus one-response training data.  
**Avoid:** Claiming the current surrogate trains long-horizon recovery.  
**Follow-up:** How would you build process supervision?

### Q40. What is exploration?

**Spoken:** “Sampling diverse plausible actions to discover successful behavior.”  
**Deep:** qualification uses temperature and three seeds, but adapter evaluation is greedy. A stronger RL loop needs controlled group sampling, diversity diagnostics, and a fixed inference budget.  
**Evidence:** `runner.py` options, evaluation sampler.  
**Avoid:** Treating different random seeds as an adequate exploration strategy.  
**Follow-up:** How would you avoid wasting rollouts?

## 5.6 Evaluation and research-method questions

### Q41. Why exact block match?

**Spoken:** “It is deterministic and conservative for a tiny pilot.”  
**Deep:** score requires exactly the keys `action`, `old`, `new`, exact `replace`, and byte-equivalent blocks. It measures protocol-plus-reference-match, not all semantically correct patches.  
**Evidence:** `evaluate_failure_adapter.py:score`.  
**Avoid:** Calling it a complete software-correctness oracle.  
**Follow-up:** Could there be false negatives?

### Q42. Why three repositories?

**Spoken:** “They demonstrate a repository-separated train/dev/test path within the zero-budget scope.”  
**Deep:** they are insufficient for inference; the experimental unit should be repository/task, not generated token or decoding seed.  
**Evidence:** task list and final report.  
**Avoid:** “Three repositories prove generalization.”  
**Follow-up:** How many tasks are enough?

### Q43. Are the tasks statistically independent?

**Spoken:** “They are distinct repositories, but three hand-selected tasks are not a representative random sample.”  
**Deep:** task-selection bias, historical pretraining contamination, and differing bug difficulty undermine population inference.  
**Evidence:** task construction and absent sampling frame.  
**Avoid:** Applying a simple binomial interval as if representativeness were guaranteed.  
**Follow-up:** Design a sampling frame.

### Q44. What is internal validity?

**Spoken:** “Whether the observed comparison is attributable to the intervention under this experiment.”  
**Deep:** same prompt/decoder/metric helps, but single examples, sequential base-to-adapter mutation, backend conversion, and no replicated training runs leave threats.  
**Evidence:** evaluation and training scripts.  
**Avoid:** Confusing internal with external validity.  
**Follow-up:** What is the strongest internal control?

### Q45. What is external validity?

**Spoken:** “Whether findings generalize to other bugs, repositories, models, and environments.”  
**Deep:** external validity is extremely limited because tasks, model, adapter, hardware, and prompts are narrow.  
**Evidence:** final report scope.  
**Avoid:** Universal conclusions about DPO or coding agents.  
**Follow-up:** What replication would improve it most?

### Q46. What is data leakage here?

**Spoken:** “Information from evaluation tasks or hidden graders entering training, prompts, or tuning decisions.”  
**Deep:** repository splitting reduces direct fine-tuning leakage, but task blocks and historical fixes are explicit, and pretraining contamination is unknown. Repeated tuning after seeing test output would also leak.  
**Evidence:** explicit `TASKS` and frozen artifacts.  
**Avoid:** Claiming “held-out” means unseen by the foundation model.  
**Follow-up:** Would a temporal split help?

### Q47. What is a baseline?

**Spoken:** “The frozen unadapted Qwen under the same prompt, decoder, and metric.”  
**Deep:** a stronger study also needs SFT on random tasks, compute-matched random curriculum, perhaps rejection-sampling and larger-model baselines.  
**Evidence:** evaluation conditions and charter.  
**Avoid:** Comparing methods with different inference budgets.  
**Follow-up:** What is the most important missing baseline?

### Q48. What is an ablation?

**Spoken:** “Remove or vary one component to estimate its contribution.”  
**Deep:** useful ForgeRL ablations include schema strictness, LoRA rank/layers, failure-targeted versus random data, reward terms, trajectory type, KL strength, and inference budget.  
**Evidence:** charter calls for curriculum/reward/inference ablations; only schema intervention is observed.  
**Avoid:** Calling unrelated experiments ablations without controlled equivalence.  
**Follow-up:** Which ablation has highest information value?

### Q49. Why no confidence interval in the report?

**Spoken:** “Because one task per split is too small and not a representative independent sample; a numerical interval could imply unjustified generalization.”  
**Deep:** even the binomial interval is almost uninformative at 0/3, and sampling assumptions are weak.  
**Evidence:** `BENCHMARKS.md`, final report.  
**Avoid:** Saying confidence intervals are impossible; say they are unhelpful/misleading for the intended claim.  
**Follow-up:** What interval would you report in a larger study?

### Q50. Could results be cherry-picked?

**Spoken:** “The repository preserves invalid and negative runs, which reduces but does not eliminate selection risk.”  
**Deep:** stronger protection needs preregistered task sampling, complete run registry, signed artifacts, and reporting every seed and exclusion.  
**Evidence:** experiment directories, failure notes, `EVAL_PLAN.md`.  
**Avoid:** Claiming Git history proves no private discarded runs existed.  
**Follow-up:** How would you preregister the next study?

## 5.7 GGUF, MLX, and local systems

### Q51. What is GGUF?

**Spoken:** “A model file format carrying tensors and metadata, commonly used by local inference engines.”  
**Deep:** this source contains quantized Q4_K tensors plus architecture/tokenizer metadata. ForgeRL verifies a source SHA-256 before conversion.  
**Evidence:** `gguf_backend.py`.  
**Avoid:** Calling GGUF itself an inference algorithm.  
**Follow-up:** What does Q4_K mean conceptually?

### Q52. Why decode GGUF into MLX?

**Spoken:** “Ollama was convenient for inference, but LoRA training needed differentiable tensors and gradients.”  
**Deep:** the backend maps GGUF tensor names to MLX Qwen3 model names, checks shapes/metadata/tokenizer, and uses strict loading.  
**Evidence:** `load_local_gguf`.  
**Avoid:** Claiming the quantized weights remain trained in packed Q4 form; affected tensors are decoded to floating representation.  
**Follow-up:** What memory cost does dequantization add?

### Q53. What was the Q4_K bug?

**Spoken:** “Native MLX Q4_K decoding disagreed with an independent GGUF implementation, so affected tensors were re-decoded.”  
**Deep:** `gguf.GGUFReader` identifies Q4_K tensors and `gguf.dequantize` converts them individually to float16 to bound temporary memory.  
**Evidence:** comments in `gguf_backend.py`, `EXP-FRL-004`.  
**Avoid:** Claiming the repository fixed MLX upstream.  
**Follow-up:** How did you validate the correction?

### Q54. Why hard-code the Ollama blob path?

**Spoken:** “It froze the exact local pilot source, but it is a portability flaw.”  
**Deep:** production code should resolve a configured path, verify the expected digest, and separate machine configuration from source.  
**Evidence:** `gguf_backend.py:SOURCE`.  
**Avoid:** Defending machine-specific absolute paths as good packaging.  
**Follow-up:** How would you refactor it securely?

### Q55. Is MLX mandatory?

**Spoken:** “Only for the recorded differentiable training and numerical LoRA tests; qualification inference uses Ollama and standard-library orchestration.”  
**Deep:** portable CI therefore cannot reproduce the training path.  
**Evidence:** `REPRODUCIBILITY.md`, workflow.  
**Avoid:** Saying GitHub Actions validates GPU training.  
**Follow-up:** How would you add a portable tiny-model integration test?

## 5.8 Advanced architecture questions

### Q56. What is the system’s trusted computing base?

**Spoken:** “The host orchestrator, cases/expected outputs, Docker daemon and host kernel, pinned images, and local model/runtime supply chain.”  
**Deep:** candidate code and model output are untrusted. Narrowing the TCB further would move execution to isolated workers or microVMs and sign grader artifacts.  
**Evidence:** architecture.  
**Avoid:** Saying only the grader is trusted.  
**Follow-up:** How would you attest workers remotely?

### Q57. How would you scale rollout collection?

**Spoken:** “Use a queue, immutable task manifests, autoscaled isolated workers, artifact storage, and a coordinator that deduplicates attempts and records provenance.”  
**Deep:** separate control plane from untrusted execution; assign idempotency keys; stream capped logs; store content-addressed artifacts; monitor reward distributions and infrastructure failure rates.  
**Evidence:** proposed—not implemented.  
**Avoid:** Presenting this as current architecture.  
**Follow-up:** Where would backpressure live?

### Q58. How would you prevent duplicate or biased tasks?

**Spoken:** “Canonicalize repository/commit/issue identities, deduplicate patches and tests, group splits by repository, and freeze a sampling manifest before training.”  
**Deep:** include license, provenance, contamination checks, difficulty strata, and cluster-aware statistics.  
**Evidence:** proposed extension of source-hash/manifest practice.  
**Avoid:** Randomly splitting rows from the same repository.  
**Follow-up:** How do you detect semantic duplicates?

### Q59. How would you store millions of trajectories?

**Spoken:** “Metadata in a transactional index; content-addressed compressed blobs in object storage; immutable manifests link them.”  
**Deep:** partition by model/task/date, redact secrets, set retention, validate schemas, and separate raw sensitive traces from derived training data.  
**Evidence:** proposed.  
**Avoid:** Putting huge raw JSON directly in Git.  
**Follow-up:** How would you support reproducible dataset snapshots?

### Q60. What observability matters?

**Spoken:** “Task success, valid actions, test progression, recovery, finish quality, tokens, latency, sandbox failures, reward distributions, and policy drift.”  
**Deep:** correlate model version, prompt/scaffold, image, worker, repository commit, adapter, and run ID; alert separately on infrastructure and model regressions.  
**Evidence:** charter metrics plus proposed production layer.  
**Avoid:** Monitoring only average reward.  
**Follow-up:** What SLO would you define first?

### Q61. How would you roll back a bad adapter?

**Spoken:** “Keep base and adapters immutable, deploy adapters by version behind evaluation gates, canary traffic, and switch the pointer back.”  
**Deep:** store lineage, compatibility, signed hashes, pre-deployment benchmark results, and trigger thresholds.  
**Evidence:** adapter separation supports this; deployment system is proposed.  
**Avoid:** Merging adapter weights irreversibly before validation.  
**Follow-up:** What if the tokenizer changed?

### Q62. What is the largest current bottleneck?

**Spoken:** “High-quality, diverse, leakage-controlled repair trajectories—not the optimizer code.”  
**Deep:** one pair cannot identify an algorithmic effect; sandbox throughput and local memory also constrain data generation and multi-seed training.  
**Evidence:** one-example/pair configs and final report.  
**Avoid:** Assuming more gradient steps solve data scarcity.  
**Follow-up:** How would you prioritize data quality?

## 5.9 Adversarial and hostile questions

### Q63. None of the models fixed a task. Did the project fail?

**Spoken:** “The repair-improvement hypothesis was not supported in this pilot. The project still succeeded at building and validating the measurement, sandbox, and local training mechanics, and it exposed that proxy optimization did not transfer.”  
**Deep:** separate engineering objectives from scientific outcomes. A negative capability result is valid only at this narrow scale.  
**Evidence:** `FINAL_REPORT.md`, `EXP-FRL-012/015/016`.  
**Avoid:** Evading the zero score or calling it success.  
**Follow-up:** Why should I care?

### Q64. Is this really reinforcement learning?

**Spoken:** “Not as a full online RL system. SFT and DPO are offline; the GRPO component is explicitly a clipped two-candidate surrogate using verifier-relative rewards.”  
**Deep:** it implements real policy-ratio optimization but lacks group sampling and iterative environment interaction.  
**Evidence:** `alignment_pilot.py`.  
**Avoid:** Fighting over labels; state mechanics exactly.  
**Follow-up:** Rename the project?

### Q65. Why call it GRPO at all?

**Spoken:** “Because the surrogate tests group-relative signed advantages and clipped policy ratios, but every report qualifies it as a surrogate.”  
**Deep:** a clearer production name might be “two-candidate clipped verifier-reward objective” to avoid ambiguity.  
**Evidence:** README and metrics interpretation.  
**Avoid:** Omitting the qualifier.  
**Follow-up:** What is missing from canonical GRPO?

### Q66. Are three tasks scientifically meaningful?

**Spoken:** “They are useful as integration tests and a feasibility pilot, not as population-level scientific evidence.”  
**Deep:** the confidence interval is huge and task selection is not representative.  
**Evidence:** final report explicitly says underpowered.  
**Avoid:** “Three repositories are enough because they are disjoint.”  
**Follow-up:** Why publish the number?

### Q67. Did you cherry-pick the margin?

**Spoken:** “The margin is reported as an optimizer diagnostic beside the zero repair outcome, not as the headline capability metric.”  
**Deep:** all relevant artifacts and the malformed DPO output are preserved; a future study should preregister primary/secondary metrics.  
**Evidence:** `EXP-FRL-013/015`, failure note.  
**Avoid:** Defending the margin as equivalent to quality.  
**Follow-up:** What should the primary metric be?

### Q68. Could this just be overfitting?

**Spoken:** “Yes—the evidence strongly supports narrow fitting and provides no evidence against overfitting.”  
**Deep:** one example/pair, large margin movement, zero transfer, and malformed generation are exactly why a larger dataset and validation curve are needed.  
**Evidence:** training/evaluation artifacts.  
**Avoid:** Claiming the frozen base prevents adapter overfitting.  
**Follow-up:** How would you detect it earlier?

### Q69. How is this different from a wrapper around Qwen?

**Spoken:** “The model is a component; the research contribution is the constrained agent protocol, adversarial grader, isolated execution, evidence lineage, differentiable local conversion, post-training mechanics, and controlled evaluation.”  
**Deep:** acknowledge the base model and MLX/Ollama libraries; originality lies in integration, controls, discovered failure modes, and experiment framing.  
**Evidence:** source modules and failure analysis.  
**Avoid:** Claiming novel foundation-model algorithms.  
**Follow-up:** Which component is most reusable?

### Q70. Why should anyone trust your sandbox?

**Spoken:** “They should trust only the tested properties, not an absolute security claim.”  
**Deep:** enumerate controls and regression tests, disclose shared-kernel and worker-metadata limitations, and propose microVMs for stronger isolation.  
**Evidence:** `test_runner.py`, requirements.  
**Avoid:** “Docker makes it secure.”  
**Follow-up:** Show me one test that matters.

### Q71. The nested README says no weights were trained. Which story is true?

**Spoken:** “That nested README is stale. The later immutable experiments demonstrate adapter training, while the broader charter hypothesis remains incomplete.”  
**Deep:** point to timestamps/run lineage, metrics, changed tensors, and reload checks. Commit a documentation correction before presenting publicly.  
**Evidence:** `forgerl/README.md` versus `EXP-FRL-011`–`014`.  
**Avoid:** Pretending there is no contradiction.  
**Follow-up:** What is your source-of-truth policy?

### Q72. Why did DPO make malformed repetition?

**Spoken:** “The narrow one-pair update likely distorted generation, but the experiment does not isolate a single cause.”  
**Deep:** candidates include overfitting, high effective update strength, inadequate regularization, final-layer-only adaptation, length-normalized objective, and decoding interactions.  
**Evidence:** malformed response in `EXP-FRL-015`.  
**Avoid:** A definitive causal diagnosis.  
**Follow-up:** What experiment separates the causes?

### Q73. Why not tune until one task passed?

**Spoken:** “Because tuning on the three-task evaluation would convert it into development data and destroy the meaning of the result.”  
**Deep:** use a larger dev set for hyperparameters, freeze the test manifest, and evaluate once or report all sequential looks with correction.  
**Evidence:** frozen-evaluation principle in charter.  
**Avoid:** Optimizing for a demo by leaking the test answer.  
**Follow-up:** How do you handle an accidental test leak?

### Q74. Isn’t exact match unfair?

**Spoken:** “It is intentionally strict and can reject correct alternatives, so I describe it as exact-block repair, not semantic repair.”  
**Deep:** follow-up work should run patches against hidden tests and use exact match only as a high-precision diagnostic.  
**Evidence:** score function.  
**Avoid:** Claiming zero semantic solutions with certainty.  
**Follow-up:** Could any recorded response be semantically correct?

### Q75. Was the model actually Q4 during training?

**Spoken:** “The source was the pinned Q4_K GGUF, but affected packed tensors were decoded to float16 for MLX training.”  
**Deep:** this is not QLoRA training directly over a 4-bit quantized base in the usual sense.  
**Evidence:** `gguf_backend.py`.  
**Avoid:** “I trained the 4-bit weights.”  
**Follow-up:** How would true QLoRA differ?

### Q76. Can `scripts/verify.py` prove the experiments happened?

**Spoken:** “No. It checks that published JSON claims are internally consistent; it cannot independently recreate excluded weights or establish provenance.”  
**Deep:** `verify_runs.py` is stronger locally because it checks binaries and hashes, but trusted execution, signed logs, and external replication would provide stronger evidence.  
**Evidence:** script docstrings and behavior.  
**Avoid:** Calling it experimental reproduction.  
**Follow-up:** What would make results independently reproducible?

## 5.10 Behavioral and ownership questions

### Q77. What was your hardest debugging incident?

**Spoken:** “The exit-code grader accepted `os._exit(0)`, revealing that an apparently passing test could be a reward exploit.”  
**Deep:** explain detection, reproduction, severity, redesign, invalidation of historical results, and regression test. This demonstrates security and research integrity together.  
**Evidence:** `FRL-FAIL-001`.  
**Avoid:** Describing only the fix without the impact on prior evidence.  
**Follow-up:** What process change followed?

### Q78. Describe a second hard bug.

**Spoken:** “An output-flooding candidate caused cleanup to hang because the Docker client pipe remained attached and unread.”  
**Deep:** close/kill the attached process output before bounded container removal; preserve cleanup timeout as failure.  
**Evidence:** `FRL-FAIL-004`, grader implementation.  
**Avoid:** Calling output caps sufficient without cleanup design.  
**Follow-up:** How would async I/O improve this?

### Q79. How did you respond to a failed hypothesis?

**Spoken:** “I kept the zero results and narrowed the conclusion instead of tuning on the evaluation set.”  
**Deep:** objective improvements became a diagnostic finding, not a substituted success metric.  
**Evidence:** final report and failure artifacts.  
**Avoid:** Reframing the original hypothesis after seeing results.  
**Follow-up:** What would make you stop the research line?

### Q80. What are you most proud of?

**Spoken:** “The system catches when a clean training curve tells a false capability story.”  
**Deep:** cite the combination of security hardening, artifact lineage, and honest negative reporting.  
**Evidence:** full evidence map.  
**Avoid:** Choosing a flashy metric without qualification.  
**Follow-up:** What would you improve first?

---

# 6. Code-review preparation and exercises

## 6.1 `runner.py`

**Inputs/outputs:** CLI config and task definitions enter; immutable configs, episode JSON, and metrics leave. `episode` transforms model actions and observations; `grade` returns structured pass/failure data.

**Strengths:** strict path/action validation, no host execution, host semantic comparison, bounded reads, explicit infrastructure failures, environment/source capture.

**Technical debt:** orchestration, HTTP client, sandbox, and grading share one large module; dynamic import paths assume execution from `forgerl`; no static types; Docker cleanup remains complex; cases are matched by list equality; synchronous loop limits throughput.

**Production improvements:** typed configs/results, JSON-schema validation library, adapter interfaces for model and sandbox backends, content-addressed task IDs, async process supervision, structured logs, seccomp/microVM option, explicit infrastructure-versus-policy outcome taxonomy.

**Review question:** “Why identify a trusted test suite by equality against task lists?”  
**Answer:** It prevents caller-supplied arbitrary expected data but is brittle and O(number of suites). Use an opaque host-generated suite ID mapped to an immutable manifest.

## 6.2 `gguf_backend.py`

**Inputs/outputs:** pinned GGUF and tokenizer/config directory enter; loaded MLX model/tokenizer leave.

**Invariants:** source digest, Qwen3 architecture metadata, dimensions, tied embeddings, vocabulary IDs, supported names, unpacked dtypes, unique target names, and strict model shapes.

**Strengths:** fails closed on disagreement and decodes Q4_K tensors individually to bound transient memory.

**Technical debt:** absolute machine path, architecture-specific mapping, no automated small-fixture test, imports heavy optional dependencies inside runtime, source format and runtime compatibility are manually curated.

**Review question:** “Why is strict tensor loading critical?”  
**Answer:** Non-strict loading could silently omit or mis-map weights, producing plausible but invalid model behavior.

## 6.3 `adapter_pilot.py`

**Strengths:** offline environment flags, hash verification, bounded steps, prompt masking, frozen-base checks, zero-init check, tensor hashes, adapter save/reload, finite-loss guard.

**Debt:** single training example, hard-coded optimizer/hyperparameters, no validation set, no gradient clipping, one hardware path, memory limit nearly reaches system capacity, dense script structure.

**Review question:** “Why compare only final-token logits for zero-init/reload?”  
**Answer:** It is a compact equivalence sentinel but not exhaustive. Stronger validation should compare logits across all response positions or hashes of adapter tensors after reload.

## 6.4 `alignment_pilot.py`

**Strengths:** explicit frozen reference values, bounded runs, objective/config persistence, changed-tensor allowlist, exact margin reload.

**Debt:** minified style, one fixed pair, fixed advantages, no group sampling, no explicit KL in surrogate, no validation, no checkpointing/recovery, average-token score deviates from common sequence-level DPO.

**Review question:** “Why is `min` correct for negative advantages?”  
**Answer:** In the negative-advantage case, excessive probability increase makes `ρA` more negative; the clipped surrogate selects the more conservative/worse term in the maximization formulation, represented with a leading negative in the minimized loss.

## 6.5 `evaluate_failure_adapter.py`

**Strengths:** frozen task list, same prompts and greedy decoding, transparent exact scorer, raw responses retained.

**Debt:** exact string brittleness, one task per split, sequentially mutates the in-memory model when loading the adapter, no repeated seeds/pass@k, no actual patch application in this evaluator, no confidence reporting.

**Review question:** “Could loading an adapter mutate the base used earlier?”  
**Answer:** Base rows are generated first, then the adapter is loaded. That ordering preserves recorded base outputs, but clearer isolation would reload separate base and adapter model instances.

## 6.6 Practical exercises

1. **Add a safe search tool:** define query/path enums, prohibit regex denial-of-service or use a bounded engine, cap matches/bytes, execute against an allowlisted snapshot, and test traversal, huge files, binary files, and pathological patterns.
2. **Add a repair task:** pin repository and buggy/fixed commits, store license, freeze target/tests, prove buggy fails and fixed passes, assign split by repository, record hashes, and avoid using it for tuning after test freeze.
3. **Add a grader:** keep oracle data host-side, define exact typed result semantics, test adversarial early exits/fake results/timeouts, distinguish infrastructure failure, and version the grader.
4. **Add a reward component:** state causal purpose, scale, maximum contribution, gaming path, and ablation plan. Do not add a proxy without an adversarial test.
5. **Replace Ollama backend:** implement a model-client interface preserving messages, schema, decoding parameters, token accounting, model digest, and raw responses; run golden protocol tests.
6. **Improve replay determinism:** capture tokenizer/template, runtime versions, hardware, environment, exact model/image hashes, decoding implementation, RNG state, and complete observations. Still disclose nondeterministic kernels.
7. **Diagnose Docker failure:** classify image missing, daemon unavailable, permission error, container timeout, output cap, cleanup timeout, test failure, or worker response invalidity before blaming the policy.
8. **Prevent grader leakage:** never mount expected outputs; use opaque suite IDs; minimize test feedback; separate public from hidden workers; scan traces and training datasets for hidden content.
9. **Improve coverage:** add property-based `same_json`/path tests, malformed worker JSON, Unicode/size boundary tests, Docker process-fork attacks, symlinks, disk exhaustion, model HTTP malformed responses, and end-to-end tiny-model CI.

---

# 7. Results defence

## 7.1 Results table

| Condition | Training evidence | Exact repair | Defensible statement |
|---|---|---:|---|
| Frozen base | No update | 0/3 | No observed exact repair under greedy frozen prompts. |
| SFT LoRA | Loss 1.529 → 0.125 on one response | 0/3 | Mechanics and memorization worked; no transfer observed. |
| DPO LoRA | Margin 0.382 → 4.684 on one pair | 0/3 | Preference objective moved strongly; capability did not improve. |
| GRPO-style surrogate LoRA | Margin 0.382 → 1.220 on two candidates | 0/3 | Clipped relative-reward mechanics worked; no repair gain. |

## 7.2 What the margins prove

- Gradients flowed through the decoded local model into LoRA tensors.
- The chosen/rejected relative score changed in the intended direction.
- Only expected adapter tensors changed according to the recorded audit.
- Saved adapters reproduced the recorded margin after reload.

## 7.3 What they do not prove

- That generated patches became more correct.
- That DPO is better than the surrogate.
- That failure-derived data beats random data.
- That the policy improved on unseen repositories.
- That the reward function is robust at scale.
- That the result is statistically significant.
- That the same behavior holds for other models or hardware.

## 7.4 Strong hostile-answer script

“The zero out of three is the primary capability result. I do not replace it with the training margin. The margin tells me the optimization path was real and functioning; the zero repairs tell me that the learned preference was too narrow or otherwise failed to transfer. With three hand-selected tasks I cannot distinguish data scarcity, adapter capacity, objective choice, backend effects, prompt design, or ordinary variance. The next study needs a frozen task manifest with dozens to hundreds of independent repository tasks, compute-matched failure-targeted and random curricula, multiple training seeds, actual patch-and-test grading, and preregistered primary metrics.”

---

# 8. Production and scaling design

## 8.1 Proposed architecture

```text
Dataset registry ──► task manifest/version ──► rollout queue
       │                                         │
       │                                isolated worker pool
       │                              (microVM/container hosts)
       │                                         │
       └── licenses/provenance             capped artifacts
                                                 │
                                         host-side graders
                                                 │
                         ┌───────────────────────┴───────────────────┐
                         ▼                                           ▼
                  trajectory lake                           metrics/lineage DB
                         │                                           │
                  dataset builder                                   dashboards
                         │
              SFT / preference / online-RL trainers
                         │
                   model registry
                         │
             offline gates ─► canary ─► serving
                         │
                  rollback pointer
```

## 8.2 Staged roadmap

1. **Research validity:** 50–100+ tasks across many repositories; frozen manifests; test-based semantics; contamination review; multiple seeds; compute-matched baseline.
2. **Data engine:** normalized trajectories, failure taxonomy, pair-quality review, dataset versioning, privacy/license gates.
3. **Parallel rollout:** idempotent queue, isolated workers, artifact store, retry policy that never drops failures, observability.
4. **Training platform:** GPU trainer, distributed checkpoints, gradient/optimizer telemetry, reference-policy versioning, held-out regression suite.
5. **Security hardening:** microVM boundary, minimal signed images, secretless workers, egress control, patch cadence, supply-chain SBOM, red-team corpus.
6. **Deployment:** registry, evaluation policy, human review for code changes, canaries, rollback, incident runbooks, audit retention.

## 8.3 Cost categories

Do not quote exact numbers without workload assumptions. Model costs from: GPU training hours; rollout inference tokens; CPU/memory sandbox minutes; object storage and egress; artifact indexing; observability retention; security scanning; engineer/reviewer time; benchmark licensing/compliance; idle capacity and failed runs. The largest variable is usually rollout and training compute multiplied by candidates, tasks, seeds, and ablations.

## 8.4 Bottlenecks

- Reliable, diverse tasks with legal provenance.
- Correct graders and protection against reward hacking.
- Sandbox startup and repository dependency setup.
- Long-context inference throughput.
- Sparse reward and low successful-trajectory yield.
- Experiment multiplicity across methods, seeds, and hyperparameters.
- Human review of ambiguous or security-sensitive repairs.

---

# 9. Mock interviews

## 9.1 Thirty-minute screen

**Flow:** 3-minute overview; 7 minutes architecture; 7 minutes result; 7 minutes one deep topic; 6 minutes candidate questions.

**Questions:** What problem? Why JSON? How is code isolated? What did SFT/DPO change? Why 0/3? What would you do next?

**Scoring (10):** clarity 2; accurate architecture 2; result honesty 2; one technical depth area 2; limitations/next experiment 2.

**Red flags:** says DPO improved repair; calls surrogate full GRPO; says Docker is fully secure; hides sample size.

**Exceptional:** connects reward-channel security with research validity and distinguishes proxy, mechanism, and outcome.

## 9.2 Sixty-minute senior ML-systems interview

**Flow:** 5 overview; 15 code/data flow; 10 SFT/LoRA math; 10 DPO/surrogate; 10 sandbox; 10 experiment redesign.

**Core questions:** derive assistant-only CE; calculate LoRA parameters; explain the reference margin; trace one test action; threat-model the worker; design a 100-task study; debug malformed DPO output.

**Scoring (20):** systems correctness 4; ML math 4; security 4; experimentation 4; communication/ownership 4.

**Exceptional:** identifies average-token DPO as a design choice, the sequential model load as clarity debt, and CI’s incomplete integration coverage without prompting.

## 9.3 Ninety-minute staff architecture interview

**Prompt:** “Turn ForgeRL into a multi-tenant platform producing 10 million safe trajectories monthly.”

**Expected areas:** control/data planes; task registry; queues and idempotency; sandbox pool; content-addressed storage; lineage; autoscaling/backpressure; identity/secrets; egress; SLOs; human review; model registry; evaluation gates; cost model; incident response.

**Cross-questions:** How do you stop poisoned tasks? What if grader version changes? How do you replay after image deletion? How do you allocate GPU versus CPU bottlenecks? What is the blast radius of a container escape? How do you delete sensitive traces while preserving experiment lineage?

**Scoring (25):** requirements/trade-offs 5; architecture 5; security/reliability 5; ML/data governance 5; evolution/cost 5.

**Red flags:** one central service executes untrusted code; arbitrary outbound internet; mutable datasets; retrying failures until success without accounting; no tenant boundary.

## 9.4 Research-defence interview

**Opening attack:** “You have zero successes and three tasks. There is no research result.”

**Ideal response:** agree that no general capability effect is established; defend the negative feasibility observation and audited mechanics; identify threats; propose a preregistered powered design.

**Questions:** experimental unit; selection bias; contamination; primary endpoint; power; multiple comparisons; compute matching; seed hierarchy; stopping rule; exact match false negatives; DPO pair construction; reward validity.

**Scoring:** rewards epistemic honesty. Penalize substituting margin for success or treating seeds on one task as independent tasks.

## 9.5 Security-review interview

**Scenario:** candidate code is actively malicious and tenants are mutually hostile.

**Questions:** draw trust boundaries; exploit original grader; container escape response; hidden-test exfiltration; output flood; fork bomb; disk bomb; dependency attack; artifact poisoning; secrets; signed images; audit logs.

**Ideal conclusion:** current controls are appropriate for a local feasibility pilot but insufficient for hostile multi-tenancy; recommend isolated worker hosts/microVMs, secretless jobs, strict egress, signed minimal images, quotas, monitoring, and incident containment.

---

# 10. Difficult cross-question chains

## Chain 1 — “DPO worked”

1. **What worked?** The one-pair objective and margin.
2. **Did repair improve?** No, 0/3 before and after.
3. **Then why report margin?** To prove the update was mechanically effective and diagnose proxy/outcome separation.
4. **Could it be overfit?** Yes; that is the leading interpretation, not ruled out.
5. **How would you prove transfer?** Larger repository-disjoint test set, multiple training seeds, fixed test, task-level uncertainty.

## Chain 2 — “GRPO”

1. **Is it full GRPO?** No, a two-candidate clipped surrogate.
2. **What is real?** LoRA gradients, policy ratios, signed relative advantages, clipping, verifier-derived preference.
3. **What is missing?** Live group sampling, rollout refresh, many prompts, online verification, robust KL control.
4. **Why useful?** It validates a local differentiable mechanics path cheaply.
5. **What would you rename it?** Two-candidate clipped verifier-reward LoRA pilot.

## Chain 3 — Sandbox

1. **Why Docker?** Affordable defense-in-depth locally.
2. **Can it escape?** Shared-kernel vulnerabilities are residual risk.
3. **Why trust the grade?** Expected values and comparison stay on host; outputs are validated.
4. **What can still be faked?** Worker mutation/alias metadata.
5. **Production boundary?** MicroVMs/isolated hosts plus signed images, secretless jobs, egress control, monitoring.

## Chain 4 — Statistics

1. **0/3 means zero capability?** No; zero observed successes.
2. **95% interval?** Extremely wide; rule-of-three upper bound is approximately 1 at n=3.
3. **Why no interval?** It would imply representativeness the selected tasks do not have.
4. **What is the experimental unit?** Independent repository-task, with training seed hierarchy.
5. **How many tasks?** Determine by power analysis for a preregistered minimum effect and clustered variance.

## Chain 5 — Schema intervention

1. **Invalid actions fell to zero; did the model improve?** No, the scaffold changed.
2. **Is that cheating?** Not during harness qualification if transparently reported.
3. **Could it contaminate results?** Yes if compared as a training effect.
4. **How control it?** Freeze scaffold across all model conditions.
5. **What does it teach?** System capability depends on model-plus-scaffold, so both must be versioned.

## Chain 6 — Exact match

1. **Why exact?** Deterministic conservative pilot.
2. **False negatives?** Semantically correct alternative patches can fail.
3. **Then is 0/3 trustworthy?** Trustworthy for exact-block success, not all semantic correctness.
4. **Better metric?** Apply patch and run hidden tests, plus patch-scope/quality diagnostics.
5. **Security issue?** Test harness must resist bypass and keep expected behavior secret.

## Chain 7 — Local model identity

1. **Same Qwen in Ollama and MLX?** Same pinned GGUF source and checked tokenizer mapping.
2. **Bitwise same output?** Not claimed; kernels and decoding paths differ.
3. **Why convert?** Gradients require a differentiable backend.
4. **What changed in conversion?** Q4_K tensors decoded to float16 and names mapped.
5. **Threat to validity?** Backend behavior is a confound; cross-backend logit/generation comparisons should be expanded.

## Chain 8 — Reproducibility

1. **Can I rerun from GitHub alone?** Portable checks yes; exact training no, because model/adapters and hardware path are external/excluded.
2. **Then reproducible?** Partially: artifacts and procedures are reproducible; full independent reproduction requires the pinned model and compatible environment.
3. **What is verified?** JSON consistency, source snapshots/hashes, expected metrics.
4. **What is not?** That published metrics came from untampered execution.
5. **Improve?** Signed attestations, containerized dependencies, released adapters where licensing permits, external replication.

## Chain 9 — Reward hacking

1. **Example?** `os._exit(0)` fooled exit-code grading.
2. **Why did it matter?** False positive reward would train exploitation.
3. **Fix?** Host-held semantic comparison of typed outputs.
4. **Remaining proxies?** validity/finish/step rewards and worker metadata.
5. **General lesson?** Reward infrastructure is security-critical model-training code.

## Chain 10 — Ownership

1. **What did you build?** Name exact modules and decisions you can explain.
2. **What libraries did you rely on?** Qwen, Ollama, Docker, MLX/MLX-LM, GGUF.
3. **What is original?** Integration, controls, experiment lineage, failure analysis, and bounded study design.
4. **What would you rewrite?** Stale docs, typed modularity, portable backend config, larger evaluation.
5. **Show proof of understanding.** Trace one action or derive one loss from code without memorized marketing language.

---

# 11. Prioritized study plan

## Seven-day intensive plan

1. **Day 1:** Memorize the 30-second, two-minute, and ten-minute walkthroughs. Trace `runner.py` end to end.
2. **Day 2:** Derive CE, LoRA, DPO, policy gradient, normalized advantage, clipped ratio, KL, and pass@k by hand.
3. **Day 3:** Study `adapter_pilot.py`, `alignment_pilot.py`, and all `EXP-FRL-011`–`016` metrics. Practice explaining what each number does not mean.
4. **Day 4:** Threat-model `grade`; reproduce the exit-code and output-flood stories; compare Docker, gVisor, and microVMs conceptually.
5. **Day 5:** Design the 100-task multi-seed study and production rollout architecture on a whiteboard.
6. **Day 6:** Answer Q1–Q80 aloud. Record yourself; remove claims not backed by a file or artifact.
7. **Day 7:** Run one 60-minute mock and one hostile research defence. Practice opening files and explaining code live.

---

# 12. One-page cheat sheet

## Core story

ForgeRL is a local testbed for converting coding-agent failures into post-training signal. Qwen emits bounded JSON actions; candidate code runs in hardened Docker; expected outputs stay on the host; trajectories and failures are preserved. Real LoRA SFT/DPO/clipped-surrogate updates worked mechanically, but all methods remained 0/3 on frozen exact repository repairs.

## Numbers

- Qualification after schema hardening: **3/18**, with **0 invalid actions out of 93**.
- Loose-schema predecessor: **66 invalid actions out of 125**.
- SFT: **1.529 → 0.125** loss over 20 updates.
- Trainable LoRA parameters: **40,960**; four adapter tensors; base frozen.
- DPO margin: **0.382 → 4.684**.
- GRPO-style surrogate margin: **0.382 → 1.220**.
- Exact repairs: **base 0/3; SFT 0/3; DPO 0/3; surrogate 0/3**.
- Paid API/cloud spend recorded: **₹0 / $0**; local resource cost still exists.

## Equations

- CE: `-mean log pθ(correct next token)`.
- LoRA: `Wx + sBAx`; parameters `r(din+dout)` per matrix.
- DPO: `softplus(-β[(cθ-rθ)-(cref-rref)])`.
- Advantage: `(reward-mean)/std`.
- Ratio: `exp(logπθ-logπold)`.
- Clipped objective: `min(ρA, clip(ρ,1-ε,1+ε)A)`.
- KL: `Eπθ[logπθ-logπref]`.
- pass@k: `1-C(n-c,k)/C(n,k)`.

## Files to know cold

`README.md`; `forgerl/PROJECT_CHARTER.md`; `forgerl/runner.py`; `forgerl/worker.py`; `forgerl/test_runner.py`; `forgerl/FAILURE_ANALYSIS.md`; `forgerl/gguf_backend.py`; `forgerl/training_math.py`; `forgerl/adapter_pilot.py`; `forgerl/alignment_pilot.py`; `forgerl/evaluate_failure_adapter.py`; `forgerl/FINAL_REPORT.md`; `scripts/verify.py`.

## Ten strongest talking points

1. Found and fixed a reward-channel exploit rather than hiding it.
2. Host-held semantic grading separates untrusted execution from truth.
3. Defense-in-depth sandbox controls have targeted regression tests.
4. Strict schemas measurably removed protocol errors.
5. Run artifacts preserve source/config/model/image lineage.
6. Corrected and validated a local GGUF-to-differentiable-MLX path.
7. Verified LoRA with multiple independent frozen-base/reload checks.
8. Implemented real DPO and clipped policy-ratio mechanics locally.
9. Kept the negative 0/3 result as primary.
10. Can explain exactly why optimizer success is not capability success.

## Ten limitations to volunteer

1. One task per train/dev/test repository block.
2. One SFT example and one preference pair.
3. GRPO is only a two-candidate surrogate.
4. Exact string metric can reject semantic alternatives.
5. No powered, compute-matched curriculum comparison.
6. Unknown foundation-model pretraining contamination.
7. Local Apple/MLX path limits portability.
8. Docker is not hostile multi-tenant isolation.
9. Portable CI does not run full Docker/MLX integration.
10. Nested `forgerl/README.md` is stale.

## Claims never to make

- “ForgeRL improved repository repair.”
- “DPO achieved a 4.684 repair score.”
- “We implemented full GRPO.”
- “The research hypothesis was proven or disproven.”
- “Three tasks establish generalization.”
- “Docker makes arbitrary code completely safe.”
- “The evaluation has no leakage.”
- “The Q4 GGUF stayed quantized during LoRA training.”
- “CI reproduces the complete training pipeline.”
- “Zero paid spend means zero total cost.”
- “The repository proves who authored every line.”
- “No correct semantic patch was generated”—the exact metric proves only no exact reference repair.

## Twenty highest-probability questions

1. What is ForgeRL?
2. Walk me through one episode.
3. Why strict JSON?
4. Why Docker?
5. How are hidden graders protected?
6. What was the `os._exit(0)` exploit?
7. What is LoRA and why use it?
8. How did you verify the base was frozen?
9. What is assistant-only cross-entropy?
10. Explain DPO and beta.
11. What does the preference margin mean?
12. Is this full GRPO?
13. Why did proxy metrics improve but repair stay zero?
14. Is 0/3 useful?
15. What threatens validity?
16. How would you design the next experiment?
17. How would you make the sandbox production-safe?
18. What was the GGUF decoding issue?
19. What did you personally build and learn?
20. What would you change first?

## Final readiness checklist

- [ ] I can give 30-second, 2-minute, and 10-minute versions without exaggeration.
- [ ] I can trace `runner.py` from model request to hidden result.
- [ ] I can explain every Docker flag and at least three residual risks.
- [ ] I can derive CE, LoRA, DPO, advantages, clipping, KL, and pass@k.
- [ ] I can explain why the GRPO component is a surrogate.
- [ ] I know every headline metric and its file.
- [ ] I can defend 0/3 without calling it either universal failure or success.
- [ ] I can identify internal validity, external validity, and leakage threats.
- [ ] I can design a powered follow-up and compute-matched baseline.
- [ ] I can acknowledge the stale nested README immediately.
- [ ] I can whiteboard a production rollout architecture and trust boundaries.
- [ ] I can answer hostile questions calmly and with file-backed evidence.

---

# 13. Repository evidence index

| Evidence | Location |
|---|---|
| Public project summary | `README.md` |
| Research hypothesis, users, falsifiers, non-goals | `forgerl/PROJECT_CHARTER.md` |
| Qualification protocol | `forgerl/EVAL_PLAN.md` |
| Security/feasibility requirements | `forgerl/REQUIREMENTS.md` |
| Qualification results | `forgerl/BENCHMARKS.md` |
| Failure taxonomy | `forgerl/FAILURE_ANALYSIS.md` |
| Reproducibility limits | `forgerl/REPRODUCIBILITY.md` |
| Agent, grader, persistence | `forgerl/runner.py` |
| Sandbox/protocol regressions | `forgerl/test_runner.py` |
| GGUF decoding and MLX mapping | `forgerl/gguf_backend.py` |
| SFT objective and pilot | `forgerl/training_math.py`, `forgerl/adapter_pilot.py` |
| DPO and surrogate objectives | `forgerl/alignment_math.py`, `forgerl/alignment_pilot.py` |
| Exact repair evaluation | `forgerl/evaluate_failure_adapter.py` |
| SFT evidence | `forgerl/experiments/EXP-FRL-011`, `EXP-FRL-012` |
| DPO evidence | `forgerl/experiments/EXP-FRL-013`, `EXP-FRL-015` |
| Surrogate evidence | `forgerl/experiments/EXP-FRL-014`, `EXP-FRL-016` |
| Final bounded conclusion | `forgerl/FINAL_REPORT.md` |
| Publishable consistency check | `scripts/verify.py` |
| Full local artifact audit | `scripts/verify_runs.py` |

The best interview posture is precise confidence: the engineering is real, the optimizer mechanics are real, the negative repair result is real, and the broad research claim remains untested.
