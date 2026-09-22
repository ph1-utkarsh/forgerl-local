"""Read public metadata and pin a free training checkpoint; no weights download."""
import json
from pathlib import Path
from urllib.request import urlopen

REPO = "mlx-community/Qwen3-4B-Instruct-2507-4bit"
output = Path(__file__).resolve().parent / "experiments" / "EXP-FRL-002" / "checkpoint-plan.json"
if output.exists():
    raise FileExistsError(output)
with urlopen(f"https://huggingface.co/api/models/{REPO}?blobs=true", timeout=30) as response:
    metadata = json.load(response)
revision = metadata["sha"]
with urlopen(f"https://huggingface.co/{REPO}/resolve/{revision}/config.json", timeout=30) as response:
    config = json.load(response)
if "model_file" in config or config.get("auto_map"):
    raise ValueError("custom remote model code requires separate review")
files = [{"name": file["rfilename"], "size": file.get("size"),
          "lfs_sha256": file.get("lfs", {}).get("sha256")}
         for file in metadata["siblings"]
         if file["rfilename"].endswith((".safetensors", ".json", ".txt", ".jinja"))]
plan = {"repository": REPO, "revision": revision, "files": files,
        "known_download_bytes": sum(file["size"] or 0 for file in files),
        "config": config, "weights_downloaded": False, "paid_spend": 0,
        "purpose": "candidate local adapter-training representation; not identical to Ollama GGUF quantization"}
output.write_text(json.dumps(plan, indent=2))
print(json.dumps({k: plan[k] for k in ("repository", "revision", "known_download_bytes", "weights_downloaded")}, indent=2))
