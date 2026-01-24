"""Daily Briefing Agent with MCP Tools."""
import sys
import os

print(os.getenv('OLLAMA_API_KEY'))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from scripts import base_tools, prompts

from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

import asyncio

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

async def get_tools():
    mcp_config = base_tools.load_mcp_config('gmail', 'google-calendar')
    client = MultiServerMCPClient(mcp_config)

    mcp_tools = await client.get_tools()
    all_tools = mcp_tools + [base_tools.web_search, base_tools.get_weather]

    print(f"Loaded {len(all_tools)} tools\n")
    return all_tools

async def get_briefing(query=None):
    tools = await get_tools()
    system_prompt = prompts.get_daily_briefing_prompt()

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )

    if query is None:
        query = """Give me my daily briefing:
                   1. Today's weather
                   2. Today's calendar events
                   3. Summary of unread emails
                   4. Top news headlines"""

    result = await agent.ainvoke({"messages": [HumanMessage(content=query)]})

    response = result['messages'][-1].text

    print(f"\nDaily Briefing:\n{response}")
    return response

if __name__ == "__main__":
    asyncio.run(get_briefing())
