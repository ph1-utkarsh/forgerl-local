"""Regrade preserved final patches without making any model calls."""
import argparse
import hashlib
import json
from pathlib import Path
from qualification import TASKS
from runner import grade, pinned_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    image = pinned_image()
    tasks = {t.name: t for t in TASKS}
    results = []
    for path in sorted(args.source.glob("*.json")):
        original = json.loads(path.read_text())
        if "trace" not in original:
            continue
        hidden = grade(original["source"], tasks[original["task"]].hidden, image)
        record = {"task": original["task"], "seed": original["seed"],
                  "original_artifact_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "original_success": original["success"], "hidden": hidden,
                  "success": original["finished"] and hidden["passed"]}
        (args.output / path.name).write_text(json.dumps(record, indent=2))
        results.append(record)
    summary = {"attempted": len(results), "successful": sum(r["success"] for r in results),
               "changed_outcomes": sum(r["success"] != r["original_success"] for r in results),
               "image": image, "model_calls": 0,
               "grader_sha256": hashlib.sha256((Path(__file__).parent / "runner.py").read_bytes()).hexdigest()}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
