from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Verification:
    ok: bool
    message: str


class Verifier:
    """Deterministic postconditions for common tools; never treats model text as proof."""

    def verify(self, tool: str, arguments: dict, output: str, ok: bool) -> Verification:
        if not ok:
            return Verification(False, "The tool reported failure.")
        if tool == "write_file":
            path = Path(str(arguments.get("path", ""))).expanduser()
            return Verification(path.exists(), f"File {'exists' if path.exists() else 'was not found'} after writing.")
        if tool == "take_screenshot":
            path = Path(str(arguments.get("path", "screenshot.png"))).expanduser()
            return Verification(path.exists(), f"Screenshot {'exists' if path.exists() else 'was not created'}.")
        if tool == "read_file":
            return Verification(bool(output), "File content was returned." if output else "The file was empty or unreadable.")
        return Verification(True, "Tool completed successfully; no additional deterministic postcondition is available.")
