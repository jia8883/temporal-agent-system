from temporalio import activity


def write_codes_to_promo_db(title: str, count: int):
    if count > 100:
        raise RuntimeError("The DB cannot write more than 100 codes at once")
    print(f"{count} promo codes with title [{title}] written to the Promo DB.")


@activity.defn
async def write_promo_activity(data: dict):

    print("[ACTIVITY] executing batch...")
    
    title = data["title"]
    count = data["count"]

    write_codes_to_promo_db(title, count)