"""Activate the persistent A4 profile and prefer it over the old DHCP profile."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
credentials = json.loads((ROOT / "private/kali-credentials.json").read_text())
for command in (
    ["nmcli", "connection", "modify", "A4-ADMIN-20242388", "connection.autoconnect", "yes",
     "connection.autoconnect-priority", "100"],
    ["nmcli", "connection", "up", "A4-ADMIN-20242388"],
):
    subprocess.run(["sudo", "-S", "-p", "", *command], input=credentials["password"] + "\n",
                   text=True, check=True, timeout=90)
