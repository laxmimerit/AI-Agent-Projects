"""
Utility functions for agent operations.
"""
from langchain.messages import HumanMessage, AIMessage, ToolMessage

def stream_agent_response(agent, query, thread_id=None):

    config = {'configurable': {'thread_id': thread_id}}
    state = {'messages': [HumanMessage(query)]}

    for chunk in agent.stream(state, stream_mode='updates', config=config):
        for node_name, messages in chunk.items():
            message = messages['messages'][0]
            # print(f'\n\nNode: {node_name}')
            # print(message)

            # Handle AI messages with tool calls
            if isinstance(message, AIMessage) and message.tool_calls:
                for tool_call in message.tool_calls:
                    print(f"\n  Tool Called: {tool_call['name']}")
                    print(f"   Args: {tool_call['args']}")
                    print()

            # Handle tool responses
            elif isinstance(message, ToolMessage):
                print(f"\n  Tool Response: {message.text[:50]}...")
                print(f"\n  Tool Result (length: {len(message.text)} chars)")
                print()


            # Handle AI text responses
            elif isinstance(message, AIMessage) and message.text:
                # Stream the text content
                print(message.text, end='', flush=True)

# stream_agent_response(agent, 'what is the weather in mumbai', '5_session_3')