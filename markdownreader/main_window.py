"""Main application window — assembles all panels and manages state."""

import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QDragEnterEvent, QDropEvent, QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QAction, QMenuBar, QStatusBar,
    QToolBar, QLabel, QFileDialog, QMessageBox, QWidget, QVBoxLayout,
    QApplication, QSizePolicy, QShortcut,
)

from markdownreader.editor import MarkdownEditor
from markdownreader.preview import MarkdownPreview
from markdownreader.sidebar import Sidebar
from markdownreader.search_bar import SearchBar
from markdownreader.renderer import render_with_theme
from markdownreader.pdf_export import export_to_pdf
from markdownreader.settings import Settings
from markdownreader.utils import SHORTCUTS, is_markdown_file


class MainWindow(QMainWindow):
    """The main application window with editor, preview, sidebar, and search."""

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._current_file: Path | None = None
        self._last_rendered_text = ""

        self.setWindowTitle("MarkdownReader")
        self.setMinimumSize(900, 600)
        self._restore_geometry()

        self.setAcceptDrops(True)

        self._setup_ui()
        self._setup_menus()
        self._setup_shortcuts()
        self._setup_statusbar()

        self._apply_theme()

    def _restore_geometry(self):
        geom = self._settings.window_geometry
        if geom:
            self.restoreGeometry(geom)
        else:
            self.resize(1200, 800)

    # ──────────────────────────── UI Assembly ────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar(self)
        self._sidebar.file_selected.connect(self._on_sidebar_file_selected)

        # Editor
        self._editor = MarkdownEditor(self)
        self._editor.content_changed.connect(self._on_content_changed)

        # Preview
        self._preview = MarkdownPreview(self._settings, self)
        self._preview.show_placeholder()

        # Search bar (overlays above editor)
        self._search_bar = SearchBar(self._editor, self)

        # Search bar goes above editor
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self._search_bar)
        editor_layout.addWidget(self._editor)

        # Splitter: editor + preview
        self._splitter = QSplitter(Qt.Horizontal)
        self._splitter.setHandleWidth(3)
        self._splitter.setStyleSheet("""
            QSplitter::handle {
                background: #21262d;
            }
            QSplitter::handle:hover {
                background: #58a6ff;
            }
        """)

        # Wrap editor in another splitter with sidebar
        self._outer_splitter = QSplitter(Qt.Horizontal)
        self._outer_splitter.setHandleWidth(3)
        self._outer_splitter.setStyleSheet(self._splitter.styleSheet())

        self._outer_splitter.addWidget(self._sidebar)
        self._outer_splitter.addWidget(editor_container)
        self._outer_splitter.addWidget(self._preview)

        # Set initial sizes
        self._outer_splitter.setSizes([self._settings.sidebar_width, 400, 500])
        self._outer_splitter.setStretchFactor(0, 0)
        self._outer_splitter.setStretchFactor(1, 1)
        self._outer_splitter.setStretchFactor(2, 1)

        main_layout.addWidget(self._outer_splitter)

    def _setup_menus(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: #0d1117;
                color: #c9d1d9;
                border-bottom: 1px solid #21262d;
                padding: 2px 0;
                font-size: 13px;
            }
            QMenuBar::item {
                padding: 4px 10px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #21262d;
            }
            QMenu {
                background: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 4px 0;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QMenu::item:selected {
                background: #21262d;
            }
            QMenu::item:disabled {
                color: #484f58;
            }
            QMenu::separator {
                height: 1px;
                background: #21262d;
                margin: 4px 8px;
            }
            QMenu::icon {
                padding-left: 8px;
            }
        """)

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        self._action_new = QAction("新建(&N)", self)
        self._action_new.setShortcut(SHORTCUTS["new_file"])
        self._action_new.triggered.connect(self._new_file)
        file_menu.addAction(self._action_new)

        self._action_open = QAction("打开(&O)...", self)
        self._action_open.setShortcut(SHORTCUTS["open_file"])
        self._action_open.triggered.connect(self._open_file_dialog)
        file_menu.addAction(self._action_open)

        self._recent_menu = file_menu.addMenu("最近打开")
        self._update_recent_menu()

        file_menu.addSeparator()

        self._action_save = QAction("保存(&S)", self)
        self._action_save.setShortcut(SHORTCUTS["save_file"])
        self._action_save.triggered.connect(self._save_file)
        file_menu.addAction(self._action_save)

        self._action_save_as = QAction("另存为(&A)...", self)
        self._action_save_as.setShortcut(SHORTCUTS["save_as"])
        self._action_save_as.triggered.connect(self._save_file_as)
        file_menu.addAction(self._action_save_as)

        file_menu.addSeparator()

        self._action_export_pdf = QAction("导出PDF(&P)...", self)
        self._action_export_pdf.setShortcut(SHORTCUTS["export_pdf"])
        self._action_export_pdf.triggered.connect(self._export_pdf)
        file_menu.addAction(self._action_export_pdf)

        file_menu.addSeparator()

        self._action_quit = QAction("退出(&Q)", self)
        self._action_quit.setShortcut(SHORTCUTS["quit"])
        self._action_quit.triggered.connect(self.close)
        file_menu.addAction(self._action_quit)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        self._action_toggle_sidebar = QAction("切换侧边栏(&S)", self)
        self._action_toggle_sidebar.setShortcut(SHORTCUTS["toggle_sidebar"])
        self._action_toggle_sidebar.triggered.connect(self._toggle_sidebar)
        view_menu.addAction(self._action_toggle_sidebar)

        self._action_toggle_theme = QAction("切换主题(&T)", self)
        self._action_toggle_theme.setShortcut(SHORTCUTS["toggle_theme"])
        self._action_toggle_theme.triggered.connect(self._toggle_theme)
        view_menu.addAction(self._action_toggle_theme)

        self._action_toggle_highlight = QAction("切换代码高亮(&H)", self)
        self._action_toggle_highlight.setCheckable(True)
        self._action_toggle_highlight.setChecked(self._settings.code_highlight_enabled)
        self._action_toggle_highlight.setShortcut(SHORTCUTS["toggle_highlight"])
        self._action_toggle_highlight.triggered.connect(self._toggle_code_highlight)
        view_menu.addAction(self._action_toggle_highlight)

        view_menu.addSeparator()

        action_zoom_in = QAction("放大(&I)", self)
        action_zoom_in.setShortcut(SHORTCUTS["zoom_in"])
        action_zoom_in.triggered.connect(self._zoom_in)
        view_menu.addAction(action_zoom_in)

        action_zoom_out = QAction("缩小(&O)", self)
        action_zoom_out.setShortcut(SHORTCUTS["zoom_out"])
        action_zoom_out.triggered.connect(self._zoom_out)
        view_menu.addAction(action_zoom_out)

        action_zoom_reset = QAction("重置缩放(&R)", self)
        action_zoom_reset.setShortcut(SHORTCUTS["zoom_reset"])
        action_zoom_reset.triggered.connect(self._zoom_reset)
        view_menu.addAction(action_zoom_reset)

        view_menu.addSeparator()

        action_focus_editor = QAction("聚焦编辑器(&E)", self)
        action_focus_editor.setShortcut(SHORTCUTS["focus_editor"])
        action_focus_editor.triggered.connect(self._editor.setFocus)
        view_menu.addAction(action_focus_editor)

        action_focus_preview = QAction("聚焦预览(&P)", self)
        action_focus_preview.setShortcut(SHORTCUTS["focus_preview"])
        action_focus_preview.triggered.connect(lambda: self._preview.setFocus())
        view_menu.addAction(action_focus_preview)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        action_find = QAction("查找(&F)", self)
        action_find.setShortcut(SHORTCUTS["find"])
        action_find.triggered.connect(self._search_bar.toggle)
        edit_menu.addAction(action_find)

        action_find_next = QAction("查找下一个(&N)", self)
        action_find_next.setShortcut(SHORTCUTS["find_next"])
        action_find_next.triggered.connect(self._search_bar.find_next)
        edit_menu.addAction(action_find_next)

        action_find_prev = QAction("查找上一个(&P)", self)
        action_find_prev.setShortcut(SHORTCUTS["find_prev"])
        action_find_prev.triggered.connect(self._search_bar.find_prev)
        edit_menu.addAction(action_find_prev)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        action_about = QAction("关于(&A)", self)
        action_about.triggered.connect(self._show_about)
        help_menu.addAction(action_about)

    def _setup_shortcuts(self):
        """Additional keyboard shortcuts not attached to menu actions."""
        QShortcut(QKeySequence("Escape"), self, self._on_escape)

    def _setup_statusbar(self):
        self._statusbar = QStatusBar()
        self._statusbar.setStyleSheet("""
            QStatusBar {
                background: #0d1117;
                color: #8b949e;
                border-top: 1px solid #21262d;
                font-size: 12px;
                padding: 2px 8px;
            }
        """)
        self.setStatusBar(self._statusbar)

        self._file_label = QLabel("未打开文件")
        self._statusbar.addWidget(self._file_label)

        self._position_label = QLabel("")
        self._statusbar.addPermanentWidget(self._position_label)

        self._theme_label = QLabel(f"主题: {'暗色' if self._settings.theme == 'dark' else '亮色'}")
        self._statusbar.addPermanentWidget(self._theme_label)

        self._highlight_label = QLabel(
            f"高亮: {'开' if self._settings.code_highlight_enabled else '关'}"
        )
        self._statusbar.addPermanentWidget(self._highlight_label)

    # ──────────────────────────── File Operations ────────────────────────────

    def open_file(self, path: Path):
        """Open a markdown file for viewing and editing."""
        if not path.is_file():
            return

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = path.read_text(encoding="utf-8-sig")
            except Exception:
                QMessageBox.warning(self, "错误", f"无法读取文件:\n{path}")
                return

        self._current_file = path
        self._editor.current_file = path
        self._editor.set_content(text)
        self._update_title()
        self._file_label.setText(str(path.name))
        self._statusbar.showMessage(f"已打开 {path.name}", 3000)

        # Set sidebar root
        self._sidebar.set_root(path.parent)

        # Add to recent files
        self._settings.add_recent(str(path))
        self._update_recent_menu()

        # Show preview
        self._preview.hide_placeholder()
        self._on_content_changed()

    def _new_file(self):
        self._current_file = None
        self._editor.current_file = None
        self._editor.set_content("")
        self._update_title()
        self._file_label.setText("未命名")
        self._preview.show_placeholder()
        self._editor.setFocus()

    def _open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "打开 Markdown 文件",
            "",
            "Markdown 文件 (*.md *.markdown *.mdown *.mkd *.txt *.rst);;所有文件 (*)",
        )
        if path:
            self.open_file(Path(path))

    def _save_file(self):
        if self._current_file is None:
            self._save_file_as()
            return

        try:
            self._current_file.write_text(self._editor.get_content(), encoding="utf-8")
            self._statusbar.showMessage(f"已保存 {self._current_file.name}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存:\n{e}")

    def _save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "另存为",
            "",
            "Markdown 文件 (*.md);;所有文件 (*)",
        )
        if path:
            self._current_file = Path(path)
            self._editor.current_file = self._current_file
            self._save_file()
            self._update_title()

    def _export_pdf(self):
        if self._preview.get_html():
            export_to_pdf(self._preview._text_browser, self)
        else:
            QMessageBox.information(self, "导出", "没有可导出的内容，请先打开 Markdown 文件。")

    def _update_title(self):
        name = self._current_file.name if self._current_file else "未命名"
        self.setWindowTitle(f"{name} — MarkdownReader")

    def _update_recent_menu(self):
        self._recent_menu.clear()
        for file_path in self._settings.recent_files:
            p = Path(file_path)
            action = QAction(p.name, self)
            action.setToolTip(str(p))
            action.triggered.connect(lambda checked, fp=file_path: self.open_file(Path(fp)))
            self._recent_menu.addAction(action)
        if not self._settings.recent_files:
            action = QAction("(空)", self)
            action.setEnabled(False)
            self._recent_menu.addAction(action)

    # ──────────────────────────── Preview & Rendering ────────────────────────────

    def _on_content_changed(self):
        """Debounced content update → preview render."""
        text = self._editor.get_content()
        if text != self._last_rendered_text:
            self._last_rendered_text = text
            self._preview.update_preview(text)
            self._update_position_label()

    def _update_position_label(self):
        cursor = self._editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self._position_label.setText(f"行 {line}, 列 {col}")

    # ──────────────────────────── View Controls ────────────────────────────

    def _toggle_sidebar(self):
        if self._sidebar.isVisible():
            self._settings.sidebar_width = self._sidebar.width()
            self._sidebar.hide()
        else:
            self._sidebar.show()
            self._sidebar.setMinimumWidth(self._settings.sidebar_width)

    def _toggle_theme(self):
        new_theme = "light" if self._settings.theme == "dark" else "dark"
        self._settings.theme = new_theme
        self._apply_theme()
        self._theme_label.setText(f"主题: {'暗色' if new_theme == 'dark' else '亮色'}")
        self._on_content_changed()

    def _toggle_code_highlight(self, checked: bool):
        self._settings.code_highlight_enabled = checked
        self._action_toggle_highlight.setChecked(checked)
        self._highlight_label.setText(f"高亮: {'开' if checked else '关'}")
        self._on_content_changed()

    def _apply_theme(self):
        theme = self._settings.theme
        if theme == "dark":
            bg = "#0d1117"
            fg = "#c9d1d9"
            editor_bg = "#0d1117"
            editor_fg = "#c9d1d9"
            sidebar_bg = "#161b22"
            handle = "#21262d"
            sel_bg = "#264f78"
            hover_bg = "#1c2128"
        else:
            bg = "#ffffff"
            fg = "#1f2328"
            editor_bg = "#ffffff"
            editor_fg = "#1f2328"
            sidebar_bg = "#f6f8fa"
            handle = "#d0d7de"
            sel_bg = "#b3d7ff"
            hover_bg = "#eaeef2"

        self.setStyleSheet(f"""
            QMainWindow {{ background: {bg}; }}
            QWidget {{ color: {fg}; font-size: 13px; }}
        """)

        self._editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {editor_bg};
                color: {editor_fg};
                border: none;
                selection-background-color: {sel_bg};
                padding: 8px 8px 8px 4px;
            }}
        """)

        self._sidebar.setStyleSheet(f"""
            QWidget {{ background: {sidebar_bg}; }}
            QTreeView {{
                background: {sidebar_bg};
                color: {fg};
                border: none;
                outline: none;
                font-size: 13px;
            }}
            QTreeView::item {{
                padding: 3px 4px;
                border-radius: 4px;
                margin: 0 2px;
            }}
            QTreeView::item:selected {{
                background: {"#21262d" if theme == "dark" else "#d0d7de"};
            }}
            QTreeView::item:hover {{
                background: {hover_bg};
            }}
        """)

        self._splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {handle};
            }}
            QSplitter::handle:hover {{
                background: {"#58a6ff" if theme == "dark" else "#0969da"};
            }}
        """)
        self._outer_splitter.setStyleSheet(self._splitter.styleSheet())

    def _zoom_in(self):
        self._editor.zoomIn(1)
        self._preview.zoom_in()

    def _zoom_out(self):
        self._editor.zoomOut(1)
        self._preview.zoom_out()

    def _zoom_reset(self):
        font = self._editor.font()
        font.setPointSize(14)
        self._editor.setFont(font)
        self._preview.zoom_reset()

    def _show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("关于 MarkdownReader")
        msg.setIcon(QMessageBox.Information)
        msg.setTextFormat(Qt.RichText)
        msg.setText(
            "<h2>MarkdownReader</h2>"
            "<p>一款现代 Markdown 阅读器，支持实时预览</p>"
            "<p><b>功能:</b></p>"
            "<ul>"
            "<li>实时 Markdown 预览</li>"
            "<li>文件浏览器侧边栏</li>"
            "<li>代码语法高亮 (Pygments)</li>"
            "<li>暗色/亮色主题切换</li>"
            "<li>导出 PDF</li>"
            "<li>正则表达式搜索</li>"
            "<li>拖拽打开文件</li>"
            "<li>键盘快捷键</li>"
            "</ul>"
            "<p>版本 1.0.0</p>"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        if self._settings.theme == "dark":
            msg.setStyleSheet("""
                QMessageBox { background: #161b22; color: #c9d1d9; }
                QLabel { color: #c9d1d9; font-size: 13px; }
                QPushButton {
                    background: #21262d; color: #c9d1d9;
                    border: 1px solid #30363d; border-radius: 6px;
                    padding: 6px 16px; font-size: 13px;
                }
                QPushButton:hover { background: #30363d; }
            """)
        msg.exec_()

    # ──────────────────────────── Event Overrides ────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            if path.is_file():
                self.open_file(path)

    def _on_escape(self):
        if self._search_bar.isVisible():
            self._search_bar.hide()
            self._editor.setFocus()

    def _on_sidebar_file_selected(self, path: Path):
        if path.is_file() and is_markdown_file(path):
            self.open_file(path)

    def closeEvent(self, event):
        self._settings.window_geometry = self.saveGeometry()
        self._settings.save()
        super().closeEvent(event)
