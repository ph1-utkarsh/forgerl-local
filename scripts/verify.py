"""Validate publishable ForgeRL claims without excluded model/adapter binaries."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
exp = ROOT / "forgerl/experiments"
sft = json.loads((exp / "EXP-FRL-012/metrics.json").read_text())
dpo = json.loads((exp / "EXP-FRL-013/metrics.json").read_text())
grpo = json.loads((exp / "EXP-FRL-014/metrics.json").read_text())
dpo_eval = json.loads((exp / "EXP-FRL-015/metrics.json").read_text())
grpo_eval = json.loads((exp / "EXP-FRL-016/metrics.json").read_text())

assert sft["base_exact"] == sft["adapter_exact"] == 0
assert dpo_eval["base_exact"] == dpo_eval["adapter_exact"] == 0
assert grpo_eval["base_exact"] == grpo_eval["adapter_exact"] == 0
for row, objective in ((dpo, "dpo"), (grpo, "grpo")):
    assert row["objective"] == objective
    assert row["margin_improved"] and row["frozen_base_unchanged"]
    assert abs(row["final_margin"] - row["reload_margin"]) < 1e-5
    assert row["paid_spend"] == 0
assert (exp / "EXP-FRL-015/FAILURE.md").exists()
assert (exp / "EXP-FRL-016/FAILURE.md").exists()
print("FORGERL VERIFY: PASS")
