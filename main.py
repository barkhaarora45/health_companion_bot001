from logic.ai_health_bridge import health_check_interaction

def on_face_event(patient_id):
    print("[MAIN] Face recognized:", patient_id)

    # For now, simulate patient name
    patient_name = "Barkha"

    # ONE-TIME sensor-based interaction
    health_check_interaction(patient_name)


if __name__ == "__main__":
    print("🤖 Robot main controller started")
    print("Waiting for face recognition event...")

    # TEMPORARY MANUAL TEST
    # Later this will be called by face_id_emitter
    on_face_event("TEST_PATIENT")
