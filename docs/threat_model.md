# Threat Model

## Scenario

BankGuard is a fictional financial-services AI assistant. It can answer customer questions and propose tool calls.

The model is explicitly treated as an **untrusted decision-support component**. It is not an authorization system.

## Assets

- Customer account and transaction data
- Personal data
- Internal prompts and configuration
- Application credentials/secrets
- Integrity of customer records
- Integrity of financial actions
- Service availability and cost budget

## Trust boundaries

1. User / retrieved content -> model context
2. Model output -> application control plane
3. Control plane -> tool/runtime layer
4. Tool/runtime layer -> customer data
5. Model output -> user interface

## Primary attack paths

### Prompt injection
Direct or indirect content manipulates the model and causes it to request a privileged action or reveal hidden context.

### Sensitive information disclosure
The model returns credentials, personal data, cross-customer information or internal configuration.

### Excessive agency
A compromised or hallucinating model invokes destructive/state-changing tools.

### Hidden context exposure
System instructions or application context are surfaced to the user.

### Improper output handling
Model-generated HTML/script-like content reaches a downstream renderer without encoding or validation.

### Unbounded consumption
Oversized prompts/context produce uncontrolled resource use or output volume.

## Load-bearing controls

- **Authorization outside the model:** model tool calls are proposals only.
- **Read-only tool allowlist:** state-changing tools are not callable by the AI.
- **Customer scope enforcement:** requested account must equal authenticated account.
- **Output redaction:** known secrets and account identifiers are removed.
- **Output encoding:** model content is HTML-escaped before rendering.
- **Input/output budgets:** bound context and response size.
- **Audit events:** denied tools and triggered controls are recorded.

## Residual risk

Prompt-injection detection is deliberately not treated as a complete prevention mechanism. Detection can fail against novel, encoded, multimodal or indirect attacks. The security objective is therefore blast-radius reduction: even if the model follows the malicious instruction, the application control plane should prevent a privileged security impact.
