# BRUCE

**Binary Reasoning Unassisted Core Engine** — a voice-first, tool-using personal AI agent for Windows.

This repository contains the first usable BRUCE foundation: a provider-independent orchestrator, deterministic tools, permission gates, persistent memory, and a CLI. It deliberately favors explicit actions and observable results over unrestricted model-generated shell commands.

## Quick start

Requires Python 3.11+.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
bruce
```

Set one provider in `.env`:

- `BRUCE_PROVIDER=ollama` and `BRUCE_MODEL=llama3.2` for a local Ollama server
- `BRUCE_PROVIDER=groq`, `GROQ_API_KEY=...`, and a currently available Groq model for Groq

Use `bruce --once "open notepad"` for a single command. Commands that change the machine require confirmation unless `--approve` is supplied. Never enable automatic approval for untrusted prompts.

## Architecture

```text
CLI / future voice input -> Orchestrator -> LLM provider
                                      -> typed tool calls
                                      -> permission gate
                                      -> deterministic executor
                                      -> result + memory
```

The initial tools are `open_application`, `run_command`, `read_file`, `write_file`, and `remember`. The tool registry is intentionally small so capabilities can be added with clear schemas and tests. Voice, browser automation, screen observation, and recovery loops are planned extensions, not claims about the current implementation.

## Safety

- Tool calls are validated before execution.
- Destructive or machine-changing tools require approval.
- Shell execution is disabled unless explicitly enabled with `BRUCE_ALLOW_SHELL=true`.
- File access is restricted to configured allowed roots when `BRUCE_ALLOWED_ROOTS` is set.
- Provider responses are parsed as strict JSON tool plans; malformed responses do not execute anything.

## Development

```powershell
pip install -e ".[dev]"
pytest
```

See [SECURITY.md](SECURITY.md) for the threat model and [CONTRIBUTING.md](CONTRIBUTING.md) for extension guidance.
