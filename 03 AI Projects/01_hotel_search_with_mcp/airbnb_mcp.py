"""Airbnb MCP Server."""
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

from scripts import base_tools, prompts

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI

import asyncio

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

async def get_tools():
    mcp_config = base_tools.load_mcp_config('airbnb')
    client = MultiServerMCPClient(mcp_config)

    mcp_tools = await client.get_tools()
    all_tools = mcp_tools + [base_tools.web_search, base_tools.get_weather]

    print(f"Loaded {len(all_tools)} Tools")
    print(f"Tools Available: {all_tools}")

    return all_tools

async def hotel_search(query):
    tools = await get_tools()
    agent = create_agent(model=model, tools=tools, system_prompt=prompts.AIRBNB_PROMPT)
    result = await agent.ainvoke({'messages': [HumanMessage(query)]})

    response = result['messages'][-1].text
    print(response)

    return response

if __name__=="__main__":
    query = "Show me hotels for a party in Mumbai also check weather."
    asyncio.run(hotel_search(query))
