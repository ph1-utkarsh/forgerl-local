# Local execution decision — 2026-09-20

User directive: complete the three projects using local resources; no paid calls.

- Cloud GPU/API budget: exactly zero. No paid endpoint or automatic model download.
- Available inference: Ollama 0.34.0, `qwen3:4b-instruct-2507-q4_K_M` (4B, Q4_K_M, Apache-2.0), and `qwen3:4b`.
- Local development: Python 3.9.6, PyTorch 2.8.0, Transformers 4.27.4. MPS initially reported unavailable inside the sandbox; an approved diagnostic outside it confirmed `mps_built=True` and `mps_available=True`. GPU jobs require the corresponding execution permission. Docker engine 29.5.2 and existing Python images are available.
- Use existing Docker Python image by immutable image ID. No host execution of model patches. No outbound network in task containers.
- Model training, GPU kernel results, multimodal capability, and generalization remain unproven. Text-only Qwen cannot establish vision results. Ollama's serving endpoint is not a training implementation.
- Human time: asynchronous development, no required weekly commitment; calendar remains an estimate.
- License default: original fixtures and permissive dependencies. Publication remains a separate approval step.

Stage 0 can close for a bounded feasibility program. Its first experiment tests environment/grader and local inference feasibility. It does not certify that all original completion criteria are achievable with this hardware.
