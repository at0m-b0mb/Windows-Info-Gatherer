"""System / OS identity collector."""

from __future__ import annotations

import getpass
import platform
import socket

from .. import demo_data as D
from ..model import Category, Section
from .base import Collector, is_demo, powershell, run


def _parse_systeminfo(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            out[key.strip()] = val.strip()
    return out


class SystemCollector(Collector):
    key = "system"
    name = "System"
    icon = "🖥️"
    subtitle = "Operating system identity, build and uptime"

    _KEYS = [
        "Host Name", "OS Name", "OS Version", "OS Manufacturer",
        "Registered Owner", "Registered Organization", "Product ID",
        "Original Install Date", "System Boot Time", "System Manufacturer",
        "System Model", "System Type", "BIOS Version", "Domain", "Time Zone",
    ]

    def collect(self) -> Category:
        cat = Category(self.key, self.name, self.icon, self.subtitle)
        overview = cat.new_section("Operating System")

        if is_demo():
            data = D.SYSTEM
        else:
            data = _parse_systeminfo(run(["systeminfo"], timeout=60))
            data.setdefault("Host Name", socket.gethostname())
            data.setdefault("OS Name", platform.platform())

        for k in self._KEYS:
            if data.get(k):
                overview.kv(k, data[k])

        # Uptime / locale extras
        extra = cat.new_section("Session")
        if is_demo():
            extra.kv("Current User", D.DOMAIN_USER)
            extra.kv("Logon Server", f"\\\\{D.HOST}")
            extra.kv("System Locale", "en-IN; English (India)")
            extra.kv("Uptime", "7 hours, 14 minutes")
        else:
            extra.kv("Current User", f"{platform.node()}\\{getpass.getuser()}")
            extra.kv("Python Host", platform.python_version())
            up = powershell(
                "(Get-Date) - (Get-CimInstance Win32_OperatingSystem)."
                "LastBootUpTime | ForEach-Object { "
                "'{0}d {1}h {2}m' -f $_.Days,$_.Hours,$_.Minutes }"
            ).strip()
            if up:
                extra.kv("Uptime", up)

        return cat
