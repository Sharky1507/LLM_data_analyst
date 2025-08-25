#!/usr/bin/env python3
"""
Script to start both the Django server and Chainlit chatbot server
"""
import subprocess
import time
import sys
import os
from pathlib import Path
import signal
import threading

def start_chatbot_server():
    """Start the Chainlit chatbot server"""
    print("🤖 Starting Chainlit chatbot server...")
    chatbot_root = Path(__file__).parent.parent / "chatbot_package"
    run_script = chatbot_root / "run_chatbot.py"
    
    if not run_script.exists():
        print(f"❌ Chatbot script not found at {run_script}")
        return None
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(run_script)],
            cwd=str(chatbot_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Give it time to start
        
        if process.poll() is None:
            print("✅ Chainlit chatbot server started on http://localhost:8002")
            return process
        else:
            print("❌ Failed to start chatbot server")
            return None
    except Exception as e:
        print(f"❌ Error starting chatbot server: {e}")
        return None

def start_django_server():
    """Start the Django development server"""
    print("🌐 Starting Django server...")
    try:
        process = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Give it time to start
        
        if process.poll() is None:
            print("✅ Django server started on http://127.0.0.1:8000")
            return process
        else:
            print("❌ Failed to start Django server")
            return None
    except Exception as e:
        print(f"❌ Error starting Django server: {e}")
        return None

def setup_database():
    """Run Django migrations"""
    print("🗄️  Setting up database...")
    try:
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("✅ Database setup complete")
        return True
    except subprocess.CalledProcessError:
        print("❌ Database setup failed")
        return False

def main():
    print("🚀 Starting Data Analyst Chatbot Website")
    print("=" * 50)
    
    # Setup database first
    if not setup_database():
        sys.exit(1)
    
    chatbot_process = None
    django_process = None
    
    try:
        # Start chatbot server
        chatbot_process = start_chatbot_server()
        
        # Start Django server
        django_process = start_django_server()
        
        if not django_process:
            sys.exit(1)
        
        print("\n🎉 Both servers are running!")
        print("📊 Main website: http://127.0.0.1:8000")
        print("🤖 Chatbot (direct): http://localhost:8002")
        print("\nPress Ctrl+C to stop both servers")
        
        # Wait for processes
        try:
            django_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
    
    finally:
        # Clean up processes
        if chatbot_process and chatbot_process.poll() is None:
            print("Stopping chatbot server...")
            chatbot_process.terminate()
            try:
                chatbot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                chatbot_process.kill()
        
        if django_process and django_process.poll() is None:
            print("Stopping Django server...")
            django_process.terminate()
            try:
                django_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                django_process.kill()
        
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
