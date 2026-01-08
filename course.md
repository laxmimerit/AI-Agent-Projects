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
- Host Agent with Open WebUI / Chat Agent UI
    - Design FastAPI endpoints for invoke and stream responses 

- Youtube Video Analyzer
    - YouTube Transcript API
    - Fetch video transcripts
    - Summarize any video
    - Extract key points with timestamps

- API Builder Agent
    - Takes sample notebook. clean it and place it inside working api blocks
    - Create structured prompt with powerful model to follow pre-defined structure
    - Allow Google search gounding
    - Build unit test script to make sure it is working.

- Data Analysis Agent
    - analyze any kind of file
    - generate graph
    - code sandbox
    - Gmail expense tracker
    - attach graph generator MCP

- Daily Briefing Agent
    - Fetches weather (OpenWeatherMap API)
    - Reads today's calendar events (Google Calendar)
    - Summarizes unread emails (Gmail)
    - Shows top news headlines (Ollama Search)

- Travel Planning Agent
    - Search flights (Skyscanner API)
    - Find hotels (Booking API)
    - Create itinerary in Google Sheets
    - Add trip events to Google Calendar

- Voice Agent (Optional)
    - Langchain + Livekit

### Real-World Projects
- E-Commerce Campaign Builder
    - Use mailchimp to send emailers based on user prefs and orders
    - Approval Agent (human approval before sending)
    - Monitoring / Logging Agent

- E-Commerce Customer Support Agent
    - Understand customer intent (refund, status, cancellation)
    - Query real-time order data via safe SQL tools
    - Apply business rules for refunds/cancellations
    - Use chat history for continuity (no repetition)
    - Escalate to humans when confidence is low

- E-Commerce Operational Metrics Explainer
    - Analyze the metrics
    - Build Graph
    - Find out inconsistencies
    - Analyze time-series data
    - Use graph builder MCP
