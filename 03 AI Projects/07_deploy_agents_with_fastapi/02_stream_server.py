# fastapi dev .\02_stream_server.py
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
print(root_dir)

from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage, AIMessageChunk

from scripts import base_tools, prompts, utils

checkpointer = InMemorySaver()
tools = None

# Pydantic Data Model
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    model: str = "gemini-2.5-flash"
    thread_id: str = "default"


async def get_tools():
    mcp_config = utils.load_mcp_config("gmail", "yahoo-finance", "google-sheets")
    # print("mcp config loaded:", mcp_config)

    client = MultiServerMCPClient(mcp_config)
    mcp_tools = await client.get_tools()
    tools = mcp_tools + [base_tools.web_search, base_tools.get_weather]

    # # Filter tools that work with Gemini
    filter_tools = [
        "delete_email",
        "batch_modify_emails",
        "batch_delete_emails",
        "delete_label",
        "delete_filter",
        "update_cells",
    ]

    safe_tools = [tool for tool in tools if tool.name not in filter_tools]

    print(f"Loaded {len(safe_tools)} Tools")
    print(f"Tools Available\n{[tool.name for tool in safe_tools]}")

    return safe_tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tools
    tools = await get_tools()
    print("Tools are loaded. ready to create agent!")
    yield


app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def stream_response(query, model_name, thread_id):
    system_prompt = prompts.get_assistant_prompt()

    # Initialize model and agent
    model = ChatGoogleGenerativeAI(model=model_name)
    agent = create_agent(model=model, tools=tools, system_prompt=system_prompt, checkpointer=checkpointer)

    # Configuration with thread ID for conversation memory
    config = {"configurable": {"thread_id": thread_id}}

    async for chunk, metadata in agent.astream(
        {'messages':[HumanMessage(query)]},
        stream_mode='messages', config=config):

        data = {
            "type": chunk.__class__.__name__,
            "content": chunk.text
        }

        if isinstance(chunk, AIMessageChunk) and chunk.tool_calls:
            data['tool_calls'] = chunk.tool_calls

        # send json response
        yield (json.dumps(data) + "\n").encode()


@app.get("/")
async def read_root():
    return {"Hello": "Laxmi. Your FastAPI Server is up!"}


@app.post("/chat_stream")
async def chat_stream(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Empty prompt!")
    
    try:
        return StreamingResponse(
            stream_response(request.query, request.model, request.thread_id),
            media_type="application/x-ndjson")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="0.0.0.0", port=8002)