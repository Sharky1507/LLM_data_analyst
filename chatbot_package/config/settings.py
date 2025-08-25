"""
Configuration settings for the Data Analysis Chatbot
"""
import os
from pathlib import Path

# Chatbot package root directory
CHATBOT_ROOT = Path(__file__).parent.parent

# Database settings
DATABASE_PATH = CHATBOT_ROOT / "data" / "movies.db"
CUSTOM_DB_PATH = os.environ.get("CHATBOT_DB_PATH")
if CUSTOM_DB_PATH:
    DATABASE_PATH = Path(CUSTOM_DB_PATH)

# Groq API settings
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama3-8b-8192")

# Available models:
# - llama3-8b-8192: Fast, good for most tasks
# - llama3-70b-8192: More powerful, slower
# - mixtral-8x7b-32768: Good balance of speed and capability

# Chainlit settings
DEFAULT_PORT = int(os.environ.get("CHAINLIT_PORT", "8002"))
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "5"))

# Chart settings
DEFAULT_CHART_COLORS = {
    'bar': '#24C8BF',
    'line': '#ff9900', 
    'scatter': '#df84ff',
    'pie': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
}

# Logging settings
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = CHATBOT_ROOT / "chatbot.log"

# System message template
SYSTEM_MESSAGE_TEMPLATE = """You are a data analysis expert. Help users analyze data from the database by writing SQL queries and creating visualizations.

CRITICAL WORKFLOW:
1. ALWAYS call query_db FIRST to get actual data from the database
2. ONLY call plot_chart AFTER you have real data from query_db
3. Extract actual values from the query results to use in plot_chart

RULES:
- NEVER use placeholder or example data in plot_chart
- ALWAYS use real data from query_db results
- For charts: extract x_values (categories) and y_values (numbers) from query results
- Keep responses business-friendly (no technical SQL details)
- Limit results to 5-10 items for clarity
- Choose appropriate chart types: bar (comparisons), pie (distributions), line (trends)

Database schema:
{table_info}"""
