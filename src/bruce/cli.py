from __future__ import annotations

import argparse
import json
from .config import Settings
from .diagnostics import diagnostics
from .orchestrator import Orchestrator
from .voice import Voice, VoiceUnavailable


def main() -> None:
    parser = argparse.ArgumentParser(description="BRUCE personal computer agent")
    parser.add_argument("--once")
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--voice", action="store_true")
    parser.add_argument("--speak", action="store_true")
    parser.add_argument("--listen-once", action="store_true")
    parser.add_argument("--list-audio-devices", action="store_true")
    parser.add_argument("--doctor", action="store_true", help="Check optional dependencies and local services")
    args = parser.parse_args()
    settings = Settings.from_env()

    if args.doctor:
        print(json.dumps(diagnostics(settings), indent=2))
        return
    if args.list_audio_devices:
        try:
            for device in Voice.audio_devices():
                print(f"{device['index']}: {device['name']}")
        except VoiceUnavailable as exc:
            parser.error(str(exc))
        return

    voice = None
    if args.voice or args.speak or settings.speak_responses or args.listen_once:
        try:
            voice = Voice(settings)
        except VoiceUnavailable as exc:
            if args.voice or args.listen_once:
                parser.error(str(exc))
            print(f"Voice disabled: {exc}")

    agent = Orchestrator(settings, approve=lambda action: args.approve or input(f"Approve {action['tool']}? [y/N] ").lower() == "y")

    def respond(text: str):
        result = agent.handle(text)
        print(f"BRUCE> {result}")
        if voice and (args.speak or settings.speak_responses):
            voice.speak(result)

    if args.listen_once:
        text = voice.listen() if voice else ""
        if text:
            respond(text)
        else:
            print("BRUCE> No speech detected.")
        return
    if args.once:
        respond(args.once)
        return

    print("BRUCE online. Type 'exit' to quit.")
    while True:
        try:
            text = voice.listen() if args.voice and voice else input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as exc:
            print(f"BRUCE error> {exc}")
            continue
        if text and text.lower() not in {"exit", "quit", "stop listening"}:
            try:
                respond(text)
            except Exception as exc:
                print(f"BRUCE error> {exc}")
        elif text:
            break
