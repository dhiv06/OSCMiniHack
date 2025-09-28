# classifier.py
# Small rule-based classifier used by the Flask API to prioritize incoming
# short messages (for example from the chat UI). The goal is to be simple,
# deterministic, and easy to audit; this is NOT a full NLP model.
import re
from typing import List, Tuple

# Emotion keyword dictionaries for classification. These are plain-text
# substring matches (the incoming message is lowercased before matching).
HAPPY_KEYWORDS = {
    "happy", "joy", "excited", "great", "awesome", "amazing", "wonderful", "fantastic",
    "love", "perfect", "excellent", "brilliant", "thrilled", "delighted", "cheerful",
    "😊", "😄", "😃", "🎉", "❤️", "😍", "🥰", "😁", "👍", "🎊"
}

SAD_KEYWORDS = {
    "sad", "depressed", "crying", "tears", "heartbroken", "miserable", "devastated",
    "disappointed", "upset", "down", "blue", "gloomy", "sorrowful", "grief",
    "😢", "😭", "😞", "☹️", "😔", "💔", "😿", "😥", "😰"
}

ANGRY_KEYWORDS = {
    "angry", "mad", "furious", "rage", "hate", "annoyed", "frustrated", "irritated",
    "pissed", "outraged", "livid", "enraged", "bitter", "resentful", "hostile",
    "😠", "😡", "🤬", "👿", "😤", "💢", "😾", "🔥"
}

SCARED_KEYWORDS = {
    "scared", "afraid", "terrified", "frightened", "worried", "anxious", "nervous",
    "panic", "fear", "fearful", "alarmed", "horrified", "petrified", "spooked",
    "😨", "😰", "😱", "😟", "😧", "🙀", "😳", "😵"
}


def classify_text(text: str) -> Tuple[str, float, List[str]]:
    """Classify a short message into an emotion label.

    Returns:
      - label: 'happy' | 'sad' | 'angry' | 'scared' | 'normal'
      - score: heuristic confidence based on keyword matches (0.0 to 1.0)
      - matched_keywords: the subset of keywords that matched the text

    Implementation notes:
      - Empty or whitespace-only input is treated as 'normal' with score 0.0.
      - We scan for emotion keywords and return the emotion with most matches.
      - If multiple emotions tie, priority is: angry > sad > scared > happy.
      - Confidence increases with more keyword matches.
      - This function is intentionally simple: it avoids ML model dependencies
        so it can run offline and be inspected/edited easily.
    """
    # Guard: empty or whitespace-only input
    if not text or not text.strip():
        return "normal", 0.0, []

    # Lowercase the input for case-insensitive substring matching
    t = text.lower()

    # Collect matches from each emotion set
    happy_hits = [kw for kw in HAPPY_KEYWORDS if kw in t]
    sad_hits = [kw for kw in SAD_KEYWORDS if kw in t]
    angry_hits = [kw for kw in ANGRY_KEYWORDS if kw in t]
    scared_hits = [kw for kw in SCARED_KEYWORDS if kw in t]

    # Count matches for each emotion
    emotion_scores = {
        'happy': len(happy_hits),
        'sad': len(sad_hits),
        'angry': len(angry_hits),
        'scared': len(scared_hits)
    }

    # Find the emotion with most matches
    max_score = max(emotion_scores.values())
    
    if max_score == 0:
        return "normal", 0.2, []
    
    # Priority order if tied: angry > sad > scared > happy
    if emotion_scores['angry'] == max_score:
        confidence = min(1.0, max_score * 0.3 + 0.4)
        return "angry", confidence, angry_hits
    elif emotion_scores['sad'] == max_score:
        confidence = min(1.0, max_score * 0.3 + 0.4)
        return "sad", confidence, sad_hits
    elif emotion_scores['scared'] == max_score:
        confidence = min(1.0, max_score * 0.3 + 0.4)
        return "scared", confidence, scared_hits
    elif emotion_scores['happy'] == max_score:
        confidence = min(1.0, max_score * 0.3 + 0.4)
        return "happy", confidence, happy_hits
    
    return "normal", 0.2, []
