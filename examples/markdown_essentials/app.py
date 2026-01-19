import anyio

from htmy import Renderer, md


async def render_post() -> None:
    md_post = md.MD("post.md")  # Create an htmy.md.MD component.
    rendered = await Renderer().render(md_post)  # Render the MD component.
    print(rendered)  # Print the result.


if __name__ == "__main__":
    anyio.run(render_post)
