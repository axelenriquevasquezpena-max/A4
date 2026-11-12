"""Stage the lab into the authorized Kali guest using VMware Tools."""
from pathlib import Path
import zipfile

from kali_guest import vmrun, VMX

ROOT = Path(__file__).resolve().parents[1]
GUEST = "/home/axel/A4-CIS-2024-2388"


def main():
    archive = ROOT / "private/a4-kali.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
        files = list((ROOT / "scripts").glob("*.py")) + list((ROOT / "scripts").glob("*.sh"))
        files += [ROOT / name for name in ("requirements.txt", "inventory.json", "private/lab-credentials.json",
                                           "private/kali-credentials.json")]
        for path in files:
            package.write(path, path.relative_to(ROOT).as_posix())
    vmrun("copyFileFromHostToGuest", VMX, str(archive), "/tmp/a4-kali.zip")
    vmrun("runScriptInGuest", VMX, "/bin/bash",
          f"umask 077\nmkdir -p {GUEST}\npython3 -m zipfile -e /tmp/a4-kali.zip {GUEST}\nrm /tmp/a4-kali.zip")
    print("Guest staged at " + GUEST)


if __name__ == "__main__":
    main()
