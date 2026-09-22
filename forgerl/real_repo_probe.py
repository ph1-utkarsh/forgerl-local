"""Qualify one pinned BugsInPy task in an isolated local container.

This is dataset/environment qualification, not an agent or training run.
"""
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import tempfile
import time
import argparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/youtube-dl"
BUGGY = "99036a1298089068dcf80c0985bfcc3f8c24f281"
FIXED = "1cc47c667419e0eadc0a6989256ab7b276852adf"
IMAGE = "python:3.12-slim"
TEST = "test.test_utils.TestUtil.test_match_str"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", str(SOURCE), *args], check=True,
                          capture_output=True).stdout


def extract(commit, destination):
    archive = git("archive", "--format=tar", commit)
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise ValueError(f"unsafe archive member: {member.name}")
        # Members were explicitly constrained above; Python 3.9 has no filter=.
        stream.extractall(destination)


def run(commit, image_id):
    with tempfile.TemporaryDirectory(prefix="frl-real-") as temporary:
        checkout = Path(temporary)
        extract(commit, checkout)
        # The buggy revision predates the regression assertions. Freeze the
        # fixed revision's test file and use it unchanged for both revisions.
        (checkout / "test/test_utils.py").write_bytes(
            git("show", f"{FIXED}:test/test_utils.py"))
        start = time.monotonic()
        command = ["docker", "run", "--rm", "--pull=never", "--network=none",
                   "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
                   "--pids-limit=128", "--memory=512m", "--memory-swap=512m", "--cpus=1",
                   "--user=65534:65534", "--log-driver=none",
                   "--mount", f"type=bind,src={checkout},dst=/repo,readonly",
                   "--workdir=/repo", "--env=PYTHONDONTWRITEBYTECODE=1", image_id,
                   "python", "-B", "-m", "unittest", "-q", TEST]
        result = subprocess.run(command, capture_output=True, timeout=60)
        return {"commit": commit, "returncode": result.returncode,
                "stdout": result.stdout.decode(errors="replace")[-16000:],
                "stderr": result.stderr.decode(errors="replace")[-16000:],
                "seconds": time.monotonic() - start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not args.run_id.startswith("EXP-FRL-") or not args.run_id.replace("-", "").isalnum():
        parser.error("invalid run ID")
    out = ROOT / "forgerl/experiments" / args.run_id
    out.mkdir(parents=True, exist_ok=False)
    image_id = subprocess.run(["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
                              check=True, capture_output=True, text=True).stdout.strip()
    if not image_id.startswith("sha256:"):
        raise RuntimeError("unresolved container image")
    license_data = git("show", f"{BUGGY}:LICENSE")
    patch = git("diff", "--binary", BUGGY, FIXED)
    frozen_test = git("show", f"{FIXED}:test/test_utils.py")
    config = {"dataset": "BugsInPy", "project": "youtube-dl", "bug_id": 1,
              "source_url": "https://github.com/ytdl-org/youtube-dl",
              "buggy_commit": BUGGY, "fixed_commit": FIXED, "test": TEST,
              "image": IMAGE, "image_id": image_id, "network": "none",
              "license": "Unlicense", "license_sha256": sha256(license_data),
              "upstream_patch_sha256": sha256(patch), "paid_spend": 0,
              "frozen_test_source": f"{FIXED}:test/test_utils.py",
              "frozen_test_sha256": sha256(frozen_test),
              "purpose": "real-repository environment and oracle qualification only"}
    (out / "config.json").write_text(json.dumps(config, indent=2))
    (out / "LICENSE").write_bytes(license_data)
    (out / "upstream.patch").write_bytes(patch)
    (out / "frozen_test_utils.py").write_bytes(frozen_test)
    (out / "real_repo_probe.py").write_bytes(Path(__file__).read_bytes())
    buggy = run(BUGGY, image_id)
    fixed = run(FIXED, image_id)
    (out / "buggy.json").write_text(json.dumps(buggy, indent=2))
    (out / "fixed.json").write_text(json.dumps(fixed, indent=2))
    metrics = {"buggy_failed": buggy["returncode"] != 0,
               "fixed_passed": fixed["returncode"] == 0,
               "qualified": buggy["returncode"] != 0 and fixed["returncode"] == 0,
               "paid_spend": 0}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
    if not metrics["qualified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
