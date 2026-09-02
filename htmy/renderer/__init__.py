from typing import TYPE_CHECKING

from .baseline import Renderer as _BaselineRenderer
from .typing import is_renderer as is_renderer
from .typing import is_streaming_renderer as is_streaming_renderer

# Replace _DefaultRenderer with its Rust-based counterpart if it is available.
if TYPE_CHECKING:
    from .default import Renderer as _DefaultRenderer
else:
    try:
        from htmy_rs.renderer import Renderer as _DefaultRenderer
    except ImportError:
        from .default import Renderer as _DefaultRenderer

Renderer = _DefaultRenderer
"""The default renderer."""

StreamingRenderer = _BaselineRenderer
"""The default streaming renderer."""

BaselineRenderer = _BaselineRenderer
"""The baseline renderer."""
