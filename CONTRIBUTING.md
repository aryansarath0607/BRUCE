# Contributing

1. Create a focused branch.
2. Add or update tests for behavior changes.
3. Keep provider code separate from execution code.
4. Do not add a tool that bypasses the permission gate.
5. Run `pytest` before opening a pull request.

A tool should be deterministic, have a small input schema, return a structured result, and declare whether approval is required.
