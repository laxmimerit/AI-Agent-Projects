import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver

from scripts import base_tools, prompts, utils

load_dotenv()

import os

# print(os.getenv('OLLAMA_API_KEY'))

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
checkpointer = InMemorySaver()
agent = None


async def get_tools():
    mcp_config = utils.load_mcp_config("gmail", "yahoo-finance", "google-sheets")
    client = MultiServerMCPClient(mcp_config)
    mcp_tools = await client.get_tools()
    tools = mcp_tools + [base_tools.web_search, base_tools.get_weather]

    filter_tools = ['delete_email', 'batch_modify_emails', 'batch_delete_emails', 'delete_label', 'delete_filter', 'update_cells']
    safe_tools = [tool for tool in tools if tool.name not in filter_tools]

    print(f"Loaded {len(safe_tools)} Tools")
    print(f"Tools Available\n{[tool.name for tool in safe_tools]}")
    return safe_tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    tools = await get_tools()
    system_prompt = prompts.get_daily_briefing_prompt()
    agent = create_agent(model=model, tools=tools, system_prompt=system_prompt, checkpointer=checkpointer)
    print("Agent ready")
    yield


app = FastAPI(lifespan=lifespan)


class QueryRequest(BaseModel):
    query: str
    thread_id: str = "default"


async def stream_response(query: str, thread_id: str = "default"):
    config = {"configurable": {"thread_id": thread_id}}
    async for chunk in agent.astream(
        {"messages": [("user", query)]},
        stream_mode="values",
        config=config,
    ):
        if "messages" in chunk and chunk["messages"]:
            msg = chunk["messages"][-1]
            data = {
                "type": msg.__class__.__name__,
                "content": getattr(msg, 'text', ''),
            }
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                data["tool_calls"] = msg.tool_calls
            yield (json.dumps(data) + "\n").encode()


@app.post("/stream")
async def stream_endpoint(request: QueryRequest):
    return StreamingResponse(
        stream_response(request.query, request.thread_id),
        media_type="application/x-ndjson",
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
