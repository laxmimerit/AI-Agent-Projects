"""Simple Airbnb MCP module."""
######## MCP SETUP ###############
# MCP GITHUB
# https://github.com/laxmimerit/MCP-Mastery-with-Claude-and-Langchain
# https://github.com/laxmimerit/Agentic-RAG-with-LangGraph-and-Ollama

# https://github.com/langchain-ai/langchain-mcp-adapters

import warnings
warnings.filterwarnings('ignore')

# Add scripts directory to system path
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

from scripts import base_tools

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

import asyncio
from datetime import datetime, timedelta

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def get_system_prompt():
    """Generate system prompt with current date context."""
    today = datetime.now()

    # Default: 5-day trip starting from today
    checkin_date = today
    checkout_date = today + timedelta(days=5)

    return f"""
You are a travel planning assistant with access to multiple tools.

CURRENT DATE CONTEXT:
- Today's date: {today.strftime('%Y-%m-%d (%A)')}
- Default check-in: {checkin_date.strftime('%Y-%m-%d')}
- Default checkout (5 days later): {checkout_date.strftime('%Y-%m-%d')}

Tasks you can perform:
- Search Airbnb listings (defaults: adults=2, use dates from context or user request)
- Get weather information for destinations
- Search web for attractions, events, travel info
- Add trip events to Google Calendar

Default trip settings:
- Trip duration: 5 days (can be adjusted based on user request)
- Default: 2 adults
- Do NOT apply price filters unless explicitly requested by user

Instructions:
- Be proactive, search immediately when asked
- Use dates from user query if specified, otherwise use default dates from context
- Present Airbnb results with links: https://www.airbnb.com/rooms/{{listing_id}}
- Include pricing information and ratings
- Show a variety of options at different price points
- Add travel events to Google Calendar with proper times and locations
"""

async def get_tools():
    # Removed google-sheets MCP for testing
    client = MultiServerMCPClient(
        {
            "airbnb": {
                "command": "npx",
                "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
                "transport": "stdio"
            },
            "google-calendar": {
                "command": "npx",
                "args": ["@cocal/google-calendar-mcp"],
                "env": {
                    "GOOGLE_OAUTH_CREDENTIALS": "C:\\Users\\laxmi\\.gmail-mcp\\gcp-oauth.keys.json"
                },
                "transport": "stdio"
            }
        }
    )

    mcp_tools = await client.get_tools()

    # Filter out tools with nested array schemas incompatible with Gemini
    filtered_tools = [
        tool for tool in mcp_tools
        if tool.name not in ['update_cells', 'batch_update_cells', 'get_multiple_sheet_data', 'batch_update']
    ]

    all_tools = filtered_tools + [base_tools.web_search, base_tools.get_weather]

    print(f"Loaded {len(all_tools)} Tools")

    return all_tools

async def hotel_search(query):
    print("Getting tools...")
    tools = await get_tools()
    print(f"Creating agent with {len(tools)} tools...")

    # Get system prompt with current date context
    system_prompt = get_system_prompt()
    print(f"\n{system_prompt}\n")

    # Create agent using langchain.agents.create_agent
    agent = create_agent(model=model, tools=tools, system_prompt=system_prompt)

    print("Invoking agent with query...")

    try:
        # Invoke agent with timeout
        result = await asyncio.wait_for(
            agent.ainvoke({"messages": [HumanMessage(content=query)]}),
            timeout=120.0  # 2 minutes for agent to complete
        )
        print("Agent completed!")

        # Get the final response
        response = result['messages'][-1].content
        print("\nResponse:")
        print(response)

        return response

    except asyncio.TimeoutError:
        print("ERROR: Agent execution timed out after 2 minutes")
        return "Execution timed out"
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

if __name__=="__main__":
    # Full travel planning query (uncomment to test full flow):
    query = "Plan a romantic 5-day trip to Mumbai. Find romantic hotels for 2 adults, check weather, and you must add the trip to my primary Google Calendar."

    asyncio.run(hotel_search(query))