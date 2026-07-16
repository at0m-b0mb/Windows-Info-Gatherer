"""Installed software, patches and environment collector."""

from __future__ import annotations

import os

from .. import demo_data as D
from ..model import Category
from .base import Collector, is_demo, powershell, run


class SoftwareCollector(Collector):
    key = "software"
    name = "Software"
    icon = "📦"
    subtitle = "Installed programs, hotfixes and environment"

    def collect(self) -> Category:
        cat = Category(self.key, self.name, self.icon, self.subtitle)

        apps = cat.new_section(
            "Installed Programs", kind="table",
            headers=["Name", "Version", "Publisher"],
        )
        if is_demo():
            for row in D.INSTALLED:
                apps.add_row(*row)
            apps.note = f"{len(D.INSTALLED)} programs enumerated from the registry."
        else:
            rows = []
            for line in powershell(
                "$p='HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
                "'HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*';"
                "Get-ItemProperty $p -EA SilentlyContinue | "
                "Where-Object DisplayName | Sort-Object DisplayName | "
                "ForEach-Object { '{0}|{1}|{2}' -f "
                "$_.DisplayName,$_.DisplayVersion,$_.Publisher }"
            ).splitlines():
                p = line.split("|")
                if p[0].strip():
                    rows.append((p[0].strip(),
                                 p[1].strip() if len(p) > 1 else "",
                                 p[2].strip() if len(p) > 2 else ""))
            seen = set()
            for name, ver, pub in rows:
                if name not in seen:
                    seen.add(name)
                    apps.add_row(name, ver, pub)
            apps.note = f"{len(seen)} programs enumerated from the registry."

        hotfix = cat.new_section("Installed Hotfixes (KB)")
        if is_demo():
            hotfix.kv("Latest patches", ", ".join(D.HOTFIXES))
        else:
            kbs = [ln.strip() for ln in run(["wmic", "qfe", "get",
                   "HotFixID"]).splitlines() if ln.strip().startswith("KB")]
            if not kbs:
                kbs = [ln.strip() for ln in powershell(
                    "Get-HotFix | Select-Object -Expand HotFixID").splitlines()
                    if ln.strip().startswith("KB")]
            hotfix.kv("Installed patches", ", ".join(kbs[:40]) or "None found")

        env = cat.new_section("Environment Variables")
        source = D.ENV_VARS if is_demo() else os.environ
        interesting = ["COMPUTERNAME", "USERNAME", "USERDOMAIN",
                       "NUMBER_OF_PROCESSORS", "OS", "PROCESSOR_ARCHITECTURE",
                       "SystemRoot", "TEMP", "PATH"]
        for k in interesting:
            if source.get(k):
                val = source[k]
                if k == "PATH" and len(val) > 90:
                    val = val[:90] + " ..."
                env.kv(k, val)

        return cat
