"""
Main FastAPI application.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import admin, student

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Attendance Wizard",
    description="Robust attendance tracking system with secure authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(admin.router)
app.include_router(student.router)


# ============================================================================
# Frontend Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def student_login_page(request: Request):
    """Student login page."""
    return templates.TemplateResponse("student_login.html", {"request": request})


@app.get("/student/register", response_class=HTMLResponse)
async def student_register_page(request: Request):
    """Student registration page."""
    return templates.TemplateResponse("student_register.html", {"request": request})


@app.get("/student/reset-password", response_class=HTMLResponse)
async def student_reset_password_page(request: Request):
    """Student password reset page."""
    return templates.TemplateResponse("student_reset_password.html", {"request": request})


@app.get("/attendance", response_class=HTMLResponse)
async def student_attendance_page(request: Request):
    """Student attendance marking page."""
    return templates.TemplateResponse("student_attendance.html", {"request": request})


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page."""
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    """Admin dashboard page."""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": "Attendance Wizard"}
