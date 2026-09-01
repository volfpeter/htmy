from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from htmy import ErrorBoundary, Fragment, SafeStr, WithContext, component, html

if TYPE_CHECKING:
    from htmy import Component, ComponentType, Context
    from htmy.renderer.typing import RendererType


# -- Utils


class WrapAsync:
    def __init__(self, *children: ComponentType) -> None:
        self.children = children

    async def htmy(self, context: Context) -> Component:
        return self.children


class Nested:
    def __init__(self, *children: ComponentType) -> None:
        self.children = children

    def htmy(self, context: Context) -> Component:
        return html.div(
            "Foo",
            html.div("bar"),
            Fragment(
                html.div(
                    WrapAsync("Before error", html.div(*self.children), "After error"),
                )
            ),
        )


def sync_async_divs(i: int) -> Fragment:
    return Fragment(html.div(f"Sync {i}", " ", "end"), WrapAsync(html.div(f"Async {i}", " ", "end")))


class SyncReturnsNone:
    def htmy(self, context: Context) -> Component:
        return None


class AsyncReturnsNone:
    async def htmy(self, context: Context) -> Component:
        return None


# -- Sync and async page.


@component
def page(content: ComponentType, context: Context) -> Component:
    return (
        html.DOCTYPE.html,
        html.html(
            html.head(
                html.title("Test page"),
                html.Meta.charset(),
                None,
                SyncReturnsNone(),
                html.Meta.viewport(),
                None,
                None,
                html.script(src="https://cdn.tailwindcss.com"),
                SyncReturnsNone(),
                AsyncReturnsNone(),
                html.Link.css("https://cdn.jsdelivr.net/npm/daisyui@4.12.11/dist/full.min.css"),
            ),
            html.body(
                content,
                class_="h-screen w-screen",
            ),
            lang="en",
        ),
    )


@component
async def a_page(content: ComponentType, context: Context) -> Component:
    return (
        html.DOCTYPE.html,
        html.html(
            html.head(
                html.title("Test page"),
                html.Meta.charset(),
                None,
                AsyncReturnsNone(),
                html.Meta.viewport(),
                None,
                None,
                html.script(src="https://cdn.tailwindcss.com"),
                SyncReturnsNone(),
                AsyncReturnsNone(),
                html.Link.css("https://cdn.jsdelivr.net/npm/daisyui@4.12.11/dist/full.min.css"),
            ),
            html.body(
                content,
                class_="h-screen w-screen",
            ),
            lang="en",
        ),
    )


# -- Sync and async error components.


class SyncError:
    def htmy(self, context: Context) -> Component:
        raise ValueError("sync-error-component")


class AsyncError:
    async def htmy(self, context: Context) -> Component:
        raise ValueError("async-error-component")


# -- Sync and async context providers.


class SyncContextProvider:
    def __init__(self, *children: ComponentType) -> None:
        self.children = children

    def htmy_context(self) -> Context:
        return {"marker": "sync-provider"}

    def htmy(self, context: Context) -> Component:
        return (html.p("sync-provider", data_marker=context["marker"]), *self.children)


class AsyncContextProvider:
    def __init__(self, *children: ComponentType) -> None:
        self.children = children

    async def htmy_context(self) -> Context:
        return {"marker": "async-provider"}

    def htmy(self, context: Context) -> Component:
        return (html.p("async-provider", data_marker=context["marker"]), *self.children)


@component.context_only
def context_marker(context: Context) -> Component:
    return html.span("context-marker", data_marker=context.get("marker"))


# -- Tests


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("component",),
    (
        # -- Render a component sequence directly.
        ([Nested(sync_async_divs(i)) for i in range(100)],),
        # -- Render a larger, nested component tree.
        (page(Fragment(*[Nested(sync_async_divs(i)) for i in range(100)])),),
        # -- Error boundary
        (Nested(ErrorBoundary(Nested(SyncError()), fallback="Fallback to sync error.")),),
        (Nested(ErrorBoundary(Nested(AsyncError()), fallback="Fallback to async error.")),),
        # -- Context providers, escaping, and empty/None components.
        (
            Nested(
                WithContext(
                    SyncContextProvider(context_marker()),
                    AsyncContextProvider(context_marker()),
                    context_marker(),
                    context={"marker": "wrapped"},
                ),
                "escaped < text &",
                SafeStr("safe < text &"),
                None,
                Fragment(),
                WrapAsync(None, html.em("async child")),
                SyncReturnsNone(),
                AsyncReturnsNone(),
            ),
        ),
    ),
)
async def test_renderers(
    *,
    component: Component,
    default_renderer: RendererType,
    baseline_renderer: RendererType,
    streaming_renderer: RendererType,
    rs_renderer: RendererType,
) -> None:
    default_renderer_result = await default_renderer.render(component)
    baseline_renderer_result = await baseline_renderer.render(component)
    streaming_renderer_result = await streaming_renderer.render(component)
    rs_renderer_result = await rs_renderer.render(component)
    assert default_renderer_result == baseline_renderer_result
    assert streaming_renderer_result == baseline_renderer_result
    assert rs_renderer_result == baseline_renderer_result


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("component", "expected"),
    (
        (None, ""),
        (SyncReturnsNone(), ""),
        (AsyncReturnsNone(), ""),
        ((SyncReturnsNone(), "text", AsyncReturnsNone()), "text"),
    ),
)
async def test_none_components_render_nothing(
    *,
    component: Component,
    expected: str,
    default_renderer: RendererType,
    baseline_renderer: RendererType,
    streaming_renderer: RendererType,
    rs_renderer: RendererType,
) -> None:
    """`None` components must not raise and must not render anything."""
    for renderer in (default_renderer, baseline_renderer, streaming_renderer, rs_renderer):
        assert await renderer.render(component) == expected


@pytest.mark.anyio
@pytest.mark.parametrize(
    "component",
    (
        123,
        # Sequences are not valid tag children, only components may return them.
        html.div(["a", "b"]),  # type: ignore[arg-type]
    ),
)
async def test_invalid_component_raises_value_error(
    *,
    component: Component,
    default_renderer: RendererType,
    baseline_renderer: RendererType,
    streaming_renderer: RendererType,
    rs_renderer: RendererType,
) -> None:
    for renderer in (default_renderer, baseline_renderer, streaming_renderer, rs_renderer):
        with pytest.raises(ValueError, match="Invalid component type"):
            await renderer.render(component)
