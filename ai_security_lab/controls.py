from __future__ import annotations
import html
import re
from .data import DEMO_SECRETS, SYSTEM_PROMPT

MAX_INPUT_CHARS = 2000
MAX_OUTPUT_CHARS = 2000
INJECTION_SIGNALS = [
    r"ignore (all|any|the|previous)",
    r"disregard .*instructions",
    r"system prompt",
    r"developer message",
    r"hidden instructions",
    r"do not follow .*policy",
    r"jailbreak",
]
SENSITIVE_PATTERNS = [
    re.escape(DEMO_SECRETS["internal_api_key"]),
    re.escape(DEMO_SECRETS["database_password"]),
    r"\b\d{2}-\d{2}-\d{2}\b",
    r"\b\d{8}\b",
]

def input_controls(prompt):
    events = []
    if len(prompt) > MAX_INPUT_CHARS:
        events.append("input_budget_exceeded")
        prompt = prompt[:MAX_INPUT_CHARS]
    if any(re.search(signal, prompt, re.I) for signal in INJECTION_SIGNALS):
        events.append("prompt_injection_signal")
    return prompt, events

def output_controls(output):
    events = []
    if SYSTEM_PROMPT.strip() in output or "SYSTEM_SECRET_POLICY" in output:
        output = output.replace(SYSTEM_PROMPT, "[REDACTED INTERNAL CONTEXT]").replace("SYSTEM_SECRET_POLICY", "[REDACTED]")
        events.append("hidden_context_redacted")
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, output):
            output = re.sub(pattern, "[REDACTED]", output)
            events.append("sensitive_data_redacted")
    escaped = html.escape(output, quote=True)
    if escaped != output:
        events.append("output_encoded")
    output = escaped
    if len(output) > MAX_OUTPUT_CHARS:
        output = output[:MAX_OUTPUT_CHARS] + "...[TRUNCATED]"
        events.append("output_budget_enforced")
    return output, events
