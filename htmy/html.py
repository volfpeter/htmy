from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .typing import ComponentType


from .core import SafeStr
from .tag import Tag, TagWithProps


class DOCTYPE:
    """Document type declaration."""

    html = SafeStr("<!DOCTYPE html>")
    """HTML document type."""


html = Tag("html")
"""
`<html>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/html.
"""

head = Tag("head")
"""
`<head>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/head.
"""

body = Tag("body")
"""
`<body>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body.
"""

base = TagWithProps("base")
"""
`<base>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base.
"""

title = Tag("title", child_separator=None)  # TODO: allow only a single str child.
"""
`<title>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/title.
"""

link = TagWithProps("link")
"""
`<link>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link.
"""


class Link:
    """`link` tag factories."""

    @staticmethod
    def css(href: str) -> ComponentType:
        return link(rel="stylesheet", type="text/css", href=href)


meta = TagWithProps("meta")
"""
`<meta>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta.
"""


class Meta:
    """`meta` tag factories."""

    @staticmethod
    def author(content: str) -> ComponentType:
        return meta(name="author", content=content)

    @staticmethod
    def charset(charset: str = "utf-8") -> ComponentType:
        return meta(charset=charset)

    @staticmethod
    def description(content: str) -> ComponentType:
        return meta(name="description", content=content)

    @staticmethod
    def keywords(content: str) -> ComponentType:
        return meta(name="keywords", content=content)

    @staticmethod
    def viewport(content: str = "width=device-width, initial-scale=1.0") -> ComponentType:
        return meta(name="viewport", content=content)


script = Tag("script")  # TODO: allow only a single str child.
"""
`<script>` element.

The script tag should have only one child, the script content. If it's not
empty, it should be a `SafeStr` for HTML and plain `str` for XHTML.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script.
"""

style = Tag("style")  # TODO: only allow a single str child, automatically convert plain str to SafeStr.
"""
`<style>` element.

The style tag should have only one child, the style content. If it's not
empty, it should be a `SafeStr` to avoid XML escaping.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/style.
"""

dialog = Tag("dialog")
"""
`<dialog>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog.
"""

address = Tag("address")
"""
`<address>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address.
"""

article = Tag("article")
"""
`<article>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/article.
"""

aside = Tag("aside")
"""
`<aside>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/aside.
"""

blockquote = Tag("blockquote")
"""
`<blockquote>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/blockquote.
"""

div = Tag("div")
"""
`<div>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/div.
"""

embed = TagWithProps("embed")
"""
`<embed>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/embed.
"""

figure = Tag("figure")
"""
`<figure>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/figure.
"""

figcaption = Tag("figcaption")
"""
`<figcaption>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/figcaption.
"""

footer = Tag("footer")
"""
`<footer>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/footer.
"""

header = Tag("header")
"""
`<header>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/header.
"""

hgroup = Tag("hgroup")
"""
`<hgroup>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/hgroup.
"""

hr = TagWithProps("hr")
"""
`<hr>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/hr.
"""

iframe = Tag("iframe")
"""
`<iframe>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe.
"""

main = Tag("main")
"""
`<main>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/main.
"""

details = Tag("details")
"""
`<details>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details.
"""

summary = Tag("summary", child_separator=None)
"""
`<summary>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/summary.
"""

nav = Tag("nav")
"""
`<nav>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/nav.
"""

menu = Tag("menu")
"""
`<menu>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/menu.
"""

noscript = Tag("noscript")
"""
`<noscript>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/noscript.
"""

pre = Tag("pre", child_separator=None)
"""
`<pre>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/pre.
"""

section = Tag("section")
"""
`<section>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section.
"""

template = Tag("template")
"""
`<template>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/template.
"""

form = Tag("form")
"""
`<form>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form.
"""

search = Tag("search")
"""
`<search>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/search.
"""

button = Tag("button")
"""
`<button>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button.
"""

option = Tag("option")
"""
`<option>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option.
"""

optgroup = Tag("optgroup")
"""
`<optgroup>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/optgroup.
"""

datalist = Tag("datalist")
"""
`<datalist>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/datalist.
"""

fieldset = Tag("fieldset")
"""
`<fieldset>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/fieldset.
"""

input_ = TagWithProps("input")
"""
`<input>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input.
"""

label = Tag("label")
"""
`<label>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/label.
"""

legend = Tag("legend")
"""
`<legend>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/legend.
"""

meter = Tag("meter")
"""
`<meter>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter.
"""

object = Tag("object")
"""
`<object>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object.
"""

output = Tag("output")
"""
`<output>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/output.
"""

progress = Tag("progress")
"""
`<progress>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/progress.
"""

select = Tag("select")
"""
`<select>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select.
"""

textarea = Tag("textarea")
"""
`<textarea>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea.
"""

a = Tag("a", child_separator=None)
"""
`<a>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a.
"""

abbr = Tag("abbr", child_separator=None)
"""
`<abbr>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/abbr.
"""

b = Tag("b", child_separator=None)
"""
`<b>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/b.
"""

bdi = Tag("bdi", child_separator=None)
"""
`<bdi>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdi.
"""

bdo = Tag("bdo", child_separator=None)
"""
`<bdo>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdo.
"""

br = TagWithProps("br")
"""
`<br>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/br.
"""

cite = Tag("cite", child_separator=None)
"""
`<cite>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/cite.
"""

code = Tag("code", child_separator=None)
"""
`<code>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/code.
"""

data = Tag("data", child_separator=None)
"""
`<data>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data.
"""

del_ = Tag("del", child_separator=None)
"""
`<del>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/del.
"""

dfn = Tag("dfn", child_separator=None)
"""
`<dfn>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dfn.
"""

em = Tag("em", child_separator=None)
"""
`<em>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/em.
"""

i = Tag("i", child_separator=None)
"""
`<i>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/i.
"""

kbd = Tag("kbd", child_separator=None)
"""
`<kbd>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/kbd.
"""

picture = Tag("picture")
"""
`<picture>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/picture.
"""

img = TagWithProps("img")
"""
`<img>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img.
"""

source = TagWithProps("source")
"""
`<source>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source.
"""

ins = Tag("ins", child_separator=None)
"""
`<ins>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ins.
"""

mark = Tag("mark", child_separator=None)
"""
`<mark>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/mark.
"""

q = Tag("q", child_separator=None)
"""
`<q>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/q.
"""

s = Tag("s", child_separator=None)
"""
`<s>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/s.
"""

samp = Tag("samp", child_separator=None)
"""
`<samp>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/samp.
"""

small = Tag("small", child_separator=None)
"""
`<small>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/small.
"""

span = Tag("span", child_separator=None)
"""
`<span>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/span.
"""

strong = Tag("strong", child_separator=None)
"""
`<strong>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/strong.
"""

sub = Tag("sub", child_separator=None)
"""
`<sub>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/sub.
"""

sup = Tag("sup", child_separator=None)
"""
`<sup>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/sup.
"""

svg = Tag("svg", child_separator=None)
"""
`<svg>` element.

See https://developer.mozilla.org/en-US/docs/Web/SVG/Element/svg.
"""

u = Tag("u", child_separator=None)
"""
`<u>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/u.
"""

var = Tag("var", child_separator=None)
"""
`<var>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/var.
"""

wbr = TagWithProps("wbr")
"""
`<wbr>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/wbr.
"""

li = Tag("li", child_separator=None)
"""
`<li>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/li.
"""

ol = Tag("ol")
"""
`<ol>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ol.
"""

ul = Tag("ul")
"""
`<ul>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ul.
"""

dl = Tag("dl")
"""
`<dl>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dl.
"""

dt = Tag("dt", child_separator=None)
"""
`<dt>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dt.
"""

dd = Tag("dd")
"""
`<dd>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dd.
"""

caption = Tag("caption")
"""
`<caption>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/caption.
"""

table = Tag("table")
"""
`<table>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table.
"""

thead = Tag("thead")
"""
`<thead>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/thead.
"""

tbody = Tag("tbody")
"""
`<tbody>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tbody.
"""

tfoot = Tag("tfoot")
"""
`<tfoot>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tfoot.
"""

tr = Tag("tr")
"""
`<tr>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tr.
"""

th = Tag("th", child_separator=None)
"""
`<th>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th.
"""

td = Tag("td", child_separator=None)
"""
`<td>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/td.
"""

colgroup = Tag("colgroup")
"""
`<colgroup>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/colgroup.
"""

col = TagWithProps("col")
"""
`<col>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/col.
"""

h1 = Tag("h1", child_separator=None)
"""
`<h1>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h1.
"""

h2 = Tag("h2", child_separator=None)
"""
`<h2>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h2.
"""

h3 = Tag("h3", child_separator=None)
"""
`<h3>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h3.
"""

h4 = Tag("h4", child_separator=None)
"""
`<h4>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h4.
"""

h5 = Tag("h5", child_separator=None)
"""
`<h5>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h5.
"""

h6 = Tag("h6", child_separator=None)
"""
`<h6>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/h6.
"""

p = Tag("p", child_separator=None)
"""
`<p>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/p.
"""

time = Tag("time", child_separator=None)
"""
`<time>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/time.
"""

audio = Tag("audio")
"""
`<audio>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio.
"""

video = Tag("video")
"""
`<video>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video.
"""

track = TagWithProps("track")
"""
`<track>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track.
"""

canvas = Tag("canvas")
"""
`<canvas>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas.
"""

area = TagWithProps("area")
"""
`<area>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area.
"""

map = Tag("map")
"""
`<map>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/map.
"""

slot = Tag("slot")
"""
`<slot>` element.

See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/slot.
"""


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
