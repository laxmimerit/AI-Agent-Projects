### Getting Started
- Setting Up
- Environment & API Keys Setup (Gemini, Google, Slack, etc.)
- uv Setup with and without Anaconda
- Google GenAI Model
- Messages
- Tools

### Agent Fundamentals
- Agent Fundamentals
    - Model Usage
    - Tracing
    - Streaming
    - Error Handling & Retries
    - Fallback Models
- Agent Memory
    - Short-term Memory
    - Long-term Memory
- Agent Middlewares
    - Human-in-the-Loop
    - Logging Middleware
    - PII Redaction
- Prompt Engineering
- Guardrails
    - Prompt Injection Defense
- Context Engineering

### AI Projects
- Airbnb Hotel Search with MCP
    - Introduce MCP
    - Introduce Airbnb mcp code

- Travel Planning Agent
    - Search web-search and weather tool
    - Find hotels (Airbnb API)
    - Create itinerary in Google Sheets
    - Add trip events to Google Calendar

- Data Analysis Agent
    - analyze any kind of file
    - Gmail expense tracker
    - generate graph
    - code sandbox with e2b
    - attach graph generator MCP (antviz)

- Daily Briefing Agent
    - Fetches weather (OpenWeatherMap API)
    - Reads today's calendar events (Google Calendar)
    - Summarizes unread emails (Gmail)
    - Shows top news headlines (Ollama Search)

- Host Agent with Langchain's Chat Agent UI
    - Create structured prompt with powerful model to follow pre-defined structure
    - Allow Google search gounding

- Design and Deploy FastAPI endpoints for invoke and stream responses 
    - Basic end point design
    - Add Agent streaming endpoint
    - Add documents support
    
- Voice Agent (Optional)
    - Langchain + Livekit

### Real-World Projects
- Amazon E-Commerce Campaign Builder
    - Use mailchimp to send emailers based on user prefs and orders
    - Approval Agent (human approval before sending)
    - Monitoring / Logging Agent

- Amazon E-Commerce Customer Support Agent
    - Understand customer intent (refund, status, cancellation)
    - Query real-time order data via safe SQL tools
    - Apply business rules for refunds/cancellations
    - Use chat history for continuity (no repetition)
    - Escalate to humans when confidence is low