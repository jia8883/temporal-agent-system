import os
import httpx
import json
from typing import List, Dict, Any

from temporalio import activity
from openai import OpenAI


# OpenRouter client configuration
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


@activity.defn
async def call_llm_activity(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calls the LLM with function (tool) calling enabled.

    Returns:
        - {"type": "tool_call", ...} if LLM requests a tool
        - {"type": "final", ...} if LLM returns a final answer
    """

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",  
        messages=messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ],
        tool_choice="auto",  # Let the LLM decide whether to use a tool
    )

    msg = response.choices[0].message

    # If the LLM requests a tool call, return structured tool call info
    if msg.tool_calls:
        return {
            "type": "tool_call",
            "tool_name": msg.tool_calls[0].function.name,
            "arguments": msg.tool_calls[0].function.arguments,
        }

    # Otherwise, return final response
    return {
        "type": "final",
        "content": msg.content,
    }


FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

@activity.defn
async def web_search_activity(query: str) -> str:
    """
    Executes a web search using Firecrawl API and formats results
    into a string suitable for LLM input.
    """

    url = "https://api.firecrawl.dev/v1/search"

    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "limit": 5,  
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Firecrawl error: {response.text}")

    data = response.json()

    # Convert search results into a readable format for LLM
    results = []

    for item in data.get("data", []):
        title = item.get("title", "")
        url = item.get("url", "")
        snippet = item.get("description", "")

        results.append(f"{title}\n{url}\n{snippet}")

    return "\n\n".join(results)


@activity.defn
async def run_tool_activity(input: dict) -> str:
    """
    Dispatches tool execution based on tool name.

    Args:
        input: {
            "tool_name": str,
            "arguments": str (JSON string)
        }
    """

    tool_name = input.get("tool_name")
    arguments = input.get("arguments")

    if not tool_name:
        raise ValueError("Missing 'tool_name'")

    if not arguments:
        raise ValueError("Missing 'arguments'")

    # Parse arguments
    args = json.loads(arguments)

    if tool_name == "web_search":
        query = args.get("query")

        if not query:
            raise ValueError("Missing 'query' in web_search arguments")

        return await web_search_activity(query)

    raise ValueError(f"Unknown tool: {tool_name}")