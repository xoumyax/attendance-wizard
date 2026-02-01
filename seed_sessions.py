"""
Seed the database with test sessions and admin settings.
"""
import sys
import os
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Base, Session as SessionModel, AdminSettings

def seed_sessions():
    """Create initial test sessions and admin settings."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if sessions exist
        existing_count = db.query(SessionModel).count()
        if existing_count > 0:
            print(f"⏭️  Database already has {existing_count} sessions. Skipping seed.")
            return
        
        print("🌱 Seeding database with sessions...")
        
        # Create 2 test sessions for today
        today = date.today()
        test_session1 = SessionModel(
            date=datetime.combine(today, datetime.min.time()),
            is_test_session=True
        )
        test_session2 = SessionModel(
            date=datetime.combine(today, datetime.min.time()),
            is_test_session=True
        )
        db.add(test_session1)
        db.add(test_session2)
        print(f"✅ Created 2 test sessions for {today}")
        
        # Create 30 regular sessions (Feb-Apr 2026)
        regular_dates = [
            "2026-02-02", "2026-02-04", "2026-02-06", "2026-02-09", "2026-02-11",
            "2026-02-13", "2026-02-16", "2026-02-18", "2026-02-20", "2026-02-23",
            "2026-02-25", "2026-02-27", "2026-03-02", "2026-03-04", "2026-03-06",
            "2026-03-09", "2026-03-11", "2026-03-13", "2026-03-23", "2026-03-25",
            "2026-03-27", "2026-03-30", "2026-04-01", "2026-04-03", "2026-04-06",
            "2026-04-08", "2026-04-10", "2026-04-13", "2026-04-15", "2026-04-17"
        ]
        
        for date_str in regular_dates:
            session_date = datetime.strptime(date_str, "%Y-%m-%d")
            session = SessionModel(
                date=session_date,
                is_test_session=False
            )
            db.add(session)
        
        print(f"✅ Created 30 regular sessions (Feb-Apr 2026)")
        
        # Create admin settings if not exists
        settings = db.query(AdminSettings).first()
        if not settings:
            settings = AdminSettings(disable_time_restrictions=False)
            db.add(settings)
            print("✅ Created admin settings")
        
        db.commit()
        print("\n🎉 Database seeded successfully!")
        print(f"📊 Total sessions: {db.query(SessionModel).count()}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_sessions()
