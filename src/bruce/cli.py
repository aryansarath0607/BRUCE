from __future__ import annotations

import argparse
from .config import Settings
from .orchestrator import Orchestrator
from .voice import Voice, VoiceUnavailable


def main() -> None:
    parser = argparse.ArgumentParser(description="BRUCE personal computer agent")
    parser.add_argument("--once")
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--voice", action="store_true")
    parser.add_argument("--speak", action="store_true")
    parser.add_argument("--listen-once", action="store_true")
    parser.add_argument("--list-audio-devices", action="store_true", help="List microphone names and indexes")
    parser.add_argument("--plan", action="store_true")
    args = parser.parse_args()
    settings = Settings.from_env()

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
        if args.plan:
            print("BRUCE plan> " + text)
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
