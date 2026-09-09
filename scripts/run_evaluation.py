import json
from collections import defaultdict
from pathlib import Path

from ai_security_lab.evaluation import evaluate, load_cases

ROOT = Path(__file__).resolve().parents[1]
cases = load_cases(ROOT / "tests" / "attacks.json")
totals, rows = evaluate(cases)

by_category = defaultdict(lambda: {"total": 0, "vulnerable_secure": 0, "hardened_secure": 0})
for row in rows:
    c = by_category[row["category"]]
    c["total"] += 1
    c["vulnerable_secure"] += int(row["vulnerable_secure"])
    c["hardened_secure"] += int(row["hardened_secure"])

results = {"totals": totals, "by_category": dict(by_category), "cases": rows}
(ROOT / "docs" / "evaluation_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

lines = [
    "# Adversarial Evaluation Results",
    "",
    "> Deterministic control-validation suite. These results measure the application",
    "> security control plane against defined attack oracles; they are not a benchmark",
    "> of any foundation model.",
    "",
    f"**Cases:** {totals['total']}",
    f"**Vulnerable baseline secure:** {totals['vulnerable_secure']}/{totals['total']}",
    f"**Hardened control plane secure:** {totals['hardened_secure']}/{totals['total']}",
    "",
    "| OWASP risk | Baseline | Hardened |",
    "|---|---:|---:|",
]
for category, values in by_category.items():
    lines.append(f"| {category} | {values['vulnerable_secure']}/{values['total']} | {values['hardened_secure']}/{values['total']} |")
lines += ["", "## Security design conclusion", "", "The lab intentionally assumes that model behavior can be manipulated. The hardened architecture therefore moves authorization, customer scoping, state-change policy, output encoding/redaction and resource budgets outside the model."]
(ROOT / "docs" / "evaluation_results.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
