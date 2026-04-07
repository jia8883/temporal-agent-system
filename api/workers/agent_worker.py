import asyncio

from temporalio.worker import Worker

from api.utils.temporal_client import get_temporal_client
from api.workflows.agent_workflow import AgentWorkflow
from api.activities.agent_activity import (
    call_llm_activity,
    web_search_activity,
    run_tool_activity,
)
from api.utils.temporal_ready import wait_for_temporal_ready


async def main():
    client = await get_temporal_client()

    print("Connected to Temporal (Agent Worker)")

    await wait_for_temporal_ready(client)

    worker = Worker(
        client,
        task_queue="agent-task-queue",
        workflows=[AgentWorkflow],
        activities=[
            call_llm_activity,
            web_search_activity,
            run_tool_activity,
        ],
    )

    print("Agent Worker started. Waiting for tasks...")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())