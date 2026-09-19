from __future__ import annotations

import argparse
from .config import Settings
from .orchestrator import Orchestrator

def main() -> None:
    parser = argparse.ArgumentParser(description="BRUCE personal computer agent")
    parser.add_argument("--once", help="Process one command and exit")
    parser.add_argument("--approve", action="store_true", help="Approve machine-changing actions")
    args = parser.parse_args()
    settings = Settings.from_env()
    agent = Orchestrator(settings, approve=lambda action: args.approve or input(f"Approve {action['tool']}? [y/N] ").lower() == "y")
    if args.once:
        print(agent.handle(args.once)); return
    print("BRUCE online. Type 'exit' to quit.")
    while True:
        try: text = input("You> ").strip()
        except (EOFError, KeyboardInterrupt): break
        if text.lower() in {"exit", "quit"}: break
        if text:
            try: print(f"BRUCE> {agent.handle(text)}")
            except Exception as exc: print(f"BRUCE error> {exc}")
