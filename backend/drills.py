"""Drill recommendations for tennis practice."""
from sqlalchemy.orm import Session
from backend.database import DrillLog, SessionLocal
from datetime import datetime, timedelta


DRILLS = {
    "Forehand": [
        {
            "id": "fh_1",
            "name": "Crosscourt Forehand Consistency",
            "description": "Build consistency on forehand crosscourt shots",
            "instructions": [
                "Feed balls from the opposite baseline or use ball machine",
                "Hit forehands diagonally across the court",
                "Target: 20 consecutive shots in the court",
                "Progress: Increase pace gradually"
            ],
            "target_reps": 20,
            "difficulty": "Beginner",
            "benefits": "Consistency and control"
        },
        {
            "id": "fh_2",
            "name": "Forehand Down the Line",
            "description": "Develop precision on forehand down the line",
            "instructions": [
                "Position yourself on the baseline",
                "Hit forehand shots down the sideline",
                "Target: 15 consecutive shots in the court",
                "Focus on depth and accuracy"
            ],
            "target_reps": 15,
            "difficulty": "Intermediate",
            "benefits": "Stroke precision and court awareness"
        },
        {
            "id": "fh_3",
            "name": "Forehand Loop Drill",
            "description": "Practice forehand loops and open court shots",
            "instructions": [
                "Alternate between crosscourt and down-the-line forehands",
                "Create an opening and hit aggressive shots",
                "Target: Hit 5 consecutive winners from loop patterns",
                "Simulate match-like situations"
            ],
            "target_reps": 5,
            "difficulty": "Advanced",
            "benefits": "Shot variety and aggressive play"
        }
    ],
    "Backhand": [
        {
            "id": "bh_1",
            "name": "Backhand Crosscourt Consistency",
            "description": "Build consistency on backhand crosscourt shots",
            "instructions": [
                "Feed balls from the opposite baseline",
                "Hit backhands diagonally across the court",
                "Target: 20 consecutive shots in the court",
                "Focus on solid contact and follow-through"
            ],
            "target_reps": 20,
            "difficulty": "Beginner",
            "benefits": "Consistency and control"
        },
        {
            "id": "bh_2",
            "name": "Backhand Down the Line",
            "description": "Develop precision on backhand down the line",
            "instructions": [
                "Position yourself on the baseline",
                "Hit backhand shots down the sideline",
                "Target: 12 consecutive shots in the court",
                "Emphasize depth and the follow-through"
            ],
            "target_reps": 12,
            "difficulty": "Intermediate",
            "benefits": "Precision and defensive positioning"
        },
        {
            "id": "bh_3",
            "name": "One-Handed Backhand Slice",
            "description": "Master the backhand slice",
            "instructions": [
                "Practice slice backhand returns to different depths",
                "Target: 10 slices with good depth control",
                "Vary the angle and spin",
                "Practice both defensive and offensive slices"
            ],
            "target_reps": 10,
            "difficulty": "Advanced",
            "benefits": "Shot variety and net approach"
        }
    ],
    "Serve": [
        {
            "id": "serve_1",
            "name": "Flat Serve Accuracy",
            "description": "Develop flat serve accuracy",
            "instructions": [
                "Serve 10 balls to the deuce court",
                "Rest, then serve 10 balls to the ad court",
                "Target: 16 out of 20 serves in the box",
                "Focus on consistency over pace"
            ],
            "target_reps": 20,
            "difficulty": "Beginner",
            "benefits": "Serve consistency"
        },
        {
            "id": "serve_2",
            "name": "Slice Serve Control",
            "description": "Master slice serve with accuracy",
            "instructions": [
                "Practice slice serve to different zones",
                "10 serves to deuce court (wide), 10 to ad court",
                "Target: Control slice movement while maintaining accuracy",
                "Progress: Increase pace"
            ],
            "target_reps": 20,
            "difficulty": "Intermediate",
            "benefits": "Serve variety and placement"
        },
        {
            "id": "serve_3",
            "name": "Kick Serve Development",
            "description": "Develop kick serve for returning serves",
            "instructions": [
                "Practice kick serve motion with focus on rotation",
                "Serve 10 to each court",
                "Target: High kick with minimum 16 feet clearance over net",
                "Game simulation: Mix with other serve types"
            ],
            "target_reps": 20,
            "difficulty": "Advanced",
            "benefits": "Premium serve options"
        }
    ],
    "Volley": [
        {
            "id": "volley_1",
            "name": "Forehand Volley Basics",
            "description": "Build forehand volley fundamentals",
            "instructions": [
                "Stand at the net",
                "Coach feeds balls to forehand side",
                "Target: 20 consecutive forehands volleys in court",
                "Focus on short backswing and clean contact"
            ],
            "target_reps": 20,
            "difficulty": "Beginner",
            "benefits": "Net play foundation"
        },
        {
            "id": "volley_2",
            "name": "Backhand Volley Drill",
            "description": "Develop backhand volley skills",
            "instructions": [
                "Coach feeds to backhand side at net",
                "Target: 15 consecutive backhand volleys",
                "Mix with forehand volleys for alternating practice",
                "Work on punch and positioning"
            ],
            "target_reps": 15,
            "difficulty": "Intermediate",
            "benefits": "Balanced net play"
        },
        {
            "id": "volley_3",
            "name": "High Volley & Overhead Practice",
            "description": "Practice elevated balls at the net",
            "instructions": [
                "Feed high balls near the net",
                "Practice high volleys and overheads",
                "Target: 12 consecutive successfully executed shots",
                "Focus on control and depth"
            ],
            "target_reps": 12,
            "difficulty": "Advanced",
            "benefits": "Complete net coverage"
        }
    ],
    "Return": [
        {
            "id": "return_1",
            "name": "Return of Serve Fundamentals",
            "description": "Build return of serve consistency",
            "instructions": [
                "Partner serves at moderate pace",
                "Practice returns to both sides",
                "Target: Return 12 first serves and 12 second serves in court",
                "Focus on neutral positioning and racquet prep"
            ],
            "target_reps": 24,
            "difficulty": "Beginner",
            "benefits": "Return consistency"
        },
        {
            "id": "return_2",
            "name": "Aggressive Return of Serve",
            "description": "Develop aggressive return game",
            "instructions": [
                "Receive faster serves at 100+ mph",
                "Practice early contact and aggressive returns",
                "Target: 10 quality returns with depth",
                "Vary targets (crosscourt and down the line)"
            ],
            "target_reps": 10,
            "difficulty": "Intermediate",
            "benefits": "Aggressive return options"
        },
        {
            "id": "return_3",
            "name": "Return of Serve Pressure Drill",
            "description": "Practice returns under match pressure",
            "instructions": [
                "Opponent serves 6 points with rotation",
                "You must break serve pattern consistently",
                "Target: Win 4 out of 6 break point scenarios",
                "Work on reading serves and execution"
            ],
            "target_reps": 6,
            "difficulty": "Advanced",
            "benefits": "Match toughness"
        }
    ],
    "Movement": [
        {
            "id": "movement_1",
            "name": "Footwork Ladder Drill",
            "description": "Improve court footwork and positioning",
            "instructions": [
                "Use agility ladder for quick feet development",
                "Practice split steps and recovery movements",
                "Target: Complete 5 clean runs through ladder",
                "Focus on quick feet and balance"
            ],
            "target_reps": 5,
            "difficulty": "Beginner",
            "benefits": "Footwork speed"
        },
        {
            "id": "movement_2",
            "name": "Court Coverage Patterns",
            "description": "Develop efficient court movement patterns",
            "instructions": [
                "Coach feeds balls; you move to each ball and hit",
                "Work on split steps, cross-steps, and recovery",
                "Target: Retrieve and hit 15 balls from various positions",
                "Simulate match-like movement"
            ],
            "target_reps": 15,
            "difficulty": "Intermediate",
            "benefits": "Court positioning"
        },
        {
            "id": "movement_3",
            "name": "Point Simulation - Movement",
            "description": "Practice movement during realistic points",
            "instructions": [
                "Coach calls out shot patterns; you respond athletically",
                "Complete 10 multi-shot points with emphasis on movement",
                "Target: Execute proper recovery and positioning each point",
                "Build consistency and match fitness"
            ],
            "target_reps": 10,
            "difficulty": "Advanced",
            "benefits": "Match-specific movement"
        }
    ]
}


class DrillManager:
    """Manage drill recommendations and tracking."""
    
    @staticmethod
    def get_all_drills() -> dict:
        """Get all available drills organized by type."""
        return DRILLS
    
    @staticmethod
    def get_drills_by_focus(focus_area: str) -> dict:
        """Get recommended drills based on a focus area."""
        if focus_area in DRILLS:
            return {
                "success": True,
                "drills": DRILLS[focus_area]
            }
        return {
            "success": False,
            "message": f"No drills found for focus area: {focus_area}"
        }
    
    @staticmethod
    def get_recommended_drills(user_id: int) -> dict:
        """Get drill recommendations based on user profile and history."""
        db = SessionLocal()
        try:
            # Get user's recent drill performance
            recent_drills = db.query(DrillLog).filter(
                DrillLog.user_id == user_id
            ).order_by(DrillLog.date.desc()).limit(10).all()
            
            # If user is new, recommend beginner drills
            if not recent_drills:
                recommended = []
                for drill_type, drills in DRILLS.items():
                    for drill in drills:
                        if drill["difficulty"] == "Beginner":
                            recommended.append({
                                **drill,
                                "drill_type": drill_type
                            })
                            break
                return {
                    "success": True,
                    "recommended": recommended,
                    "message": "Beginner drills recommended"
                }
            
            # Analyze recent performance and recommend next drills
            completed_types = set()
            low_accuracy = []
            
            for log in recent_drills:
                completed_types.add(log.drill_type)
                if log.accuracy_score and log.accuracy_score < 75:
                    low_accuracy.append(log.drill_type)
            
            # Recommendations: Practice weak areas, then branch to new drills
            recommended = []
            
            # First: Recommend same drills but higher difficulty if accuracy is good
            for log in recent_drills[:3]:
                if log.accuracy_score and log.accuracy_score >= 80:
                    # Find next difficulty
                    if log.drill_type in DRILLS:
                        for drill in DRILLS[log.drill_type]:
                            if drill["id"] == log.drill_id:
                                current_diff = drill["difficulty"]
                                # Find next difficulty level
                                next_diff = "Advanced" if current_diff == "Intermediate" else "Intermediate" if current_diff == "Beginner" else "Advanced"
                                for advanced_drill in DRILLS[log.drill_type]:
                                    if advanced_drill["difficulty"] == next_diff:
                                        recommended.append({
                                            **advanced_drill,
                                            "drill_type": log.drill_type,
                                            "reason": f"Progress from {log.drill_name}"
                                        })
                                break
            
            # Second: Recommend drills for weak areas
            for drill_type in low_accuracy:
                if drill_type in DRILLS:
                    for drill in DRILLS[drill_type]:
                        if drill["difficulty"] == "Beginner":
                            recommended.append({
                                **drill,
                                "drill_type": drill_type,
                                "reason": "Practice weak area"
                            })
                            break
            
            # Third: Recommend new drill types
            all_types = set(DRILLS.keys())
            new_types = all_types - completed_types
            for drill_type in list(new_types)[:2]:
                for drill in DRILLS[drill_type]:
                    if drill["difficulty"] == "Beginner":
                        recommended.append({
                            **drill,
                            "drill_type": drill_type,
                            "reason": "Expand your skills"
                        })
                        break
            
            return {
                "success": True,
                "recommended": recommended[:5]  # Top 5 recommendations
            }
        except Exception as e:
            return {"success": False, "message": str(e), "recommended": []}
        finally:
            db.close()
    
    @staticmethod
    def log_drill(user_id: int, drill_id: str, drill_type: str, 
                  reps: int, accuracy_score: float = None) -> dict:
        """Log a completed drill."""
        db = SessionLocal()
        try:
            drill_id = str(drill_id).strip()
            drill_type = str(drill_type).strip()
            reps = int(reps)
            accuracy_score = float(accuracy_score) if accuracy_score is not None else None

            if drill_type not in DRILLS:
                return {"success": False, "message": "Invalid drill type"}
            if not (1 <= reps <= 1000):
                return {"success": False, "message": "Reps must be between 1 and 1000"}
            if accuracy_score is not None and not (0 <= accuracy_score <= 100):
                return {"success": False, "message": "Accuracy score must be between 0 and 100"}

            # Find drill details
            drill = None
            if drill_type in DRILLS:
                for d in DRILLS[drill_type]:
                    if d["id"] == drill_id:
                        drill = d
                        break
            
            if not drill:
                return {"success": False, "message": "Drill not found"}
            
            # Create log entry
            log = DrillLog(
                user_id=user_id,
                drill_id=drill_id,
                drill_name=drill["name"],
                drill_type=drill_type,
                completed=True,
                reps=reps,
                accuracy_score=accuracy_score
            )
            db.add(log)
            db.commit()
            
            return {
                "success": True,
                "message": "Drill logged successfully",
                "log_id": log.id
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_drill_history(user_id: int, days: int = 30) -> dict:
        """Get drill practice history for the last N days."""
        db = SessionLocal()
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            logs = db.query(DrillLog).filter(
                DrillLog.user_id == user_id,
                DrillLog.date >= since
            ).order_by(DrillLog.date.desc()).all()
            
            history = [
                {
                    "date": log.date,
                    "drill": log.drill_name,
                    "type": log.drill_type,
                    "reps": log.reps,
                    "accuracy": log.accuracy_score
                }
                for log in logs
            ]
            
            return {"success": True, "history": history}
        except Exception as e:
            return {"success": False, "message": str(e), "history": []}
        finally:
            db.close()
