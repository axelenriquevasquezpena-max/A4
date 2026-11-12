"""Measure the real SSH retry limit and incomplete-authentication timeout."""
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import time
import paramiko

ROOT = Path(__file__).resolve().parents[1]


def transport():
    connection = paramiko.Transport(socket.create_connection(("10.24.23.1", 22), timeout=20))
    connection.start_client(timeout=30)
    return connection


def main():
    result = {"started_utc": datetime.now(timezone.utc).isoformat(), "attempts": []}
    connection = transport()
    try:
        for attempt in range(1, 6):
            try:
                connection.auth_password("axel", "A4-INTENTIONALLY-INCORRECT-PASSWORD", fallback=False)
                result["attempts"].append({"attempt": attempt, "unexpected_login": True})
                break
            except paramiko.SSHException as exc:
                result["attempts"].append({"attempt": attempt, "exception": type(exc).__name__,
                                           "connection_active": connection.is_active()})
                if not connection.is_active():
                    break
        result["retry_connection_closed"] = not connection.is_active()
    finally:
        connection.close()
    connection = transport()
    start = time.monotonic()
    try:
        # Wait for the server's authentication timer, without sending credentials.
        connection.join(timeout=240)
        result["authentication_timeout"] = {
            "closed_by_server": not connection.is_active(),
            "elapsed_wall_seconds": round(time.monotonic() - start, 2), "configured_seconds": 60}
    finally:
        connection.close()
    result["ended_utc"] = datetime.now(timezone.utc).isoformat()
    path = ROOT / "docs/evidencias/ssh-authentication-tests.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
