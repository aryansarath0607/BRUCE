from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    provider: str = "ollama"
    model: str = "llama3.2"
    ollama_base_url: str = "http://localhost:11434"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_api_key: str = ""
    allow_shell: bool = False
    allowed_roots: tuple[Path, ...] = ()
    memory_path: Path = Path(".bruce/memory.json")

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        roots = tuple(Path(p).expanduser().resolve() for p in os.getenv("BRUCE_ALLOWED_ROOTS", "").split(";") if p)
        return cls(
            provider=os.getenv("BRUCE_PROVIDER", "ollama").lower(),
            model=os.getenv("BRUCE_MODEL", "llama3.2"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
            groq_base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/"),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            allow_shell=os.getenv("BRUCE_ALLOW_SHELL", "false").lower() in {"1", "true", "yes"},
            allowed_roots=roots,
            memory_path=Path(os.getenv("BRUCE_MEMORY_PATH", ".bruce/memory.json")),
        )

    def json(self) -> str:
        return json.dumps({"provider": self.provider, "model": self.model}, indent=2)
