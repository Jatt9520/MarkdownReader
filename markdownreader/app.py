"""QApplication bootstrap and global configuration."""

import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from markdownreader.settings import Settings
from markdownreader.main_window import MainWindow


class MarkdownReaderApp:
    def __init__(self, argv: list[str]):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        self.qapp = QApplication(argv)
        self.qapp.setApplicationName("MarkdownReader")
        self.qapp.setOrganizationName("MarkdownReader")

        self.settings = Settings()
        self.settings.load()

        self.window = MainWindow(self.settings)

    def run(self) -> int:
        self.window.show()

        if len(sys.argv) > 1:
            path = Path(sys.argv[1])
            if path.is_file():
                self.window.open_file(path)

        return self.qapp.exec_()
