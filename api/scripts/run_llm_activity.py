import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api.activities.agent_activity import call_llm_activity


async def test():
    messages = [
        {"role": "system", "content": "You are a helpful agent."},
        {"role": "user", "content": "Find information about OpenAI"}
    ]

    result = await call_llm_activity(messages)
    print(result)


if __name__ == "__main__":
    asyncio.run(test())