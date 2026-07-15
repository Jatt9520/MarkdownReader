"""PDF export via QPrinter."""

from pathlib import Path

from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QFileDialog, QMessageBox


def export_to_pdf(text_browser, parent=None) -> bool:
    """Export text browser contents to PDF."""

    path, _ = QFileDialog.getSaveFileName(
        parent,
        "导出 PDF",
        "document.pdf",
        "PDF 文件 (*.pdf);;所有文件 (*)",
    )
    if not path:
        return False

    output = Path(path)
    if not output.suffix:
        output = output.with_suffix(".pdf")

    try:
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(str(output))
        printer.setPageSize(QPrinter.A4)
        text_browser.document().print_(printer)

        QMessageBox.information(
            parent,
            "导出完成",
            f"PDF 已导出到:\n{output}",
        )
        return True

    except Exception as e:
        QMessageBox.critical(
            parent,
            "导出失败",
            f"PDF 导出失败:\n{e}",
        )
        return False
