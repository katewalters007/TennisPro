"""Configuration settings for TennisPro."""
import os
from datetime import timedelta

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tennis_pro.db")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MFA
MFA_ISSUER = "TennisPro"
MFA_WINDOW = 1  # Allow time drift of ±1 window

# App Settings
APP_NAME = "TennisPro"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Master Your Game - Track • Train • Improve"

# Features
FEATURES = {
    "AUTHENTICATION": True,
    "MFA": True,
    "SCORE_TRACKING": True,
    "WORKOUTS": True,
    "DRILLS": True,
    "ANALYTICS": True
}

# Body Parts for Focus Areas
BODY_PARTS = [
    "Legs",
    "Shoulders", 
    "Core",
    "Arms",
    "Endurance"
]

# Match Types
MATCH_TYPES = [
    "Singles",
    "Doubles",
    "Practice"
]

# Difficulty Levels
DIFFICULTY_LEVELS = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

# Drill Types
DRILL_TYPES = [
    "Forehand",
    "Backhand",
    "Serve",
    "Volley",
    "Return",
    "Movement"
]

# UI Settings
THEME = "light"
PRIMARY_COLOR = "#2d8659"
SECONDARY_COLOR = "#1e5f3e"
