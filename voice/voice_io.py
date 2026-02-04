# voice_io.py

import sounddevice as sd
import numpy as np
import whisper
import pyttsx3

SAMPLE_RATE = 16000
DURATION = 7

# Load Whisper model ONCE
whisper_model = whisper.load_model("base")


def listen():
    """Record voice and convert to text"""
    print("🎤 Speak clearly...")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    audio = np.squeeze(audio)

    if np.abs(audio).mean() < 0.001:
        return None

    result = whisper_model.transcribe(audio, language="en", fp16=False)
    return result["text"].strip()


def speak(text):
    """Convert text to speech (robust for Windows)"""
    print("🔊 Bot:", text)

    engine = pyttsx3.init()          # 🔑 re-initialize every time
    engine.setProperty("rate", 165)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()
    engine.stop()                    # 🔑 force cleanup
