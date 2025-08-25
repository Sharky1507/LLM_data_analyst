#!/usr/bin/env python3
"""
Example usage of the Data Analysis Chatbot Package
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
chatbot_root = Path(__file__).parent
src_path = chatbot_root / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv

async def example_usage():
    """Example of how to use the chatbot programmatically"""
    
    # Load environment variables
    load_dotenv()
    
    # Import chatbot components
    from bot import ChatBot
    from tools import tools_schema, run_sqlite_query, plot_chart
    from utils import generate_sqlite_table_info_query
    
    print("🤖 Data Analysis Chatbot Example")
    print("=" * 50)
    
    # Get database schema for system message
    table_info_query = generate_sqlite_table_info_query([])
    result, column_names = await run_sqlite_query(table_info_query, markdown=False)
    table_info = '\n'.join([item[0] for item in result])
    
    # System message
    system_message = f"""You are a helpful data analysis assistant. 
    You can query the database and create visualizations.
    
    Database schema:
    {table_info}"""
    
    # Tool functions
    tool_functions = {
        "query_db": run_sqlite_query,
        "plot_chart": plot_chart
    }
    
    # Create chatbot instance
    bot = ChatBot(system_message, tools_schema, tool_functions)
    
    # Example queries
    example_queries = [
        "How many movies are in the database?",
        "Show me the top 5 highest rated movies",
        "What are the most common genres?"
    ]
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        try:
            # Send query to bot
            response = await bot(query)
            print(f"Response: {response.content}")
            
            # Handle function calls if any
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"Function calls: {len(response.tool_calls)}")
                
                # Execute function calls
                final_response, tool_responses = await bot.call_functions(response.tool_calls)
                print(f"Final response: {final_response.content}")
                
                # Check for charts
                chart_responses = [res for res in tool_responses if res['name'] == 'plot_chart']
                if chart_responses:
                    print(f"Generated {len(chart_responses)} chart(s)")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Example completed!")

if __name__ == "__main__":
    asyncio.run(example_usage())
