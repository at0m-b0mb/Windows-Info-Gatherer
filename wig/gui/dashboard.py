"""Builds the Dashboard overview page from the collected categories."""

from __future__ import annotations

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget,
)

from ..model import Category, Severity
from . import theme
from .widgets import Card, StatTile, risk_summary_card


def _find(categories, key):
    for c in categories:
        if c.key == key:
            return c
    return None


def _section(cat, title):
    if not cat:
        return None
    for s in cat.sections:
        if s.title == title:
            return s
    return None


def build_dashboard(categories: List[Category], host: str, demo: bool) -> QWidget:
    system = _find(categories, "system")
    users = _find(categories, "users")
    network = _find(categories, "network")
    software = _find(categories, "software")
    audit = _find(categories, "audit")

    sys_sec = _section(system, "Operating System")
    sys_map = dict(sys_sec.rows) if sys_sec else {}
    os_name = sys_map.get("OS Name", "Windows").replace("Microsoft ", "")

    accounts = _section(users, "Local Accounts")
    n_users = len(accounts.table_rows) if accounts else 0
    n_admins = sum(1 for r in (accounts.table_rows if accounts else [])
                   if len(r) > 3 and r[3] == "Yes")

    ports = _section(network, "Listening Ports")
    n_ports = len(ports.table_rows) if ports else 0
    wifi = _section(network, "Saved Wi-Fi Profiles")
    n_wifi = sum(1 for r in (wifi.table_rows if wifi else [])
                 if len(r) > 3 and r[3] and r[3] != "(open)")

    apps = _section(software, "Installed Programs")
    n_apps = len(apps.table_rows) if apps else 0

    findings_sec = _section(audit, "Findings")
    findings = findings_sec.findings if findings_sec else []
    n_crit = sum(1 for f in findings if f.severity == Severity.CRITICAL)
    n_high = sum(1 for f in findings if f.severity == Severity.HIGH)
    risk_accent = (theme.SEVERITY["Critical"] if n_crit else
                   theme.SEVERITY["High"] if n_high else theme.ACCENT)

    page = QWidget()
    outer = QVBoxLayout(page)
    outer.setContentsMargins(28, 22, 28, 28)
    outer.setSpacing(18)

    # Hero line
    hero = QLabel(f"Snapshot of <b>{host}</b> &mdash; "
                  f"<span style='color:{theme.ACCENT}'>{os_name}</span>")
    hero.setStyleSheet("font-size:15px;")
    outer.addWidget(hero)

    # Tiles
    grid = QGridLayout()
    grid.setSpacing(14)
    tiles = [
        StatTile("🖥️", os_name.split("(")[0].strip()[:18] or "Windows", "Operating System"),
        StatTile("👤", str(n_users), "Local Accounts"),
        StatTile("🔑", str(n_admins), "Administrators",
                 accent=theme.SEVERITY["High"] if n_admins > 1 else None),
        StatTile("🌐", str(n_ports), "Listening Ports"),
        StatTile("📡", str(n_wifi), "Wi-Fi Keys", accent=theme.ACCENT),
        StatTile("📦", str(n_apps), "Installed Apps"),
        StatTile("🛡️", str(len(findings)), "Audit Findings", accent=risk_accent),
        StatTile("⚠️", f"{n_crit + n_high}", "Critical + High", accent=risk_accent),
    ]
    for i, t in enumerate(tiles):
        grid.addWidget(t, i // 4, i % 4)
    outer.addLayout(grid)

    # Risk posture strip (severity breakdown)
    if findings:
        counts = {}
        for f in findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        outer.addWidget(risk_summary_card(counts, len(findings)))

    # Two-column: top findings + quick facts
    cols = QHBoxLayout()
    cols.setSpacing(16)

    from ..model import Section
    top_align = Qt.AlignmentFlag.AlignTop
    if findings_sec and findings:
        top = Section("Top Security Findings", kind="findings")
        top.findings = findings[:4]
        cols.addWidget(Card(top), 3, top_align)

    if sys_sec:
        facts = Section("At a Glance")
        wanted = ["Host Name", "OS Version", "System Manufacturer",
                  "System Model", "System Boot Time", "Domain"]
        for k in wanted:
            if sys_map.get(k):
                facts.kv(k, sys_map[k])
        cols.addWidget(Card(facts), 2, top_align)

    cols_wrap = QWidget()
    cols_wrap.setLayout(cols)
    outer.addWidget(cols_wrap)
    outer.addStretch()
    return page
