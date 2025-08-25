import chainlit as cl
from dotenv import load_dotenv
import logging
import os
from pathlib import Path

# Load environment variables from .env file in the chatbot package root
# Get the chatbot package root directory (1 level up from this file)
chatbot_root = Path(__file__).parent.parent
env_path = chatbot_root / ".env"

if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    # Try loading from current working directory
    load_dotenv()
    print("⚠️ Using fallback .env loading from current directory")

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "5"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = chatbot_root / "chatbot.log"

# Verify API key is loaded
if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not found in environment variables")
    print("Make sure .env file exists in the project root with GROQ_API_KEY=your_key")
    raise ValueError("GROQ_API_KEY environment variable is required")
else:
    print(f"✅ GROQ_API_KEY loaded successfully (key: {GROQ_API_KEY[:10]}...)")

from plotly.graph_objs import Figure

from utils import generate_sqlite_table_info_query, format_table_info
from tools import tools_schema, run_sqlite_query, plot_chart
from bot import ChatBot

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), 
                   format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.addHandler(logging.FileHandler(LOG_FILE))

schema_table_pairs = []

tool_run_sqlite_query = cl.step(type="tool", show_input="json", language="str")(run_sqlite_query)
tool_plot_chart = cl.step(type="tool", show_input="json", language="json")(plot_chart)
original_run_sqlite_query = tool_run_sqlite_query.__wrapped__
# cl.instrument_openai() 
# for automatic steps

@cl.on_chat_start
async def on_chat_start():
    # build schema query
    table_info_query = generate_sqlite_table_info_query(schema_table_pairs)

    # execute query
    result, column_names = await original_run_sqlite_query(table_info_query, markdown=False)

    # format result into string to be used in prompt
    # table_info = format_table_info(result, column_names)
    table_info = '\n'.join([item[0] for item in result])

    system_message = f"""You are a data analysis expert. Help users analyze data from the database by writing SQL queries and creating visualizations.

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

    # print(system_message)
    
    tool_functions = {
        "query_db": tool_run_sqlite_query,
	    "plot_chart": tool_plot_chart
    }

    cl.user_session.set("bot", ChatBot(system_message, tools_schema, tool_functions))


@cl.on_message
async def on_message(message: cl.Message):
    bot = cl.user_session.get("bot")

    msg = cl.Message(author="Assistant", content="")
    await msg.send()

    # step 1: user request and first response from the bot
    try:
        response_message = await bot(message.content)
        msg.content = response_message.content or ""
        
        # pending message to be sent
        if len(msg.content)>0:
            await msg.update()
    except Exception as e:
        print(f"❌ Error in initial bot response: {e}")
        msg.content = f"I encountered an error: {str(e)}"
        await msg.update()
        return


    # step 2: check tool_calls - as long as there are tool calls and it doesn't cross MAX_ITER count, call iteratively
    cur_iter = 0
    tool_calls = response_message.tool_calls
    print(f"🐛 DEBUG: Initial tool_calls: {tool_calls}")
    while cur_iter <= MAX_ITERATIONS:

        # if tool_calls:
        if tool_calls:
            print(f"🐛 DEBUG: Processing {len(tool_calls)} tool calls")
            bot.messages.append(response_message) # add tool call to messages before calling executing function calls
            try:
                response_message, function_responses = await bot.call_functions(tool_calls)
            except Exception as e:
                print(f"❌ Error in function calls: {e}")
                await cl.Message(author="Assistant", content=f"Error executing tools: {str(e)}").send()
                break

            # response_message is response after completing function calls and sending it back to the bot
            if response_message.content and len(response_message.content)>0:
                await cl.Message(author="Assistant", content=response_message.content).send()

            # reassign tool_calls from new response
            tool_calls = response_message.tool_calls

            # some responses like charts should be displayed explicitly
            function_responses_to_display = [res for res in function_responses if res['name'] in bot.exclude_functions]
            print(f"🐛 DEBUG: function_responses_to_display: {function_responses_to_display}")
            for function_res in function_responses_to_display:
                print(f"🐛 DEBUG: Processing function response: {function_res['name']}")
                print(f"🐛 DEBUG: Content type: {type(function_res['content'])}")
                print(f"🐛 DEBUG: Is Figure? {isinstance(function_res['content'], Figure)}")
                # plot chart
                if isinstance(function_res["content"], Figure):
                    chart = cl.Plotly(name="chart", figure=function_res['content'], display="inline")
                    await cl.Message(author="Assistant", content="", elements=[chart]).send()
                else:
                    print(f"🐛 DEBUG: Content is not a Figure, it's: {function_res['content']}")
        else:
            break
        cur_iter += 1
