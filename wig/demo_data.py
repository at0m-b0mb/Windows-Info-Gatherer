"""Realistic, internally-consistent demo values.

Used whenever WinRecon runs off Windows (or with ``--demo``) so every page is
fully populated for demos, screenshots and development.  The numbers are made
up but coherent -- one fictional workstation, ``DESKTOP-KP7724``.
"""

HOST = "DESKTOP-KP7724"
DOMAIN = "WORKGROUP"
USER = "KP"
DOMAIN_USER = f"{HOST.lower()}\\kp"

SYSTEM = {
    "Host Name": HOST,
    "OS Name": "Microsoft Windows 11 Pro",
    "OS Version": "10.0.22631 N/A Build 22631",
    "OS Build": "22631.4317",
    "OS Manufacturer": "Microsoft Corporation",
    "Registered Owner": "Kailash Parshad",
    "Registered Organization": "at0m-b0mb Labs",
    "Product ID": "00330-80000-00000-AA123",
    "Original Install Date": "2024-03-11, 09:42:17",
    "System Boot Time": "2026-07-15, 07:58:03",
    "System Manufacturer": "ASUSTeK COMPUTER INC.",
    "System Model": "ROG Zephyrus G14 GA402RJ",
    "System Type": "x64-based PC",
    "BIOS Version": "GA402RJ.320, 2024-01-18",
    "Domain": DOMAIN,
    "Time Zone": "(UTC+05:30) Chennai, Kolkata, Mumbai, New Delhi",
}

CPU = {
    "Name": "AMD Ryzen 9 6900HS with Radeon Graphics",
    "Cores": "8",
    "Logical Processors": "16",
    "Max Clock Speed": "3301 MHz",
    "Architecture": "x64",
    "Virtualization": "Enabled",
    "L2 Cache": "4096 KB",
    "L3 Cache": "16384 KB",
}

MEMORY_MODULES = [
    # Bank, Capacity, Speed, Manufacturer, Part
    ["Channel A / DIMM 0", "8 GB", "4800 MHz", "Samsung", "M425R1GB4BB0-CQKOD"],
    ["Channel B / DIMM 0", "8 GB", "4800 MHz", "Samsung", "M425R1GB4BB0-CQKOD"],
]
MEMORY_TOTAL_GB = 16

DISKS = [
    # Model, Interface, Size, Media
    ["Micron 2450 NVMe 1024GB", "NVMe", "953.87 GB", "Fixed hard disk"],
]
VOLUMES = [
    # Drive, Label, FS, Capacity, Free, %Free
    ["C:", "Windows", "NTFS", "476.42 GB", "182.03 GB", "38%"],
    ["D:", "Data", "NTFS", "477.45 GB", "301.77 GB", "63%"],
]
GPUS = [
    ["NVIDIA GeForce RTX 3050 Ti Laptop GPU", "31.0.15.3161", "4 GB"],
    ["AMD Radeon(TM) Graphics", "31.0.12027.9001", "512 MB"],
]

LOCAL_USERS = [
    # Name, FullName, Enabled, Admin, LastLogon
    ["Administrator", "", "No", "Yes", "Never"],
    ["DefaultAccount", "", "No", "No", "Never"],
    ["Guest", "", "No", "No", "Never"],
    ["KP", "Kailash Parshad", "Yes", "Yes", "2026-07-15 07:58"],
    ["svc_backup", "Backup Service", "Yes", "No", "2026-07-14 02:00"],
]
ADMINS = ["Administrator", "KP"]

NIC = [
    # Name, IPv4, Mask, Gateway, MAC, DHCP
    ["Wi-Fi", "192.168.1.37", "255.255.255.0", "192.168.1.1", "A4-6B-B6-2C-8D-1F", "Enabled"],
    ["Ethernet", "10.0.0.14", "255.255.255.0", "10.0.0.1", "00-E0-4C-68-12-9A", "Disabled"],
]
DNS = ["192.168.1.1", "1.1.1.1", "8.8.8.8"]

LISTENING = [
    # Proto, Local, State, PID, Process
    ["TCP", "0.0.0.0:135", "LISTENING", "968", "svchost.exe"],
    ["TCP", "0.0.0.0:445", "LISTENING", "4", "System"],
    ["TCP", "127.0.0.1:5432", "LISTENING", "6112", "postgres.exe"],
    ["TCP", "0.0.0.0:3389", "LISTENING", "1240", "svchost.exe (TermService)"],
    ["TCP", "192.168.1.37:139", "LISTENING", "4", "System"],
    ["UDP", "0.0.0.0:5353", "--", "3120", "mDNSResponder.exe"],
]
SHARES = [
    ["ADMIN$", "C:\\Windows", "Remote Admin"],
    ["C$", "C:\\", "Default share"],
    ["IPC$", "", "Remote IPC"],
    ["Backups", "D:\\Backups", "Team backups"],
]
WIFI_PROFILES = [
    # SSID, Auth, Cipher, Key(demo)
    ["HackLab-5G", "WPA2-Personal", "CCMP", "S3cur3-L@b-2026"],
    ["CoffeeShop_Guest", "Open", "None", ""],
    ["at0m-home", "WPA3-Personal", "CCMP", "n0tth3r3alp@ss"],
]

INSTALLED = [
    # Name, Version, Publisher
    ["Google Chrome", "126.0.6478.127", "Google LLC"],
    ["Mozilla Firefox", "127.0.1", "Mozilla"],
    ["Python 3.12.4 (64-bit)", "3.12.4150.0", "Python Software Foundation"],
    ["Git", "2.45.2", "The Git Development Community"],
    ["Wireshark 4.2.5", "4.2.5", "The Wireshark developer community"],
    ["Nmap 7.94", "7.94", "Nmap Project"],
    ["VMware Workstation", "17.5.2", "VMware, Inc."],
    ["7-Zip 24.05", "24.05", "Igor Pavlov"],
    ["Microsoft Visual C++ 2015-2022 Redistributable", "14.40.33810", "Microsoft Corporation"],
    ["Notepad++", "8.6.9", "Notepad++ Team"],
]
HOTFIXES = ["KB5040442", "KB5039895", "KB5037591", "KB5027397", "KB5012170"]

PROCESSES = [
    # Name, PID, Mem(KB), User
    ["System", "4", "144", "SYSTEM"],
    ["svchost.exe", "968", "18,204", "SYSTEM"],
    ["explorer.exe", "6540", "112,880", USER],
    ["chrome.exe", "8112", "384,512", USER],
    ["Code.exe", "9330", "298,140", USER],
    ["MsMpEng.exe", "3204", "241,760", "SYSTEM"],
    ["powershell.exe", "10456", "84,220", USER],
    ["postgres.exe", "6112", "56,900", "NETWORK SERVICE"],
]
SERVICES = [
    # Name, Display, State, Start
    ["WinDefend", "Microsoft Defender Antivirus Service", "Running", "Automatic"],
    ["MpsSvc", "Windows Defender Firewall", "Running", "Automatic"],
    ["TermService", "Remote Desktop Services", "Running", "Manual"],
    ["Spooler", "Print Spooler", "Running", "Automatic"],
    ["Schedule", "Task Scheduler", "Running", "Automatic"],
    ["LanmanServer", "Server (SMB)", "Running", "Automatic"],
    ["wuauserv", "Windows Update", "Stopped", "Manual"],
    ["sshd", "OpenSSH SSH Server", "Running", "Automatic"],
]
STARTUP = [
    # Name, Command, Location
    ["Steam", "\"C:\\Program Files\\Steam\\steam.exe\" -silent", "HKLM\\...\\Run"],
    ["OneDrive", "C:\\Users\\KP\\AppData\\Local\\Microsoft\\OneDrive\\OneDrive.exe /background", "HKCU\\...\\Run"],
    ["RustDesk", "C:\\Program Files\\RustDesk\\rustdesk.exe --tray", "Startup folder"],
]
SCHEDULED_TASKS = [
    ["\\Backups\\NightlyBackup", "Ready", "Daily 02:00", "svc_backup"],
    ["\\GoogleUpdateTaskMachineUA", "Ready", "Daily 09:00", "SYSTEM"],
    ["\\Microsoft\\Windows\\Defrag\\ScheduledDefrag", "Ready", "Weekly", "SYSTEM"],
]

ENV_VARS = {
    "COMPUTERNAME": HOST,
    "USERNAME": USER,
    "USERDOMAIN": HOST,
    "NUMBER_OF_PROCESSORS": "16",
    "OS": "Windows_NT",
    "PROCESSOR_ARCHITECTURE": "AMD64",
    "SystemRoot": "C:\\Windows",
    "TEMP": "C:\\Users\\KP\\AppData\\Local\\Temp",
    "PATH": "C:\\Windows\\system32;C:\\Windows;C:\\Program Files\\Git\\cmd;C:\\Python312\\;...",
}

PRIVILEGES = [
    ["SeShutdownPrivilege", "Shut down the system", "Disabled"],
    ["SeChangeNotifyPrivilege", "Bypass traverse checking", "Enabled"],
    ["SeUndockPrivilege", "Remove computer from docking station", "Disabled"],
    ["SeIncreaseWorkingSetPrivilege", "Increase a process working set", "Disabled"],
    ["SeTimeZonePrivilege", "Change the time zone", "Disabled"],
    ["SeBackupPrivilege", "Back up files and directories", "Disabled"],
]

DEFENDER = {
    "Antivirus Enabled": "True",
    "Real-Time Protection": "True",
    "Tamper Protection": "False",
    "Cloud Protection": "True",
    "Signature Version": "1.415.283.0",
    "Signature Age (days)": "1",
}
