# Blockers

- RESOLVED 2026-09-21: Docker's credential helper stalled on `python:3.8-slim`; an anonymous Docker config acquired digest `sha256:1d5283...a613f` without credentials or paid services.

## Current — 2026-09-20

Budget/time questions below are CLOSED by local-only, zero-paid-spend authorization and asynchronous work assumptions. Do not ask for paid compute again.

Open: local differentiable training backend/checkpoint (MLX under investigation); external repository-disjoint dataset and power analysis; adversarial trust in mutation/alias metadata. Ollama inference is not SFT/RL. Helix CUDA/Triton measurements remain unavailable on this hardware. Historical bootstrap blockers follow.

## BLK-FRL-001 — Resource envelope

**Why it matters:** model size, method, seed count, benchmark size, and statistical power cannot be made realistic without budget and GPU availability.  
**Evidence:** verified local machine has 16 GB unified memory and no CUDA GPU.  
**Options:** (A) local-only tiny-model research; (B) capped rental GPU budget; (C) existing remote GPU access.  
**Recommendation:** choose a firm monthly/total cap and available GPU class; default to a 1B–3B single-GPU pilot.

## BLK-FRL-002 — Operating constraints

Weekly hours and acceptable model/data license families are unknown. These affect scope and public release eligibility.
