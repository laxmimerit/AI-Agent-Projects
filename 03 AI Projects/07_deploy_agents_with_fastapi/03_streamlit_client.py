# Streamlit Tutorials
# https://www.youtube.com/watch?v=hff2tHUzxJM&list=PLc2rvfiptPSSpZ99EnJbH5LjTJ_nOoSWW

import streamlit as st
import httpx
import json
import os
from datetime import datetime
import markdown2
from xhtml2pdf import pisa

st.title("Personal Assistant")

thread_id = st.sidebar.text_input("Thread ID", value="default")

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("Clear Messages"):
    # clear state messages
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("Download PDF"):
    assistant_msgs = [m for m in st.session_state.messages if m["role"] == "assistant"]
    if assistant_msgs:
        last_msg = assistant_msgs[-1]
        question_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
        question = question_msgs[-1]["content"] if question_msgs else "response"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_question = "".join(
            c if c.isalnum() or c in " _-" else "" for c in question[:50]
        ).strip()
        filename = f"{timestamp}_{safe_question}.pdf"
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        filepath = os.path.join(downloads_dir, filename)

        html = markdown2.markdown(
            last_msg["content"],
            extras=["tables", "fenced-code-blocks", "cuddled-lists"],
        )
        
        styled_html = f"""<html><head><meta charset="utf-8">
        <style>
            body {{ 
                font-family: Helvetica, Arial, sans-serif; 
                font-size: 14px; 
                line-height: 1.25; 
                padding: 15px; 
            }}
            h1 {{ font-size: 21px; margin: 8px 0 4px 0; line-height: 1.2; }}
            h2 {{ font-size: 18px; margin: 6px 0 3px 0; line-height: 1.2; }}
            h3 {{ font-size: 17px; margin: 5px 0 3px 0; line-height: 1.2; }}
            p {{ margin: 3px 0; line-height: 1.25; }}
            ul, ol {{ margin: 2px 0; padding-left: 20px; }}
            li {{ margin: 1px 0; padding: 0; line-height: 1.25; }}
            li p {{ display: inline; margin: 0; }}
            strong {{ font-weight: bold; }}
            code {{ background: #f4f4f4; padding: 2px 4px; font-size: 13px; }}
            pre {{ background: #f4f4f4; padding: 6px; margin: 4px 0; font-size: 13px; line-height: 1.2; }}
            table {{ border-collapse: collapse; width: 100%; margin: 5px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 4px; font-size: 13px; line-height: 1.2; }}
            th {{ background: #f0f0f0; font-weight: bold; }}
        </style></head><body>{html}</body></html>"""


        with open(filepath, "wb") as f:
            pisa.CreatePDF(styled_html, dest=f)
        st.sidebar.success(f"Saved to {filename}")
    else:
        st.sidebar.warning("No assistant message to export")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"].replace("$", "\\$"))


query = st.chat_input("Ask anything...")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        tool_container = st.container()

        placeholder = st.empty()
        full_response = ""

        # receive server response
        #
        #
        with httpx.Client(timeout=None) as client:
            with client.stream(
                "POST",
                "http://localhost:8002/chat_stream",
                json={"query": query, "thread_id": thread_id},
            ) as response:
                for line in response.iter_lines():
                    if not line.strip():
                        continue

                    chunk = json.loads(line)

                    msg_type = chunk.get("type", "")
                    content = chunk.get("content", "")

                    if chunk.get("tool_calls"):
                        for tc in chunk["tool_calls"]:
                            with tool_container:
                                st.status(f"🔧 {tc['name']}", state="complete").write(
                                    f"```json\n{json.dumps(tc['args'], indent=2)}\n```"
                                )

                    if content and "AI" in msg_type:
                        full_response = full_response + content
                        placeholder.markdown(full_response.replace("$", "\\$"))
                    # st.write(chunk)

        # placeholder.markdown(full_response.replace("$", "\\$"))

    st.session_state.messages.append({"role": "assistant", "content": full_response})
