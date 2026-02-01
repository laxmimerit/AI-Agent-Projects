import streamlit as st
import httpx
import json

BASE_URL = "http://localhost:8000"

st.title("Personal Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

thread_id = st.sidebar.text_input("Thread ID", value="default")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"].replace("$", "\\$"))

if query := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        tool_container = st.container()
        placeholder = st.empty()
        full_response = ""

        with httpx.Client(timeout=None) as client:
            with client.stream("POST", f"{BASE_URL}/stream", json={"query": query, "thread_id": thread_id}) as response:
                for line in response.iter_lines():
                    if not line.strip():
                        continue
                    chunk = json.loads(line)
                    msg_type = chunk.get("type", "")
                    content = chunk.get("content", "")

                    if chunk.get("tool_calls"):
                        for tc in chunk["tool_calls"]:
                            with tool_container:
                                st.status(f"🔧 {tc['name']}", state="complete").write(f"```json\n{json.dumps(tc['args'], indent=2)}\n```")

                    if content and "AI" in msg_type:
                        full_response = content
                        placeholder.markdown(full_response.replace("$", "\\$") + "▌")

        placeholder.markdown(full_response.replace("$", "\\$"))

    st.session_state.messages.append({"role": "assistant", "content": full_response})
