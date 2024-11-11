import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, ClassVar, overload

from async_lru import alru_cache

from .core import ContextAware
from .io import open_file

TranslationResource = Mapping[str, Any]
"""Translation resource type."""


class I18nError(Exception): ...


class I18nKeyError(I18nError): ...


class I18nValueError(I18nError): ...


class I18n(ContextAware):
    """
    Context-aware async internationalization utility.
    """

    __slots__ = ("_path", "_fallback")

    _root_keys: ClassVar[frozenset[str]] = frozenset(("", "."))
    """Special keys that represent the "root" object, i.e. the entire translation resource file."""

    def __init__(self, path: str | Path, fallback: str | Path | None = None) -> None:
        """
        Initialization.

        Arguments:
            path: Path to the root directory that contains the translation resources.
            fallback: Optional fallback path to use if `path` doesn't contain the required resources.
        """
        self._path: Path = Path(path) if isinstance(path, str) else path
        self._fallback: Path | None = Path(fallback) if isinstance(fallback, str) else fallback

    @overload
    async def get(self, dotted_path: str, key: str) -> Any: ...

    @overload
    async def get(self, dotted_path: str, key: str, **kwargs: Any) -> str: ...

    async def get(self, dotted_path: str, key: str, **kwargs: Any) -> Any:
        """
        Returns the translation resource at the given location.

        If keyword arguments are provided, it's expected that the referenced data
        is a [format string](https://docs.python.org/3/library/string.html#formatstrings)
        which can be fully formatted using the given keyword arguments.

        Arguments:
            dotted_path: A package-like (dot separated) path to the file that contains
                the required translation resource, relative to `path`.
            key: The key in the translation resource whose value is requested. Use dots to reference
                embedded attributes.

        Returns:
            The loaded value.

        Raises:
            I18nError: If the given translation resource is not found or invalid.
        """
        try:
            return await self._resolve(self._path, dotted_path, key, **kwargs)
        except I18nError:
            if self._fallback is None:
                raise

            return await self._resolve(self._fallback, dotted_path, key, **kwargs)

    @classmethod
    async def _resolve(cls, root: Path, dotted_subpath: str, key: str, **kwargs: Any) -> Any:
        """
        Resolves the given translation resource.

        Arguments:
            root: The root path to use.
            dotted_subpath: Subpath under `root` with dots as separators.
            key: The key in the translation resource.

        Returns:
            The resolved translation resource.

        Raises:
            I18nKeyError: If the translation resource doesn't contain the requested key.
            I18nValueError: If the translation resource is not found or its content is invalid.
        """
        result = await load_translation_resource(resolve_json_path(root, dotted_subpath))
        if key in cls._root_keys:
            return result

        for k in key.split("."):
            try:
                result = result[k]
            except KeyError as e:
                raise I18nKeyError(f"Key not found: {key}") from e

        if len(kwargs) > 0:
            if not isinstance(result, str):
                raise I18nValueError("Formatting is only supported for strings.")

            return result.format(**kwargs)

        return result


@alru_cache(8)
async def load_translation_resource(path: Path) -> TranslationResource:
    """
    Loads the translation resource from the given path.

    Arguments:
        path: The path of the translation resource to load.

    Returns:
        The loaded translation resource.

    Raises:
        I18nValueError: If the translation resource is not a JSON dict.
    """

    try:
        async with await open_file(path, "r") as f:
            content = await f.read()
    except FileNotFoundError as e:
        raise I18nValueError(f"Translation resource not found: {str(path)}") from e

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise I18nValueError("Translation resource decoding failed.") from e

    if isinstance(result, dict):
        return result

    raise I18nValueError("Only dict translation resources are allowed.")


def resolve_json_path(root: Path, dotted_subpath: str) -> Path:
    """
    Resolves the given dotted subpath relative to root.

    Arguments:
        root: The root path.
        dotted_subpath: Subpath under `root` with dots as separators.

    Returns:
        The resolved path.

    Raises:
        I18nValueError: If the given dotted path is invalid.
    """
    *dirs, name = dotted_subpath.split(".")
    if not name:
        raise I18nValueError("Invalid path.")

    return root / Path(*dirs) / f"{name}.json"
