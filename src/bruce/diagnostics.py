from __future__ import annotations

import importlib.util
import platform
import shutil


def diagnostics(settings) -> dict:
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "provider": settings.provider,
        "model": settings.model,
        "shell_enabled": settings.allow_shell,
        "voice_packages": all(importlib.util.find_spec(name) for name in ("speech_recognition", "pyttsx3")),
        "pyaudio": importlib.util.find_spec("pyaudio") is not None,
        "playwright": importlib.util.find_spec("playwright") is not None,
        "ollama_on_path": shutil.which("ollama") is not None,
    }
