"""
Server entry point.
"""
import os
import sys
import uvicorn
from pathlib import Path

# Change to the directory containing this script
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Add the directory to Python path
sys.path.insert(0, str(script_dir))

from app.config import settings

if __name__ == "__main__":
    print(f"Starting server from: {os.getcwd()}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
