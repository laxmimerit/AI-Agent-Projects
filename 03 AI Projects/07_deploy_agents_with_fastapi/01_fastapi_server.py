# fastapi dev .\01_fastapi_server.py
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
# print(root_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage

app = FastAPI()

# Pydantic Data Model
class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=2)
    model: str = 'gemini-2.5-flash'

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello": "Laxmi kant"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Empty prompt!")
    
    try:
        model = ChatGoogleGenerativeAI(model=request.model)
        agent = create_agent(model=model)
        response = agent.invoke({'messages': [HumanMessage(request.prompt)]})

        return {'response': response['messages'][-1].text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


if __name__=="__main__":
    import uvicorn
    uvicorn.run(app=app, host='0.0.0.0', port=8001)