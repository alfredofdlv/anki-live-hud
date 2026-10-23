"""Run real Anki Desktop against a new disposable profile, never the default base.

Usage: python scripts/test_native.py [--installed-exe PATH]
The installed executable can be exercised through an isolated test-driver add-on.
No driver, test deck, or test code is included in the release archive.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def prepare() -> Path:
    from anki.collection import Collection
    from anki.lang import set_lang
    from aqt.profiles import ProfileManager

    from scripts.build import build

    base = Path(tempfile.mkdtemp(prefix="anki-live-hud-"))
    set_lang("en_US")
    pm = ProfileManager(base)
    pm.setupMeta()
    pm.create("HUD Test")
    pm.load("HUD Test")
    pm.meta["defaultLang"] = "en_US"
    pm.set_update_check(False)
    pm.set_reduce_motion(False)
    pm.profile["autoSync"] = False
    pm.profile["syncMedia"] = False
    pm.save()
    pm.db.close()
    profile = base / "HUD Test"
    profile.mkdir(exist_ok=True)
    col = Collection(str(profile / "collection.anki2"))
    did = col.decks.id("Everyday English")
    col.decks.set_current(did)
    examples = [
        ("What does “put up with” mean?", "To tolerate someone or something."),
        ("What does “look forward to” mean?", "To feel excited about a future event."),
        ("What does “figure out” mean?", "To understand or solve something."),
        ("What does “come across” mean?", "To find or meet by chance."),
    ]
    for index in range(16):
        front, back = examples[index % len(examples)]
        note = col.new_note(col.models.by_name("Basic"))
        note["Front"] = (
            '<div style="font-size:12px;letter-spacing:2px;opacity:.55;margin:60px 0 28px">'
            "EVERYDAY ENGLISH</div>" + front
        )
        note["Back"] = back
        col.add_note(note, did)
    finish_deck = col.decks.id("Finish test")
    note = col.new_note(col.models.by_name("Basic"))
    note["Front"], note["Back"] = "Finish this study queue", "Rate this card Easy."
    col.add_note(note, finish_deck)
    col.close()
    addon_path = base / "addons21/anki_live_hud"
    addon_path.mkdir(parents=True)
    with ZipFile(build()) as archive:
        archive.extractall(addon_path)
    driver = base / "addons21/hud_test_driver"
    driver.mkdir()
    driver.joinpath("__init__.py").write_text(
        "import os, sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "from aqt import gui_hooks\n"
        "from aqt.qt import QTimer\n"
        "from scripts.native_driver import run\n"
        "gui_hooks.profile_did_open.append(lambda: QTimer.singleShot(1200, run))\n",
        encoding="utf-8",
    )
    return base


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-exe", type=Path)
    args = parser.parse_args()
    output = ROOT / "test-results/native"
    output.mkdir(parents=True, exist_ok=True)
    base = prepare()
    env = dict(os.environ)
    env.update(
        {
            "HUD_TEST_ROOT": str(ROOT),
            "HUD_TEST_OUTPUT": str(output),
            "QT_QPA_PLATFORM": "windows" if sys.platform == "win32" else "offscreen",
            "PYTHONUTF8": "1",
            "ANKI_SINGLE_INSTANCE_KEY": "anki-live-hud-test-" + base.name,
        }
    )
    command = (
        [str(args.installed_exe)]
        if args.installed_exe
        else [
            sys.executable,
            "-c",
            "import aqt; aqt.run()",
        ]
    )
    runs = []
    for phase in ("review", "restart", "finish"):
        env["HUD_TEST_PHASE"] = phase
        (output / f"{phase}.json").unlink(missing_ok=True)
        command_line = command + ["-b", str(base), "-p", "HUD Test", "-l", "en_US"]
        result = subprocess.run(
            command_line,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=150,
            cwd=ROOT,
        )
        output.joinpath(f"{phase}.log").write_bytes(result.stdout)
        report_path = output / f"{phase}.json"
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
        print(
            json.dumps({"phase": phase, "exit_code": result.returncode, "report": report}, indent=2)
        )
        runs.append(report)
        if result.returncode or report.get("outcome") != "passed":
            print(result.stdout.decode("utf-8", errors="replace"))
            raise SystemExit(1)
    from PIL import Image

    images = [Image.open(p).convert("RGB") for p in sorted(output.glob("frame-*.png"))]
    if images:
        images[0].save(
            output / "native-review.gif",
            save_all=True,
            append_images=images[1:],
            duration=70,
            loop=0,
        )
    for image in images:
        image.close()
    print(f"Native tests passed. Disposable base retained for inspection: {base}")


if __name__ == "__main__":
    main()
