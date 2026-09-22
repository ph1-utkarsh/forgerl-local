"""Bounded local baseline. Generated code executes only inside Docker."""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen

from qualification import TASKS
from cases import CASES

ROOT = Path(__file__).resolve().parent
MODEL = "qwen3:4b-instruct-2507-q4_K_M"
IMAGE_TAG = "python:3.12-slim"
SYSTEM = '''You are repairing a Python repository. Respond with one JSON object per turn.
Allowed actions:
{"action":"list"}
{"action":"read","path":"solution.py"}
{"action":"write","path":"solution.py","content":"complete Python source"}
{"action":"test"}
{"action":"finish"}
Read code, repair it, run public tests, then finish. No prose outside JSON.
Only solution.py is editable. Tests are managed by the evaluator.'''


def api(path, payload=None, timeout=180):
    data = None if payload is None else json.dumps(payload).encode()
    request = Request("http://127.0.0.1:11434/api/" + path, data=data,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def pinned_image():
    result = subprocess.run(["docker", "image", "inspect", IMAGE_TAG, "--format", "{{.Id}}"],
                            capture_output=True, text=True, check=True, timeout=15)
    value = result.stdout.strip()
    if not value.startswith("sha256:"):
        raise RuntimeError("Docker image must be pinned by local digest")
    return value


def grade(source, tests, image, timeout=12):
    """A fresh resource-limited container; no host secrets or writable mounts."""
    name = "frl-" + uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix="frl-") as temporary:
        directory = Path(temporary)
        directory.chmod(0o755)
        (directory / "solution.py").write_text(source)
        # Resolve only trusted static suite identifiers; hidden expected outputs
        # and test programs never enter the untrusted container.
        matches = [(task, suite) for task in TASKS for suite in ("public", "hidden", "both")
                   if tests == (task.public if suite == "public" else task.hidden
                                if suite == "hidden" else task.public + task.hidden)]
        if len(matches) != 1:
            raise ValueError("unknown trusted test suite")
        task, suite = matches[0]
        spec = CASES[task.name]
        cases = spec["public"] + spec["hidden"] if suite == "both" else spec[suite]
        request = {"function": spec["function"], "inputs": [row[0] for row in cases]}
        (directory / "worker.py").write_text((ROOT / "worker.py").read_text())
        for file in directory.iterdir():
            file.chmod(0o644)
        command = ["docker", "run", "-i", "--rm", "--name", name, "--pull=never",
                   "--network=none", "--read-only", "--cap-drop=ALL",
                   "--security-opt=no-new-privileges", "--pids-limit=64",
                   "--memory=256m", "--memory-swap=256m", "--cpus=1",
                   "--user=65534:65534", "--log-driver=none",
                   "--mount", f"type=bind,src={directory},dst=/work,readonly",
                   "--workdir=/work", "--env=PYTHONDONTWRITEBYTECODE=1", image,
                   "python", "-B", "worker.py"]
        # Output is bounded by the host reader. Expected outputs remain here.
        with tempfile.TemporaryFile() as output:
            start = time.monotonic()
            process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.stdin.write(json.dumps(request).encode())
            process.stdin.close()
            import selectors
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)
            size = 0
            reason = None
            try:
                while True:
                    if time.monotonic() - start > timeout:
                        reason = "timeout"
                        break
                    events = selector.select(0.1)
                    if events:
                        chunk = process.stdout.read1(4096)
                        if not chunk:
                            break
                        size += len(chunk)
                        if size > 65536:
                            reason = "output_limit"
                            break
                        output.write(chunk)
                    elif process.poll() is not None:
                        break
                if reason:
                    subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)
                    process.kill()
                code = process.wait(timeout=15)
            finally:
                selector.close()
                process.stdout.close()
                if process.poll() is None:
                    process.kill()
                    process.wait()
                subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)
            output.seek(0)
            log = output.read().decode(errors="replace")
        checks = []
        try:
            rows = json.loads(log)
            if not isinstance(rows, list) or len(rows) != len(cases):
                raise ValueError("wrong response length")
            for row, (_, expected) in zip(rows, cases):
                if not isinstance(row, dict):
                    raise ValueError("wrong response type")
                if isinstance(expected, dict) and "raises" in expected:
                    correct = row.get("raises") == expected["raises"]
                else:
                    correct = ("value" in row and row["value"] == expected
                               and "raises" not in row)
                correct = correct and row.get("mutated") is False
                if task.name == "merge" and "raises" not in row:
                    correct = correct and row.get("alias") is False
                checks.append(bool(correct))
        except (ValueError, TypeError):
            reason = reason or "invalid_worker_response"
        return {"passed": code == 0 and reason is None and bool(checks) and all(checks),
                "checks_passed": sum(checks), "checks_total": len(cases), "returncode": code,
                "reason": reason, "output": log[-4000:], "seconds": time.monotonic() - start}


def valid_path(value):
    if not isinstance(value, str) or PurePosixPath(value).is_absolute():
        return False
    return value == "solution.py"


def action_step(action, source, task, image):
    if not isinstance(action, dict):
        raise ValueError("action must be an object")
    kind = action.get("action")
    if kind == "list":
        return source, {"files": ["solution.py"], "public_tests": task.public}, False
    if kind in ("read", "write") and not valid_path(action.get("path")):
        raise ValueError("only solution.py is accessible")
    if kind == "read":
        return source, {"content": source}, False
    if kind == "write":
        content = action.get("content")
        if not isinstance(content, str) or len(content.encode()) > 16000:
            raise ValueError("content must be text within 16000 bytes")
        return content, {"written": True}, False
    if kind == "test":
        return source, grade(source, task.public, image), False
    if kind == "finish":
        return source, {"finished": True}, True
    raise ValueError("unknown action")


def episode(task, seed, image, max_steps):
    source = task.buggy
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": task.instruction}]
    trace = []
    done = False
    start = time.monotonic()
    for step in range(max_steps):
        record = {"step": step}
        try:
            response = api("chat", {"model": MODEL, "messages": messages,
                           "stream": False, "format": "json", "keep_alive": "5m",
                           "options": {"temperature": 0.2, "seed": seed, "num_ctx": 4096,
                                       "num_predict": 512}})
            record["response"] = response
            content = response["message"]["content"]
            messages.append({"role": "assistant", "content": content})
            action = json.loads(content)
            source, observation, done = action_step(action, source, task, image)
            record.update(action=action, observation=observation, valid=True)
        except (ValueError, KeyError, TypeError) as error:
            observation = {"error": str(error)}
            record.update(observation=observation, valid=False)
        except Exception as error:
            record.update(error=repr(error), valid=False, transport_failure=True)
            trace.append(record)
            break
        messages.append({"role": "user", "content": json.dumps(observation)})
        trace.append(record)
        if done:
            break
    result = grade(source, task.hidden, image)
    return {"task": task.name, "seed": seed, "finished": done, "trace": trace,
            "source": source, "hidden": result, "success": done and result["passed"],
            "seconds": time.monotonic() - start,
            "prompt_tokens": sum(t.get("response", {}).get("prompt_eval_count", 0) for t in trace),
            "output_tokens": sum(t.get("response", {}).get("eval_count", 0) for t in trace)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["controls", "baseline"])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--seeds", default="0,1,2")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--max-steps", type=int, default=8)
    args = parser.parse_args()
    if not args.run_id.replace("-", "").isalnum() or not 1 <= args.limit <= len(TASKS):
        parser.error("invalid run ID or task limit")
    image = pinned_image()
    directory = ROOT / "experiments" / args.run_id
    directory.mkdir(parents=True, exist_ok=False)
    config = vars(args)
    config.update(image=image, model=MODEL, python=sys.version, platform=platform.platform(),
                  source_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in [Path(__file__), ROOT / "qualification.py",
                                           ROOT / "cases.py", ROOT / "worker.py"]})
    for filename in config["source_hashes"]:
        (directory / filename).write_bytes((ROOT / filename).read_bytes())
    if args.mode == "baseline":
        config["ollama_version"] = api("version")
        config["model_metadata"] = [m for m in api("tags")["models"] if m["name"] == MODEL]
    (directory / "config.json").write_text(json.dumps(config, indent=2))
    results = []
    for task in TASKS[:args.limit]:
        if args.mode == "controls":
            row = {"task": task.name, "buggy": grade(task.buggy, task.hidden, image),
                   "oracle": grade(task.oracle, task.public + task.hidden, image)}
            row["success"] = not row["buggy"]["passed"] and row["oracle"]["passed"]
            rows = [row]
        else:
            rows = []
            for seed in map(int, args.seeds.split(",")):
                row = episode(task, seed, image, args.max_steps)
                (directory / f"{task.name}-{seed}.json").write_text(json.dumps(row, indent=2))
                rows.append(row)
                print(json.dumps({"task": task.name, "seed": seed, "success": row["success"],
                                  "seconds": row["seconds"]}), flush=True)
        for row in rows:
            results.append(row)
            if args.mode == "controls":
                (directory / f"{task.name}.json").write_text(json.dumps(row, indent=2))
                print(json.dumps({"task": task.name, "success": row["success"]}), flush=True)
    summary = {"cohort": "qualification-only", "attempted": len(results),
               "successful": sum(r["success"] for r in results), "paid_spend": 0}
    (directory / "metrics.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)
    if args.mode == "controls" and summary["successful"] != summary["attempted"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
