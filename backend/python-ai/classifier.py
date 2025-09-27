# classifier.py
import re
from typing import List, Tuple

# Keyword sets — expand as needed
SOS_KEYWORDS = {
    "sos", "mayday", "help me", "help!", "evacuate", "trapped",
    "under rubble", "bleeding", "unconscious", "not breathing", "no pulse"
}

URGENT_KEYWORDS = {
    "fire", "injury", "injured", "flood", "collapse", "gas leak",
    "smoke", "power out", "danger", "stuck", "medical"
}

def classify_text(text: str) -> Tuple[str, float, List[str]]:
    """
    Classify a message as sos / urgent / normal.
    Returns: (label, score, matched_keywords)
    """
    if not text or not text.strip():
        return "normal", 0.0, []

    t = text.lower()
    matched = []

    sos_hits = [kw for kw in SOS_KEYWORDS if kw in t]
    urgent_hits = [kw for kw in URGENT_KEYWORDS if kw in t]

    if sos_hits:
        return "sos", 1.0, sos_hits
    if urgent_hits:
        return "urgent", 0.7, urgent_hits

    return "normal", 0.1, []
