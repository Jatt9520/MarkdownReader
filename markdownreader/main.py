"""Application entry point."""

import sys
import traceback


def main():
    try:
        from markdownreader.app import MarkdownReaderApp

        app = MarkdownReaderApp(sys.argv)
        sys.exit(app.run())
    except Exception as e:
        log_path = r"C:\Users\admin\Desktop\MarkdownReader_crash.log"
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Error: {e}\n\n")
            traceback.print_exc(file=f)
        print(f"FATAL ERROR — see {log_path}")
        traceback.print_exc()
        input("按 Enter 键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
