# Attendance Wizard 🧙‍♂️

A robust attendance tracking system with secure authentication, session management, and automated grading.

## Features

### For Students
- 🔐 Secure login with JWT authentication
- ⏰ Mark attendance during 8-9 AM window
- 🎫 Submit 6-digit session tokens
- 📊 View personal attendance records

### For Admins
- 👤 Secure admin authentication (xoumyax / YuZhiyuan)
- 📅 Create and manage 30+ sessions
- 🎲 Generate time-limited tokens (2-min expiry)
- 🧪 Test sessions with 24-hour tokens
- 📈 Export Excel reports with auto-grading
- 🔧 Toggle time restrictions for testing

### Grading System
- ≥85% attendance: 10 points
- ≥75% attendance: 8 points
- ≥50% attendance: 5 points
- <50% attendance: 0 points

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Seed Database**
   ```bash
   python seed_students.py
   ```

4. **Run Server**
   ```bash
   python run.py
   ```

5. **Access Application**
   - Student Portal: http://localhost:8000
   - Admin Portal: http://localhost:8000/admin/login

## Admin Credentials
- Username: `xoumyax` or `YuZhiyuan`
- Password: `admin`

## Student Credentials (Sample)
- Roll Number: `2021001` to `2021010`
- Password: `password123`

## Project Structure
```
attendanceWizard/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication
│   ├── utils.py             # Utilities
│   └── routers/
│       ├── admin.py         # Admin endpoints
│       └── student.py       # Student endpoints
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── student_login.html
│   ├── student_attendance.html
│   ├── admin_login.html
│   └── admin_dashboard.html
├── seed_students.py         # Database seeding
├── run.py                   # Server entry point
├── requirements.txt
└── .env
```

## Testing
- 2 test sessions created for today (Jan 31, 2026)
- Test tokens valid for 24 hours
- Time restrictions can be toggled by admin

## Security Features
- JWT-based authentication
- Bcrypt password hashing
- Token expiration (2 minutes for regular sessions)
- Time window enforcement (8-9 AM)
- Duplicate attendance prevention
- Admin-only routes protection
