# Security Engineering Report

## Design question

**What happens when the model is successfully manipulated?**

The vulnerable baseline implicitly trusts model decisions. A model can therefore turn a prompt injection or hallucination into a privileged tool call, customer-data leak or unsafe downstream output.

The hardened design assumes the model can be wrong or manipulated. Controls are placed at deterministic application boundaries.

## Implemented controls

### 1. Tool authorization outside the LLM
The LLM may propose a tool, but `ToolPolicy` independently checks whether that capability is permitted.

### 2. Least privilege
The AI receives only two read-only tools: `get_balance` and `get_transactions`.

Transfers, deletion, profile modification and bulk export are denied.

### 3. Object-level authorization
Read operations are constrained to the authenticated customer's account.

### 4. Sensitive-output controls
Known secrets and account-number patterns are redacted before release.

### 5. Output encoding
Model output is treated as untrusted text and HTML-escaped before rendering.

### 6. Consumption budgets
Inputs and outputs are bounded to reduce uncontrolled resource use.

### 7. Security telemetry
Control activations and denied tool calls are recorded as security events.

## Important limitation

The `MockRiskyLLM` is deterministic by design. It allows the security-control layer to be tested reproducibly without relying on a stochastic external model.

An optional OpenAI-compatible provider is included for extension, but the core claim is not "my model cannot be fooled." The claim is:

> A manipulated model should not automatically become an authorised banking actor.

## Next engineering iterations

- Policy-as-code rules with richer role/capability models
- Human approval for high-risk actions
- Retrieval trust labels and provenance
- Indirect prompt-injection test corpus
- Security event export to SIEM
- Rate limiting and per-user cost budgets
- CI adversarial regression gates
- Real-model evaluation with attack success rate and false-positive measurements
