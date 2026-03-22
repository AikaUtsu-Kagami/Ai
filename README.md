# Voice + Vision Robot AI Chatbot

This project gives you a working foundation for a **speech-to-text (STT) + text-to-speech (TTS) AI assistant** that can:

- Listen from a microphone (OpenAI mode) or keyboard (local mode fallback).
- Speak responses out loud (OpenAI mode) or print to console (local mode fallback).
- Use a camera as "eyes" (face detection signal included in chat context).
- Send action commands to a robot over serial.
- **Speak proactively** when idle (it does not only wait for direct prompts).

## Features

- **Modes:**
  - `ASSISTANT_MODE=auto` (default): uses OpenAI when key is present; otherwise local mode.
  - `ASSISTANT_MODE=openai`: force cloud STT/TTS/LLM.
  - `ASSISTANT_MODE=local`: force local keyboard/console mode.
- **STT:** OpenAI transcription API (`gpt-4o-mini-transcribe` by default).
- **Chat reasoning:** OpenAI chat model (`gpt-4o-mini` by default) or local rule-based fallback.
- **TTS:** OpenAI speech API (`gpt-4o-mini-tts` by default).
- **Vision:** OpenCV face detection loop and live metadata injection.
- **Robot control:** Serial protocol command sender (easy to map to Arduino/ESP32 firmware).
- **Autonomy:** proactive comments every `PROACTIVE_SECONDS` when conditions are met.

## Architecture

- `main.py` – runtime loop and orchestration + mode selection.
- `robot_voice_vision_bot/audio.py` – mic capture + STT/TTS + local fallback audio adapter.
- `robot_voice_vision_bot/vision.py` – camera capture and face counting.
- `robot_voice_vision_bot/chatbot.py` – OpenAI brain + local brain + proactive behavior hooks.
- `robot_voice_vision_bot/robot.py` – robot command mapping + serial transport.
- `robot_voice_vision_bot/config.py` – environment configuration.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env`.

- For full voice AI: set `OPENAI_API_KEY` and keep `ASSISTANT_MODE=auto` or `openai`.
- For no-key local testing: set `ASSISTANT_MODE=local`.

## Run

```bash
python main.py
```

## Robot firmware protocol

The app sends one line per command:

- `MOVE_FORWARD:30`
- `MOVE_BACKWARD:30`
- `TURN_LEFT:20`
- `TURN_RIGHT:20`
- `STOP:0`
- `WAVE:1`

Your robot firmware should read newline-delimited serial commands and execute them.

## Notes

- If `ROBOT_SERIAL_PORT` is empty, chat and vision still run, and robot control is skipped.
- Camera index defaults to `0`; change in `VisionEye(camera_index=...)` if needed.
- For production robots, add safety interlocks and motor timeouts.
