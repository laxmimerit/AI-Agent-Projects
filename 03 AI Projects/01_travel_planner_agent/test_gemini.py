"""Test Gemini API connectivity without tools."""
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import asyncio

async def test_basic_gemini():
    print("Testing basic Gemini API call...")
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

    try:
        result = await asyncio.wait_for(
            model.ainvoke([HumanMessage(content="Say hello in one sentence.")]),
            timeout=30.0
        )
        print(f"✓ Success! Response: {result.content}")
        return True
    except asyncio.TimeoutError:
        print("✗ Failed: API call timed out")
        return False
    except Exception as e:
        print(f"✗ Failed: {type(e).__name__}: {str(e)}")
        return False

async def test_gemini_with_one_tool():
    print("\nTesting Gemini API with 1 simple tool...")
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

    from langchain_core.tools import tool

    @tool
    def get_weather(location: str) -> str:
        """Get weather for a location."""
        return f"Weather in {location}: Sunny, 25°C"

    model_with_tool = model.bind_tools([get_weather])

    try:
        result = await asyncio.wait_for(
            model_with_tool.ainvoke([HumanMessage(content="What's the weather in Mumbai?")]),
            timeout=30.0
        )
        print(f"✓ Success! Response: {result.content}")
        if hasattr(result, 'tool_calls') and result.tool_calls:
            print(f"  Tool calls requested: {result.tool_calls}")
        return True
    except asyncio.TimeoutError:
        print("✗ Failed: API call timed out")
        return False
    except Exception as e:
        print(f"✗ Failed: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GEMINI API CONNECTIVITY TEST")
    print("=" * 60)

    asyncio.run(test_basic_gemini())
    asyncio.run(test_gemini_with_one_tool())

    print("\n" + "=" * 60)
    print("If both tests passed, the issue is with tool loading/quantity")
    print("If tests failed, check your GOOGLE_API_KEY in .env")
    print("=" * 60)
