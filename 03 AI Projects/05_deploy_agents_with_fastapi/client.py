# client_advanced.py
import httpx
import json
from typing import Iterator, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class StreamChunk:
    """Structured representation of a stream chunk"""
    type: str
    content: str = ""
    metadata: Optional[dict] = None
    tool_calls: Optional[list] = None
    error: Optional[str] = None
    message_type: Optional[str] = None


class AgentStreamClient:
    """Advanced client for LangChain agent streaming"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=None)
    
    def stream_values(self, query: str, config: dict = None) -> Iterator[StreamChunk]:
        """Stream complete agent state"""
        endpoint = f"{self.base_url}/stream/values"
        payload = {"query": query}
        if config:
            payload["config"] = config
        
        with self.client.stream("POST", endpoint, json=payload) as response:
            for line in response.iter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        yield StreamChunk(
                            type=data.get("type"),
                            content=data.get("content", ""),
                            metadata=data.get("metadata"),
                            tool_calls=data.get("tool_calls"),
                            error=data.get("error"),
                            message_type=data.get("message_type")
                        )
                    except json.JSONDecodeError:
                        continue
    
    def stream_incremental(self, query: str, config: dict = None) -> Iterator[StreamChunk]:
        """Stream only deltas (incremental content)"""
        endpoint = f"{self.base_url}/stream/incremental"
        payload = {"query": query}
        if config:
            payload["config"] = config
        
        with self.client.stream("POST", endpoint, json=payload) as response:
            for line in response.iter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        yield StreamChunk(
                            type=data.get("type"),
                            content=data.get("content", ""),
                            error=data.get("error"),
                            message_type=data.get("message_type")
                        )
                    except json.JSONDecodeError:
                        continue
    
    def get_complete_response(self, query: str, config: dict = None) -> str:
        """Get complete response as single string"""
        complete_response = []
        
        for chunk in self.stream_incremental(query, config):
            if chunk.type == "error":
                raise Exception(f"Agent error: {chunk.error}")
            
            if chunk.type == "done":
                break
            
            if chunk.content:
                complete_response.append(chunk.content)
        
        return "".join(complete_response)
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


# Example usage
if __name__ == "__main__":
    with AgentStreamClient() as client:
        # Stream with live updates
        print("=== Streaming Response ===\n")
        for chunk in client.stream_incremental("What's the weather in London?"):
            if chunk.type == "delta":
                print(chunk.content, end="", flush=True)
            elif chunk.type == "tool_call":
                print(f"\n[Calling tools]")
            elif chunk.type == "done":
                print("\n\n=== Complete ===")
                break
            elif chunk.type == "error":
                print(f"\nError: {chunk.error}")
                break
        
        # Or get complete response at once
        print("\n\n=== Complete Response ===\n")
        response = client.get_complete_response("Explain quantum computing")
        print(response)