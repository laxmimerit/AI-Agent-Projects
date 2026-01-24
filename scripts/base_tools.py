import os
import json

from langchain.tools import tool
import ollama
import requests

# -------------------------
# MCP Config Loader
# -------------------------
def load_mcp_config(*server_names):
    """Load MCP server configurations from mcp_config.json.

    Args:
        *server_names: Names of servers to load (e.g., 'airbnb', 'google-calendar', 'google-sheets')

    Returns:
        dict: Dictionary of MCP server configurations

    Example:
        config = load_mcp_config('airbnb', 'google-calendar')
    """
    config_path = os.path.join(os.path.dirname(__file__), 'mcp_config.json')

    with open(config_path, 'r') as f:
        all_configs = json.load(f)

    if not server_names:
        return all_configs

    return {name: all_configs[name] for name in server_names if name in all_configs}


# -------------------------
# Web Search Tool
# -------------------------
# @tool('live_web_search', description='Perform live search using Ollama.')
@tool
def web_search(query: str):
    """
    Perform a live web search using Ollama Cloud Web Search API for real-time information and news.

    Input:
        query: search query string

    Output:
        JSON string of top results (max_results=2).
    """

    response = ollama.web_search(query=query, max_results=2)
    response = response.results

    return response


# -------------------------
# Weather Tool
# -------------------------
@tool
def get_weather(location: str):
    """Get current weather for a location using WeatherAPI.com.
    
    Use for queries about weather, temperature, or conditions in any city.
    Examples: "weather in Paris", "temperature in Tokyo", "is it raining in London"
    
    Args:
        location: City name (e.g., "New York", "London", "Tokyo")
        
    Returns:
        Current weather information including temperature and conditions.
    """

    url = f"http://api.weatherapi.com/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={location}&aqi=no"

    response = requests.get(url=url, timeout=10)
    response.raise_for_status()

    data = response.json()

    return data