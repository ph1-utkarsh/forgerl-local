# Local training backend feasibility

MLX 0.32.2 on Apple Metal passed a scalar gradient test. Loss fell from 18.666667938 to 0.00006472156 across ten steps. This only validates device/autodiff operation. It is not model training or capability evidence.

The sandbox hid MPS availability; approved execution outside it exposed the GPU. The reproducible command is `.venv/bin/python forgerl/probe_mlx.py --output <fresh-output-path>` with Apple GPU permission.

Installed MLX LM 0.31.3 standard `load_model` searches for `model*.safetensors`; the Ollama model is a GGUF blob. No drop-in training path for that exact blob has been validated. Options: a separately pinned free MLX checkpoint of the same base model, or a carefully validated conversion. Prefer the standard checkpoint path over an unverified conversion.

Next real training acceptance: load a pinned pretrained checkpoint, attach adapters, perform an optimizer step, verify adapter weights changed while base weights stayed frozen, persist/reload the adapter, and reproduce logits. Then run an actual memory/step-time pilot. Full evaluation gates still precede research training.
