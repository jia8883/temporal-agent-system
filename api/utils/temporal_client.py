import asyncio
from temporalio.client import Client


async def get_temporal_client():
    for i in range(20):
        try:
            client = await Client.connect(
                "temporal:7233",
                namespace="default",
                )
            print("Connected to Temporal")
            return client
        except Exception as e:
            print(f"Retry {i+1}/20... {e}")
            await asyncio.sleep(2)

    raise Exception("Temporal connection failed")