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
    """Lightweight Markdown syntax highlighting for the editor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        # Headings
        fmt_h = QTextCharFormat()
        fmt_h.setForeground(QColor("#79c0ff"))
        fmt_h.setFontWeight(QFont.Bold)
        self._rules.append((fmt_h, r"^#{1,6}\s+.*$"))

        # Bold
        fmt_bold = QTextCharFormat()
        fmt_bold.setFontWeight(QFont.Bold)
        fmt_bold.setForeground(QColor("#e6edf3"))
        self._rules.append((fmt_bold, r"\*\*[^*]+\*\*"))

        # Italic
        fmt_italic = QTextCharFormat()
        fmt_italic.setFontItalic(True)
        fmt_italic.setForeground(QColor("#c9d1d9"))
        self._rules.append((fmt_italic, r"(?<!\*)\*(?!\*)[^*]+\*(?!\*)"))

        # Inline code
        fmt_code = QTextCharFormat()
        fmt_code.setForeground(QColor("#79c0ff"))
        fmt_code.setBackground(QColor("#161b22"))
        self._rules.append((fmt_code, r"`[^`]+`"))

        # Links
        fmt_link = QTextCharFormat()
        fmt_link.setForeground(QColor("#58a6ff"))
        fmt_link.setFontUnderline(True)
        self._rules.append((fmt_link, r"\[([^\]]+)\]\([^\)]+\)"))

        # Blockquote
        fmt_bq = QTextCharFormat()
        fmt_bq.setForeground(QColor("#8b949e"))
        fmt_bq.setFontItalic(True)
        self._rules.append((fmt_bq, r"^>\s+.*$"))

        # Horizontal rule
        fmt_hr = QTextCharFormat()
        fmt_hr.setForeground(QColor("#30363d"))
        self._rules.append((fmt_hr, r"^(-{3,}|\*{3,}|_{3,})$"))

        # List markers
        fmt_list = QTextCharFormat()
        fmt_list.setForeground(QColor("#ff7b72"))
        self._rules.append((fmt_list, r"^(\s*[-*+]|\s*\d+\.)\s"))

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file: Path | None = None
        self._change_timer = QTimer()
        self._change_timer.setSingleShot(True)
        self._change_timer.setInterval(300)
        self._change_timer.timeout.connect(self.content_changed.emit)

        self._setup_editor()
        self._setup_line_numbers()
        self._setup_highlighter()

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
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), QColor("#0d1117"))

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
                    painter.setPen(QColor("#58a6ff"))
                else:
                    painter.setPen(QColor("#484f58"))
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
