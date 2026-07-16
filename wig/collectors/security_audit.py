"""Security-audit collector.

Runs a set of light, read-only posture checks and privilege-escalation
heuristics and reports them as prioritised :class:`Finding` objects.  Nothing
here modifies the system -- it only reads state that a defender (or an attacker
already on the box) would look at first.
"""

from __future__ import annotations

from .. import demo_data as D
from ..model import Category, Finding, Severity
from .base import Collector, is_demo, powershell, run


class SecurityAuditCollector(Collector):
    key = "audit"
    name = "Security Audit"
    icon = "🛡️"
    subtitle = "Posture checks and privilege-escalation heuristics"

    def collect(self) -> Category:
        cat = Category(self.key, self.name, self.icon, self.subtitle)

        posture = cat.new_section("Defensive Posture")
        if is_demo():
            posture.kv("UAC (EnableLUA)", "Enabled")
            posture.kv("Windows Defender", "Running")
            posture.kv("Real-Time Protection", "On")
            posture.kv("Tamper Protection", "Off")
            posture.kv("Firewall (Domain/Private/Public)", "On / On / Off")
            posture.kv("BitLocker (C:)", "Not encrypted")
            posture.kv("RDP", "Enabled (port 3389)")
            posture.kv("SMBv1", "Disabled")
        else:
            self._live_posture(posture)

        findings = cat.new_section("Findings", kind="findings")
        if is_demo():
            self._demo_findings(findings)
        else:
            self._live_findings(findings)

        # Sort by severity so the worst items float to the top.
        findings.findings.sort(key=lambda f: f.severity.rank)

        counts = {}
        for f in findings.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        cat.subtitle = (
            f"{len(findings.findings)} findings "
            f"({counts.get(Severity.CRITICAL,0)} critical, "
            f"{counts.get(Severity.HIGH,0)} high, "
            f"{counts.get(Severity.MEDIUM,0)} medium)"
        )
        return cat

    # ------------------------------------------------------------------ demo
    @staticmethod
    def _demo_findings(section):
        F = Finding
        section.add_finding(F(
            "Saved Wi-Fi keys recoverable in clear text",
            Severity.HIGH,
            "3 wireless profiles store pre-shared keys that were recovered with "
            "`netsh wlan show profile key=clear`, including HackLab-5G "
            "(WPA2). Anyone with local access can harvest these.",
            "Treat the workstation as a credential store; rotate PSKs if the "
            "device is lost or shared.",
        ))
        section.add_finding(F(
            "BitLocker is disabled on the system drive",
            Severity.HIGH,
            "C: is not encrypted. Offline attacks (drive removal, WinPE) can "
            "read all data and dump SAM/SYSTEM hives for hash extraction.",
            "Enable BitLocker with a TPM+PIN protector on all fixed drives.",
        ))
        section.add_finding(F(
            "Tamper Protection is off",
            Severity.MEDIUM,
            "Microsoft Defender Tamper Protection is disabled, so malware (or a "
            "user with admin) can silently switch off real-time protection.",
            "Enable Tamper Protection via Windows Security > Virus & threat "
            "protection settings.",
        ))
        section.add_finding(F(
            "Remote Desktop is exposed",
            Severity.MEDIUM,
            "TermService is listening on 3389/tcp. Combined with weak lockout "
            "(10 attempts) this is a viable password-spray / BlueKeep surface.",
            "Restrict RDP to VPN, require NLA, and enforce account lockout.",
        ))
        section.add_finding(F(
            "Public-profile firewall is off",
            Severity.MEDIUM,
            "The Public firewall profile is disabled, exposing SMB (445) and "
            "NetBIOS (139) on untrusted networks such as the demo Wi-Fi.",
            "Enable the firewall on every profile; block inbound 139/445 on "
            "public networks.",
        ))
        section.add_finding(F(
            "Service account 'svc_backup' has SeBackupPrivilege",
            Severity.MEDIUM,
            "A non-admin service account holds backup rights, which allow "
            "reading any file (including SAM/SYSTEM) -- a common privilege-"
            "escalation path.",
            "Remove backup rights from interactive/service accounts that don't "
            "strictly need them.",
        ))
        section.add_finding(F(
            "Password policy allows short passwords",
            Severity.LOW,
            "Minimum password length is 8 with a 42-day max age; below current "
            "hardening baselines for privileged workstations.",
            "Raise minimum length to 14+ and prefer passphrases / FIDO2.",
        ))
        section.add_finding(F(
            "UAC is enabled",
            Severity.GOOD,
            "EnableLUA=1 and admin approval mode is active, so elevation "
            "prompts are enforced.",
            "No action needed. Keep UAC at the default or higher.",
        ))

    # ------------------------------------------------------------------ live
    @staticmethod
    def _live_posture(section):
        uac = powershell(
            "(Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\"
            "CurrentVersion\\Policies\\System').EnableLUA").strip()
        section.kv("UAC (EnableLUA)", "Enabled" if uac == "1" else "Disabled")

        mp = powershell(
            "$m=Get-MpComputerStatus; '{0}|{1}|{2}' -f "
            "$m.AntivirusEnabled,$m.RealTimeProtectionEnabled,"
            "$m.IsTamperProtected").strip().split("|")
        if len(mp) == 3:
            section.kv("Windows Defender", "Enabled" if mp[0] == "True" else "Off")
            section.kv("Real-Time Protection", "On" if mp[1] == "True" else "Off")
            section.kv("Tamper Protection", "On" if mp[2] == "True" else "Off")

        fw = powershell(
            "(Get-NetFirewallProfile | Select-Object -Expand Enabled) "
            "-join '/'").strip()
        if fw:
            section.kv("Firewall (Domain/Private/Public)", fw)

        bl = powershell(
            "(Get-BitLockerVolume -MountPoint C: -EA SilentlyContinue)."
            "ProtectionStatus").strip()
        section.kv("BitLocker (C:)",
                   "On" if bl == "On" or bl == "1" else "Not encrypted")

    @staticmethod
    def _live_findings(section):
        F = Finding
        # Local admin?
        if "S-1-5-32-544" in run(["whoami", "/groups"]):
            section.add_finding(F(
                "Current session is a local Administrator",
                Severity.INFO,
                "The running user is in the local Administrators group; all "
                "collected data reflects a privileged context.",
                "Run day-to-day tasks as a standard user.",
            ))
        # AlwaysInstallElevated -> instant SYSTEM
        hk = powershell(
            "(Get-ItemProperty 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\"
            "Installer' -EA SilentlyContinue).AlwaysInstallElevated").strip()
        hcu = powershell(
            "(Get-ItemProperty 'HKCU:\\SOFTWARE\\Policies\\Microsoft\\Windows\\"
            "Installer' -EA SilentlyContinue).AlwaysInstallElevated").strip()
        if hk == "1" and hcu == "1":
            section.add_finding(F(
                "AlwaysInstallElevated is enabled",
                Severity.CRITICAL,
                "Both HKLM and HKCU set AlwaysInstallElevated=1. Any user can "
                "install a crafted MSI as SYSTEM -- trivial privilege "
                "escalation.",
                "Set both policy values to 0 immediately.",
            ))
        # Tamper protection off
        if "False" in powershell(
                "(Get-MpComputerStatus).IsTamperProtected"):
            section.add_finding(F(
                "Tamper Protection is off",
                Severity.MEDIUM,
                "Defender Tamper Protection is disabled.",
                "Enable it in Windows Security settings.",
            ))
        # Stored credentials
        if "Target:" in run(["cmdkey", "/list"]):
            section.add_finding(F(
                "Stored credentials present in Credential Manager",
                Severity.MEDIUM,
                "`cmdkey /list` shows saved credentials that may be reusable "
                "for lateral movement (runas /savecred).",
                "Audit and remove unnecessary stored credentials.",
            ))
        if not section.findings:
            section.add_finding(F(
                "No high-risk misconfigurations detected by quick checks",
                Severity.GOOD,
                "The lightweight heuristics did not flag an obvious issue. This "
                "is not a full assessment.",
                "Follow up with a full CIS benchmark / vuln scan.",
            ))
