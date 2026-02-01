"""
Script to import student data from Canvas CSV files.
Reads CSV files and populates the database with student UINs and names.

Usage:
    python import_students_csv.py <path_to_csv_file>
    
Example:
    python import_students_csv.py "/Users/.../Grades-CSCE_704_600_.csv"
"""
import sys
import csv
from app.database import SessionLocal, engine, Base
from app.models import Student

# Create all tables
Base.metadata.create_all(bind=engine)


def import_students_from_csv(csv_path: str):
    """Import students from Canvas CSV file."""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("📚 IMPORTING STUDENTS FROM CSV")
        print("=" * 60)
        print(f"File: {csv_path}\n")
        
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Skip the "Points Possible" row
                if row.get('Student', '').strip() == 'Points Possible':
                    continue
                
                # Extract data
                name = row.get('Student', '').strip()
                uin = row.get('SIS User ID', '').strip()
                
                # Skip if no name or UIN
                if not name or not uin or name == 'Student, Test':
                    if name:
                        print(f"⏭️  Skipped: {name} (missing UIN or test student)")
                        skipped_count += 1
                    continue
                
                # Check if student already exists
                existing = db.query(Student).filter(
                    Student.uin == uin
                ).first()
                
                if existing:
                    print(f"⏭️  Skipped: {name} (UIN: {uin}) - already exists")
                    skipped_count += 1
                    continue
                
                # Create new student (without password - they'll set it during registration)
                try:
                    student = Student(
                        uin=uin,
                        name=name,
                        hashed_password="",  # Empty until student registers
                        is_registered=False
                    )
                    
                    db.add(student)
                    print(f"✅ Added: {name} (UIN: {uin})")
                    added_count += 1
                    
                except Exception as e:
                    print(f"❌ Error adding {name} (UIN: {uin}): {e}")
                    error_count += 1
        
        # Commit all changes
        db.commit()
        
        print()
        print("=" * 60)
        print("📊 IMPORT SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully added: {added_count} students")
        print(f"⏭️  Skipped: {skipped_count} students")
        print(f"❌ Errors: {error_count} students")
        print(f"📈 Total students in database: {db.query(Student).count()}")
        print("=" * 60)
        print()
        
        if added_count > 0:
            print("🎉 Import completed successfully!")
            print()
            print("📝 Students must now register by:")
            print("   1. Going to http://localhost:8000/register")
            print("   2. Entering their Name and UIN")
            print("   3. Setting a password")
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_students_csv.py <path_to_csv_file>")
        print("\nExample:")
        print("  python import_students_csv.py '/Users/.../Grades-CSCE_704_600_.csv'")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    import_students_from_csv(csv_path)
