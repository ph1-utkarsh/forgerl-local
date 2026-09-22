"""Read-only compatibility probe for the user's existing local Qwen blob."""
import json
from pathlib import Path
import time
import mlx.core as mx

SOURCE = Path("/Users/sanjaybisen/.ollama/models/blobs/sha256-85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9")
OUTPUT = Path(__file__).resolve().parent / "experiments/EXP-FRL-002/gguf-probe.json"
if OUTPUT.exists():
    raise FileExistsError(OUTPUT)
mx.set_memory_limit(10 * 1024**3)
mx.set_cache_limit(64 * 1024**2)
start = time.monotonic()
weights, metadata = mx.load(str(SOURCE), format="gguf", return_metadata=True)
record = {"source": str(SOURCE), "seconds": time.monotonic() - start,
          "tensors": {name: {"shape": list(value.shape), "dtype": str(value.dtype)}
                      for name, value in weights.items()},
          "tensor_bytes": sum(value.nbytes for value in weights.values()),
          "architecture": metadata.get("general.architecture"),
          "paid_spend": 0, "interpretation": "tensor loading only; no model parity or training claim"}
OUTPUT.write_text(json.dumps(record, indent=2))
print(json.dumps({k: v for k, v in record.items() if k != "tensors"}, indent=2))
print(json.dumps(dict(list(record["tensors"].items())[:8]), indent=2))
