# tone_rewriter.py
# Rule-based tone transformation system for improving message quality
# Converts aggressive/negative messages into more constructive alternatives
import re
from typing import Dict, List

# Tone transformation patterns - maps problematic phrases to better alternatives
TONE_PATTERNS = {
    'supportive': {
        # Angry to supportive
        r'\bi\'m done with this\b': "I think we should pause and revisit this later",
        r'\bthis is stupid\b': "I'm having trouble understanding this approach",
        r'\byou always\b': "I've noticed that sometimes",
        r'\byou never\b': "it would help if we could",
        r'\bwhatever\b': "I understand we see this differently",
        r'\bi don\'t care\b': "I need some time to process this",
        r'\bfine\b': "I hear what you're saying",
        r'\bwrong\b': "I see it differently",
        r'\bidiotic?\b': "confusing",
        r'\bstupid\b': "challenging",
        
        # Sad to supportive
        r'\bi can\'t do this\b': "I'm finding this challenging and could use support",
        r'\bi\'m terrible at\b': "I'm still learning",
        r'\bi hate myself\b': "I'm being hard on myself",
        r'\bnothing works\b': "I haven't found the right approach yet",
        r'\bi give up\b': "I need to take a break and try again",
    },
    
    'professional': {
        # Angry to professional
        r'\bi\'m done with this\b': "I believe we should reassess our current approach",
        r'\bthis is stupid\b': "I have concerns about this strategy",
        r'\byou always\b': "I've observed a pattern where",
        r'\byou never\b': "I think we could improve by",
        r'\bwhatever\b': "I acknowledge your perspective",
        r'\bi don\'t care\b': "I need additional time to evaluate this",
        r'\bfine\b': "I understand your position",
        r'\bwrong\b': "I have a different viewpoint",
        r'\bidiotic?\b': "suboptimal",
        r'\bstupid\b': "inefficient",
        
        # General improvements
        r'\byeah\b': "Yes",
        r'\bnope\b': "No",
        r'\bkinda\b': "somewhat",
        r'\bgonna\b': "going to",
    },
    
    'neutral': {
        # Angry to neutral
        r'\bi\'m done with this\b': "I think we need a different approach",
        r'\bthis is stupid\b': "This isn't working for me",
        r'\byou always\b': "I notice that",
        r'\byou never\b': "It would help if",
        r'\bwhatever\b': "Okay",
        r'\bi don\'t care\b': "I'm not sure about this",
        r'\bfine\b': "Alright",
        r'\bwrong\b': "different",
        r'\bidiotic?\b': "unclear",
        r'\bstupid\b': "difficult",
        
        # Scared to neutral
        r'\bi\'m terrified\b': "I'm concerned about",
        r'\bi can\'t handle\b': "This is challenging for me",
        r'\bi\'m freaking out\b': "I'm feeling overwhelmed",
    }
}

def rewrite_tone(text: str, target_tone: str) -> str:
    """Transform the tone of a message using rule-based pattern matching.
    
    Args:
        text: Original message text
        target_tone: Target tone ('supportive', 'professional', 'neutral')
    
    Returns:
        Rewritten text with improved tone
    """
    if target_tone not in TONE_PATTERNS:
        return text
    
    result = text.lower()
    patterns = TONE_PATTERNS[target_tone]
    
    # Apply transformation patterns
    for pattern, replacement in patterns.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Capitalize first letter and maintain original capitalization style
    if result and text:
        # If original was all caps, keep it all caps
        if text.isupper():
            result = result.upper()
        # If original started with capital, capitalize first letter
        elif text[0].isupper():
            result = result[0].upper() + result[1:]
    
    return result

def get_rewrite_suggestions(text: str, detected_emotion: str) -> Dict[str, str]:
    """Get multiple tone rewrite suggestions based on detected emotion.
    
    Args:
        text: Original message text
        detected_emotion: Emotion detected by classifier
    
    Returns:
        Dictionary mapping tone names to rewritten versions
    """
    suggestions = {}
    
    # Only suggest rewrites for negative emotions
    if detected_emotion in ['angry', 'sad', 'scared']:
        suggestions['supportive'] = rewrite_tone(text, 'supportive')
        suggestions['professional'] = rewrite_tone(text, 'professional') 
        suggestions['neutral'] = rewrite_tone(text, 'neutral')
        
        # Remove suggestions that are identical to original
        original_lower = text.lower().strip()
        suggestions = {k: v for k, v in suggestions.items() 
                      if v.lower().strip() != original_lower}
    
    return suggestions