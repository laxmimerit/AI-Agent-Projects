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

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI

import asyncio

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

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
            },
            "google-sheets": {
                "command": "uvx",
                "args": ["mcp-google-sheets@latest"],
                "env": {
                    "CREDENTIALS_PATH": "C:\\Users\\laxmi\\.gmail-mcp\\gcp-oauth.keys.json",
                    "TOKEN_PATH": "C:\\Users\\laxmi\\.gmail-mcp\\token.json"
                },
                "transport": "stdio"
            }
        }
    )

    mcp_tools = await client.get_tools()
    all_tools = mcp_tools + [base_tools.web_search, base_tools.get_weather]

    print(f"Loaded {len(all_tools)} Tools")

    return all_tools

async def hotel_search(query):
    tools = await get_tools()
    agent = create_agent(model=model, tools=tools, system_prompt=system_prompt)
    result = await agent.ainvoke({'messages': [HumanMessage(query)]})

    response = result['messages'][-1].content[0]['text']
    print(response)

    return response

if __name__=="__main__":
    query = "Plan a 3-day trip to Mumbai. Find hotels, check weather, create itinerary in Google Sheets and add events to Calendar."
    asyncio.run(hotel_search(query))