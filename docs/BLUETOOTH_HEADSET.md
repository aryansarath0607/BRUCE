# BRUCE voice input

BRUCE can permanently select your Bluetooth headset microphone through `.env`. First pair/connect the headset in Windows, then list available inputs:

```powershell
bruce --list-audio-devices
```

Copy a stable part of the headset microphone name into `.env`:

```dotenv
BRUCE_VOICE_INPUT_NAME=WH-1000XM5
```

Alternatively use its index:

```dotenv
BRUCE_VOICE_INPUT_INDEX=3
```

The name setting is preferred because Windows/PyAudio device indexes can change after reconnecting Bluetooth devices. Do not set both; the index takes precedence. BRUCE will print the selected microphone when voice mode starts and will fail clearly if the configured device is unavailable instead of silently using the wrong microphone.

Run:

```powershell
bruce --voice --speak
```

Windows must have the headset connected before BRUCE starts. If the headset is disconnected, reconnect it and restart BRUCE so PyAudio can enumerate it again.
