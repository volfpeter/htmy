from .baseline import Renderer as _BaselineRenderer
from .default import Renderer as _DefaultRenderer
from .typing import is_renderer as is_renderer
from .typing import is_streaming_renderer as is_streaming_renderer

Renderer = _DefaultRenderer
"""The default renderer."""

StreamingRenderer = _BaselineRenderer
"""The default streaming renderer."""

BaselineRenderer = _BaselineRenderer
"""The baseline renderer."""
