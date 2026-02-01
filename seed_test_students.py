"""
Seed the database with 2 test students that are already registered.
These students can be used for testing without going through registration.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Base, Student
from app.auth import hash_password

def seed_test_students():
    """Create 2 test students that are already registered."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("🌱 Seeding test students...")
        
        # Test Student 1
        test1_uin = "999999991"
        existing1 = db.query(Student).filter(Student.uin == test1_uin).first()
        
        if existing1:
            print(f"⏭️  Test student 1 already exists (UIN: {test1_uin})")
        else:
            student1 = Student(
                uin=test1_uin,
                name="Test, Student One",
                hashed_password=hash_password("test123"),
                is_registered=True
            )
            db.add(student1)
            print(f"✅ Created test student 1:")
            print(f"   Name: Test, Student One")
            print(f"   UIN: {test1_uin}")
            print(f"   Password: test123")
        
        # Test Student 2
        test2_uin = "999999992"
        existing2 = db.query(Student).filter(Student.uin == test2_uin).first()
        
        if existing2:
            print(f"⏭️  Test student 2 already exists (UIN: {test2_uin})")
        else:
            student2 = Student(
                uin=test2_uin,
                name="Test, Student Two",
                hashed_password=hash_password("test123"),
                is_registered=True
            )
            db.add(student2)
            print(f"✅ Created test student 2:")
            print(f"   Name: Test, Student Two")
            print(f"   UIN: {test2_uin}")
            print(f"   Password: test123")
        
        # Test Student 3 (Unregistered - for testing full registration flow)
        test3_uin = "999999993"
        existing3 = db.query(Student).filter(Student.uin == test3_uin).first()
        
        if existing3:
            print(f"⏭️  Test student 3 already exists (UIN: {test3_uin})")
        else:
            student3 = Student(
                uin=test3_uin,
                name="puffyboo",
                hashed_password="",  # Empty password - not registered yet
                is_registered=False
            )
            db.add(student3)
            print(f"✅ Created test student 3 (UNREGISTERED):")
            print(f"   Name: puffyboo")
            print(f"   UIN: {test3_uin}")
            print(f"   Status: Not registered - must complete registration first")
        
        db.commit()
        print("\n🎉 Test students ready!")
        print("\n📝 Pre-registered students (can login directly):")
        print("   UIN: 999999991 | Password: test123")
        print("   UIN: 999999992 | Password: test123")
        print("\n📝 Unregistered student (must register first):")
        print("   Name: puffyboo | UIN: 999999993")
        print("   → Go to /student/register to complete registration")
        
    except Exception as e:
        print(f"❌ Error seeding test students: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_students()
