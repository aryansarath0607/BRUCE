from __future__ import annotations

import argparse
from .config import Settings
from .orchestrator import Orchestrator
from .voice import Voice, VoiceUnavailable


def main() -> None:
    parser = argparse.ArgumentParser(description="BRUCE personal computer agent")
    parser.add_argument("--once", help="Process one command and exit")
    parser.add_argument("--approve", action="store_true", help="Approve machine-changing actions")
    parser.add_argument("--voice", action="store_true", help="Use the microphone for an interactive session")
    parser.add_argument("--speak", action="store_true", help="Read responses aloud")
    parser.add_argument("--plan", action="store_true", help="Display the plan before execution")
    args = parser.parse_args()
    settings = Settings.from_env()
    voice = None
    if args.voice or args.speak or settings.speak_responses:
        try:
            voice = Voice(settings)
        except VoiceUnavailable as exc:
            if args.voice:
                parser.error(str(exc))
            print(f"Voice disabled: {exc}")

    agent = Orchestrator(settings, approve=lambda action: args.approve or input(f"Approve {action['tool']}? [y/N] ").lower() == "y")

    def respond(text: str):
        result = agent.handle(text)
        if args.plan:
            print("BRUCE plan> " + text)
        print(f"BRUCE> {result}")
        if voice and (args.speak or settings.speak_responses):
            voice.speak(result)

    if args.once:
        respond(args.once)
        return

    print("BRUCE online. Type 'exit' to quit.")
    while True:
        try:
            text = voice.listen() if args.voice else input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as exc:
            print(f"BRUCE voice error> {exc}")
            continue
        if not text:
            continue
        if text.lower() in {"exit", "quit", "stop listening"}:
            break
        try:
            respond(text)
        except Exception as exc:
            print(f"BRUCE error> {exc}")
