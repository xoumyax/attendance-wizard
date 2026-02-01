"""
Admin API endpoints for session and token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, date
import os

from .. import models, schemas, auth, utils
from ..database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


def get_current_admin(authorization: Optional[str] = Header(None)) -> str:
    """Dependency to verify admin authentication."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    return auth.verify_admin_token(token)


@router.post("/login", response_model=dict)
def admin_login(req: schemas.AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin login endpoint."""
    if not auth.verify_admin_credentials(req.username, req.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )
    
    # Create JWT token
    access_token = auth.create_access_token(
        data={"sub": req.username, "type": "admin"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "admin",
        "user_info": {"username": req.username}
    }


@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    total_students = db.query(models.Student).count()
    total_registered_students = db.query(models.Student).filter(
        models.Student.is_registered == True
    ).count()
    total_sessions = db.query(models.Session).count()
    total_attendances = db.query(models.Attendance).count()
    
    # Get today's session
    today = date.today()
    today_session = db.query(models.Session).filter(
        func.date(models.Session.date) == today
    ).first()
    
    # Get recent attendances
    recent = db.query(models.Attendance).order_by(
        models.Attendance.marked_at.desc()
    ).limit(10).all()
    
    recent_attendances = []
    for att in recent:
        recent_attendances.append(schemas.AttendanceRecord(
            student_uin=att.student.uin,
            student_name=att.student.name,
            session_date=att.session.date,
            marked_at=att.marked_at
        ))
    
    return schemas.DashboardStats(
        total_students=total_students,
        total_registered_students=total_registered_students,
        total_sessions=total_sessions,
        total_attendances=total_attendances,
        today_session=today_session,
        recent_attendances=recent_attendances
    )

@router.get("/students/grades", response_model=List[schemas.StudentStats])
def get_all_student_grades(
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get grades and statistics for all students."""
    students = db.query(models.Student).order_by(models.Student.name).all()
    
    # Get all regular sessions (exclude test sessions from grading)
    regular_sessions = db.query(models.Session).filter(
        models.Session.is_test_session == False
    ).all()
    total_regular_sessions = len(regular_sessions)
    
    student_stats = []
    for student in students:
        # Count attendances for regular sessions only
        attended_regular = db.query(models.Attendance).join(
            models.Session
        ).filter(
            models.Attendance.student_id == student.id,
            models.Session.is_test_session == False
        ).count()
        
        # Calculate attendance percentage and grade
        if total_regular_sessions > 0:
            attendance_percentage = (attended_regular / total_regular_sessions) * 100
            grade_points = utils.calculate_grade(attendance_percentage)
        else:
            attendance_percentage = 0.0
            grade_points = 0
        
        student_stats.append(schemas.StudentStats(
            uin=student.uin,
            name=student.name,
            total_sessions=total_regular_sessions,
            attended_sessions=attended_regular,
            attendance_percentage=round(attendance_percentage, 2),
            grade_points=grade_points
        ))
    
    return student_stats

@router.post("/sessions/create-test")
def create_test_sessions(
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create 2 test sessions for today."""
    today = date.today()
    
    # Check if test sessions already exist for today
    existing = db.query(models.Session).filter(
        func.date(models.Session.date) == today,
        models.Session.is_test_session == True
    ).count()
    
    if existing >= 2:
        raise HTTPException(
            status_code=400,
            detail="2 test sessions already exist for today"
        )
    
    # Create 2 test sessions
    sessions_created = []
    for i in range(2 - existing):
        session = models.Session(
            date=datetime.combine(today, datetime.min.time()),
            is_test_session=True
        )
        db.add(session)
        db.flush()
        sessions_created.append({
            "id": session.id,
            "date": session.date,
            "is_test_session": True
        })
    
    db.commit()
    
    return {
        "message": f"Created {len(sessions_created)} test sessions for today",
        "sessions": sessions_created
    }


@router.post("/sessions/create-regular")
def create_regular_sessions(
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create 30 regular sessions on preset dates."""
    preset_dates = [
        "2026-02-02", "2026-02-04", "2026-02-06", "2026-02-09", "2026-02-11",
        "2026-02-13", "2026-02-16", "2026-02-18", "2026-02-20", "2026-02-23",
        "2026-02-25", "2026-02-27", "2026-03-02", "2026-03-16", "2026-03-18",
        "2026-03-20", "2026-03-23", "2026-03-25", "2026-03-27", "2026-03-30",
        "2026-04-01", "2026-04-03", "2026-04-06", "2026-04-08", "2026-04-10",
        "2026-04-13", "2026-04-15", "2026-04-17", "2026-04-20", "2026-04-24"
    ]
    
    # Check existing sessions
    existing_dates = {
        s.date.date() for s in db.query(models.Session).filter(
            models.Session.is_test_session == False
        ).all()
    }
    
    sessions_created = []
    for date_str in preset_dates:
        session_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if session_date not in existing_dates:
            session = models.Session(
                date=datetime.combine(session_date, datetime.min.time()),
                is_test_session=False
            )
            db.add(session)
            db.flush()
            sessions_created.append({
                "id": session.id,
                "date": session.date,
                "is_test_session": False
            })
    
    db.commit()
    
    return {
        "message": f"Created {len(sessions_created)} regular sessions",
        "sessions": sessions_created
    }


@router.get("/sessions", response_model=List[schemas.SessionResponse])
def get_all_sessions(
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all sessions."""
    sessions = db.query(models.Session).order_by(models.Session.date.desc()).all()
    return sessions


@router.get("/sessions/today")
def get_today_sessions(
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get today's sessions."""
    today = date.today()
    sessions = db.query(models.Session).filter(
        func.date(models.Session.date) == today
    ).all()
    
    return {"sessions": [schemas.SessionResponse.model_validate(s) for s in sessions]}


@router.post("/tokens/generate")
def generate_token(
    req: schemas.TokenGenerate,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Generate a session token."""
    session = db.query(models.Session).filter(
        models.Session.id == req.session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    token = utils.generate_session_token()
    expires_at = utils.calculate_token_expiry(session.is_test_session)
    
    session_token = models.SessionToken(
        session_id=req.session_id,
        token=token,
        expires_at=expires_at,
        is_active=True
    )
    
    db.add(session_token)
    db.commit()
    
    return {
        "session_id": req.session_id,
        "token": token,
        "expires_at": expires_at,
        "is_test_session": session.is_test_session,
        "expiry_info": f"Valid for {'24 hours' if session.is_test_session else '2 minutes'}"
    }


@router.get("/tokens/active/{session_id}")
def get_active_tokens(
    session_id: int,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get active tokens for a session."""
    tokens = db.query(models.SessionToken).filter(
        models.SessionToken.session_id == session_id,
        models.SessionToken.is_active == True,
        models.SessionToken.expires_at >= datetime.utcnow()
    ).all()
    
    return {
        "session_id": session_id,
        "tokens": [
            {
                "token": t.token,
                "expires_at": t.expires_at,
                "created_at": t.created_at
            } for t in tokens
        ]
    }


@router.get("/tokens/history")
def get_token_history(
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get complete token generation history across all sessions."""
    tokens = db.query(models.SessionToken).join(models.Session).order_by(
        models.SessionToken.created_at.desc()
    ).all()
    
    return {
        "tokens": [
            {
                "id": t.id,
                "session_id": t.session_id,
                "session_date": t.session.date,
                "is_test_session": t.session.is_test_session,
                "token": t.token,
                "created_at": t.created_at,
                "expires_at": t.expires_at,
                "is_active": t.is_active,
                "is_expired": t.expires_at < datetime.utcnow()
            } for t in tokens
        ],
        "total": len(tokens)
    }


@router.get("/tokens/history/{session_id}")
def get_session_token_history(
    session_id: int,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get token generation history for a specific session."""
    session = db.query(models.Session).filter(
        models.Session.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    tokens = db.query(models.SessionToken).filter(
        models.SessionToken.session_id == session_id
    ).order_by(models.SessionToken.created_at.desc()).all()
    
    return {
        "session_id": session_id,
        "session_date": session.date,
        "is_test_session": session.is_test_session,
        "tokens": [
            {
                "id": t.id,
                "token": t.token,
                "created_at": t.created_at,
                "expires_at": t.expires_at,
                "is_active": t.is_active,
                "is_expired": t.expires_at < datetime.utcnow()
            } for t in tokens
        ],
        "total": len(tokens)
    }


@router.get("/attendance/session/{session_id}")
def get_session_attendance(
    session_id: int,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get attendance for a specific session."""
    session = db.query(models.Session).filter(
        models.Session.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    attendances = db.query(models.Attendance).filter(
        models.Attendance.session_id == session_id
    ).all()
    
    return {
        "session": schemas.SessionResponse.model_validate(session),
        "attendances": [
            {
                "roll_number": a.student.uin,
                "name": a.student.name,
                "marked_at": a.marked_at
            } for a in attendances
        ],
        "count": len(attendances)
    }


@router.get("/export/excel")
def export_attendance_excel(
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Export attendance to Excel with grading."""
    students = db.query(models.Student).all()
    
    # Get counts for both test and regular sessions
    total_sessions = db.query(models.Session).count()
    total_regular_sessions = db.query(models.Session).filter(
        models.Session.is_test_session == False
    ).count()
    
    attendance_data = []
    for student in students:
        # All attended sessions
        all_attended = db.query(models.Attendance).filter(
            models.Attendance.student_id == student.id
        ).count()
        
        # Regular sessions attended (for grading)
        regular_attended = db.query(models.Attendance).join(models.Session).filter(
            models.Attendance.student_id == student.id,
            models.Session.is_test_session == False
        ).count()
        
        # Test sessions attended
        test_attended = all_attended - regular_attended
        
        # Calculate percentage based on regular sessions only
        percentage = (regular_attended / total_regular_sessions * 100) if total_regular_sessions > 0 else 0
        grade = utils.calculate_grade(percentage)
        
        attendance_data.append({
            "uin": student.uin,
            "name": student.name,
            "total_sessions": total_sessions,
            "total_regular_sessions": total_regular_sessions,
            "attended_all": all_attended,
            "attended_regular": regular_attended,
            "attended_test": test_attended,
            "attendance_percentage": round(percentage, 2),
            "grade_points": grade
        })
    
    # Generate Excel file with updated columns
    df = pd.DataFrame(attendance_data)
    
    # Reorder columns
    column_order = [
        "uin", "name", "total_sessions", "total_regular_sessions",
        "attended_all", "attended_regular", "attended_test",
        "attendance_percentage", "grade_points"
    ]
    df = df[column_order]
    
    # Rename columns for better readability
    df.columns = [
        "UIN", "Name", "Total Sessions (All)", "Regular Sessions",
        "Attended (All)", "Attended (Regular)", "Attended (Test)",
        "Attendance % (Regular)", "Grade Points"
    ]
    
    # Generate filename
    filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Create Excel writer with styling
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Attendance Report', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Attendance Report']
        
        # Adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    return {
        "message": "Excel report generated successfully",
        "filename": filename,
        "path": os.path.abspath(filename),
        "total_students": len(students),
        "total_sessions": total_sessions,
        "total_regular_sessions": total_regular_sessions,
        "note": "Grading based on regular sessions only. Test sessions not included in grade calculation."
    }


@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    """Get admin settings (public endpoint for students to check time restrictions)."""
    settings = db.query(models.AdminSettings).first()
    if not settings:
        settings = models.AdminSettings(disable_time_restrictions=False)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return schemas.SettingsResponse.model_validate(settings)


@router.put("/settings")
def update_settings(
    req: schemas.SettingsUpdate,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update admin settings."""
    settings = db.query(models.AdminSettings).first()
    if not settings:
        settings = models.AdminSettings()
        db.add(settings)
    
    settings.disable_time_restrictions = req.disable_time_restrictions
    settings.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(settings)
    
    return {
        "message": "Settings updated successfully",
        "settings": schemas.SettingsResponse.model_validate(settings)
    }
