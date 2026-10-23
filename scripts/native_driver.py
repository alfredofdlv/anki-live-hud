"""Test-only, asynchronous Qt automation inside an isolated Anki process."""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path


def run() -> None:
    import aqt
    from aqt.qt import QApplication, QNetworkProxy, QPoint, Qt, QTimer, qVersion
    from aqt.theme import theme_manager
    from aqt.webview import AnkiWebPage
    from PyQt6.QtTest import QTest

    mw = aqt.mw
    # A test-process override: this host's proxy discovery stalls loopback WebEngine pages.
    # The product does not change proxy settings, and this never touches system settings.
    QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
    output = Path(os.environ["HUD_TEST_OUTPUT"])
    phase = os.environ["HUD_TEST_PHASE"]
    report = {
        "version": aqt.appVersion,
        "qt": qVersion(),
        "python": sys.version.split()[0],
        "phase": phase,
        "checks": [],
    }
    errors = []
    frames = []
    original_hook = sys.excepthook
    original_console = AnkiWebPage.javaScriptConsoleMessage

    def exception_hook(kind, value, tb):
        errors.append("".join(traceback.format_exception(kind, value, tb)))

    def console(page, level, message, line, source):
        if level == page.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            errors.append(f"JavaScript error at {line}: {message}")
        original_console(page, level, message, line, source)

    sys.excepthook = exception_hook
    AnkiWebPage.javaScriptConsoleMessage = console

    class Pause:
        def __init__(self, milliseconds):
            self.milliseconds = milliseconds

        def __await__(self):
            yield self.milliseconds

    async def wait(predicate, message, timeout=12):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            await Pause(10)
            if errors:
                raise AssertionError(errors[-1])
            if predicate():
                return
        raise AssertionError("Timed out: " + message)

    async def settle(seconds=0.5):
        await Pause(round(seconds * 1000))

    async def js(web, code):
        result = []
        web.evalWithCallback(code, result.append)
        await wait(lambda: bool(result), "JavaScript callback")
        return result[0]

    async def click(web, selector):
        position = await js(
            web,
            "(() => {const e=document.querySelector("
            + json.dumps(selector)
            + ");if(!e)return null;"
            "const r=e.getBoundingClientRect();"
            "return [r.x+r.width/2,r.y+r.height/2]})()",
        )
        assert position, f"Missing button: {selector}"
        factor = web.zoomFactor()
        QTest.mouseClick(
            web.focusProxy() or web,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            QPoint(round(position[0] * factor), round(position[1] * factor)),
        )

    def check(name, condition):
        assert condition, name
        report["checks"].append(name)

    async def capture(name):
        await settle()
        mw.grab().save(str(output / f"{name}.png"))

    async def scenario():
        hud = mw.anki_live_hud
        try:
            await wait(lambda: bool(mw.col), "profile open")
            check("isolated profile", Path(mw.pm.base).name.startswith("anki-live-hud-"))
            check("add-on loaded", hasattr(mw, "anki_live_hud"))
            mw.resize(1120, 850)
            mw.show()
            mw.activateWindow()
            QApplication.setActiveWindow(mw)
            if phase == "finish":
                mw.col.decks.set_current(mw.col.decks.id("Finish test"))
            mw.moveToState("review")
            await wait(lambda: hud.ready and hud.snapshot is not None, "populated HUD")
            await settle()
            identity = await js(hud.web, "window.__hudIdentity = Math.random()")
            check("persistent sidebar visible", hud.dock.isVisible())
            check(
                "collection values rendered",
                await js(hud.web, "document.getElementById('reviews').textContent")
                == str(hud.snapshot["reviews"]),
            )
            if phase == "restart":
                check("statistics survive restart", hud.snapshot["reviews"] == 7)
                check("settings survive restart", hud.config["daily_goal"] == 4)
                check("resized width survives restart", hud.config["width"] == 340)
            elif phase == "finish":
                mw.web.setFocus()
                QTest.keyClick(mw.web.focusProxy() or mw.web, Qt.Key.Key_Space)
                await wait(lambda: mw.reviewer.state == "answer", "final card reveal")
                QTest.keyClick(mw.web.focusProxy() or mw.web, Qt.Key.Key_4)
                await wait(lambda: mw.state == "overview", "natural end of study queue")
                check("exhausted queue hides dock safely", not hud.dock.isVisible())
                mw.col.decks.set_current(mw.col.decks.id("Everyday English"))
                mw.moveToState("review")
                await wait(lambda: hud.snapshot["reviews"] == 8, "final answer recovered")
                check("final rating retained across deck switch", hud.snapshot["easy"] == 2)
            else:
                hud.save_config({**hud.config, "daily_goal": 4, "theme": "dark"})
                theme_manager.set_night_mode(True)
                aqt.gui_hooks.theme_did_change()
                await capture("reviewer-initial-dark")
                check("empty accuracy is unavailable", hud.snapshot["accuracy"] is None)
                for count, rating in enumerate([1, 2, 3, 4], 1):
                    mw.web.setFocus()
                    QTest.keyClick(mw.web.focusProxy() or mw.web, Qt.Key.Key_Space)
                    await wait(lambda: mw.reviewer.state == "answer", "keyboard reveal")
                    await wait(lambda: mw.reviewer._states_mutated, "scheduling states")
                    QTest.keyClick(mw.web.focusProxy() or mw.web, getattr(Qt.Key, f"Key_{rating}"))
                    await wait(
                        lambda count=count: hud.snapshot["reviews"] == count,
                        f"keyboard rating {rating}",
                    )
                    check(f"keyboard rating {rating}", hud.snapshot["last_rating"] == rating)
                    check(
                        f"remaining matches Anki after rating {rating}",
                        hud.snapshot["remaining"] == sum(mw.col.sched.counts()),
                    )
                await settle()
                check(
                    "all rating counts",
                    [hud.snapshot[k] for k in ("again", "hard", "good", "easy")] == [1, 1, 1, 1],
                )
                check("accuracy 75 percent", hud.snapshot["accuracy"] == 75)
                check("goal reached", hud.snapshot["progress"] == 100)
                check(
                    "document persists across cards",
                    await js(hud.web, "window.__hudIdentity") == identity,
                )
                await capture("reviewer-answered-dark")
                for count in range(5, 9):
                    await wait(lambda: mw.reviewer.state == "question", "next card")
                    await click(mw.reviewer.bottom.web, "#ansbut")
                    await wait(lambda: mw.reviewer.state == "answer", "mouse reveal")
                    await wait(lambda: mw.reviewer._states_mutated, "scheduling states")
                    await settle(0.08)
                    await click(mw.reviewer.bottom.web, 'button[onclick*="ease3"]')
                    await wait(lambda count=count: hud.snapshot["reviews"] == count, "mouse rating")
                    if count == 5:
                        for _ in range(12):
                            frames.append(mw.grab().toImage())
                            await settle(0.045)
                check("rapid actual mouse ratings", hud.snapshot["reviews"] == 8)
                mw.undo()
                await wait(lambda: hud.snapshot["reviews"] == 7, "undo")
                check("undo accuracy restored", abs(hud.snapshot["accuracy"] - 600 / 7) < 0.001)
                await settle()
                check(
                    "undo rendered",
                    await js(hud.web, "document.getElementById('reviews').textContent") == "7",
                )
                hud.save_config({**hud.config, "compact": True})
                await capture("reviewer-compact-dark")
                # Use the HUD's own HTML controls, then verify reviewer keys still work.
                await click(hud.web, '[data-command="collapse"]')
                await wait(lambda: hud.effective_collapsed, "HUD collapse control")
                await capture("reviewer-collapsed")
                hud.expand()
                check(
                    "expand preserves document",
                    await js(hud.web, "window.__hudIdentity") == identity,
                )
                hud.save_config({**hud.config, "compact": False, "theme": "light"})
                theme_manager.set_night_mode(False)
                aqt.gui_hooks.theme_did_change()
                await capture("reviewer-light")
                hud.save_config({**hud.config, "theme": "auto"})
                theme_manager.set_night_mode(True)
                aqt.gui_hooks.theme_did_change()
                check(
                    "automatic dark theme",
                    await js(hud.web, "document.documentElement.dataset.theme") == "dark",
                )
                theme_manager.set_night_mode(False)
                aqt.gui_hooks.theme_did_change()
                check(
                    "automatic light theme",
                    await js(hud.web, "document.documentElement.dataset.theme") == "light",
                )
                hud.save_config({**hud.config, "animations": False})
                check(
                    "animation setting applied",
                    await js(hud.web, "document.documentElement.dataset.motion") == "false",
                )
                hud.save_config({**hud.config, "animations": True})
                mw.pm.set_reduce_motion(True)
                aqt.gui_hooks.body_classes_need_update()
                check(
                    "Anki reduced motion respected",
                    await js(hud.web, "document.documentElement.dataset.motion") == "false",
                )
                mw.pm.set_reduce_motion(False)
                hud.save_config({**hud.config, "enabled": False})
                check("disable hides dock", not hud.dock.isVisible())
                hud.save_config({**hud.config, "enabled": True})
                check("enable restores dock", hud.dock.isVisible())
                mw.resize(760, 850)
                await settle()
                check("small window auto collapse", hud.effective_collapsed)
                mw.resize(1120, 850)
                await settle()
                check("wide window restores panel", not hud.effective_collapsed)
                await click(hud.web, '[data-command="hide"]')
                await wait(lambda: not hud.dock.isVisible(), "hide control")
                check("hide preserves review", mw.state == "review")
                await capture("reviewer-without-hud")
                hud.toggle_visible(True)
                mw.moveToState("deckBrowser")
                check("session end hides panel", not hud.dock.isVisible())
                mw.moveToState("review")
                await wait(lambda: hud.dock.isVisible(), "resume review")
                check(
                    "resume preserves document",
                    await js(hud.web, "window.__hudIdentity") == identity,
                )
                from aqt.qt import QDialog, QSpinBox

                def accept_settings():
                    dialog = next(
                        widget
                        for widget in QApplication.topLevelWidgets()
                        if isinstance(widget, QDialog)
                        and widget.windowTitle() == "Anki Live HUD · Settings"
                    )
                    dialog.findChildren(QSpinBox)[0].setValue(5)
                    dialog.accept()

                QTimer.singleShot(200, accept_settings)
                await click(hud.web, '[data-command="settings"]')
                await wait(lambda: hud.config["daily_goal"] == 5, "settings dialog Save")
                check("native settings dialog applies edits", hud.config["daily_goal"] == 5)
                hud.save_config({**hud.config, "daily_goal": 4})
                mw.resizeDocks([hud.dock], [340], Qt.Orientation.Horizontal)
                await wait(lambda: hud.config["width"] == 340, "resize persistence")
                check("native divider width saved", hud.config["width"] == 340)
                # Exercise the actual Anki package installer on this isolated add-on.
                from aqt.addons import InstallOk

                package = next((Path(os.environ["HUD_TEST_ROOT"]) / "dist").glob("*.ankiaddon"))
                installed = mw.addonManager.install(str(package))
                check(
                    "package accepted by native installer",
                    isinstance(installed, InstallOk) and installed.compatible,
                )
                for index, frame in enumerate(frames):
                    frame.save(str(output / f"frame-{index:03}.png"))
            report["snapshot"] = hud.snapshot
            check("no Python or JavaScript errors", not errors)
            report["outcome"] = "passed"
        except BaseException:
            report["outcome"] = "failed"
            report["error"] = traceback.format_exc()
            report["diagnostics"] = {
                "state": mw.state,
                "ready": hud.ready,
                "snapshot": hud.snapshot,
                "inflight": hud.inflight,
            }
            mw.grab().save(str(output / "failure.png"))
        finally:
            sys.excepthook = original_hook
            AnkiWebPage.javaScriptConsoleMessage = original_console
            output.joinpath(f"{phase}.json").write_text(
                json.dumps(report, indent=2), encoding="utf-8"
            )
            print(json.dumps(report), flush=True)
            mw.close()
            QTimer.singleShot(
                1500,
                lambda: QApplication.instance().exit(0 if report["outcome"] == "passed" else 1),
            )

    iterator = scenario().__await__()

    def step():
        try:
            delay = next(iterator)
        except StopIteration:
            return
        QTimer.singleShot(delay, step)

    QTimer.singleShot(0, step)
