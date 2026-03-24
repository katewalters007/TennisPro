# � TennisPro - Complete Tennis Training App

A comprehensive Streamlit-based tennis training application with user authentication, MFA, score tracking, personalized workouts, and tennis-focused drills.

## Features

### 🔐 Security
- **User Authentication**: Secure registration and login with bcrypt password hashing
- **Multi-Factor Authentication (MFA)**: Two-factor authentication using TOTP (Time-based One-Time Password)
- **QR Code Setup**: Easy 2FA setup with authenticator apps

### 📊 Score Tracking
- Log match results (Singles, Doubles, Practice)
- Track detailed statistics (points won/lost, sets won/lost)
- View match history and head-to-head records
- Analyze performance by match type

### 💪 Personalized Workouts
- **5 Body Part Focus Areas**:
  - Legs (explosiveness, agility, footwork)
  - Shoulders (serve power, stability)
  - Core (rotation power, stability)
  - Arms (grip strength, arm speed)
  - Endurance (cardiovascular fitness)

- **Tennis-specific exercises** for each body part and difficulty level
- Difficulty progression (Beginner → Intermediate → Advanced)
- Workout logging and history tracking

### 🎾 Drill Recommendations
- **6 Drill Categories**:
  - Forehand (consistency, down-the-line, loops)
  - Backhand (consistency, down-the-line, slice)
  - Serve (flat, slice, kick serves)
  - Volley (forehand, backhand, overhead)
  - Return of Serve (fundamentals, aggressive, pressure)
  - Movement (footwork, court coverage, point simulation)

- Smart recommendation engine based on:
  - Player level and focus areas
  - Drill accuracy scores
  - Completion history
- Accuracy tracking for each drill

### 📈 Analytics & Statistics
- Win/loss statistics over customizable periods
- Match type breakdown
- Average performance metrics
- Visualization with Plotly charts

## Installation

1. **Clone the repository**
   ```bash
   cd /workspaces/TennisPro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose a database**

  Local development uses SQLite automatically.

  For Streamlit Cloud or any persistent deployment, set a hosted PostgreSQL connection string:
  ```bash
  export DATABASE_URL="postgresql://postgres:your_password@db.your-project.supabase.co:5432/postgres?sslmode=require"
  ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
TennisPro/
├── backend/
│   ├── __init__.py
│   ├── auth.py              # Authentication & MFA management
│   ├── database.py          # Database models and setup
│   ├── workouts.py          # Workout recommendations & tracking
│   ├── drills.py            # Drill recommendations & tracking
│   └── scores.py            # Score tracking & statistics
├── streamlit_app.py         # Main Streamlit frontend
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── tennis_pro.db           # Local SQLite fallback database (auto-created)
```

## Database Schema

### Users
- User authentication with hashed passwords
- MFA settings and secret keys
- Account metadata

### Scores
- Match type (Singles, Doubles, Practice)
- Opponent name and results
- Point and set statistics
- Match notes

### Workouts
- User body focus areas (1-5 priority scale)
- Workout completion logs
- Duration and difficulty tracking

### Drills
- Drill completion logs
- Drill type and name
- Reps completed and accuracy scores
- Completion dates

## Usage

### Getting Started
1. Create a new account with username and password
2. Set up two-factor authentication (recommended)
3. Select your body focus areas (Legs, Shoulders, Core, Arms, Endurance)
4. View personalized workout and drill recommendations

### Logging Matches
1. Go to "Scores" tab
2. Enter opponent name, match type, and results
3. Add optional match notes
4. View complete match history

### Training
1. **Workouts**: Complete recommended workouts based on your focus areas
2. **Drills**: Practice tennis-specific drills with difficulty progression
3. **Track**: Log completed workouts and drills with metrics

### Analytics
1. View statistics for custom time periods
2. Track win rates and match breakdowns
3. Monitor training progress

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python
- **Database**: SQLAlchemy ORM with SQLite for local development and PostgreSQL for persistent deployments
- **Authentication**: bcrypt, PyOTP, QRCode
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy

## Security Features

- **Password Hashing**: bcrypt with salt
- **2FA**: Time-based One-Time Passwords (TOTP)
- **Secure Session Management**: Streamlit session state
- **Data Isolation**: User-specific data queries
- **Verification Code Protection**: Verification codes are hashed at rest
- **Rate Limiting**: Login, code verification, and resend endpoints are throttled
- **Input Validation**: Username, email, password, and score inputs are validated and normalized
- **Transport Security for Email**: SMTP verification emails use TLS when configured
- **Optional Secret Encryption at Rest**: MFA secret values can be encrypted using `APP_ENCRYPTION_KEY`

### Security Environment Variables

Set these for production deployments:

- `DATABASE_URL` for a persistent PostgreSQL database
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`
- `VERIFICATION_CODE_PEPPER` for verification code hashing hardening
- `APP_ENCRYPTION_KEY` for optional at-rest encryption of MFA secrets

## Streamlit Cloud Database Setup

For Streamlit Community Cloud, use a hosted PostgreSQL database instead of SQLite so accounts and training data survive restarts.

1. Create a Supabase project.
2. Open `Project Settings -> Database` and copy the PostgreSQL connection string.
3. Replace `[YOUR-PASSWORD]` with your database password.
4. Ensure the URL includes `?sslmode=require`.
5. In Streamlit Cloud, open `App settings -> Secrets` and add:

  ```toml
  DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.your-project.supabase.co:5432/postgres?sslmode=require"
  SMTP_HOST = "smtp.gmail.com"
  SMTP_PORT = "587"
  SMTP_USERNAME = "your_email@gmail.com"
  SMTP_PASSWORD = "your_app_password"
  SMTP_FROM_EMAIL = "your_email@gmail.com"
  SMTP_USE_TLS = "true"
  APP_ENCRYPTION_KEY = "replace_with_fernet_key"
  VERIFICATION_CODE_PEPPER = "replace_with_long_random_secret"
  ```

6. Save the secrets and reboot the app.

The app creates its tables automatically in PostgreSQL on first startup.

## Customization

### Adding New Workouts
Edit `backend/workouts.py` - Add exercises to the `WORKOUTS` dictionary

### Adding New Drills
Edit `backend/drills.py` - Add drills to the `DRILLS` dictionary

### Adding New Body Focus Areas
1. Update `WORKOUTS` dictionary in `workouts.py`
2. Update `body_parts` in `streamlit_app.py` setup_body_focus()

## Future Enhancements

- Real-time match tracking during play
- Video analysis of strokes
- Integration with wearables for fitness data
- Social features (leaderboards, player matching)
- Advanced analytics (serve velocity, court positioning)
- Mobile app version
- Integration with tennis coaching platforms

## License

See LICENSE file for details

## Support

For issues or questions, please create an issue in the repository.
