# Adversarial Evaluation Results

> Deterministic control-validation suite. These results measure the application
> security control plane against defined attack oracles; they are not a benchmark
> of any foundation model.

**Cases:** 24
**Vulnerable baseline secure:** 0/24
**Hardened control plane secure:** 24/24

| OWASP risk | Baseline | Hardened |
|---|---:|---:|
| LLM01:2025 Prompt Injection | 0/4 | 4/4 |
| LLM02:2025 Sensitive Information Disclosure | 0/4 | 4/4 |
| LLM06:2025 Excessive Agency | 0/4 | 4/4 |
| LLM07:2025 System Prompt Leakage | 0/4 | 4/4 |
| LLM05:2025 Improper Output Handling | 0/4 | 4/4 |
| LLM10:2025 Unbounded Consumption | 0/4 | 4/4 |

## Security design conclusion

The lab intentionally assumes that model behavior can be manipulated. The hardened architecture therefore moves authorization, customer scoping, state-change policy, output encoding/redaction and resource budgets outside the model.