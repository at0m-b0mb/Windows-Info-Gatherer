"""Users, groups and account-security posture collector."""

from __future__ import annotations

from .. import demo_data as D
from ..model import Category
from .base import Collector, is_demo, powershell, run


class UsersSecurityCollector(Collector):
    key = "users"
    name = "Users & Security"
    icon = "👤"
    subtitle = "Local accounts, groups and password policy"

    def collect(self) -> Category:
        cat = Category(self.key, self.name, self.icon, self.subtitle)

        users = cat.new_section(
            "Local Accounts", kind="table",
            headers=["User", "Full Name", "Enabled", "Admin", "Last Logon"],
        )
        admins = set()
        if is_demo():
            admins = set(D.ADMINS)
            for row in D.LOCAL_USERS:
                users.add_row(*row)
        else:
            admin_out = run(["net", "localgroup", "Administrators"])
            for line in admin_out.splitlines():
                s = line.strip()
                if s and not s.startswith("-") and "command completed" not in s.lower():
                    admins.add(s.split("\\")[-1])
            for line in powershell(
                "Get-LocalUser | ForEach-Object { '{0}|{1}|{2}|{3}' -f "
                "$_.Name,$_.FullName,$_.Enabled,"
                "($(if($_.LastLogon){$_.LastLogon}else{'Never'})) }"
            ).splitlines():
                p = line.split("|")
                if len(p) >= 3:
                    name = p[0].strip()
                    is_admin = "Yes" if name in admins else "No"
                    users.add_row(name, p[1].strip(), p[2].strip(), is_admin,
                                  p[3].strip() if len(p) > 3 else "")

        groups = cat.new_section(
            "Local Groups", kind="table", headers=["Group", "Description"],
        )
        if is_demo():
            groups.add_row("Administrators", "Full, unrestricted access to the computer")
            groups.add_row("Users", "Ordinary users, cannot make system-wide changes")
            groups.add_row("Remote Desktop Users", "Granted the right to logon remotely")
            groups.add_row("Backup Operators", "Can override security to back up files")
        else:
            for line in powershell(
                "Get-LocalGroup | ForEach-Object { '{0}|{1}' -f "
                "$_.Name,$_.Description }"
            ).splitlines():
                p = line.split("|")
                if len(p) == 2 and p[0].strip():
                    groups.add_row(p[0].strip(), p[1].strip())

        policy = cat.new_section("Password & Account Policy")
        if is_demo():
            policy.kv("Minimum Password Length", "8 characters")
            policy.kv("Maximum Password Age", "42 days")
            policy.kv("Minimum Password Age", "0 days")
            policy.kv("Password History", "24 remembered")
            policy.kv("Lockout Threshold", "10 invalid attempts")
            policy.kv("Lockout Duration", "30 minutes")
        else:
            for line in run(["net", "accounts"]).splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    if v.strip():
                        policy.kv(k.strip(), v.strip())

        return cat
