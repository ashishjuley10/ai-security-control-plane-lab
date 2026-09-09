# Framework Mapping

This lab focuses on six risks from the **OWASP GenAI LLM Top 10 2026**, selected because they directly exercise secure design, adversarial testing and control engineering in an AI application.

| Lab area | OWASP GenAI LLM Top 10 2026 | Control demonstrated |
|---|---|---|
| Direct/indirect injection | LLM01 Prompt Injection | Model output treated as untrusted; authorization outside model |
| Data leakage | LLM02 Sensitive Information Disclosure | Data minimisation, scoping, redaction |
| Tool abuse | LLM03 Excessive Agency | Least privilege, read-only allowlist, capability restriction |
| Resource abuse | LLM06 Unbounded Consumption | Input/output budgets |
| Prompt/context leakage | LLM08 Hidden Context Exposure | Context non-disclosure and redaction |
| Unsafe rendering | LLM10 Improper Output Handling | Output encoding and downstream validation |

## NIST AI RMF / NIST AI 600-1 alignment

The project also demonstrates practical controls consistent with the intent of the NIST AI Risk Management Framework and Generative AI Profile:

- **GOVERN:** defined roles, policies and control ownership
- **MAP:** assets, trust boundaries, threat paths and impact
- **MEASURE:** repeatable adversarial test cases with pass/fail security oracles
- **MANAGE:** least privilege, control enforcement and residual-risk documentation

This is an engineering demonstration, not a claim of formal compliance or certification.
