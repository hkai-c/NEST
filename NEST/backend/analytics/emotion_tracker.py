from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
import models
from ml.emotion_analyzer import EmotionAnalyzer

class EmotionTracker:
    def __init__(self, db: Session):
        self.db = db
        self.emotion_analyzer = EmotionAnalyzer()
    
    def record_emotion(
        self,
        user_id: int,
        text_content: Optional[str] = None,
        voice_file_path: Optional[str] = None,
        emotion_data: Optional[Dict] = None
    ) -> models.EmotionRecord:
        """
        Record a new emotion entry for a user
        """
        if not emotion_data and text_content:
            emotion_data = self.emotion_analyzer.analyze_text(text_content)
        
        record = models.EmotionRecord(
            user_id=user_id,
            text_content=text_content,
            voice_file_path=voice_file_path,
            emotion_data=emotion_data
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        return record
    
    def get_user_emotions(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[models.EmotionRecord]:
        """
        Get emotion records for a user within a date range
        """
        query = self.db.query(models.EmotionRecord).filter(
            models.EmotionRecord.user_id == user_id
        )
        
        if start_date:
            query = query.filter(models.EmotionRecord.timestamp >= start_date)
        if end_date:
            query = query.filter(models.EmotionRecord.timestamp <= end_date)
        
        return query.order_by(models.EmotionRecord.timestamp).all()
    
    def generate_emotion_report(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict:
        """
        Generate a comprehensive emotion report for a user
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        records = self.get_user_emotions(user_id, start_date, end_date)
        
        if not records:
            return {
                "error": "No emotion records found for the specified period"
            }
        
        # Convert records to DataFrame for analysis
        df = pd.DataFrame([
            {
                "timestamp": record.timestamp,
                "dominant_emotion": record.emotion_data["dominant_emotion"],
                "sentiment_score": record.emotion_data["sentiment_score"]
            }
            for record in records
        ])
        
        # Calculate daily averages
        daily_stats = df.groupby(df["timestamp"].dt.date).agg({
            "sentiment_score": ["mean", "std"],
            "dominant_emotion": lambda x: x.mode().iloc[0] if not x.empty else None
        }).reset_index()
        
        # Calculate emotion distribution
        emotion_distribution = df["dominant_emotion"].value_counts(normalize=True).to_dict()
        
        # Calculate sentiment trends
        sentiment_trend = df["sentiment_score"].rolling(window=7).mean().tolist()
        
        # Generate insights
        insights = self._generate_insights(df, daily_stats)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_records": len(records),
                "average_sentiment": df["sentiment_score"].mean(),
                "most_common_emotion": df["dominant_emotion"].mode().iloc[0],
                "emotion_distribution": emotion_distribution
            },
            "trends": {
                "daily_stats": daily_stats.to_dict(orient="records"),
                "sentiment_trend": sentiment_trend
            },
            "insights": insights
        }
    
    def _generate_insights(
        self,
        df: pd.DataFrame,
        daily_stats: pd.DataFrame
    ) -> List[Dict]:
        """
        Generate insights from emotion data
        """
        insights = []
        
        # Sentiment trend insight
        recent_sentiment = df["sentiment_score"].tail(7).mean()
        overall_sentiment = df["sentiment_score"].mean()
        
        if recent_sentiment > overall_sentiment:
            insights.append({
                "type": "positive_trend",
                "message": "Your emotional state has been more positive recently"
            })
        elif recent_sentiment < overall_sentiment:
            insights.append({
                "type": "negative_trend",
                "message": "Your emotional state has been more challenging recently"
            })
        
        # Emotion consistency insight
        emotion_consistency = df["dominant_emotion"].nunique() / len(df)
        if emotion_consistency < 0.3:
            insights.append({
                "type": "emotion_consistency",
                "message": "You've been experiencing consistent emotions recently"
            })
        
        # Daily pattern insight
        daily_patterns = df.groupby(df["timestamp"].dt.hour)["sentiment_score"].mean()
        best_hour = daily_patterns.idxmax()
        worst_hour = daily_patterns.idxmin()
        
        insights.append({
            "type": "daily_pattern",
            "message": f"You tend to feel best around {best_hour}:00 and most challenged around {worst_hour}:00"
        })
        
        return insights
    
    def get_emotion_correlations(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict:
        """
        Analyze correlations between emotions and other factors
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        records = self.get_user_emotions(user_id, start_date, end_date)
        
        if not records:
            return {
                "error": "No emotion records found for the specified period"
            }
        
        # TODO: Implement correlation analysis with other factors
        # This could include:
        # - Time of day
        # - Day of week
        # - Weather
        # - Activity levels
        # - Sleep patterns
        
        return {
            "message": "Correlation analysis not yet implemented"
        } 