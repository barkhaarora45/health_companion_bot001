import time
from google import genai

from .prompt import SYSTEM_PROMPT
from .config import AI_CONFIG
from .voice_io import listen, speak

# Gemini client (sends request to gemini)
client = genai.Client(api_key="AIzaSyAb8HEKePjKhXaD0_vhT-QCj7WnhahOwOM")
MODEL_NAME = "gemini-3-flash-preview"


def chat(user_input):
    for attempt in range(2): # try maximum two times 0 and 1
        try:
            time.sleep(1.5) # adds delay to avoid api spams and rate limits (takes input in seconds)

            response = client.models.generate_content( # this is where code talks to gemini
                model=MODEL_NAME,
                contents=SYSTEM_PROMPT + "\n\nUser: " + user_input,
                config=AI_CONFIG # controls tone, length, behaviour
            )

            if response and response.candidates:
                # response = {
                #   "candidates": [
                #     {
                #       "content": {
                #         "parts": [ {"text": "You should rest well."} ]
                #       }
                #     }
                #   ]
                # }
                return response.candidates[0].content.parts[0].text.strip()

            return "I am here to help with wellness and lifestyle guidance." # if no response from AI

        except Exception as e:
            # "429" is rate limit error and attempt = 0 means first try because of indexing
            if "429" in str(e) and attempt == 0:
                time.sleep(3) # wait 3 seconds
                continue # retry because it was the first attempt
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