"""Headless Chromium checks of the production HTML/CSS/JS, with synthetic inputs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.preview import fixture  # noqa: E402


def main() -> None:
    output = ROOT / "test-results/ui"
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    with sync_playwright() as p:
        executable = os.getenv("HUD_CHROMIUM")
        browser = p.chromium.launch(**({"executable_path": executable} if executable else {}))
        page = browser.new_page(viewport={"width": 900, "height": 900})
        errors = []
        requests = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append(request.url))
        page.set_content(fixture(), wait_until="load")
        page.evaluate(
            "() => {window.hudCommands=[];window.pycmd=c=>hudCommands.push(c);"
            "AnkiLiveHUD.connect();}"
        )

        def check(name, condition):
            assert condition, name
            checks.append(name)

        def text(id):
            return page.locator("#" + id).inner_text()

        def settled_reviews(n):
            page.wait_for_function(
                "n => document.getElementById('reviews').textContent === String(n)", arg=n
            )
            page.wait_for_timeout(400)

        check("empty accuracy is unavailable", text("accuracy") == "—")
        check(
            "native bridge receives OS motion preference",
            page.evaluate(
                "hudCommands.includes('hud:motion:full') && hudCommands.includes('hud:ready')"
            ),
        )
        for rating in [1, 2, 3, 4]:
            page.evaluate("rate", rating)
        settled_reviews(4)
        check("all ratings counted", text("reviews") == "4")
        check("accuracy", text("accuracy") == "75.0%")
        check("correct classification", text("correct") == "3" and text("again") == "1")
        check("passing streak counts Hard Good Easy", text("streak") == "3")
        check("exact Good run resets on Easy", text("good-streak") == "0")
        check("today's longest answer run", text("best-streak") == "3")
        check(
            "categorical answer timeline",
            page.locator("#answer-timeline [role=listitem]").count() == 4,
        )
        check(
            "real SVG accuracy graph rendered",
            bool(page.locator("#accuracy-line").get_attribute("d"))
            and not page.locator("#chart-empty").is_visible(),
        )
        check("delta visible", page.locator("#delta-reviews").inner_text() == "+1")
        page.locator("#hud").screenshot(path=output / "dark.png")
        # Retarget while the first tween is in flight; final values must converge.
        page.evaluate("() => { for(let i=0;i<20;i++) rate(3); }")
        check(
            "goal crossing celebrates",
            "active" in page.locator("#celebration").get_attribute("class"),
        )
        settled_reviews(24)
        check("rapid answers converge", text("correct") == "23")
        check(
            "long streak exceeds chart capacity correctly",
            text("streak") == "23" and text("best-streak") == "23" and text("good-streak") == "20",
        )
        check(
            "chart limited to 24 actual answers",
            page.locator("#answer-timeline [role=listitem]").count() == 24,
        )
        check(
            "progress capped", page.locator("#goal-meter").get_attribute("aria-valuenow") == "100"
        )
        page.evaluate("undo()")
        settled_reviews(23)
        check("undo converges", text("correct") == "22")
        check("undo restores last answer", "restored" in text("last-answer"))
        check(
            "undo restores streak and recent history",
            text("streak") == "22"
            and text("good-streak") == "19"
            and page.locator("#answer-timeline [role=listitem]").count() == 23,
        )
        page.evaluate("rate(1)")
        settled_reviews(24)
        check(
            "Again starts fresh streak without erasing record",
            text("streak") == "0" and text("best-streak") == "22" and text("good-streak") == "0",
        )
        page.evaluate("undo()")
        settled_reviews(23)
        check("undo Again restores the broken streak", text("streak") == "22")
        page.wait_for_timeout(1200)
        page.evaluate("render()")
        check(
            "refresh does not replay celebration",
            "active" not in page.locator("#celebration").get_attribute("class"),
        )
        page.evaluate("() => { cfg.theme='light'; render(); }")
        page.locator("#hud").screenshot(path=output / "light.png")
        page.evaluate("() => { cfg.show_streak=false; cfg.show_recent_chart=false; render(); }")
        check(
            "insight visibility controls",
            not page.locator("#streak-card").is_visible()
            and not page.locator("#recent-chart").is_visible(),
        )
        page.evaluate("() => { cfg.show_streak=true; cfg.show_recent_chart=true; render(); }")
        page.evaluate("() => { cfg.compact=true; render(); }")
        check("compact hides footer", not page.locator(".footnote").is_visible())
        page.locator("#hud").screenshot(path=output / "compact.png")
        page.evaluate("() => { cfg.animations=false; render(); rate(4); }")
        check("disabled animations update immediately", text("reviews") == "24")
        check("disabled animations clear deltas", not page.locator(".delta.shown").count())
        page.emulate_media(reduced_motion="reduce")
        page.wait_for_function("hudCommands.includes('hud:motion:reduce')")
        check(
            "OS motion changes reach native feedback",
            page.evaluate("hudCommands.includes('hud:motion:reduce')"),
        )
        page.evaluate("() => { cfg.animations=true; render(); rate(4); }")
        check("OS reduced motion updates immediately", text("reviews") == "25")
        check(
            "OS reduced motion disables animations",
            page.locator("html").get_attribute("data-motion") == "false",
        )
        page.evaluate("() => { cfg.show_distribution=false; render(); }")
        check("distribution visibility", not page.locator("#distribution").is_visible())
        page.evaluate(
            "() => { const s=stats(); s.day=2; s.reviews=0;s.correct=0;s.again=0;"
            "s.progress=0;s.accuracy=null;"
            "AnkiLiveHUD.update({stats:s,config:cfg,reason:'sync'}); }"
        )
        check(
            "day rollover resets without tween", text("reviews") == "0" and text("accuracy") == "—"
        )
        page.evaluate(
            "() => { cfg.compact=false; cfg.show_distribution=true; render();"
            "document.getElementById('hud').style.width='240px'; }"
        )
        check(
            "narrow layout has no horizontal overflow",
            page.evaluate(
                "() => {const e=document.getElementById('hud');"
                "return e.scrollWidth<=e.clientWidth;}"
            ),
        )
        page.locator("#hud").screenshot(path=output / "narrow.png")
        check("no JavaScript errors", not errors)
        check("no network requests", not requests)
        report = {
            "outcome": "passed",
            "checks": checks,
            "errors": errors,
            "browser": browser.version,
        }
        output.joinpath("report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
