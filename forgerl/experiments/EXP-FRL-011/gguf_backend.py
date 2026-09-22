"""Explicit dense-Qwen3 mapping from the installed GGUF to MLX.

An independent GGUF decoder repairs Q4_K decoding; no weight re-quantization. It checks
metadata, all parameter names/shapes, and tokenizer IDs before returning a model.
The decoded representation must be evaluated separately from Ollama kernels.
"""
import hashlib
import json
from pathlib import Path
import re

SOURCE = Path("/Users/sanjaybisen/.ollama/models/blobs/sha256-85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9")
SOURCE_SHA256 = "85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9"
LAYER_NAMES = {
    "attn_norm": "input_layernorm", "ffn_norm": "post_attention_layernorm",
    "attn_q": "self_attn.q_proj", "attn_k": "self_attn.k_proj",
    "attn_v": "self_attn.v_proj", "attn_output": "self_attn.o_proj",
    "attn_q_norm": "self_attn.q_norm", "attn_k_norm": "self_attn.k_norm",
    "ffn_gate": "mlp.gate_proj", "ffn_up": "mlp.up_proj", "ffn_down": "mlp.down_proj",
}


def mapped_name(name):
    if name == "token_embd.weight":
        return "model.embed_tokens.weight"
    if name == "output_norm.weight":
        return "model.norm.weight"
    if name == "output.weight":
        return "lm_head.weight"
    match = re.fullmatch(r"blk\.(\d+)\.([a-z_]+)\.weight", name)
    if match and match[2] in LAYER_NAMES:
        return f"model.layers.{match[1]}.{LAYER_NAMES[match[2]]}.weight"
    raise ValueError(f"unsupported GGUF tensor name: {name}")


def load_local_gguf(tokenizer_dir):
    import gguf
    import numpy as np
    import mlx.core as mx
    from mlx_lm.models.qwen3 import Model, ModelArgs
    from mlx_lm.utils import load_tokenizer
    tokenizer_dir = Path(tokenizer_dir)
    config = json.loads((tokenizer_dir / "config.json").read_text())
    weights, metadata = mx.load(str(SOURCE), format="gguf", return_metadata=True)
    # EXP-FRL-004: native MLX 0.32.2 Q4_K decoding disagrees with gguf 0.19.0.
    # Replace affected tensors individually to bound temporary memory usage.
    reader = gguf.GGUFReader(str(SOURCE))
    for tensor in reader.tensors:
        if tensor.tensor_type == gguf.GGMLQuantizationType.Q4_K:
            decoded = gguf.dequantize(tensor.data, tensor.tensor_type).astype(np.float16)
            weights[tensor.name] = mx.array(decoded)
            mx.eval(weights[tensor.name])
            del decoded
    if metadata.get("general.architecture") != "qwen3":
        raise ValueError("only dense qwen3 is supported")
    checks = {"embedding_length": "hidden_size", "block_count": "num_hidden_layers",
              "feed_forward_length": "intermediate_size", "attention.head_count": "num_attention_heads",
              "attention.head_count_kv": "num_key_value_heads", "rope.freq_base": "rope_theta"}
    for gguf_key, config_key in checks.items():
        if metadata.get("qwen3." + gguf_key) != config[config_key]:
            raise ValueError(f"GGUF/config disagreement: {gguf_key}")
    if bool(config["tie_word_embeddings"]) != ("output.weight" not in weights):
        raise ValueError("embedding tying mismatch")
    tokenizer = load_tokenizer(tokenizer_dir)
    tokens = metadata["tokenizer.ggml.tokens"]
    for token, index in tokenizer.get_vocab().items():
        if index >= len(tokens) or tokens[index] != token:
            raise ValueError(f"tokenizer ID mismatch at {index}")
    renamed = {}
    for name, value in weights.items():
        if value.dtype not in (mx.float16, mx.float32):
            raise ValueError(f"unexpected packed tensor representation: {name}")
        target = mapped_name(name)
        if target in renamed:
            raise ValueError(f"duplicate mapped parameter: {target}")
        renamed[target] = value
    model = Model(ModelArgs.from_dict(config))
    model.load_weights(list(renamed.items()), strict=True)
    mx.eval(model.parameters())
    return model, tokenizer


def verify_source():
    digest = hashlib.sha256()
    with SOURCE.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != SOURCE_SHA256:
        raise ValueError("installed GGUF checksum changed")
    return digest.hexdigest()
