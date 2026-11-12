"""Open the recorded-evidence viewer in Kali and capture the actual guest screen."""
import argparse
import time
from kali_guest import vmrun, VMX, ROOT
from desplegar_kali import GUEST

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("phase", choices=("audit", "apply", "restart"))
args = parser.parse_args()
command = f"{GUEST}/.venv/bin/python {GUEST}/scripts/mostrar_resultados.py {args.phase} --wait"
vmrun("runScriptInGuest", VMX, "/bin/bash",
      "export DISPLAY=:0\nexport XAUTHORITY=/home/axel/.Xauthority\nxset dpms force on\nxfce4-screensaver-command --deactivate")
vmrun("runProgramInGuest", VMX, "-noWait", "/usr/bin/env", "DISPLAY=:0", "XAUTHORITY=/home/axel/.Xauthority",
      "/usr/bin/xfce4-terminal", "--disable-server", "--maximize", f"--title=A4 CIS - {args.phase}",
      "--command=" + command)
time.sleep(3)  # Allow the new terminal window to render before taking the screenshot.
path = ROOT / f"docs/evidencias/kali-{args.phase}.png"
vmrun("runProgramInGuest", VMX, "/usr/bin/env", "DISPLAY=:0", "XAUTHORITY=/home/axel/.Xauthority",
      "/usr/bin/xfce4-screenshooter", "-f", "-s", "/tmp/a4-evidence.png")
vmrun("copyFileFromGuestToHost", VMX, "/tmp/a4-evidence.png", str(path))
print(path)
