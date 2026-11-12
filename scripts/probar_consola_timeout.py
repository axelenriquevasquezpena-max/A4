"""Observe real console inactivity without sending input during the timer."""
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import uuid

from netmiko._telnetlib.telnetlib import Telnet
from gns3_local import GNS3

ROOT = Path(__file__).resolve().parents[1]
node = next(n for n in GNS3().nodes() if n["name"] == "R1-AXEL")
with Telnet(node["console_host"], node["console"], timeout=20) as console:
    console.write(b"\r")
    # GNS3 replays console history. Synchronize using a unique live command;
    # a historical prompt or logout must never count as a new timeout.
    marker = ("show clock | include A4TIMEOUT" + uuid.uuid4().hex[:12]).encode()
    console.write(marker + b"\r")
    initial = console.read_until(marker, timeout=30)
    if marker not in initial or b"R1-AXEL#" not in console.read_until(b"R1-AXEL#", timeout=30):
        raise RuntimeError("Fresh console prompt not observed")
    result = {"started_utc": datetime.now(timezone.utc).isoformat(), "configured_timeout_seconds": 300}
    start = time.monotonic()
    output = console.read_until(b"Press RETURN to get started", timeout=900)
    elapsed = round(time.monotonic() - start, 2)
    result.update({"elapsed_wall_seconds": elapsed,
                   "returned_to_login": b"Press RETURN to get started" in output and elapsed >= 270,
                   "console_event": "Press RETURN to get started" if b"Press RETURN to get started" in output else "No logout observed",
                   "ended_utc": datetime.now(timezone.utc).isoformat()})
(ROOT / "docs/evidencias/console-idle-timeout.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
