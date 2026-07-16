"""Shared data model used by collectors, the GUI, and the report exporter.

Every collector returns a :class:`Category`.  A category holds a list of
:class:`Section` objects, and each section is one of three shapes:

* ``keyvalue`` -- an ordered list of ``(label, value)`` pairs.
* ``table``    -- ``headers`` plus a list of row lists.
* ``findings`` -- a list of :class:`Finding` (used by the Security Audit page).

Keeping a single structured model means the GUI and the HTML/JSON/TXT
exporters render from exactly the same data with no divergence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple


class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"
    GOOD = "Good"

    @property
    def rank(self) -> int:
        order = {
            "Critical": 0,
            "High": 1,
            "Medium": 2,
            "Low": 3,
            "Info": 4,
            "Good": 5,
        }
        return order[self.value]


@dataclass
class Finding:
    """A single security-audit observation with a severity and advice."""

    title: str
    severity: Severity
    detail: str
    recommendation: str = ""


@dataclass
class Section:
    title: str
    kind: str = "keyvalue"  # keyvalue | table | findings
    rows: List[Tuple[str, str]] = field(default_factory=list)
    headers: List[str] = field(default_factory=list)
    table_rows: List[List[str]] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    note: str = ""

    # --- convenience builders -------------------------------------------------
    def kv(self, label: str, value) -> "Section":
        self.rows.append((str(label), "" if value is None else str(value)))
        return self

    def add_row(self, *cells) -> "Section":
        self.table_rows.append([("" if c is None else str(c)) for c in cells])
        return self

    def add_finding(self, finding: Finding) -> "Section":
        self.findings.append(finding)
        return self

    @property
    def is_empty(self) -> bool:
        return not (self.rows or self.table_rows or self.findings)


@dataclass
class Category:
    key: str
    name: str
    icon: str  # emoji glyph used in the sidebar
    subtitle: str = ""
    sections: List[Section] = field(default_factory=list)

    def add(self, section: Section) -> Section:
        self.sections.append(section)
        return section

    def new_section(self, title: str, kind: str = "keyvalue", **kw) -> Section:
        s = Section(title=title, kind=kind, **kw)
        self.sections.append(s)
        return s
