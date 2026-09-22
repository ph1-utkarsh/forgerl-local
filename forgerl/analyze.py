"""Summarize all episodes including failures; never turn fixtures into claims."""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics


def summarize(directory):
    rows = []
    for path in sorted(directory.glob("*.json")):
        row = json.loads(path.read_text())
        if "trace" in row:
            rows.append(row)
    if not rows:
        raise ValueError("no episode records")
    categories = Counter()
    actions = invalid = 0
    per_task = {}
    for row in rows:
        actions += len(row["trace"])
        bad = sum(not step.get("valid", False) for step in row["trace"])
        invalid += bad
        if row["success"]:
            category = "success"
        elif any(step.get("transport_failure") for step in row["trace"]):
            category = "transport_failure"
        elif not row["finished"]:
            category = "action_budget_or_protocol"
        else:
            category = "incorrect_patch"
        categories[category] += 1
        counts = per_task.setdefault(row["task"], {"attempted": 0, "successful": 0})
        counts["attempted"] += 1
        counts["successful"] += int(row["success"])
    return {"attempted": len(rows), "successful": sum(r["success"] for r in rows),
            "hidden_pass_even_without_finish": sum(r["hidden"]["passed"] for r in rows),
            "actions": actions, "invalid_actions": invalid,
            "valid_action_fraction": (actions-invalid)/actions if actions else None,
            "seconds_total": sum(r["seconds"] for r in rows),
            "seconds_median": statistics.median(r["seconds"] for r in rows),
            "prompt_tokens": sum(r["prompt_tokens"] for r in rows),
            "output_tokens": sum(r["output_tokens"] for r in rows),
            "failure_categories": dict(categories), "per_task": per_task,
            "interpretation": "qualification fixtures only; no population or post-training inference"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.directory), indent=2))
