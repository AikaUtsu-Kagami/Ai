from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    assistant_mode: str = os.getenv("ASSISTANT_MODE", "auto")  # auto|openai|local
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    tts_model: str = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    stt_model: str = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
    voice: str = os.getenv("OPENAI_TTS_VOICE", "alloy")
    sample_rate: int = int(os.getenv("MIC_SAMPLE_RATE", "16000"))
    record_seconds: int = int(os.getenv("MIC_RECORD_SECONDS", "5"))
    proactive_seconds: int = int(os.getenv("PROACTIVE_SECONDS", "18"))
    robot_port: str = os.getenv("ROBOT_SERIAL_PORT", "")
    robot_baud: int = int(os.getenv("ROBOT_SERIAL_BAUD", "115200"))


def load_settings() -> Settings:
    return Settings(openai_api_key=os.getenv("OPENAI_API_KEY", ""))
