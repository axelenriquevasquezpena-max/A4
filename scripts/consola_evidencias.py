"""Capture actual router/VPCS console evidence, optionally save the baseline."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from netmiko import ConnectHandler
from netmiko._telnetlib.telnetlib import Telnet
from cis_ios import sanitize
from gns3_local import GNS3

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("before", "after", "restart"))
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--configure-vpcs", action="store_true")
    args = parser.parse_args()
    nodes = {n["name"]: n for n in GNS3().nodes()}
    node = nodes["R1-AXEL"]
    credentials = json.loads((ROOT / "private/lab-credentials.json").read_text())
    conn = ConnectHandler(device_type="cisco_ios_telnet", host=node["console_host"],
                          port=node["console"], username="", password="", secret=credentials["secret"],
                          fast_cli=False, global_delay_factor=2)
    output = [f"UTC host: {datetime.now(timezone.utc).isoformat()}"]
    try:
        conn.enable()
        if args.save:
            result = conn.save_config()
            if "[OK]" not in result:
                raise RuntimeError("Save not confirmed")
            output += ["$ write memory", result]
        prompt = re.escape(conn.find_prompt())
        for command in ("show clock", "show version", "show ip interface brief", "show ip ssh", "show cdp",
                        "show line", "ping 10.24.88.20", "ping 10.24.23.10"):
            output += [f"\n$ {command}", conn.send_command(command, expect_string=prompt, read_timeout=60)]
        for command, name in (("show running-config", "running"), ("show startup-config", "startup")):
            config = conn.send_command(command, expect_string=prompt, read_timeout=60)
            (ROOT / f"private/{args.stage}-{name}.cfg").write_text(config, encoding="utf-8")
            (ROOT / f"configs/running/{args.stage}-{name}-real-sanitizado.cfg").write_text(sanitize(config), encoding="utf-8")
    finally:
        conn.disconnect()
    (ROOT / f"docs/evidencias/router-{args.stage}.txt").write_text("\n".join(output), encoding="utf-8")
    node = nodes["PC-CLIENTE"]
    transcript = []
    with Telnet(node["console_host"], node["console"], timeout=20) as session:
        session.write(b"\r")
        session.read_until(b">", timeout=15)
        commands = (["ip 10.24.88.20/24 10.24.88.1", "save"] if args.configure_vpcs else [])
        commands += ["show ip", "ping 10.24.88.1 -c 3", "ping 10.24.23.10 -c 3"]
        for command in commands:
            session.write(command.encode() + b"\r")
            echoed = session.read_until(command.encode(), timeout=10)
            transcript.append((echoed + session.read_until(b">", timeout=30)).decode(errors="replace"))
    (ROOT / f"docs/evidencias/vpcs-{args.stage}.txt").write_text("\n".join(transcript), encoding="utf-8")
    print(f"Console evidence exported: {args.stage}")


if __name__ == "__main__":
    main()
