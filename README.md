# BRUCE

BRUCE is a private, safety-first Windows AI agent. It now has a provider-independent orchestrator, voice I/O with Bluetooth input selection, planning/recovery, persistent memory, a SQLite task journal, deterministic verification, web/file/system tools, screenshots, clipboard support, diagnostics, and an optional Playwright browser skill.

## Install

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[all]"
playwright install chromium
Copy-Item .env.example .env
```

Optional groups can be installed separately: `.[voice]`, `.[screen]`, `.[clipboard]`, or `.[browser]`.

## Use

```powershell
bruce --doctor
bruce --list-audio-devices
bruce --voice --speak
bruce --once "search the web for local AI models"
bruce --approve --once "take a screenshot"
```

## JARVIS-style architecture

```text
voice/text -> planner -> approval gate -> typed tools -> verification -> recovery -> task journal -> memory
```

The task journal is stored in `.bruce/tasks.sqlite3`. It records requests, steps, statuses, and outputs so failures are inspectable rather than silently lost. Verification checks deterministic postconditions such as whether a written file or screenshot exists; model text is never treated as proof.

The browser skill is intentionally optional and starts with navigation and extraction. Sensitive browser actions should remain behind an approval layer before being expanded to forms, downloads, or account actions.

BRUCE is not unlimited autonomy: shell execution is disabled by default, machine-changing actions require approval, and browser automation is opt-in.
