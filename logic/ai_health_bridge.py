from logic.fake_sensor_data import get_sensor_data
from logic.sensor_analyzer import analyze_sensor_data
from voice.chatnew import chat
from voice.tts import speak

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

    reply = chat(user_prompt)
    speak(reply)
