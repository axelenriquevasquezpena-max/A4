"""Run inside Kali: configure dedicated lab profiles and install the auditor."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    credentials = json.loads((ROOT / "private/kali-credentials.json").read_text())
    (ROOT / "private").chmod(0o700)
    for file in (ROOT / "private").iterdir():
        file.chmod(0o600)

    def root(*args):
        subprocess.run(["sudo", "-S", "-p", "", *args], input=credentials["password"] + "\n",
                       text=True, check=True, timeout=240)

    names = subprocess.check_output(["nmcli", "-t", "-f", "NAME", "connection", "show"], text=True).splitlines()
    if "A4-ADMIN-20242388" not in names:
        root("nmcli", "connection", "add", "type", "ethernet", "ifname", "eth0", "con-name", "A4-ADMIN-20242388",
             "ipv4.method", "manual", "ipv4.addresses", "10.24.23.10/24", "ipv4.never-default", "yes",
             "ipv4.routes", "10.24.88.0/24 10.24.23.1", "ipv6.method", "disabled")
    root("nmcli", "connection", "modify", "A4-ADMIN-20242388", "connection.autoconnect", "yes",
         "connection.autoconnect-priority", "100")
    root("nmcli", "connection", "up", "A4-ADMIN-20242388")
    if "A4-INTERNET-TEMP" not in names:
        root("nmcli", "connection", "add", "type", "ethernet", "ifname", "eth1", "con-name", "A4-INTERNET-TEMP",
             "ipv4.method", "auto", "ipv6.method", "disabled", "connection.autoconnect", "no")
    root("nmcli", "connection", "up", "A4-INTERNET-TEMP")
    subprocess.run(["ip", "-br", "address"], check=True)
    subprocess.run([sys.executable, "-m", "venv", str(ROOT / ".venv")], check=True)
    subprocess.run([str(ROOT / ".venv/bin/python"), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")],
                   check=True, timeout=240)
    subprocess.run(["ping", "-c", "3", "10.24.23.1"], check=True)
    print("KALI_READY", flush=True)


if __name__ == "__main__":
    with open("/tmp/a4-preparacion.log", "w", buffering=1) as log:
        import os
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
        main()
