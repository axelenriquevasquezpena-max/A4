"""Subset auditor/remediator for CIS Cisco IOS 12 v4.0.0. Run from Kali."""

import argparse
from datetime import datetime, timezone
import getpass
import ipaddress
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
ERROR_PATTERN = r"(?im)^%.*(?:Invalid|Incomplete|Ambiguous|Error|Failed|not supported)"


def blocks(config, prefix):
    result = []
    current = None
    for line in config.splitlines():
        if line and not line[0].isspace():
            current = None
            if line.startswith(prefix):
                current = {"header": line.strip(), "lines": []}
                result.append(current)
        elif current is not None and line.strip():
            current["lines"].append(line.strip())
    return result


def timeout_ok(block):
    values = [s for s in block["lines"] if s.startswith("exec-timeout ")]
    if not values:
        return True  # IOS 12 default: 10 minutes, omitted from running-config.
    match = re.fullmatch(r"exec-timeout (\d+)(?: (\d+))?", values[-1])
    if not match:
        return False
    minutes, seconds = int(match[1]), int(match[2] or 0)
    return seconds < 60 and 0 < minutes * 60 + seconds <= 600


def evaluate(config, ssh):
    """Return ten controls with evidence-free status and exact remediation plan."""
    if not re.search(r"(?m)^hostname \S+", config) or not re.search(r"(?m)^end\s*$", config):
        raise ValueError("Incomplete running-config")
    lines = set(config.splitlines())
    vty = blocks(config, "line vty ")
    aux = blocks(config, "line aux ")
    console = blocks(config, "line con ")
    results = []

    def add(cid, title, ok, commands):
        results.append({"id": cid, "title": title,
                        "status": "UNKNOWN" if ok is None else ("PASS" if ok else "FAIL"),
                        "commands": commands if ok is False else []})

    def per_line(cid, title, groups, predicate, command):
        bad = [b for b in groups if not predicate(b)]
        commands = [c for b in bad for c in (b["header"], command, "exit")]
        add(cid, title, not bad if groups else None, commands)

    per_line("1.2.2", "Solo SSH en todas las VTY", vty,
             lambda b: "transport input ssh" in b["lines"], "transport input ssh")
    per_line("1.2.3", "AUX sin EXEC", aux,
             lambda b: "no exec" in b["lines"], "no exec")
    per_line("1.2.7", "Timeout consola <= 10 minutos", console, timeout_ok, "exec-timeout 5 0")
    per_line("1.2.9", "Timeout VTY <= 10 minutos", vty, timeout_ok, "exec-timeout 5 0")
    timeout = re.search(r"Authentication timeout:\s*(\d+)\s*secs", ssh, re.I)
    retries = re.search(r"Authentication retries:\s*(\d+)", ssh, re.I)
    add("2.1.1.1.4", "SSH autenticacion <= 60 segundos",
        0 < int(timeout[1]) <= 60 if timeout else None, ["ip ssh time-out 60"])
    add("2.1.1.1.5", "SSH reintentos <= 3",
        0 < int(retries[1]) <= 3 if retries else None, ["ip ssh authentication-retries 2"])
    operational = bool(re.search(r"SSH Enabled - version 2\.0\b", ssh, re.I))
    ssh_known = bool(re.search(r"SSH (?:Enabled|Disabled)", ssh, re.I))
    add("2.1.1.2", "Solo SSHv2", ("ip ssh version 2" in lines and operational) if ssh_known else None,
        ["ip ssh version 2"])
    for cid, title, command in [
        ("2.1.2", "CDP desactivado", "no cdp run"),
        ("2.1.6", "TCP keepalives entrantes", "service tcp-keepalives-in"),
        ("2.1.7", "TCP keepalives salientes", "service tcp-keepalives-out"),
    ]:
        add(cid, title, command in lines, [command])
    return results


def sanitize(config):
    output = ["! Running-config real sanitizado; no usar como respaldo restaurable."]
    in_certificate = False
    for line in config.splitlines():
        stripped = line.strip()
        if stripped.startswith("crypto pki certificate chain"):
            in_certificate = True
            output.append("! [CERTIFICADOS OMITIDOS]")
            continue
        if in_certificate:
            if not line or line[0].isspace() or stripped == "!":
                continue
            in_certificate = False
        if re.search(r"(?i)\b(secret|password|community|key-string|private-key)\b", line) or re.search(
                r"(?i)^\s*(username |snmp-server host |tacacs-server key |radius-server key |crypto isakmp key )", line):
            output.append("! [CREDENCIAL OMITIDA]")
        else:
            output.append(line)
    return "\n".join(output) + "\n"


def snapshot(conn):
    config = conn.send_command("show running-config")
    ssh = conn.send_command("show ip ssh")
    return config, evaluate(config, ssh)


def all_pass(results):
    return bool(results) and all(r["status"] == "PASS" for r in results)


def process_device(device, credentials, mode, run_id, connector, root=ROOT):
    record = {"name": device["name"], "host": device["host"], "mode": mode,
              "before": [], "after": [], "planned_commands": [], "errors": [], "saved": False}
    rawdir = root / "private" / run_id
    publicdir = root / "configs" / "running"
    rawdir.mkdir(parents=True, exist_ok=True)
    publicdir.mkdir(parents=True, exist_ok=True)
    params = dict(device_type="cisco_ios", host=device["host"], port=device.get("port", 22),
                  conn_timeout=30, auth_timeout=30, banner_timeout=60,
                  fast_cli=False, global_delay_factor=2, **credentials)
    conn = None

    def export(config, stage):
        name = f"{run_id}-{device['name']}-{stage}.cfg"
        (publicdir / name).write_text(sanitize(config), encoding="utf-8")
        if stage == "before":
            path = rawdir / f"{device['name']}-before.cfg"
            path.write_text(config, encoding="utf-8")
            path.chmod(0o600)

    try:
        conn = connector(**params)
        conn.enable()
        version = conn.send_command("show version")
        (rawdir / f"{device['name']}-version.txt").write_text(version, encoding="utf-8")
        if not re.search(r"\bVersion\s+12\.\d", version):
            raise ValueError("This profile requires IOS 12")
        config, record["before"] = snapshot(conn)
        export(config, "before")
        if mode == "apply":
            if any(r["status"] == "UNKNOWN" for r in record["before"]):
                record["errors"].append("Datos UNKNOWN: revisar antes de aplicar")
                return record
            commands = [c for r in record["before"] for c in r["commands"]]
            record["planned_commands"] = commands
            try:
                if commands:
                    output = conn.send_config_set(commands, error_pattern=ERROR_PATTERN)
                    if re.search(ERROR_PATTERN, output):
                        raise RuntimeError("IOS rejected a command")
            except Exception as exc:
                record["errors"].append(f"Aplicacion parcial o fallida: {type(exc).__name__}")
                if conn.check_config_mode():
                    conn.exit_config_mode()
            finally:
                config, record["after"] = snapshot(conn)
                export(config, "after")
            if all_pass(record["after"]) and not record["errors"]:
                fresh = connector(**params)
                try:
                    fresh.enable()
                    fresh.send_command("show clock")
                finally:
                    fresh.disconnect()
                saved = conn.save_config()
                if not re.search(r"\[OK\]", saved) or re.search(ERROR_PATTERN, saved):
                    raise RuntimeError("Startup save not confirmed")
                record["saved"] = True
    except Exception as exc:
        # Exception text can contain command output or credentials: retain type only.
        record["errors"].append(f"Operacion fallida: {type(exc).__name__}; revisar consola/conectividad/version")
    finally:
        if conn is not None:
            try:
                conn.disconnect()
            except Exception:
                record["errors"].append("Fallo al cerrar sesion")
    return record


def load_inventory(path):
    devices = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(devices, list) or not devices:
        raise ValueError("Inventory must be a nonempty list")
    names, targets = set(), set()
    for d in devices:
        if not isinstance(d, dict) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", d.get("name", "")):
            raise ValueError("Invalid device name")
        ipaddress.ip_address(d["host"])
        port = d.get("port", 22)
        if type(port) is not int or not 1 <= port <= 65535:
            raise ValueError("Invalid port")
        target = (d["host"], port)
        if d["name"] in names or target in targets:
            raise ValueError("Duplicate device")
        names.add(d["name"])
        targets.add(target)
    return devices


def write_report(report, directory):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Informe de ejecución", "", f"UTC: {report['timestamp']}",
             f"Modo: {report['mode']}", "", "Alcance: 10 controles CIS IOS 12 v4.0.0 seleccionados.", ""]
    for d in report["devices"]:
        lines += [f"## {d['name']} — {d['host']}", "", f"Startup guardado: {d['saved']}", ""]
        for stage in ("before", "after"):
            if not d[stage]:
                continue
            lines += [f"### {stage}", "", "| CIS | Control | Estado |", "|---|---|---|"]
            lines += [f"| {r['id']} | {r['title']} | {r['status']} |" for r in d[stage]]
            lines.append("")
        lines += [f"- ERROR: {e}" for e in d["errors"]]
        lines.append("")
    (directory / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("audit", "apply"))
    parser.add_argument("--inventory", type=Path, default=ROOT / "inventory.json")
    args = parser.parse_args()
    try:
        devices = load_inventory(args.inventory)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(f"Inventario invalido: {type(exc).__name__}")
    try:
        from netmiko import ConnectHandler
    except ImportError:
        parser.error("Instalar requirements.txt en el entorno virtual")
    credentials = {"username": input("Usuario: ").strip(), "password": getpass.getpass("Password SSH: "),
                   "secret": getpass.getpass("Enable secret: ")}
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%S%fZ")
    report = {"timestamp": now.isoformat(), "mode": args.mode,
              "benchmark": "CIS Cisco IOS 12 v4.0.0 (10 selected controls)", "devices": []}
    directory = ROOT / "reports" / run_id
    for device in devices:
        print(f"{args.mode}: {device['name']} ({device['host']})")
        report["devices"].append(process_device(device, credentials, args.mode, run_id, ConnectHandler))
        write_report(report, directory)  # Persist each device, even if a later device fails.
    print(f"Informe: {directory / 'report.md'}")
    success = all(not d["errors"] and all_pass(d["after"] if args.mode == "apply" else d["before"])
                  for d in report["devices"])
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
