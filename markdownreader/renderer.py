"""Markdown-to-HTML rendering with theme-aware Pygments code highlighting."""

import html as html_module
import re

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension

from markdownreader.settings import Settings

# Token colors must match the preview background: a light palette on the dark
# theme drops below 2:1 contrast. "github-dark" ships with Pygments >= 2.13.
PYGMENTS_STYLES = {
    "dark": "github-dark",
    "light": "default",
}


def build_pygments_css(theme: str) -> str:
    """Pygments stylesheet whose token colors suit the given theme."""
    try:
        from pygments.formatters import HtmlFormatter
    except ImportError:
        return ""
    try:
        formatter = HtmlFormatter(style=PYGMENTS_STYLES.get(theme, "default"), cssclass="highlight")
    except ValueError:
        formatter = HtmlFormatter(cssclass="highlight")
    return formatter.get_style_defs(".highlight")


def build_markdown_converter(code_highlight: bool = True, nl2br: bool = False) -> markdown.Markdown:
    extensions = [
        FencedCodeExtension(),
        TableExtension(),
        "markdown.extensions.sane_lists",
        "markdown.extensions.smarty",
    ]
    if nl2br:
        extensions.append("markdown.extensions.nl2br")
    if code_highlight:
        extensions.insert(1, CodeHiliteExtension(
            linenums=False,
            css_class="highlight",
            guess_lang=False,
            use_pygments=True,
        ))
    return markdown.Markdown(extensions=extensions)


# Task list items ("- [ ] foo" / "- [x] foo") render as glyphs — Qt rich text
# has no <input type="checkbox"> support.
_TASK_ITEM_RE = re.compile(r"(<li[^>]*>(?:\s*<p[^>]*>)?)\s*\[([ xX])\]\s+")
_HEADING_TAG_RE = re.compile(r"<h([1-6])[^>]*>")
_HEADING_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")


def _apply_task_lists(body_html: str) -> str:
    def repl(match):
        box = "☑" if match.group(2).lower() == "x" else "☐"
        return f"{match.group(1)}{box} "
    return _TASK_ITEM_RE.sub(repl, body_html)


def _inject_heading_anchors(body_html: str) -> str:
    # Anchor numbering must match extract_outline(): both count <hN> tags in
    # document order.
    counter = 0

    def repl(match):
        nonlocal counter
        anchor = f"md-heading-{counter}"
        counter += 1
        return match.group(0) + f'<a name="{anchor}"></a>'

    return _HEADING_TAG_RE.sub(repl, body_html)


def extract_outline(body_html: str) -> list[tuple[int, str, str]]:
    """(level, plain text, anchor) for every heading, in document order."""
    outline = []
    for index, match in enumerate(_HEADING_RE.finditer(body_html)):
        text = html_module.unescape(_TAG_RE.sub("", match.group(2))).strip()
        outline.append((int(match.group(1)), text, f"md-heading-{index}"))
    return outline


def render_document(text: str, theme: str, settings: Settings, code_highlight: bool = True) -> tuple[str, list]:
    """Convert markdown text; return (full HTML page, heading outline)."""
    converter = build_markdown_converter(code_highlight, nl2br=settings.preview_nl2br)
    converter.reset()
    body_html = converter.convert(text)

    body_html = _apply_task_lists(body_html)
    body_html = _inject_heading_anchors(body_html)
    outline = extract_outline(body_html)

    code_css = build_pygments_css(theme) if code_highlight else ""
    html = _wrap_html(body_html, theme, settings.preview_font_size, code_css)
    return html, outline


def _wrap_html(body_html: str, theme: str, font_size: int, code_css: str) -> str:
    if theme == "dark":
        bg = "#0d1117"
        fg = "#c9d1d9"
        heading = "#e6edf3"
        link = "#58a6ff"
        code_bg = "#161b22"
        border = "#21262d"
        muted = "#8b949e"
        blockquote_bg = "#1c2635"
    else:
        bg = "#ffffff"
        fg = "#1f2328"
        heading = "#1f2328"
        link = "#0969da"
        code_bg = "#f6f8fa"
        border = "#d0d7de"
        muted = "#656d76"
        blockquote_bg = "#f0f6fc"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{code_css}
<style>
body {{
    font-family: "Segoe UI", "Noto Sans SC", Helvetica, Arial, sans-serif;
    line-height: 1.75;
    padding: 32px 48px;
    margin: 0;
    font-size: {font_size}px;
    color: {fg};
    background: {bg};
}}
h1, h2, h3, h4, h5, h6 {{ color: {heading}; margin-top: 1.6em; margin-bottom: 0.6em; font-weight: 600; }}
h1 {{ font-size: 2em; border-bottom: 1px solid {border}; padding-bottom: 0.4em; }}
h2 {{ font-size: 1.5em; border-bottom: 1px solid {border}; padding-bottom: 0.3em; }}
h3 {{ font-size: 1.25em; }}
a {{ color: {link}; text-decoration: none; }}
code {{ background: {code_bg}; padding: 0.2em 0.45em; font-size: 88%; font-family: "Cascadia Code", "Fira Code", "JetBrains Mono", Consolas, monospace; }}
pre {{ background: {code_bg}; padding: 18px 20px; line-height: 1.5; border: 1px solid {border}; }}
pre code {{ background: transparent; padding: 0; font-size: 92%; border: none; }}
blockquote {{ border-left: 4px solid {link}; color: {muted}; margin: 1em 0; padding: 0.5em 1.2em; background: {blockquote_bg}; }}
table {{ border-collapse: collapse; width: 100%; margin: 1.2em 0; border: 1px solid {border}; }}
th, td {{ border: 1px solid {border}; padding: 10px 14px; text-align: left; }}
th {{ background: {code_bg}; font-weight: 600; }}
img {{ max-width: 100%; }}
hr {{ border: none; border-top: 1px solid {border}; margin: 2.5em 0; }}
ul, ol {{ padding-left: 1.8em; }}
li {{ margin: 0.3em 0; }}
.highlight {{ background: {code_bg}; padding: 18px 20px; border: 1px solid {border}; margin: 1em 0; }}
.highlight pre {{ background: transparent; margin: 0; padding: 0; border: none; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""
