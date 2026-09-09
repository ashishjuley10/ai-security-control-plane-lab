import json
from pathlib import Path

from ai_security_lab.engine import HardenedEngine
from ai_security_lab.models import UserContext

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests" / "benign.json").read_text(encoding="utf-8"))

passed = 0
rows = []

print("\nBENIGN TASK EVALUATION")
print("=" * 72)

for case in CASES:
    engine = HardenedEngine()
    context = UserContext("user-100", "ACC-100")
    result = engine.process(case["prompt"], context)
    failures = []

    required_tool = case.get("required_tool")
    if required_tool and required_tool not in result.executed_tools:
        failures.append("expected tool not executed: {}".format(required_tool))

    must_contain = case.get("must_contain")
    if must_contain and must_contain.lower() not in result.output.lower():
        failures.append("expected output missing: {}".format(must_contain))

    success = not failures
    passed += int(success)
    rows.append({
        "id": case["id"],
        "success": success,
        "executed_tools": result.executed_tools,
        "security_events": result.security_events,
        "failures": failures,
    })

    print("{} | {} | {}".format(case["id"], "PASS" if success else "FAIL", case["prompt"]))
    for failure in failures:
        print("    - {}".format(failure))

summary = {
    "total": len(CASES),
    "passed": passed,
    "task_success_rate": round(passed / len(CASES), 4) if CASES else 0.0,
    "cases": rows,
}

(ROOT / "docs" / "benign_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

print("=" * 72)
print("Benign task success: {}/{} ({:.1f}%)".format(passed, len(CASES), summary["task_success_rate"] * 100))

if passed != len(CASES):
    raise SystemExit(1)
