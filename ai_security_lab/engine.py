from __future__ import annotations
from .controls import input_controls, output_controls
from .models import SecurityResult, UserContext
from .providers import LLMProvider, MockRiskyLLM
from .tools import ToolPolicy, ToolRuntime

class VulnerableEngine:
    def __init__(self, provider: LLMProvider | None = None):
        self.provider = provider or MockRiskyLLM()
        self.runtime = ToolRuntime()

    def process(self, prompt: str, context: UserContext) -> SecurityResult:
        decision = self.provider.decide(prompt, context)
        executed = []
        output = decision.answer
        if decision.tool_name:
            tool_output = self.runtime.execute(decision.tool_name, decision.tool_args)
            output = f"{decision.answer}\n{tool_output}"
            executed.append(decision.tool_name)
        return SecurityResult(output, executed, list(self.runtime.state_changes), [])

class HardenedEngine:
    def __init__(self, provider: LLMProvider | None = None):
        self.provider = provider or MockRiskyLLM()
        self.runtime = ToolRuntime()

    def process(self, prompt: str, context: UserContext) -> SecurityResult:
        clean_prompt, events = input_controls(prompt)
        decision = self.provider.decide(clean_prompt, context)
        output = decision.answer
        executed = []
        if decision.tool_name:
            allowed, reason = ToolPolicy.authorize(decision.tool_name, decision.tool_args, context)
            if allowed:
                tool_output = self.runtime.execute(decision.tool_name, decision.tool_args)
                executed.append(decision.tool_name)
                output = f"{decision.answer}\n{tool_output}"
                events.append("tool_authorized")
            else:
                output = "Request blocked by the AI security control plane."
                events.append(f"tool_denied:{reason}")
        output, output_events = output_controls(output)
        events.extend(output_events)
        return SecurityResult(output, executed, list(self.runtime.state_changes), events)
