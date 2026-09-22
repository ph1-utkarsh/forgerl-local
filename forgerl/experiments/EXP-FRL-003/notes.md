# Existing local Qwen: five-step adapter mechanics pilot

Source is the installed Ollama GGUF blob, whose SHA-256 is recorded and verified. MLX core decodes unsupported GGUF quantization to FP16; the explicit dense-Qwen3 mapping checks metadata, tokenizer IDs, parameter names and shapes. The original file is never modified. No additional large checkpoint was required.

Five assistant-masked SFT updates on one synthetic list-action example trained 40,960 LoRA parameters in the final transformer layer. This is an engineering feasibility check, not a curriculum or generalization experiment. The example contains no qualification task solution.

Measured: loss 16.45125 before updates and 5.60929 after five updates; all frozen base tensor hashes unchanged; all four adapter tensors changed; fresh model/adapter reload had zero maximum absolute error in the checked final-position logits. Peak allocator memory reported 10,742,614,704 bytes (about 10.005 GiB), slightly above the nominal 10 GiB allocator setting. Treat that setting as an allocator budget, not a hard process/RSS ceiling. Total pilot time: 61.40 seconds including verification and reload.

Important: these checks prove update/save/reload mechanics. They do not yet prove the decoded model matches Ollama inference. EXP-FRL-004 separately checks short generations. No improved coding-capability claim is warranted.
