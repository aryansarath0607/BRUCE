from __future__ import annotations

class VoiceUnavailable(RuntimeError):
    pass

class Voice:
    """Optional microphone/STT/TTS adapter. Importing BRUCE never requires audio packages."""
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

    def listen(self) -> str:
        with self.sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            print("Listening...")
            audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=self.phrase_time_limit)
        try:
            return self.recognizer.recognize_google(audio, language=self.language).strip()
        except self.sr.UnknownValueError:
            return ""
        except self.sr.RequestError as exc:
            raise VoiceUnavailable(f"Speech recognition service unavailable: {exc}") from exc

    def speak(self, text: str) -> None:
        self.engine.say(text)
        self.engine.runAndWait()
