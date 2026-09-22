"""Evaluate base vs failure-derived adapter on frozen train/dev/test repair blocks."""
import argparse, json, os
from pathlib import Path
os.environ["HF_HUB_OFFLINE"]="1"; os.environ["TOKENIZERS_PARALLELISM"]="false"
import mlx.core as mx
from mlx_lm import generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tuner.utils import load_adapters
from gguf_backend import load_local_gguf

ROOT=Path(__file__).resolve().parents[1]
SYSTEM='Return exactly one JSON object with string fields action, old, new. action must be "replace". Use the exact old substring and the minimal corrected replacement.'
TASKS=[
 {"split":"train","name":"youtube-dl","old":"    UNARY_OPERATORS = {\n        '': lambda v: v is not None,\n        '!': lambda v: v is None,\n    }\n","new":"    UNARY_OPERATORS = {\n        '': lambda v: (v is True) if isinstance(v, bool) else (v is not None),\n        '!': lambda v: (v is False) if isinstance(v, bool) else (v is None),\n    }\n","issue":"Positive boolean keys reject False; negated keys accept False and missing values."},
 {"split":"development","name":"tornado","old":"        if self._next_timeout <= current_time:\n            callback_time_sec = self.callback_time / 1000.0\n            self._next_timeout += (math.floor((current_time - self._next_timeout) /\n                                              callback_time_sec) + 1) * callback_time_sec\n","new":"        callback_time_sec = self.callback_time / 1000.0\n        if self._next_timeout <= current_time:\n            self._next_timeout += (math.floor((current_time - self._next_timeout) /\n                                              callback_time_sec) + 1) * callback_time_sec\n        else:\n            self._next_timeout += callback_time_sec\n","issue":"When the clock moves backwards, advance the periodic callback instead of repeating the same timeout."},
 {"split":"test","name":"PySnooper","old":"            with open(output_path, 'a') as output_file:\n","new":"            with open(output, 'a') as output_file:\n","issue":"File output uses an undefined/wrong path variable; write to the supplied output path."}
]

def score(text,task):
    try:
        row=json.loads(text); valid=set(row)=={"action","old","new"} and row["action"]=="replace"
        return {"valid_json_action":valid,"exact_repair":valid and row["old"]==task["old"] and row["new"]==task["new"]}
    except (json.JSONDecodeError,TypeError): return {"valid_json_action":False,"exact_repair":False}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--run-id",required=True); parser.add_argument("--adapter-run",required=True); args=parser.parse_args()
    out=ROOT/"forgerl/experiments"/args.run_id; out.mkdir(parents=True,exist_ok=False)
    mx.set_memory_limit(10*1024**3); mx.set_cache_limit(256*1024**2)
    model,tokenizer=load_local_gguf(ROOT/"models/qwen3-4b-instruct-mlx")
    prompts=[]
    for task in TASKS:
        user=f"Repair {task['name']}. {task['issue']} Exact buggy block:\n{task['old']}"
        prompts.append(tokenizer.apply_chat_template([{"role":"system","content":SYSTEM},{"role":"user","content":user}],tokenize=False,add_generation_prompt=True))
    rows=[]
    for label in ("base","adapter"):
        if label=="adapter": model=load_adapters(model,str(ROOT/"forgerl/experiments"/args.adapter_run)); model.eval()
        for task,prompt in zip(TASKS,prompts):
            text=generate(model,tokenizer,prompt=prompt,max_tokens=384,sampler=make_sampler(temp=0))
            rows.append({"condition":label,"task":task["name"],"split":task["split"],"response":text,**score(text,task)})
            print(json.dumps({k:rows[-1][k] for k in ("condition","task","exact_repair")}),flush=True)
    metrics={"rows":rows,"base_exact":sum(r["exact_repair"] for r in rows if r["condition"]=="base"),
             "adapter_exact":sum(r["exact_repair"] for r in rows if r["condition"]=="adapter"),"paid_spend":0,
             "interpretation":"three-task exact-block pilot; one task per split is underpowered"}
    (out/"config.json").write_text(json.dumps({"adapter_run":args.adapter_run,"decoding":"greedy","max_tokens":384,"paid_spend":0},indent=2))
    (out/"metrics.json").write_text(json.dumps(metrics,indent=2)); (out/"evaluate_failure_adapter.py").write_bytes(Path(__file__).read_bytes())

if __name__=="__main__": main()
