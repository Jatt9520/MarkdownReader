# MarkdownReader

A modern Markdown reader with live preview, dark/light themes, and PDF export.

## Features

- **Live Preview** — Real-time rendered markdown using QWebEngineView
- **File Browser** — Sidebar tree view for navigating project files
- **Code Highlighting** — Pygments-powered syntax highlighting for fenced code blocks, with toggle on/off (`Ctrl+Shift+H`)
- **Dark/Light Themes** — Toggle between themes with `Ctrl+Shift+T`
- **PDF Export** — Export the current document to PDF with `Ctrl+E`
- **Search** — Regex-capable find bar with `Ctrl+F`
- **Keyboard Shortcuts** — Full keyboard navigation (see below)
- **Drag & Drop** — Drag markdown files onto the window to open them

## Requirements

- Python 3.10+
- PyQt5
- PyQtWebEngine
- Pygments
- Markdown

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run from project root
python -m markdownreader

# Or with a file argument
python -m markdownreader README.md

# Or via the entry point (after pip install -e .)
markdownreader
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save file |
| `Ctrl+Shift+S` | Save as |
| `Ctrl+N` | New file |
| `Ctrl+W` | Close file |
| `Ctrl+B` | Toggle sidebar |
| `Ctrl+Shift+T` | Toggle theme |
| `Ctrl+Shift+H` | Toggle code highlighting |
| `Ctrl+F` | Find |
| `F3` / `Shift+F3` | Find next / previous |
| `Ctrl++` / `Ctrl+-` | Zoom in / out |
| `Ctrl+0` | Reset zoom |
| `Ctrl+E` | Export PDF |
| `F5` | Reload preview |
| `Ctrl+1` | Focus editor |
| `Ctrl+2` | Focus preview |
| `Escape` | Close search bar |

## Packaging

### Portable EXE (Recommended)

```bash
# Windows - double-click build.bat, or:
build.bat
```

### With PyInstaller (Manual)

```bash
pip install pyinstaller
pyinstaller MarkdownReader.spec
```

### As a wheel

```bash
pip install build
python -m build
pip install dist/markdownreader-0.2.1-py3-none-any.whl
```

## Project Structure

```
MarkdownReader/
├── pyproject.toml
├── requirements.txt
├── README.md
├── build.bat
├── MarkdownReader.spec
└── markdownreader/
    ├── __init__.py
    ├── __main__.py
    ├── main.py
    ├── app.py
    ├── main_window.py
    ├── editor.py
    ├── preview.py
    ├── sidebar.py
    ├── search_bar.py
    ├── renderer.py
    ├── pdf_export.py
    ├── settings.py
    └── utils.py
```

## License

MIT
