"""Display recorded live-run evidence in a Kali terminal for screenshots/video."""
import argparse
from datetime import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("phase", choices=("audit", "apply", "restart"))
parser.add_argument("--wait", action="store_true")
args = parser.parse_args()
reports = sorted((ROOT / "reports").glob(f"*-{args.phase}/report.json"))
report = json.loads(reports[-1].read_text())
record = report["devices"][0]
print("A4 | AXEL ENRIQUE VASQUEZ PENA | 2024-2388")
print("Hora actual:", datetime.now().astimezone().isoformat(timespec="seconds"))
print("EVIDENCIA GUARDADA de ejecucion real:", report["timestamp"])
print("Fase:", args.phase, "| Router:", record["host"], "| Cisco IOS 12.4")
print("=" * 86)
results = record["after"] if args.phase == "apply" else record["before"]
for result in results:
    print(f"{result['id']:12} {result['status']:7} {result['title']}")
print("=" * 86)
print("Controles PASS:", sum(r["status"] == "PASS" for r in results), "/", len(results))
print("Errores:", record["errors"], "| Startup guardado:", record["saved"])
print((ROOT / f"docs/evidencias/nmap-{args.phase}.txt").read_text())
print((ROOT / f"docs/evidencias/ping-{args.phase}.txt").read_text())
if args.wait:
    input("ENTER para cerrar esta vista de evidencias...")
