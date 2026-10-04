"""AI assistant controller: context-menu actions and request lifecycle."""

import time

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMenu, QMessageBox

from markdownreader.ai.client import AIClient
from markdownreader.ai.presets import ACTION_TITLES, build_prompt

# 续写只带光标前的尾部上下文，避免大文档撑爆请求
CONTINUE_CONTEXT_CHARS = 4000


class AIAssistant(QObject):
    """Wires the editor's context menu to AI actions; owns the client."""

    def __init__(self, settings, editor, statusbar, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._editor = editor
        self._statusbar = statusbar
        self._window = parent
        self._pending = None
        self._started_at = 0.0
        self._client = AIClient(self)
        self._client.finished.connect(self._on_finished)
        self._client.failed.connect(self._on_failed)
        editor.ai_menu_hook = self._build_menu

    # ─────────────────────────── Menu ───────────────────────────

    def _build_menu(self, menu: QMenu):
        ai_menu = QMenu("AI 助手", menu)
        for title, action_id in ACTION_TITLES:
            ai_menu.addAction(title, lambda checked=False, a=action_id: self.run(a))
        ai_menu.addSeparator()
        ai_menu.addAction("AI 设置...", self._open_settings)
        first = menu.actions()[0] if menu.actions() else None
        if first is not None:
            menu.insertMenu(first, ai_menu)
            menu.insertSeparator(first)
        else:
            menu.addMenu(ai_menu)

    # ─────────────────────────── Actions ───────────────────────────

    def is_configured(self) -> bool:
        return self._settings.ai_configured

    def run(self, action: str):
        if self._pending is not None:
            self._statusbar.showMessage("AI 正在处理上一条请求，请稍候", 3000)
            return
        if not self.is_configured():
            QMessageBox.information(
                self._window, "AI 助手",
                "尚未配置 AI 服务商。\n\n请在「设置 → AI 助手」中填入接口地址、"
                "API Key 和模型（支持 DeepSeek、Kimi、GLM、OpenAI、本地 Ollama 等）。")
            self._open_settings()
            return

        cursor = self._editor.textCursor()
        custom = None
        if action == "continue":
            text = self._editor.toPlainText()[:cursor.position()][-
                                                                CONTINUE_CONTEXT_CHARS:]
            if not text.strip():
                self._statusbar.showMessage("光标前没有可续写的内容", 3000)
                return
        else:
            text = cursor.selectedText().replace("\u2029", "\n")
            if not text.strip():
                self._statusbar.showMessage("请先选中文字", 3000)
                return
        if action == "custom":
            from PyQt5.QtWidgets import QInputDialog
            custom, ok = QInputDialog.getMultiLineText(
                self._window, "自定义指令", "输入要应用到所选文本的指令：", "")
            if not ok or not custom.strip():
                return

        system, user = build_prompt(action, text, custom)
        self._pending = (action, cursor)
        self._started_at = time.monotonic()
        self._statusbar.showMessage("AI 处理中…（完成后自动应用到文档）", 0)
        self._client.complete(
            self._settings.ai_api_base, self._settings.ai_api_key,
            self._settings.ai_model, system, user)

    def _open_settings(self):
        from markdownreader.ai.settings_dialog import AISettingsDialog
        dialog = AISettingsDialog(self._settings, self._window)
        if dialog.exec_() and self.is_configured():
            self._statusbar.showMessage("AI 助手已配置", 3000)

    # ─────────────────────────── Results ───────────────────────────

    def _on_finished(self, content: str, usage: str):
        if self._pending is None:
            return
        action, cursor = self._pending
        self._pending = None
        seconds = time.monotonic() - self._started_at

        if action == "explain":
            QMessageBox.information(self._window, "AI 解释", content)
        elif action == "summarize":
            if cursor.hasSelection():
                cursor.setPosition(max(cursor.anchor(), cursor.position()))
            cursor.insertText("\n\n" + content)
        elif action == "continue":
            cursor.clearSelection()
            cursor.insertText("\n\n" + content)
        else:  # polish / translate / custom: replace the selection
            cursor.insertText(content)

        note = f" · {usage}" if usage else ""
        self._statusbar.showMessage(f"AI 完成（{seconds:.1f}s{note}）", 5000)

    def _on_failed(self, message: str):
        self._pending = None
        self._statusbar.showMessage("AI 请求失败", 5000)
        QMessageBox.warning(self._window, "AI 请求失败", message)
