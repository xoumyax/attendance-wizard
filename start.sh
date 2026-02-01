#!/bin/bash
set -e

echo "🌱 Running database initialization..."

# Run seed scripts (they check if data exists and skip if already seeded)
python seed_sessions.py
python seed_test_students.py

echo "✅ Database ready!"
echo "🚀 Starting server..."

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
