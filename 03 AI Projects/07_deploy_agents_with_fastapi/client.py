import httpx
import json


def stream_query(query: str, base_url: str = "http://localhost:8000"):
    with httpx.Client(timeout=None) as client:
        with client.stream("POST", f"{base_url}/stream", json={"query": query}) as response:
            for line in response.iter_lines():
                if line.strip():
                    data = json.loads(line)
                    yield data


if __name__ == "__main__":
    for chunk in stream_query("What's the weather in London?"):
        msg_type = chunk.get("type")
        content = chunk.get("content", "")

        if content and "AI" in msg_type:
            print(content, end="", flush=True)
        elif chunk.get("tool_calls"):
            print("[Calling tools]")

    print()
