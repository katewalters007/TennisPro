"""Database models and operations for TennisPro."""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database setup
DATABASE_URL = "sqlite:///./tennis_pro.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User model for storing player information."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    mfa_secret = Column(String, nullable=True)
    mfa_enabled = Column(Boolean, default=True)  # Automatically enabled
    email_verified = Column(Boolean, default=False)
    email_verification_code = Column(String, nullable=True)
    email_code_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scores = relationship("Score", back_populates="user", cascade="all, delete-orphan")
    workout_logs = relationship("WorkoutLog", back_populates="user", cascade="all, delete-orphan")
    drill_logs = relationship("DrillLog", back_populates="user", cascade="all, delete-orphan")
    body_focus = relationship("UserBodyFocus", back_populates="user", cascade="all, delete-orphan")


class Score(Base):
    """Score tracking for matches and practices."""
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    match_type = Column(String)  # Singles, Doubles, Practice
    opponent = Column(String)
    score_won = Column(Integer)
    score_lost = Column(Integer)
    sets_won = Column(Integer)
    sets_lost = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="scores")


class UserBodyFocus(Base):
    """Track which body parts user wants to improve."""
    __tablename__ = "user_body_focus"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    body_part = Column(String)  # Legs, Shoulders, Core, Arms, Endurance
    focus_level = Column(Integer)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="body_focus")


class WorkoutLog(Base):
    """Track completed workouts."""
    __tablename__ = "workout_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    workout_id = Column(String)
    workout_name = Column(String)
    body_part = Column(String)
    completed = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)
    duration_minutes = Column(Integer, nullable=True)
    difficulty = Column(String)  # Beginner, Intermediate, Advanced
    
    user = relationship("User", back_populates="workout_logs")


class DrillLog(Base):
    """Track completed drills."""
    __tablename__ = "drill_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    drill_id = Column(String)
    drill_name = Column(String)
    drill_type = Column(String)  # Forehand, Backhand, Serve, Volley, etc.
    completed = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)
    reps = Column(Integer, nullable=True)
    accuracy_score = Column(Float, nullable=True)  # 0-100
    
    user = relationship("User", back_populates="drill_logs")


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
