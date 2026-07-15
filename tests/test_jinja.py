from collections.abc import Mapping
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

from htmy import Renderer, SafeStr
from htmy.jinja import DefaultSlots, JinjaContextFactory, JinjaTemplate, JinjaTemplates
from htmy.renderer import BaselineRenderer
from htmy.typing import Component

_TEMPLATE_DIR = Path(__file__).parent / "data"

_SYNC_TEMPLATES = JinjaTemplates(Environment(loader=FileSystemLoader(_TEMPLATE_DIR), autoescape=True))

_ASYNC_TEMPLATES = JinjaTemplates(
    Environment(
        loader=FileSystemLoader(_TEMPLATE_DIR),
        enable_async=True,
        autoescape=True,
    )
)


@pytest.mark.parametrize(
    "templates",
    [_SYNC_TEMPLATES, _ASYNC_TEMPLATES],
    ids=["sync", "async"],
)
@pytest.mark.parametrize(
    ("jinja_context", "slots", "default_slots", "make_context", "use_default_slots", "expected"),
    [
        pytest.param(None, None, None, None, False, "title=\nheading=\nmessage=", id="default-context"),
        pytest.param({}, None, None, None, False, "title=\nheading=\nmessage=", id="empty-context"),
        pytest.param(
            {"title": "Hello", "heading": "Hi there", "message": "Welcome."},
            None,
            None,
            None,
            False,
            "title=Hello\nheading=Hi there\nmessage=Welcome.",
            id="filled-context",
        ),
        pytest.param(
            {"title": "A & B", "heading": "", "message": ""},
            None,
            None,
            None,
            False,
            "title=A &amp; B\nheading=\nmessage=",
            id="autoescape",
        ),
        pytest.param(
            {"title": "Hello"},
            {"children": SafeStr("<b>child</b>")},
            None,
            None,
            False,
            "title=Hello\nheading=\nmessage=\nnav=\nchildren=<b>child</b>",
            id="single-slot",
        ),
        pytest.param(
            {"title": "Hello"},
            {"children": SafeStr("body"), "nav": SafeStr("<nav>links</nav>")},
            None,
            None,
            False,
            "title=Hello\nheading=\nmessage=\nnav=<nav>links</nav>\nchildren=body",
            id="multiple-slots",
        ),
        pytest.param(
            {"title": "<b>"},
            {"children": SafeStr("<b>child</b>")},
            None,
            None,
            False,
            "title=&lt;b&gt;\nheading=\nmessage=\nnav=\nchildren=<b>child</b>",
            id="no-double-escape",
        ),
        pytest.param(
            {"title": "t", "slots": {"children": "should-not-win"}},
            {"children": SafeStr("real")},
            None,
            None,
            False,
            "title=t\nheading=\nmessage=\nnav=\nchildren=real",
            id="slots-key-is-reserved",
        ),
        pytest.param(
            {"title": "static"},
            None,
            None,
            lambda ctx: {"title": "from make_context"},
            False,
            "title=from make_context\nheading=\nmessage=",
            id="make-context-overrides-static",
        ),
        pytest.param(
            {"title": "t"},
            {"children": SafeStr("real")},
            None,
            lambda ctx: {"slots": "forbidden"},
            False,
            "title=t\nheading=\nmessage=\nnav=\nchildren=real",
            id="make-context-cannot-override-slots",
        ),
        pytest.param(
            {"title": "Hello"},
            None,
            {"children": SafeStr("<b>default-child</b>"), "nav": SafeStr("default-nav")},
            None,
            True,
            "title=Hello\nheading=\nmessage=\nnav=default-nav\nchildren=<b>default-child</b>",
            id="default-slots-only",
        ),
        pytest.param(
            {"title": "Hello"},
            None,
            {"children": SafeStr("<b>default-child</b>"), "nav": SafeStr("default-nav")},
            None,
            False,
            "title=Hello\nheading=\nmessage=",
            id="default-slots-opted-out",
        ),
        pytest.param(
            {"title": "Hello"},
            {"children": SafeStr("explicit-children")},
            {"children": SafeStr("default-children"), "nav": SafeStr("<nav>default-nav</nav>")},
            None,
            True,
            ("title=Hello\nheading=\nmessage=\nnav=<nav>default-nav</nav>\nchildren=explicit-children"),
            id="default-slots-merged-with-explicit",
        ),
        pytest.param(
            {"title": "Hello"},
            {"children": SafeStr("explicit-children")},
            {"children": SafeStr("default-children"), "nav": SafeStr("<nav>default-nav</nav>")},
            None,
            False,
            ("title=Hello\nheading=\nmessage=\nnav=\nchildren=explicit-children"),
            id="default-slots-opted-out-keeps-explicit",
        ),
        pytest.param(
            {"title": "outer-title"},
            {
                "children": JinjaTemplate(
                    "hello-world.jinja",
                    jinja_context={"title": "inner-title"},
                    slots={"children": SafeStr("<i>deep</i>")},
                )
            },
            None,
            None,
            False,
            (
                "title=outer-title\nheading=\nmessage=\nnav=\n"
                "children=title=inner-title\nheading=\nmessage=\nnav=\nchildren=<i>deep</i>"
            ),
            id="recursion",
        ),
    ],
)
@pytest.mark.anyio
async def test_jinja_template(
    default_renderer: Renderer,
    baseline_renderer: BaselineRenderer,
    templates: JinjaTemplates,
    jinja_context: Mapping[str, object] | None,
    slots: Mapping[str, Component] | None,
    default_slots: Mapping[str, Component] | None,
    make_context: JinjaContextFactory | None,
    use_default_slots: bool,
    expected: str,
) -> None:
    """Renders a Jinja template with both renderers and both template sources."""
    template = JinjaTemplate(
        "hello-world.jinja",
        jinja_context=jinja_context,
        slots=slots,
        make_context=make_context,
        use_default_slots=use_default_slots,
    )
    component = DefaultSlots(default_slots).in_context(template) if default_slots is not None else template
    for renderer in (default_renderer, baseline_renderer):
        result = await renderer.render(component, context=templates.to_context())
        assert result == expected
