"""Markdown text editor panel with line numbers and syntax awareness."""

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtWidgets import (
    QPlainTextEdit, QWidget, QVBoxLayout, QShortcut,
    QSizePolicy,
)

from markdownreader.utils import SHORTCUTS


class LineNumberArea(QWidget):
    """Gutter widget that draws line numbers."""

    def __init__(self, editor: "MarkdownEditor"):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return self._editor.line_number_area_size_hint()

    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)


class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    """Markdown syntax highlighting for the editor, themed for the pane."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []
        self.set_theme("dark")

    def set_theme(self, theme: str):
        if theme == "light":
            palette = [
                # headings
                (QColor("#0550ae"), None, False, False, r"^#{1,6}\s+.*$"),
                # bold
                (QColor("#1f2328"), None, True, False, r"\*\*[^*]+\*\*"),
                # italic
                (QColor("#57606a"), None, False, True, r"(?<!\*)\*(?!\*)[^*]+\*(?!\*)"),
                # inline code
                (QColor("#8250df"), QColor("#f6f8fa"), False, False, r"`[^`]+`"),
                # links
                (QColor("#0a3069"), None, False, True, r"\[([^\]]+)\]\([^\)]+\)"),
                # blockquote
                (QColor("#57606a"), None, False, True, r"^>\s+.*$"),
                # horizontal rule
                (QColor("#d0d7de"), None, False, False, r"^(-{3,}|\*{3,}|_{3,})$"),
                # list markers
                (QColor("#cf222e"), None, False, False, r"^(\s*[-*+]|\s*\d+\.)\s"),
            ]
        else:
            palette = [
                (QColor("#79c0ff"), None, False, False, r"^#{1,6}\s+.*$"),
                (QColor("#e6edf3"), None, True, False, r"\*\*[^*]+\*\*"),
                (QColor("#c9d1d9"), None, False, True, r"(?<!\*)\*(?!\*)[^*]+\*(?!\*)"),
                (QColor("#79c0ff"), QColor("#161b22"), False, False, r"`[^`]+`"),
                (QColor("#58a6ff"), None, False, True, r"\[([^\]]+)\]\([^\)]+\)"),
                (QColor("#8b949e"), None, False, True, r"^>\s+.*$"),
                (QColor("#30363d"), None, False, False, r"^(-{3,}|\*{3,}|_{3,})$"),
                (QColor("#ff7b72"), None, False, False, r"^(\s*[-*+]|\s*\d+\.)\s"),
            ]

        self._rules = []
        for color, bg, bold, italic, pattern in palette:
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            if bg:
                fmt.setBackground(bg)
            if bold:
                fmt.setFontWeight(QFont.Bold)
            if italic:
                fmt.setFontItalic(True)
            self._rules.append((fmt, pattern))
        self.rehighlight()

    def highlightBlock(self, text: str):
        import re
        for fmt, pattern in self._rules:
            for m in re.finditer(pattern, text, re.MULTILINE):
                start = m.start()
                length = m.end() - start
                self.setFormat(start, length, fmt)


class MarkdownEditor(QPlainTextEdit):
    """Text editor with line numbers and live change notification."""

    content_changed = pyqtSignal()

    # Gutter colors per theme: (background, current line, other lines)
    GUTTER_COLORS = {
        "dark": ("#0d1117", "#58a6ff", "#484f58"),
        "light": ("#f6f8fa", "#0969da", "#8c959f"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file: Path | None = None
        self._theme = "dark"
        self._change_timer = QTimer()
        self._change_timer.setSingleShot(True)
        self._change_timer.setInterval(300)
        self._change_timer.timeout.connect(self.content_changed.emit)

        self._setup_editor()
        self._setup_line_numbers()
        self._setup_highlighter()

    def set_theme(self, theme: str):
        """Restyle gutter and syntax colors for the given theme."""
        self._theme = theme
        self._highlighter.set_theme(theme)
        self._line_area.update()

    def _setup_editor(self):
        font = QFont("Cascadia Code", 14)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Dark editor styling
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                selection-background-color: #264f78;
                padding: 8px 8px 8px 4px;
            }
        """)

        self.textChanged.connect(self._on_text_changed)

    def _setup_line_numbers(self):
        self._line_area = LineNumberArea(self)
        self.blockCountChanged.connect(self._update_line_area_width)
        self.updateRequest.connect(self._update_line_area)
        self._update_line_area_width(0)

    def _setup_highlighter(self):
        self._highlighter = MarkdownSyntaxHighlighter(self.document())

    def line_number_area_size_hint(self):
        digits = max(1, len(str(self.blockCount())))
        return self.fontMetrics().horizontalAdvance("9") * digits + 16

    def _update_line_area_width(self, _):
        self.setViewportMargins(self.line_number_area_size_hint(), 0, 0, 0)

    def _update_line_area(self, rect, dy):
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(cr.left(), cr.top(), self.line_number_area_size_hint(), cr.height())

    def line_number_area_paint_event(self, event):
        from PyQt5.QtGui import QPainter, QFont
        gutter_bg, current_color, number_color = self.GUTTER_COLORS.get(self._theme, self.GUTTER_COLORS["dark"])
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), QColor(gutter_bg))

        font = QFont("Cascadia Code", 11)
        font.setStyleHint(QFont.Monospace)
        painter.setFont(font)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        # Current line number
        current_line = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if block_number == current_line:
                    painter.setPen(QColor(current_color))
                else:
                    painter.setPen(QColor(number_color))
                painter.drawText(
                    0, top, self._line_area.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
        painter.end()

    def _on_text_changed(self):
        self._change_timer.start()

    @property
    def current_file(self) -> Path | None:
        return self._current_file

    @current_file.setter
    def current_file(self, path: Path | None):
        self._current_file = path

    def set_content(self, text: str):
        self.blockSignals(True)
        self.setPlainText(text)
        self.blockSignals(False)
        self.content_changed.emit()

    def get_content(self) -> str:
        return self.toPlainText()
