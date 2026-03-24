# Quick Start Guide for TennisPro

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run streamlit_app.py
```

The app will automatically:
- Create a local SQLite database (`tennis_pro.db`) when `DATABASE_URL` is not set
- Initialize all tables
- Open in your default browser at `http://localhost:8501`

### 3. Optional: Use a Persistent Hosted Database

For Streamlit Cloud or any deployment where data must survive restarts, set a hosted PostgreSQL connection string before starting the app:

```bash
export DATABASE_URL="postgresql://postgres:your_password@db.your-project.supabase.co:5432/postgres?sslmode=require"
streamlit run streamlit_app.py
```

## First Time Setup

### Step 1: Create an Account
1. Click "Create Account" tab
2. Enter username, email, and password
3. Click "Create Account"

### Step 2: Login
1. Use your username and password to login
2. You'll be prompted to set up 2FA or proceed to dashboard

### Step 3: Setup 2FA (Optional but Recommended)
1. Click "Enable 2FA"
2. Scan QR code with authenticator app (Google Authenticator, Authy, Microsoft Authenticator, etc.)
3. Enter 6-digit code to verify
4. Your account is now secured with 2FA

### Step 4: Configure Your Training Profile
1. Select body parts you want to improve (Legs, Shoulders, Core, Arms, Endurance)
2. Set focus level (1-5) for each area
3. Click "Save Body Focus Areas"

## Using TennisPro

### Dashboard Tab
- View quick stats (matches, wins, training areas)
- See recent matches and recommended workouts
- Monitor your training progress

### Scores Tab
- Log match results (Singles, Doubles, Practice)
- Track opponent names and scores
- Add match notes
- View full match history

### Workouts Tab
- Get personalized workout recommendations based on your focus areas
- View detailed exercise instructions
- Log completed workouts with duration
- Track workout history

### Drills Tab
- Get recommended drills based on your skill level and weak areas
- Browse all available drill types (Forehand, Backhand, Serve, Volley, Return, Movement)
- Practice drills with reps and accuracy tracking
- View drill instructions and benefits

### Stats Tab
- View detailed statistics over custom time periods
- See match type breakdown
- Track win rates and trends
- Visualize performance with charts

### Settings Tab
- View account information
- Check 2FA status
- Logout safely

## Example Training Flow

1. **Log a Match**
   - Go to Scores tab
   - Enter match details (opponent, score, sets)
   - Add notes about your performance

2. **Get Workout Recommendations**
   - Check Workouts tab
   - See exercises tailored to your body focus areas
   - Complete a workout and log it

3. **Practice Drills**
   - Browse recommended drills
   - Practice the drills on court or with ball machine
   - Log reps and accuracy score

4. **Track Progress**
   - Check Stats tab to see your improvement
   - Adjust difficulty levels as you improve
   - View achievements and milestones

## Database Files

- **tennis_pro.db**: Local SQLite fallback database when `DATABASE_URL` is not set
- Located in project root directory
- Auto-created on first run for local development
- For Streamlit Cloud, use hosted PostgreSQL instead of relying on this file

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Database locked error
- Close all other instances of the app
- Delete tennis_pro.db and restart (loses all data)

### Streamlit Cloud loses data after restart
- Set `DATABASE_URL` to a hosted PostgreSQL database in Streamlit secrets
- SQLite files on Streamlit Cloud are not persistent

### Streamlit not responding
- Press Ctrl+C to stop the server
- Run: `streamlit run streamlit_app.py` again

### 2FA not working
- Ensure your device time is synchronized
- Try the previous/next code if current one fails
- Check that authenticator app is properly configured

## Tips for Success

1. **Regular Logging**: Log matches immediately after playing
2. **Consistent Training**: Complete workouts and drills regularly for best results
3. **Progressive Difficulty**: Advance difficulty levels as you master fundamentals
4. **Detailed Notes**: Add notes to matches for personal analysis
5. **Varied Drills**: Practice different drill types to develop all strokes
6. **Track Accuracy**: Log accuracy scores to monitor your progress

## File Structure

```
TennisPro/
├── streamlit_app.py           # Main application
├── requirements.txt           # Dependencies
├── tennis_pro.db             # Local SQLite fallback database
├── README.md                 # Full documentation
├── QUICKSTART.md             # This file
└── backend/
    ├── auth.py               # Authentication & MFA
    ├── database.py           # Database models
    ├── workouts.py           # Workout system
    ├── drills.py             # Drill system
    ├── scores.py             # Score tracking
    ├── config.py             # Configuration
    ├── utils.py              # Utility functions
    └── __init__.py           # Package init
```

## Getting Help

- Check README.md for detailed feature documentation
- Review code comments in backend modules
- Check browser console (F12) for JavaScript errors
- Ensure all dependencies are installed correctly

## Next Steps

1. Start logging your tennis matches
2. Complete personalized workouts
3. Practice recommended drills
4. Review your statistics and progress
5. Invite friends to use TennisPro
