import sys
sys.path.append('D:\\Courses\\Udemy\\AI Agent Projects')

import warnings
warnings.filterwarnings('ignore')

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from typing import AsyncGenerator
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from scripts import base_tools

load_dotenv()

app = FastAPI(title="LangChain Agent Streaming API")

# Initialize agent
current_date = datetime.now().strftime("%Y-%m-%d")
model = ChatGoogleGenerativeAI(model='gemini-3-flash-preview')
tools = [base_tools.web_search, base_tools.get_weather]
agent = create_agent(model=model, tools=tools)


# Request model
class QueryRequest(BaseModel):
    query: str
    config: dict = {}


async def stream_agent_values(query: str, config: dict = None) -> AsyncGenerator[bytes, None]:
    """
    Stream agent responses in 'values' mode
    Each chunk is a complete JSON object followed by newline
    """
    try:
        stream_config = config or {}
        
        async for chunk in agent.astream(
            {"messages": [("user", query)]},
            stream_mode="values",
            config=stream_config
        ):
            # Extract message information
            if "messages" in chunk and chunk["messages"]:
                last_message = chunk["messages"][-1]
                
                # Build response chunk
                response_chunk = {
                    "type": last_message.__class__.__name__,
                    "content": getattr(last_message, 'content', ''),
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "message_count": len(chunk["messages"])
                    }
                }
                
                # Add tool call info if present
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    response_chunk["tool_calls"] = [
                        {
                            "name": tc.get("name"),
                            "args": tc.get("args"),
                            "id": tc.get("id")
                        }
                        for tc in last_message.tool_calls
                    ]
                
                # Send as newline-delimited JSON
                yield (json.dumps(response_chunk) + "\n").encode('utf-8')
        
        # Send completion signal
        completion_chunk = {
            "type": "stream_end",
            "metadata": {"timestamp": datetime.now().isoformat()}
        }
        yield (json.dumps(completion_chunk) + "\n").encode('utf-8')
        
    except Exception as e:
        error_chunk = {
            "type": "error",
            "error": str(e),
            "metadata": {"timestamp": datetime.now().isoformat()}
        }
        yield (json.dumps(error_chunk) + "\n").encode('utf-8')


async def stream_agent_incremental(query: str, config: dict = None) -> AsyncGenerator[bytes, None]:
    """
    Stream only incremental content (delta updates)
    More efficient for real-time display
    """
    try:
        stream_config = config or {}
        previous_content = ""
        
        async for chunk in agent.astream(
            {"messages": [("user", query)]},
            stream_mode="values",
            config=stream_config
        ):
            if "messages" in chunk and chunk["messages"]:
                last_message = chunk["messages"][-1]
                current_content = getattr(last_message, 'content', '')
                
                # Calculate delta (new content only)
                if len(current_content) > len(previous_content):
                    delta = current_content[len(previous_content):]
                    
                    response_chunk = {
                        "type": "delta",
                        "content": delta,
                        "message_type": last_message.__class__.__name__
                    }
                    
                    yield (json.dumps(response_chunk) + "\n").encode('utf-8')
                    previous_content = current_content
                
                # Handle tool calls
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    tool_chunk = {
                        "type": "tool_call",
                        "tools": [tc.get("name") for tc in last_message.tool_calls]
                    }
                    yield (json.dumps(tool_chunk) + "\n").encode('utf-8')
        
        # Completion signal
        yield (json.dumps({"type": "done"}) + "\n").encode('utf-8')
        
    except Exception as e:
        yield (json.dumps({"type": "error", "error": str(e)}) + "\n").encode('utf-8')


@app.post("/stream/values")
async def stream_values_endpoint(request: QueryRequest):
    """
    Stream complete agent state at each step
    Returns full message content with metadata
    """
    return StreamingResponse(
        stream_agent_values(request.query, request.config),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/stream/incremental")
async def stream_incremental_endpoint(request: QueryRequest):
    """
    Stream only new content (deltas)
    More efficient for real-time updates
    """
    return StreamingResponse(
        stream_agent_incremental(request.query, request.config),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)