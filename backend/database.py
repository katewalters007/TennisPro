"""Database models and operations for TennisPro."""
import logging
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from backend.config import DATABASE_URL


logger = logging.getLogger(__name__)
SQLITE_FALLBACK_URL = "sqlite:///./tennis_pro.db"


def _normalize_database_url(raw_url: str) -> str:
    """Normalize common database URL variants for SQLAlchemy."""
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url


def _create_engine(database_url: str):
    """Create a database engine with backend-specific settings."""
    normalized_url = _normalize_database_url(database_url)
    url = make_url(normalized_url)

    engine_kwargs = {
        "pool_pre_ping": True,
        "future": True,
    }

    if url.drivername.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}

    return create_engine(normalized_url, **engine_kwargs)


def _initialize_engine(database_url: str):
    """Initialize engine and gracefully fall back to SQLite if connection fails."""
    try:
        primary_engine = _create_engine(database_url)
    except Exception as exc:
        logger.warning(
            "Failed to create engine for DATABASE_URL '%s'. "
            "Falling back to local SQLite database at '%s'. Error: %s",
            database_url,
            SQLITE_FALLBACK_URL,
            exc,
        )
        fallback_engine = _create_engine(SQLITE_FALLBACK_URL)
        with fallback_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return fallback_engine

    try:
        with primary_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return primary_engine
    except SQLAlchemyError as exc:
        logger.warning(
            "Primary database initialization failed for DATABASE_URL '%s'. "
            "Falling back to local SQLite database at '%s'. Error: %s",
            database_url,
            SQLITE_FALLBACK_URL,
            exc,
        )

        fallback_engine = _create_engine(SQLITE_FALLBACK_URL)
        with fallback_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return fallback_engine


engine = _initialize_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_database_backend() -> str:
    """Return the current database backend name for diagnostics."""
    return engine.url.get_backend_name()


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
