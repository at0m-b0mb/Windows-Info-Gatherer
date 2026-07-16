#!/usr/bin/env python3
"""Render WinRecon offscreen and grab a PNG of each page for the README.

Runs headless (QT_QPA_PLATFORM=offscreen) so it works on any machine.
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import QCoreApplication, QEventLoop, Qt, QTimer  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from wig.collectors.base import set_demo_mode  # noqa: E402
from wig.gui.main_window import MainWindow  # noqa: E402
from wig.gui.theme import stylesheet  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "screenshots")


def pump(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def grab(win, name):
    win.repaint()
    pump(120)
    pix = win.grab()
    path = os.path.join(OUT, name)
    pix.save(path)
    print(f"  saved {name}  ({pix.width()}x{pix.height()})")


def main():
    os.makedirs(OUT, exist_ok=True)
    set_demo_mode(True)
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet())
    win = MainWindow()
    win.resize(1220, 800)
    win.show()

    # Wait for the background scan to finish and pages to build.
    for _ in range(60):
        pump(100)
        if win.categories and win.export_btn.isEnabled():
            break
    pump(300)

    pages = ["01_dashboard.png", "02_system.png", "03_hardware.png",
             "04_users.png", "05_network.png", "06_software.png",
             "07_processes.png", "08_audit.png"]
    for idx, name in enumerate(pages):
        win._go(idx)
        pump(150)
        grab(win, name)

    print("Done.")


if __name__ == "__main__":
    main()
