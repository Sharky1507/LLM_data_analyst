import asyncio
import os
import sqlite3
from src.data_analysis_llm_agent.bot import ChatBot
from src.data_analysis_llm_agent.tools import query_database, plot_chart
from src.data_analysis_llm_agent.utils import get_schema

# Set up test environment
os.environ["GEMINI_API_KEY"] = "your_gemini_api_key_here"  # Replace with your actual key

async def test_bot():
    # Database setup
    db_path = "data/sample_data.db"
    
    # Get database schema
    schema = get_schema(db_path)
    
    # Define system prompt
    system_prompt = f"""You are a helpful data analyst. You have access to a database with the following schema:
    
{schema}

You can query the database and create visualizations to help answer questions about the data.
"""

    # Define tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "description": "Execute a SQL query on the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "plot_chart",
                "description": "Create a chart/visualization from data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string", 
                            "description": "CSV formatted data to plot"
                        },
                        "chart_type": {
                            "type": "string",
                            "description": "Type of chart (bar, line, scatter, etc.)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Chart title"
                        }
                    },
                    "required": ["data", "chart_type", "title"]
                }
            }
        }
    ]

    # Tool functions
    tool_functions = {
        "query_database": lambda query: query_database(query, db_path),
        "plot_chart": plot_chart
    }

    # Create bot
    bot = ChatBot(system_prompt, tools, tool_functions)
    
    # Test queries
    test_queries = [
        "How many movies are in the database?",
        "Show me the top 5 highest rated movies",
        "What are the different genres available?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: {query}")
        print("-" * 50)
        
        try:
            response = await bot(query)
            print(f"✅ Response: {response.content}")
            
            # If there are tool calls, execute them
            if response.tool_calls:
                print(f"🔧 Tool calls detected: {len(response.tool_calls)}")
                final_response, tool_responses = await bot.call_functions(response.tool_calls)
                print(f"📊 Final response: {final_response.content}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_bot())