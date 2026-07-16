"""Registry of all category collectors, in display order."""

from __future__ import annotations

from .hardware import HardwareCollector
from .network import NetworkCollector
from .processes import ProcessesCollector
from .security_audit import SecurityAuditCollector
from .software import SoftwareCollector
from .system import SystemCollector
from .users_security import UsersSecurityCollector

# Order here defines the order in the sidebar and in exported reports.
COLLECTORS = [
    SystemCollector(),
    HardwareCollector(),
    UsersSecurityCollector(),
    NetworkCollector(),
    SoftwareCollector(),
    ProcessesCollector(),
    SecurityAuditCollector(),
]


def collect_all():
    """Run every collector and return a list of ``Category`` objects."""
    return [c.collect() for c in COLLECTORS]
