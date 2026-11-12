"""VMware Tools bridge. Credentials are read only from ignored private files."""
import argparse
import json
from pathlib import Path
import subprocess

from gns3_local import GNS3

ROOT = Path(__file__).resolve().parents[1]
VMX = r"C:\Virtual Machines\Kali Linux\Kali Linux.vmx"


def vmrun(*arguments):
    config = GNS3().config
    credentials = json.loads((ROOT / "private/kali-credentials.json").read_text())
    command = [config["VMware"]["vmrun_path"], "-gu", credentials["username"], "-gp", credentials["password"],
               *arguments]
    result = subprocess.run(command, capture_output=True, text=True, timeout=1200)
    if result.returncode:
        # Do not print command lines: they contain the guest password.
        raise RuntimeError(result.stdout.strip() or result.stderr.strip() or "VMware guest operation failed")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("list", "put", "get", "run"))
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    if args.action == "list":
        print(vmrun("listProcessesInGuest", VMX))
    elif args.action == "put":
        print(vmrun("copyFileFromHostToGuest", VMX, *args.paths))
    elif args.action == "get":
        print(vmrun("copyFileFromGuestToHost", VMX, *args.paths))
    else:
        print(vmrun("runProgramInGuest", VMX, "/bin/bash", *args.paths))


if __name__ == "__main__":
    main()
