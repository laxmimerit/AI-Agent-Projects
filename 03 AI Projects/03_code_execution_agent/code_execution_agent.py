"""Code Execution Agent with MCP Tools."""
import warnings
warnings.filterwarnings('ignore')

import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

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

system_prompt = """You are a code execution assistant with visualization capabilities.

Tools: Python code execution (E2B), chart visualization

Instructions:
- Execute Python code in a secure sandbox environment
- Use chart tools to create visualizations (line, bar, pie, scatter, etc.)
- Explain code execution results clearly
- Create data visualizations when appropriate
- Handle errors gracefully and provide debugging help"""

async def get_tools():
    client = MultiServerMCPClient({
        "e2b": {
            "command": "npx",
            "args": ["-y", "@e2b/mcp-server"],
            "transport": "stdio"
        },
        "mcp-server-chart": {
            "command": "npx",
            "args": ["-y", "@antv/mcp-server-chart"],
            "transport": "stdio"
        }
    })

    mcp_tools = await client.get_tools()

    print(f"Loaded {len(mcp_tools)} tools\n")
    return mcp_tools

async def execute_code(query, thread_id="default"):
    tools = await get_tools()

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
    query = """Execute this Python code:

    import numpy as np
    import pandas as pd

    # Create sample sales data
    data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'Sales': [15000, 18000, 12000, 22000, 25000],
        'Profit': [3000, 4500, 2000, 6000, 7500]
    }

    df = pd.DataFrame(data)
    print(df)
    print(f"\\nTotal Sales: ${df['Sales'].sum()}")
    print(f"Average Profit: ${df['Profit'].mean():.2f}")

    # Also create a bar chart showing Sales by Month"""

    asyncio.run(execute_code(query))
