"""Bounded local-Qwen baseline on one qualified real repository bug."""
import argparse
import hashlib
import json
from pathlib import Path
import selectors
import subprocess
import tempfile
import time

from runner import api, MODEL, ACTION_SCHEMA as _UNUSED
from real_repo_probe import ROOT, SOURCE, BUGGY, FIXED, IMAGE, TEST, extract, git

TARGET = "youtube_dl/utils.py"
SYSTEM = '''Repair one bug in a historical Python repository. Return exactly one JSON object.
Actions require all fields action, old, new. Allowed actions:
{"action":"read","old":"","new":""}
{"action":"replace","old":"exact source substring","new":"replacement source"}
{"action":"test","old":"","new":""}
{"action":"finish","old":"","new":""}
Only youtube_dl/utils.py is editable. Read the supplied region, make the smallest repair, test, finish.'''
SCHEMA = {"type": "object", "properties": {
    "action": {"type": "string", "enum": ["read", "replace", "test", "finish"]},
    "old": {"type": "string"}, "new": {"type": "string"}},
    "required": ["action", "old", "new"], "additionalProperties": False}
READ_SCHEMA = {"type": "object", "properties": {
    "action": {"type": "string", "enum": ["read"]},
    "old": {"type": "string", "enum": [""]}, "new": {"type": "string", "enum": [""]}},
    "required": ["action", "old", "new"], "additionalProperties": False}


def bounded_test(source, image_id, timeout=60):
    with tempfile.TemporaryDirectory(prefix="frl-agent-") as temporary:
        checkout = Path(temporary)
        extract(BUGGY, checkout)
        (checkout / "test/test_utils.py").write_bytes(git("show", f"{FIXED}:test/test_utils.py"))
        (checkout / TARGET).write_text(source)
        command = ["docker", "run", "--rm", "--pull=never", "--network=none",
                   "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
                   "--pids-limit=128", "--memory=512m", "--memory-swap=512m", "--cpus=1",
                   "--user=65534:65534", "--log-driver=none",
                   "--mount", f"type=bind,src={checkout},dst=/repo,readonly",
                   "--workdir=/repo", "--env=PYTHONDONTWRITEBYTECODE=1", image_id,
                   "python", "-B", "-m", "unittest", "-q", TEST]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        chunks, size, reason, start = [], 0, None, time.monotonic()
        try:
            while True:
                if time.monotonic() - start > timeout:
                    reason = "timeout"; process.kill(); break
                events = selector.select(0.1)
                if events:
                    chunk = process.stdout.read1(4096)
                    if not chunk: break
                    size += len(chunk)
                    if size > 65536:
                        reason = "output_limit"; process.kill(); break
                    chunks.append(chunk)
                elif process.poll() is not None: break
            code = process.wait(timeout=10)
        finally:
            selector.close()
            if process.poll() is None: process.kill(); process.wait()
        log = b"".join(chunks).decode(errors="replace")
        return {"passed": code == 0 and reason is None, "returncode": code,
                "reason": reason, "output": log[-8000:], "seconds": time.monotonic() - start}


def context(source):
    start = source.index("def _match_one")
    end = source.index("\ndef match_str", start)
    return source[start:end]


def episode(seed, image_id, max_steps):
    source = git("show", f"{BUGGY}:{TARGET}").decode()
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": "Unary boolean filters are wrong: a positive key must reject False, while !key must accept False. Repair the implementation."}]
    trace, done = [], False
    for step in range(max_steps):
        response = api("chat", {"model": MODEL, "messages": messages, "stream": False,
                       "format": READ_SCHEMA if step == 0 else SCHEMA, "keep_alive": "5m",
                       "options": {"temperature": 0.2, "seed": seed, "num_ctx": 4096,
                                   "num_predict": 768}})
        raw = response["message"]["content"]
        messages.append({"role": "assistant", "content": raw})
        record = {"step": step, "response": response}
        try:
            action = json.loads(raw); kind = action["action"]
            if kind == "read": observation = {"path": TARGET, "content": context(source)}
            elif kind == "replace":
                old, new = action["old"], action["new"]
                if not old or len(new.encode()) > 12000 or source.count(old) != 1:
                    raise ValueError("old must identify exactly one substring; replacement <=12000 bytes")
                source = source.replace(old, new, 1); observation = {"replaced": True}
            elif kind == "test": observation = bounded_test(source, image_id)
            elif kind == "finish": observation = {"finished": True}; done = True
            else: raise ValueError("unknown action")
            record.update(action=action, observation=observation, valid=True)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            observation = {"error": str(error)}; record.update(observation=observation, valid=False)
        trace.append(record)
        messages.append({"role": "user", "content": json.dumps(observation)})
        if done: break
    grade = bounded_test(source, image_id)
    return {"seed": seed, "finished": done, "success": done and grade["passed"],
            "grade": grade, "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "matches_upstream": source.encode() == git("show", f"{FIXED}:{TARGET}"), "trace": trace,
            "prompt_tokens": sum(x["response"].get("prompt_eval_count", 0) for x in trace),
            "output_tokens": sum(x["response"].get("eval_count", 0) for x in trace)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--run-id", required=True)
    parser.add_argument("--seeds", default="0,1,2"); parser.add_argument("--max-steps", type=int, default=8)
    args = parser.parse_args()
    if not args.run_id.startswith("EXP-FRL-") or not 1 <= args.max_steps <= 12: parser.error("invalid bounds")
    out = ROOT / "forgerl/experiments" / args.run_id; out.mkdir(parents=True, exist_ok=False)
    image_id = subprocess.run(["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
                              check=True, capture_output=True, text=True).stdout.strip()
    config = {"model": MODEL, "buggy_commit": BUGGY, "fixed_commit": FIXED, "target": TARGET,
              "frozen_test_sha256": hashlib.sha256(git("show", f"{FIXED}:test/test_utils.py")).hexdigest(),
              "image_id": image_id, "seeds": args.seeds, "max_steps": args.max_steps,
              "paid_spend": 0, "cohort": "real-repository feasibility; not held-out research evaluation"}
    (out / "config.json").write_text(json.dumps(config, indent=2)); (out / "real_repo_agent.py").write_bytes(Path(__file__).read_bytes())
    rows = []
    for seed in map(int, args.seeds.split(",")):
        row = episode(seed, image_id, args.max_steps); rows.append(row)
        (out / f"seed-{seed}.json").write_text(json.dumps(row, indent=2)); print(json.dumps({"seed": seed, "success": row["success"]}), flush=True)
    metrics = {"attempted": len(rows), "successful": sum(r["success"] for r in rows),
               "finished": sum(r["finished"] for r in rows), "paid_spend": 0}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2)); print(json.dumps(metrics, indent=2))


if __name__ == "__main__": main()
