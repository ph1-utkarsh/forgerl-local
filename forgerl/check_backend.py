"""Compare short raw-prompt generations with the existing Ollama reference."""
import json
import os
from pathlib import Path
import time
import argparse

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from runner import api, MODEL
from gguf_backend import load_local_gguf
import mlx.core as mx
from mlx_lm import generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.utils import load_tokenizer

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--run-id", required=True)
args = parser.parse_args()
if not args.run_id.startswith("EXP-FRL-") or not args.run_id.replace("-", "").isalnum():
    raise ValueError("invalid run ID")
output = ROOT / "forgerl/experiments" / args.run_id
output.mkdir(parents=True, exist_ok=False)
model_dir = ROOT / "models/qwen3-4b-instruct-mlx"
tokenizer = load_tokenizer(model_dir)
questions = ["Reply with exactly the number: 2+2.",
             "Complete the sequence with one number: 1, 2, 3,",
             "Return exactly the lowercase word hello."]
rows = []
for question in questions:
    prompt = tokenizer.apply_chat_template([{"role": "user", "content": question}],
                                           tokenize=False, add_generation_prompt=True)
    reference = api("generate", {"model": MODEL, "prompt": prompt, "raw": True,
                    "stream": False, "keep_alive": 0, "logprobs": True, "top_logprobs": 5,
                    "options": {"temperature": 0, "seed": 0, "num_predict": 8,
                                "num_ctx": 2048, "repeat_penalty": 1}})
    rows.append({"question": question, "prompt": prompt, "ollama": reference})
mx.set_memory_limit(10 * 1024**3)
mx.set_cache_limit(256 * 1024**2)
model, tokenizer = load_local_gguf(model_dir)
for index, row in enumerate(rows):
    start = time.monotonic()
    result = generate(model, tokenizer, prompt=row["prompt"], max_tokens=8,
                      sampler=make_sampler(temp=0))
    row.update(mlx=result, mlx_seconds=time.monotonic() - start,
               exact_text_match=result == row["ollama"].get("response"))
    (output / f"prompt-{index}.json").write_text(json.dumps(row, indent=2))
    print(json.dumps({"question": row["question"], "ollama": row["ollama"].get("response"),
                      "mlx": result, "exact_text_match": row["exact_text_match"]}), flush=True)
summary = {"attempted": len(rows), "exact_text_matches": sum(r["exact_text_match"] for r in rows),
           "logprobs_available": all(bool(r["ollama"].get("logprobs")) for r in rows),
           "interpretation": "short generation sanity check, not a full numerical parity proof",
           "paid_spend": 0}
(output / "metrics.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
