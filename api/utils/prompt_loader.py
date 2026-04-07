def load_prompt(name: str) -> str:
    with open(f"/app/prompts/{name}.txt", "r", encoding="utf-8") as f:
        return f.read().strip()