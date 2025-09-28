# analytics.py
# Simple in-memory analytics system for tracking emotion patterns
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict, Counter

class EmotionAnalytics:
    """Simple in-memory analytics system for emotion tracking."""
    
    def __init__(self):
        # Store emotion data: {user_id: [(timestamp, emotion, confidence, text_length), ...]}
        self.emotion_data = defaultdict(list)
    
    def log_emotion(self, user_id: str, emotion: str, confidence: float, text_length: int = 0):
        """Log an emotion event for analytics."""
        timestamp = datetime.now()
        self.emotion_data[user_id].append({
            'timestamp': timestamp,
            'emotion': emotion,
            'confidence': confidence,
            'text_length': text_length
        })
        
        # Keep only last 1000 entries per user to prevent memory bloat
        if len(self.emotion_data[user_id]) > 1000:
            self.emotion_data[user_id] = self.emotion_data[user_id][-1000:]
    
    def get_emotion_trends(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get emotion trends for a user over the last N days."""
        if user_id not in self.emotion_data:
            return self._empty_trends()
        
        # Filter to last N days
        cutoff = datetime.now() - timedelta(days=days)
        recent_data = [
            entry for entry in self.emotion_data[user_id] 
            if entry['timestamp'] > cutoff
        ]
        
        if not recent_data:
            return self._empty_trends()
        
        # Calculate emotion distribution
        emotions = [entry['emotion'] for entry in recent_data]
        emotion_counts = Counter(emotions)
        total = len(emotions)
        
        emotion_percentages = {
            emotion: round((count / total) * 100, 1)
            for emotion, count in emotion_counts.items()
        }
        
        # Time-based patterns (hourly)
        hourly_emotions = defaultdict(list)
        for entry in recent_data:
            hour = entry['timestamp'].hour
            hourly_emotions[hour].append(entry['emotion'])
        
        # Find most common emotion by hour
        peak_hours = {}
        for hour, hour_emotions in hourly_emotions.items():
            if hour_emotions:
                most_common = Counter(hour_emotions).most_common(1)[0]
                peak_hours[hour] = {
                    'emotion': most_common[0],
                    'count': most_common[1]
                }
        
        # Generate insights
        insights = self._generate_insights(emotion_percentages, peak_hours, recent_data, days)
        
        return {
            'total_messages': total,
            'emotion_breakdown': emotion_percentages,
            'peak_hours': peak_hours,
            'insights': insights,
            'period_days': days
        }
    
    def _empty_trends(self) -> Dict[str, Any]:
        """Return empty trends structure."""
        return {
            'total_messages': 0,
            'emotion_breakdown': {},
            'peak_hours': {},
            'insights': ['No data available yet. Start sending messages to see your patterns!'],
            'period_days': 7
        }
    
    def _generate_insights(self, emotion_percentages: Dict[str, float], 
                          peak_hours: Dict[int, Dict], recent_data: List[Dict], days: int) -> List[str]:
        """Generate human-readable insights from the data."""
        insights = []
        
        # Emotion distribution insights
        if emotion_percentages:
            dominant_emotion = max(emotion_percentages.items(), key=lambda x: x[1])
            if dominant_emotion[1] > 40:
                period_text = "today" if days == 1 else f"this week"
                insights.append(f"So far {period_text}, {dominant_emotion[1]:.0f}% of your messages were {dominant_emotion[0]}.")
            
            # Negative emotion warnings
            negative_total = sum(
                percentage for emotion, percentage in emotion_percentages.items()
                if emotion in ['angry', 'sad', 'scared']
            )
            if negative_total > 50:
                period_text = "today" if days == 1 else "recently"
                insights.append(f"You've been expressing difficult emotions in {negative_total:.0f}% of messages {period_text}. Consider taking breaks.")
        
        # Time-based insights
        if peak_hours:
            # Find late night patterns (10pm - 2am)
            late_night_emotions = []
            for hour in range(22, 24):  # 10pm-12am
                if hour in peak_hours:
                    late_night_emotions.append(peak_hours[hour])
            for hour in range(0, 3):  # 12am-3am  
                if hour in peak_hours:
                    late_night_emotions.append(peak_hours[hour])
            
            if late_night_emotions:
                negative_late = sum(1 for data in late_night_emotions 
                                  if data['emotion'] in ['angry', 'sad', 'scared'])
                if negative_late > 0:
                    period_text = "tonight" if days == 1 else "late at night"
                    insights.append(f"You've sent frustrated messages {period_text}. Try waiting until morning for important conversations.")
        
        # Message length patterns
        if recent_data:
            avg_length = sum(entry.get('text_length', 0) for entry in recent_data) / len(recent_data)
            if avg_length > 200:
                insights.append("Your messages are getting longer. Consider breaking complex thoughts into smaller messages.")
        
        # Positive reinforcement
        if emotion_percentages.get('happy', 0) > 30:
            insights.append("Great job maintaining positive communication! Keep spreading good vibes.")
        
        if not insights:
            insights.append("Your communication patterns look healthy. Keep it up!")
        
        return insights

# Global analytics instance
analytics = EmotionAnalytics()