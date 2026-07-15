"""PDF export via QPrinter."""

from pathlib import Path

from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QFileDialog, QMessageBox


def export_to_pdf(text_browser, parent=None) -> bool:
    """Export text browser contents to PDF."""

    path, _ = QFileDialog.getSaveFileName(
        parent,
        "Export to PDF",
        "document.pdf",
        "PDF Files (*.pdf);;All Files (*)",
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
            "Export Complete",
            f"PDF exported to:\n{output}",
        )
        return True

    except Exception as e:
        QMessageBox.critical(
            parent,
            "Export Failed",
            f"Failed to export PDF:\n{e}",
        )
        return False
