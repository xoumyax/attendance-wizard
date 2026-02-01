"""
Initialize database tables on startup.
This ensures tables are created before seeding.
"""
from app.database import engine
from app.models import Base

def init_db():
    """Create all database tables."""
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready!")

if __name__ == "__main__":
    init_db()
