"""Application entry point."""

import sys
import tempfile
import traceback
from pathlib import Path


def main():
    try:
        from markdownreader.app import MarkdownReaderApp

        app = MarkdownReaderApp(sys.argv)
        sys.exit(app.run())
    except Exception:
        err = traceback.format_exc()
        log_path = Path(tempfile.gettempdir()) / "MarkdownReader_crash.log"
        try:
            log_path.write_text(err, encoding="utf-8")
        except OSError:
            log_path = None
        print(f"FATAL ERROR — see {log_path}", file=sys.stderr)
        print(err, file=sys.stderr)
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox

            if QApplication.instance() is None:
                QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "MarkdownReader 启动失败",
                f"发生未处理的错误:\n\n{err[-800:]}\n\n完整日志: {log_path}",
            )
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
