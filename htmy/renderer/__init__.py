from .default import Renderer as _DefaultRenderer
from .recursive import Renderer as _RecursiveRenderer

Renderer = _DefaultRenderer
"""The default renderer."""

RecursiveRenderer = _RecursiveRenderer
"""A simple recursive renderer."""
