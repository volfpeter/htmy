import asyncio
from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Any

import pytest

from htmy import (
    Component,
    Context,
    ErrorBoundary,
    Formatter,
    Tag,
    TagWithProps,
    WithContext,
    XBool,
    component,
)
from htmy.renderer.typing import RendererType


class Page:
    @staticmethod
    def page() -> Component:
        class DemoValueError(ValueError): ...

        class CustomTagFormatter(Formatter):
            def __init__(
                self,
                *,
                default_formatter: Callable[[Any], str] = str,
                name_formatter: Callable[[str], str] | None = None,
            ) -> None:
                super().__init__(default_formatter=default_formatter, name_formatter=name_formatter)
                self.add(int, lambda i: f"int:{i}")

        class ARaise:
            async def htmy(self, context: Context) -> Component:
                raise DemoValueError("Deliberate")

        div = Tag("div")

        h1 = Tag("h1", child_separator=None)

        a_h2 = Tag("a_h2", child_separator=None)

        a_main = Tag("a_main")

        img = TagWithProps("img")

        tp = TagWithProps("tp")

        class AsyncText:
            def __init__(self, value: str) -> None:
                self._value = value

            async def htmy(self, context: Context) -> Component:
                await asyncio.sleep(context["aio-sleep"])
                return self._value

        @component
        def sync_fc(props: int, context: Context) -> Component:
            return f"sync_fc-{Formatter.from_context(context).format_value(props)}"

        @component
        async def async_fc(props: int, context: Context) -> Component:
            await asyncio.sleep(context["aio-sleep"])
            return f"async_fc-{Formatter.from_context(context).format_value(props)}"

        return WithContext(
            None,
            a_main(
                img(src="/example.png"),
                tp(x="x1", y="y1", checked=XBool.true, required=XBool(True), value_skipped=XBool(False)),
                sync_fc(987321),
                async_fc(456),
                a_main(
                    None,
                    Formatter().in_context(
                        div(
                            AsyncText("sd<fs> df"),
                            h1(
                                AsyncText("sdfds"),
                                created_at=datetime(2024, 10, 3, 4, 42, 2, 71, tzinfo=timezone.utc),
                                on_day_=date(2024, 10, 3),
                            ),
                            dp_1=123,
                            _class="w-full",
                            none=None,
                        )
                    ),
                    None,
                    ErrorBoundary(
                        div(
                            None,
                            ARaise(),
                        ),
                        fallback=h1("Fallback after rendering error.", None),
                        errors={TypeError, ValueError},
                    ),
                ),
                div(ErrorBoundary(ARaise(), fallback=None)),
                a_h2("something"),
                div(AsyncText("something else"), div(AsyncText("inner something else"))),
                p_1=123,
                p_2="fls",
                p_3=True,
            ),
            None,
            context={**CustomTagFormatter().to_context(), "aio-sleep": 1},
        )

    @staticmethod
    def rendered() -> str:
        return "\n".join(
            (
                # \n-s in this tuple mark places where None children are ignored
                # but still slightly mess up the output. The reason for not fixing
                # these is because stricted None checks would impact performance.
                '<a_main p-1="int:123" p-2="fls" p-3="true">',
                '<img src="/example.png"/>',
                '<tp x="x1" y="y1" checked="" required="" />',
                "sync_fc-int:987321",
                "async_fc-int:456",
                "<a_main >\n",
                '<div dp-1="123" class="w-full" >',
                "sd&lt;fs&gt; df",
                '<h1 created-at="2024-10-03T04:42:02.000071+00:00" on_day="2024-10-03">sdfds</h1>',
                "</div>\n",
                "<h1 >Fallback after rendering error.</h1>",
                "</a_main>",
                "<div >\n\n</div>",
                "<a_h2 >something</a_h2>",
                "<div >",
                "something else",
                "<div >",
                "inner something else",
                "</div>",
                "</div>",
                "</a_main>",
            )
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("page", "context", "expected"),
    (
        (Page.page(), None, Page.rendered()),
        (Page.page(), None, Page.rendered()),
    ),
)
async def test_complex_page_rendering(
    default_renderer: RendererType,
    baseline_renderer: RendererType,
    streaming_renderer: RendererType,
    page: Component,
    context: Context | None,
    expected: str,
) -> None:
    result = await default_renderer.render(page, context)
    assert result == expected

    result = await baseline_renderer.render(page, context)
    assert result == expected

    result = await streaming_renderer.render(page, context)
    assert result == expected
