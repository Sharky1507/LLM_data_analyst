#!/usr/bin/env python3
"""
Test script for the chatbot package
"""
import os
import sys
from pathlib import Path

# Add src to path
chatbot_root = Path(__file__).parent
src_path = chatbot_root / "src"
sys.path.insert(0, str(src_path))

async def test_chatbot_package():
    """Test the chatbot package functionality"""
    print("🧪 Testing Data Analysis Chatbot Package...")
    print("-" * 50)
    
    # Test imports
    try:
        from bot import ChatBot
        from tools import tools_schema, run_sqlite_query, plot_chart
        from utils import generate_sqlite_table_info_query
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test database connection
    try:
        result, columns = await run_sqlite_query("SELECT COUNT(*) as total_movies FROM movies", markdown=False)
        total_movies = result[0][0] if result else 0
        print(f"✅ Database connection successful - Found {total_movies} movies")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    # Test Groq API (if key is available)
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("⚠️  GROQ_API_KEY not set - skipping API test")
        print("   Please set your API key in .env file")
    else:
        try:
            # Create a simple bot instance
            system_message = "You are a helpful data analysis assistant."
            tool_functions = {
                "query_db": run_sqlite_query,
                "plot_chart": plot_chart
            }
            
            bot = ChatBot(system_message, tools_schema, tool_functions)
            print("✅ ChatBot instance created successfully")
            
            # Test a simple query (without function calling)
            response = await bot("Hello! Can you help me analyze data?")
            if response and hasattr(response, 'content'):
                print("✅ Bot response received")
                print(f"   Sample response: {response.content[:100]}...")
            else:
                print("⚠️  Bot response format unexpected")
                
        except Exception as e:
            print(f"❌ Bot test error: {e}")
            return False
    
    print("-" * 50)
    print("🎉 Package test completed!")
    return True

if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Run test
    asyncio.run(test_chatbot_package())
