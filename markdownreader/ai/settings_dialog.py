"""Dialog for configuring the AI assistant (bring-your-own-key)."""

from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QVBoxLayout,
)

from markdownreader.ai.client import AIClient
from markdownreader.ai.presets import AI_PRESETS, PRESET_CUSTOM


class AISettingsDialog(QDialog):
    """Provider preset picker plus base URL / API key / model fields."""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._client = AIClient(self)
        self._client.finished.connect(self._on_test_ok)
        self._client.failed.connect(self._on_test_failed)

        self.setWindowTitle("AI 助手设置")
        self.setMinimumWidth(540)
        self._setup_ui()
        self._restore_theme(settings)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self._preset_combo = QComboBox()
        self._preset_combo.addItems([PRESET_CUSTOM] + list(AI_PRESETS))
        self._preset_combo.currentTextChanged.connect(self._on_preset_changed)
        form.addRow("服务商预设:", self._preset_combo)

        self._base_edit = QLineEdit(self._settings.ai_api_base)
        self._base_edit.setPlaceholderText("https://api.example.com/v1")
        form.addRow("接口地址:", self._base_edit)

        self._key_edit = QLineEdit(self._settings.ai_api_key)
        self._key_edit.setEchoMode(QLineEdit.Password)
        key_row = QHBoxLayout()
        key_row.addWidget(self._key_edit)
        self._show_key_cb = QCheckBox("显示")
        self._show_key_cb.toggled.connect(
            lambda checked: self._key_edit.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password))
        key_row.addWidget(self._show_key_cb)
        form.addRow("API Key:", key_row)

        self._model_edit = QLineEdit(self._settings.ai_model)
        self._model_edit.setPlaceholderText("模型名称，如 deepseek-chat")
        form.addRow("模型:", self._model_edit)

        layout.addLayout(form)

        note = QLabel(
            "兼容 OpenAI 接口格式的服务商均可使用（含本地 Ollama）。\n"
            "API Key 保存在本机注册表（明文）；请求内容仅发送给你选择的服务商，"
            "本应用不经手任何数据。")
        note.setWordWrap(True)
        note.setStyleSheet("color: #8b949e; font-size: 12px;")
        layout.addWidget(note)

        test_row = QHBoxLayout()
        self._test_btn = QPushButton("测试连接")
        self._test_btn.clicked.connect(self._on_test)
        test_row.addWidget(self._test_btn)
        self._test_result = QLabel("")
        test_row.addWidget(self._test_result, 1)
        layout.addLayout(test_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Restore the matching preset if the saved base matches one
        current_base = self._settings.ai_api_base.strip()
        for name, preset in AI_PRESETS.items():
            if preset["base"] == current_base:
                self._preset_combo.setCurrentText(name)
                break
        else:
            self._preset_combo.setCurrentText(PRESET_CUSTOM)

    def _restore_theme(self, settings):
        if settings.theme == "dark":
            self.setStyleSheet("""
                QDialog { background: #161b22; }
                QLabel { color: #c9d1d9; font-size: 13px; }
                QLineEdit, QComboBox {
                    background: #0d1117; color: #c9d1d9;
                    border: 1px solid #30363d; border-radius: 6px; padding: 5px 8px;
                }
                QCheckBox { color: #8b949e; }
                QPushButton {
                    background: #21262d; color: #c9d1d9;
                    border: 1px solid #30363d; border-radius: 6px; padding: 5px 14px;
                }
                QPushButton:hover { background: #30363d; }
            """)

    def _on_preset_changed(self, name: str):
        preset = AI_PRESETS.get(name)
        if not preset:
            return
        self._base_edit.setText(preset["base"])
        self._model_edit.setText(preset["model"])
        if preset.get("key") and not self._key_edit.text().strip():
            self._key_edit.setText(preset["key"])

    def _on_test(self):
        self._test_btn.setEnabled(False)
        self._test_result.setText("测试中…")
        self._client.complete(
            self._base_edit.text(), self._key_edit.text(), self._model_edit.text(),
            "You are a connection test. Reply with exactly: pong", "ping")

    def _on_test_ok(self, content: str, _usage: str):
        self._test_btn.setEnabled(True)
        self._test_result.setText("✓ 连接成功")

    def _on_test_failed(self, message: str):
        self._test_btn.setEnabled(True)
        self._test_result.setText(f"✗ {message.splitlines()[0]}")

    def accept(self):
        self._settings.ai_api_base = self._base_edit.text().strip()
        self._settings.ai_api_key = self._key_edit.text()
        self._settings.ai_model = self._model_edit.text().strip()
        super().accept()
