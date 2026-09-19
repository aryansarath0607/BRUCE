from __future__ import annotations

import re


class VoiceUnavailable(RuntimeError):
    pass


class Voice:
    """Optional headset voice adapter. The wake word defaults to ``bruce``.

    This implementation uses speech recognition to detect the wake phrase. It is
    intentionally opt-in: BRUCE does not record or transmit audio until voice
    mode is started by the user.
    """

    def __init__(self, settings):
        try:
            import speech_recognition as sr
            import pyttsx3
        except ImportError as exc:
            raise VoiceUnavailable("Install voice support with: pip install -e '.[voice]'") from exc
        self.sr = sr
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', settings.voice_rate)
        self.language = settings.voice_language
        self.backend = settings.voice_backend
        self.wake_word = settings.wake_word
        self.timeout = settings.listen_timeout
        self.phrase_time_limit = settings.phrase_time_limit
        self.device_index = self._select_device(settings.voice_input_name, settings.voice_input_index)

    @staticmethod
    def audio_devices() -> list[dict]:
        import speech_recognition as sr
        return [{'index': i, 'name': name} for i, name in enumerate(sr.Microphone.list_microphone_names())]

    def _select_device(self, wanted_name: str, wanted_index: int | None) -> int | None:
        devices = self.audio_devices()
        if wanted_index is not None:
            if any(d['index'] == wanted_index for d in devices):
                return wanted_index
            raise VoiceUnavailable(f'Microphone index {wanted_index} is unavailable; run bruce --list-audio-devices')
        if wanted_name:
            needle = wanted_name.casefold()
            for device in devices:
                if needle in device['name'].casefold():
                    print(f"Microphone: {device['name']} (device {device['index']})")
                    return device['index']
            raise VoiceUnavailable(f'No microphone matched {wanted_name!r}; run bruce --list-audio-devices')
        print('Microphone: Windows default input device')
        return None

    def _recognize(self, audio) -> str:
        if self.backend == 'whisper':
            try:
                import openai
                result = openai.audio.transcriptions.create(model='gpt-4o-mini-transcribe', file=('audio.wav', audio.get_wav_data(), 'audio/wav'))
                return getattr(result, 'text', '')
            except Exception:
                return ''
        try:
            return self.recognizer.recognize_google(audio, language=self.language)
        except Exception:
            return ''

    def listen(self, require_wake_word: bool = False) -> str:
        with self.sr.Microphone(device_index=self.device_index) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.25)
            print('Listening...')
            audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=self.phrase_time_limit)
        text = re.sub(r'\s+', ' ', self._recognize(audio)).strip()
        if not text:
            return ''
        if require_wake_word:
            match = re.match(rf'^\s*{re.escape(self.wake_word)}(?:\b|[,.:!?-])\s*(.*)$', text, re.I)
            return match.group(1).strip() if match else ''
        return text

    def speak(self, text: str) -> None:
        if text:
            self.engine.say(text)
            self.engine.runAndWait()
