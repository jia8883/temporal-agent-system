import asyncio

async def wait_for_temporal_ready(client):
    for i in range(20):
        try:
            async for _ in client.list_workflows(""):
                break

            print("Temporal ready")
            return

        except Exception as e:
            print(f"Waiting for Temporal... ({i+1}/20) {e}")
            await asyncio.sleep(2)

    raise RuntimeError("Temporal not ready")