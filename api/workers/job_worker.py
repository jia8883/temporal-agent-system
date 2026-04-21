import asyncio

from temporalio.worker import Worker

from api.utils.temporal_client import get_temporal_client
from api.workflows.job_workflow import JobWorkflow
from api.activities.job_activity import process_batch_activity
from api.utils.temporal_ready import wait_for_temporal_ready


async def main():
    # Connect to Temporal server
    client = await get_temporal_client()

    print("Connected to Temporal")

    await wait_for_temporal_ready(client)

    # Register workflow and activity to worker
    worker = Worker(
        client,
        task_queue="job-task-queue",  
        workflows=[JobWorkflow],
        activities=[process_batch_activity],
    )

    print("Job Worker started. Waiting for tasks...")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())