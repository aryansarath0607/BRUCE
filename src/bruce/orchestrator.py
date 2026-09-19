from __future__ import annotations

from .config import Settings
from .memory import Memory
from .planner import Planner
from .providers import provider_from_settings
from .recovery import RecoveryLoop
from .tools import ToolRegistry


class Orchestrator:
    def __init__(self, settings: Settings | None = None, provider=None, approve=None, planner=None, recovery_loop=None):
        self.settings = settings or Settings.from_env()
        self.memory = Memory(self.settings.memory_path)
        self.registry = ToolRegistry(self.settings, self.memory)
        self.provider = provider or provider_from_settings(self.settings)
        self.approve = approve or (lambda _: False)
        self.planner = planner or Planner(self.provider)
        self.recovery = recovery_loop or RecoveryLoop(self.provider, self.registry, self.memory)

    def handle(self, text: str) -> str:
        plan = self.planner.build(text, self.registry.descriptions(), self.memory.context())
        results: list[str] = []
        plan_result = plan.message

        for index, step in enumerate(plan.steps[:5], 1):
            name = step.tool
            tool = self.registry.tools.get(name)
            if not tool:
                results.append(f"Step {index}: {name}: unknown tool")
                continue
            if tool.requires_approval and not self.approve(step.to_action()):
                results.append(f"Step {index}: {name}: skipped (approval required)")
                continue
            result = self.registry.execute(name, step.arguments)
            results.append(f"Step {index}: {name}: {result.output}")
            if not result.ok:
                recovery = self.recovery.execute(text, step.to_action(), result.output)
                results.extend(recovery)
                plan_result += "\n" + "\n".join(results)
                break

        if results:
            plan_result += "\n" + "\n".join(results)
        else:
            plan_result += "\nNo tool actions were necessary."

        self.memory.add_turn(text, plan_result)
        return plan_result
