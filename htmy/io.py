from pathlib import Path

from anyio import open_file as open_file


async def load_text_file(path: str | Path) -> str:
    """Loads the text content from the given path."""
    async with await open_file(path, "r") as f:
        return await f.read()
