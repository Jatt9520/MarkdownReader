"""Persistent application settings (theme, font size, window state)."""

import json
from pathlib import Path

from PyQt5.QtCore import QSettings


class Settings:
    """Thin wrapper around QSettings with typed accessors."""

    def __init__(self):
        self._qs = QSettings("MarkdownReader", "MarkdownReader")

    # --- Theme ---
    @property
    def theme(self) -> str:
        return self._qs.value("theme", "dark", type=str)

    @theme.setter
    def theme(self, value: str):
        self._qs.setValue("theme", value)

    # --- Font size ---
    @property
    def editor_font_size(self) -> int:
        return int(self._qs.value("editor_font_size", 14))

    @editor_font_size.setter
    def editor_font_size(self, value: int):
        self._qs.setValue("editor_font_size", value)

    @property
    def preview_font_size(self) -> int:
        return int(self._qs.value("preview_font_size", 16))

    @preview_font_size.setter
    def preview_font_size(self, value: int):
        self._qs.setValue("preview_font_size", value)

    # --- Window geometry ---
    @property
    def window_geometry(self) -> bytes | None:
        return self._qs.value("window_geometry")

    @window_geometry.setter
    def window_geometry(self, value: bytes):
        self._qs.setValue("window_geometry", value)

    @property
    def window_state(self) -> bytes | None:
        return self._qs.value("window_state")

    @window_state.setter
    def window_state(self, value: bytes):
        self._qs.setValue("window_state", value)

    # --- Sidebar width ---
    @property
    def sidebar_width(self) -> int:
        return int(self._qs.value("sidebar_width", 220))

    @sidebar_width.setter
    def sidebar_width(self, value: int):
        self._qs.setValue("sidebar_width", value)

    # --- Code highlighting ---
    @property
    def code_highlight_enabled(self) -> bool:
        return bool(self._qs.value("code_highlight_enabled", True, type=bool))

    @code_highlight_enabled.setter
    def code_highlight_enabled(self, value: bool):
        self._qs.setValue("code_highlight_enabled", value)

    # --- Recent files ---
    @property
    def recent_files(self) -> list[str]:
        raw = self._qs.value("recent_files", [], type=list)
        return raw if isinstance(raw, list) else []

    @recent_files.setter
    def recent_files(self, value: list[str]):
        self._qs.setValue("recent_files", value)

    def add_recent(self, path: str, max_items: int = 10):
        files = [f for f in self.recent_files if f != path]
        files.insert(0, path)
        self.recent_files = files[:max_items]

    def load(self):
        pass  # QSettings auto-loads on first access

    def save(self):
        self._qs.sync()
