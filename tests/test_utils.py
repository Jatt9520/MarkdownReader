"""File-format and encoding tests."""

from pathlib import Path

from markdownreader.utils import MARKDOWN_EXTENSIONS, is_markdown_file, read_text_auto


def test_markdown_extension_whitelist(tmp_path):
    assert is_markdown_file(Path("a.md"))
    assert is_markdown_file(Path("a.QMD"))
    for ext in (".qmd", ".rmd", ".mdwn", ".livemd", ".mkdn", ".text"):
        assert ext in MARKDOWN_EXTENSIONS
    assert not is_markdown_file(Path("a.exe"))


def test_read_utf8(tmp_path):
    p = tmp_path / "u.md"
    p.write_text("中文内容", encoding="utf-8")
    text, enc = read_text_auto(p)
    assert text == "中文内容" and enc == "utf-8"


def test_read_utf8_bom(tmp_path):
    p = tmp_path / "b.md"
    p.write_text("BOM 内容", encoding="utf-8-sig")
    text, enc = read_text_auto(p)
    assert text == "BOM 内容" and enc == "utf-8-sig"


def test_read_gb18030(tmp_path):
    p = tmp_path / "g.txt"
    p.write_bytes("中文 GBK 编码的内容".encode("gb18030"))
    text, enc = read_text_auto(p)
    assert text == "中文 GBK 编码的内容" and enc == "gb18030"


def test_read_binary_never_crashes(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(bytes(range(256)) * 16)
    text, _ = read_text_auto(p)
    assert isinstance(text, str) and text  # replacement decode, no exception
