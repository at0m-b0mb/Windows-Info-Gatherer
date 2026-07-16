"""Hardware collector: CPU, memory, disks, GPU."""

from __future__ import annotations

from .. import demo_data as D
from ..model import Category
from .base import Collector, is_demo, powershell


def _ps_lines(script: str):
    out = powershell(script)
    return [ln.rstrip() for ln in out.splitlines() if ln.strip()]


class HardwareCollector(Collector):
    key = "hardware"
    name = "Hardware"
    icon = "🧩"
    subtitle = "Processor, memory, storage and graphics"

    def collect(self) -> Category:
        cat = Category(self.key, self.name, self.icon, self.subtitle)

        cpu = cat.new_section("Processor")
        if is_demo():
            for k, v in D.CPU.items():
                cpu.kv(k, v)
        else:
            data = powershell(
                "Get-CimInstance Win32_Processor | Select-Object "
                "Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,"
                "L2CacheSize,L3CacheSize,AddressWidth | Format-List"
            )
            for line in data.splitlines():
                if ":" in line:
                    k, _, val = line.partition(":")
                    if val.strip():
                        cpu.kv(k.strip(), val.strip())

        mem = cat.new_section(
            "Memory Modules", kind="table",
            headers=["Bank", "Capacity", "Speed", "Manufacturer", "Part Number"],
        )
        if is_demo():
            for row in D.MEMORY_MODULES:
                mem.add_row(*row)
            mem.note = f"Total installed: {D.MEMORY_TOTAL_GB} GB"
        else:
            data = powershell(
                "Get-CimInstance Win32_PhysicalMemory | ForEach-Object { "
                "'{0}|{1}|{2}|{3}|{4}' -f $_.DeviceLocator,"
                "[math]::Round($_.Capacity/1GB,0),$_.Speed,"
                "$_.Manufacturer,$_.PartNumber }"
            )
            total = 0
            for line in data.splitlines():
                parts = line.split("|")
                if len(parts) == 5:
                    cap = parts[1].strip()
                    mem.add_row(parts[0], f"{cap} GB", f"{parts[2]} MHz",
                                parts[3].strip(), parts[4].strip())
                    try:
                        total += int(cap)
                    except ValueError:
                        pass
            if total:
                mem.note = f"Total installed: {total} GB"

        disks = cat.new_section(
            "Physical Disks", kind="table",
            headers=["Model", "Interface", "Size", "Media Type"],
        )
        vols = cat.new_section(
            "Volumes", kind="table",
            headers=["Drive", "Label", "File System", "Capacity", "Free", "% Free"],
        )
        if is_demo():
            for row in D.DISKS:
                disks.add_row(*row)
            for row in D.VOLUMES:
                vols.add_row(*row)
        else:
            for line in _ps_lines(
                "Get-CimInstance Win32_DiskDrive | ForEach-Object { "
                "'{0}|{1}|{2}|{3}' -f $_.Model,$_.InterfaceType,"
                "[math]::Round($_.Size/1GB,2),$_.MediaType }"
            ):
                p = line.split("|")
                if len(p) == 4:
                    disks.add_row(p[0], p[1], f"{p[2]} GB", p[3])
            for line in _ps_lines(
                "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | "
                "ForEach-Object { '{0}|{1}|{2}|{3}|{4}' -f $_.DeviceID,"
                "$_.VolumeName,$_.FileSystem,"
                "[math]::Round($_.Size/1GB,2),[math]::Round($_.FreeSpace/1GB,2) }"
            ):
                p = line.split("|")
                if len(p) == 5:
                    try:
                        pct = f"{round(float(p[4]) / float(p[3]) * 100)}%"
                    except (ValueError, ZeroDivisionError):
                        pct = "--"
                    vols.add_row(p[0], p[1], p[2], f"{p[3]} GB", f"{p[4]} GB", pct)

        gpu = cat.new_section(
            "Graphics", kind="table",
            headers=["Adapter", "Driver Version", "Memory"],
        )
        if is_demo():
            for row in D.GPUS:
                gpu.add_row(*row)
        else:
            for line in _ps_lines(
                "Get-CimInstance Win32_VideoController | ForEach-Object { "
                "'{0}|{1}|{2}' -f $_.Name,$_.DriverVersion,"
                "[math]::Round($_.AdapterRAM/1MB,0) }"
            ):
                p = line.split("|")
                if len(p) == 3:
                    gpu.add_row(p[0], p[1], f"{p[2]} MB")

        return cat
