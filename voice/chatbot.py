def generate_message(patient, action):
    name = patient["preferred_name"]

    if action == "GREETING":
        return f"Hello {name}, I am here with you."

    if action == "MEDICINE":
        return f"Hello {name}, it is time to take your medicine."

    if action == "CHECKUP":
        return f"{name}, how are you feeling right now?"

    return None
