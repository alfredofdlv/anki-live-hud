"""Build and validate a deterministic .ankiaddon archive with runtime files only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = {
    "__init__.py",
    "hooks.py",
    "settings.py",
    "state.py",
    "statistics.py",
    "manifest.json",
    "config.json",
    "config.md",
    "web/hud.html",
    "web/hud.css",
    "web/hud.js",
}


def build(output: Path | None = None) -> Path:
    manifest = json.loads((ROOT / "addon/manifest.json").read_text(encoding="utf-8"))
    output = output or ROOT / "dist" / f"anki-live-hud-{manifest['version']}.ankiaddon"
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for name in sorted(RUNTIME | {"LICENSE"}):
            source = ROOT / "LICENSE" if name == "LICENSE" else ROOT / "addon" / name
            info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes())
    with ZipFile(output) as archive:
        assert set(archive.namelist()) == RUNTIME | {"LICENSE"}
        assert archive.testzip() is None
        assert json.loads(archive.read("manifest.json"))["package"] == "anki_live_hud"
        for name in archive.namelist():
            assert "__pycache__" not in name and not name.startswith(("/", "addon/"))
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8"
    )
    return output


if __name__ == "__main__":
    print(build())
