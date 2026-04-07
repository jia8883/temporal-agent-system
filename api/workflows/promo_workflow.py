from temporalio import workflow
from datetime import timedelta
from api.activities.promo_activity import write_promo_activity


@workflow.defn
class PromoWorkflow:

    def __init__(self):
        self.queue = []
        self.status = "idle"
        self.paused = False

    @workflow.run
    async def run(self):
        while True:
            
            print("[WORKFLOW] processing...")

            if self.paused:
                self.status = "paused"
                await workflow.sleep(1)
                continue

            if not self.queue:
                self.status = "idle"
                await workflow.sleep(1)
                continue

            self.status = "running"

            item = self.queue.pop(0)
            title = item["title"]
            count = item["count"]

            remaining = count

            while remaining > 0:

                if self.paused:
                    break

                batch = min(100, remaining)

                await workflow.execute_activity(
                    write_promo_activity,
                    {
                        "title": title,
                        "count": batch
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                )

                remaining -= batch

                await workflow.sleep(10)

    @workflow.signal
    def add_request(self, data: dict):
        self.queue.append(data)

    @workflow.signal
    def pause(self):
        self.paused = True

    @workflow.signal
    def resume(self):
        self.paused = False

    @workflow.signal
    def discard(self):
        self.queue = []

    @workflow.query
    def get_status(self):
        return self.status