"""Utility functions for TennisPro."""
from datetime import datetime
import json
import re


def get_player_level(win_percentage: float) -> str:
    """Determine player level based on win percentage."""
    if win_percentage >= 70:
        return "Advanced"
    elif win_percentage >= 50:
        return "Intermediate"
    else:
        return "Beginner"


def format_date(date: datetime) -> str:
    """Format datetime for display."""
    if date is None:
        return "N/A"
    return date.strftime("%m/%d/%Y")


def format_time(date: datetime) -> str:
    """Format datetime with time."""
    if date is None:
        return "N/A"
    return date.strftime("%m/%d/%Y %I:%M %p")


def calculate_set_score(points_won: int, points_lost: int) -> str:
    """Calculate set score from points."""
    return f"{points_won}-{points_lost}"


def get_match_result(sets_won: int, sets_lost: int) -> str:
    """Get match result."""
    if sets_won > sets_lost:
        return "Won"
    elif sets_won < sets_lost:
        return "Lost"
    else:
        return "Tied"


def get_focus_area_emoji(body_part: str) -> str:
    """Get emoji for body part."""
    emojis = {
        "Legs": "💪",
        "Shoulders": "🏐",
        "Core": "🌀",
        "Arms": "🎾",
        "Endurance": "⚡"
    }
    return emojis.get(body_part, "🎯")


def get_difficulty_emoji(difficulty: str) -> str:
    """Get emoji for difficulty."""
    emojis = {
        "Beginner": "🟢",
        "Intermediate": "🟡",
        "Advanced": "🔴"
    }
    return emojis.get(difficulty, "❓")


def calculate_workout_level(completed_count: int) -> str:
    """Calculate recommended workout level based on completion."""
    if completed_count < 5:
        return "Beginner"
    elif completed_count < 15:
        return "Intermediate"
    else:
        return "Advanced"


def get_drill_recommendation_reason(accuracy: float, difficulty: str) -> str:
    """Get reason for drill recommendation."""
    if accuracy < 60:
        return "Practice weak area"
    elif accuracy < 75:
        return "Improve consistency"
    elif difficulty == "Beginner":
        return "Master fundamentals"
    elif difficulty == "Intermediate":
        return "Progress to advanced"
    else:
        return "Challenge yourself"


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength with OWASP-aligned minimum checks."""
    if len(password) < 10:
        return False, "Password must be at least 10 characters"
    if len(password) > 128:
        return False, "Password is too long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must include at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must include at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must include at least one number"
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, "Password must include at least one special character"
    return True, "Valid password"


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 50:
        return False, "Username is too long"
    if not username.replace("_", "").replace("-", "").isalnum():
        return False, "Username can only contain letters, numbers, hyphens, and underscores"
    return True, "Valid username"


def normalize_input(value: str, max_length: int = 255) -> str:
    """Normalize user input by trimming and enforcing max length."""
    if value is None:
        return ""
    return value.strip()[:max_length]


def validate_safe_text(value: str, field_name: str, max_length: int = 255) -> tuple[bool, str]:
    """Validate free text input length and basic safety constraints."""
    cleaned = normalize_input(value, max_length=max_length)
    if not cleaned:
        return False, f"{field_name} is required"
    if "\x00" in cleaned:
        return False, f"{field_name} contains invalid characters"
    return True, cleaned


def get_streak_count(logs: list) -> int:
    """Calculate streak of consecutive training days."""
    if not logs:
        return 0
    
    from datetime import timedelta, date
    
    # Count consecutive days from today backwards
    streak = 0
    current_date = date.today()
    
    sorted_dates = sorted(set([log['date'].date() for log in logs]), reverse=True)
    
    for log_date in sorted_dates:
        if (current_date - log_date).days <= 1:
            streak += 1
            current_date = log_date
        else:
            break
    
    return streak


def get_achievement_badge(user_stats: dict) -> list:
    """Get achievement badges based on user stats."""
    badges = []
    
    if user_stats.get('total_matches', 0) >= 5:
        badges.append({"name": "Active Player", "emoji": "🎾"})
    
    if user_stats.get('win_percentage', 0) >= 70:
        badges.append({"name": "Champion", "emoji": "🏆"})
    
    if user_stats.get('total_matches', 0) >= 20:
        badges.append({"name": "Consistent", "emoji": "🔥"})
    
    if user_stats.get('mfa_enabled', False):
        badges.append({"name": "Security Conscious", "emoji": "🔒"})
    
    return badges
