"""Async client for OpenAI-compatible chat completion APIs (QtNetwork)."""

import json

from PyQt5.QtCore import QObject, QJsonDocument, QUrl, pyqtSignal
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


class AIClient(QObject):
    """One-shot chat completion requests; signals return to the event loop."""

    finished = pyqtSignal(str, str)  # assistant message content, usage note
    failed = pyqtSignal(str)         # human-readable error

    TIMEOUT_MS = 60_000

    def __init__(self, parent=None):
        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)
        self._reply = None

    @property
    def busy(self) -> bool:
        return self._reply is not None

    def cancel(self):
        if self._reply is not None:
            self._reply.abort()

    def complete(self, base: str, key: str, model: str, system: str, user: str):
        """POST one chat completion; results arrive via finished/failed."""
        if self._reply is not None:
            self.failed.emit("已有请求在进行中，请稍候")
            return
        if not base.strip() or not model.strip():
            self.failed.emit("接口地址或模型未配置")
            return

        request = QNetworkRequest(QUrl(base.rstrip("/") + "/chat/completions"))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        if key:
            request.setRawHeader(b"Authorization", b"Bearer " + key.encode("utf-8"))
        if hasattr(request, "setTransferTimeout"):
            request.setTransferTimeout(self.TIMEOUT_MS)

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.7,
            "stream": False,
        }
        body = QJsonDocument(payload).toJson(QJsonDocument.Compact)

        reply = self._nam.post(request, body)
        self._reply = reply
        reply.finished.connect(lambda: self._on_finished(reply))

    def _on_finished(self, reply: QNetworkReply):
        self._reply = None
        reply.deleteLater()
        if reply.error() != QNetworkReply.NoError:
            self.failed.emit(self._human_error(reply))
            return

        try:
            data = json.loads(bytes(reply.readAll()).decode("utf-8", "replace"))
            content = data["choices"][0]["message"]["content"].strip()
        except (ValueError, KeyError, IndexError, TypeError):
            self.failed.emit("服务商返回了无法解析的响应")
            return

        usage = data.get("usage") or {}
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        note = ""
        if prompt_tokens is not None and completion_tokens is not None:
            note = f"tokens {prompt_tokens}+{completion_tokens}"
        self.finished.emit(content, note)

    @staticmethod
    def _human_error(reply: QNetworkReply) -> str:
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if status in (401, 403):
            message = "API Key 无效或没有权限，请检查设置"
        elif status == 404:
            message = "接口地址或模型不存在，请检查设置"
        elif status == 429:
            message = "请求过于频繁或额度不足，请稍后再试"
        elif isinstance(status, int) and status >= 500:
            message = "服务商服务器错误，请稍后再试"
        else:
            message = {
                QNetworkReply.ConnectionRefusedError: "无法连接服务商，请检查网络或本地服务是否启动",
                QNetworkReply.HostNotFoundError: "找不到服务商地址，请检查接口地址",
                QNetworkReply.TimeoutError: "请求超时，请稍后重试",
                QNetworkReply.OperationCanceledError: "请求已取消",
                QNetworkReply.AuthenticationRequiredError: "认证失败，请检查 API Key",
                QNetworkReply.SslHandshakeFailedError: "SSL 握手失败，请检查接口地址",
            }.get(reply.error(), f"请求失败（{reply.error()}）")

        detail = bytes(reply.readAll()).decode("utf-8", "replace")
        try:
            detail = json.loads(detail).get("error", {}).get("message", "")
        except ValueError:
            pass
        detail = detail.strip()
        if detail:
            message += f"\n\n服务商返回：{detail[:200]}"
        return message
