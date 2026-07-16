"""Network collector: adapters, listening ports, shares and Wi-Fi profiles."""

from __future__ import annotations

import re

from .. import demo_data as D
from ..model import Category
from .base import Collector, is_demo, run


class NetworkCollector(Collector):
    key = "network"
    name = "Network"
    icon = "🌐"
    subtitle = "Adapters, listening ports, shares and saved Wi-Fi keys"

    def collect(self) -> Category:
        cat = Category(self.key, self.name, self.icon, self.subtitle)

        nic = cat.new_section(
            "Adapters", kind="table",
            headers=["Adapter", "IPv4", "Subnet Mask", "Gateway", "MAC", "DHCP"],
        )
        dns = cat.new_section("DNS Servers")
        if is_demo():
            for row in D.NIC:
                nic.add_row(*row)
            for i, srv in enumerate(D.DNS, 1):
                dns.kv(f"Server {i}", srv)
        else:
            self._parse_ipconfig(run(["ipconfig", "/all"]), nic, dns)

        ports = cat.new_section(
            "Listening Ports", kind="table",
            headers=["Proto", "Local Address", "State", "PID", "Process"],
        )
        if is_demo():
            for row in D.LISTENING:
                ports.add_row(*row)
        else:
            self._parse_netstat(run(["netstat", "-ano"]), ports)
        ports.note = "Open listeners are a primary remote attack surface."

        shares = cat.new_section(
            "SMB Shares", kind="table", headers=["Share", "Path", "Remark"],
        )
        if is_demo():
            for row in D.SHARES:
                shares.add_row(*row)
        else:
            for line in run(["net", "share"]).splitlines():
                m = re.match(r"^(\S+)\s+([A-Za-z]:\\\S*|)\s{2,}(.*)$", line)
                if m and m.group(1) not in ("Share", "The"):
                    shares.add_row(m.group(1), m.group(2), m.group(3).strip())

        wifi = cat.new_section(
            "Saved Wi-Fi Profiles", kind="table",
            headers=["SSID", "Authentication", "Cipher", "Key (recovered)"],
        )
        wifi.note = ("Keys recovered with `netsh wlan show profile key=clear`. "
                     "Requires admin. A classic post-exploitation win.")
        if is_demo():
            for ssid, auth, cipher, key in D.WIFI_PROFILES:
                wifi.add_row(ssid, auth, cipher, key or "(open)")
        else:
            self._collect_wifi(wifi)

        return cat

    # ------------------------------------------------------------------ parse
    @staticmethod
    def _parse_ipconfig(text, nic, dns):
        adapter = None
        info = {}
        dns_seen = []

        def flush():
            if adapter and info.get("ipv4"):
                nic.add_row(adapter, info.get("ipv4", ""), info.get("mask", ""),
                            info.get("gw", ""), info.get("mac", ""),
                            info.get("dhcp", ""))

        for raw in text.splitlines():
            if raw and not raw.startswith(" "):
                flush()
                adapter = raw.replace("adapter", "").replace(":", "").strip()
                info = {}
                continue
            line = raw.strip()
            if "IPv4 Address" in line:
                info["ipv4"] = line.split(":")[-1].replace("(Preferred)", "").strip()
            elif "Subnet Mask" in line:
                info["mask"] = line.split(":")[-1].strip()
            elif "Default Gateway" in line:
                info["gw"] = line.split(":")[-1].strip()
            elif "Physical Address" in line:
                info["mac"] = line.split(":", 1)[-1].strip()
            elif "DHCP Enabled" in line:
                info["dhcp"] = line.split(":")[-1].strip()
            elif "DNS Servers" in line:
                srv = line.split(":")[-1].strip()
                if srv:
                    dns_seen.append(srv)
        flush()
        for i, srv in enumerate(dict.fromkeys(dns_seen), 1):
            dns.kv(f"Server {i}", srv)

    @staticmethod
    def _parse_netstat(text, ports):
        # Best-effort PID -> image name map via tasklist output is skipped for
        # speed; PID is still shown for pivoting.
        for line in text.splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[0] in ("TCP", "UDP"):
                proto, local = parts[0], parts[1]
                if proto == "TCP" and len(parts) >= 5:
                    state, pid = parts[3], parts[4]
                    if state != "LISTENING":
                        continue
                else:
                    state, pid = "--", parts[-1]
                ports.add_row(proto, local, state, pid, "")

    @staticmethod
    def _collect_wifi(wifi):
        profiles = re.findall(r":\s(.+)$",
                              run(["netsh", "wlan", "show", "profiles"]),
                              re.MULTILINE)
        for name in [p.strip() for p in profiles]:
            detail = run(["netsh", "wlan", "show", "profile",
                          f"name={name}", "key=clear"])
            auth = re.search(r"Authentication\s*:\s*(.+)", detail)
            cipher = re.search(r"Cipher\s*:\s*(.+)", detail)
            key = re.search(r"Key Content\s*:\s*(.+)", detail)
            wifi.add_row(name,
                         auth.group(1).strip() if auth else "",
                         cipher.group(1).strip() if cipher else "",
                         key.group(1).strip() if key else "(not stored / no admin)")
