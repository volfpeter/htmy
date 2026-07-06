from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, Protocol, TypeAlias

import anyio
from markupsafe import Markup

from .core import ContextAware, SafeStr
from .renderer.context import RendererContext
from .typing import Component, Context

JinjaContextFactory: TypeAlias = Callable[[Context], Mapping[str, Any]]
"""A function that builds additional Jinja context entries from an `htmy` rendering context."""

if TYPE_CHECKING:
    from jinja2 import Template


class JinjaTemplateSource(Protocol):
    """Protocol for Jinja2 template sources such as `jinja2.Environment`."""

    def get_template(self, name: str) -> Template:
        """Returns the Jinja2 template with the given name."""
        ...


class JinjaTemplates(ContextAware):
    """
    Context-aware Jinja2 template source that can be placed in the `htmy` rendering context.

    The `JinjaTemplate` component looks up the `JinjaTemplates` instance from the `htmy` rendering
    context to find and render templates.
    """

    __slots__ = ("_source",)

    def __init__(self, source: JinjaTemplateSource) -> None:
        """
        Initialization.

        Arguments:
            source: A Jinja2 template source, e.g. a `jinja2.Environment` instance.
        """
        self._source = source

    @property
    def source(self) -> JinjaTemplateSource:
        """The wrapped Jinja2 template source."""
        return self._source

    def get_template(self, name: str) -> Template:
        """Returns the Jinja2 template with the given name."""
        return self._source.get_template(name)


class DefaultSlots(ContextAware):
    """
    Context-aware holder of default named slots for `JinjaTemplate`.

    The `JinjaTemplate` component looks up the `DefaultSlots` instance from the `htmy` rendering
    context. If found, `JinjaTemplate` renders each slot and passes the rendered values as
    `markupsafe.Markup` strings to the Jinja template.
    """

    __slots__ = ("_slots",)

    def __init__(self, slots: Mapping[str, Component] | None = None) -> None:
        """
        Initialization.

        Arguments:
            slots: Optional mapping of slot names to `htmy` components.
        """
        self._slots = {} if slots is None else slots

    @property
    def slots(self) -> Mapping[str, Component]:
        """Mapping of slot names to `htmy` components."""
        return self._slots


class JinjaTemplate:
    """
    Component that renders a Jinja2 template.

    The template source (a `JinjaTemplates` instance) must be in the `htmy` rendering context.
    The looked up template source is used to load and render the template.

    If a `DefaultSlots` instance is found in the `htmy` rendering context, its slots are rendered
    and included in the `slots` context variable passed to Jinja. `slots` passed directly to this
    component take precedence over `DefaultSlots` slots when both contain a slot with the same name.

    Jinja context creation precedence: `jinja_context`, `_build_context()`, `make_context`, and
    finally the reserved `slots` key.
    """

    __slots__ = ("_jinja_context", "_make_context", "_slots", "_template_name")

    def __init__(
        self,
        template_name: str,
        *,
        jinja_context: Mapping[str, Any] | None = None,
        make_context: JinjaContextFactory | None = None,
        slots: Mapping[str, Component] | None = None,
    ) -> None:
        """
        Initialization.

        Arguments:
            template_name: The name of the template to render.
            jinja_context: Optional mapping passed to Jinja as the template context.
            make_context: Optional callable that receives the `htmy` rendering context and
                returns additional Jinja context entries. It runs after `_build_context()`,
                but before slot rendering, so it can not override the reserved `slots` key.
            slots: Optional named slots to be rendered in the template. Values are `htmy` components,
                they are rendered before being passed to Jinja as `markupsafe.Markup` to avoid
                double-escaping, content is not re-escaped by Jinja's autoescape. Slots are available
                through the `slots` key in the Jinja context and accessed as `{{ slots.<name> }}`.
        """
        self._template_name = template_name
        self._jinja_context = jinja_context
        self._make_context = make_context
        self._slots = slots

    def _build_context(self, htmy_context: Context, /) -> dict[str, Any]:
        """
        Returns the Jinja rendering context for this component.

        The returned dictionary is owned by the caller, so it can be modified in place.

        Arguments:
            htmy_context: The `htmy` rendering context.
        """
        return {} if self._jinja_context is None else dict(self._jinja_context)

    async def htmy(self, context: Context) -> Component:
        """Renders the component."""
        templates = JinjaTemplates.from_context(context)
        renderer = RendererContext.from_context(context)
        default_slots = DefaultSlots.from_context(context, None)

        template = templates.get_template(self._template_name)
        slots: dict[str, Markup] = {}

        jinja_context = self._build_context(context)
        if self._make_context is not None:
            jinja_context.update(self._make_context(context))

        if default_slots is not None:
            for name, component in default_slots.slots.items():
                slots[name] = Markup(await renderer.render(component, context))  # noqa: S704

        if self._slots is not None:
            for name, component in self._slots.items():
                slots[name] = Markup(await renderer.render(component, context))  # noqa: S704

        if len(slots) > 0:
            jinja_context["slots"] = slots

        if template.environment.is_async:
            rendered = await template.render_async(**jinja_context)
        else:
            rendered = await anyio.to_thread.run_sync(lambda: template.render(**jinja_context))

        return SafeStr(rendered)
