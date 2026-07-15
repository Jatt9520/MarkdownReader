"""File browser sidebar — tree view of the filesystem."""

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QLabel, QHBoxLayout,
    QLineEdit, QFileSystemModel, QHeaderView, QToolButton, QSizePolicy,
)

from markdownreader.utils import is_markdown_file


class Sidebar(QWidget):
    """Collapsible file browser sidebar with tree view."""

    file_selected = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_dir: Path | None = None
        self._setup_ui()
        self.setMinimumWidth(160)
        self.setMaximumWidth(400)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 6, 8, 6)

        self._title = QLabel("文件")
        self._title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8b949e;")
        header_layout.addWidget(self._title)

        header_layout.addStretch()

        # Collapse button
        self._collapse_btn = QToolButton()
        self._collapse_btn.setText("◀")
        self._collapse_btn.setFixedSize(20, 20)
        self._collapse_btn.setStyleSheet("""
            QToolButton { border: none; color: #8b949e; font-size: 10px; }
            QToolButton:hover { color: #c9d1d9; }
        """)
        self._collapse_btn.clicked.connect(self._toggle_collapse)
        header_layout.addWidget(self._collapse_btn)

        layout.addWidget(header)

        # Tree view
        self._tree = QTreeView()
        self._tree.setHeaderHidden(True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(16)
        self._tree.setExpandsOnDoubleClick(True)
        self._tree.setUniformRowHeights(True)
        self._tree.clicked.connect(self._on_item_clicked)

        self._model = QStandardItemModel()
        self._tree.setModel(self._model)

        layout.addWidget(self._tree)

    def set_root(self, path: Path):
        """Set the root directory for the file tree."""
        if not path.is_dir():
            path = path.parent

        self._current_dir = path
        self._title.setText(path.name or str(path))
        self._build_tree(path)

    def _build_tree(self, root: Path):
        """Recursively build the file tree."""
        self._model.clear()
        root_item = self._model.invisibleRootItem()
        self._add_directory(root_item, root, depth=0, max_depth=4)

    def _add_directory(self, parent_item: QStandardItem, directory: Path, depth: int, max_depth: int):
        if depth > max_depth:
            return

        try:
            entries = sorted(directory.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return

        for entry in entries:
            if entry.name.startswith(".") and entry.name != ".gitignore":
                continue
            if entry.is_dir() and entry.name in {"node_modules", "__pycache__", ".git", ".venv", "venv", "dist", "build"}:
                continue

            item = QStandardItem(entry.name)
            item.setData(str(entry), Qt.UserRole)
            item.setEditable(False)

            if entry.is_dir():
                item.setFont(QFont("Segoe UI", 9))
                self._add_directory(item, entry, depth + 1, max_depth)
            else:
                item.setFont(QFont("Segoe UI", 9))
                # Dim non-markdown files slightly
                if not is_markdown_file(entry):
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor("#6e7681"))

            parent_item.appendRow(item)

    def _on_item_clicked(self, index):
        path_str = self._model.data(index, Qt.UserRole)
        if path_str:
            path = Path(path_str)
            if path.is_file():
                self.file_selected.emit(path)

    def _toggle_collapse(self):
        if self._tree.isVisible():
            self._tree.hide()
            self._collapse_btn.setText("▶")
        else:
            self._tree.show()
            self._collapse_btn.setText("◀")
