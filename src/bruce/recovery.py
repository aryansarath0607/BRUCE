from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RecoveryOutcome:
    message: str
    steps: list[dict[str, Any]]


class RecoveryLoop:
    """Attempts a minimal corrective action when a planned tool step fails."""

    def __init__(self, provider, registry, memory):
        self.provider = provider
        self.registry = registry
        self.memory = memory

    def recover(self, original_text: str, failed_step: dict[str, Any], failure: str) -> RecoveryOutcome:
        context = (
            f"Original request: {original_text}\n"
            f"Failed step: {failed_step.get('tool')}\n"
            f"Failure details: {failure}\n"
            "Recover with a smaller corrective plan. Return JSON with a 'message' and 'actions' list."
        )
        reply = self.provider.complete(
            "Recover from the failed task using the smallest corrective action.",
            self.registry.descriptions(),
            context,
        )
        actions = reply.actions if reply.actions else []
        return RecoveryOutcome(message=reply.message, steps=actions)

    def execute(self, original_text: str, failed_step: dict[str, Any], failure: str) -> list[str]:
        recovery = self.recover(original_text, failed_step, failure)
        results: list[str] = []
        for idx, step in enumerate(recovery.steps[:3], 1):
            name = step.get("tool")
            arguments = step.get("arguments", {})
            tool = self.registry.tools.get(name)
            if not tool:
                results.append(f"Recovery {idx}: {name}: unknown tool")
                continue
            result = self.registry.execute(name, arguments)
            results.append(f"Recovery {idx}: {name}: {result.output}")
            if not result.ok:
                results.append(f"Recovery {idx}: {name} failed again; the system remains in a safe state.")
                break
        if recovery.message:
            results.insert(0, recovery.message)
        return results
