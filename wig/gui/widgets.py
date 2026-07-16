"""Reusable Qt widgets: nav buttons, stat tiles, cards, tables and findings."""

from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from ..model import Section
from . import theme


class NavButton(QPushButton):
    def __init__(self, icon: str, text: str):
        # Escape '&' so Qt doesn't treat it as a mnemonic accelerator.
        super().__init__(f"  {icon}   {text.replace('&', '&&')}")
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class StatTile(QFrame):
    """Small dashboard metric: big value, label and an emoji glyph."""

    def __init__(self, icon: str, value: str, label: str, accent: str = None):
        super().__init__()
        self.setObjectName("Tile")
        self.setMinimumHeight(92)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)

        top = QHBoxLayout()
        ic = QLabel(icon)
        ic.setObjectName("TileIcon")
        top.addWidget(ic)
        top.addStretch()
        lay.addLayout(top)

        self.value_lbl = QLabel(value)
        self.value_lbl.setObjectName("TileVal")
        if accent:
            self.value_lbl.setStyleSheet(f"color:{accent};")
        lay.addWidget(self.value_lbl)

        lbl = QLabel(label)
        lbl.setObjectName("TileLabel")
        lay.addWidget(lbl)


class Card(QFrame):
    """A titled container that renders one :class:`Section`."""

    def __init__(self, section: Section):
        super().__init__()
        self.section = section
        self.setObjectName("Card")
        self._search_text = ""
        self._rows_widgets = []  # (widget, haystack)

        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(18, 16, 18, 16)
        self.lay.setSpacing(10)

        # Title row: label + optional count badge.
        head = QHBoxLayout()
        head.setSpacing(9)
        title = QLabel(section.title.upper())
        title.setObjectName("CardTitle")
        head.addWidget(title)
        count = (len(section.table_rows) if section.kind == "table"
                 else len(section.findings) if section.kind == "findings"
                 else 0)
        if count:
            badge = QLabel(str(count))
            badge.setObjectName("CountBadge")
            head.addWidget(badge)
        head.addStretch()
        self.lay.addLayout(head)

        if section.kind == "keyvalue":
            self._build_keyvalue(section)
        elif section.kind == "table":
            self._build_table(section)
        elif section.kind == "findings":
            self._build_findings(section)

        if section.note:
            note = QLabel(section.note)
            note.setObjectName("CardNote")
            note.setWordWrap(True)
            self.lay.addWidget(note)

    # ------------------------------------------------------------------ kv
    def _build_keyvalue(self, section: Section):
        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(7)
        grid.setColumnStretch(1, 1)
        for r, (k, v) in enumerate(section.rows):
            key = QLabel(k)
            key.setObjectName("KvKey")
            key.setMinimumWidth(170)
            key.setAlignment(Qt.AlignmentFlag.AlignTop)
            val = QLabel(v)
            val.setObjectName("KvVal")
            val.setWordWrap(True)
            val.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
            color = theme.semantic_color(section.title, k, v)
            if color:
                val.setStyleSheet(f"color:{color}; font-weight:600;")
            grid.addWidget(key, r, 0)
            grid.addWidget(val, r, 1)
            self._rows_widgets.append(((key, val), f"{k} {v}".lower()))
        self.lay.addLayout(grid)

    # --------------------------------------------------------------- table
    def _build_table(self, section: Section):
        table = QTableWidget(len(section.table_rows), len(section.headers))
        table.setHorizontalHeaderLabels(section.headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        table.setShowGrid(False)
        table.setWordWrap(False)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        for r, row in enumerate(section.table_rows):
            for c, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                head = section.headers[c] if c < len(section.headers) else ""
                color = theme.semantic_color(section.title, head, cell)
                if color:
                    item.setForeground(QColor(color))
                table.setItem(r, c, item)
        header = table.horizontalHeader()
        for c in range(len(section.headers)):
            mode = (QHeaderView.ResizeMode.Stretch if c == 0
                    else QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(c, mode)
        row_px = 31
        table.verticalHeader().setDefaultSectionSize(row_px)
        # Size the table to exactly fit its rows (header + rows), capped so long
        # tables scroll internally instead of stretching the whole page.
        desired = 40 + row_px * max(1, len(section.table_rows)) + 4
        table.setFixedHeight(min(desired, 470))
        table.setSizePolicy(QSizePolicy.Policy.Expanding,
                            QSizePolicy.Policy.Fixed)
        table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._table = table
        self.lay.addWidget(table)

    # ------------------------------------------------------------ findings
    def _build_findings(self, section: Section):
        for f in section.findings:
            self.lay.addWidget(self._finding_widget(f))
            self._rows_widgets.append(
                (None, f"{f.title} {f.detail} {f.severity.value}".lower()))

    @staticmethod
    def _finding_widget(finding) -> QWidget:
        color = theme.SEVERITY.get(finding.severity.value, theme.MUTED)
        box = QFrame()
        box.setObjectName("Finding")
        box.setStyleSheet(
            f"#Finding {{ border-left: 3px solid {color}; }}")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(5)

        head = QHBoxLayout()
        head.setSpacing(10)
        badge = QLabel(finding.severity.value.upper())
        badge.setStyleSheet(
            f"background:{color}22; color:{color}; border:1px solid {color}55;"
            f"border-radius:9px; padding:1px 9px; font-size:10px; font-weight:700;")
        title = QLabel(finding.title)
        title.setObjectName("FindingTitle")
        title.setWordWrap(True)
        head.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        head.addWidget(title, 1)
        lay.addLayout(head)

        detail = QLabel(finding.detail)
        detail.setObjectName("FindingDetail")
        detail.setWordWrap(True)
        lay.addWidget(detail)

        if finding.recommendation:
            rec = QLabel("▸  " + finding.recommendation)
            rec.setObjectName("FindingRec")
            rec.setWordWrap(True)
            lay.addWidget(rec)
        return box

    # ------------------------------------------------------------- filter
    def apply_filter(self, text: str) -> bool:
        """Show/hide rows by search text. Returns True if the card stays visible."""
        text = text.lower().strip()
        if not text:
            for widgets, _ in self._rows_widgets:
                if widgets:
                    for w in widgets:
                        w.setVisible(True)
            if hasattr(self, "_table"):
                for r in range(self._table.rowCount()):
                    self._table.setRowHidden(r, False)
            return True

        any_match = text in self.section.title.lower()

        if hasattr(self, "_table"):
            for r in range(self._table.rowCount()):
                hay = " ".join(
                    (self._table.item(r, c).text() if self._table.item(r, c)
                     else "")
                    for c in range(self._table.columnCount())).lower()
                match = text in hay
                self._table.setRowHidden(r, not match)
                any_match = any_match or match

        for widgets, hay in self._rows_widgets:
            match = text in hay
            any_match = any_match or match
            if widgets:
                for w in widgets:
                    w.setVisible(match or text in self.section.title.lower())
        return any_match


class SeverityBar(QWidget):
    """A rounded, stacked proportional bar of finding severities."""

    def __init__(self, segments):
        super().__init__()
        # segments: list of (label, color, count)
        self.segments = [s for s in segments if s[2] > 0]
        self.setFixedHeight(12)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = h / 2
        track = QPainterPath()
        track.addRoundedRect(QRectF(0, 0, w, h), r, r)
        p.fillPath(track, QColor(theme.BORDER))
        total = sum(c for _, _, c in self.segments)
        if not total:
            return
        p.setClipPath(track)
        x = 0.0
        gap = 2.0
        for _label, color, count in self.segments:
            seg = w * count / total
            p.fillRect(QRectF(x, 0, max(seg - gap, 1), h), QColor(color))
            x += seg


def risk_summary_card(counts: dict, total: int) -> QFrame:
    """Card with a risk-level badge, a severity bar and a legend."""
    from ..model import Severity

    n_c = counts.get(Severity.CRITICAL, 0)
    n_h = counts.get(Severity.HIGH, 0)
    n_m = counts.get(Severity.MEDIUM, 0)
    label, color = theme.risk_level(n_c, n_h, n_m)

    card = QFrame()
    card.setObjectName("Card")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(18, 16, 18, 16)
    lay.setSpacing(12)

    head = QHBoxLayout()
    head.setSpacing(10)
    title = QLabel("RISK POSTURE")
    title.setObjectName("CardTitle")
    head.addWidget(title)
    head.addStretch()
    badge = QLabel(label + " RISK")
    badge.setObjectName("RiskBadge")
    badge.setStyleSheet(
        f"background:{color}22; color:{color}; border:1px solid {color}66;")
    head.addWidget(badge)
    lay.addLayout(head)

    order = [
        ("Critical", theme.SEVERITY["Critical"], n_c),
        ("High", theme.SEVERITY["High"], n_h),
        ("Medium", theme.SEVERITY["Medium"], n_m),
        ("Low", theme.SEVERITY["Low"], counts.get(Severity.LOW, 0)),
        ("Good", theme.GOOD, counts.get(Severity.GOOD, 0)
         + counts.get(Severity.INFO, 0)),
    ]
    lay.addWidget(SeverityBar(order))

    legend = QHBoxLayout()
    legend.setSpacing(16)
    for name, col, cnt in order:
        item = QLabel(f"<span style='color:{col}'>●</span> "
                      f"<b style='color:{theme.TEXT}'>{cnt}</b> {name}")
        item.setObjectName("LegendItem")
        legend.addWidget(item)
    legend.addStretch()
    total_lbl = QLabel(f"{total} findings")
    total_lbl.setObjectName("LegendItem")
    legend.addWidget(total_lbl)
    lay.addLayout(legend)
    return card
