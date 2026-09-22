"""Qualify pinned Tornado BugsInPy bug 5 under its Python runtime."""
import argparse, hashlib, io, json, subprocess, tarfile, tempfile, time
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/tornado"
BUGGY = "2d4053daa56c609d642b214399e046671d4a593e"
FIXED = "886643965b5cb782503d8d7b374b7a794ec2077b"
IMAGE = "python:3.8-slim"
TEST_FILE = "tornado/test/ioloop_test.py"
TEST = "tornado.test.ioloop_test.TestPeriodicCallbackMath.test_clock_backwards"


def git(*args):
    return subprocess.run(["git", "-C", str(SOURCE), *args], check=True,
                          capture_output=True).stdout


def extract(commit, destination):
    with tarfile.open(fileobj=io.BytesIO(git("archive", "--format=tar", commit))) as stream:
        safe = []
        for member in stream.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"unsafe member: {member.name}")
            if not member.issym() and not member.islnk():
                safe.append(member)
        stream.extractall(destination, members=safe)


def run(commit, image_id, frozen_test):
    with tempfile.TemporaryDirectory(prefix="frl-tornado-") as temporary:
        checkout = Path(temporary); extract(commit, checkout)
        (checkout / TEST_FILE).write_bytes(frozen_test)
        start = time.monotonic()
        result = subprocess.run(["docker", "run", "--rm", "--pull=never", "--network=none",
            "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
            "--pids-limit=128", "--memory=512m", "--memory-swap=512m", "--cpus=1",
            "--user=65534:65534", "--log-driver=none",
            "--mount", f"type=bind,src={checkout},dst=/repo,readonly", "--workdir=/repo",
            "--env=PYTHONDONTWRITEBYTECODE=1", image_id, "python", "-B", "-m", "unittest", "-q", TEST],
            capture_output=True, timeout=60)
        return {"commit": commit, "returncode": result.returncode,
                "stdout": result.stdout.decode(errors="replace")[-16000:],
                "stderr": result.stderr.decode(errors="replace")[-16000:],
                "seconds": time.monotonic() - start}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--run-id", required=True); args = parser.parse_args()
    out = ROOT / "forgerl/experiments" / args.run_id; out.mkdir(parents=True, exist_ok=False)
    image_id = subprocess.run(["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
                              check=True, capture_output=True, text=True).stdout.strip()
    frozen = git("show", f"{FIXED}:{TEST_FILE}"); license_data = git("show", f"{BUGGY}:LICENSE")
    patch = git("diff", "--binary", BUGGY, FIXED)
    digest = lambda data: hashlib.sha256(data).hexdigest()
    config = {"purpose": "real-repository environment and oracle qualification only",
        "dataset": "BugsInPy", "project": "tornado", "bug_id": 5,
        "source_url": "https://github.com/tornadoweb/tornado", "buggy_commit": BUGGY,
        "fixed_commit": FIXED, "test": TEST, "frozen_test_source": f"{FIXED}:{TEST_FILE}",
        "frozen_test_sha256": digest(frozen), "license": "Apache-2.0",
        "license_sha256": digest(license_data), "upstream_patch_sha256": digest(patch),
        "image": IMAGE, "image_id": image_id, "network": "none", "paid_spend": 0}
    (out / "config.json").write_text(json.dumps(config, indent=2)); (out / "LICENSE").write_bytes(license_data)
    (out / "upstream.patch").write_bytes(patch); (out / "frozen_test.py").write_bytes(frozen)
    (out / "tornado_probe.py").write_bytes(Path(__file__).read_bytes())
    buggy, fixed = run(BUGGY, image_id, frozen), run(FIXED, image_id, frozen)
    (out / "buggy.json").write_text(json.dumps(buggy, indent=2)); (out / "fixed.json").write_text(json.dumps(fixed, indent=2))
    metrics = {"buggy_failed": buggy["returncode"] != 0, "fixed_passed": fixed["returncode"] == 0,
               "qualified": buggy["returncode"] != 0 and fixed["returncode"] == 0, "paid_spend": 0}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2)); print(json.dumps(metrics, indent=2))
    if not metrics["qualified"]: raise SystemExit(1)


if __name__ == "__main__": main()
