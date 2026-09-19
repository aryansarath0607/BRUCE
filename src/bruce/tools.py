from __future__ import annotations

import os
import subprocess
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

@dataclass
class ToolResult:
    ok: bool
    output: str

@dataclass
class Tool:
    name: str
    description: str
    schema: dict
    requires_approval: bool
    handler: Callable[[dict], ToolResult]

class ToolRegistry:
    def __init__(self, settings, memory):
        self.settings, self.memory = settings, memory
        self.tools = {
            "open_application": Tool("open_application", "Open a Windows application or URL", {"type":"object","properties":{"target":{"type":"string"}},"required":["target"]}, True, self.open_application),
            "run_command": Tool("run_command", "Run a command in a subprocess", {"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}, True, self.run_command),
            "read_file": Tool("read_file", "Read a UTF-8 text file", {"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}, False, self.read_file),
            "write_file": Tool("write_file", "Write UTF-8 text to a file", {"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}, True, self.write_file),
            "remember": Tool("remember", "Store a useful personal fact", {"type":"object","properties":{"fact":{"type":"string"}},"required":["fact"]}, False, self.remember),
        }

    def descriptions(self): return [{"name": t.name, "description": t.description, "parameters": t.schema} for t in self.tools.values()]
    def _path(self, value):
        path = Path(value).expanduser().resolve()
        if self.settings.allowed_roots and not any(path == root or root in path.parents for root in self.settings.allowed_roots):
            raise PermissionError(f"Path is outside BRUCE_ALLOWED_ROOTS: {path}")
        return path
    def execute(self, name, arguments):
        if name not in self.tools: return ToolResult(False, f"Unknown tool: {name}")
        try: return self.tools[name].handler(arguments)
        except (OSError, ValueError, PermissionError, subprocess.SubprocessError) as exc: return ToolResult(False, str(exc))
    def open_application(self, a):
        target = str(a.get("target", "")).strip()
        if not target: raise ValueError("target is required")
        if target.startswith(("http://", "https://")): webbrowser.open(target)
        elif os.name == "nt": os.startfile(target)  # type: ignore[attr-defined]
        else: subprocess.Popen([target])
        return ToolResult(True, f"Opened {target}")
    def run_command(self, a):
        if not self.settings.allow_shell: raise PermissionError("Shell execution is disabled; set BRUCE_ALLOW_SHELL=true")
        result = subprocess.run(a.get("command", ""), shell=True, capture_output=True, text=True, timeout=60)
        return ToolResult(result.returncode == 0, (result.stdout or result.stderr).strip() or f"exit code {result.returncode}")
    def read_file(self, a):
        path = self._path(a.get("path", "")); return ToolResult(True, path.read_text(encoding="utf-8"))
    def write_file(self, a):
        path = self._path(a.get("path", "")); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(a.get("content", ""), encoding="utf-8"); return ToolResult(True, f"Wrote {path}")
    def remember(self, a):
        fact = str(a.get("fact", "")).strip()
        if not fact: raise ValueError("fact is required")
        self.memory.remember(fact); return ToolResult(True, "Remembered.")
