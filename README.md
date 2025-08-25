# Data Analysis Chatbot Package

A powerful conversational AI chatbot for data analysis using Groq's Llama models, built with Chainlit and function calling capabilities.

## Features

- **Database Querying**: Execute SQL queries on SQLite databases
- **Data Visualization**: Generate interactive charts (bar, line, scatter, pie) using Plotly
- **Function Calling**: AI automatically decides when to use tools based on user requests
- **Error Handling**: Robust error handling with retry logic
- **Interactive UI**: Clean web-based chat interface using Chainlit

## Quick Start

### 1. Installation

```bash
# Clone or copy the chatbot_package folder
cd chatbot_package

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your Groq API key
# Get your API key from: https://console.groq.com/keys
echo "GROQ_API_KEY=your_actual_groq_api_key_here" > .env
```

### 3. Run the Chatbot

```bash
# Simple way
python run_chatbot.py

# Or specify a custom port
python run_chatbot.py --port 8080

# Or run directly with chainlit
chainlit run src/app.py --port 8002
```

### 4. Access the Chatbot

Open your browser and go to: `http://localhost:8002`

## Project Structure

```
chatbot_package/
├── src/
│   ├── app.py          # Main Chainlit application
│   ├── bot.py          # ChatBot class with Groq integration
│   ├── tools.py        # Database and plotting tools
│   └── utils.py        # Utility functions
├── data/
│   └── movies.db       # Sample SQLite database
├── config/
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
└── run_chatbot.py     # Main entry point
```

## Usage Examples

### Basic Queries
- "How many movies are in the database?"
- "Show me the top 5 highest rated movies"
- "What are the different genres available?"

### Data Analysis with Charts
- "Create a bar chart showing top 5 directors by number of movies"
- "Plot a pie chart of movie genres distribution"
- "Show a line chart of average movie ratings by year"

### Complex Analysis
- "Compare IMDB scores vs Metacritic scores for top movies"
- "Show the distribution of movie runtime"
- "Analyze movies by decade and genre"

## Integration with Other Projects

### Method 1: Import as Module

```python
import sys
sys.path.append('path/to/chatbot_package/src')

from bot import ChatBot
from tools import tools_schema, run_sqlite_query, plot_chart

# Create bot instance
tool_functions = {
    "query_db": run_sqlite_query,
    "plot_chart": plot_chart
}

bot = ChatBot(system_message, tools_schema, tool_functions)

# Use the bot
response = await bot("Show me top 5 movies")
```

### Method 2: API Integration

You can wrap the chatbot in a FastAPI application:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import sys
sys.path.append('path/to/chatbot_package/src')

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Initialize and use chatbot
    response = await bot(request.message)
    return {"response": response.content}
```

### Method 3: Embed in React/Next.js

Use the iframe method or build a custom API wrapper.

## Database Configuration

### Using Your Own Database

1. Replace `data/movies.db` with your SQLite database
2. Update the database path in `tools.py` if needed
3. The chatbot will automatically introspect your database schema

### Using PostgreSQL

Update the `run_postgres_query` function in `tools.py` with your database credentials:

```python
# Set environment variables
os.environ['DB_NAME'] = 'your_db_name'
os.environ['DB_USER'] = 'your_username'
os.environ['DB_PASSWORD'] = 'your_password'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
```

## Configuration Options

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required)
- `CHATBOT_DB_PATH`: Custom path to SQLite database (optional)

### Model Configuration

You can change the Groq model in `src/bot.py`:

```python
model = "llama3-8b-8192"    # Fast, good for most tasks
# model = "llama3-70b-8192"  # More powerful, slower
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Issues**: Verify your Groq API key is correct
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('GROQ_API_KEY'))"
   ```

3. **Database Not Found**: Check that the database path is correct
   ```bash
   ls -la data/movies.db
   ```

4. **Port Already in Use**: Try a different port
   ```bash
   python run_chatbot.py --port 8080
   ```

## Dependencies

- `chainlit`: Web-based chat interface
- `groq`: Groq API client
- `plotly`: Interactive charts
- `pandas`: Data manipulation
- `python-dotenv`: Environment variable management
- `sqlite3`: Database connectivity (built-in)

