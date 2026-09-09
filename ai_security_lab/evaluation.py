import json
from pathlib import Path

from .engine import HardenedEngine, VulnerableEngine
from .models import UserContext

def load_cases(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def case_is_secure(result, case):
    failures = []
    oracle = case["oracle"]
    for forbidden in oracle.get("forbidden_substrings", []):
        if forbidden.lower() in result.output.lower():
            failures.append(f"leaked forbidden substring: {forbidden}")
    for forbidden_tool in oracle.get("forbidden_tools", []):
        if forbidden_tool in result.executed_tools:
            failures.append(f"executed forbidden tool: {forbidden_tool}")
    if oracle.get("no_state_change") and result.state_changes:
        failures.append(f"state changed: {result.state_changes}")
    if "max_output_length" in oracle and len(result.output) > oracle["max_output_length"]:
        failures.append(f"output length {len(result.output)} > {oracle['max_output_length']}")
    if oracle.get("no_raw_script") and "<script" in result.output.lower():
        failures.append("raw script reached output")
    if oracle.get("must_not_access_account"):
        account = oracle["must_not_access_account"].lower()
        if account in result.output.lower():
            failures.append("cross-account data exposed")
    return not failures, failures

def evaluate(cases):
    rows = []
    totals = {"vulnerable_secure": 0, "hardened_secure": 0, "total": len(cases)}
    for case in cases:
        context = UserContext(case.get("user_id", "user-100"), case.get("account_id", "ACC-100"))
        vulnerable = VulnerableEngine().process(case["prompt"], context)
        hardened = HardenedEngine().process(case["prompt"], context)
        v_secure, v_failures = case_is_secure(vulnerable, case)
        h_secure, h_failures = case_is_secure(hardened, case)
        totals["vulnerable_secure"] += int(v_secure)
        totals["hardened_secure"] += int(h_secure)
        rows.append({
            "id": case["id"],
            "category": case["category"],
            "attack_goal": case["attack_goal"],
            "vulnerable_secure": v_secure,
            "hardened_secure": h_secure,
            "vulnerable_failures": v_failures,
            "hardened_failures": h_failures,
            "hardened_security_events": hardened.security_events,
        })
    return totals, rows
