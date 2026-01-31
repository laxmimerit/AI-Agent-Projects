"""Daily Briefing Agent with MCP Tools."""
"""Use gmail, google calendar, yahoo news, web search and weather for daily morning update"""

import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from scripts import base_tools, prompts, utils

from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

checkpointer = InMemorySaver()


async def get_tools():
    mcp_config = utils.load_mcp_config("gmail","google-calendar", "yahoo-finance")
    # print("mcp config loaded:", mcp_config)

    client = MultiServerMCPClient(mcp_config)

    mcp_tools = await client.get_tools()

    tools = mcp_tools + [base_tools.web_search, base_tools.get_weather]

    # # Filter tools that work with Gemini
    filter_tools = ['delete_email', 'batch_modify_emails', 'batch_delete_emails','delete_label','delete_filter']
    
    safe_tools = [tool for tool in tools if tool.name not in filter_tools]

    print(f"Loaded {len(safe_tools)} Tools")
    print(f"Tools Available\n{[tool.name for tool in safe_tools]}")

    return safe_tools

async def get_briefing(query, thread_id='default'):
    tools = await get_tools()

    system_prompt = prompts.get_daily_briefing_prompt()

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer
    )

    config = {"configurable": {"thread_id": thread_id}}
    result = await agent.ainvoke({'messages': [HumanMessage(query)]}, config=config)

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

        await get_briefing(query)

if __name__ == "__main__":
    # query = """Give me my daily briefing:
    #                1. Today's weather
    #                2. Today's calendar events
    #                3. Summary of unread emails
    #                4. Top news headlines"""
    # asyncio.run(get_briefing(query))
    asyncio.run(ask())



