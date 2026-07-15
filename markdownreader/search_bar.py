"""Search and replace bar widget."""

from PyQt5.QtCore import Qt, pyqtSignal, QRegExp
from PyQt5.QtGui import QTextDocument, QTextCursor, QColor
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QToolButton, QLabel, QCheckBox,
    QVBoxLayout, QSizePolicy,
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
        self._search_input.setPlaceholderText("Search...")
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

        self._match_label = QLabel("0 results")
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
        self._case_cb.setToolTip("Case sensitive")
        self._case_cb.setStyleSheet(opt_style)
        self._case_cb.toggled.connect(self._on_search_changed)
        row.addWidget(self._case_cb)

        self._regex_cb = QCheckBox(".*")
        self._regex_cb.setToolTip("Regular expression")
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
            self._clear_highlights()
            self._match_label.setText("0 results")
            return

        flags = QTextDocument.FindFlags()
        if self._case_cb.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self._regex_cb.isChecked():
            flags |= QTextDocument.FindRegularExpression

        # Search forward or backward
        if direction > 0:
            found = self._editor.find(text, flags)
        elif direction < 0:
            flags |= QTextDocument.FindBackward
            found = self._editor.find(text, flags)
        else:
            # Initial search — move to start and find all
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self._editor.setTextCursor(cursor)
            found = self._editor.find(text, flags)

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

        self._match_label.setText(f"{count} result{'s' if count != 1 else ''}")

    def _clear_highlights(self):
        cursor = self._editor.textCursor()
        cursor.clearSelection()
        self._editor.setTextCursor(cursor)
