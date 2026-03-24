"""Score tracking for tennis matches and practice."""
from sqlalchemy.orm import Session
from backend.database import Score, SessionLocal, User
from datetime import datetime, timedelta
from typing import Optional
from backend.utils import normalize_input, validate_safe_text


class ScoreManager:
    """Manage match scores and statistics."""

    ALLOWED_MATCH_TYPES = {"Singles", "Doubles", "Practice"}
    
    @staticmethod
    def log_score(user_id: int, match_type: str, opponent: str,
                  score_won: int, score_lost: int,
                  sets_won: int, sets_lost: int,
                  notes: Optional[str] = None) -> dict:
        """Log a match score."""
        db = SessionLocal()
        try:
            match_type = normalize_input(match_type, max_length=20)
            if match_type not in ScoreManager.ALLOWED_MATCH_TYPES:
                return {"success": False, "message": "Invalid match type"}

            opponent_ok, opponent_clean = validate_safe_text(opponent, "Opponent", max_length=80)
            if not opponent_ok:
                return {"success": False, "message": opponent_clean}

            if not (0 <= int(score_won) <= 1000 and 0 <= int(score_lost) <= 1000):
                return {"success": False, "message": "Points must be between 0 and 1000"}

            if not (0 <= int(sets_won) <= 3 and 0 <= int(sets_lost) <= 3):
                return {"success": False, "message": "Sets must be between 0 and 3"}

            notes_clean = normalize_input(notes or "", max_length=500)

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "User not found"}
            
            score = Score(
                user_id=user_id,
                match_type=match_type,
                opponent=opponent_clean,
                score_won=int(score_won),
                score_lost=int(score_lost),
                sets_won=int(sets_won),
                sets_lost=int(sets_lost),
                notes=notes_clean if notes_clean else None
            )
            db.add(score)
            db.commit()
            db.refresh(score)
            
            return {
                "success": True,
                "message": "Score logged successfully",
                "score_id": score.id,
                "result": "Won" if sets_won > sets_lost else "Lost"
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_score_history(user_id: int, limit: int = 20) -> dict:
        """Get recent match scores."""
        db = SessionLocal()
        try:
            scores = db.query(Score).filter(
                Score.user_id == user_id
            ).order_by(Score.date.desc()).limit(limit).all()
            
            history = []
            for score in scores:
                history.append({
                    "id": score.id,
                    "date": score.date,
                    "match_type": score.match_type,
                    "opponent": score.opponent,
                    "score": f"{score.score_won}-{score.score_lost}",
                    "sets": f"{score.sets_won}-{score.sets_lost}",
                    "result": "Won" if score.sets_won > score.sets_lost else "Lost",
                    "notes": score.notes
                })
            
            return {"success": True, "history": history}
        except Exception as e:
            return {"success": False, "message": str(e), "history": []}
        finally:
            db.close()
    
    @staticmethod
    def get_statistics(user_id: int, days: int = 90) -> dict:
        """Get player statistics."""
        db = SessionLocal()
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            scores = db.query(Score).filter(
                Score.user_id == user_id,
                Score.date >= since
            ).all()
            
            if not scores:
                return {
                    "success": True,
                    "stats": {
                        "total_matches": 0,
                        "wins": 0,
                        "losses": 0,
                        "win_percentage": 0,
                        "avg_points_per_match": 0,
                        "by_match_type": {}
                    }
                }
            
            total = len(scores)
            wins = sum(1 for s in scores if s.sets_won > s.sets_lost)
            losses = total - wins
            
            total_points_won = sum(s.score_won for s in scores)
            total_points = sum(s.score_won + s.score_lost for s in scores)
            
            win_pct = (wins / total * 100) if total > 0 else 0
            avg_points = (total_points_won / total) if total > 0 else 0
            
            # Stats by match type
            by_type = {}
            for match_type in set(s.match_type for s in scores):
                type_scores = [s for s in scores if s.match_type == match_type]
                type_wins = sum(1 for s in type_scores if s.sets_won > s.sets_lost)
                by_type[match_type] = {
                    "matches": len(type_scores),
                    "wins": type_wins,
                    "losses": len(type_scores) - type_wins
                }
            
            return {
                "success": True,
                "stats": {
                    "total_matches": total,
                    "wins": wins,
                    "losses": losses,
                    "win_percentage": round(win_pct, 1),
                    "avg_points_per_match": round(avg_points, 1),
                    "by_match_type": by_type,
                    "period_days": days,
                    "total_points_won": total_points_won,
                    "total_points_played": total_points
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e), "stats": {}}
        finally:
            db.close()
    
    @staticmethod
    def get_head_to_head(user_id: int, opponent: str) -> dict:
        """Get head-to-head record against a specific opponent."""
        db = SessionLocal()
        try:
            scores = db.query(Score).filter(
                Score.user_id == user_id,
                Score.opponent.ilike(f"%{opponent}%")
            ).all()
            
            if not scores:
                return {
                    "success": True,
                    "opponent": opponent,
                    "record": "0-0",
                    "matches": []
                }
            
            wins = sum(1 for s in scores if s.sets_won > s.sets_lost)
            losses = len(scores) - wins
            
            matches = [
                {
                    "date": s.date,
                    "match_type": s.match_type,
                    "score": f"{s.score_won}-{s.score_lost}",
                    "sets": f"{s.sets_won}-{s.sets_lost}",
                    "result": "Won" if s.sets_won > s.sets_lost else "Lost"
                }
                for s in sorted(scores, key=lambda x: x.date, reverse=True)
            ]
            
            return {
                "success": True,
                "opponent": opponent,
                "record": f"{wins}-{losses}",
                "matches": matches
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()
