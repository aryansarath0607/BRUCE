from __future__ import annotations

import re
import subprocess
from typing import Any


class VoiceUnavailable(RuntimeError):
    pass


class Voice:
    """Optional microphone/STT/TTS adapter with multi-backend recognition."""

    def __init__(self, settings):
        try:
            import speech_recognition as sr
            import pyttsx3
        except ImportError as exc:
            raise VoiceUnavailable("Install voice dependencies with: pip install -e '.[voice]'") from exc
        self.sr = sr
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", settings.voice_rate)
        self.language = settings.voice_language
        self.timeout = settings.listen_timeout
        self.phrase_time_limit = settings.phrase_time_limit
        self.voice_backend = settings.voice_backend
        self.wake_word = settings.wake_word.lower()

    def _clean_result(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text or "").strip()
        if cleaned.lower().startswith(self.wake_word):
            cleaned = cleaned[len(self.wake_word):].strip(" ,.-:;!?")
        return cleaned

    def _try_google(self, audio) -> str:
        return self.recognizer.recognize_google(audio, language=self.language)

    def _try_whisper(self, audio) -> str:
        try:
            import openai
        except ImportError:
            return ""
        try:
            transcript = openai.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=("audio.wav", audio.get_wav_data(), "audio/wav"),
            )
            return getattr(transcript, "text", "")
        except Exception:
            return ""

    def listen(self) -> str:
        with self.sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            print("Listening...")
            audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=self.phrase_time_limit)

        for backend in self._backend_order():
            try:
                if backend == "google":
                    text = self._try_google(audio)
                elif backend == "whisper":
                    text = self._try_whisper(audio)
                else:
                    text = self._try_google(audio)
                if text:
                    return self._clean_result(text)
            except (self.sr.UnknownValueError, self.sr.RequestError, Exception):
                continue
        return ""

    def _backend_order(self) -> list[str]:
        preferred = self.voice_backend.lower()
        order = [preferred] if preferred in {"google", "whisper"} else ["google", "whisper"]
        if "whisper" not in order:
            order.append("whisper")
        return order

    def speak(self, text: str) -> None:
        if not text:
            return
        self.engine.say(text)
        self.engine.runAndWait()

    @staticmethod
    def available() -> bool:
        try:
            import speech_recognition  # noqa: F401
            import pyttsx3  # noqa: F401
            return True
        except ImportError:
            return False
