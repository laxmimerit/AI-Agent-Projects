"""Travel Planner Agent with MCP Tools."""
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

from scripts import base_tools, prompts

from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

import asyncio

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

checkpointer = InMemorySaver()

async def get_tools():
    mcp_config = base_tools.load_mcp_config('airbnb', 'google-calendar')
    client = MultiServerMCPClient(mcp_config)

    mcp_tools = await client.get_tools()
    all_tools = mcp_tools + [base_tools.web_search, base_tools.get_weather]

    print(f"Loaded {len(all_tools)} tools\n")
    return all_tools

async def plan_trip(query, thread_id="default"):
    tools = await get_tools()
    system_prompt = prompts.get_travel_planner_prompt()

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
    query = """Plan a romantic 5-day trip to Mumbai. 
                Find romantic hotels for 2 adults, check weather, 
                and add the trip to my primary Google Calendar."""
    
    asyncio.run(plan_trip(query))