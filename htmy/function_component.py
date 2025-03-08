from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, Protocol, TypeAlias, overload

from .typing import AsyncComponent, Component, Context, SyncComponent
from .typing import T as TProps
from .typing import U as TSelf

# -- Typing for "full" function components and context only method components.

_SyncFunctionComponent: TypeAlias = Callable[[TProps, Context], Component]
"""
Protocol definition for sync function components that have both a properties and a context argument.
"""

_AsyncFunctionComponent: TypeAlias = Callable[[TProps, Context], Coroutine[Any, Any, Component]]
"""
Protocol definition for async function components that have both a properties and a context argument.
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


# -- Typing for "full" method components.

_SyncMethodComponent: TypeAlias = Callable[[TSelf, TProps, Context], Component]
"""
Protocol definition for sync method components that have both a properties and a context argument.
"""

_AsyncMethodComponent: TypeAlias = Callable[[TSelf, TProps, Context], Coroutine[Any, Any, Component]]
"""
Protocol definition for async method components that have both a properties and a context argument.
"""


# -- Component decorators.


class ComponentDecorators:
    """
    Function component decorators.
    """

    __slots__ = ()

    # -- Function component decorator.

    @overload
    def __call__(self, func: _SyncFunctionComponent[TProps]) -> Callable[[TProps], SyncComponent]: ...

    @overload
    def __call__(self, func: _AsyncFunctionComponent[TProps]) -> Callable[[TProps], AsyncComponent]: ...

    def __call__(
        self,
        func: _SyncFunctionComponent[TProps] | _AsyncFunctionComponent[TProps],
    ) -> Callable[[TProps], SyncComponent] | Callable[[TProps], AsyncComponent]:
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

        async def render() -> str:
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

            def async_wrapper(props: TProps) -> AsyncComponent:
                # This function must be async, in case the renderer inspects it to decide how to handle it.
                async def component(context: Context) -> Component:
                    return await func(props, context)  # type: ignore[no-any-return]

                component.htmy = component  # type: ignore[attr-defined]
                return component  # type: ignore[return-value]

            return async_wrapper
        else:

            def sync_wrapper(props: TProps) -> SyncComponent:
                def component(context: Context) -> Component:
                    return func(props, context)  # type: ignore[return-value]

                component.htmy = component  # type: ignore[attr-defined]
                return component  # type: ignore[return-value]

            return sync_wrapper

    @overload
    def function(self, func: _SyncFunctionComponent[TProps]) -> Callable[[TProps], SyncComponent]: ...

    @overload
    def function(self, func: _AsyncFunctionComponent[TProps]) -> Callable[[TProps], AsyncComponent]: ...

    def function(
        self,
        func: _SyncFunctionComponent[TProps] | _AsyncFunctionComponent[TProps],
    ) -> Callable[[TProps], SyncComponent] | Callable[[TProps], AsyncComponent]:
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

        async def render() -> str:
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

    # -- Context-only function component decorator.

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
        func: _ContextOnlySyncFunctionComponent | _ContextOnlyAsyncFunctionComponent,
    ) -> _DecoratedContextOnlySyncFunctionComponent | _DecoratedContextOnlyAsyncFunctionComponent:
        """
        Decorator that converts the decorated function into a component.

        If used on an async function, the resulting component will also be async;
        otherwise it will be sync.

        Example:

        ```python
        @component.context_only
        def my_component(ctx):
            return "Context only function component."

        async def render() -> str:
           return await Renderer().render(
               my_component()
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

        # This assignment adds support for context-only function components without call signature.
        wrapper.htmy = func  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    # -- Method component decorator.

    @overload
    def method(
        self, func: _SyncMethodComponent[TSelf, TProps]
    ) -> Callable[[TSelf, TProps], SyncComponent]: ...

    @overload
    def method(
        self, func: _AsyncMethodComponent[TSelf, TProps]
    ) -> Callable[[TSelf, TProps], AsyncComponent]: ...

    def method(
        self,
        func: _SyncMethodComponent[TSelf, TProps] | _AsyncMethodComponent[TSelf, TProps],
    ) -> Callable[[TSelf, TProps], SyncComponent] | Callable[[TSelf, TProps], AsyncComponent]:
        """
        Decorator that converts the decorated method into one that must be called with
        the method component's properties and returns a component instance.

        If used on an async method, the resulting component will also be async;
        otherwise it will be sync.

        Example:

        ```python
        @dataclass
        class MyBusinessObject:
            message: str

            @component.method
            def paragraph(self, props: int, context: Context) -> Component:
                return html.p(f"{self.message} {props}")


        async def render() -> str:
            return await Renderer().render(
                MyBusinessObject("Hi!").paragraph(42)
            )
        ```

        Arguments:
            func: The decorated method.

        Returns:
            A method that must be called with the method component's properties and
            returns a component instance. (Or loosly speaking, an `HTMYComponentType` which
            can be "instantiated" with the method component's properties.)
        """
        if asyncio.iscoroutinefunction(func):

            def async_wrapper(self: TSelf, props: TProps) -> AsyncComponent:
                # This function must be async, in case the renderer inspects it to decide how to handle it.
                async def component(context: Context) -> Component:
                    return await func(self, props, context)  # type: ignore[no-any-return]

                component.htmy = component  # type: ignore[attr-defined]
                return component  # type: ignore[return-value]

            return async_wrapper
        else:

            def sync_wrapper(self: TSelf, props: TProps) -> SyncComponent:
                def component(context: Context) -> Component:
                    return func(self, props, context)  # type: ignore[return-value]

                component.htmy = component  # type: ignore[attr-defined]
                return component  # type: ignore[return-value]

            return sync_wrapper

    # -- Context-only function component decorator.

    @overload
    def context_only_method(
        self, func: _SyncFunctionComponent[TSelf]
    ) -> Callable[[TSelf], SyncComponent]: ...

    @overload
    def context_only_method(
        self, func: _AsyncFunctionComponent[TSelf]
    ) -> Callable[[TSelf], AsyncComponent]: ...

    def context_only_method(
        self,
        func: _SyncFunctionComponent[TSelf] | _AsyncFunctionComponent[TSelf],
    ) -> Callable[[TSelf], SyncComponent] | Callable[[TSelf], AsyncComponent]:
        """
        Decorator that converts the decorated method into one that must be called
        without any arguments and returns a component instance.

        If used on an async method, the resulting component will also be async;
        otherwise it will be sync.

        Example:

        ```python
        @dataclass
        class MyBusinessObject:
            message: str

            @component.context_only_method
            def paragraph(self, context: Context) -> Component:
                return html.p(f"{self.message} Goodbye!")


        async def render() -> str:
            return await Renderer().render(
                MyBusinessObject("Hello!").paragraph()
            )
        ```

        Arguments:
            func: The decorated method.

        Returns:
            A method that must be called without any arguments and returns a component instance.
            (Or loosly speaking, an `HTMYComponentType` which can be "instantiated" by calling
            the method.)
        """
        # A context only method component must be implemented in the same way as
        # a function component. The self argument replaces the props argument
        # and it is added automatically by Python when the method is called.
        # Even the type hint must be the same.
        # This implementation doesn't make the function itself a component though,
        # so the call signature is always necessary (unlike for context-only function
        # components).
        return self(func)


component = ComponentDecorators()
"""
Decorators for converting functions into components

This is an instance of `ComponentDecorators`.
"""
