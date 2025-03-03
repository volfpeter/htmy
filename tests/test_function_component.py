import asyncio
from datetime import date
from time import perf_counter

import pytest

from htmy import Component, Context, Renderer, component, html
from htmy.renderer import BaselineRenderer

async_delay = 0.16
rendering_context: Context = {"date": date(2025, 3, 14)}
message = "Hello, world!"
date_string = rendering_context["date"].isoformat()
date_and_message = f"<p >{date_string}: {message}</p>"

# -- Function components.


@component
def sync_function_component(msg: str, ctx: Context) -> html.p:
    dt: date = ctx["date"]
    return html.p(dt.isoformat(), ": ", msg)


@component
async def async_function_component(msg: str, ctx: Context) -> html.p:
    await asyncio.sleep(async_delay)
    dt: date = ctx["date"]
    return html.p(dt.isoformat(), ": ", msg)


# -- Function components using function alias.


@component.function
def sync_function_component_with_function_alias(msg: str, ctx: Context) -> html.p:
    dt: date = ctx["date"]
    return html.p(dt.isoformat(), ": ", msg)


@component.function
async def async_function_component_with_function_alias(msg: str, ctx: Context) -> html.p:
    await asyncio.sleep(async_delay)
    dt: date = ctx["date"]
    return html.p(dt.isoformat(), ": ", msg)


# -- Context-only function components.


@component.context_only
def sync_context_only_function_component(ctx: Context) -> html.p:
    dt: date = ctx["date"]
    return html.p(dt.isoformat(), ": ", message)


@component.context_only
async def async_context_only_function_component(ctx: Context) -> html.p:
    await asyncio.sleep(async_delay)
    dt: date = ctx["date"]
    return html.p(dt.isoformat(), ": ", message)


@pytest.fixture(scope="session")
def renderer() -> Renderer:
    return Renderer(rendering_context)


@pytest.fixture(scope="session")
def baseline_renderer() -> BaselineRenderer:
    return BaselineRenderer(rendering_context)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("comp", "expected", "min_duration"),
    (
        # -- Function component
        (
            sync_function_component(message),
            date_and_message,
            0,
        ),
        (
            async_function_component(message),
            date_and_message,
            async_delay,
        ),
        (
            sync_function_component_with_function_alias(message),
            date_and_message,
            0,
        ),
        (
            async_function_component_with_function_alias(message),
            date_and_message,
            async_delay,
        ),
        # -- Context-only function component with call signature.
        (
            sync_context_only_function_component(),
            date_and_message,
            0,
        ),
        (
            async_context_only_function_component(),
            date_and_message,
            async_delay,
        ),
        # -- Context-only function component without call signature.
        (
            sync_context_only_function_component,
            date_and_message,
            0,
        ),
        (
            async_context_only_function_component,
            date_and_message,
            async_delay,
        ),
    ),
)
async def test_function_component(
    renderer: Renderer,
    baseline_renderer: BaselineRenderer,
    comp: Component,
    expected: str,
    min_duration: float,
) -> None:
    t_start = perf_counter()
    assert await renderer.render(comp) == expected
    # Test that async calls in async components are awaited.
    assert perf_counter() - t_start >= min_duration

    t_start = perf_counter()
    assert await baseline_renderer.render(comp) == expected
    # Test that async calls in async components are awaited.
    assert perf_counter() - t_start >= min_duration
