"""Search and replace bar widget."""

from PyQt5.QtGui import QTextDocument, QTextCursor
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QToolButton, QLabel, QCheckBox,
    QVBoxLayout,
)


class SearchBar(QWidget):
    """Find bar with regex support, case sensitivity, and match highlighting."""

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self._editor = editor
        self._matches = []
        self._current_match = -1
        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Main search row
        row = QHBoxLayout()
        row.setSpacing(6)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("搜索...")
        self._search_input.setFixedWidth(300)
        self._search_input.textChanged.connect(self._on_search_changed)
        self._search_input.returnPressed.connect(self.find_next)
        self._search_input.setStyleSheet("""
            QLineEdit {
                background: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #58a6ff;
            }
        """)
        row.addWidget(self._search_input)

        self._match_label = QLabel("0 个结果")
        self._match_label.setStyleSheet("color: #8b949e; font-size: 12px; min-width: 70px;")
        row.addWidget(self._match_label)

        # Navigation buttons
        btn_style = """
            QToolButton {
                border: 1px solid #30363d;
                border-radius: 4px;
                color: #c9d1d9;
                background: #21262d;
                padding: 4px 10px;
                font-size: 12px;
            }
            QToolButton:hover { background: #30363d; border-color: #484f58; }
            QToolButton:pressed { background: #484f58; }
        """

        self._prev_btn = QToolButton(text="▲")
        self._prev_btn.setFixedSize(30, 26)
        self._prev_btn.setStyleSheet(btn_style)
        self._prev_btn.clicked.connect(self.find_prev)
        row.addWidget(self._prev_btn)

        self._next_btn = QToolButton(text="▼")
        self._next_btn.setFixedSize(30, 26)
        self._next_btn.setStyleSheet(btn_style)
        self._next_btn.clicked.connect(self.find_next)
        row.addWidget(self._next_btn)

        # Options
        opt_style = "color: #8b949e; font-size: 12px; padding: 2px;"
        self._case_cb = QCheckBox("Aa")
        self._case_cb.setToolTip("区分大小写")
        self._case_cb.setStyleSheet(opt_style)
        self._case_cb.toggled.connect(self._on_search_changed)
        row.addWidget(self._case_cb)

        self._regex_cb = QCheckBox(".*")
        self._regex_cb.setToolTip("正则表达式")
        self._regex_cb.setStyleSheet(opt_style)
        self._regex_cb.toggled.connect(self._on_search_changed)
        row.addWidget(self._regex_cb)

        row.addStretch()

        self._close_btn = QToolButton(text="✕")
        self._close_btn.setFixedSize(26, 26)
        self._close_btn.setStyleSheet(btn_style)
        self._close_btn.clicked.connect(self.hide)
        row.addWidget(self._close_btn)

        layout.addLayout(row)

        self.setStyleSheet("background: #161b22; border-bottom: 1px solid #21262d; border-radius: 0;")

    def toggle(self):
        if self.isVisible():
            self.hide()
            self._editor.setFocus()
        else:
            self.show()
            self._search_input.setFocus()
            # Pre-fill with selected text
            cursor = self._editor.textCursor()
            if cursor.hasSelection():
                self._search_input.setText(cursor.selectedText())
            self._search_input.selectAll()

    def find_next(self):
        self._search(1)

    def find_prev(self):
        self._search(-1)

    def _on_search_changed(self):
        self._search(0)

    def _search(self, direction: int):
        text = self._search_input.text()
        if not text:
            self._match_label.setText("0 个结果")
            return

        flags = QTextDocument.FindFlags()
        if self._case_cb.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self._regex_cb.isChecked():
            flags |= QTextDocument.FindRegularExpression

        if direction > 0:
            # Wrap around: restart from the top when the end is reached
            if not self._editor.find(text, flags):
                cursor = self._editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                self._editor.setTextCursor(cursor)
                self._editor.find(text, flags)
        elif direction < 0:
            flags |= QTextDocument.FindBackward
            if not self._editor.find(text, flags):
                cursor = self._editor.textCursor()
                cursor.movePosition(QTextCursor.End)
                self._editor.setTextCursor(cursor)
                self._editor.find(text, flags)
        else:
            # Initial search — jump to the first match from the top
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self._editor.setTextCursor(cursor)
            self._editor.find(text, flags)

        # Count all matches
        self._count_matches(text, flags)

    def _count_matches(self, text: str, flags: QTextDocument.FindFlags):
        doc = self._editor.document()
        cursor = QTextCursor(doc)
        count = 0
        while True:
            cursor = doc.find(text, cursor, flags)
            if cursor.isNull():
                break
            count += 1

        self._match_label.setText(f"{count} 个结果")

    def _clear_highlights(self):
        cursor = self._editor.textCursor()
        cursor.clearSelection()
        self._editor.setTextCursor(cursor)

    def apply_theme(self, theme: str):
        """Restyle the bar for the active theme."""
        if theme == "dark":
            bar_bg, border, fg, muted = "#161b22", "#21262d", "#c9d1d9", "#8b949e"
            input_bg, input_border, accent = "#0d1117", "#30363d", "#58a6ff"
            btn_bg, btn_hover, btn_pressed = "#21262d", "#30363d", "#484f58"
        else:
            bar_bg, border, fg, muted = "#f6f8fa", "#d0d7de", "#1f2328", "#656d76"
            input_bg, input_border, accent = "#ffffff", "#d0d7de", "#0969da"
            btn_bg, btn_hover, btn_pressed = "#ffffff", "#eaeef2", "#d0d7de"

        self.setStyleSheet(
            f"background: {bar_bg}; border-bottom: 1px solid {border};")
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {input_bg}; color: {fg};
                border: 1px solid {input_border}; border-radius: 6px;
                padding: 5px 10px; font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {accent}; }}
        """)
        self._match_label.setStyleSheet(f"color: {muted}; font-size: 12px; min-width: 70px;")
        btn_style = f"""
            QToolButton {{
                border: 1px solid {input_border}; border-radius: 4px;
                color: {fg}; background: {btn_bg};
                padding: 4px 10px; font-size: 12px;
            }}
            QToolButton:hover {{ background: {btn_hover}; }}
            QToolButton:pressed {{ background: {btn_pressed}; }}
        """
        for button in (self._prev_btn, self._next_btn, self._close_btn):
            button.setStyleSheet(btn_style)
        opt_style = f"color: {muted}; font-size: 12px; padding: 2px;"
        self._case_cb.setStyleSheet(opt_style)
        self._regex_cb.setStyleSheet(opt_style)
