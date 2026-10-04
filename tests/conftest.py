"""Shared pytest fixtures: isolate QSettings from the user's registry."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from PyQt5.QtCore import QSettings, QTemporaryDir  # noqa: E402

from markdownreader.settings import Settings  # noqa: E402


@pytest.fixture()
def settings(monkeypatch):
    """Settings instance backed by a throwaway ini file."""
    tmp = QTemporaryDir()
    monkeypatch.setattr(
        Settings, "__init__",
        lambda self: setattr(self, "_qs", QSettings(str(Path(tmp.path()) / "s.ini"), QSettings.IniFormat)),
    )
    yield Settings()
    tmp.remove()
