"""PDF export functionality."""

from pathlib import Path

from PyQt5.QtCore import QUrl, QMarginsF
from PyQt5.QtGui import QPageLayout, QPageSize
from PyQt5.QtWidgets import QFileDialog, QMessageBox


def export_to_pdf(web_view, parent=None) -> bool:
    """Export the web view contents to a PDF file.

    Returns True if export was successful, False if cancelled or failed.
    """
    default_name = "document.pdf"
    path, _ = QFileDialog.getSaveFileName(
        parent,
        "Export to PDF",
        default_name,
        "PDF Files (*.pdf);;All Files (*)",
    )
    if not path:
        return False

    output = Path(path)
    if not output.suffix:
        output = output.with_suffix(".pdf")

    try:
        # Configure PDF layout
        layout = QPageLayout()
        layout.setPageSize(QPageSize(QPageSize.A4))
        layout.setOrientation(QPageLayout.Portrait)
        layout.setMargins(QMarginsF(15, 15, 15, 15))

        # Use QWebEngineView's printToPdf
        page = web_view.page()
        page.printToPdf(str(output), layout)

        # Show success message
        QMessageBox.information(
            parent,
            "Export Complete",
            f"PDF exported successfully to:\n{output}",
        )
        return True

    except Exception as e:
        QMessageBox.critical(
            parent,
            "Export Failed",
            f"Failed to export PDF:\n{str(e)}",
        )
        return False
