# voice_io.py
import sounddevice as sd 
import numpy as np
import whisper
import pyttsx3

SAMPLE_RATE = 16000 # 16000 Hz is standard for speech models
DURATION = 7 # max recording time

# Load Whisper model ONCE, not inside listen()
whisper_model = whisper.load_model("base") # initialize


def listen():
    """Record voice and convert to text"""
    print("🎤 Speak clearly...")

    audio = sd.rec( # record audio function from sounddevice library
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE, # captures samples per second
        channels=1, # 1 = mono, 2 = stereo
        dtype="float32" # format of numbers
    ) # this function returns a numpy array
    sd.wait()

    audio = np.squeeze(audio) # Removes extra dimensions
    # Converts shape from (112000, 1) → (112000,) because Whisper expects 1D array

    if np.abs(audio).mean() < 0.001: # silence detection from numpy
        return None
        # abs: how loud the sound is
        # mean: average loudness

    result = whisper_model.transcribe(audio, language="en", fp16=False) # converts audio to text which returns a dictionary
    # fp16=False instructs the program to use full-precision (FP32) floating-point numbers instead of half-precision (FP16)
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
