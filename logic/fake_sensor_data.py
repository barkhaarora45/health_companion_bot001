import random
import time

def get_sensor_data():
    """
    Simulated sensor data.
    This will later be replaced by ThingSpeak API calls.
    """
    return {
        "heart_rate": random.randint(65, 120),   # bpm
        "spo2": random.randint(90, 99),           # %
        "temperature": round(random.uniform(36.5, 38.5), 1),  # °C
        "air_quality": round(random.uniform(0.05, 0.4), 2),   # arbitrary
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
