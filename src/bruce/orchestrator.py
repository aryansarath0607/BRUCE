from __future__ import annotations

from .config import Settings
from .memory import Memory
from .providers import provider_from_settings
from .tools import ToolRegistry

class Orchestrator:
    def __init__(self, settings: Settings | None = None, provider=None, approve=None):
        self.settings = settings or Settings.from_env()
        self.memory = Memory(self.settings.memory_path)
        self.registry = ToolRegistry(self.settings, self.memory)
        self.provider = provider or provider_from_settings(self.settings)
        self.approve = approve or (lambda _: False)

    def handle(self, text: str) -> str:
        reply = self.provider.complete(text, self.registry.descriptions(), self.memory.context())
        results = []
        for action in reply.actions[:3]:
            name, args = action.get("tool"), action.get("arguments", {})
            tool = self.registry.tools.get(name)
            if not tool:
                results.append(f"{name}: unknown tool")
                continue
            if tool.requires_approval and not self.approve(action):
                results.append(f"{name}: skipped (approval required)")
                continue
            result = self.registry.execute(name, args)
            results.append(f"{name}: {result.output}")
        answer = reply.message
        if results: answer += "\n" + "\n".join(results)
        self.memory.add_turn(text, answer)
        return answer
