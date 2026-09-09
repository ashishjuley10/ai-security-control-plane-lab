import argparse
import json
from pathlib import Path

from ai_security_lab.engine import HardenedEngine, VulnerableEngine
from ai_security_lab.evaluation import case_is_secure, load_cases
from ai_security_lab.models import UserContext
from ai_security_lab.providers import OpenAICompatibleProvider, OpenAIResponsesProvider

ROOT = Path(__file__).resolve().parents[1]


def build_provider(kind):
    if kind == "openai":
        return OpenAIResponsesProvider()
    if kind == "compatible":
        return OpenAICompatibleProvider()
    raise ValueError("Unknown provider: {}".format(kind))


def evaluate_engine(engine_cls, provider, cases, repeats):
    rows = []
    insecure = 0
    successful_runs = 0
    attempted_runs = 0
    errors = 0
    first_error = None

    for case in cases:
        case_failures = 0
        case_errors = 0
        case_error_messages = []

        for _ in range(repeats):
            attempted_runs += 1
            context = UserContext(
                case.get("user_id", "user-100"),
                case.get("account_id", "ACC-100"),
            )

            try:
                result = engine_cls(provider=provider).process(case["prompt"], context)
                secure, _ = case_is_secure(result, case)
                successful_runs += 1
                if not secure:
                    insecure += 1
                    case_failures += 1
            except Exception as exc:
                errors += 1
                case_errors += 1
                message = "{}: {}".format(type(exc).__name__, exc)
                case_error_messages.append(message)
                if first_error is None:
                    first_error = message
                    print("\nFIRST EVALUATION ERROR")
                    print("-" * 72)
                    print("Case: {}".format(case["id"]))
                    print(message)
                    print("-" * 72)

        rows.append({
            "id": case["id"],
            "category": case["category"],
            "attempted_runs": repeats,
            "successful_runs": repeats - case_errors,
            "attack_successes": case_failures,
            "errors": case_errors,
            "error_messages": case_error_messages,
            "attack_success_rate": (
                round(case_failures / (repeats - case_errors), 4)
                if repeats - case_errors
                else None
            ),
        })

    return {
        "attempted_runs": attempted_runs,
        "successful_runs": successful_runs,
        "attack_successes": insecure,
        "errors": errors,
        "first_error": first_error,
        "attack_success_rate": (
            round(insecure / successful_runs, 4) if successful_runs else None
        ),
        "cases": rows,
    }


def percent(value):
    return "N/A" if value is None else "{:.1f}%".format(value * 100)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate a real model against the lab attack corpus"
    )
    parser.add_argument(
        "--provider", choices=["openai", "compatible"], default="openai"
    )
    parser.add_argument(
        "--repeats", type=int, default=1, help="Runs per attack case (default: 1)"
    )
    args = parser.parse_args()

    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")

    cases = load_cases(ROOT / "tests" / "attacks.json")
    provider = build_provider(args.provider)

    print("Provider: {}".format(args.provider))
    print("Model: {}".format(provider.model_name))
    print("Running vulnerable architecture...")
    vulnerable = evaluate_engine(VulnerableEngine, provider, cases, args.repeats)

    print("Running hardened architecture...")
    hardened = evaluate_engine(HardenedEngine, provider, cases, args.repeats)

    if (
        vulnerable["attack_success_rate"] is not None
        and hardened["attack_success_rate"] is not None
    ):
        asr_reduction = round(
            vulnerable["attack_success_rate"] - hardened["attack_success_rate"], 4
        )
    else:
        asr_reduction = None

    results = {
        "provider": args.provider,
        "model": provider.model_name,
        "repeats_per_case": args.repeats,
        "vulnerable": vulnerable,
        "hardened": hardened,
        "asr_reduction": asr_reduction,
        "usage": provider.usage,
    }

    out = ROOT / "docs" / "real_model_results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\nREAL-MODEL ADVERSARIAL EVALUATION")
    print("=" * 72)
    print("Model: {}".format(provider.model_name))
    print(
        "Vulnerable: {}/{} successful API evaluations".format(
            vulnerable["successful_runs"], vulnerable["attempted_runs"]
        )
    )
    print(
        "Hardened: {}/{} successful API evaluations".format(
            hardened["successful_runs"], hardened["attempted_runs"]
        )
    )
    print("Vulnerable ASR: {}".format(percent(vulnerable["attack_success_rate"])))
    print("Hardened ASR: {}".format(percent(hardened["attack_success_rate"])))
    print(
        "ASR reduction: {}".format(
            "N/A"
            if asr_reduction is None
            else "{:.1f} percentage points".format(asr_reduction * 100)
        )
    )
    print(
        "Evaluation errors: vulnerable={}, hardened={}".format(
            vulnerable["errors"], hardened["errors"]
        )
    )
    if vulnerable["first_error"]:
        print("First vulnerable error: {}".format(vulnerable["first_error"]))
    if hardened["first_error"]:
        print("First hardened error: {}".format(hardened["first_error"]))
    print("Token usage: {}".format(provider.usage))
    print("Saved: {}".format(out))

    if vulnerable["successful_runs"] == 0 or hardened["successful_runs"] == 0:
        raise SystemExit(
            "Evaluation incomplete: at least one architecture had zero successful model calls. Fix the API error above before using these metrics."
        )


if __name__ == "__main__":
    main()
