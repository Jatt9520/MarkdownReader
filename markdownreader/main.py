"""Application entry point."""

import sys
from markdownreader.app import MarkdownReaderApp


def main():
    app = MarkdownReaderApp(sys.argv)
    sys.exit(app.run())
