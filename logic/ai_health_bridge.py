from logic.fake_sensor_data import get_sensor_data  #this gets random data of a supposed sensor
from logic.sensor_analyzer import analyze_sensor_data #literally just 4 if statements
from voice.chatnew import chat #calls gemini api to generate response
from voice.tts import speak #uses pyttsx3 to say whatever text is passed to speak()

def health_check_interaction(patient_name="Patient"):
    data = get_sensor_data()
    status, reason = analyze_sensor_data(data)

    print("📊 Sensor Data:", data)

    if status == "NORMAL":
        speak(f"Hello {patient_name}, your health readings look normal.")
        return

    # Construct safe prompt for chatbot
    user_prompt = (
        f"The patient named {patient_name} has the following health issues: {reason}. "
        f"Heart rate is {data['heart_rate']} bpm, oxygen level is {data['spo2']} percent, "
        f"and temperature is {data['temperature']} degrees Celsius. "
        "Respond with a calm, reassuring message and suggest basic care steps."
    )

    reply = chat(user_prompt)  #this prompt is being sent to gemini and response being stored in reply
    speak(reply) #pyttsx3 is uded for speaking the response.
