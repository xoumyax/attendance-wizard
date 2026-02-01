"""
Seed script to populate the database with sample student data.
Run this after setting up the environment to add test students.

Usage:
    python seed_students.py
"""
import sys
from app.database import SessionLocal, engine, Base
from app.models import Student
from app.auth import hash_password

# Create all tables
Base.metadata.create_all(bind=engine)

# Sample student data - modify as needed
SAMPLE_STUDENTS = [
    {"roll_number": "2021001", "name": "Alice Johnson", "password": "password123"},
    {"roll_number": "2021002", "name": "Bob Smith", "password": "password123"},
    {"roll_number": "2021003", "name": "Charlie Brown", "password": "password123"},
    {"roll_number": "2021004", "name": "Diana Prince", "password": "password123"},
    {"roll_number": "2021005", "name": "Ethan Hunt", "password": "password123"},
    {"roll_number": "2021006", "name": "Fiona Apple", "password": "password123"},
    {"roll_number": "2021007", "name": "George Wilson", "password": "password123"},
    {"roll_number": "2021008", "name": "Hannah Montana", "password": "password123"},
    {"roll_number": "2021009", "name": "Isaac Newton", "password": "password123"},
    {"roll_number": "2021010", "name": "Julia Roberts", "password": "password123"},
]


def seed_students():
    """Seed the database with sample students."""
    db = SessionLocal()
    
    try:
        # Check existing students
        existing_count = db.query(Student).count()
        
        print("=" * 60)
        print("🌱 ATTENDANCE WIZARD - DATABASE SEEDING")
        print("=" * 60)
        print()
        
        if existing_count > 0:
            print(f"⚠️  Warning: Database already contains {existing_count} students.")
            response = input("Do you want to add more students? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("❌ Seeding cancelled.")
                return
            print()
        
        added_count = 0
        skipped_count = 0
        
        print("📝 Adding students to database...")
        print("-" * 60)
        
        for student_data in SAMPLE_STUDENTS:
            # Check if student already exists
            existing = db.query(Student).filter(
                Student.roll_number == student_data["roll_number"]
            ).first()
            
            if existing:
                print(f"⏭️  Skipped: {student_data['roll_number']} - {student_data['name']} (already exists)")
                skipped_count += 1
                continue
            
            # Create new student
            student = Student(
                roll_number=student_data["roll_number"],
                name=student_data["name"],
                hashed_password=hash_password(student_data["password"])
            )
            
            db.add(student)
            print(f"✅ Added: {student_data['roll_number']} - {student_data['name']}")
            added_count += 1
        
        # Commit all changes
        db.commit()
        
        print()
        print("=" * 60)
        print("📊 SEEDING SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully added: {added_count} students")
        print(f"⏭️  Skipped existing: {skipped_count} students")
        print(f"📈 Total students in database: {db.query(Student).count()}")
        print("=" * 60)
        print()
        
        if added_count > 0:
            print("🎉 Seeding completed successfully!")
            print()
            print("📝 Sample Login Credentials:")
            print(f"   Roll Number: {SAMPLE_STUDENTS[0]['roll_number']}")
            print(f"   Password: {SAMPLE_STUDENTS[0]['password']}")
            print()
            print("🔐 Admin Login Credentials:")
            print("   Username: xoumyax or YuZhiyuan")
            print("   Password: admin")
            print()
            print("🚀 You can now start the server with: python run.py")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed_students()
    except KeyboardInterrupt:
        print("\n\n❌ Seeding interrupted by user.")
        sys.exit(1)
