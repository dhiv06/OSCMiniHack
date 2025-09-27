# classifier.py
# Small rule-based classifier used by the Flask API to prioritize incoming
# short messages (for example from the chat UI). The goal is to be simple,
# deterministic, and easy to audit; this is NOT a full NLP model.
import re
from typing import List, Tuple

# Two keyword sets that indicate escalating severity. These are plain-text
# substring matches (the incoming message is lowercased before matching).
# Expand or tweak these sets to tune sensitivity.
SOS_KEYWORDS = {
    "sos", "mayday", "help me", "help!", "evacuate", "trapped", "🆘",
    "under rubble", "bleeding", "unconscious", "not breathing", "no pulse", "blood", "explosion",
}

URGENT_KEYWORDS = {
    "fire", "injury", "injured", "flood", "collapse", "gas leak", "🚨",
    "smoke", "power out", "danger", "stuck", "medical", "dangerous"
}


def classify_text(text: str) -> Tuple[str, float, List[str]]:
    """Classify a short message into a severity label.

    Returns:
      - label: 'sos' | 'urgent' | 'normal'
      - score: heuristic confidence (1.0 high, ~0.7 medium, low otherwise)
      - matched_keywords: the subset of keywords that matched the text

    Implementation notes:
      - Empty or whitespace-only input is treated as 'normal' with score 0.0.
      - We scan for SOS keywords first; any SOS hit yields an immediate 'sos'.
      - If no SOS matches but one or more URGENT keywords match, we return
        'urgent' with a lower confidence score.
      - This function is intentionally simple: it avoids ML model dependencies
        so it can run offline and be inspected/edited easily.
    """
    # Guard: empty or whitespace-only input
    if not text or not text.strip():
        return "normal", 0.0, []

    # Lowercase the input for case-insensitive substring matching
    t = text.lower()

    # Collect matches from each set. We return the matching keywords so the
    # frontend or logs can show what triggered the classification.
    sos_hits = [kw for kw in SOS_KEYWORDS if kw in t]
    urgent_hits = [kw for kw in URGENT_KEYWORDS if kw in t]

    # Priority: SOS > URGENT > NORMAL
    if sos_hits:
        return "sos", 1.0, sos_hits
    if urgent_hits:
        return "urgent", 0.7, urgent_hits

    return "normal", 0.1, []
