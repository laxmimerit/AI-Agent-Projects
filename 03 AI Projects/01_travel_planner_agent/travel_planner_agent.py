"""Simple Airbnb MCP module."""
######## MCP SETUP ###############
# MCP GITHUB
# https://github.com/laxmimerit/MCP-Mastery-with-Claude-and-Langchain
# https://github.com/laxmimerit/Agentic-RAG-with-LangGraph-and-Ollama

# https://github.com/langchain-ai/langchain-mcp-adapters

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

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

system_prompt = """
You are a travel planning assistant with access to multiple tools.

Tasks you can perform:
- Search Airbnb listings (defaults: adults=2, no dates if not specified)
- Get weather information for destinations
- Search web for attractions, events, travel info
- Create trip itineraries in Google Sheets
- Add trip events to Google Calendar

Instructions:
- Be proactive, search immediately when asked
- Present Airbnb results with links: https://www.airbnb.com/rooms/{listing_id}
- Create structured itineraries in Google Sheets with dates, activities, costs
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
    # Start with a simple test query
    query = "What's the weather in Mumbai?"
    # Complex query (uncomment when simple query works):
    query = "Plan a 3-day trip to Mumbai. Find hotels, check weather, create itinerary add events to Calendar."
    asyncio.run(hotel_search(query))