"""Bounded real Qwen adapter update and reload test; not a capability study."""
import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--source", choices=["gguf", "mlx"], default="gguf")
    parser.add_argument("--messages-file")
    args = parser.parse_args()
    if not args.run_id.replace("-", "").isalnum() or not 1 <= args.steps <= 20:
        parser.error("bounded pilot requires a valid run ID and 1..20 steps")
    output = ROOT / "forgerl/experiments" / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    model_dir = ROOT / "models/qwen3-4b-instruct-mlx"
    plan = json.loads((ROOT / "forgerl/experiments/EXP-FRL-002/checkpoint-plan.json").read_text())
    if args.source == "mlx":
        for expected in plan["files"]:
            path = model_dir / expected["name"]
            if path.stat().st_size != expected["size"]:
                raise ValueError(f"size mismatch: {path.name}")
            if expected["lfs_sha256"] and file_hash(path) != expected["lfs_sha256"]:
                raise ValueError(f"hash mismatch: {path.name}")
    else:
        from gguf_backend import load_local_gguf, verify_source, SOURCE_SHA256
        verify_source()

    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    from mlx.utils import tree_flatten
    from mlx_lm import load
    from mlx_lm.tuner.utils import linear_to_lora_layers
    import numpy as np
    from training_math import assistant_token_loss

    if not mx.metal.is_available():
        raise RuntimeError("Metal unavailable; run with approved Apple GPU access")
    memory_limit = (10 if args.source == "gguf" else 6) * 1024**3
    mx.set_memory_limit(memory_limit)
    mx.set_cache_limit(512 * 1024**2)
    mx.random.seed(0)
    adapter_config = {"fine_tune_type": "lora", "num_layers": 1,
                      "lora_parameters": {"rank": 4, "scale": 4.0, "dropout": 0.0,
                                          "keys": ["self_attn.q_proj", "self_attn.v_proj"]}}
    messages = [{"role": "user", "content": "Return the JSON action to list the repository files."},
                {"role": "assistant", "content": '{"action":"list","path":"solution.py","content":""}'}]
    if args.messages_file:
        messages_path = Path(args.messages_file).resolve()
        if ROOT not in messages_path.parents:
            raise ValueError("messages file must be inside the portfolio")
        messages = json.loads(messages_path.read_text())
        if [row.get("role") for row in messages] != ["user", "assistant"]:
            raise ValueError("pilot requires exactly one user/assistant training pair")
    config = {"checkpoint": plan["repository"], "revision": plan["revision"],
              "seed": 0, "steps": args.steps, "learning_rate": 0.001,
              "adapter": adapter_config, "messages": messages,
              "purpose": "training-mechanics qualification only; no research fixtures used",
              "versions": {name: importlib.metadata.version(name) for name in ("mlx", "mlx-lm", "transformers")},
              "memory_limit_bytes": memory_limit, "paid_spend": 0, "source_format": args.source,
              "script_sha256": file_hash(Path(__file__))}
    if args.messages_file:
        config["messages_file"] = str(messages_path.relative_to(ROOT))
        config["messages_sha256"] = file_hash(messages_path)
    config["objective_sha256"] = file_hash(Path(__file__).with_name("training_math.py"))
    if args.source == "gguf":
        config["checkpoint"] = "installed Ollama Qwen3-4B-Instruct-2507 Q4_K_M decoded to FP16 by MLX"
        config["revision"] = SOURCE_SHA256
        config["mapping_sha256"] = file_hash(Path(__file__).with_name("gguf_backend.py"))
    (output / "config.json").write_text(json.dumps(config, indent=2))
    (output / "adapter_pilot.py").write_bytes(Path(__file__).read_bytes())
    (output / "training_math.py").write_bytes(Path(__file__).with_name("training_math.py").read_bytes())
    if args.source == "gguf":
        (output / "gguf_backend.py").write_bytes(Path(__file__).with_name("gguf_backend.py").read_bytes())
    start = time.monotonic()
    model, tokenizer = load_local_gguf(model_dir) if args.source == "gguf" else load(str(model_dir))
    print("Loaded pinned checkpoint", flush=True)
    prefix = tokenizer.apply_chat_template(messages[:1], tokenize=True, add_generation_prompt=True)
    tokens = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=False)
    if tokens[:len(prefix)] != prefix or not len(prefix) < len(tokens) <= 512:
        raise ValueError("unexpected chat tokenization or context length")
    x = mx.array([tokens[:-1]])
    targets = mx.array([tokens[1:]])
    original_logits = model(x)[:, -1, :].astype(mx.float32)
    mx.eval(original_logits)
    model.freeze()
    linear_to_lora_layers(model, adapter_config["num_layers"], adapter_config["lora_parameters"])
    trainable = dict(tree_flatten(model.trainable_parameters()))
    if not trainable or not all(name.endswith(("lora_a", "lora_b")) for name in trainable):
        raise ValueError("base parameters unexpectedly trainable")
    initial_logits = model(x)[:, -1, :].astype(mx.float32)
    zero_init_error = mx.max(mx.abs(original_logits - initial_logits)).item()
    if zero_init_error != 0:
        raise AssertionError("zero-initialized adapter changed base logits")
    del initial_logits, original_logits

    def parameter_hashes():
        result = {}
        for name, value in tree_flatten(model.parameters()):
            if value.dtype == mx.bfloat16:
                value = value.astype(mx.float32)
            result[name] = hashlib.sha256(np.asarray(value).tobytes()).hexdigest()
        return result

    before_hashes = parameter_hashes()

    def loss_fn(network):
        logits = network(x).astype(mx.float32)
        return assistant_token_loss(logits, targets, len(prefix) - 1)

    optimizer = optim.Adam(learning_rate=0.001)
    loss_and_grad = nn.value_and_grad(model, loss_fn)
    losses = []
    step_seconds = []
    for step in range(args.steps):
        step_start = time.monotonic()
        loss, gradients = loss_and_grad(model)
        optimizer.update(model, gradients)
        mx.eval(model.parameters(), optimizer.state, loss)
        value = loss.item()
        if not np.isfinite(value):
            raise ValueError("nonfinite pilot loss")
        losses.append(value)
        step_seconds.append(time.monotonic() - step_start)
        print(json.dumps({"step": step, "loss_before_update": value,
                          "seconds": step_seconds[-1], "peak_memory_bytes": mx.get_peak_memory()}), flush=True)
    final_loss = loss_fn(model).item()
    after_hashes = parameter_hashes()
    changed = [name for name in before_hashes if before_hashes[name] != after_hashes[name]]
    if not changed or any(name not in trainable for name in changed):
        raise AssertionError("adapter did not change, or frozen base changed")
    adapter_file = output / "adapters.safetensors"
    mx.save_safetensors(str(adapter_file), dict(tree_flatten(model.trainable_parameters())))
    (output / "adapter_config.json").write_text(json.dumps(adapter_config, indent=2))
    trained_logits = model(x)[:, -1, :].astype(mx.float32)
    mx.eval(trained_logits)
    peak = mx.get_peak_memory()
    trainable_count = sum(value.size for value in trainable.values())
    del model, optimizer, gradients, loss_and_grad, trainable
    gc.collect()
    mx.clear_cache()
    if args.source == "gguf":
        from mlx_lm.tuner.utils import load_adapters
        restored, _ = load_local_gguf(model_dir)
        restored = load_adapters(restored, str(output))
        restored.eval()
    else:
        restored, _ = load(str(model_dir), adapter_path=str(output))
    restored_logits = restored(x)[:, -1, :].astype(mx.float32)
    reload_error = mx.max(mx.abs(trained_logits - restored_logits)).item()
    metrics = {"passed": reload_error <= 1e-5 and final_loss < losses[0],
               "losses_before_update": losses, "final_loss": final_loss,
               "zero_init_max_logit_error": zero_init_error,
               "reload_max_logit_error": reload_error,
               "frozen_base_unchanged": True, "changed_adapter_tensors": changed,
               "trainable_parameters": trainable_count, "sequence_tokens": len(tokens),
               "step_seconds": step_seconds, "peak_training_memory_bytes": peak,
               "total_seconds": time.monotonic() - start,
               "adapter_sha256": file_hash(adapter_file), "paid_spend": 0,
               "interpretation": "one-example SFT mechanics only; no capability/generalization claim"}
    (output / "parameter_hashes.json").write_text(json.dumps({"before": before_hashes, "after": after_hashes}, indent=2))
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
    if not metrics["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
