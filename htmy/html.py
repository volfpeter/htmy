from __future__ import annotations

from .core import SafeStr, Tag, TagConfig, TagWithProps
from .typing import PropertyValue


class _DefaultTagConfig:
    inline_children: TagConfig = {"child_separator": None}


class DOCTYPE:
    """Document type declaration."""

    html = SafeStr("<!DOCTYPE html>")
    """HTML document type."""


class html(Tag):
    """
    `<html>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/html.
    """

    __slots__ = ()


class head(Tag):
    """
    `<head>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/head.
    """

    __slots__ = ()


class body(Tag):
    """
    `<body>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body.
    """

    __slots__ = ()


class base(TagWithProps):
    """
    `<base>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base.
    """

    __slots__ = ()


class title(Tag):
    """
    `<title>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/title.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children

    def __init__(self, text: str, **props: PropertyValue) -> None:
        super().__init__(text, **props)


class link(TagWithProps):
    """
    `<link>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link.
    """

    __slots__ = ()

    @classmethod
    def css(cls, href: str) -> link:
        return cls(rel="stylesheet", type="text/css", href=href)


class meta(TagWithProps):
    """
    `<meta>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta.
    """

    __slots__ = ()

    @classmethod
    def author(cls, content: str) -> meta:
        return cls(name="author", content=content)

    @classmethod
    def charset(cls, charset: str = "utf-8") -> meta:
        return cls(charset=charset)

    @classmethod
    def description(cls, content: str) -> meta:
        return cls(name="description", content=content)

    @classmethod
    def keywords(cls, content: str) -> meta:
        return cls(name="keywords", content=content)

    @classmethod
    def viewport(cls, content: str = "width=device-width, initial-scale=1.0") -> meta:
        return cls(name="viewport", content=content)


class script(Tag):
    """
    `<script>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script.
    """

    __slots__ = ()

    def __init__(self, text: str = "", **props: PropertyValue) -> None:
        """
        Initialization.

        Arguments:
            text: The inner content of the tag. If not empty, it should be a
                `SafeStr` for HTML and plain `str` for XHTML.
            **props: Tag attributes.
        """
        super().__init__(text, **props)


class style(Tag):
    """
    `<style>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/style.
    """

    __slots__ = ()

    def __init__(self, content: str, **props: PropertyValue) -> None:
        """
        Initialization.

        Arguments:
            content: The content of the tag. It is automatically converted to a `SafeStr`.
            **props: Tag attributes.
        """
        super().__init__(SafeStr(content), **props)


class dialog(Tag):
    """
    `<dialog>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog.
    """

    __slots__ = ()


class address(Tag):
    """
    `<address>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address.
    """

    __slots__ = ()


class article(Tag):
    """
    `<article>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/article.
    """

    __slots__ = ()


class aside(Tag):
    """
    `<aside>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/aside.
    """

    __slots__ = ()


class blockquote(Tag):
    """
    `<blockquote>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/blockquote.
    """

    __slots__ = ()


class div(Tag):
    """
    `<div>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/div.
    """

    __slots__ = ()


class embed(TagWithProps):
    """
    `<embed>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/embed.
    """

    __slots__ = ()


class figure(Tag):
    """
    `<figure>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/figure.
    """

    __slots__ = ()


class figcaption(Tag):
    """
    `<figcaption>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/figcaption.
    """

    __slots__ = ()


class footer(Tag):
    """
    `<footer>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/footer.
    """

    __slots__ = ()


class header(Tag):
    """
    `<header>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/header.
    """

    __slots__ = ()


class hgroup(Tag):
    """
    `<hgroup>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/hgroup.
    """

    __slots__ = ()


class hr(TagWithProps):
    """
    `<hr>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/hr.
    """

    __slots__ = ()


class iframe(TagWithProps):
    """
    `<iframe>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe.
    """

    __slots__ = ()


class main(Tag):
    """
    `<main>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/main.
    """

    __slots__ = ()


class details(Tag):
    """
    `<details>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details.
    """

    __slots__ = ()


class summary(Tag):
    """
    `<summary>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/summary.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class nav(Tag):
    """
    `<nav>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/nav.
    """

    __slots__ = ()


class menu(Tag):
    """
    `<menu>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/menu.
    """

    __slots__ = ()


class noscript(Tag):
    """
    `<noscript>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/noscript.
    """

    __slots__ = ()


class pre(Tag):
    """
    `<pre>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/pre.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class section(Tag):
    """
    `<section>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section.
    """

    __slots__ = ()


class template(Tag):
    """
    `<>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/template.
    """

    __slots__ = ()


class form(Tag):
    """
    `<form>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form.
    """

    __slots__ = ()


class search(Tag):
    """
    `<search>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/search.
    """

    __slots__ = ()


class button(Tag):
    """
    `<button>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button.
    """

    __slots__ = ()


class option(Tag):
    """
    `<option>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option.
    """

    __slots__ = ()


class optgroup(Tag):
    """
    `<optgroup>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/optgroup.
    """

    __slots__ = ()


class datalist(Tag):
    """
    `<datalist>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/datalist.
    """

    __slots__ = ()


class fieldset(Tag):
    """
    `<fieldset>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/fieldset.
    """

    __slots__ = ()


class input_(TagWithProps):
    """
    `<input>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input.
    """

    __slots__ = ()

    def _get_htmy_name(self) -> str:
        return "input"


class label(Tag):
    """
    `<label>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/label.
    """

    __slots__ = ()


class legend(Tag):
    """
    `<legend>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/legend.
    """

    __slots__ = ()


class meter(Tag):
    """
    `<meter>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter.
    """

    __slots__ = ()


class object(Tag):
    """
    `<object>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object.
    """

    __slots__ = ()


class output(Tag):
    """
    `<output>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/output.
    """

    __slots__ = ()


class progress(Tag):
    """
    `<progress>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/progress.
    """

    __slots__ = ()


class select(Tag):
    """
    `<select>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select.
    """

    __slots__ = ()


class textarea(Tag):
    """
    `<textarea>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea.
    """

    __slots__ = ()


class a(Tag):
    """
    `<a>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class abbr(Tag):
    """
    `<abbr>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/abbr.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class b(Tag):
    """
    `<b>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/b.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class bdi(Tag):
    """
    `<bdi>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdi.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class bdo(Tag):
    """
    `<bdo>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdo.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class br(TagWithProps):
    """
    `<br>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/br.
    """

    __slots__ = ()


class cite(Tag):
    """
    `<cite>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/cite.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class code(Tag):
    """
    `<code>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/code.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class data(Tag):
    """
    `<data>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class del_(Tag):
    """
    `<del>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/del.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children

    def _get_htmy_name(self) -> str:
        return "del"


class dfn(Tag):
    """
    `<dfn>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dfn.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class em(Tag):
    """
    `<em>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/em.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class i(Tag):
    """
    `<i>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/i.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class picture(Tag):
    """
    `<picture>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/picture.
    """

    __slots__ = ()


class img(TagWithProps):
    """
    `<img>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img.
    """

    __slots__ = ()


class source(TagWithProps):
    """
    `<source>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source.
    """

    __slots__ = ()


class ins(Tag):
    """
    `<ins>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ins.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class mark(Tag):
    """
    `<mark>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/mark.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class q(Tag):
    """
    `<q>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/q.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class s(Tag):
    """
    `<s>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/s.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class samp(Tag):
    """
    `<samp>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/samp.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class small(Tag):
    """
    `<small>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/small.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class span(Tag):
    """
    `<span>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/span.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class strong(Tag):
    """
    `<strong>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/strong.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class sub(Tag):
    """
    `<sub>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/sub.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class sup(Tag):
    """
    `<sup>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/sup.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class u(Tag):
    """
    `<u>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/u.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class var(Tag):
    """
    `<var>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/var.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class wbr(Tag):
    """
    `<>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class li(Tag):
    """
    `<li>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/li.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class ol(Tag):
    """
    `<ol>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ol.
    """

    __slots__ = ()


class ul(Tag):
    """
    `<ul>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ul.
    """

    __slots__ = ()


class dl(Tag):
    """
    `<dl>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dl.
    """

    __slots__ = ()


class dt(Tag):
    """
    `<dt>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dt.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class dd(Tag):
    """
    `<dd>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dd.
    """

    __slots__ = ()


class caption(Tag):
    """
    `<caption>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/caption.
    """

    __slots__ = ()


class table(Tag):
    """
    `<table>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table.
    """

    __slots__ = ()


class thead(Tag):
    """
    `<thead>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/thead.
    """

    __slots__ = ()


class tbody(Tag):
    """
    `<tbody>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tbody.
    """

    __slots__ = ()


class tfoot(Tag):
    """
    `<tfoot>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tfoot.
    """

    __slots__ = ()


class tr(Tag):
    """
    `<tr>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tr.
    """

    __slots__ = ()


class th(Tag):
    """
    `<th>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class td(Tag):
    """
    `<td>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/td.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class colgroup(TagWithProps):
    """
    `<colgroup>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/colgroup.
    """

    __slots__ = ()


class col(TagWithProps):
    """
    `<col>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/col.
    """

    __slots__ = ()


class h1(Tag):
    """
    `<h1>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h1.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class h2(Tag):
    """
    `<h2>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h2.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class h3(Tag):
    """
    `<h3>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h3.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class h4(Tag):
    """
    `<h4>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h4.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class h5(Tag):
    """
    `<h5>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h5.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class h6(Tag):
    """
    `<h6>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h6.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class p(Tag):
    """
    `<p>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/p.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class time(Tag):
    """
    `<time>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/time.
    """

    __slots__ = ()

    tag_config = _DefaultTagConfig.inline_children


class audio(Tag):
    """
    `<audio>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio.
    """

    __slots__ = ()


class video(Tag):
    """
    `<video>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video.
    """

    __slots__ = ()


class track(TagWithProps):
    """
    `<track>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track.
    """

    __slots__ = ()


class canvas(Tag):
    """
    `<canvas>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas.
    """

    __slots__ = ()


class area(TagWithProps):
    """
    `<area>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area.
    """

    __slots__ = ()


class map(Tag):
    """
    `<map>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/map.
    """

    __slots__ = ()


class slot(Tag):
    """
    `<slot>` element.

    See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/slot.
    """

    __slots__ = ()


class entity:
    amp = SafeStr("&amp;")
    apos = SafeStr("&apos;")
    cent = SafeStr("&cent;")
    copy = SafeStr("&copy;")
    euro = SafeStr("&euro;")
    gt = SafeStr("&gt;")
    lt = SafeStr("&lt;")
    mdash = SafeStr("&mdash;")
    nbsp = SafeStr("&nbsp;")
    ndash = SafeStr("&ndash;")
    pound = SafeStr("&pound;")
    quot = SafeStr("&quot;")
    reg = SafeStr("&reg;")
    times = SafeStr("&times;")
    yen = SafeStr("&yen;")
