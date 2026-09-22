# Qualification disposition

Five-step, single-example adapter mechanics passed after correcting Q4_K decoding. Base tensor hashes unchanged; four adapter tensors changed; exact checkpoint reload logits. Peak MLX allocation 10,754,375,304 bytes is slightly above the nominal 10 GiB allocator budget; this is not a hard process-RSS cap. Concurrent system load affects observed timings.

The saved config's phrase "decoded to FP16 by MLX" is imprecise: its immutable backend snapshot uses gguf 0.19.0 for Q4_K and MLX 0.32.2 for other tensors. See the pinned environment. Original EXP-FRL-003 used the incorrect native path and is not valid model-training evidence.

No repository repair capability, generalization, RL improvement, or statistical hypothesis was tested here. Three short generation matches in EXP-FRL-005 are not full numerical equivalence.
