import datetime

def decide_action(patient):
    now = datetime.datetime.now().strftime("%H:%M")

    if now in patient["medicine_times"]:
        return "MEDICINE"

    return "GREETING"
