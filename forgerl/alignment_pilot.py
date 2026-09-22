"""Bounded real-model DPO or grouped verifiable-reward LoRA update."""
import argparse,gc,hashlib,json,os,time
from pathlib import Path
os.environ["HF_HUB_OFFLINE"]="1"; os.environ["TOKENIZERS_PARALLELISM"]="false"
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten
from mlx_lm.tuner.utils import linear_to_lora_layers,load_adapters
from gguf_backend import load_local_gguf,verify_source,SOURCE_SHA256
from training_math import assistant_token_loss

ROOT=Path(__file__).resolve().parents[1]
PAIR=json.loads((ROOT/"forgerl/training/youtube_failure_example.json").read_text())
REJECTED='{"action":"replace","old":"    UNARY_OPERATORS = {\\n        \'\': lambda v: v is not None,\\n        \'!\': lambda v: v is None,\\n    }\\n","new":"    UNARY_OPERATORS = {\\n        \'\': lambda v: v is not None,\\n        \'!\': lambda v: v is False,\\n    }\\n"}'

def digest(value): return hashlib.sha256(np.asarray(value).tobytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--run-id",required=True); parser.add_argument("--objective",choices=["dpo","grpo"],required=True); parser.add_argument("--steps",type=int,default=10); args=parser.parse_args()
    if not 1<=args.steps<=20: parser.error("steps must be 1..20")
    out=ROOT/"forgerl/experiments"/args.run_id; out.mkdir(parents=True,exist_ok=False); verify_source()
    mx.set_memory_limit(10*1024**3); mx.set_cache_limit(512*1024**2); mx.random.seed(0)
    model,tokenizer=load_local_gguf(ROOT/"models/qwen3-4b-instruct-mlx")
    prompt=tokenizer.apply_chat_template(PAIR[:1],tokenize=True,add_generation_prompt=True)
    def encoded(answer): return tokenizer.apply_chat_template(PAIR[:1]+[{"role":"assistant","content":answer}],tokenize=True,add_generation_prompt=False)
    chosen,rejected=encoded(PAIR[1]["content"]),encoded(REJECTED)
    def arrays(tokens): return mx.array([tokens[:-1]]),mx.array([tokens[1:]])
    cx,cy=arrays(chosen); rx,ry=arrays(rejected); start=len(prompt)-1
    def lp(network,x,y): return -assistant_token_loss(network(x).astype(mx.float32),y,start)
    ref_c=lp(model,cx,cy).item(); ref_r=lp(model,rx,ry).item(); ref_margin=ref_c-ref_r
    model.freeze(); adapter={"rank":4,"scale":4.0,"dropout":0.0,"keys":["self_attn.q_proj","self_attn.v_proj"]}
    linear_to_lora_layers(model,1,adapter); trainable=dict(tree_flatten(model.trainable_parameters()))
    before={n:digest(v) for n,v in tree_flatten(model.parameters())}
    beta=.2; clip=.2
    def loss_fn(network):
        c,r=lp(network,cx,cy),lp(network,rx,ry)
        if args.objective=="dpo": return mx.logaddexp(mx.array(0,dtype=mx.float32),-beta*((c-r)-ref_margin))
        ratios=mx.stack([mx.exp(c-ref_c),mx.exp(r-ref_r)]); advantages=mx.array([1.,-1.])
        clipped=mx.clip(ratios,1-clip,1+clip); return -mx.mean(mx.minimum(ratios*advantages,clipped*advantages))
    optimizer=optim.Adam(learning_rate=5e-4); value_grad=nn.value_and_grad(model,loss_fn); losses=[]
    start_time=time.monotonic()
    for step in range(args.steps):
        loss,grads=value_grad(model); optimizer.update(model,grads); mx.eval(model.parameters(),optimizer.state,loss); losses.append(loss.item()); print(json.dumps({"step":step,"loss":losses[-1]}),flush=True)
    final_c=lp(model,cx,cy).item(); final_r=lp(model,rx,ry).item(); after={n:digest(v) for n,v in tree_flatten(model.parameters())}
    changed=[n for n in before if before[n]!=after[n]]
    if not changed or any(n not in trainable for n in changed): raise AssertionError("invalid parameter changes")
    mx.save_safetensors(str(out/"adapters.safetensors"),dict(tree_flatten(model.trainable_parameters())))
    (out/"adapter_config.json").write_text(json.dumps({"fine_tune_type":"lora","num_layers":1,"lora_parameters":adapter},indent=2))
    del model,optimizer,grads,value_grad; gc.collect(); mx.clear_cache()
    restored,_=load_local_gguf(ROOT/"models/qwen3-4b-instruct-mlx"); restored=load_adapters(restored,str(out)); restored.eval()
    reload_margin=lp(restored,cx,cy).item()-lp(restored,rx,ry).item()
    metrics={"objective":args.objective,"losses":losses,"reference_margin":ref_margin,"final_margin":final_c-final_r,"reload_margin":reload_margin,
      "margin_improved":final_c-final_r>ref_margin,"changed_adapter_tensors":changed,"frozen_base_unchanged":True,"trainable_parameters":sum(v.size for v in trainable.values()),
      "total_seconds":time.monotonic()-start_time,"paid_spend":0,"interpretation":"one preference pair mechanics; no capability claim"}
    config={"objective":args.objective,"steps":args.steps,"beta":beta,"clip":clip,"source_sha256":SOURCE_SHA256,"paid_spend":0}
    (out/"config.json").write_text(json.dumps(config,indent=2)); (out/"metrics.json").write_text(json.dumps(metrics,indent=2)); (out/"alignment_pilot.py").write_bytes(Path(__file__).read_bytes()); (out/"alignment_math.py").write_bytes((Path(__file__).with_name("alignment_math.py")).read_bytes())
    print(json.dumps(metrics,indent=2))

if __name__=="__main__": main()
