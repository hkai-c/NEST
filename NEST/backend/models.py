from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    emotion_records = relationship("EmotionRecord", back_populates="user")
    meditation_sessions = relationship("MeditationSession", back_populates="user")

class EmotionRecord(Base):
    __tablename__ = "emotion_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    emotion_data = Column(JSON)  # Stores emotion analysis results
    text_content = Column(String, nullable=True)
    voice_file_path = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="emotion_records")

class MeditationSession(Base):
    __tablename__ = "meditation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    session_type = Column(String)  # e.g., "breathing", "mindfulness", "body_scan"
    duration = Column(Integer)  # Duration in seconds
    notes = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="meditation_sessions")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    session_type = Column(String)  # e.g., "ai_chat", "peer_support"
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    content = Column(String)
    sender_type = Column(String)  # "user" or "ai"
    emotion_analysis = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages") 