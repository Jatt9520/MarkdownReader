"""Shared utilities: file helpers, encoding detection, keyboard shortcuts."""

from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

# Supported file extensions
MARKDOWN_EXTENSIONS = {
    ".md", ".markdown", ".mdown", ".mkd", ".mkdn", ".mdwn", ".livemd",
    ".qmd", ".rmd", ".txt", ".text", ".rst",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

# Decode order: explicit UTF-8 BOM, plain UTF-8, then GB18030 (superset of
# GBK/GB2312, common on Chinese Windows). GB18030 accepts most byte streams,
# so it comes after UTF-8; the final pass never fails and never opens empty.
_UTF8_BOM = b"\xef\xbb\xbf"


def is_markdown_file(path: Path) -> bool:
    return path.suffix.lower() in MARKDOWN_EXTENSIONS


def is_image_file(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def read_text_auto(path: Path) -> tuple[str, str]:
    """Read a text file, trying common encodings; returns (text, encoding).

    The last candidate decodes with replacement so a file always opens
    instead of erroring out.
    """
    raw = path.read_bytes()
    if raw.startswith(_UTF8_BOM):
        return raw.decode("utf-8-sig"), "utf-8-sig"
    for encoding in ("utf-8", "gb18030"):
        try:
            return raw.decode(encoding), encoding
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8"


def count_words(text: str) -> tuple[int, int]:
    """Return (visible characters, words) for mixed CJK/Latin text.

    CJK characters count as one word each; Latin/digit runs count as
    one word per whitespace-delimited run.
    """
    import re
    visible = re.sub(r"\s+", "", text)
    cjk = len(re.findall(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", text))
    latin = len(re.findall(r"[A-Za-z0-9_]+", text))
    return len(visible), cjk + latin


def make_app_icon():
    """Programmatic app icon: dark rounded square with a markdown-style M↓."""
    from PyQt5.QtCore import QRectF
    from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap

    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#0d1117"))
    painter.setPen(QPen(QColor("#30363d"), 4))
    painter.drawRoundedRect(QRectF(6, 6, size - 12, size - 12), 24, 24)
    painter.setFont(QFont("Segoe UI", 52, QFont.Bold))
    painter.setPen(QColor("#c9d1d9"))
    painter.drawText(QRectF(0, 4, size * 0.62, size - 8), Qt.AlignCenter, "M")
    painter.setPen(QColor("#58a6ff"))
    painter.drawText(QRectF(size * 0.52, 4, size * 0.44, size - 8), Qt.AlignCenter, "↓")
    painter.end()
    return QIcon(pixmap)


# Keyboard shortcuts
SHORTCUTS = {
    "open_file": QKeySequence.StandardKey.Open,
    "save_file": QKeySequence.StandardKey.Save,
    "save_as": QKeySequence("Ctrl+Shift+S"),
    "new_file": QKeySequence.StandardKey.New,
    "close_file": QKeySequence("Ctrl+W"),
    "quit": QKeySequence.StandardKey.Quit,
    "find": QKeySequence.StandardKey.Find,
    "find_next": QKeySequence.StandardKey.FindNext,
    "find_prev": QKeySequence.StandardKey.FindPrevious,
    "toggle_sidebar": QKeySequence("Ctrl+B"),
    "toggle_theme": QKeySequence("Ctrl+Shift+T"),
    "zoom_in": QKeySequence.StandardKey.ZoomIn,
    "zoom_out": QKeySequence.StandardKey.ZoomOut,
    "zoom_reset": QKeySequence("Ctrl+0"),
    "export_pdf": QKeySequence("Ctrl+E"),
    "reload": QKeySequence("F5"),
    "focus_editor": QKeySequence("Ctrl+1"),
    "focus_preview": QKeySequence("Ctrl+2"),
    "toggle_highlight": QKeySequence("Ctrl+Shift+H"),
}
