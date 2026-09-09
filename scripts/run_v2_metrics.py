import json
from pathlib import Path

from ai_security_lab.evaluation import evaluate, load_cases
from ai_security_lab.engine import HardenedEngine
from ai_security_lab.models import UserContext

ROOT = Path(__file__).resolve().parents[1]

attack_cases = load_cases(ROOT / "tests" / "attacks.json")
attack_totals, attack_rows = evaluate(attack_cases)

baseline_attack_success = attack_totals["total"] - attack_totals["vulnerable_secure"]
hardened_attack_success = attack_totals["total"] - attack_totals["hardened_secure"]

baseline_asr = baseline_attack_success / attack_totals["total"] if attack_totals["total"] else 0.0
hardened_asr = hardened_attack_success / attack_totals["total"] if attack_totals["total"] else 0.0

benign_cases = json.loads((ROOT / "tests" / "benign.json").read_text(encoding="utf-8"))
benign_passed = 0
benign_rows = []

for case in benign_cases:
    engine = HardenedEngine()
    result = engine.process(case["prompt"], UserContext("user-100", "ACC-100"))
    failures = []

    required_tool = case.get("required_tool")
    if required_tool and required_tool not in result.executed_tools:
        failures.append("expected tool not executed: {}".format(required_tool))

    must_contain = case.get("must_contain")
    if must_contain and must_contain.lower() not in result.output.lower():
        failures.append("expected output missing: {}".format(must_contain))

    success = not failures
    benign_passed += int(success)
    benign_rows.append({
        "id": case["id"],
        "success": success,
        "failures": failures,
    })

benign_tsr = benign_passed / len(benign_cases) if benign_cases else 0.0

metrics = {
    "adversarial_cases": attack_totals["total"],
    "baseline_attack_success_rate": round(baseline_asr, 4),
    "hardened_attack_success_rate": round(hardened_asr, 4),
    "attack_success_rate_reduction": round(baseline_asr - hardened_asr, 4),
    "benign_cases": len(benign_cases),
    "benign_task_success_rate": round(benign_tsr, 4),
    "attack_rows": attack_rows,
    "benign_rows": benign_rows,
}

(ROOT / "docs" / "v0.2_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

lines = [
    "# v0.2 Security Metrics",
    "",
    "> Deterministic control-plane evaluation. These metrics measure defined",
    "> security oracles and legitimate task retention, not foundation-model safety.",
    "",
    "| Metric | Result |",
    "|---|---:|",
    "| Adversarial cases | {} |".format(metrics["adversarial_cases"]),
    "| Vulnerable baseline ASR | {:.1f}% |".format(metrics["baseline_attack_success_rate"] * 100),
    "| Hardened control-plane ASR | {:.1f}% |".format(metrics["hardened_attack_success_rate"] * 100),
    "| ASR reduction | {:.1f} percentage points |".format(metrics["attack_success_rate_reduction"] * 100),
    "| Benign cases | {} |".format(metrics["benign_cases"]),
    "| Hardened benign task success | {:.1f}% |".format(metrics["benign_task_success_rate"] * 100),
    "",
    "## Interpretation",
    "",
    "The hardened architecture is evaluated on both security and usefulness. A",
    "system that blocks every request would score well on attack resistance but",
    "fail the benign task metric. v0.2 tracks both sides of that trade-off.",
]

(ROOT / "docs" / "v0.2_metrics.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))

if benign_passed != len(benign_cases):
    raise SystemExit(1)
