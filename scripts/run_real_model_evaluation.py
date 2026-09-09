import argparse
import json
from pathlib import Path

from ai_security_lab.engine import HardenedEngine, VulnerableEngine
from ai_security_lab.evaluation import case_is_secure, load_cases
from ai_security_lab.models import UserContext
from ai_security_lab.providers import OpenAICompatibleProvider

ROOT = Path(__file__).resolve().parents[1]


def evaluate_engine(engine_cls, provider, cases, repeats):
    rows = []
    insecure = 0
    total_runs = 0

    for case in cases:
        case_failures = 0
        for _ in range(repeats):
            context = UserContext(case.get("user_id", "user-100"), case.get("account_id", "ACC-100"))
            result = engine_cls(provider=provider).process(case["prompt"], context)
            secure, failures = case_is_secure(result, case)
            total_runs += 1
            if not secure:
                insecure += 1
                case_failures += 1

        rows.append({
            "id": case["id"],
            "category": case["category"],
            "runs": repeats,
            "attack_successes": case_failures,
            "attack_success_rate": round(case_failures / repeats, 4),
        })

    return {
        "runs": total_runs,
        "attack_successes": insecure,
        "attack_success_rate": round(insecure / total_runs, 4) if total_runs else 0.0,
        "cases": rows,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate a real OpenAI-compatible model against the lab attack corpus")
    parser.add_argument("--repeats", type=int, default=3, help="Runs per attack case (default: 3)")
    args = parser.parse_args()

    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")

    cases = load_cases(ROOT / "tests" / "attacks.json")
    provider = OpenAICompatibleProvider()

    print("Running vulnerable architecture against real model...")
    vulnerable = evaluate_engine(VulnerableEngine, provider, cases, args.repeats)

    print("Running hardened architecture against real model...")
    hardened = evaluate_engine(HardenedEngine, provider, cases, args.repeats)

    results = {
        "model_source": "OpenAI-compatible endpoint from environment",
        "repeats_per_case": args.repeats,
        "vulnerable": vulnerable,
        "hardened": hardened,
        "asr_reduction": round(vulnerable["attack_success_rate"] - hardened["attack_success_rate"], 4),
    }

    out = ROOT / "docs" / "real_model_results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\nREAL-MODEL ADVERSARIAL EVALUATION")
    print("=" * 72)
    print("Runs per architecture: {}".format(vulnerable["runs"]))
    print("Vulnerable ASR: {:.1f}%".format(vulnerable["attack_success_rate"] * 100))
    print("Hardened ASR: {:.1f}%".format(hardened["attack_success_rate"] * 100))
    print("ASR reduction: {:.1f} percentage points".format(results["asr_reduction"] * 100))
    print("Saved: {}".format(out))


if __name__ == "__main__":
    main()
