__version__ = "0.10.0"

from .core import ContextAware as ContextAware
from .core import Formatter as Formatter
from .core import Fragment as Fragment
from .core import SafeStr as SafeStr
from .core import SkipProperty as SkipProperty
from .core import Text as Text
from .core import WithContext as WithContext
from .core import XBool as XBool
from .core import xml_format_string as xml_format_string
from .error_boundary import ErrorBoundary as ErrorBoundary
from .function_component import component as component
from .renderer import Renderer as Renderer
from .renderer import StreamingRenderer as StreamingRenderer
from .renderer.typing import RendererType as RendererType
from .snippet import Slots as Slots
from .snippet import Snippet as Snippet
from .tag import Tag as Tag
from .tag import TagWithProps as TagWithProps
from .tag import wildcard_tag as wildcard_tag
from .typing import AsyncComponent as AsyncComponent
from .typing import AsyncContextProvider as AsyncContextProvider
from .typing import Component as Component
from .typing import ComponentSequence as ComponentSequence
from .typing import ComponentType as ComponentType
from .typing import Context as Context
from .typing import ContextKey as ContextKey
from .typing import ContextProvider as ContextProvider
from .typing import ContextValue as ContextValue
from .typing import HTMYComponentType as HTMYComponentType
from .typing import MutableContext as MutableContext
from .typing import Properties as Properties
from .typing import PropertyValue as PropertyValue
from .typing import StrictComponentType as StrictComponentType
from .typing import SyncComponent as SyncComponent
from .typing import SyncContextProvider as SyncContextProvider
from .utils import as_component_sequence as as_component_sequence
from .utils import as_component_type as as_component_type
from .utils import is_component_sequence as is_component_sequence
from .utils import join
from .utils import join_components as join_components

join_classes = join

HTMY = Renderer
"""Deprecated alias for `Renderer`."""
