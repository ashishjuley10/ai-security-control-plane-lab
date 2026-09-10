# Security engineering report

## Design question

What happens when the model proposes an unsafe action? The lab compares direct execution with application-enforced authorization using synthetic banking data.

## Implemented boundaries

The hardened engine validates proposal types before use, restricts execution to two read-only tools and requires the requested account to match trusted caller context. Output controls redact selected synthetic values, HTML-escape text and enforce a character limit. Security events record decisions in memory. The provider adapters reject invalid decision schemas as errors.

## Evidence

The deterministic corpus contains 24 attack scenarios and eight legitimate tasks. The review reproduces zero hardened oracle violations while legitimate tasks remain usable. The vulnerable mock deliberately follows the unsafe requests; its failure rate is not representative of a general-purpose model. The test suite also covers malformed proposals and cross-account reads.

The historical real-model JSON records a separate, single-pass evaluation. It was not rerun during this review and cannot establish the behavior of the changed parser or control plane. Read the README and review notes before quoting it.

## Limits

Authentication is assumed; no identity provider is integrated. The corpus contains no implemented retrieval pipeline. Known-value regex redaction is bypassable and does not provide general DLP. HTML escaping is appropriate for HTML text contexts, not every downstream sink. Character limits do not replace rate limits or token and cost budgets. In-memory security events do not constitute a production audit trail.

## Next work selected by risk

For a real deployment, bind caller identity to server-side entitlements, limit data before it enters context, validate tool arguments against strict schemas, enforce authorization again in the backend, and add persistent redacted audit events. Extend evaluation to retrieval poisoning, repeated model runs and benign model-backed tasks. Use a private test environment with synthetic data.
