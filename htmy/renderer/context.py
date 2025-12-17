from htmy.typing import Context

from .typing import RendererType, is_renderer


class RendererContext:
    """
    Context key for storing, and utility for retrieving the renderer instance from the rendering context.
    """

    @classmethod
    def from_context(cls, context: Context) -> RendererType:
        """
        Returns the renderer instance from the given context.

        Arguments:
            context: The context the renderer instance should be loaded from.

        Raises:
            KeyError: If no renderer instance was found in the context.
            TypeError: If the value corresponding to `RendererContext` in the context is not a renderer.
        """
        renderer = context[cls]

        if not is_renderer(renderer):
            raise TypeError("The value corresponding to RendererContext in the context must be a renderer.")

        return renderer
