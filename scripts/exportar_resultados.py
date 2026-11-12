"""Package public results from Kali; exclude credentials and original backups."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]

with zipfile.ZipFile("/tmp/a4-resultados.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for directory in ("reports", "configs/running", "docs/evidencias"):
        for path in (ROOT / directory).rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(ROOT).as_posix())
