from __future__ import annotations

import io
import tempfile
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd


class AudioIO:
    """OpenAI-backed audio for STT + TTS."""

    def __init__(self, client, sample_rate: int, record_seconds: int) -> None:
        self.client = client
        self.sample_rate = sample_rate
        self.record_seconds = record_seconds

    def listen(self) -> str:
        wav_bytes = self.record_to_wav_bytes()
        return self.transcribe(wav_bytes)

    def record_to_wav_bytes(self) -> bytes:
        frames = int(self.record_seconds * self.sample_rate)
        audio = sd.rec(frames, samplerate=self.sample_rate, channels=1, dtype="int16")
        sd.wait()

        with io.BytesIO() as buffer:
            with wave.open(buffer, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(np.asarray(audio).tobytes())
            return buffer.getvalue()

    def transcribe(self, wav_bytes: bytes) -> str:
        with io.BytesIO(wav_bytes) as fp:
            fp.name = "mic_input.wav"
            result = self.client.audio.transcriptions.create(model=self.client.stt_model, file=fp)
        return (result.text or "").strip()

    def speak(self, text: str) -> Path:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            output_path = Path(tf.name)

        with self.client.audio.speech.with_streaming_response.create(
            model=self.client.tts_model,
            voice=self.client.voice,
            input=text,
            format="wav",
        ) as response:
            response.stream_to_file(output_path)

        try:
            import simpleaudio

            wave_obj = simpleaudio.WaveObject.from_wave_file(str(output_path))
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except Exception:
            print(f"[TTS file saved: {output_path}]")
        return output_path


class LocalAudioIO:
    """Local fallback mode: keyboard in / console out."""

    def listen(self) -> str:
        return input("You (type, blank = silence): ").strip()

    def speak(self, text: str):
        print(f"Bot: {text}")
        return None
