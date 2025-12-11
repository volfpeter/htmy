from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from htmy import ErrorBoundary, Fragment, Renderer, component, html
from htmy.renderer import BaselineRenderer

if TYPE_CHECKING:
    from htmy import Component, ComponentType, Context

# -- Sync and async page.


@component
def page(content: ComponentType, context: Context) -> Component:
    return (
        html.DOCTYPE.html,
        html.html(
            html.head(
                html.title("Test page"),
                html.Meta.charset(),
                html.Meta.viewport(),
                html.script(src="https://cdn.tailwindcss.com"),
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
                html.Meta.viewport(),
                html.script(src="https://cdn.tailwindcss.com"),
                html.Link.css("https://cdn.jsdelivr.net/npm/daisyui@4.12.11/dist/full.min.css"),
            ),
            html.body(
                content,
                class_="h-screen w-screen",
            ),
            lang="en",
        ),
    )


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
    return Fragment(html.div(f"Sync {i}", " ", "end"), WrapAsync(html.div("Async {i}", " ", "end")))


# -- Sync and async error components.


class SyncError:
    def htmy(self, context: Context) -> Component:
        raise ValueError("sync-error-component")


class AsyncError:
    async def htmy(self, context: Context) -> Component:
        raise ValueError("async-error-component")


# -- Tests


@pytest.mark.asyncio
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
    ),
)
async def test_renderers(
    *,
    component: Component,
    default_renderer: Renderer,
    baseline_renderer: BaselineRenderer,
) -> None:
    default_renderer_result = await default_renderer.render(component)
    baseline_renderer_result = await baseline_renderer.render(component)
    assert default_renderer_result == baseline_renderer_result
