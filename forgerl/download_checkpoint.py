"""Fetch only the reviewed, immutable public checkpoint. No inference service."""
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
os.environ["HF_HOME"] = str(ROOT / ".hf-cache")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "60"
os.environ["HF_HUB_DISABLE_XET"] = "1"

from huggingface_hub import snapshot_download

plan = json.loads((ROOT / "forgerl/experiments/EXP-FRL-002/checkpoint-plan.json").read_text())
if plan["known_download_bytes"] > 3_000_000_000:
    raise ValueError("checkpoint exceeds the 3 GB acquisition cap")
start = time.monotonic()
path = snapshot_download(
    repo_id=plan["repository"], revision=plan["revision"], token=False,
    local_dir=ROOT / "models/qwen3-4b-instruct-mlx", max_workers=4,
    allow_patterns=[file["name"] for file in plan["files"]],
)
receipt = {"repository": plan["repository"], "revision": plan["revision"],
           "path": str(path), "seconds": time.monotonic() - start, "paid_spend": 0}
output = ROOT / "forgerl/experiments/EXP-FRL-002/download-receipt.json"
if output.exists():
    raise FileExistsError(output)
output.write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt, indent=2))
