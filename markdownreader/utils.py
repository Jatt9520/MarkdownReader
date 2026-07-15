"""Shared utilities: file helpers, keyboard shortcut definitions."""

from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

# Supported file extensions
MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd", ".txt", ".rst"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


def is_markdown_file(path: Path) -> bool:
    return path.suffix.lower() in MARKDOWN_EXTENSIONS


def is_image_file(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


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
