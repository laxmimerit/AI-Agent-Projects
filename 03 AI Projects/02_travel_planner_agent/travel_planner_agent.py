"""Travel Planner Agent with MCP Tools."""

import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from scripts import base_tools, prompts, utils

from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

checkpointer = InMemorySaver()


async def get_tools():
    mcp_config = utils.load_mcp_config("airbnb", "google-calendar")
    # print("mcp config loaded:", mcp_config)

    client = MultiServerMCPClient(mcp_config)

    mcp_tools = await client.get_tools()

    tools = mcp_tools + [base_tools.web_search, base_tools.get_weather]

    print(f"Loaded {len(tools)} Tools")
    print(f"Tools Available\n{[tool.name for tool in tools]}")

    return tools


async def plan_trip(query, thread_id="default"):
    tools = await get_tools()

    system_prompt = prompts.get_travel_planner_prompt()

    agent = create_agent(
        model=model, tools=tools, system_prompt=system_prompt, checkpointer=checkpointer
    )

    config = {"configurable": {"thread_id": thread_id}}

    result = await agent.ainvoke({"messages": [HumanMessage(query)]}, config=config)

    response = result['messages'][-1].text

    print("\n============== Output =============")
    print(response)


async def ask():
    print("\nChat mode started. Type 'q' or 'quite' to exit.\n")
    while True:
        print("\n\n\nAsk Question. Type 'q' or 'quite' to exit.")
        query = input("You: ").strip()

        if query.lower() in ["q", "quite"]:
            print("Exiting chat mode.")
            break

        await plan_trip(query)

if __name__ == "__main__":
    # query = """Plan a romantic 5-day trip to Mumbai. 
    #             Find romantic hotels for 2 adults, check weather, 
    #             and add the trip to my primary Google Calendar.
    #             Add the itenary in the calendar description.""" 
    
    # asyncio.run(plan_trip(query))

    asyncio.run(ask())
