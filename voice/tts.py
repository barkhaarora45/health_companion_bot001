import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 150) # but speaking rate in voice_io.py is 165, this will cause inconsistency

def speak(text):
    if not text:
        return
    engine.say(text)
    engine.runAndWait()

# tts.py : engine initialized outside (reusing same engine)
# - pros : faster and cleaner due to no re-initializations
# - cons : but it can freeze or bug on some systems

# voice_io.py : engine initialized inside (fresh engine every call)
# - pros : more stable
# - cons : slower