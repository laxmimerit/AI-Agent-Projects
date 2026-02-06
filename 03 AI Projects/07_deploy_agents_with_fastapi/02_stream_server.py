# fastapi dev .\02_stream_server.py
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
# print(root_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage

from scripts import base_tools, prompts, utils

checkpointer = InMemorySaver()
tools = None
system_prompt = None


app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Data Model
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    model: str = 'gemini-2.5-flash'
    thread_id: str = "default"

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
    global tools, system_prompt
    tools = await get_tools()
    system_prompt = prompts.get_daily_briefing_prompt()
    print("Tools loaded, ready to create agents")
    yield

async def stream_response(query: str, model_name: str = 'gemini-2.5-flash', thread_id: str = "default"):
    model = ChatGoogleGenerativeAI(model=model_name)
    agent = create_agent(model=model, tools=tools, system_prompt=system_prompt, checkpointer=checkpointer)

    config = {"configurable": {"thread_id": thread_id}}
    async for chunk in agent.astream(
        {"messages": [HumanMessage(query)]},
        stream_mode="values",
        config=config,
    ):
        if "messages" in chunk and chunk["messages"]:
            msg = chunk["messages"][-1]
            data = {
                "type": msg.__class__.__name__,
                "content": msg.text,
            }
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                data["tool_calls"] = msg.tool_calls
            yield (json.dumps(data) + "\n").encode()


@app.post("/stream")
async def stream_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Empty prompt!")

    try:
        return StreamingResponse(
            stream_response(request.query, request.model, request.thread_id),
            media_type="application/x-ndjson",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@app.get("/")
async def read_root():
    return {"Hello": "Laxmi kant"}

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app=app, host='0.0.0.0', port=8000)
