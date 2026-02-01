"""
Configuration management using environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    
    # Admin Credentials
    ADMIN_USER_1: str = "xoumyax"
    ADMIN_USER_2: str = "YuZhiyuan"
    ADMIN_PASSWORD: str = "adminwizards@csce439704"
    
    # Database
    DATABASE_URL: str = "sqlite:///./attendance.db"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Attendance Settings
    ATTENDANCE_START_HOUR: int = 8
    ATTENDANCE_END_HOUR: int = 9
    SESSION_TOKEN_EXPIRY_MINUTES: int = 5  # Regular sessions: 5 minutes
    TEST_SESSION_TOKEN_EXPIRY_HOURS: int = 24  # Test sessions: 24 hours
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
