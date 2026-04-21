from temporalio import activity


def write_batch_to_db(title: str, count: int):
    if count > 100:
        raise RuntimeError("The DB cannot write more than 100 items at once")
    print(f"{count} items with job [{title}] written to the DB.")


@activity.defn
async def process_batch_activity(data: dict):

    print("[ACTIVITY] executing batch...")
    
    title = data["title"]
    count = data["count"]

    write_batch_to_db(title, count)