"""PyInstaller packaging script.

Usage:
    python package.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    project_dir = Path(__file__).parent

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "MarkdownReader",
        "--windowed",
        "--onefile",
        "--add-data", f"markdownreader{os.sep}resources;markdownreader/resources",
        "--hidden-import", "PyQt5.QtWebEngineWidgets",
        "--hidden-import", "PyQt5.QtWebEngine",
        "--hidden-import", "PyQt5.QtWebEngineCore",
        "--hidden-import", "markdown",
        "--hidden-import", "markdown.extensions",
        "--hidden-import", "markdown.extensions.codehilite",
        "--hidden-import", "markdown.extensions.fenced_code",
        "--hidden-import", "markdown.extensions.tables",
        "--hidden-import", "markdown.extensions.toc",
        "--hidden-import", "markdown.extensions.nl2br",
        "--hidden-import", "markdown.extensions.sane_lists",
        "--hidden-import", "markdown.extensions.smarty",
        "--hidden-import", "pygments",
        "--hidden-import", "pygments.formatters",
        "--hidden-import", "pygments.lexers",
        "--collect-all", "markdown",
        "--collect-all", "pygments",
        str(project_dir / "markdownreader" / "main.py"),
    ]

    print("Building MarkdownReader with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=str(project_dir))

    if result.returncode == 0:
        print("\nBuild successful!")
        print(f"Output: {project_dir / 'dist' / 'MarkdownReader.exe'}")
    else:
        print(f"\nBuild failed with exit code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    import os
    main()
