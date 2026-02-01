"""
Seed script to import real students from Canvas CSV files for production deployment.
Automatically imports students from CSCE 704 and CSCE 439 CSV files.

Usage:
    python seed_students.py
"""
import sys
import csv
import os
from app.database import SessionLocal, engine, Base
from app.models import Student
from app.auth import hash_password

# Create all tables
Base.metadata.create_all(bind=engine)

# CSV files in the repository
CSV_FILES = [
    "CSCE_704.csv",
    "CSCE_439.csv"
]


def import_from_csv(db, csv_path: str):
    """Import students from a Canvas CSV file."""
    added = 0
    skipped = 0
    
    if not os.path.exists(csv_path):
        print(f"⚠️  Warning: {csv_path} not found, skipping...")
        return added, skipped
    
    print(f"\n📂 Reading {csv_path}...")
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            # Skip the "Points Possible" row and test students
            if row.get('Student', '').strip() in ['Points Possible', 'Student, Test']:
                continue
            
            name = row.get('Student', '').strip()
            uin = row.get('SIS User ID', '').strip()
            
            # Skip if no name or UIN
            if not name or not uin:
                continue
            
            # Check if student already exists
            existing = db.query(Student).filter(Student.uin == uin).first()
            
            if existing:
                skipped += 1
                continue
            
            # Create new unregistered student
            try:
                student = Student(
                    uin=uin,
                    name=name,
                    hashed_password="",  # Empty until student registers
                    is_registered=False
                )
                db.add(student)
                print(f"  ✅ {name} (UIN: {uin})")
                added += 1
            except Exception as e:
                print(f"  ❌ Error adding {name}: {e}")
    
    return added, skipped


def seed_students():
    """Seed the database with real students from CSV files."""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("🌱 IMPORTING REAL STUDENTS FROM CSV FILES")
        print("=" * 60)
        
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
