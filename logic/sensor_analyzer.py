def analyze_sensor_data(data):
    """
    Rule-based health interpretation.
    AI is NOT used here.
    """

    alerts = []

    if data["heart_rate"] > 100:
        alerts.append("high heart rate")

    if data["spo2"] < 94:
        alerts.append("low oxygen level")

    if data["temperature"] > 38.0:
        alerts.append("fever detected")

    if not alerts:
        return "NORMAL", None

    return "ALERT", ", ".join(alerts)
