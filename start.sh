#!/bin/bash
set -e

echo "🌱 Running database initialization..."

# Create database tables
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine); print('✅ Database tables created')"

# Run seed scripts (they check if data exists and skip if already seeded)
echo "📊 Seeding sessions..."
python seed_sessions.py

echo "👥 Seeding real students from CSV..."
python seed_students.py

echo "👥 Seeding test students..."
python seed_test_students.py

echo "✅ Database ready!"
echo "🚀 Starting server..."

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
