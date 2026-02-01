"""
Utility functions for token generation, grading, and Excel export.
"""
import random
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict
from .config import settings


def generate_session_token() -> str:
    """Generate a random 6-digit token."""
    return f"{random.randint(0, 999999):06d}"


def calculate_token_expiry(is_test_session: bool = False) -> datetime:
    """
    Calculate token expiry time.
    
    Args:
        is_test_session: Whether this is a test session
        
    Returns:
        Expiry datetime
    """
    if is_test_session:
        return datetime.utcnow() + timedelta(hours=settings.TEST_SESSION_TOKEN_EXPIRY_HOURS)
    else:
        return datetime.utcnow() + timedelta(minutes=settings.SESSION_TOKEN_EXPIRY_MINUTES)


def calculate_grade(attendance_percentage: float) -> int:
    """
    Calculate grade points based on attendance percentage.
    
    Args:
        attendance_percentage: Percentage of attended sessions (0-100)
        
    Returns:
        Grade points (0, 5, 8, or 10)
    """
    if attendance_percentage >= 85:
        return 10
    elif attendance_percentage >= 75:
        return 8
    elif attendance_percentage >= 50:
        return 5
    else:
        return 0


def is_within_attendance_window(disable_time_restrictions: bool = False) -> bool:
    """
    Check if current time is within attendance window (8-9 AM).
    
    Args:
        disable_time_restrictions: If True, always return True (for testing)
        
    Returns:
        True if within window or restrictions disabled, False otherwise
    """
    if disable_time_restrictions:
        return True
    
    current_hour = datetime.now().hour
    return settings.ATTENDANCE_START_HOUR <= current_hour < settings.ATTENDANCE_END_HOUR


def export_to_excel(attendance_data: List[Dict], filename: str = "attendance_report.xlsx"):
    """
    Export attendance data to Excel with grading.
    
    Args:
        attendance_data: List of dicts with student attendance info
        filename: Output filename
        
    Returns:
        Path to the generated Excel file
    """
    df = pd.DataFrame(attendance_data)
    
    # Reorder columns
    column_order = [
        "roll_number", "name", "total_sessions", "attended_sessions",
        "attendance_percentage", "grade_points"
    ]
    df = df[column_order]
    
    # Rename columns for better readability
    df.columns = [
        "Roll Number", "Name", "Total Sessions", "Attended Sessions",
        "Attendance %", "Grade Points"
    ]
    
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
    
    return filename
