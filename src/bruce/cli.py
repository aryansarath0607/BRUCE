from __future__ import annotations

import argparse
from .config import Settings
from .orchestrator import Orchestrator
from .voice import Voice, VoiceUnavailable


def main() -> None:
    parser = argparse.ArgumentParser(description='BRUCE personal computer agent')
    parser.add_argument('--once')
    parser.add_argument('--approve', action='store_true', help='Approve machine-changing actions for this run')
    parser.add_argument('--voice', action='store_true', help='Listen for commands')
    parser.add_argument('--wake', action='store_true', help='Listen only for commands beginning with the wake word')
    parser.add_argument('--speak', action='store_true')
    parser.add_argument('--list-audio-devices', action='store_true')
    args = parser.parse_args()
    settings = Settings.from_env()

    if args.list_audio_devices:
        try:
            for device in Voice.audio_devices():
                print(f"{device['index']}: {device['name']}")
        except Exception as exc:
            parser.error(str(exc))
        return

    voice = None
    if args.voice or args.wake or args.speak or settings.speak_responses:
        try:
            voice = Voice(settings)
        except VoiceUnavailable as exc:
            parser.error(str(exc))

    approve = lambda action: args.approve or input(f"Approve {action['tool']}? [y/N] ").strip().lower() == 'y'
    agent = Orchestrator(settings, approve=approve)

    def respond(text: str) -> None:
        answer = agent.handle(text)
        print(f'BRUCE> {answer}')
        if voice and (args.speak or settings.speak_responses):
            voice.speak(answer)

    if args.once:
        respond(args.once)
        return
    if not args.voice and not args.wake:
        print("BRUCE online. Type 'exit' to quit.")

    while True:
        try:
            if voice and (args.voice or args.wake):
                text = voice.listen(require_wake_word=args.wake)
            else:
                text = input('You> ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as exc:
            print(f'BRUCE voice error> {exc}')
            continue
        if not text:
            continue
        if text.lower() in {'exit', 'quit', 'stop listening'}:
            break
        try:
            respond(text)
        except Exception as exc:
            print(f'BRUCE error> {exc}')
