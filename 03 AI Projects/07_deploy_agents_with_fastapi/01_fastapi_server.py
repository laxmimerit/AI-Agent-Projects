"""
GenAI Server - FastAPI + LangChain Agent
Author: Laxmi Kant (KGP Talkie)
"""

import warnings
warnings.filterwarnings('ignore')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

load_dotenv()

# Pydantic Model
class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)

# FastAPI App
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model
model = ChatGoogleGenerativeAI(model='gemini-3-flash-preview')

# Create the agent
agent = create_agent(
    model=model,
)

@app.get("/")
async def root():
    return {"message": "GenAI API is running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Empty prompt")
    
    try:
        response = agent.invoke({"input": request.prompt})
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)