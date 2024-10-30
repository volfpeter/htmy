import asyncio

from htmy import HTMY, md


async def render_post() -> None:
    md_post = md.MD("post.md")  # Create an htmy.md.MD component.
    rendered = await HTMY().render(md_post)  # Render the MD component.
    print(rendered)  # Print the result.


if __name__ == "__main__":
    asyncio.run(render_post())
