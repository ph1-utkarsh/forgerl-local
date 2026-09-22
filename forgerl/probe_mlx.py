"""Check local Metal autodiff before any model download or training promise."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    import mlx.core as mx
    metadata = {"platform": platform.platform(), "mlx_version": importlib.metadata.version("mlx"),
                "metal_available": mx.metal.is_available(), "paid_spend": 0,
                "interpretation": "autodiff smoke test only; no LLM weights trained"}
    start = time.monotonic()
    x = mx.array([1.0, 2.0, 3.0])
    target = 2.0 * x

    def loss(weight):
        return mx.mean((weight * x - target) ** 2)

    weight = mx.array(0.0)
    before = loss(weight).item()
    for _ in range(10):
        gradient = mx.grad(loss)(weight)
        weight = weight - 0.05 * gradient
        mx.eval(weight)
    metadata.update(loss_before=before, loss_after=loss(weight).item(),
                    weight=weight.item(), seconds=time.monotonic() - start)
    metadata["passed"] = metadata["loss_after"] < before and metadata["metal_available"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata, indent=2))
    if not metadata["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
