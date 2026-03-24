"""Workout recommendations for tennis players."""
from sqlalchemy.orm import Session
from backend.database import UserBodyFocus, WorkoutLog, SessionLocal, User
from datetime import datetime, timedelta


WORKOUTS = {
    "Legs": [
        {
            "id": "leg_1",
            "name": "Court Sprints & Lunge Drills",
            "description": "Explosive leg training for quick court movement",
            "exercises": [
                "20 x 20ft court sprints (rest 30s between)",
                "Walking lunges across court (3 sets x 10)",
                "Lateral shuffles (3 sets x 20ft each direction)",
                "Single-leg hops (3 sets x 10 each leg)"
            ],
            "duration": 30,
            "difficulty": "Intermediate",
            "benefits": "Improves footwork, explosiveness, and court agility"
        },
        {
            "id": "leg_2",
            "name": "Quad & Calf Strength",
            "description": "Build leg strength for powerful serving and movement",
            "exercises": [
                "Squats (3 sets x 15)",
                "Bulgarian split squats (3 sets x 10 each leg)",
                "Calf raises (3 sets x 20)",
                "Wall sit (3 x 45 seconds)"
            ],
            "duration": 25,
            "difficulty": "Beginner",
            "benefits": "Increases leg power and stability"
        },
        {
            "id": "leg_3",
            "name": "Plyometric Leg Training",
            "description": "Explosive power training for serve and court coverage",
            "exercises": [
                "Box jumps (3 sets x 8)",
                "Jump squats (3 sets x 12)",
                "Broad jumps (3 sets x 5)",
                "Single-leg balance hops (2 sets x 10 each)"
            ],
            "duration": 20,
            "difficulty": "Advanced",
            "benefits": "Maximum explosive power and court reactivity"
        }
    ],
    "Shoulders": [
        {
            "id": "shoulder_1",
            "name": "Serve Power Development",
            "description": "Build shoulder strength for powerful serves",
            "exercises": [
                "Medicine ball overhead slams (3 sets x 12)",
                "Shoulder press (3 sets x 10)",
                "Lateral raises (3 sets x 12)",
                "Reverse pec deck (3 sets x 12)"
            ],
            "duration": 25,
            "difficulty": "Intermediate",
            "benefits": "Increases serve velocity and shoulder stability"
        },
        {
            "id": "shoulder_2",
            "name": "Rotator Cuff Strength",
            "description": "Prevent injury and improve shoulder health",
            "exercises": [
                "Band pull-aparts (3 sets x 15)",
                "Internal rotation (3 sets x 12 each side)",
                "External rotation (3 sets x 12 each side)",
                "Face pulls (3 sets x 15)"
            ],
            "duration": 20,
            "difficulty": "Beginner",
            "benefits": "Injury prevention and shoulder stability"
        },
        {
            "id": "shoulder_3",
            "name": "Full Shoulder Complex",
            "description": "Complete shoulder workout combining strength and stability",
            "exercises": [
                "Push-ups (3 sets x 15)",
                "Downward dog hold to cobra (3 sets x 10)",
                "Shrugs with weight (3 sets x 12)",
                "Band rows (3 sets x 15)"
            ],
            "duration": 30,
            "difficulty": "Intermediate",
            "benefits": "Overall shoulder conditioning for tennis"
        }
    ],
    "Core": [
        {
            "id": "core_1",
            "name": "Tennis Core Stability",
            "description": "Build core power for serve and stroke stability",
            "exercises": [
                "Plank hold (3 x 60 seconds)",
                "Russian twists (3 sets x 20)",
                "Dead bugs (3 sets x 12 each side)",
                "Mountain climbers (3 sets x 20)"
            ],
            "duration": 20,
            "difficulty": "Beginner",
            "benefits": "Improved stroke control and stability"
        },
        {
            "id": "core_2",
            "name": "Rotational Core Power",
            "description": "Build rotational power for groundstrokes and serves",
            "exercises": [
                "Medicine ball wood chops (3 sets x 12 each side)",
                "Pallof press (3 sets x 10 each side)",
                "Bicycle crunches (3 sets x 15)",
                "Ab wheel rollouts (3 sets x 10)"
            ],
            "duration": 25,
            "difficulty": "Intermediate",
            "benefits": "Explosive power in groundstrokes"
        },
        {
            "id": "core_3",
            "name": "Advanced Core Circuit",
            "description": "High-intensity core training for competitive players",
            "exercises": [
                "V-ups (3 sets x 12)",
                "Decline sit-ups with twist (3 sets x 15)",
                "Side plank with hip dip (2 sets x 12 each side)",
                "Ab wheel on unstable surface (3 sets x 10)"
            ],
            "duration": 30,
            "difficulty": "Advanced",
            "benefits": "Maximum core strength and power"
        }
    ],
    "Arms": [
        {
            "id": "arm_1",
            "name": "Forearm & Grip Strength",
            "description": "Develop grip strength for powerful strokes",
            "exercises": [
                "Grip strength exercises with gripper (3 sets x 12)",
                "Wrist curls (3 sets x 15)",
                "Reverse wrist curls (3 sets x 15)",
                "Farmer's carries (3 sets x 40ft)"
            ],
            "duration": 20,
            "difficulty": "Beginner",
            "benefits": "Stronger grip and racquet control"
        },
        {
            "id": "arm_2",
            "name": "Bicep & Tricep Builder",
            "description": "Build arm strength for powerful strokes",
            "exercises": [
                "Dumbbell curls (3 sets x 12)",
                "Tricep dips (3 sets x 10)",
                "Overhead tricep extension (3 sets x 12)",
                "Hammer curls (3 sets x 12)"
            ],
            "duration": 25,
            "difficulty": "Intermediate",
            "benefits": "Increased arm speed and power"
        },
        {
            "id": "arm_3",
            "name": "Complete Arm Circuit",
            "description": "Full arm development including endurance",
            "exercises": [
                "Push-ups (3 sets x 15)",
                "Close-grip push-ups (3 sets x 12)",
                "Superset: Curls + Tricep extensions (3 sets x 12)",
                "Endurance carries (3 x 60 seconds)"
            ],
            "duration": 30,
            "difficulty": "Intermediate",
            "benefits": "Complete arm strength and endurance"
        }
    ],
    "Endurance": [
        {
            "id": "endurance_1",
            "name": "Aerobic Conditioning",
            "description": "Build cardiovascular fitness for long matches",
            "exercises": [
                "Steady-state run: 30 minutes at moderate pace",
                "Or: 30 minutes cycling at moderate intensity"
            ],
            "duration": 30,
            "difficulty": "Beginner",
            "benefits": "Aerobic base for match endurance"
        },
        {
            "id": "endurance_2",
            "name": "Court Sprint Intervals",
            "description": "Match-specific interval training",
            "exercises": [
                "Warm-up: 5 minutes easy movement",
                "10 x 1 minute sprints with 1 minute walk recovery",
                "Cool-down: 3 minutes easy pace"
            ],
            "duration": 25,
            "difficulty": "Intermediate",
            "benefits": "Match-specific cardiovascular fitness"
        },
        {
            "id": "endurance_3",
            "name": "High-Intensity Interval Training",
            "description": "Maximum cardiovascular fitness development",
            "exercises": [
                "30 seconds max effort sprint, 30 seconds recovery (x12)",
                "Including court-specific movements when possible"
            ],
            "duration": 20,
            "difficulty": "Advanced",
            "benefits": "Peak cardiovascular fitness"
        }
    ]
}


class WorkoutManager:
    """Manage workout recommendations and tracking."""
    
    @staticmethod
    def get_recommended_workouts(user_id: int) -> dict:
        """Get workout recommendations based on user's body focus areas."""
        db = SessionLocal()
        try:
            # Get user's focus areas
            focus_areas = db.query(UserBodyFocus).filter(
                UserBodyFocus.user_id == user_id
            ).all()
            
            if not focus_areas:
                return {
                    "success": True,
                    "message": "Please set your body focus areas first",
                    "workouts": []
                }
            
            # Get workouts for focus areas
            recommended = []
            for focus in focus_areas:
                if focus.body_part in WORKOUTS:
                    workouts = WORKOUTS[focus.body_part]
                    # Pick difficulty based on focus level
                    difficulty = "Beginner" if focus.focus_level <= 2 else ("Intermediate" if focus.focus_level <= 4 else "Advanced")
                    
                    for workout in workouts:
                        if workout["difficulty"] == difficulty:
                            recommended.append({
                                **workout,
                                "body_part": focus.body_part,
                                "focus_level": focus.focus_level
                            })
                            break
            
            return {
                "success": True,
                "workouts": recommended
            }
        except Exception as e:
            return {"success": False, "message": str(e), "workouts": []}
        finally:
            db.close()
    
    @staticmethod
    def log_workout(user_id: int, workout_id: str, body_part: str, 
                   duration_minutes: int, difficulty: str) -> dict:
        """Log a completed workout."""
        db = SessionLocal()
        try:
            workout_id = str(workout_id).strip()
            body_part = str(body_part).strip()
            difficulty = str(difficulty).strip()
            duration_minutes = int(duration_minutes)

            if body_part not in WORKOUTS:
                return {"success": False, "message": "Invalid body part"}
            if difficulty not in {"Beginner", "Intermediate", "Advanced"}:
                return {"success": False, "message": "Invalid difficulty"}
            if not (5 <= duration_minutes <= 180):
                return {"success": False, "message": "Workout duration must be between 5 and 180 minutes"}

            # Find workout details
            workout = None
            if body_part in WORKOUTS:
                for w in WORKOUTS[body_part]:
                    if w["id"] == workout_id:
                        workout = w
                        break
            
            if not workout:
                return {"success": False, "message": "Workout not found"}
            
            # Create log entry
            log = WorkoutLog(
                user_id=user_id,
                workout_id=workout_id,
                workout_name=workout["name"],
                body_part=body_part,
                completed=True,
                duration_minutes=duration_minutes,
                difficulty=difficulty
            )
            db.add(log)
            db.commit()
            
            return {
                "success": True,
                "message": "Workout logged successfully",
                "log_id": log.id
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_workout_history(user_id: int, days: int = 30) -> dict:
        """Get workout history for the last N days."""
        db = SessionLocal()
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            logs = db.query(WorkoutLog).filter(
                WorkoutLog.user_id == user_id,
                WorkoutLog.date >= since
            ).order_by(WorkoutLog.date.desc()).all()
            
            history = [
                {
                    "date": log.date,
                    "workout": log.workout_name,
                    "body_part": log.body_part,
                    "duration": log.duration_minutes,
                    "difficulty": log.difficulty
                }
                for log in logs
            ]
            
            return {"success": True, "history": history}
        except Exception as e:
            return {"success": False, "message": str(e), "history": []}
        finally:
            db.close()
