from __future__ import annotations

import time

from robot_voice_vision_bot.audio import AudioIO, LocalAudioIO
from robot_voice_vision_bot.chatbot import LocalChatBrain, OpenAIChatBrain
from robot_voice_vision_bot.config import load_settings
from robot_voice_vision_bot.robot import SerialRobotController
from robot_voice_vision_bot.vision import VisionEye


def build_openai_mode(settings):
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    # attach selected models for audio helper usage
    client.stt_model = settings.stt_model
    client.tts_model = settings.tts_model
    client.voice = settings.voice
    audio = AudioIO(client, sample_rate=settings.sample_rate, record_seconds=settings.record_seconds)
    brain = OpenAIChatBrain(client, model=settings.model)
    return audio, brain


def build_local_mode():
    return LocalAudioIO(), LocalChatBrain()


def main() -> None:
    settings = load_settings()

    use_openai = settings.assistant_mode == "openai" or (
        settings.assistant_mode == "auto" and bool(settings.openai_api_key)
    )

    if use_openai:
        try:
            audio, brain = build_openai_mode(settings)
            print("Running in OPENAI mode (voice STT/TTS + LLM).")
        except Exception as exc:
            print(f"OpenAI mode failed ({exc}); falling back to LOCAL mode.")
            audio, brain = build_local_mode()
    else:
        audio, brain = build_local_mode()
        print("Running in LOCAL mode (keyboard I/O, local reasoning).")

    vision = VisionEye()
    robot = SerialRobotController(settings.robot_port, settings.robot_baud)

    robot_connected = robot.connect()
    vision.start()

    print("Robot AI started. Press Ctrl+C to stop.")
    if robot_connected:
        print(f"Robot connected on {settings.robot_port} @ {settings.robot_baud}")
    else:
        print("Robot not connected (set ROBOT_SERIAL_PORT to enable hardware control).")

    last_user_at = time.monotonic()
    last_proactive_at = 0.0

    try:
        while True:
            print("\nListening...")
            text = audio.listen()

            snapshot = vision.snapshot()
            now = time.monotonic()

            if text:
                print(f"You: {text}")
                last_user_at = now
                decision = brain.respond(text, snapshot)
                if decision.robot_command:
                    command_sent = robot.send(decision.robot_command)
                    print(f"Robot command: {command_sent}")
                audio.speak(decision.reply)
                continue

            idle_seconds = now - last_user_at
            can_proactive = (now - last_proactive_at) >= settings.proactive_seconds
            if can_proactive:
                proactive_msg = brain.proactive(snapshot, idle_seconds)
                if proactive_msg:
                    last_proactive_at = now
                    audio.speak(proactive_msg)
    except KeyboardInterrupt:
        print("\nStopping robot AI...")
    finally:
        vision.stop()
        robot.disconnect()


if __name__ == "__main__":
    main()
