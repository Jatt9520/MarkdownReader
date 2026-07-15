"""Live Markdown preview using QWebEngineView."""

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QTimer, QMarginsF
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings, QWebEngineProfile

from markdownreader.renderer import render_with_theme
from markdownreader.settings import Settings


class PreviewWebPage(QWebEnginePage):
    """Custom web page that suppresses external link navigation."""

    link_clicked = pyqtSignal(str)

    def acceptNavigationRequest(self, url: QUrl, nav_type: QWebEnginePage.NavigationType, is_main_frame: bool):
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked and url.scheme() in ("http", "https"):
            self.link_clicked.emit(url.toString())
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class MarkdownPreview(QWidget):
    """Rendered markdown preview panel."""

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._current_html = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._web_view = QWebEngineView()
        self._page = PreviewWebPage(self._web_view)
        self._web_view.setPage(self._page)

        # Enable dark mode and smooth scrolling
        settings = self._web_view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

        layout.addWidget(self._web_view)

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
        self._web_view.setHtml(html, QUrl("file:///"))

    def set_theme(self, theme: str):
        """Re-render current content with a new theme."""
        if self._current_html:
            from markdownreader.renderer import render_markdown
            # We need to re-render from raw text, so we store it
            pass

    def show_placeholder(self):
        self._web_view.hide()
        self._placeholder.show()

    def hide_placeholder(self):
        self._placeholder.hide()
        self._web_view.show()

    def get_html(self) -> str:
        return self._current_html

    def print_to_pdf(self, output_path: Path, callback=None):
        """Export the current view to PDF."""
        self._page.printToPdf(str(output_path), callback)

    def zoom_in(self):
        current = self._web_view.zoomFactor()
        self._web_view.setZoomFactor(min(current + 0.1, 3.0))

    def zoom_out(self):
        current = self._web_view.zoomFactor()
        self._web_view.setZoomFactor(max(current - 0.1, 0.3))

    def zoom_reset(self):
        self._web_view.setZoomFactor(1.0)
