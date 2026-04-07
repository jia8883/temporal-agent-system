import asyncio

from temporalio.worker import Worker

from api.utils.temporal_client import get_temporal_client
from api.workflows.promo_workflow import PromoWorkflow
from api.activities.promo_activity import write_promo_activity
from api.utils.temporal_ready import wait_for_temporal_ready


async def main():
    # Connect to Temporal server
    client = await get_temporal_client()

    print("Connected to Temporal")

    await wait_for_temporal_ready(client)

    # Register workflow and activity to worker
    worker = Worker(
        client,
        task_queue="promo-task-queue",  
        workflows=[PromoWorkflow],
        activities=[write_promo_activity],
    )

    print("Promo Worker started. Waiting for tasks...")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())