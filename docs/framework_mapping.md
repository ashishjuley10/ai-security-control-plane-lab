# Framework mapping

The maintained corpus uses the OWASP Top 10 for LLM Applications 2025 edition currently published by OWASP. The earlier 2026 labels and several category numbers in this repository were incorrect. Historical real-model results retain their original labels to preserve the recorded evidence.

| Lab area | OWASP reference | Demonstrated control |
|---|---|---|
| Prompt injection | LLM01:2025 | Application authorization independent of model instructions |
| Sensitive information disclosure | LLM02:2025 | Account scoping and selected-value redaction |
| Unsafe output handling | LLM05:2025 | HTML text encoding |
| Excessive agency | LLM06:2025 | Read-only tool allowlist and rejected privileged capabilities |
| System prompt leakage | LLM07:2025 | Selected internal-context redaction |
| Unbounded consumption | LLM10:2025 | Input and output character budgets |

Official reference: https://genai.owasp.org/llm-top-10/ (checked 10 September 2026).

The corpus tests direct prompts. It does not implement retrieved-document ingestion, a RAG access-control system or browser execution. Character and substring oracles are limited proxies for security impact.

## NIST AI RMF alignment

The threat model identifies assets and boundaries; the evaluation scripts measure defined outcomes; deterministic controls constrain the permitted impact. These artefacts support discussion of the MAP, MEASURE and MANAGE functions. GOVERN is only partially represented through documented assumptions and policy intent: the lab does not demonstrate organizational governance, accountable risk owners or formal approval workflows.

NIST reference: https://www.nist.gov/itl/ai-risk-management-framework (checked 10 September 2026).

This is an educational alignment exercise. It does not establish compliance or certification under OWASP, NIST, ISO 27001 or data-protection law.
