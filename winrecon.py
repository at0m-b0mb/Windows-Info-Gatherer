#!/usr/bin/env python3
"""WinRecon — Windows Information Gatherer.

A cross-platform PyQt6 desktop tool that collects the system, hardware, user,
network, software and security-posture information a defender or ethical hacker
needs for a fast assessment of a Windows host — and exports it to HTML/JSON/TXT.

Usage:
    python winrecon.py                 # launch the GUI (live on Windows)
    python winrecon.py --demo          # launch the GUI with demo data
    python winrecon.py --cli --html out.html    # headless report, no GUI
    python winrecon.py --cli --json out.json
    python winrecon.py --cli --txt  out.txt

On any non-Windows OS the tool automatically runs in demo mode so the interface
can be explored, screenshotted and developed anywhere.
"""

from __future__ import annotations

import argparse
import sys

from wig import __app_name__, __version__


def _cli(args) -> int:
    from wig.collectors import collect_all
    from wig.collectors.base import is_demo
    from wig import report

    print(f"[*] {__app_name__} v{__version__} — collecting "
          f"({'DEMO' if is_demo() else 'LIVE'})…")
    categories = collect_all()
    demo = is_demo()

    wrote = False
    if args.html:
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(report.to_html(categories, demo))
        print(f"[+] HTML report → {args.html}")
        wrote = True
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            fh.write(report.to_json(categories, demo))
        print(f"[+] JSON report → {args.json}")
        wrote = True
    if args.txt:
        with open(args.txt, "w", encoding="utf-8") as fh:
            fh.write(report.to_text(categories, demo))
        print(f"[+] Text report → {args.txt}")
        wrote = True

    if not wrote:
        print(report.to_text(categories, demo))
    return 0


def _gui() -> int:
    from PyQt6.QtWidgets import QApplication
    from wig.gui.theme import stylesheet
    from wig.gui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setStyleSheet(stylesheet())
    win = MainWindow()
    win.center_on_screen()
    win.show()
    return app.exec()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="winrecon", description=f"{__app_name__} — Windows Information Gatherer")
    parser.add_argument("--demo", action="store_true",
                        help="force demo data even on Windows")
    parser.add_argument("--cli", action="store_true",
                        help="run headless (no GUI) and print/export a report")
    parser.add_argument("--html", metavar="FILE", help="write an HTML report")
    parser.add_argument("--json", metavar="FILE", help="write a JSON report")
    parser.add_argument("--txt", metavar="FILE", help="write a text report")
    parser.add_argument("--version", action="version",
                        version=f"{__app_name__} {__version__}")
    args = parser.parse_args()

    from wig.collectors.base import set_demo_mode
    set_demo_mode(args.demo)

    if args.cli or args.html or args.json or args.txt:
        return _cli(args)
    return _gui()


if __name__ == "__main__":
    sys.exit(main())
