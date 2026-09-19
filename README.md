# BRUCE

BRUCE is a private, safety-first Windows AI agent with voice input, Bluetooth-headset selection, an LLM router, typed tools, memory, planning, recovery, task tracking, diagnostics, screenshots, web search, and optional browser automation.

## Wake word

The wake word is **Bruce** by default. To run voice mode and only accept phrases beginning with the wake word:

```powershell
pip install -e ".[voice]"
Copy-Item .env.example .env
bruce --wake --speak
```

Say:

```text
Bruce, open VS Code
Bruce, search the web for Ollama
Bruce, show system information
```

You can change it with `BRUCE_WAKE_WORD`, but the default is `bruce`.

## Bluetooth headset

```powershell
bruce --list-audio-devices
```

Then set a stable part of the headset microphone name in `.env`:

```dotenv
BRUCE_VOICE_INPUT_NAME=Your Bluetooth Headset
```

Name selection is preferred over an index because Windows audio indexes can change after reconnecting a headset.

## PC and internet access

BRUCE can use explicitly enabled tools for files, applications, URLs, web search, screenshots, clipboard, system information, and optional shell commands. Shell access is disabled by default:

```dotenv
BRUCE_ALLOW_SHELL=false
BRUCE_ALLOWED_ROOTS=C:\Users\YourName\Documents;C:\Users\YourName\Projects
```

BRUCE cannot safely be given unrestricted automatic access to an entire PC. The implementation uses allowlisted folders, approval gates, and typed tools so a model cannot silently delete files, send messages, install software, or execute arbitrary commands. Use `--approve` only when you understand the requested action.

## Commands

```powershell
bruce --doctor
bruce --list-audio-devices
bruce --wake --speak
bruce --once "search the web for local AI models"
bruce --approve --once "take a screenshot"
```

The next safe expansion point is connecting the existing planner, task journal, verification engine, and browser skill to the current orchestrator; those components should remain behind the same approval policy.
