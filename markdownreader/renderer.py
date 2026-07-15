"""Markdown-to-HTML rendering with Pygments code highlighting."""

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension

from markdownreader.settings import Settings

PYGMENTS_CSS = ""

try:
    from pygments.formatters import HtmlFormatter
    formatter = HtmlFormatter(nowrap=True, cssclass="highlight")
    PYGMENTS_CSS = formatter.get_style_defs(".highlight")
except ImportError:
    pass


def build_markdown_converter(code_highlight: bool = True) -> markdown.Markdown:
    extensions = [
        FencedCodeExtension(),
        TableExtension(),
        TocExtension(permalink=False),
        "markdown.extensions.nl2br",
        "markdown.extensions.sane_lists",
        "markdown.extensions.smarty",
    ]
    if code_highlight:
        extensions.insert(1, CodeHiliteExtension(
            linenums=False,
            css_class="highlight",
            guess_lang=True,
            use_pygments=True,
        ))
    return markdown.Markdown(extensions=extensions)


def render_markdown(text: str, converter: markdown.Markdown | None = None) -> str:
    """Convert markdown text to a complete HTML page."""
    if converter is None:
        converter = build_markdown_converter()
    converter.reset()
    body_html = converter.convert(text)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{PYGMENTS_CSS}
<style id="theme-style">
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.7;
    padding: 24px 40px;
    margin: 0;
    color: #c9d1d9;
    background: #0d1117;
}}
h1, h2, h3, h4, h5, h6 {{ color: #e6edf3; margin-top: 1.4em; margin-bottom: 0.5em; font-weight: 600; }}
h1 {{ font-size: 2em; border-bottom: 1px solid #21262d; padding-bottom: 0.3em; }}
h2 {{ font-size: 1.5em; border-bottom: 1px solid #21262d; padding-bottom: 0.3em; }}
a {{ color: #58a6ff; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
code {{ background: #161b22; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }}
pre {{ background: #161b22; padding: 16px; border-radius: 6px; overflow-x: auto; line-height: 1.45; }}
pre code {{ background: transparent; padding: 0; font-size: 100%; }}
blockquote {{ border-left: 4px solid #30363d; color: #8b949e; margin: 0; padding: 0 1em; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ border: 1px solid #21262d; padding: 8px 12px; text-align: left; }}
th {{ background: #161b22; font-weight: 600; }}
img {{ max-width: 100%; }}
hr {{ border: none; border-top: 1px solid #21262d; margin: 2em 0; }}
/* Pygments highlight overrides */
.highlight {{ background: #161b22; border-radius: 6px; padding: 16px; overflow-x: auto; }}
.highlight pre {{ background: transparent; margin: 0; padding: 0; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""


def render_with_theme(text: str, theme: str, settings: Settings, code_highlight: bool = True) -> str:
    """Render markdown with the specified theme applied."""
    converter = build_markdown_converter(code_highlight)
    converter.reset()
    body_html = converter.convert(text)

    font_size = settings.preview_font_size

    if theme == "dark":
        bg = "#0d1117"
        fg = "#c9d1d9"
        heading = "#e6edf3"
        link = "#58a6ff"
        code_bg = "#161b22"
        border = "#21262d"
        muted = "#8b949e"
    else:
        bg = "#ffffff"
        fg = "#1f2328"
        heading = "#1f2328"
        link = "#0969da"
        code_bg = "#f6f8fa"
        border = "#d0d7de"
        muted = "#656d76"

    # Code highlight CSS (only if pygments is active)
    code_css = PYGMENTS_CSS if code_highlight else ""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{code_css}
<style id="theme-style">
* {{ box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", Helvetica, Arial, sans-serif;
    line-height: 1.75;
    padding: 32px 48px;
    margin: 0;
    font-size: {font_size}px;
    color: {fg};
    background: {bg};
    max-width: 100%;
}}
h1, h2, h3, h4, h5, h6 {{ color: {heading}; margin-top: 1.6em; margin-bottom: 0.6em; font-weight: 600; letter-spacing: -0.01em; }}
h1 {{ font-size: 2em; border-bottom: 1px solid {border}; padding-bottom: 0.4em; }}
h2 {{ font-size: 1.5em; border-bottom: 1px solid {border}; padding-bottom: 0.3em; }}
h3 {{ font-size: 1.25em; }}
a {{ color: {link}; text-decoration: none; transition: color 0.15s; }}
a:hover {{ text-decoration: underline; }}
code {{ background: {code_bg}; padding: 0.2em 0.45em; border-radius: 5px; font-size: 88%; font-family: "Cascadia Code", "Fira Code", "JetBrains Mono", Consolas, monospace; }}
pre {{ background: {code_bg}; padding: 18px 20px; border-radius: 8px; overflow-x: auto; line-height: 1.5; border: 1px solid {border}; }}
pre code {{ background: transparent; padding: 0; font-size: 92%; border: none; }}
blockquote {{ border-left: 4px solid {link}; color: {muted}; margin: 1em 0; padding: 0.5em 1.2em; background: {"rgba(56,139,253,0.06)" if theme == "dark" else "rgba(9,105,218,0.04)"}; border-radius: 0 6px 6px 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 1.2em 0; border-radius: 6px; overflow: hidden; border: 1px solid {border}; }}
th, td {{ border: 1px solid {border}; padding: 10px 14px; text-align: left; }}
th {{ background: {code_bg}; font-weight: 600; }}
tr:hover td {{ background: {"rgba(56,139,253,0.05)" if theme == "dark" else "rgba(9,105,218,0.03)"}; }}
img {{ max-width: 100%; border-radius: 6px; }}
hr {{ border: none; border-top: 1px solid {border}; margin: 2.5em 0; }}
ul, ol {{ padding-left: 1.8em; }}
li {{ margin: 0.3em 0; }}
.highlight {{ background: {code_bg}; border-radius: 8px; padding: 18px 20px; overflow-x: auto; border: 1px solid {border}; margin: 1em 0; }}
.highlight pre {{ background: transparent; margin: 0; padding: 0; border: none; }}

/* Scrollbar styling */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {border}; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {muted}; }}

/* Task lists */
input[type="checkbox"] {{ margin-right: 0.5em; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""
