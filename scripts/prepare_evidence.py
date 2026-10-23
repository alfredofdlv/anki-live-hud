"""Copy only successful, non-personal test evidence into the public documentation."""

from __future__ import annotations

import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    results = ROOT / "test-results"
    evidence = ROOT / "docs/evidence"
    images = ROOT / "docs/images"
    evidence.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)
    suite = ET.parse(results / "unit.xml").getroot().find("testsuite")
    assert suite is not None
    assert suite.attrib["failures"] == suite.attrib["errors"] == "0"
    unit = {key: int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    unit["outcome"] = "passed"
    (evidence / "unit.json").write_text(json.dumps(unit, indent=2) + "\n", encoding="utf-8")
    package = next((ROOT / "dist").glob("*.ankiaddon"))
    artifact = {
        "file": package.name,
        "sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
        "bytes": package.stat().st_size,
    }
    (evidence / "package.json").write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    for source in (
        "native/review.json",
        "native/restart.json",
        "native/finish.json",
        "ui/report.json",
    ):
        report = json.loads((results / source).read_text(encoding="utf-8"))
        assert report["outcome"] == "passed", f"Cannot publish failed evidence: {source}"
        target = evidence / (source.replace("/", "-"))
        target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for name in (
        "reviewer-initial-dark.png",
        "reviewer-answered-dark.png",
        "reviewer-compact-dark.png",
        "reviewer-collapsed.png",
        "reviewer-light.png",
        "reviewer-without-hud.png",
        "native-review.gif",
    ):
        shutil.copyfile(results / "native" / name, images / name)
    print(f"Verified native screenshots, animation and reports saved in {ROOT / 'docs'}")


if __name__ == "__main__":
    main()
