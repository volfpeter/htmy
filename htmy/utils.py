from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING:
    from .typing import Component, ComponentSequence, ComponentType


def join_components(
    components: ComponentSequence,
    separator: ComponentType,
    pad: bool = False,
) -> Generator[ComponentType, None, None]:
    """
    Joins the given components using the given separator.

    Arguments:
        components: The components to join.
        separator: The separator to use.
        pad: Whether to add a separator before the first and after the last components.
    """
    if len(components) == 0:
        return

    if pad:
        yield separator

    components_iterator = iter(components)
    yield next(components_iterator)

    for component in components_iterator:
        yield separator
        yield component

    if pad:
        yield separator


def join(*items: str | None, separator: str = " ") -> str:
    """
    Joins the given strings with the given separator, skipping `None` values.
    """
    return separator.join(i for i in items if i)


def is_component_sequence(comp: Component) -> TypeGuard[ComponentSequence]:
    """Returns whether the given component is a component sequence."""
    return isinstance(comp, (list, tuple))


def as_component_sequence(comp: Component) -> ComponentSequence:
    """Returns the given component as a component sequence."""
    # mypy doesn't understand the `is_component_sequence` type guard.
    return comp if is_component_sequence(comp) else (comp,)  # type: ignore[return-value]


def as_component_type(comp: Component) -> ComponentType:
    """Returns the given component as a `ComponentType` (not sequence)."""
    from .core import Fragment

    # mypy doesn't understand the `is_component_sequence` type guard.
    return comp if not is_component_sequence(comp) else Fragment(*comp)  # type: ignore[return-value]
