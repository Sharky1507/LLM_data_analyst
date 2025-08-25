import asyncio
import logging
import os
import json
from pathlib import Path
from dotenv import load_dotenv

import httpx
from groq import AsyncGroq

# Load environment variables if not already loaded
if not os.environ.get("GROQ_API_KEY"):
    # Try to load from chatbot package root
    chatbot_root = Path(__file__).parent.parent
    env_path = chatbot_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

logging.info(f"User message")

model = "llama3-70b-8192"  # Use regular model without tool-use-preview
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is required")

# Configure Groq client
client = AsyncGroq(api_key=api_key)

# Main chatbot class
class ChatBot:
    def __init__(self, system, tools, tool_functions):
        self.system = system
        self.tools = tools
        self.exclude_functions = ["plot_chart"]
        self.tool_functions = tool_functions
        self.messages = []
        self.max_messages = 4  # Reduced to save tokens - only keep last 2 exchanges
        if self.system:
            self.messages.append({"role": "system", "content": system})

    async def __call__(self, message):
        self.messages.append({"role": "user", "content": f"""{message}"""})
        
        # Keep only the last max_messages to save tokens
        if len(self.messages) > self.max_messages:
            # Always keep system message and only the most recent exchange
            system_msg = self.messages[0] if self.messages[0]["role"] == "system" else None
            recent_messages = self.messages[-(self.max_messages-1):]
            self.messages = [system_msg] + recent_messages if system_msg else recent_messages
            print(f"🔧 Trimmed conversation history to {len(self.messages)} messages to save tokens")
        
        response_message = await self.execute()
        
        # Handle tool calls if present
        if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
            print(f"🔧 Processing {len(response_message.tool_calls)} tool calls...")
            response_message, function_responses = await self.call_functions(response_message.tool_calls)
            print(f"✅ Tool calls completed, final response: {response_message.content[:200] if response_message.content else 'No content'}...")
        
        # Add assistant response to conversation if it has content
        if response_message.content:
            self.messages.append({"role": "assistant", "content": response_message.content})

        logging.info(f"User message: {message}")
        logging.info(f"Assistant response: {response_message.content}")

        return response_message

    async def execute(self):
        try:
            # Use Groq's chat completion API (OpenAI-compatible)
            completion = await client.chat.completions.create(
                model=model,
                messages=self.messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                temperature=0.1,  # Lower temperature for more consistent function calling
                max_tokens=4000   # Ensure enough tokens for responses
            )
            
            assistant_message = completion.choices[0].message
            print(f"🐛 DEBUG: Assistant message: {assistant_message}")
            print(f"🐛 DEBUG: Tool calls: {assistant_message.tool_calls}")
            return assistant_message
                
        except Exception as e:
            logging.error(f"Error in Groq API call: {e}")
            print(f"❌ Full error details: {e}")
            
            # Create a response object similar to OpenAI's format
            class AssistantMessage:
                def __init__(self, content):
                    self.content = content
                    self.tool_calls = []
            
            return AssistantMessage(f"I encountered an error with the API. Let me try to help you differently. Could you please rephrase your request?")

    async def call_function(self, tool_call):
        function_name = tool_call.function.name
        function_to_call = self.tool_functions[function_name]
        
        # Handle Groq function call arguments (should be JSON string)
        try:
            if hasattr(tool_call.function, 'arguments') and tool_call.function.arguments:
                function_args = json.loads(tool_call.function.arguments)
            else:
                function_args = {}
        except json.JSONDecodeError:
            logging.error(f"Failed to parse function arguments: {tool_call.function.arguments}")
            function_args = {}
        
        logging.info(f"Calling {function_name} with {function_args}")
        function_response = await function_to_call(**function_args)

        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": function_response,
        }

    async def call_functions(self, tool_calls):

        # Use asyncio.gather to make function calls in parallel
        function_responses = await asyncio.gather(
            *(self.call_function(tool_call) for tool_call in tool_calls)
            )

        # Extend conversation with all function responses
        responses_in_str = [{**item, "content": str(item["content"])} for item in function_responses]

        # Log each tool call object separately
        for res in function_responses:
            logging.info(f"Tool Call: {res}")

        self.messages.extend(responses_in_str)

        response_message = await self.execute()
        return response_message, function_responses
