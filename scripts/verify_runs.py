"""Validate immutable artifact counts and source hashes, not research validity."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "forgerl" / "experiments"
errors = []
checked = 0
for directory in sorted(ROOT.iterdir()):
    if not (directory / "config.json").exists():
        continue
    config = json.loads((directory / "config.json").read_text())
    metrics_path = directory / "metrics.json"
    if not metrics_path.exists():
        if not (directory / "FAILURE.md").exists():
            errors.append(f"{directory.name}: unfinished (missing metrics)")
        continue
    metrics = json.loads(metrics_path.read_text())
    if config.get("objective") in {"dpo", "grpo"}:
        required = {"adapters.safetensors", "adapter_config.json", "alignment_pilot.py", "alignment_math.py"}
        missing = sorted(name for name in required if not (directory / name).exists())
        if missing:
            errors.append(f"{directory.name}: missing alignment artifacts {missing}")
        if metrics.get("objective") != config["objective"] or len(metrics.get("losses", [])) != config["steps"]:
            errors.append(f"{directory.name}: alignment objective/step mismatch")
        if not metrics.get("frozen_base_unchanged"):
            errors.append(f"{directory.name}: frozen base integrity failed")
        changed = metrics.get("changed_adapter_tensors", [])
        if not changed or any(not name.endswith(("lora_a", "lora_b")) for name in changed):
            errors.append(f"{directory.name}: invalid alignment parameter changes")
        if abs(metrics.get("final_margin", float("inf")) - metrics.get("reload_margin", float("-inf"))) > 1e-5:
            errors.append(f"{directory.name}: adapter reload margin mismatch")
        if metrics.get("paid_spend") != 0 or not metrics.get("margin_improved"):
            errors.append(f"{directory.name}: alignment acceptance criteria failed")
        checked += 1
        continue
    if config.get("purpose", "").startswith("real-repository environment"):
        for filename, key in (("LICENSE", "license_sha256"),
                              ("upstream.patch", "upstream_patch_sha256")):
            if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != config[key]:
                errors.append(f"{directory.name}: altered {filename}")
        buggy = json.loads((directory / "buggy.json").read_text())
        fixed = json.loads((directory / "fixed.json").read_text())
        if metrics["buggy_failed"] != (buggy["returncode"] != 0):
            errors.append(f"{directory.name}: buggy outcome mismatch")
        if metrics["fixed_passed"] != (fixed["returncode"] == 0):
            errors.append(f"{directory.name}: fixed outcome mismatch")
        checked += 1
        continue
    if config.get("cohort", "").startswith("real-repository feasibility"):
        rows = [json.loads(path.read_text()) for path in directory.glob("seed-*.json")]
        expected = len(config["seeds"].split(","))
        if len(rows) != expected or metrics["attempted"] != expected:
            errors.append(f"{directory.name}: real-repo cohort count mismatch")
        if metrics["successful"] != sum(row["success"] for row in rows):
            errors.append(f"{directory.name}: real-repo metric mismatch")
        checked += 1
        continue
    if "adapter_run" in config:
        rows = metrics.get("rows", [])
        if len(rows) != 6 or {r.get("condition") for r in rows} != {"base", "adapter"}:
            errors.append(f"{directory.name}: invalid adapter evaluation cohort")
        if metrics.get("base_exact") != sum(r.get("exact_repair", False) for r in rows if r.get("condition") == "base"):
            errors.append(f"{directory.name}: base aggregation mismatch")
        if metrics.get("adapter_exact") != sum(r.get("exact_repair", False) for r in rows if r.get("condition") == "adapter"):
            errors.append(f"{directory.name}: adapter aggregation mismatch")
        checked += 1
        continue
    if config.get("purpose", "").startswith("training-mechanics"):
        hashes = json.loads((directory / "parameter_hashes.json").read_text())
        changed = {name for name in hashes["before"] if hashes["before"][name] != hashes["after"].get(name)}
        if set(hashes["before"]) != set(hashes["after"]):
            errors.append(f"{directory.name}: parameter set changed")
        if not changed or any(not name.endswith(("lora_a", "lora_b")) for name in changed):
            errors.append(f"{directory.name}: invalid frozen/adapter parameter changes")
        if changed != set(metrics["changed_adapter_tensors"]):
            errors.append(f"{directory.name}: changed tensor report mismatch")
        if len(metrics["losses_before_update"]) != config["steps"]:
            errors.append(f"{directory.name}: missing training step")
        for filename, key in (("adapter_pilot.py", "script_sha256"),
                              ("training_math.py", "objective_sha256"),
                              ("gguf_backend.py", "mapping_sha256")):
            if key in config and hashlib.sha256((directory / filename).read_bytes()).hexdigest() != config[key]:
                errors.append(f"{directory.name}: changed training source {filename}")
        if "messages_sha256" in config:
            candidate = Path(__file__).resolve().parents[1] / config["messages_file"]
            if hashlib.sha256(candidate.read_bytes()).hexdigest() != config["messages_sha256"]:
                errors.append(f"{directory.name}: training messages changed")
        adapter = directory / "adapters.safetensors"
        if not adapter.exists() or hashlib.sha256(adapter.read_bytes()).hexdigest() != metrics["adapter_sha256"]:
            errors.append(f"{directory.name}: missing or altered local adapter")
        checked += 1
        continue
    rows = []
    for path in directory.glob("*.json"):
        row = json.loads(path.read_text())
        if "task" in row and "success" in row:
            rows.append(row)
    expected = config["limit"] * (len(config["seeds"].split(",")) if config["mode"] == "baseline" else 1)
    if metrics["attempted"] != expected or len(rows) != expected:
        errors.append(f"{directory.name}: cohort count mismatch")
    if sum(r["success"] for r in rows) != metrics["successful"]:
        errors.append(f"{directory.name}: metric aggregation mismatch")
    identities = [(r["task"], r.get("seed")) for r in rows]
    if len(set(identities)) != len(identities):
        errors.append(f"{directory.name}: duplicate episode identity")
    for filename, digest in config["source_hashes"].items():
        snapshot = directory / filename
        if not snapshot.exists():
            if directory.name not in {"EXP-FRL-000", "EXP-FRL-001"}:
                errors.append(f"{directory.name}: missing source snapshot {filename}")
            continue
        if hashlib.sha256(snapshot.read_bytes()).hexdigest() != digest:
            errors.append(f"{directory.name}: altered source snapshot {filename}")
    checked += 1
if errors:
    raise SystemExit("\n".join(errors))
print(f"PASS: {checked} complete runs have internally consistent evidence.")
print("Historical EXP-FRL-000/001 lack source snapshots and have documented invalid grader evidence.")
