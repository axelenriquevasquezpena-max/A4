"""One-time bootstrap of the fresh A4 router and VPCS over GNS3 consoles.

Creates private lab credentials. Refuses to overwrite an addressed router.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import secrets
import string

from netmiko import ConnectHandler
from netmiko._telnetlib.telnetlib import Telnet

from cis_ios import sanitize
from gns3_local import GNS3

ROOT = Path(__file__).resolve().parents[1]


def main():
    gns3 = GNS3()
    nodes = {n["name"]: n for n in gns3.nodes()}
    router = nodes["R1-AXEL"]
    conn = ConnectHandler(device_type="cisco_ios_telnet", host=router["console_host"],
                          port=router["console"], username="", password="",
                          fast_cli=False, global_delay_factor=2)
    evidence = ROOT / "docs/evidencias"
    evidence.mkdir(parents=True, exist_ok=True)
    try:
        config = conn.send_command("show running-config", read_timeout=60)
        if "ip address 10.24." in config:
            raise RuntimeError("Router already addressed: refusing to reset the existing configuration")
        private = ROOT / "private"
        private.mkdir(exist_ok=True)
        credentials_file = private / "lab-credentials.json"
        if credentials_file.exists():
            credentials = json.loads(credentials_file.read_text())
        else:
            alphabet = string.ascii_letters + string.digits
            credentials = {"username": "axel", "password": "".join(secrets.choice(alphabet) for _ in range(22)),
                           "secret": "".join(secrets.choice(alphabet) for _ in range(24))}
            credentials_file.write_text(json.dumps(credentials, indent=2), encoding="utf-8")
            credentials_file.chmod(0o600)
        (private / "factory-running.cfg").write_text(config, encoding="utf-8")
        template = (ROOT / "configs/bootstrap-R1.txt").read_text(encoding="utf-8")
        commands = [s.strip() for s in template.splitlines()
                    if s.strip() and not s.startswith("!") and s.strip() not in ("enable", "configure terminal", "end")]
        commands = [s.replace("CAMBIAR_CLAVE_ENABLE", credentials["secret"])
                    .replace("CAMBIAR_CLAVE_USUARIO", credentials["password"]) for s in commands]
        conn.send_config_set(commands, error_pattern=r"% (?:Invalid|Incomplete|Ambiguous)")
        conn.config_mode()
        output = conn.send_command_timing("crypto key generate rsa general-keys modulus 2048",
                                          last_read=5, read_timeout=180)
        if "% Invalid" in output or "[OK]" not in output:
            raise RuntimeError("RSA generation not confirmed; inspect console")
        conn.exit_config_mode()
        now = datetime.now(timezone.utc)
        conn.send_command_timing(f"clock set {now:%H:%M:%S} {now.day} {now:%b} {now.year}", last_read=4)
        conn.clear_buffer()
        conn.set_base_prompt()
        saved = conn.save_config()
        if "[OK]" not in saved:
            raise RuntimeError("Initial startup-config save unconfirmed")
        sections = [f"UTC Windows: {now.isoformat()}"]
        for command in ("show clock", "show version", "show ip interface brief", "show ip ssh"):
            sections += [f"\n$ {command}", conn.send_command(command, read_timeout=60)]
        (evidence / "01-router-bootstrap.txt").write_text("\n".join(sections), encoding="utf-8")
        config = conn.send_command("show running-config", read_timeout=60)
        (private / "bootstrap-running.cfg").write_text(config, encoding="utf-8")
        (ROOT / "configs/running/bootstrap-real-sanitizado.cfg").write_text(sanitize(config), encoding="utf-8")
        print("Router configured, RSA 2048 generated, baseline saved. Credentials: private/lab-credentials.json")
    finally:
        conn.disconnect()

    client = nodes["PC-CLIENTE"]
    transcript = []
    with Telnet(client["console_host"], client["console"], timeout=20) as telnet:
        telnet.write(b"\r")
        telnet.read_until(b">", timeout=15)
        for command in ("ip 10.24.88.20/24 10.24.88.1", "save", "show ip", "ping 10.24.88.1 -c 3"):
            telnet.write(command.encode() + b"\r")
            echoed = telnet.read_until(command.encode(), timeout=10)
            transcript.append((echoed + telnet.read_until(b">", timeout=30)).decode(errors="replace"))
    (evidence / "02-vpcs-bootstrap.txt").write_text("\n".join(transcript), encoding="utf-8")
    print("VPCS configured. See docs/evidencias for actual console output.")


if __name__ == "__main__":
    main()
