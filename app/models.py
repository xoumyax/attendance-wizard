"""
SQLAlchemy database models.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Student(Base):
    """Student user model."""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    uin = Column(String, unique=True, index=True, nullable=False)  # University ID Number
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_registered = Column(Boolean, default=False)  # True after student sets password
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    attendances = relationship("Attendance", back_populates="student")


class Session(Base):
    """Attendance session model."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    is_test_session = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tokens = relationship("SessionToken", back_populates="session", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="session", cascade="all, delete-orphan")


class SessionToken(Base):
    """Session token model for attendance marking."""
    __tablename__ = "session_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    token = Column(String(6), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="tokens")


class Attendance(Base):
    """Attendance record model."""
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    marked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="attendances")
    session = relationship("Session", back_populates="attendances")
    
    # Prevent duplicate attendance
    __table_args__ = (
        UniqueConstraint('student_id', 'session_id', name='unique_student_session'),
    )


class AdminSettings(Base):
    """Admin settings for testing mode."""
    __tablename__ = "admin_settings"
    
    id = Column(Integer, primary_key=True)
    disable_time_restrictions = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
