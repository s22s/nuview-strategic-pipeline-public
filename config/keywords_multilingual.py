# Multilingual trigger keywords for global scoring and detection.
# generate_programs.py imports ALL_GLOBAL_TRIGGERS from this module when available.
# Add translations and local synonyms to improve recall for non-English opportunities.

ALL_GLOBAL_TRIGGERS = [
    # English
    "flood resilience",
    "disaster risk",
    "climate adaptation",
    "infrastructure modernization",

    # Spanish
    "resiliencia ante inundaciones",
    "riesgo de desastre",
    "adaptación climática",
    "modernización de infraestructura",

    # French
    "résilience aux inondations",
    "risque de catastrophe",
    "adaptation au climat",
    "modernisation des infrastructures",

    # Portuguese
    "resiliência a inundações",
    "risco de desastre",
    "adaptação climática",

    # Arabic (transliterated examples)
    "taṣadd al-fawādil",  # placeholder transliteration

    # Short global synonyms
    "natural disaster",
    "climate resilience"
]
