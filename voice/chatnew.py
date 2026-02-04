import time
from google import genai

from .prompt import SYSTEM_PROMPT
from .config import AI_CONFIG
from .voice_io import listen, speak

# Gemini client
client = genai.Client(api_key="AIzaSyAb8HEKePjKhXaD0_vhT-QCj7WnhahOwOM")
MODEL_NAME = "gemini-3-flash-preview"


def chat(user_input):
    for attempt in range(2):
        try:
            time.sleep(1.5)

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=SYSTEM_PROMPT + "\n\nUser: " + user_input,
                config=AI_CONFIG
            )

            if response and response.candidates:
                return response.candidates[0].content.parts[0].text.strip()

            return "I am here to help with wellness and lifestyle guidance."

        except Exception as e:
            if "429" in str(e) and attempt == 0:
                time.sleep(3)
                continue
            return "I am currently busy. Please try again shortly."

def run_conversation():
    print("🤖 Conversation mode started (say 'exit' to stop)\n")

    while True:
        user_text = listen()
        if user_text is None:
            continue

        if "exit" in user_text.lower():
            speak("Goodbye. Take care.")
            break

        reply = chat(user_text)
        speak(reply)

