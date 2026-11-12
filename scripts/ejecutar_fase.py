"""Host launcher: run a real test phase in Kali and retrieve its outputs."""
import argparse
from pathlib import Path
import zipfile
import sys

from kali_guest import vmrun, VMX
from desplegar_kali import GUEST, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("audit", "apply", "idempotence", "restart", "timeout", "authentication", "collect"))
    args = parser.parse_args()
    failed = False
    if args.phase != "collect":
        script = {"timeout": "scripts/probar_timeout.py", "authentication": "scripts/probar_autenticacion.py"}.get(
            args.phase, f"scripts/demostrar_kali.py {args.phase}")
        try:
            vmrun("runScriptInGuest", VMX, "/bin/bash",
                  f"cd {GUEST}\n.venv/bin/python {script} > private/{args.phase}.log 2>&1\n"
                  f"result=$?\nprintf '\\nEXIT_STATUS=%s\\n' \"$result\" >> private/{args.phase}.log\nexit $result")
        except RuntimeError as exc:
            failed = True
            print(f"Guest phase returned an error: {exc}")
        log = ROOT / f"private/kali-{args.phase}.log"
        vmrun("copyFileFromGuestToHost", VMX, f"{GUEST}/private/{args.phase}.log", str(log))
        print(log.read_text(encoding="utf-8"))
    vmrun("runProgramInGuest", VMX, "/usr/bin/python3", f"{GUEST}/scripts/exportar_resultados.py")
    archive = ROOT / "private/resultados-kali.zip"
    vmrun("copyFileFromGuestToHost", VMX, "/tmp/a4-resultados.zip", str(archive))
    with zipfile.ZipFile(archive) as package:
        for name in package.namelist():
            target = (ROOT / name).resolve()
            if not target.is_relative_to(ROOT.resolve()):
                raise RuntimeError("Unsafe archive entry")
        package.extractall(ROOT)
    print("Public results retrieved from Kali")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
