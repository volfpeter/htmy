from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, Protocol, TypeAlias, overload

from .typing import AsyncComponent, Component, Context, SyncComponent, T

# -- Typing for "full" function components.

_SyncFunctionComponent: TypeAlias = Callable[[T, Context], Component]
"""
Protocol definition for sync function components that have both a properties and a context argument.
"""

_AsyncFunctionComponent: TypeAlias = Callable[[T, Context], Coroutine[Any, Any, Component]]
"""
Protocol definition for async function components that have both a properties and a context argument.
"""

_FunctionComponent: TypeAlias = _SyncFunctionComponent[T] | _AsyncFunctionComponent[T]
"""
Function component type that has both a properties and a context argument.
"""

# -- Typing for context-only function components.

_ContextOnlySyncFunctionComponent: TypeAlias = Callable[[Context], Component]
"""
Protocol definition for sync function components that only have a context argument.
"""


class _DecoratedContextOnlySyncFunctionComponent(SyncComponent, Protocol):
    """
    Protocol definition for sync components that are also callable, and return a sync
    component when called.
    """

    def __call__(self) -> SyncComponent: ...


_ContextOnlyAsyncFunctionComponent: TypeAlias = Callable[[Context], Coroutine[Any, Any, Component]]
"""
Protocol definition for async function components that only have a context argument.
"""


class _DecoratedContextOnlyAsyncFunctionComponent(SyncComponent, Protocol):
    """
    Protocol definition for async components that are also callable, and return an async
    component when called.
    """

    def __call__(self) -> SyncComponent: ...


_ContextOnlyFunctionComponent: TypeAlias = (
    _ContextOnlySyncFunctionComponent | _ContextOnlyAsyncFunctionComponent
)
"""
Function component type that only accepts a context argument.
"""

_DecoratedContextOnlyFunction: TypeAlias = (
    _DecoratedContextOnlySyncFunctionComponent | _DecoratedContextOnlyAsyncFunctionComponent
)
"""
Protocol definition for sync or async components that are also callable, and return a sync
or async component when called.
"""


class ComponentDecorators:
    """
    Function component decorators.
    """

    __slots__ = ()

    # -- FunctionComponent decorator.

    @overload
    def __call__(self, func: _SyncFunctionComponent[T]) -> Callable[[T], SyncComponent]: ...

    @overload
    def __call__(self, func: _AsyncFunctionComponent[T]) -> Callable[[T], AsyncComponent]: ...

    def __call__(
        self,
        func: _FunctionComponent[T],
    ) -> Callable[[T], SyncComponent] | Callable[[T], AsyncComponent]:
        """
        Decorator that converts the decorated function into one that must be called with
        the function component's properties and returns a component instance.

        If used on an async function, the resulting component will also be async;
        otherwise it will be sync.

        Example:

        ```python
        @component
        def my_component(props: int, context: Context) -> Component:
            return html.p(f"Value: {props}")

        async def render():
           return await Renderer().render(
               my_component(42)
           )
        ```

        Arguments:
            func: The decorated function.

        Returns:
            A function that must be called with the function component's properties and
            returns a component instance. (Or loosly speaking, an `HTMYComponentType` which
            can be "instantiated" with the function component's properties.)
        """

        if asyncio.iscoroutinefunction(func):

            def async_wrapper(props: T) -> AsyncComponent:
                # This function must be async, in case the renderer inspects it to decide how to handle it.
                async def component(context: Context) -> Component:
                    return await func(props, context)  # type: ignore[no-any-return]

                component.htmy = component  # type: ignore[attr-defined]
                return component  # type: ignore[return-value]

            return async_wrapper
        else:

            def sync_wrapper(props: T) -> SyncComponent:
                def component(context: Context) -> Component:
                    return func(props, context)  # type: ignore[return-value]

                component.htmy = component  # type: ignore[attr-defined]
                return component  # type: ignore[return-value]

            return sync_wrapper

    @overload
    def function(self, func: _SyncFunctionComponent[T]) -> Callable[[T], SyncComponent]: ...

    @overload
    def function(self, func: _AsyncFunctionComponent[T]) -> Callable[[T], AsyncComponent]: ...

    def function(
        self,
        func: _FunctionComponent[T],
    ) -> Callable[[T], SyncComponent] | Callable[[T], AsyncComponent]:
        """
        Decorator that converts the decorated function into one that must be called with
        the function component's properties and returns a component instance.

        If used on an async function, the resulting component will also be async;
        otherwise it will be sync.

        This function is just an alias for `__call__()`.

        Example:

        ```python
        @component.function
        def my_component(props: int, context: Context) -> Component:
            return html.p(f"Value: {props}")

        async def render():
           return await Renderer().render(
               my_component(42)
           )

        Arguments:
            func: The decorated function.

        Returns:
            A function that must be called with the function component's properties and
            returns a component instance. (Or loosly speaking, an `HTMYComponentType` which
            can be "instantiated" with the function component's properties.)
        """
        return self(func)

    # -- ContextOnlyFunctionComponent decorator.

    @overload
    def context_only(
        self, func: _ContextOnlySyncFunctionComponent
    ) -> _DecoratedContextOnlySyncFunctionComponent: ...

    @overload
    def context_only(
        self, func: _ContextOnlyAsyncFunctionComponent
    ) -> _DecoratedContextOnlyAsyncFunctionComponent: ...

    def context_only(
        self,
        func: _ContextOnlyFunctionComponent,
    ) -> _DecoratedContextOnlySyncFunctionComponent | _DecoratedContextOnlyAsyncFunctionComponent:
        """
        Decorator that converts the decorated function into a component.

        If used on an async function, the resulting component will also be async;
        otherwise it will be sync.

        The decorated function will be both a component object and a callable that returns a
        component object, so it can be used in the component tree both with and without the
        call signature:

        ```python
        @component.context_only
        def my_component(ctx):
            return "Context only function component."

        async def render():
           return await Renderer().render(
               my_component(),  # With call signature.
               my_component,  # Without call signature.
           )
        ```

        Arguments:
            func: The decorated function.

        Returns:
            The created component.
        """

        def wrapper() -> SyncComponent | AsyncComponent:
            func.htmy = func  # type: ignore[union-attr]
            return func  # type: ignore[return-value]

        wrapper.htmy = func  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]


component = ComponentDecorators()
"""
Decorators for converting functions into components

This is an instance of `ComponentDecorators`.
"""
