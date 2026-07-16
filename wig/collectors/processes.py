"""Processes, services, startup items and scheduled tasks collector."""

from __future__ import annotations

import csv
import io

from .. import demo_data as D
from ..model import Category
from .base import Collector, is_demo, powershell, run


class ProcessesCollector(Collector):
    key = "processes"
    name = "Processes & Services"
    icon = "⚙️"
    subtitle = "Running processes, services, autoruns and tasks"

    def collect(self) -> Category:
        cat = Category(self.key, self.name, self.icon, self.subtitle)

        procs = cat.new_section(
            "Running Processes", kind="table",
            headers=["Image", "PID", "Memory", "User"],
        )
        if is_demo():
            for row in D.PROCESSES:
                procs.add_row(*row)
        else:
            reader = csv.reader(io.StringIO(
                run(["tasklist", "/v", "/fo", "csv"])))
            rows = list(reader)
            for r in rows[1:]:
                if len(r) >= 7:
                    procs.add_row(r[0], r[1], r[4], r[6])

        svc = cat.new_section(
            "Services", kind="table",
            headers=["Name", "Display Name", "State", "Start Mode"],
        )
        if is_demo():
            for row in D.SERVICES:
                svc.add_row(*row)
        else:
            for line in powershell(
                "Get-CimInstance Win32_Service | ForEach-Object { "
                "'{0}|{1}|{2}|{3}' -f $_.Name,$_.DisplayName,$_.State,"
                "$_.StartMode }"
            ).splitlines():
                p = line.split("|")
                if len(p) == 4 and p[0].strip():
                    svc.add_row(*[c.strip() for c in p])

        startup = cat.new_section(
            "Startup / Autoruns", kind="table",
            headers=["Name", "Command", "Location"],
        )
        if is_demo():
            for row in D.STARTUP:
                startup.add_row(*row)
        else:
            for line in powershell(
                "Get-CimInstance Win32_StartupCommand | ForEach-Object { "
                "'{0}|{1}|{2}' -f $_.Name,$_.Command,$_.Location }"
            ).splitlines():
                p = line.split("|")
                if len(p) == 3 and p[0].strip():
                    startup.add_row(*[c.strip() for c in p])

        tasks = cat.new_section(
            "Scheduled Tasks (non-Microsoft)", kind="table",
            headers=["Task", "Status", "Trigger", "Run As"],
        )
        if is_demo():
            for row in D.SCHEDULED_TASKS:
                tasks.add_row(*row)
        else:
            reader = csv.reader(io.StringIO(
                run(["schtasks", "/query", "/fo", "csv", "/v"])))
            rows = list(reader)
            header = rows[0] if rows else []
            try:
                i_name = header.index("TaskName")
                i_status = header.index("Status")
                i_run = header.index("Run As User")
            except ValueError:
                i_name, i_status, i_run = 1, 3, 4
            seen = set()
            for r in rows[1:]:
                if len(r) > max(i_name, i_status, i_run):
                    name = r[i_name]
                    if name in seen:
                        continue
                    seen.add(name)
                    tasks.add_row(name, r[i_status], "", r[i_run])

        return cat
