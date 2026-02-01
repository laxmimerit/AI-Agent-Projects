import sys
sys.path.append('D:\\Courses\\Udemy\\AI Agent Projects')

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from scripts import base_tools

load_dotenv()

app = FastAPI()

model = ChatGoogleGenerativeAI(model='gemini-3-flash-preview')
tools = [base_tools.web_search, base_tools.get_weather]
agent = create_agent(model=model, tools=tools)


class QueryRequest(BaseModel):
    query: str


async def stream_response(query: str):
    async for chunk in agent.astream(
        {"messages": [("user", query)]},
        stream_mode="values",
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
        stream_response(request.query),
        media_type="application/x-ndjson",
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)