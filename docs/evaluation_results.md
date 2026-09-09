# Adversarial Evaluation Results

> Deterministic control-validation suite. These results measure the application security control plane against defined attack oracles; they are not a benchmark of any foundation model.

**Cases:** 24  
**Vulnerable baseline secure:** 0/24  
**Hardened control plane secure:** 24/24

| OWASP risk | Baseline | Hardened |
|---|---:|---:|
| LLM01:2026 Prompt Injection | 0/4 | 4/4 |
| LLM02:2026 Sensitive Information Disclosure | 0/4 | 4/4 |
| LLM03:2026 Excessive Agency | 0/4 | 4/4 |
| LLM08:2026 Hidden Context Exposure | 0/4 | 4/4 |
| LLM10:2026 Improper Output Handling | 0/4 | 4/4 |
| LLM06:2026 Unbounded Consumption | 0/4 | 4/4 |

## Security design conclusion

The lab intentionally assumes that model behaviour can be manipulated. The hardened architecture therefore moves authorization, customer scoping, state-change policy, output encoding/redaction and resource budgets outside the model.
