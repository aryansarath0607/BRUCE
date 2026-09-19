from __future__ import annotations

import json
from pathlib import Path

class Memory:
    def __init__(self, path: Path):
        self.path = path
        self.data = {"facts": [], "history": []}
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict): self.data.update(loaded)
            except json.JSONDecodeError:
                pass

    def remember(self, fact: str) -> None:
        if fact and fact not in self.data["facts"]:
            self.data["facts"].append(fact)
            self.save()

    def add_turn(self, user: str, assistant: str) -> None:
        self.data["history"].append({"user": user, "assistant": assistant})
        self.data["history"] = self.data["history"][-20:]
        self.save()

    def context(self) -> str:
        return json.dumps({"facts": self.data["facts"][-50:], "recent": self.data["history"][-6:]})

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
