# BRUCE

BRUCE now includes a provider-independent orchestrator, deterministic tools, persistent memory, safety gates, optional voice I/O, web search, system information, and screenshots.

## Install

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[all]"
Copy-Item .env.example .env
```

For voice only, use `pip install -e ".[voice]"`. On Windows, if PyAudio installation fails, install a matching wheel or use text mode; the rest of BRUCE remains usable.

## Use

```powershell
bruce                         # text mode
bruce --voice --speak         # microphone + spoken responses
bruce --once "search the web for Ollama"
bruce --once "show system information"
bruce --approve --once "take a screenshot"
```

Available capabilities include opening applications and URLs, web search, system information, screenshots, file operations, memory, optional shell commands, and interchangeable Ollama/Groq providers. Machine-changing actions require confirmation by default. Shell execution remains disabled unless `BRUCE_ALLOW_SHELL=true`.

Voice uses microphone speech recognition and Windows' available text-to-speech engine. Speech recognition currently uses Google's recognition endpoint; the rest of the agent can run fully locally with Ollama.
