from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanStep:
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)
    reason: str = ""

    @property
    def name(self) -> str:
        return self.tool

    def to_action(self) -> dict[str, Any]:
        return {"tool": self.tool, "arguments": self.arguments}


@dataclass
class Plan:
    message: str
    steps: list[PlanStep] = field(default_factory=list)

    @property
    def summary(self) -> str:
        if not self.steps:
            return self.message
        return self.message + "\n" + "\n".join(f"{i + 1}. {step.tool}" for i, step in enumerate(self.steps))


class Planner:
    """Build a structured multi-step plan using the model with a fallback to legacy actions."""

    def __init__(self, provider):
        self.provider = provider

    def build(self, user_text: str, tools: list[dict], context: str = "") -> Plan:
        raw = self.provider.complete(
            user_text,
            tools,
            context + "\nImportant: return JSON with a 'message' and either 'plan' or 'actions'. "
            "When a request requires multiple steps, prefer a plan containing multiple actions in order.",
        )
        payload = {"message": raw.message, "plan": []}
        if raw.actions:
            payload["plan"] = [
                {"tool": action.get("tool", ""), "arguments": action.get("arguments", {}), "reason": action.get("reason", "")}
                for action in raw.actions
            ]
        if not payload["plan"]:
            payload["plan"] = [{"tool": "remember", "arguments": {"fact": user_text}, "reason": "No direct tool plan was generated."}]
        steps = [PlanStep(tool=item.get("tool", ""), arguments=item.get("arguments", {}), reason=item.get("reason", "")) for item in payload["plan"] if item.get("tool")]
        return Plan(message=raw.message, steps=steps)
