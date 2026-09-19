from bruce.memory import Memory
from bruce.config import Settings

def test_memory_round_trip(tmp_path):
    path = tmp_path / "memory.json"
    memory = Memory(path)
    memory.remember("User prefers concise answers")
    assert "concise" in memory.context()

def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("BRUCE_PROVIDER", raising=False)
    assert Settings.from_env().provider == "ollama"
