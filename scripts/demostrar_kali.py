"""Live validation wrapper for cis_ios.py. Run inside the A4 Kali guest."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from netmiko import ConnectHandler
from cis_ios import process_device, write_report, all_pass

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("audit", "apply", "idempotence", "restart"))
    args = parser.parse_args()
    credentials = json.loads((ROOT / "private/lab-credentials.json").read_text())
    device = json.loads((ROOT / "inventory.json").read_text())[0]
    evidence = ROOT / "docs/evidencias"
    evidence.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%S%fZ") + "-" + args.phase

    def running():
        with ConnectHandler(device_type="cisco_ios", host=device["host"], fast_cli=False,
                            global_delay_factor=2, **credentials) as conn:
            conn.enable()
            return conn.send_command("show running-config", read_timeout=60)

    original = running() if args.phase == "audit" else None
    mode = "apply" if args.phase in ("apply", "idempotence") else "audit"
    record = process_device(device, credentials, mode, run_id, ConnectHandler)
    report = {"timestamp": now.isoformat(), "mode": mode, "phase": args.phase,
              "benchmark": "CIS Cisco IOS 12 v4.0.0 (10 selected controls)", "devices": [record]}
    if original is not None:
        after = running()
        proof = {"timestamp": now.isoformat(), "before_sha256": hashlib.sha256(original.encode()).hexdigest(),
                 "after_sha256": hashlib.sha256(after.encode()).hexdigest(), "identical": original == after}
        (evidence / "audit-no-changes.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")
        if not proof["identical"]:
            record["errors"].append("Audit changed configuration or another session modified it")
    write_report(report, ROOT / "reports" / run_id)
    results = record["after"] if mode == "apply" else record["before"]
    print(f"{now.isoformat()} PHASE={args.phase}", flush=True)
    for result in results:
        print(f"{result['id']:12} {result['status']:8} {result['title']}", flush=True)
    print("Errors:", record["errors"], "Saved:", record["saved"], flush=True)
    if args.phase in ("audit", "apply", "restart"):
        with (evidence / f"nmap-{args.phase}.txt").open("w") as output:
            subprocess.run(["nmap", "-sT", "-Pn", "-p", "22,23", device["host"]], stdout=output,
                           stderr=subprocess.STDOUT, check=True, timeout=120)
        with (evidence / f"ping-{args.phase}.txt").open("w") as output:
            ping = subprocess.run(["ping", "-c", "5", "10.24.88.20"], stdout=output,
                                  stderr=subprocess.STDOUT, timeout=30)
        if ping.returncode:
            raise RuntimeError("Routing ping failed; see evidence")
    if record["errors"]:
        raise RuntimeError("Device operation failed; inspect report and console")
    if args.phase != "audit" and not all_pass(results):
        raise RuntimeError("Some controls did not pass")
    if args.phase == "idempotence" and record["planned_commands"]:
        raise RuntimeError("Idempotence failed")
    print("PHASE_COMPLETED", flush=True)


if __name__ == "__main__":
    main()
