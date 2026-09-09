from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class UserContext:
    user_id: str
    account_id: str
    role: str = "customer"

@dataclass
class ModelDecision:
    answer: str = ""
    tool_name: str | None = None
    tool_args: dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityResult:
    output: str
    executed_tools: list[str] = field(default_factory=list)
    state_changes: list[str] = field(default_factory=list)
    security_events: list[str] = field(default_factory=list)
