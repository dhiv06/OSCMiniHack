# classifier.py
# Small rule-based classifier for short, emergency-style messages.
import re
from typing import List, Tuple

# Keyword sets — expand as needed
# These are literal substring matches against the incoming text (lowercased).
SOS_KEYWORDS = {
    "sos", "mayday", "help me", "help!", "evacuate", "trapped",
    "under rubble", "bleeding", "unconscious", "not breathing", "no pulse", "blood", "explosion", 
}

URGENT_KEYWORDS = {
    "fire", "injury", "injured", "flood", "collapse", "gas leak",
    "smoke", "power out", "danger", "stuck", "medical", "dangerous"
}


def classify_text(text: str) -> Tuple[str, float, List[str]]:
    """
    Classify a message as one of: "sos", "urgent", or "normal".

    Returns a tuple: (label, score, matched_keywords)
      - label: one of the three strings above
      - score: heuristic confidence score (1.0 for sos, 0.7 for urgent, low otherwise)
      - matched_keywords: list of keywords from the sets that matched the text

    Notes:
      - This is a very simple substring matcher (not NLP). It is deterministic and
        easy to inspect/extend, but not robust to paraphrasing or typos.
      - Empty or whitespace-only input returns a default "normal" with score 0.0.
    """
    # Guard: empty or whitespace-only input
    if not text or not text.strip():
        return "normal", 0.0, []

    # Lowercase the input text to make keyword matching case-insensitive
    t = text.lower()
    matched = []

    # Find which SOS keywords appear as substrings in the text
    sos_hits = [kw for kw in SOS_KEYWORDS if kw in t]
    # Find which URGENT keywords appear as substrings in the text
    urgent_hits = [kw for kw in URGENT_KEYWORDS if kw in t]

    # If any SOS keywords are present we consider it an immediate SOS
    if sos_hits:
        return "sos", 1.0, sos_hits
    # Otherwise if any urgent keywords present mark as urgent with lower confidence
    if urgent_hits:
        return "urgent", 0.7, urgent_hits

    # No matches -> normal
    return "normal", 0.1, []
