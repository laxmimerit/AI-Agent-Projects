"""Google Sheets MCP Test and Analysis."""
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

from scripts import base_tools, prompts

from langchain.messages import HumanMessage, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

import asyncio

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

async def get_sheets_tools():
    """Load only Google Sheets MCP tools."""
    mcp_config = base_tools.load_mcp_config('google-sheets')
    client = MultiServerMCPClient(mcp_config)

    mcp_tools = await client.get_tools()
    print(f"Loaded {len(mcp_tools)} Google Sheets tools\n")

    # Filter tools that work with Gemini
    problematic_tools = ['update_cells', 'batch_update_cells', 'get_multiple_sheet_data',
                        'get_multiple_spreadsheet_summary', 'batch_update']

    safe_tools = [tool for tool in mcp_tools if tool.name not in problematic_tools]

    return safe_tools

async def test_sheets(query):
    tools = await get_sheets_tools()

    agent = create_agent(model=model, tools=tools, system_prompt=prompts.GOOGLE_SHEETS_PROMPT)

    result = await agent.ainvoke({"messages": [HumanMessage(content=query)]})

    # Extract final AI response
    messages = result['messages']
    ai_messages = [msg.text for msg in messages if isinstance(msg, AIMessage) and msg.text]

    response = ai_messages[-1] if ai_messages else "No response generated"
    print(response)

    return response

if __name__ == "__main__":
    query = "List all my Google Spreadsheets."
    asyncio.run(test_sheets(query))
