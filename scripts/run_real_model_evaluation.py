import argparse
import json
import random
import time
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


def error_message(exc):
    return "{}: {}".format(type(exc).__name__, exc)


def is_rate_limit_error(message):
    text = message.lower()
    return "rate_limit_exceeded" in text or "rate limit reached" in text


def is_credit_error(message):
    text = message.lower()
    return "credit_balance_exhausted" in text or "no credits remaining" in text


def evaluate_engine(engine_cls, provider, cases, repeats, delay, max_retries):
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

            result = None
            final_error = None

            for retry in range(max_retries + 1):
                try:
                    result = engine_cls(provider=provider).process(case["prompt"], context)
                    final_error = None
                    break
                except Exception as exc:
                    message = error_message(exc)
                    final_error = message

                    if is_credit_error(message):
                        # Billing/quota errors are not transient rate limits. Do not
                        # burn retries; the account balance must be fixed first.
                        break

                    if is_rate_limit_error(message) and retry < max_retries:
                        backoff = max(delay, 6.5) * (2 ** retry)
                        backoff += random.uniform(0.1, 0.8)
                        print(
                            "Rate limit on {}. Retry {}/{} in {:.1f}s...".format(
                                case["id"], retry + 1, max_retries, backoff
                            )
                        )
                        time.sleep(backoff)
                        continue

                    break

            if result is not None:
                secure, _ = case_is_secure(result, case)
                successful_runs += 1
                if not secure:
                    insecure += 1
                    case_failures += 1
            else:
                errors += 1
                case_errors += 1
                case_error_messages.append(final_error)
                if first_error is None:
                    first_error = final_error
                    print("\nFIRST EVALUATION ERROR")
                    print("-" * 72)
                    print("Case: {}".format(case["id"]))
                    print(final_error)
                    print("-" * 72)

            # Pace every case, not only failed ones. The account currently has a
            # low requests-per-minute limit, so bursts would otherwise create 429s.
            if delay > 0:
                time.sleep(delay)

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
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Seconds between model calls. OpenAI defaults to 7s to respect low-tier RPM limits.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=4,
        help="Retries for temporary rate-limit errors (default: 4)",
    )
    args = parser.parse_args()

    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")
    if args.max_retries < 0:
        raise SystemExit("--max-retries must be >= 0")

    delay = args.delay
    if delay is None:
        delay = 7.0 if args.provider == "openai" else 0.0
    if delay < 0:
        raise SystemExit("--delay must be >= 0")

    cases = load_cases(ROOT / "tests" / "attacks.json")
    provider = build_provider(args.provider)

    print("Provider: {}".format(args.provider))
    print("Model: {}".format(provider.model_name))
    print("Pacing: {:.1f}s between calls; max rate-limit retries: {}".format(delay, args.max_retries))
    print("Running vulnerable architecture...")
    vulnerable = evaluate_engine(
        VulnerableEngine, provider, cases, args.repeats, delay, args.max_retries
    )

    print("Running hardened architecture...")
    hardened = evaluate_engine(
        HardenedEngine, provider, cases, args.repeats, delay, args.max_retries
    )

    complete = vulnerable["errors"] == 0 and hardened["errors"] == 0

    if complete:
        asr_reduction = round(
            vulnerable["attack_success_rate"] - hardened["attack_success_rate"], 4
        )
    else:
        # Do not publish a reduction calculated from incomplete/asymmetric samples.
        asr_reduction = None

    results = {
        "provider": args.provider,
        "model": provider.model_name,
        "repeats_per_case": args.repeats,
        "delay_seconds": delay,
        "complete": complete,
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
            "N/A - evaluation incomplete"
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

    if not complete:
        raise SystemExit(
            "Evaluation incomplete: API/model errors occurred. Do not use the ASR metrics until a run completes with 0 errors."
        )


if __name__ == "__main__":
    main()
