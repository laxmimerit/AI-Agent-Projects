# Deploy Agents with FastAPI

## Installation

```bash
pip install fastapi uvicorn httpx streamlit markdown2 xhtml2pdf
```

## 01 FastAPI Server

Simple chat endpoint without streaming.

**Run:**
```bash
python 01_fastapi_server.py
```

**Test with curl:**
```bash
# Health check
curl http://localhost:8000/

# Chat request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?"}'
```

## 02 Stream Server

Streaming endpoint with MCP tools and memory.

**Run:**
```bash
python 02_stream_server.py
```

**Test with curl:**
```bash
# Health check
curl http://localhost:8000/health

# Stream request
curl -X POST http://localhost:8000/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in London?"}'

# Stream with thread_id for memory
curl -X POST http://localhost:8000/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in London?", "thread_id": "user-123"}'
```

## 03 Streamlit Client

Chat UI for the stream server.

**Run:**
```bash
streamlit run 03_streamlit_client.py
```
