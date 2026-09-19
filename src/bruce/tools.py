from __future__ import annotations

import os
import platform
import subprocess
import urllib.parse
import urllib.request
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
            "open_application": Tool("open_application", "Open a Windows application or URL", {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}, True, self.open_application),
            "run_command": Tool("run_command", "Run a command in a subprocess", {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}, True, self.run_command),
            "read_file": Tool("read_file", "Read a UTF-8 text file", {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}, False, self.read_file),
            "write_file": Tool("write_file", "Write UTF-8 text to a file", {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}, True, self.write_file),
            "list_directory": Tool("list_directory", "List files in a directory", {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}, False, self.list_directory),
            "clipboard_get": Tool("clipboard_get", "Read the system clipboard", {"type": "object", "properties": {}}, False, self.clipboard_get),
            "clipboard_set": Tool("clipboard_set", "Write to the system clipboard", {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}, True, self.clipboard_set),
            "search_web": Tool("search_web", "Search the web and return result titles and links", {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}, False, self.search_web),
            "system_info": Tool("system_info", "Report basic operating system and Python information", {"type": "object", "properties": {}}, False, self.system_info),
            "take_screenshot": Tool("take_screenshot", "Capture the screen to a file", {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}, True, self.take_screenshot),
            "remember": Tool("remember", "Store a useful personal fact", {"type": "object", "properties": {"fact": {"type": "string"}}, "required": ["fact"]}, False, self.remember),
        }

    def descriptions(self):
        return [{"name": t.name, "description": t.description, "parameters": t.schema} for t in self.tools.values()]

    def _path(self, value):
        path = Path(value).expanduser().resolve()
        if self.settings.allowed_roots and not any(path == root or root in path.parents for root in self.settings.allowed_roots):
            raise PermissionError(f"Path is outside BRUCE_ALLOWED_ROOTS: {path}")
        return path

    def execute(self, name, arguments):
        if name not in self.tools:
            return ToolResult(False, f"Unknown tool: {name}")
        try:
            return self.tools[name].handler(arguments)
        except (OSError, ValueError, PermissionError, subprocess.SubprocessError, TimeoutError) as exc:
            return ToolResult(False, str(exc))

    def open_application(self, a):
        target = str(a.get("target", "")).strip()
        if not target:
            raise ValueError("target is required")
        if target.startswith(("http://", "https://")):
            webbrowser.open(target)
        elif os.name == "nt":
            os.startfile(target)  # type: ignore[attr-defined]
        else:
            subprocess.Popen([target])
        return ToolResult(True, f"Opened {target}")

    def run_command(self, a):
        if not self.settings.allow_shell:
            raise PermissionError("Shell execution is disabled; set BRUCE_ALLOW_SHELL=true")
        result = subprocess.run(a.get("command", ""), shell=True, capture_output=True, text=True, timeout=60)
        return ToolResult(result.returncode == 0, (result.stdout or result.stderr).strip() or f"exit code {result.returncode}")

    def read_file(self, a):
        path = self._path(a.get("path", ""))
        return ToolResult(True, path.read_text(encoding="utf-8")[:100_000])

    def write_file(self, a):
        path = self._path(a.get("path", ""))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(a.get("content", ""), encoding="utf-8")
        return ToolResult(True, f"Wrote {path}")

    def list_directory(self, a):
        path = self._path(a.get("path", "."))
        items = sorted(p.name for p in path.iterdir())
        return ToolResult(True, "\n".join(items) if items else "Directory is empty.")

    def clipboard_get(self, _):
        try:
            import pyperclip
        except ImportError:
            return ToolResult(False, "Install pyperclip to use clipboard tools.")
        return ToolResult(True, pyperclip.paste())

    def clipboard_set(self, a):
        try:
            import pyperclip
        except ImportError:
            return ToolResult(False, "Install pyperclip to use clipboard tools.")
        pyperclip.copy(str(a.get("text", "")))
        return ToolResult(True, "Clipboard updated.")

    def search_web(self, a):
        query = str(a.get("query", "")).strip()
        if not query:
            raise ValueError("query is required")
        request = urllib.request.Request(
            "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(query),
            headers={"User-Agent": "BRUCE/0.2"},
        )
        html = urllib.request.urlopen(request, timeout=15).read().decode("utf-8", errors="replace")
        import re
        matches = re.findall(r'class="result__a" href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
        results = []
        for link, title in matches[:5]:
            results.append(f"{re.sub('<[^>]+>', '', title).strip()} — {link}")
        return ToolResult(True, "\n".join(results) or "No results found.")

    def system_info(self, _):
        import json as _json
        return ToolResult(True, _json.dumps({"os": platform.platform(), "python": platform.python_version(), "machine": platform.machine()}, indent=2))

    def take_screenshot(self, a):
        try:
            import pyautogui
        except ImportError as exc:
            raise RuntimeError("Install screenshot support with: pip install -e '.[screen]'") from exc
        path = self._path(a.get("path", "screenshot.png"))
        path.parent.mkdir(parents=True, exist_ok=True)
        pyautogui.screenshot().save(path)
        return ToolResult(True, f"Screenshot saved to {path}")

    def remember(self, a):
        fact = str(a.get("fact", "")).strip()
        if not fact:
            raise ValueError("fact is required")
        self.memory.remember(fact)
        return ToolResult(True, "Remembered.")
