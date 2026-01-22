"""Travel Planner Agent with MCP Tools."""
import warnings
warnings.filterwarnings('ignore')

import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

from scripts import base_tools

from langchain.messages import HumanMessage, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

import asyncio
from datetime import datetime, timedelta

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

checkpointer = InMemorySaver()

def get_system_prompt():
    """Generate system prompt with current date context."""
    today = datetime.now()
    checkin_date = today
    checkout_date = today + timedelta(days=5)

    return f"""You are a travel planning assistant.

Today: {today.strftime('%Y-%m-%d (%A)')}
Default dates: Check-in {checkin_date.strftime('%Y-%m-%d')}, Checkout {checkout_date.strftime('%Y-%m-%d')} (5 days)

Tools: Airbnb search, weather, web search, Google Calendar

Instructions:
- Search Airbnb (default: 2 adults, no price filters unless requested)
- Present listings with https://www.airbnb.com/rooms/{{listing_id}}
- Add events to Google Calendar with times and locations"""

async def get_tools():
    client = MultiServerMCPClient({
        "airbnb": {
            "command": "npx",
            "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            "transport": "stdio"
        },
        "google-calendar": {
            "command": "npx",
            "args": ["@cocal/google-calendar-mcp"],
            "env": {"GOOGLE_OAUTH_CREDENTIALS": "C:\\Users\\laxmi\\.gmail-mcp\\gcp-oauth.keys.json"},
            "transport": "stdio"
        }
    })

    mcp_tools = await client.get_tools()
    all_tools = mcp_tools + [base_tools.web_search, base_tools.get_weather]

    print(f"Loaded {len(all_tools)} tools\n")
    return all_tools

async def plan_trip(query, thread_id="default"):
    tools = await get_tools()
    system_prompt = get_system_prompt()

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer
    )

    config = {"configurable": {"thread_id": thread_id}}

    result = await agent.ainvoke({"messages": [HumanMessage(content=query)]}, config=config)

    response = result['messages'][-1].text

    print(f"\nResponse:\n{response}")
    return response

if __name__ == "__main__":
    query = "Plan a romantic 5-day trip to Mumbai. Find romantic hotels for 2 adults, check weather, and add the trip to my primary Google Calendar."
    asyncio.run(plan_trip(query))