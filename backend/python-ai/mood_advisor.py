# mood_advisor.py
# Comprehensive mood improvement recommendation system
# Provides personalized advice based on detected emotion patterns
import random
from typing import List, Dict, Tuple

# Comprehensive advice database organized by emotion
MOOD_ADVICE = {
    'angry': {
        'immediate': [
            "Take 5 deep breaths - inhale for 4, hold for 4, exhale for 6",
            "Step away from the screen for 2 minutes and look out a window",
            "Drink a full glass of cold water slowly",
            "Do 10 jumping jacks or push-ups to release tension",
            "Write down what's bothering you, then crumple up the paper",
            "Listen to calming music or nature sounds for 3 minutes",
            "Splash cold water on your face and wrists",
            "Count backwards from 100 by 7s to refocus your mind"
        ],
        'daily_habits': [
            "Get 7-8 hours of quality sleep - anger often stems from tiredness",
            "Stay hydrated - drink at least 8 glasses of water daily",
            "Exercise for 20+ minutes to release built-up stress hormones",
            "Practice meditation or mindfulness for 10 minutes",
            "Limit caffeine after 2pm - it can increase irritability",
            "Eat regular, balanced meals to maintain stable blood sugar",
            "Take short breaks every hour during work",
            "Write in a gratitude journal - list 3 good things daily"
        ],
        'communication': [
            "Use 'I feel...' statements instead of 'You always...'",
            "Take a 24-hour pause before responding to frustrating messages",
            "Practice the 'sandwich method': positive-concern-positive",
            "Ask clarifying questions instead of making assumptions",
            "Focus on solutions rather than dwelling on problems",
            "Set boundaries: 'I need time to think about this'",
            "Use humor appropriately to defuse tension"
        ]
    },
    
    'sad': {
        'immediate': [
            "Call or text someone you trust and care about",
            "Take a 10-minute walk outside, even if it's just around the block",
            "Listen to uplifting music or a favorite comedian",
            "Do one small act of kindness for someone else",
            "Look at photos that make you smile",
            "Pet an animal or watch cute animal videos",
            "Take a warm shower or bath",
            "Make yourself a warm drink and savor it slowly"
        ],
        'daily_habits': [
            "Spend at least 15 minutes in sunlight daily (even cloudy days help)",
            "Take walks in nature - parks, gardens, or tree-lined streets",
            "Maintain a consistent sleep schedule, even on weekends",
            "Connect with friends or family regularly, even briefly",
            "Engage in creative activities: drawing, music, crafts, cooking",
            "Volunteer or help others - it boosts mood and perspective",
            "Keep a 'wins journal' - record daily accomplishments, however small",
            "Practice gentle yoga or stretching"
        ],
        'long_term': [
            "Consider talking to a counselor or therapist",
            "Join social groups or clubs based on your interests",
            "Set small, achievable daily goals",
            "Limit social media if it makes you feel worse",
            "Create a cozy, comfortable living space",
            "Develop a hobby that gives you a sense of progress",
            "Practice self-compassion - treat yourself like a good friend"
        ]
    },
    
    'scared': {
        'immediate': [
            "Practice the 5-4-3-2-1 grounding technique: 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste",
            "Do box breathing: inhale 4, hold 4, exhale 4, hold 4, repeat 5 times",
            "Call or message someone you trust",
            "Remind yourself: 'This feeling will pass, I am safe right now'",
            "Focus on what you can control today, not future unknowns",
            "Do a quick body scan - relax tense muscles one by one",
            "Hold something comforting: a pet, pillow, or warm cup",
            "Use progressive muscle relaxation: tense and release each muscle group"
        ],
        'coping_strategies': [
            "Create a 'worry time' - 15 minutes daily to process anxious thoughts",
            "Build a support network of trusted friends and family",
            "Practice mindfulness meditation to stay present",
            "Keep a anxiety journal to identify triggers and patterns",
            "Learn to challenge catastrophic thinking with facts",
            "Develop a bedtime routine to improve sleep quality",
            "Limit news and social media consumption",
            "Practice saying 'no' to reduce overwhelming commitments"
        ],
        'building_confidence': [
            "Start each day with positive affirmations",
            "Celebrate small victories and progress",
            "Face fears gradually in small, manageable steps",
            "Learn new skills to build confidence and competence",
            "Surround yourself with supportive, positive people",
            "Practice assertiveness in low-stakes situations",
            "Keep evidence of your past successes and strengths"
        ]
    },
    
    'happy': {
        'maintain_positivity': [
            "Share your good mood with others - happiness is contagious!",
            "Take a moment to appreciate what's going well",
            "Spread kindness - compliment someone or do a favor",
            "Capture this moment - take a photo or write about it",
            "Use this positive energy for a productive task",
            "Thank someone who has made a positive impact on you",
            "Plan something fun to look forward to",
            "Practice gratitude - acknowledge what's bringing you joy"
        ],
        'building_resilience': [
            "Build habits while you're feeling good - they'll help during tough times",
            "Create positive memories and experiences to draw on later",
            "Strengthen relationships when you're in a good headspace",
            "Work on personal goals when motivation is high",
            "Practice mindfulness to fully experience positive emotions",
            "Document what's working well in your life right now",
            "Help others who might be struggling"
        ]
    },
    
    'normal': {
        'general_wellness': [
            "This is a good time to establish healthy routines",
            "Check in with friends and family you haven't spoken to lately",
            "Plan something enjoyable for the weekend",
            "Reflect on your recent communication patterns",
            "Set a small goal for personal improvement",
            "Practice a new skill or hobby for 15 minutes",
            "Organize or clean your space for mental clarity",
            "Take time to appreciate the stability you're feeling"
        ]
    }
}

def get_mood_advice(emotion: str, confidence: float, recent_patterns: Dict[str, float] = None) -> Dict[str, List[str]]:
    """Generate personalized mood improvement advice based on emotion and patterns.
    
    Args:
        emotion: Current detected emotion
        confidence: Confidence score of the detection
        recent_patterns: Dict of emotion percentages from recent messages
    
    Returns:
        Dictionary with categorized advice and recommendations
    """
    advice = {'immediate': [], 'habits': [], 'insights': []}
    
    if emotion not in MOOD_ADVICE:
        emotion = 'normal'
    
    emotion_advice = MOOD_ADVICE[emotion]
    
    # Get immediate suggestions (2-3 random ones)
    if 'immediate' in emotion_advice:
        advice['immediate'] = random.sample(emotion_advice['immediate'], 
                                          min(3, len(emotion_advice['immediate'])))
    
    # Get habit suggestions based on emotion type
    habit_keys = [key for key in emotion_advice.keys() if key != 'immediate']
    for key in habit_keys:
        selected = random.sample(emotion_advice[key], 
                               min(2, len(emotion_advice[key])))
        advice['habits'].extend(selected)
    
    # Generate insights based on patterns
    if recent_patterns:
        advice['insights'] = _generate_pattern_insights(recent_patterns, emotion)
    
    return advice

def _generate_pattern_insights(patterns: Dict[str, float], current_emotion: str) -> List[str]:
    """Generate insights based on recent emotion patterns."""
    insights = []
    
    # Calculate negative emotion percentage
    negative_total = sum(patterns.get(emotion, 0) for emotion in ['angry', 'sad', 'scared'])
    positive_total = patterns.get('happy', 0) + patterns.get('normal', 0)
    
    if negative_total > 60:
        insights.append("⚠️ You've been experiencing difficult emotions frequently. Consider implementing daily stress-reduction practices.")
        insights.append("💡 Try the '3-3-3 rule': Name 3 things you see, 3 sounds you hear, 3 parts of your body you can move.")
    
    elif negative_total > 40:
        insights.append("📊 Your emotions are running a bit intense lately. This is normal, but self-care could help.")
        insights.append("🌱 Small daily habits often work better than big changes - try just one new thing this week.")
    
    elif positive_total > 70:
        insights.append("🌟 You're maintaining great emotional balance! Keep up the positive communication patterns.")
        insights.append("💪 Use this stable period to build resilience habits for tougher times.")
    
    # Specific emotion patterns
    if patterns.get('angry', 0) > 30:
        insights.append("😤 Anger pattern detected. Focus on stress management and getting quality sleep.")
    
    if patterns.get('sad', 0) > 30:
        insights.append("💙 Consider reaching out to friends more often and spending time in nature.")
    
    if patterns.get('scared', 0) > 30:
        insights.append("🫂 Anxiety patterns detected. Grounding techniques and trusted support can help.")
    
    if not insights:
        insights.append("🌈 Your emotional patterns look healthy. Keep nurturing positive communication!")
    
    return insights

def format_advice_for_display(advice: Dict[str, List[str]], emotion: str) -> str:
    """Format advice for display in the UI."""
    
    emotion_emojis = {
        'angry': '😤', 'sad': '💙', 'scared': '🫂', 
        'happy': '😊', 'normal': '🌈'
    }
    
    emoji = emotion_emojis.get(emotion, '🌈')
    
    formatted = f"\n\n{emoji} **Mood Improvement Suggestions**\n\n"
    
    if advice['immediate']:
        formatted += "**Try Right Now:**\n"
        for tip in advice['immediate']:
            formatted += f"• {tip}\n"
        formatted += "\n"
    
    if advice['habits']:
        formatted += "**Build Better Habits:**\n"
        for tip in advice['habits'][:3]:  # Limit to 3 to avoid overwhelming
            formatted += f"• {tip}\n"
        formatted += "\n"
    
    if advice['insights']:
        formatted += "**Personal Insights:**\n"
        for insight in advice['insights']:
            formatted += f"{insight}\n"
    
    return formatted