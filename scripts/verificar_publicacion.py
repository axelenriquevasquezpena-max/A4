"""Check tracked/unignored text files for known local credentials before push."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
secrets = []
for name in ("lab-credentials.json", "kali-credentials.json"):
    path = ROOT / "private" / name
    if path.exists():
        values = json.loads(path.read_text())
        # Very short passwords can occur coincidentally in timestamps/UUIDs.
        secrets += [v for k, v in values.items() if k in ("password", "secret") and len(v) >= 8]
names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                                cwd=ROOT).decode().split("\0")
problems = []
for name in set(names):
    if not name:
        continue
    path = ROOT / name
    if name.startswith("private/"):
        problems.append(name)
        continue
    if not path.is_file() or path.suffix.lower() in (".png", ".jpg", ".zip"):
        continue
    text = path.read_text(encoding="utf-8")
    if any(secret in text for secret in secrets):
        problems.append(name)
    if path.suffix == ".cfg" and re.search(r"(?m)^\s*(?:enable secret|username \S+.*secret|snmp-server community) ", text):
        problems.append(name)
if problems:
    raise SystemExit("Review files before publication: " + ", ".join(sorted(set(problems))))
print("No known lab secrets or unsanitized IOS credentials found in public text files.")
