"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ============================================================================
# Authentication Schemas
# ============================================================================

class StudentRegisterRequest(BaseModel):
    name: str
    uin: str
    password: str


class StudentLoginRequest(BaseModel):
    uin: str
    password: str


class StudentResetPasswordRequest(BaseModel):
    uin: str
    name: str
    new_password: str


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str  # "student" or "admin"
    user_info: dict


# ============================================================================
# Session Schemas
# ============================================================================

class SessionCreate(BaseModel):
    date: datetime
    is_test_session: bool = False


class SessionResponse(BaseModel):
    id: int
    date: datetime
    is_test_session: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Token Schemas
# ============================================================================

class TokenGenerate(BaseModel):
    session_id: int


class TokenResponse(BaseModel):
    session_id: int
    token: str
    expires_at: datetime
    is_test_session: bool


# ============================================================================
# Attendance Schemas
# ============================================================================

class AttendanceMarkRequest(BaseModel):
    session_id: int
    token: str = Field(..., min_length=6, max_length=6)


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    session_id: int
    marked_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceRecord(BaseModel):
    student_uin: str
    student_name: str
    session_date: datetime
    marked_at: datetime


# ============================================================================
# Statistics Schemas
# ============================================================================

class StudentStats(BaseModel):
    uin: str
    name: str
    total_sessions: int
    attended_sessions: int
    attendance_percentage: float
    grade_points: int


class DashboardStats(BaseModel):
    total_students: int
    total_registered_students: int
    total_sessions: int
    total_attendances: int
    today_session: Optional[SessionResponse]
    recent_attendances: List[AttendanceRecord]


# ============================================================================
# Settings Schemas
# ============================================================================

class SettingsUpdate(BaseModel):
    disable_time_restrictions: bool


class SettingsResponse(BaseModel):
    disable_time_restrictions: bool
    updated_at: datetime
    
    class Config:
        from_attributes = True
