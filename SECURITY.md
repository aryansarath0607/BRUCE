# Security policy

BRUCE is an operator for a real computer. Treat model output as untrusted input.

- Keep `BRUCE_ALLOW_SHELL=false` unless you explicitly need command execution.
- Prefer dedicated tools over shell commands.
- Review prompts before using `--approve`.
- Set `BRUCE_ALLOWED_ROOTS` to project directories rather than allowing the whole disk.
- Do not commit API keys or `.env` files.
- Add a new tool only with input validation, a clear risk level, and tests.
