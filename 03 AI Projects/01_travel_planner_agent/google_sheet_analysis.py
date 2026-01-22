"""Google Sheets MCP Test and Analysis."""
import warnings
warnings.filterwarnings('ignore')

import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

import asyncio

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    convert_system_message_to_human=True  # Some models need this for tool calling
)

system_prompt = """You are a helpful Google Sheets assistant.

You have access to Google Sheets tools. When the user asks about spreadsheets:
- Use the list_spreadsheets tool to list all spreadsheets
- Use get_sheet_data to read sheet data
- Use create_spreadsheet to create new sheets

IMPORTANT: You MUST use the available tools to complete user requests. Do not try to answer without using tools."""

async def get_sheets_tools():
    """Load only Google Sheets MCP tools."""
    client = MultiServerMCPClient(
        {
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

    print(f"Loaded {len(mcp_tools)} Google Sheets Tools")
    print("\nAvailable tools:")

    # Filter to only include safe tools that work with Gemini
    safe_tools = []
    problematic_tools = ['update_cells', 'batch_update_cells', 'get_multiple_sheet_data',
                        'get_multiple_spreadsheet_summary', 'batch_update']

    for tool in mcp_tools:
        if tool.name not in problematic_tools:
            print(f"  ✓ {tool.name}")
            safe_tools.append(tool)
        else:
            print(f"  ✗ {tool.name} (skipped - complex schema)")

    return safe_tools

async def test_sheets(query):
    print("Getting Google Sheets tools...")
    tools = await get_sheets_tools()

    print(f"\nCreating agent with {len(tools)} tools...")
    agent = create_agent(model=model, tools=tools, system_prompt=system_prompt)

    print("Invoking agent with query...")
    print(f"Query: {query}\n")

    try:
        result = await asyncio.wait_for(
            agent.ainvoke({"messages": [HumanMessage(content=query)]}),
            timeout=120.0
        )
        print("Agent completed!\n")

        # Extract the AI's final response from messages
        messages = result['messages']

        # Find all AI messages with content
        ai_messages = [
            str(msg.content)
            for msg in messages
            if hasattr(msg, 'type') and msg.type == 'ai' and
               hasattr(msg, 'content') and msg.content and len(str(msg.content).strip()) > 0
        ]

        # Get the last AI message (this is the final response after tool use)
        response = ai_messages[-1] if ai_messages else "No response generated"

        print("Response:")
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
    # Test query: List available spreadsheets
    query = "List all my Google Spreadsheets."

    asyncio.run(test_sheets(query))
