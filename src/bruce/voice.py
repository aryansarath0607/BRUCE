from __future__ import annotations

import re


class VoiceUnavailable(RuntimeError):
    pass


class Voice:
    """Microphone/STT/TTS adapter with a persistent Bluetooth input-device selection."""

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
        self.input_name = settings.voice_input_name.strip()
        self.input_index = settings.voice_input_index
        self.device_index = self._select_input_device()

    @staticmethod
    def audio_devices() -> list[dict]:
        try:
            import speech_recognition as sr
            names = sr.Microphone.list_microphone_names()
        except (ImportError, OSError) as exc:
            raise VoiceUnavailable(f"Cannot enumerate microphones: {exc}") from exc
        return [{"index": index, "name": name} for index, name in enumerate(names)]

    def _select_input_device(self) -> int | None:
        devices = self.audio_devices()
        if self.input_index is not None:
            if any(device["index"] == self.input_index for device in devices):
                selected = next(device for device in devices if device["index"] == self.input_index)
                print(f"Microphone: {selected['name']} (device {self.input_index})")
                return self.input_index
            raise VoiceUnavailable(f"Configured microphone index {self.input_index} is unavailable. Run: bruce --list-audio-devices")
        if self.input_name:
            wanted = self.input_name.casefold()
            for device in devices:
                if wanted in device["name"].casefold():
                    print(f"Microphone: {device['name']} (device {device['index']})")
                    return device["index"]
            raise VoiceUnavailable(f"No microphone matched BRUCE_VOICE_INPUT_NAME={self.input_name!r}. Run: bruce --list-audio-devices")
        print("Microphone: Windows default input device")
        return None

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
            transcript = openai.audio.transcriptions.create(model="gpt-4o-mini-transcribe", file=("audio.wav", audio.get_wav_data(), "audio/wav"))
            return getattr(transcript, "text", "")
        except Exception:
            return ""

    def listen(self) -> str:
        with self.sr.Microphone(device_index=self.device_index) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            print("Listening...")
            audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=self.phrase_time_limit)
        for backend in self._backend_order():
            try:
                text = self._try_google(audio) if backend == "google" else self._try_whisper(audio)
                if text:
                    return self._clean_result(text)
            except Exception:
                continue
        return ""

    def _backend_order(self) -> list[str]:
        preferred = self.voice_backend.lower()
        order = [preferred] if preferred in {"google", "whisper"} else ["google", "whisper"]
        if "whisper" not in order:
            order.append("whisper")
        return order

    def speak(self, text: str) -> None:
        if text:
            self.engine.say(text)
            self.engine.runAndWait()

    @staticmethod
    def available() -> bool:
        try:
            import speech_recognition, pyttsx3  # noqa: F401
            return True
        except ImportError:
            return False
