#!/usr/bin/env python3
"""
Main entry point for the Data Analysis Chatbot
"""
import os
import sys
from pathlib import Path

# Add src directory to Python path
chatbot_root = Path(__file__).parent
src_path = chatbot_root / "src"
sys.path.insert(0, str(src_path))

# Set default database path
default_db_path = chatbot_root / "data" / "movies.db"
os.environ.setdefault("CHATBOT_DB_PATH", str(default_db_path))

def run_chatbot(port=8002):
    """Run the chatbot using Chainlit"""
    import subprocess
    app_path = src_path / "app.py"
    
    try:
        subprocess.run([
            "chainlit", "run", str(app_path), "--port", str(port)
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running chatbot: {e}")
        print("Make sure chainlit is installed: pip install -r requirements.txt")
    except FileNotFoundError:
        print("Chainlit not found. Please install requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the Data Analysis Chatbot")
    parser.add_argument("--port", type=int, default=8002, help="Port to run the chatbot on")
    args = parser.parse_args()
    
    run_chatbot(args.port)
