AI_CONFIG = {
    "temperature": 0.35,
    "max_output_tokens": 8192,
    "top_p": 0.9
}

# config.py → AI_CONFIG
#         ↓
# chatnew.py imports it
#         ↓
# passed into Gemini API
#         ↓
# controls how AI behaves

# Temperature Controls creativity:
# Low (0.2–0.4) → predictable, safe ✅
# High (0.8–1.0) → creative, random ❌ (risky for healthcare)