"""
Student API endpoints for authentication and attendance marking.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, date

from .. import models, schemas, auth, utils
from ..database import get_db

router = APIRouter(prefix="/api/student", tags=["student"])


def get_current_student(authorization: Optional[str] = Header(None)) -> int:
    """Dependency to verify student authentication."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    return auth.verify_student_token(token)


@router.post("/register")
def student_register(req: schemas.StudentRegisterRequest, db: Session = Depends(get_db)):
    """Student registration endpoint - verify UIN and set password."""
    # Check if student with this UIN exists in database (imported from CSV)
    student = db.query(models.Student).filter(
        models.Student.uin == req.uin
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=404,
            detail="UIN not found. Please check your UIN or contact your instructor."
        )
    
    # Verify name matches (case-insensitive comparison)
    if student.name.lower().strip() != req.name.lower().strip():
        raise HTTPException(
            status_code=400,
            detail="Name does not match our records. Please enter your name exactly as it appears in Canvas."
        )
    
    # Check if already registered
    if student.is_registered:
        raise HTTPException(
            status_code=400,
            detail="You have already registered. Please use the login page."
        )
    
    # Set password and mark as registered
    student.hashed_password = auth.hash_password(req.password)
    student.is_registered = True
    db.commit()
    
    return {
        "message": "Registration successful! You can now login.",
        "uin": student.uin,
        "name": student.name
    }


@router.post("/login")
def student_login(req: schemas.StudentLoginRequest, db: Session = Depends(get_db)):
    """Student login endpoint."""
    student = db.query(models.Student).filter(
        models.Student.uin == req.uin
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid UIN or password"
        )
    
    if not student.is_registered:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please register first before logging in"
        )
    
    if not auth.verify_password(req.password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid UIN or password"
        )
    
    # Create JWT token
    access_token = auth.create_access_token(
        data={"sub": str(student.id), "type": "student"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "student",
        "user_info": {
            "id": student.id,
            "uin": student.uin,
            "name": student.name
        }
    }


@router.post("/reset-password")
def reset_password(req: schemas.StudentResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset student password - verify UIN and name, then set new password."""
    # Find student by UIN
    student = db.query(models.Student).filter(
        models.Student.uin == req.uin
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=404,
            detail="UIN not found. Please check your UIN or contact your instructor."
        )
    
    # Verify name matches (case-insensitive comparison)
    if student.name.lower().strip() != req.name.lower().strip():
        raise HTTPException(
            status_code=400,
            detail="Name does not match our records. Please enter your name exactly as it appears in Canvas."
        )
    
    # Check if student is registered
    if not student.is_registered:
        raise HTTPException(
            status_code=400,
            detail="Account not yet activated. Please complete registration first."
        )
    
    # Update password
    student.hashed_password = auth.hash_password(req.new_password)
    db.commit()
    
    return {
        "message": "Password reset successful! You can now login with your new password.",
        "uin": student.uin,
        "name": student.name
    }


@router.get("/sessions/today")
def get_today_sessions(
    student_id: int = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get today's sessions for attendance marking."""
    today = date.today()
    sessions = db.query(models.Session).filter(
        func.date(models.Session.date) == today
    ).all()
    
    # Check which sessions student has already marked
    attended_ids = {
        a.session_id for a in db.query(models.Attendance).filter(
            models.Attendance.student_id == student_id,
            models.Attendance.session_id.in_([s.id for s in sessions])
        ).all()
    }
    
    return {
        "sessions": [
            {
                "id": s.id,
                "date": s.date,
                "is_test_session": s.is_test_session,
                "already_marked": s.id in attended_ids
            } for s in sessions
        ]
    }


@router.get("/sessions/available")
def get_available_sessions(
    student_id: int = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get all available sessions (today and future)."""
    today = date.today()
    sessions = db.query(models.Session).filter(
        func.date(models.Session.date) >= today
    ).order_by(models.Session.date).all()
    
    # Check which sessions student has already marked
    attended_ids = {
        a.session_id for a in db.query(models.Attendance).filter(
            models.Attendance.student_id == student_id
        ).all()
    }
    
    return {
        "sessions": [
            {
                "id": s.id,
                "date": s.date,
                "is_test_session": s.is_test_session,
                "already_marked": s.id in attended_ids,
                "is_today": s.date.date() == today
            } for s in sessions
        ]
    }


@router.post("/attendance/mark")
def mark_attendance(
    req: schemas.AttendanceMarkRequest,
    student_id: int = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Mark attendance for a session."""
    # Validate session exists
    session = db.query(models.Session).filter(
        models.Session.id == req.session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if session is for today
    if session.date.date() != date.today():
        raise HTTPException(
            status_code=400,
            detail="You can only mark attendance for today's sessions"
        )
    
    # Get admin settings
    settings = db.query(models.AdminSettings).first()
    time_restrictions_disabled = settings.disable_time_restrictions if settings else False
    
    # Check if within attendance window (skip for test sessions or if admin disabled restrictions)
    if not session.is_test_session and not time_restrictions_disabled:
        if not utils.is_within_attendance_window(False):
            raise HTTPException(
                status_code=403,
                detail=f"Attendance window closed. You can only mark attendance between {utils.settings.ATTENDANCE_START_HOUR}:00 AM - {utils.settings.ATTENDANCE_END_HOUR}:00 AM"
            )
    
    # Validate token
    now = datetime.utcnow()
    token_record = db.query(models.SessionToken).filter(
        models.SessionToken.session_id == req.session_id,
        models.SessionToken.token == req.token,
        models.SessionToken.is_active == True,
        models.SessionToken.expires_at >= now
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=403,
            detail="Invalid or expired session token"
        )
    
    # Check for duplicate attendance
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == student_id,
        models.Attendance.session_id == req.session_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Attendance already marked for this session"
        )
    
    # Create attendance record
    attendance = models.Attendance(
        student_id=student_id,
        session_id=req.session_id
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return {
        "message": "Attendance marked successfully",
        "attendance": schemas.AttendanceResponse.model_validate(attendance)
    }


@router.get("/attendance/my-records")
def get_my_attendance(
    student_id: int = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's attendance records."""
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()
    
    # Get all sessions (including test)
    total_sessions = db.query(models.Session).count()
    total_regular_sessions = db.query(models.Session).filter(
        models.Session.is_test_session == False
    ).count()
    
    # Get all attended sessions
    all_attendances = db.query(models.Attendance).join(models.Session).filter(
        models.Attendance.student_id == student_id
    ).all()
    
    # Get attended regular sessions (for grading)
    regular_attendances = [a for a in all_attendances if not a.session.is_test_session]
    test_attendances = [a for a in all_attendances if a.session.is_test_session]
    
    attended_sessions = len(all_attendances)
    attended_regular_sessions = len(regular_attendances)
    attended_test_sessions = len(test_attendances)
    
    # Calculate percentage based on regular sessions only
    percentage = (attended_regular_sessions / total_regular_sessions * 100) if total_regular_sessions > 0 else 0
    grade = utils.calculate_grade(percentage)
    
    return {
        "student": {
            "uin": student.uin,
            "name": student.name
        },
        "statistics": {
            "total_sessions": total_sessions,
            "total_regular_sessions": total_regular_sessions,
            "attended_sessions": attended_sessions,
            "attended_regular_sessions": attended_regular_sessions,
            "attended_test_sessions": attended_test_sessions,
            "attendance_percentage": round(percentage, 2),
            "grade_points": grade
        },
        "records": [
            {
                "session_id": a.session_id,
                "session_date": a.session.date,
                "marked_at": a.marked_at,
                "is_test_session": a.session.is_test_session
            } for a in all_attendances
        ]
    }
