#!/usr/bin/env python3
"""
Setup script for the Data Analysis Chatbot Package
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_environment():
    """Set up environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        try:
            # Copy .env.example to .env
            with open(env_example) as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env and add your GROQ_API_KEY")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ .env.example not found")
        return False

def test_database():
    """Test if the database exists"""
    db_path = Path("data/movies.db")
    if db_path.exists():
        print("✅ Database file found")
        return True
    else:
        print("❌ Database file not found at data/movies.db")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Data Analysis Chatbot Package...")
    print("-" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install requirements
    if success and not install_requirements():
        success = False
    
    # Setup environment
    if success and not setup_environment():
        success = False
    
    # Test database
    if success and not test_database():
        success = False
    
    print("-" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file and add your GROQ_API_KEY")
        print("2. Get your API key from: https://console.groq.com/keys")
        print("3. Run the chatbot: python run_chatbot.py")
    else:
        print("❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
