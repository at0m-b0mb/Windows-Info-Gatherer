"""The WinRecon main window: sidebar, top bar, pages, export and threading."""

from __future__ import annotations

import datetime as _dt
import platform
from typing import List

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QProgressBar, QPushButton, QScrollArea, QStackedWidget,
    QVBoxLayout, QWidget,
)

from .. import __app_name__, __tagline__, __version__, report
from ..collectors import COLLECTORS
from ..collectors.base import is_demo
from ..model import Category
from . import theme
from .dashboard import build_dashboard
from .widgets import Card, NavButton, risk_summary_card


class CollectWorker(QThread):
    """Runs the collectors off the UI thread."""

    progress = pyqtSignal(str, int)
    finished = pyqtSignal(list)

    def run(self):
        results: List[Category] = []
        total = len(COLLECTORS)
        for i, collector in enumerate(COLLECTORS):
            self.progress.emit(collector.name, int(i / total * 100))
            try:
                results.append(collector.collect())
            except Exception as exc:  # never let one collector kill the scan
                cat = Category(collector.key, collector.name, collector.icon,
                               f"collection error: {exc}")
                results.append(cat)
        self.progress.emit("Done", 100)
        self.finished.emit(results)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.categories: List[Category] = []
        self.host = platform.node() or "localhost"
        self._page_cards = {}   # stack index -> [Card]
        self._nav_buttons = []

        self.setWindowTitle(f"{__app_name__} — {__tagline__}")
        self.resize(1220, 800)
        self.setMinimumSize(1040, 680)

        root = QWidget()
        self.setCentralWidget(root)
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        h.addWidget(self._build_sidebar())
        h.addWidget(self._build_main(), 1)

        self._start_scan()

    # ------------------------------------------------------------- sidebar
    def _build_sidebar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("Sidebar")
        bar.setFixedWidth(232)
        lay = QVBoxLayout(bar)
        lay.setContentsMargins(16, 22, 16, 18)
        lay.setSpacing(6)

        brand = QLabel(f'<span id="a">Win</span>Recon')
        brand.setObjectName("Brand")
        brand.setText('<span style="color:%s">Win</span>Recon' % theme.ACCENT)
        lay.addWidget(brand)
        sub = QLabel("INFORMATION GATHERER")
        sub.setObjectName("BrandSub")
        lay.addWidget(sub)
        lay.addSpacing(18)

        self._nav_container = QVBoxLayout()
        self._nav_container.setSpacing(4)
        lay.addLayout(self._nav_container)

        # Dashboard is always index 0.
        self._add_nav("📊", "Dashboard", 0)
        lay.addStretch()

        ver = QLabel(f"v{__version__}  ·  by at0m-b0mb")
        ver.setStyleSheet(f"color:{theme.MUTED}; font-size:10px;")
        lay.addWidget(ver)
        return bar

    def _add_nav(self, icon: str, text: str, index: int):
        btn = NavButton(icon, text)
        btn.clicked.connect(lambda: self._go(index))
        self._nav_container.addWidget(btn)
        self._nav_buttons.append(btn)
        if index == 0:
            btn.setChecked(True)

    # ---------------------------------------------------------------- main
    def _build_main(self) -> QWidget:
        wrap = QWidget()
        v = QVBoxLayout(wrap)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(self._build_topbar())
        self.stack = QStackedWidget()
        v.addWidget(self.stack, 1)
        v.addWidget(self._build_statusbar())
        return wrap

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(78)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(28, 0, 24, 0)
        lay.setSpacing(14)

        titles = QVBoxLayout()
        titles.setSpacing(1)
        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("PageTitle")
        self.page_sub = QLabel("System overview")
        self.page_sub.setObjectName("PageSub")
        titles.addWidget(self.page_title)
        titles.addWidget(self.page_sub)
        lay.addLayout(titles)
        lay.addStretch()

        self.search = QLineEdit()
        self.search.setObjectName("Search")
        self.search.setPlaceholderText("🔍  Filter this page…")
        self.search.setFixedWidth(240)
        self.search.textChanged.connect(self._apply_search)
        lay.addWidget(self.search)

        self.refresh_btn = QPushButton("↻  Rescan")
        self.refresh_btn.setObjectName("Action")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self._start_scan)
        lay.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("⤓  Export Report")
        self.export_btn.setObjectName("Primary")
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.clicked.connect(self._export)
        self.export_btn.setEnabled(False)
        lay.addWidget(self.export_btn)
        return bar

    def _build_statusbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("StatusBar")
        bar.setFixedHeight(30)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(28, 0, 24, 0)
        lay.setSpacing(14)

        mode = QLabel("● DEMO DATA" if is_demo() else "● LIVE — real system")
        mode.setObjectName("ModeDemo" if is_demo() else "ModeLive")
        lay.addWidget(mode)
        lay.addWidget(QLabel(f"Host: {self.host}"))
        lay.addWidget(QLabel(f"{platform.system()} {platform.release()}"))
        lay.addStretch()

        self.progress = QProgressBar()
        self.progress.setFixedWidth(160)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        lay.addWidget(self.progress)

        self.status_lbl = QLabel("Ready")
        lay.addWidget(self.status_lbl)
        return bar

    # ------------------------------------------------------------- scanning
    def _start_scan(self):
        self.refresh_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.status_lbl.setText("Scanning…")
        self.worker = CollectWorker()
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, name: str, pct: int):
        self.progress.setValue(pct)
        self.status_lbl.setText(f"Collecting: {name}…")

    def _on_finished(self, categories: List[Category]):
        self.categories = categories
        self._rebuild_pages()
        self.progress.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        ts = _dt.datetime.now().strftime("%H:%M:%S")
        self.status_lbl.setText(f"Scan complete · {ts}")

    # ---------------------------------------------------------------- pages
    def _rebuild_pages(self):
        # Wipe existing pages and nav (keep Dashboard nav button at index 0).
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()
        for btn in self._nav_buttons[1:]:
            btn.deleteLater()
        del self._nav_buttons[1:]
        self._page_cards = {}

        # Dashboard (index 0)
        self.stack.addWidget(self._scroll(
            build_dashboard(self.categories, self.host, is_demo())))
        self._page_cards[0] = []

        # One page per category
        for idx, cat in enumerate(self.categories, start=1):
            page, cards = self._category_page(cat)
            self.stack.addWidget(self._scroll(page))
            self._page_cards[idx] = cards
            self._add_nav(cat.icon, cat.name, idx)

        self._go(0)

    @staticmethod
    def _scroll(inner: QWidget) -> QScrollArea:
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(inner)
        return area

    def _category_page(self, cat: Category):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(28, 22, 28, 28)
        v.setSpacing(16)
        cards = []

        # Security Audit leads with a risk-posture summary.
        if cat.key == "audit":
            findings = next((s.findings for s in cat.sections
                             if s.kind == "findings"), [])
            if findings:
                counts = {}
                for f in findings:
                    counts[f.severity] = counts.get(f.severity, 0) + 1
                v.addWidget(risk_summary_card(counts, len(findings)))

        for section in cat.sections:
            if section.is_empty:
                continue
            card = Card(section)
            cards.append(card)
            v.addWidget(card)
        if not cards:
            empty = QLabel("No data collected for this category.")
            empty.setStyleSheet(f"color:{theme.MUTED}; padding:20px;")
            v.addWidget(empty)
        v.addStretch()
        return page, cards

    # ------------------------------------------------------------- nav/search
    def _go(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)
        if index == 0:
            self.page_title.setText("Dashboard")
            self.page_sub.setText("System overview")
        else:
            cat = self.categories[index - 1]
            self.page_title.setText(f"{cat.icon}  {cat.name}")
            self.page_sub.setText(cat.subtitle)
        self.search.clear()

    def _apply_search(self, text: str):
        idx = self.stack.currentIndex()
        for card in self._page_cards.get(idx, []):
            visible = card.apply_filter(text)
            card.setVisible(visible)

    # ---------------------------------------------------------------- export
    def _export(self):
        if not self.categories:
            return
        ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        default = f"WinRecon_{self.host}_{ts}.html"
        path, chosen = QFileDialog.getSaveFileName(
            self, "Export Report", default,
            "HTML report (*.html);;JSON (*.json);;Text (*.txt)")
        if not path:
            return
        demo = is_demo()
        try:
            if path.endswith(".json") or "JSON" in chosen:
                data = report.to_json(self.categories, demo)
            elif path.endswith(".txt") or "Text" in chosen:
                data = report.to_text(self.categories, demo)
            else:
                if not path.endswith(".html"):
                    path += ".html"
                data = report.to_html(self.categories, demo)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(data)
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
            return
        self.status_lbl.setText(f"Report saved: {path}")
        QMessageBox.information(
            self, "Report exported",
            f"Saved report to:\n{path}")

    # ---------------------------------------------------------- convenience
    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        geo = self.frameGeometry()
        geo.moveCenter(screen.center())
        self.move(geo.topLeft())
