"""Independent GGUF decoder cross-check; no model generation or network."""
import json
from pathlib import Path
import numpy as np
import gguf
import mlx.core as mx
from gguf_backend import SOURCE

mx.set_memory_limit(10 * 1024**3)
mx.set_cache_limit(128 * 1024**2)
weights = mx.load(str(SOURCE), format="gguf")
reader = gguf.GGUFReader(str(SOURCE))
rows = []
for tensor in reader.tensors:
    if not (tensor.name.startswith("blk.0.") or tensor.name in
            ("token_embd.weight", "output_norm.weight")):
        continue
    packed = tensor.data[:2] if tensor.data.ndim == 2 else tensor.data
    expected = gguf.dequantize(packed, tensor.tensor_type)
    actual = np.array(weights[tensor.name][:2] if tensor.data.ndim == 2
                      else weights[tensor.name])
    expected = expected.astype(actual.dtype)
    diff = actual.astype(np.float32) - expected.astype(np.float32)
    row = {"name": tensor.name, "quant": tensor.tensor_type.name,
           "shape": list(actual.shape), "max_abs_error": float(np.max(np.abs(diff))),
           "rms_error": float(np.sqrt(np.mean(diff * diff)))}
    rows.append(row)
    print(json.dumps(row), flush=True)
out = Path(__file__).resolve().parent / "experiments/EXP-FRL-004/decode-comparison.json"
with out.open("x") as stream:
    json.dump(rows, stream, indent=2)
