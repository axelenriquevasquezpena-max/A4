"""Observe an idle SSH session until the router closes it; no keepalive traffic."""
from datetime import datetime, timezone
import json
from pathlib import Path
import select
import time

import paramiko

ROOT = Path(__file__).resolve().parents[1]


def main():
    credentials = json.loads((ROOT / "private/lab-credentials.json").read_text())
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("10.24.23.1", username=credentials["username"], password=credentials["password"],
                   look_for_keys=False, allow_agent=False, timeout=30)
    client.get_transport().set_keepalive(0)
    channel = client.invoke_shell()
    channel.settimeout(30)
    welcome = b""
    while b">" not in welcome and b"#" not in welcome:
        welcome += channel.recv(4096)
    start = time.monotonic()
    result = {"started_utc": datetime.now(timezone.utc).isoformat(), "configured_timeout_seconds": 300,
              "keepalive": False, "closed_by_server": False}
    try:
        while time.monotonic() - start < 900:
            ready, _, _ = select.select([channel], [], [], 5)
            if ready and not channel.recv(4096):
                result["closed_by_server"] = True
                break
            if channel.closed:
                result["closed_by_server"] = True
                break
        result["elapsed_wall_seconds"] = round(time.monotonic() - start, 2)
        result["ended_utc"] = datetime.now(timezone.utc).isoformat()
    finally:
        client.close()
    target = ROOT / "docs/evidencias/ssh-idle-timeout.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result), flush=True)
    if not result["closed_by_server"]:
        raise RuntimeError("No timeout observed within 900 wall-clock seconds")


if __name__ == "__main__":
    main()
