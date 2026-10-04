"""Renderer tests: theme-aware highlighting, task lists, outline, images."""

from markdownreader.renderer import render_document, extract_outline, build_pygments_css

SAMPLE = """# 标题

Python 示例：

```python
def hello(name):
    # greet the user
    print(f"Hello, {name}!")
    return True
```

无语言代码块：

```
plain text block
```

## 任务清单

- [ ] 未完成事项
- [x] 已完成事项

正文第二段。
"""


def test_dark_palette_is_github_dark(settings):
    css = build_pygments_css("dark")
    assert "ff7b72" in css.lower()
    assert "0000ff" not in css.lower()  # light-only pure blue must not appear


def test_light_palette_is_default(settings):
    assert "#008000" in build_pygments_css("light").lower()


def test_palettes_differ_per_theme(settings):
    assert build_pygments_css("dark") != build_pygments_css("light")


def test_rendered_html_embeds_theme_tokens(settings):
    dark, _ = render_document(SAMPLE, "dark", settings)
    light, _ = render_document(SAMPLE, "light", settings)
    assert "ff7b72" in dark.lower()
    assert "008000" in light.lower()


def test_task_lists_render_as_glyphs(settings):
    html, _ = render_document(SAMPLE, "dark", settings)
    assert "☐" in html and "☑" in html
    assert "[ ]" not in html


def test_outline_and_anchors(settings):
    html, outline = render_document(SAMPLE, "dark", settings)
    assert [(lv, t) for lv, t, _ in outline] == [(1, "标题"), (2, "任务清单")]
    assert all(f'<a name="{a}">' in html for _, _, a in outline)


def test_code_block_content_is_not_outline(settings):
    _, outline = render_document(SAMPLE, "dark", settings)
    assert all("greet" not in title for _, title, _ in outline)


def test_nl2br_off_is_github_style(settings):
    html, _ = render_document("line one\nline two", "dark", settings, code_highlight=False)
    assert "<br" not in html


def test_nl2br_on_renders_br(settings):
    settings.preview_nl2br = True
    html, _ = render_document("line one\nline two", "dark", settings, code_highlight=False)
    assert "<br" in html


def test_highlight_toggle_drops_token_css(settings):
    html, outline = render_document(SAMPLE, "dark", settings, code_highlight=False)
    assert "highlight ." not in html
    assert len(outline) == 2  # outline survives the toggle


def test_dark_palette_contrast_meets_wcag(settings):
    def lum(h):
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = f(r), f(g), f(b)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def contrast(a, b):
        la, lb = lum(a), lum(b)
        hi, lo = max(la, lb), min(la, lb)
        return (hi + 0.05) / (lo + 0.05)

    worst = min(contrast(c, "161b22") for c in
                ("ff7b72", "d2a8ff", "a5d6ff", "8b949e"))
    assert worst >= 4.5


def test_extract_outline_plain_html():
    html = "<h1>A</h1><p>x</p><h3>B &amp; C</h3>"
    assert extract_outline(html) == [(1, "A", "md-heading-0"), (3, "B & C", "md-heading-1")]
