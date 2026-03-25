"""
TennisPro - Complete Tennis Training App with MFA
A Streamlit-based application for tennis players to track scores,
complete personalized workouts, and practice drills.
"""
import streamlit as st
from PIL import Image
import io
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Import backend modules
from backend.auth import AuthManager
from backend.workouts import WorkoutManager
from backend.drills import DrillManager
from backend.scores import ScoreManager
from backend.database import SessionLocal, User, UserBodyFocus
from backend.utils import validate_email, validate_password, validate_username, normalize_input

# Page configuration
st.set_page_config(
    page_title="TennisPro",
    page_icon="TP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import at top for CSS
from pathlib import Path

# Custom CSS for tennis theming - Applied directly
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Manrope:wght@400;500;600&family=Space+Grotesk:wght@500;600&family=Archivo+Black&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Manrope', sans-serif; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Playfair Display', serif !important; color: #1e5f3e; letter-spacing: 0.2px; }
        
        [data-testid="stAppViewContainer"] { 
            background: linear-gradient(135deg, #ffffff 0%, #e8f5f0 50%, #d4f1e7 100%);
        }
        [data-testid="stSidebar"] { 
            background: linear-gradient(180deg, #1e5f3e 0%, #2d8659 100%) !important;
        }
        .tennis-header { 
            background: linear-gradient(135deg, #1e5f3e 0%, #2d8659 50%, #3a9d6f 100%);
            color: white; padding: 52px 30px; border-radius: 15px; text-align: center;
            margin-bottom: 20px; box-shadow: 0 8px 16px rgba(30, 95, 62, 0.2);
            border-bottom: 4px solid #ffd700;
        }
        .tennis-header h1 { 
            font-family: 'Archivo Black', 'Playfair Display', serif; font-weight: 900; color: #fff !important; font-size: 4.4em;
            margin: 10px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); letter-spacing: 2px;
        }
        .tennis-header p { color: #fff; font-size: 1.1em; margin: 10px 0 0 0; font-weight: 500; font-family: 'Space Grotesk', sans-serif; letter-spacing: 0.4px; }
        .tennis-card { 
            background: linear-gradient(135deg, #ffffff 0%, #f0fdf9 100%); padding: 20px;
            border-radius: 12px; border-left: 5px solid #2d8659; border-right: 1px solid #d4f1e7;
            border-top: 1px solid #d4f1e7; margin: 10px 0; box-shadow: 0 4px 12px rgba(30, 95, 62, 0.1);
            transition: all 0.3s ease;
        }
        .tennis-card:hover { 
            box-shadow: 0 6px 16px rgba(30, 95, 62, 0.2); transform: translateY(-2px);
        }
        .stat-box { 
            background: linear-gradient(135deg, #2d8659 0%, #1e5f3e 50%, #155d3d 100%);
            color: white; padding: 25px; border-radius: 12px; text-align: center; margin: 10px;
            box-shadow: 0 6px 16px rgba(30, 95, 62, 0.3); border-top: 3px solid #ffd700;
            transition: all 0.3s ease;
        }
        .stat-box:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(30, 95, 62, 0.4); }
        .stat-box h3 { color: #ffd700 !important; margin: 0 0 10px 0; font-size: 1.1em; }
        .stat-box h2 { color: #fff !important; margin: 10px 0; font-size: 2.5em; }
        .stat-box p { color: #d4f1e7; margin: 0; font-size: 0.95em; }
        .streamlit-expanderHeader { 
            background: linear-gradient(90deg, #2d8659 0%, #1e5f3e 100%); color: white;
            border-radius: 8px; padding: 10px; border-left: 4px solid #ffd700 !important;
        }
        .stButton > button { 
            background: linear-gradient(90deg, #2d8659 0%, #1e5f3e 100%); color: white; border: none;
            border-radius: 8px; padding: 12px 24px; font-weight: 600; transition: all 0.3s ease;
            box-shadow: 0 4px 8px rgba(30, 95, 62, 0.2);
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: 0.2px;
        }
        .stButton > button:hover { 
            background: linear-gradient(90deg, #3a9d6f 0%, #2d8659 100%);
            box-shadow: 0 6px 12px rgba(30, 95, 62, 0.3); transform: translateY(-2px);
        }
        .stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox select { 
            border: 2px solid #d4f1e7 !important; border-radius: 8px; padding: 10px;
            background-color: #fff !important; color: #1e5f3e !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus { 
            border-color: #2d8659 !important; box-shadow: 0 0 0 3px rgba(45, 134, 89, 0.1) !important;
        }
        .stTabs { gap: 1px; }
        .stTabs [data-baseweb="tab"] { 
            font-family: 'Playfair Display', serif; color: #1e5f3e; background-color: #e8f5f0;
            border-radius: 8px 8px 0 0; padding: 15px 20px; font-weight: 600;
        }
        .stTabs [aria-selected="true"] { 
            background: linear-gradient(90deg, #2d8659 0%, #1e5f3e 100%) !important; color: white !important;
        }
        .stMetricLabel { color: #1e5f3e; font-family: 'Space Grotesk', sans-serif; font-weight: 600; }
        .stMarkdown p, .stMarkdown li, .stCaption, label { font-family: 'Manrope', sans-serif !important; }
        .stAlert { border-radius: 10px; }
        .stDataFrame, .stTable { border-radius: 10px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)


def init_session_state():
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "mfa_enabled" not in st.session_state:
        st.session_state.mfa_enabled = False
    if "mfa_verified" not in st.session_state:
        st.session_state.mfa_verified = False
    if "email_verified" not in st.session_state:
        st.session_state.email_verified = False
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "selected_workout_id" not in st.session_state:
        st.session_state.selected_workout_id = None
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "temp_mfa_code" not in st.session_state:
        st.session_state.temp_mfa_code = None
    if "mfa_email_sent" not in st.session_state:
        st.session_state.mfa_email_sent = None


def show_header():
    """Display app header."""
    st.markdown("""
        <div class="tennis-header">
            <h1>TennisPro</h1>
            <p>Master Your Game • Track • Train • Improve</p>
        </div>
    """, unsafe_allow_html=True)


def login_page():
    """User login and registration page."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h2 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Sign In</h2>", unsafe_allow_html=True)
        st.markdown("""
            <div class="tennis-card">
            Sign in to your TennisPro account and start training!
            </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        if st.button("Sign In", use_container_width=True):
            if username and password:
                username = normalize_input(username, max_length=50)

                result = AuthManager.authenticate_user(username, password)
                if result["success"]:
                    st.session_state.login_attempts = 0
                    st.session_state.user_id = result["user_id"]
                    st.session_state.username = result["username"]
                    st.session_state.mfa_enabled = result["mfa_enabled"]
                    st.session_state.email_verified = result["email_verified"]

                    if result["mfa_enabled"]:
                        challenge = AuthManager.issue_login_mfa_challenge(result["user_id"])
                        if not challenge["success"]:
                            st.error(f"❌ {challenge['message']}")
                            return

                        st.session_state.mfa_verified = False
                        st.session_state.page = "email_verify"
                        st.session_state.mfa_email_sent = challenge.get("email_sent", False)
                        st.session_state.temp_mfa_code = challenge.get("verification_code")
                        st.rerun()
                    else:
                        st.session_state.mfa_verified = True
                        st.session_state.page = "dashboard"
                        st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    st.error(f"❌ {result['message']}")
            else:
                st.warning("⚠️ Please enter username and password")
    
    with col2:
        st.markdown("<h2 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Create Account</h2>", unsafe_allow_html=True)
        st.markdown("""
            <div class="tennis-card">
            Join the TennisPro community today and elevate your game!
            </div>
        """, unsafe_allow_html=True)
        
        new_username = st.text_input("New Username", key="signup_username", placeholder="Choose a username")
        new_email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
        new_password = st.text_input("Password", type="password", key="signup_password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Confirm your password")
        
        if st.button("Create Account", use_container_width=True):
            if not all([new_username, new_email, new_password, confirm_password]):
                st.warning("⚠️ All fields are required")
            elif new_password != confirm_password:
                st.error("❌ Passwords don't match")
            else:
                new_username = normalize_input(new_username, max_length=50)
                new_email = normalize_input(new_email, max_length=254).lower()

                username_valid, username_message = validate_username(new_username)
                if not username_valid:
                    st.error(f"❌ {username_message}")
                elif not validate_email(new_email):
                    st.error("❌ Enter a valid email address")
                else:
                    password_valid, password_message = validate_password(new_password)
                    if not password_valid:
                        st.error(f"❌ {password_message}")
                    else:
                        result = AuthManager.create_user(new_username, new_email, new_password)
                        if result["success"]:
                            st.success("✅ Account created and automatically verified. Please log in.")
                            st.balloons()
                        else:
                            st.error(f"❌ {result['message']}")


def mfa_setup_page():
    """MFA setup page."""
    st.markdown("<h2 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Set Up Two-Factor Authentication</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="tennis-card">
        Two-Factor Authentication (2FA) adds an extra layer of security to your account.
        Use an authenticator app like Google Authenticator, Authy, or Microsoft Authenticator.
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("📲 Enable 2FA"):
        result = AuthManager.setup_mfa(st.session_state.user_id)
        if result["success"]:
            st.success("🎾 2FA Setup Initiated!")
            
            # Display QR code
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Scan QR Code</h3>", unsafe_allow_html=True)
                qr_image = Image.open(io.BytesIO(result["qr_code"]))
                st.image(qr_image, use_column_width=True)
            
            with col2:
                st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Or Enter Manually</h3>", unsafe_allow_html=True)
                st.code(result["secret_key"], language="text")
                st.info("💾 Save this code in a safe place!")
            
            st.markdown("---")
            
            mfa_code = st.text_input("Enter 6-digit code from your authenticator app:")
            
            if st.button("✅ Verify & Enable 2FA"):
                if len(mfa_code) == 6:
                    verify_result = AuthManager.verify_mfa_code(st.session_state.user_id, mfa_code)
                    if verify_result["success"]:
                        enable_result = AuthManager.enable_mfa(st.session_state.user_id)
                        if enable_result["success"]:
                            st.success("🎉 2FA Enabled Successfully!")
                            st.session_state.mfa_verified = True
                            st.session_state.page = "dashboard"
                            st.rerun()
                        else:
                            st.error(f"❌ {enable_result['message']}")
                    else:
                        st.error("❌ Invalid code. Please try again.")
                else:
                    st.warning("⚠️ Enter a valid 6-digit code")


def email_verify_page():
    """MFA verification page."""
    st.markdown("<h2 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Verify Your Login</h2>", unsafe_allow_html=True)

    if st.session_state.get("mfa_email_sent"):
        st.markdown("""
            <div class="tennis-card">
            A one-time MFA code has been sent to your email address. Enter it below to continue.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Email could not be sent — Gmail App Password not yet configured. Use the temporary code below to log in now.")
        if st.session_state.get("temp_mfa_code"):
            st.markdown(
                f"""
                <div style='background:#1e5f3e;color:white;padding:18px 24px;border-radius:10px;
                            font-size:2em;font-weight:700;text-align:center;letter-spacing:6px;
                            margin:10px 0;'>
                🔑 {st.session_state.temp_mfa_code}
                </div>
                <p style='text-align:center;color:#555;font-size:0.9em;margin-top:4px;'>
                Enter this code below — it expires in 10 minutes.
                </p>
                """,
                unsafe_allow_html=True,
            )
    
    verification_code = st.text_input("Enter 6-digit code:", max_chars=6, key="email_verify_code", placeholder="000000")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Verify MFA Code", use_container_width=True):
            if len(verification_code) == 6 and verification_code.isdigit():
                result = AuthManager.verify_email_code(st.session_state.user_id, verification_code)
                if result["success"]:
                    st.success("✅ MFA verified successfully!")
                    st.session_state.mfa_verified = True
                    st.session_state.temp_mfa_code = None
                    st.session_state.mfa_email_sent = None
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
            else:
                st.warning("⚠️ Enter a valid 6-digit code")
    
    with col2:
        if st.button("🔄 Resend MFA Code", use_container_width=True):
            result = AuthManager.resend_verification_code(st.session_state.user_id)
            if result["success"]:
                if result.get("email_sent"):
                    st.session_state.mfa_email_sent = True
                    st.session_state.temp_mfa_code = None
                    st.success("✅ MFA code resent to your email!")
                else:
                    st.session_state.mfa_email_sent = False
                    st.session_state.temp_mfa_code = result.get("verification_code")
                    st.rerun()
            else:
                st.error(f"❌ {result['message']}")
    
    with col3:
        if st.button("🏠 Logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.mfa_enabled = False
            st.session_state.mfa_verified = False
            st.session_state.email_verified = False
            st.session_state.temp_mfa_code = None
            st.session_state.mfa_email_sent = None
            st.session_state.page = "home"
            st.rerun()

def setup_body_focus():
    """Setup body focus areas for personalized recommendations."""
    st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Where would you like to focus?</h3>", unsafe_allow_html=True)
    
    body_parts = {
        "Legs": "Speed, agility, and explosiveness",
        "Shoulders": "Serve power and stability",
        "Core": "Rotation power and stability",
        "Arms": "Grip strength and arm speed",
        "Endurance": "Cardiovascular fitness"
    }
    
    db = SessionLocal()
    try:
        existing = db.query(UserBodyFocus).filter(
            UserBodyFocus.user_id == st.session_state.user_id
        ).all()
        existing_parts = {e.body_part: e.focus_level for e in existing}
    finally:
        db.close()
    
    focus_data = {}
    for body_part, description in body_parts.items():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{body_part}**")
            st.write(f"_{description}_")
        with col2:
            focus_data[body_part] = st.slider(
                f"Focus Level",
                min_value=1,
                max_value=5,
                value=existing_parts.get(body_part, 3),
                key=f"focus_{body_part}",
                label_visibility="collapsed"
            )
    
    if st.button("💾 Save Body Focus Areas", use_container_width=True):
        db = SessionLocal()
        try:
            # Delete existing
            db.query(UserBodyFocus).filter(
                UserBodyFocus.user_id == st.session_state.user_id
            ).delete()
            
            # Add new
            for body_part, level in focus_data.items():
                focus = UserBodyFocus(
                    user_id=st.session_state.user_id,
                    body_part=body_part,
                    focus_level=level
                )
                db.add(focus)
            
            db.commit()
            st.success("✅ Body focus areas saved!")
            st.session_state.setup_complete = True
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
        finally:
            db.close()


def workouts_page():
    """Dedicated workouts page for direct navigation from recommendations."""
    show_header()
    st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Personalized Workouts</h3>", unsafe_allow_html=True)

    col_top1, col_top2 = st.columns([1, 4])
    with col_top1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    workout_result = WorkoutManager.get_recommended_workouts(st.session_state.user_id)

    if st.session_state.selected_workout_id is not None and workout_result["success"] and workout_result["workouts"]:
        selected = next((w for w in workout_result["workouts"] if w['id'] == st.session_state.selected_workout_id), None)
        if selected:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #1e5f3e 0%, #2d8659 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
                <h3 style='margin: 0; font-family: Playfair Display, serif; color: white;'>Selected Workout</h3>
                <p style='margin: 5px 0;'><strong>{selected['name']}</strong></p>
                <p style='margin: 5px 0;'>{selected['body_part']} • {selected['difficulty']} • ⏱️ {selected['duration']} min</p>
                </div>
            """, unsafe_allow_html=True)

    if workout_result["success"] and workout_result["workouts"]:
        for idx, workout in enumerate(workout_result["workouts"]):
            expanded = st.session_state.selected_workout_id == workout['id']
            with st.expander(f"🏋️ {workout['name']} - {workout['body_part']} ({workout['difficulty']})", expanded=expanded):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Duration", f"{workout['duration']} min")
                with col2:
                    st.metric("Difficulty", workout['difficulty'])
                with col3:
                    st.metric("Body Part", workout['body_part'])

                st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Exercises</h4>", unsafe_allow_html=True)
                for exercise in workout['exercises']:
                    st.write(f"• {exercise}")

                st.markdown(f"**Benefits:** {workout['benefits']}")

                col1, col2 = st.columns(2)
                with col1:
                    duration = st.number_input(
                        f"Duration (min) for {workout['id']}",
                        value=workout['duration'],
                        key=f"duration_page_{idx}"
                    )
                with col2:
                    if st.button("✅ Complete Workout", key=f"complete_page_{idx}"):
                        log_result = WorkoutManager.log_workout(
                            st.session_state.user_id,
                            workout['id'],
                            workout['body_part'],
                            int(duration),
                            workout['difficulty']
                        )
                        if log_result["success"]:
                            st.success("🎉 Workout logged!")
                            st.session_state.selected_workout_id = None
                            st.rerun()
                        else:
                            st.error(f"❌ {log_result['message']}")
    else:
        st.info("No workouts available. Please set your body focus areas!")


def dashboard_page():
    """Main dashboard page."""
    show_header()
    
    st.write(f"Welcome back, **{st.session_state.username}**! 🎾")
    
    # Check if setup is complete
    db = SessionLocal()
    try:
        focus_count = db.query(UserBodyFocus).filter(
            UserBodyFocus.user_id == st.session_state.user_id
        ).count()
    finally:
        db.close()
    
    if focus_count == 0:
        st.info("Welcome to TennisPro. Let's set up your profile.")
        setup_body_focus()
        return
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Dashboard",
        "Scores",
        "Workouts",
        "Drills",
        "Stats",
        "Settings"
    ])
    
    # Dashboard Tab
    with tab1:
        st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Your Training Hub</h3>", unsafe_allow_html=True)
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        score_result = ScoreManager.get_statistics(st.session_state.user_id, days=30)
        stats = score_result.get("stats", {})
        
        with col1:
            st.markdown(f"""
                <div class="stat-box">
                    <h3>🎯 Matches</h3>
                    <h2>{stats.get('total_matches', 0)}</h2>
                    <p>Last 30 days</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="stat-box">
                    <h3>✅ Wins</h3>
                    <h2>{stats.get('wins', 0)}</h2>
                    <p>{stats.get('win_percentage', 0)}%</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            workout_result = SessionLocal().query(UserBodyFocus).filter(
                UserBodyFocus.user_id == st.session_state.user_id
            ).count()
            st.markdown(f"""
                <div class="stat-box">
                    <h3>💪 Focus Areas</h3>
                    <h2>{workout_result}</h2>
                    <p>Active areas</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="stat-box">
                    <h3>📊 Streak</h3>
                    <h2>🔥 </h2>
                    <p>Keep training!</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Recent Matches</h4>", unsafe_allow_html=True)
            score_history = ScoreManager.get_score_history(st.session_state.user_id, limit=5)
            if score_history["success"] and score_history["history"]:
                for match in score_history["history"][:5]:
                    result_emoji = "✅" if match["result"] == "Won" else "❌"
                    st.markdown(f"""
                        {result_emoji} **{match['opponent']}** ({match['match_type']})
                        - {match['date'].strftime('%m/%d')}
                        - {match['sets']} sets
                    """)
            else:
                st.info("No matches logged yet")
        
        with col2:
            st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Recommended Workouts</h4>", unsafe_allow_html=True)
            workout_result = WorkoutManager.get_recommended_workouts(st.session_state.user_id)
            if workout_result["success"] and workout_result["workouts"]:
                for idx, workout in enumerate(workout_result["workouts"][:3]):
                    col_inner1, col_inner2 = st.columns([3, 1])
                    with col_inner1:
                        st.markdown(f"""
                            <div class="tennis-card">
                            <strong>{workout['name']}</strong><br>
                            {workout['body_part']} • {workout['difficulty']}<br>
                            ⏱️ {workout['duration']} min
                            </div>
                        """, unsafe_allow_html=True)
                    with col_inner2:
                        if st.button("📋", key=f"view_workout_{idx}", help="View this workout", use_container_width=True):
                            st.session_state.selected_workout_id = workout['id']
                            st.session_state.page = "workouts_page"
                            st.rerun()
            else:
                st.info("No workouts recommended yet")
    
    # Scores Tab
    with tab2:
        st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Match Scores</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Log New Match</h4>", unsafe_allow_html=True)
            match_type = st.selectbox("Match Type", ["Singles", "Doubles", "Practice"])
            opponent = st.text_input("Opponent Name")
            
            col_a, col_b = st.columns(2)
            with col_a:
                score_won = st.number_input("Points Won", min_value=0, value=0)
            with col_b:
                score_lost = st.number_input("Points Lost", min_value=0, value=0)
            
            col_c, col_d = st.columns(2)
            with col_c:
                sets_won = st.number_input("Sets Won", min_value=0, max_value=3, value=0)
            with col_d:
                sets_lost = st.number_input("Sets Lost", min_value=0, max_value=3, value=0)
            
            notes = st.text_area("Match Notes (optional)")
            
            if st.button("📝 Log Score", use_container_width=True):
                if opponent:
                    result = ScoreManager.log_score(
                        st.session_state.user_id,
                        match_type,
                        opponent,
                        score_won,
                        score_lost,
                        sets_won,
                        sets_lost,
                        notes
                    )
                    if result["success"]:
                        st.success(f"✅ Score logged! Result: {result['result']}")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.warning("⚠️ Enter opponent name")
        
        with col2:
            st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Match History</h4>", unsafe_allow_html=True)
            history = ScoreManager.get_score_history(st.session_state.user_id, limit=10)
            if history["success"] and history["history"]:
                for match in history["history"]:
                    result_emoji = "✅" if match["result"] == "Won" else "❌"
                    st.markdown(f"""
                        {result_emoji} {match['date'].strftime('%m/%d/%Y')} - **{match['opponent']}**
                        
                        {match['match_type']} • Sets: {match['sets']} • Points: {match['score']}
                        
                        {match['notes'] if match['notes'] else ''}
                        
                        ---
                    """)
            else:
                st.info("No matches logged yet")
    
    # Workouts Tab
    with tab3:
        st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Personalized Workouts</h3>", unsafe_allow_html=True)
        
        workout_result = WorkoutManager.get_recommended_workouts(st.session_state.user_id)
        
        # Show selected workout if one was selected from dashboard
        if st.session_state.selected_workout_id is not None and workout_result["success"] and workout_result["workouts"]:
            selected = next((w for w in workout_result["workouts"] if w['id'] == st.session_state.selected_workout_id), None)
            if selected:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e5f3e 0%, #2d8659 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
                    <h3 style='margin: 0; font-family: Playfair Display, serif; color: white;'>Selected Workout</h3>
                    <p style='margin: 5px 0;'><strong>{selected['name']}</strong></p>
                    <p style='margin: 5px 0;'>{selected['body_part']} • {selected['difficulty']} • ⏱️ {selected['duration']} min</p>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander("📖 View Details", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Duration", f"{selected['duration']} min")
                    with col2:
                        st.metric("Difficulty", selected['difficulty'])
                    with col3:
                        st.metric("Body Part", selected['body_part'])
                    
                    st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Exercises</h4>", unsafe_allow_html=True)
                    for exercise in selected['exercises']:
                        st.write(f"• {exercise}")
                    
                    st.markdown(f"**Benefits:** {selected['benefits']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        duration = st.number_input(f"Duration (min) for {selected['id']}", value=selected['duration'], key=f"duration_selected")
                    with col2:
                        if st.button(f"✅ Complete This Workout", key=f"complete_selected"):
                            log_result = WorkoutManager.log_workout(
                                st.session_state.user_id,
                                selected['id'],
                                selected['body_part'],
                                int(duration),
                                selected['difficulty']
                            )
                            if log_result["success"]:
                                st.success("🎉 Workout logged!")
                                st.session_state.selected_workout_id = None
                                st.rerun()
                            else:
                                st.error(f"❌ {log_result['message']}")
                st.markdown("---")
        
        if workout_result["success"] and workout_result["workouts"]:
            for idx, workout in enumerate(workout_result["workouts"]):
                with st.expander(f"🏋️ {workout['name']} - {workout['body_part']} ({workout['difficulty']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Duration", f"{workout['duration']} min")
                    with col2:
                        st.metric("Difficulty", workout['difficulty'])
                    with col3:
                        st.metric("Body Part", workout['body_part'])
                    
                    st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Exercises</h4>", unsafe_allow_html=True)
                    for exercise in workout['exercises']:
                        st.write(f"• {exercise}")
                    
                    st.markdown(f"**Benefits:** {workout['benefits']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        duration = st.number_input(f"Duration (min) for {workout['id']}", value=workout['duration'], key=f"duration_{idx}")
                    with col2:
                        if st.button(f"✅ Complete Workout", key=f"complete_{idx}"):
                            log_result = WorkoutManager.log_workout(
                                st.session_state.user_id,
                                workout['id'],
                                workout['body_part'],
                                int(duration),
                                workout['difficulty']
                            )
                            if log_result["success"]:
                                st.success("🎉 Workout logged!")
                                st.rerun()
                            else:
                                st.error(f"❌ {log_result['message']}")
        else:
            st.info("No workouts available. Please set your body focus areas!")
    
    # Drills Tab
    with tab4:
        st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Practice Drills</h3>", unsafe_allow_html=True)
        
        drill_result = DrillManager.get_recommended_drills(st.session_state.user_id)
        
        if drill_result["success"] and drill_result["recommended"]:
            st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Recommended Drills</h4>", unsafe_allow_html=True)
            
            for idx, drill in enumerate(drill_result["recommended"]):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    with st.expander(f"🎾 {drill['name']} - {drill['drill_type']} ({drill['difficulty']})"):
                        st.markdown(f"**Description:** {drill['description']}")
                        
                        st.markdown("<h5 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Instructions</h5>", unsafe_allow_html=True)
                        for instruction in drill['instructions']:
                            st.write(f"• {instruction}")
                        
                        st.markdown(f"**Target Reps:** {drill['target_reps']}")
                        st.markdown(f"**Benefits:** {drill['benefits']}")
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            reps = st.number_input(f"Reps completed for {drill['id']}", value=drill['target_reps'], key=f"reps_{idx}")
                        with col_b:
                            accuracy = st.slider(f"Accuracy % for {drill['id']}", 0, 100, 75, key=f"accuracy_{idx}")
                        with col_c:
                            if st.button(f"✅ Complete Drill", key=f"complete_drill_{idx}"):
                                log_result = DrillManager.log_drill(
                                    st.session_state.user_id,
                                    drill['id'],
                                    drill['drill_type'],
                                    int(reps),
                                    float(accuracy)
                                )
                                if log_result["success"]:
                                    st.success("🎉 Drill logged!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {log_result['message']}")
        else:
            st.info("No drills recommended yet. Start logging workouts and drills!")
        
        st.markdown("---")
        st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>All Available Drills</h4>", unsafe_allow_html=True)
        
        drill_types = list(DrillManager.get_all_drills().keys())
        selected_type = st.selectbox("Select Drill Type", drill_types)
        
        drills_by_type = DrillManager.get_drills_by_focus(selected_type)
        if drills_by_type["success"]:
            for drill in drills_by_type["drills"]:
                with st.expander(f"🎾 {drill['name']} ({drill['difficulty']})"):
                    st.write(f"**Description:** {drill['description']}")
                    st.write(f"**Target Reps:** {drill['target_reps']}")
                    st.write(f"**Benefits:** {drill['benefits']}")
    
    # Stats Tab
    with tab5:
        st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Performance Statistics</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            period = st.selectbox("Time Period", [7, 30, 90, 365], format_func=lambda x: f"Last {x} Days")
        
        stats_result = ScoreManager.get_statistics(st.session_state.user_id, days=period)
        
        if stats_result["success"]:
            stats = stats_result["stats"]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Matches", stats.get("total_matches", 0))
            with col2:
                st.metric("Win Rate", f"{stats.get('win_percentage', 0):.1f}%")
            with col3:
                st.metric("Wins", stats.get("wins", 0))
            
            st.markdown("---")
            
            # Match type breakdown
            by_type = stats.get("by_match_type", {})
            if by_type:
                st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Match Breakdown by Type</h4>", unsafe_allow_html=True)
                type_stats = []
                for match_type, data in by_type.items():
                    type_stats.append({
                        "Type": match_type,
                        "Matches": data["matches"],
                        "Wins": data["wins"],
                        "Losses": data["losses"]
                    })
                
                df = pd.DataFrame(type_stats)
                st.table(df)
                
                # Visualization
                fig = px.bar(df, x="Type", y=["Wins", "Losses"], 
                            title="Wins vs Losses by Match Type",
                            barmode="group")
                fig.update_layout(height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
    
    # Settings Tab
    with tab6:
        st.markdown("<h3 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Account Settings</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Your Account</h4>", unsafe_allow_html=True)
            user_info = AuthManager.get_user_by_id(st.session_state.user_id)
            if user_info["success"]:
                st.write(f"**Username:** {user_info['username']}")
                st.write(f"**Email:** {user_info['email']}")
                st.write(f"**2FA Status:** {'🔒 Enabled' if user_info['mfa_enabled'] else '🔓 Disabled'}")
        
        with col2:
            st.markdown("<h4 style='font-family: Playfair Display, serif; color: #1e5f3e;'>Security</h4>", unsafe_allow_html=True)

            st.markdown("### Email MFA Diagnostics")
            email_status = AuthManager.get_email_configuration_status()

            if email_status["configured"]:
                st.success("SMTP is configured for MFA emails.")
            else:
                st.warning(
                    "SMTP is not fully configured. Missing: "
                    + ", ".join(email_status["missing_keys"])
                )

            st.caption(
                "Source check: "
                + ", ".join(
                    [f"{key}={source}" for key, source in email_status["sources"].items()]
                )
            )

            if email_status.get("provider_hint"):
                st.info(email_status["provider_hint"])

            if st.button("Send Test Email", use_container_width=True):
                test_result = AuthManager.send_test_email(st.session_state.user_id)
                if test_result["success"]:
                    st.success(test_result["message"])
                else:
                    st.error(test_result["message"])

            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.mfa_enabled = False
                st.session_state.mfa_verified = False
                st.session_state.page = "home"
                st.rerun()


# Main app flow
def main():
    """Main application flow."""
    init_session_state()
    
    # Show header only on home page
    if st.session_state.page == "home" and st.session_state.user_id is None:
        show_header()
    
    # Route to appropriate page
    if st.session_state.user_id is None:
        login_page()
    elif st.session_state.mfa_enabled and not st.session_state.mfa_verified:
        email_verify_page()
    elif st.session_state.page == "workouts_page":
        workouts_page()
    else:
        dashboard_page()


if __name__ == "__main__":
    main()
