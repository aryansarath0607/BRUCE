# BRUCE

BRUCE is a local, safety-first personal AI agent for Windows. It now supports stronger voice recognition, multi-step reasoning, web search, file operations, clipboard tools, screenshot capture, and system inspection.

## Install

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[all]"
Copy-Item .env.example .env
```

For minimum setup only:

```powershell
pip install -e ".[voice]"
```

## Configure voice

```env
BRUCE_VOICE_BACKEND=google
BRUCE_VOICE_LANGUAGE=en-US
BRUCE_VOICE_RATE=175
BRUCE_SPEAK=false
BRUCE_WAKE_WORD=bruce
```

`BRUCE_VOICE_BACKEND` supports `google` (fastest and easiest) and `whisper` when the OpenAI transcription API is available via `OPENAI_API_KEY`.

## Commands

```powershell
bruce
bruce --voice --speak
bruce --listen-once
bruce --once "search the web for best local LLMs"
bruce --once "show system information"
bruce --approve --once "take a screenshot"
```

## Features

- natural-language command parsing
- Ollama and Groq provider support
- tool-based actions with approval gating
- multi-step planning and recovery
- memory persistence
- web search
- folder listing
- clipboard read/write
- file read/write
- screenshot capture
- system info reporting
- speech recognition with fallback ordering
- text-to-speech output

The system remains intentionally conservative: shell commands stay off unless `BRUCE_ALLOW_SHELL=true`, and machine-changing actions still require confirmation unless `--approve` is passed.
