"""Live Markdown preview using QTextBrowser."""

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser

from markdownreader.renderer import render_with_theme
from markdownreader.settings import Settings


class MarkdownPreview(QWidget):
    """Rendered markdown preview panel."""

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._current_html = ""
        self._zoom_level = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._text_browser = QTextBrowser()
        self._text_browser.setOpenExternalLinks(True)
        self._text_browser.setFont(QFont("Segoe UI", self._settings.preview_font_size))
        layout.addWidget(self._text_browser)

        # Placeholder when no file is open
        self._placeholder = QLabel("Open a Markdown file to preview\n(Ctrl+O)")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet("color: #8b949e; font-size: 16px;")
        self._placeholder.hide()
        layout.addWidget(self._placeholder)

    def update_preview(self, markdown_text: str):
        """Re-render the preview with new markdown content."""
        html = render_with_theme(markdown_text, self._settings.theme, self._settings,
                                  self._settings.code_highlight_enabled)
        self._current_html = html
        self._text_browser.setHtml(html)

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
