import streamlit as st
import httpx
import json
import os
from datetime import datetime
import markdown2
from xhtml2pdf import pisa

BASE_URL = "http://localhost:8000"

st.title("Personal Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

thread_id = st.sidebar.text_input("Thread ID", value="default")

if st.sidebar.button("Clear Messages"):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("Download PDF"):
    assistant_msgs = [m for m in st.session_state.messages if m["role"] == "assistant"]
    if assistant_msgs:
        last_msg = assistant_msgs[-1]
        question_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
        question = question_msgs[-1]["content"] if question_msgs else "response"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_question = "".join(c if c.isalnum() or c in " _-" else "" for c in question[:50]).strip()
        filename = f"{timestamp}_{safe_question}.pdf"
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        filepath = os.path.join(downloads_dir, filename)

        html = markdown2.markdown(
            last_msg["content"],
            extras=["tables", "fenced-code-blocks", "cuddled-lists"]
        )
        styled_html = f"""<html><head><meta charset="utf-8">
        <style>
            body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12px; line-height: 1.6; padding: 20px; }}
            h1 {{ font-size: 20px; }} h2 {{ font-size: 16px; }} h3 {{ font-size: 14px; }}
            code {{ background: #f4f4f4; padding: 2px 4px; }}
            pre {{ background: #f4f4f4; padding: 10px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 6px; text-align: left; }}
        </style></head><body>{html}</body></html>"""
        with open(filepath, "wb") as f:
            pisa.CreatePDF(styled_html, dest=f)
        st.sidebar.success(f"Saved to {filename}")
    else:
        st.sidebar.warning("No assistant message to export")

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
