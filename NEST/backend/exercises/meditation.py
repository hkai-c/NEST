from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from pydantic import BaseModel

class Exercise(BaseModel):
    id: str
    title: str
    description: str
    duration: int  # in seconds
    type: str  # "meditation" or "breathing"
    difficulty: str  # "beginner", "intermediate", "advanced"
    audio_url: Optional[str]
    instructions: List[str]
    benefits: List[str]

class MeditationManager:
    def __init__(self):
        self.exercises = self._load_exercises()
    
    def _load_exercises(self) -> Dict[str, Exercise]:
        """Load meditation and breathing exercises from JSON file"""
        exercises = {}
        
        # Default exercises if no file is found
        default_exercises = {
            "mindfulness_breathing": {
                "id": "mindfulness_breathing",
                "title": "Mindfulness Breathing",
                "description": "A simple breathing exercise to help you focus and relax",
                "duration": 300,  # 5 minutes
                "type": "breathing",
                "difficulty": "beginner",
                "audio_url": None,
                "instructions": [
                    "Find a comfortable position",
                    "Close your eyes",
                    "Breathe in slowly through your nose for 4 counts",
                    "Hold your breath for 2 counts",
                    "Exhale slowly through your mouth for 6 counts",
                    "Repeat for the duration of the exercise"
                ],
                "benefits": [
                    "Reduces stress and anxiety",
                    "Improves focus and concentration",
                    "Promotes relaxation"
                ]
            },
            "body_scan": {
                "id": "body_scan",
                "title": "Body Scan Meditation",
                "description": "A guided meditation to help you become aware of physical sensations",
                "duration": 600,  # 10 minutes
                "type": "meditation",
                "difficulty": "beginner",
                "audio_url": None,
                "instructions": [
                    "Lie down in a comfortable position",
                    "Close your eyes",
                    "Focus on your breath for a few moments",
                    "Slowly scan your body from head to toe",
                    "Notice any sensations without judgment",
                    "Return to your breath when finished"
                ],
                "benefits": [
                    "Increases body awareness",
                    "Reduces physical tension",
                    "Promotes relaxation"
                ]
            }
        }
        
        # Try to load from file, fall back to defaults if not found
        try:
            with open("exercises/meditation_exercises.json", "r") as f:
                exercises_data = json.load(f)
                for exercise_id, exercise_data in exercises_data.items():
                    exercises[exercise_id] = Exercise(**exercise_data)
        except FileNotFoundError:
            for exercise_id, exercise_data in default_exercises.items():
                exercises[exercise_id] = Exercise(**exercise_data)
        
        return exercises
    
    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """Get a specific exercise by ID"""
        return self.exercises.get(exercise_id)
    
    def get_exercises_by_type(self, exercise_type: str) -> List[Exercise]:
        """Get all exercises of a specific type"""
        return [
            exercise for exercise in self.exercises.values()
            if exercise.type == exercise_type
        ]
    
    def get_exercises_by_difficulty(self, difficulty: str) -> List[Exercise]:
        """Get all exercises of a specific difficulty level"""
        return [
            exercise for exercise in self.exercises.values()
            if exercise.difficulty == difficulty
        ]
    
    def get_recommended_exercises(
        self,
        user_emotion: Optional[str] = None,
        preferred_duration: Optional[int] = None
    ) -> List[Exercise]:
        """
        Get recommended exercises based on user's emotional state and preferences
        """
        exercises = list(self.exercises.values())
        
        # Filter by duration if specified
        if preferred_duration:
            exercises = [
                ex for ex in exercises
                if abs(ex.duration - preferred_duration) <= 300  # Within 5 minutes
            ]
        
        # Filter by emotion if specified
        if user_emotion:
            emotion_recommendations = {
                "anxiety": ["mindfulness_breathing", "body_scan"],
                "stress": ["mindfulness_breathing", "body_scan"],
                "anger": ["mindfulness_breathing"],
                "sadness": ["body_scan"]
            }
            recommended_ids = emotion_recommendations.get(user_emotion, [])
            exercises = [
                ex for ex in exercises
                if ex.id in recommended_ids
            ]
        
        return exercises
    
    def create_session(
        self,
        exercise_id: str,
        user_id: int,
        start_time: datetime
    ) -> Dict:
        """
        Create a new meditation/breathing session
        """
        exercise = self.get_exercise(exercise_id)
        if not exercise:
            raise ValueError(f"Exercise {exercise_id} not found")
        
        return {
            "session_id": f"{user_id}_{exercise_id}_{start_time.timestamp()}",
            "exercise": exercise,
            "start_time": start_time,
            "expected_end_time": start_time + datetime.timedelta(seconds=exercise.duration),
            "status": "in_progress"
        }
    
    def complete_session(self, session: Dict) -> Dict:
        """
        Mark a session as completed and record the actual duration
        """
        session["status"] = "completed"
        session["end_time"] = datetime.utcnow()
        session["actual_duration"] = (
            session["end_time"] - session["start_time"]
        ).total_seconds()
        
        return session 