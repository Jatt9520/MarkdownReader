"""Live Markdown preview using QTextBrowser."""

import os
from pathlib import Path

from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser

from markdownreader.renderer import render_document
from markdownreader.settings import Settings


class MarkdownPreview(QWidget):
    """Rendered markdown preview panel."""

    outline_changed = pyqtSignal(list)

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._current_html = ""
        self._zoom_level = 0
        self._base_dir: Path | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._text_browser = QTextBrowser()
        self._text_browser.setOpenExternalLinks(True)
        self._text_browser.setFont(QFont("Segoe UI", self._settings.preview_font_size))
        layout.addWidget(self._text_browser)

        # Placeholder when no file is open
        self._placeholder = QLabel("打开 Markdown 文件以预览\n(Ctrl+O)")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet("color: #8b949e; font-size: 16px;")
        self._placeholder.hide()
        layout.addWidget(self._placeholder)

    def set_base_dir(self, directory: Path | None):
        """Directory relative image/link paths resolve against."""
        self._base_dir = directory

    def update_preview(self, markdown_text: str):
        """Re-render the preview with new markdown content."""
        html, outline = render_document(markdown_text, self._settings.theme, self._settings,
                                        self._settings.code_highlight_enabled)
        self._current_html = html
        document = self._text_browser.document()
        if self._base_dir is not None:
            document.setBaseUrl(QUrl.fromLocalFile(str(self._base_dir) + os.sep))
        else:
            document.setBaseUrl(QUrl())
        self._text_browser.setHtml(html)
        self.outline_changed.emit(outline)

    def scroll_to_heading(self, anchor: str):
        """Jump to a heading anchor injected by the renderer."""
        self._text_browser.scrollToAnchor(anchor)

    def show_placeholder(self):
        self._text_browser.hide()
        self._placeholder.show()

    def hide_placeholder(self):
        self._placeholder.hide()
        self._text_browser.show()

    def get_html(self) -> str:
        return self._current_html

    def print_to_pdf(self, output_path: str):
        """Export current view to PDF via QPrinter."""
        from PyQt5.QtPrintSupport import QPrinter
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(output_path)
        printer.setPageSize(QPrinter.A4)
        self._text_browser.document().print_(printer)

    def zoom_in(self):
        self._zoom_level = min(self._zoom_level + 1, 10)
        self._text_browser.zoomIn(1)

    def zoom_out(self):
        self._zoom_level = max(self._zoom_level - 1, -5)
        self._text_browser.zoomOut(1)

    def zoom_reset(self):
        self._text_browser.zoomIn(-self._zoom_level) if self._zoom_level > 0 else self._text_browser.zoomOut(-self._zoom_level)
        self._zoom_level = 0
