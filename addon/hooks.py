"""Native persistent dock and official-hook integration. No reviewer monkey patches."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from aqt import gui_hooks
from aqt.operations import QueryOp
from aqt.qt import (
    QAction,
    QDockWidget,
    QEvent,
    QLabel,
    QObject,
    QPushButton,
    Qt,
    QTimer,
    QVBoxLayout,
    QWidget,
)
from aqt.theme import theme_manager
from aqt.webview import AnkiWebView

from .settings import show_settings, validated
from .state import RevisionGate
from .statistics import collection_snapshot

log = logging.getLogger("anki_live_hud")
WEB = Path(__file__).parent / "web"


class HudController(QObject):
    def __init__(self, mw, module: str) -> None:
        super().__init__(mw)
        self.mw = mw
        self.module = module
        self.config = validated(mw.addonManager.getConfig(module))
        self.gate = RevisionGate()
        self.inflight = None
        self.dock = None
        self.web = None
        self.rail = None
        self.ready = False
        self.snapshot = None
        self.effective_collapsed = None
        self.pending_reason = "sync"
        self._layout_busy = False
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.timeout.connect(self._refresh)
        self.width_timer = QTimer(self)
        self.width_timer.setSingleShot(True)
        self.width_timer.timeout.connect(self._remember_width)
        self.poll = QTimer(self)
        self.poll.setInterval(30000)
        self.poll.timeout.connect(self.request_refresh)
        self._install_menu()
        mw.installEventFilter(self)
        gui_hooks.reviewer_did_answer_card.append(self.on_answer)
        gui_hooks.reviewer_did_show_question.append(self.on_card)
        gui_hooks.reviewer_did_show_answer.append(self.on_card)
        gui_hooks.reviewer_will_end.append(self.on_end)
        gui_hooks.state_did_change.append(self.on_state)
        gui_hooks.operation_did_execute.append(self.on_operation)
        gui_hooks.theme_did_change.append(self.on_theme)
        gui_hooks.body_classes_need_update.append(self.on_theme)
        gui_hooks.profile_did_open.append(self.on_profile)
        gui_hooks.profile_will_close.append(self.on_close)
        gui_hooks.collection_will_temporarily_close.append(self.on_collection_close)
        mw.addonManager.setConfigUpdatedAction(module, self.on_config_updated)

    def _install_menu(self) -> None:
        menu = self.mw.form.menuTools.addMenu("Anki Live HUD")
        self.visible_action = QAction("Show during reviews", self.mw)
        self.visible_action.setCheckable(True)
        self.visible_action.setChecked(self.config["visible"])
        self.visible_action.triggered.connect(self.toggle_visible)
        menu.addAction(self.visible_action)
        collapse = QAction("Collapse / expand", self.mw)
        collapse.triggered.connect(self.toggle_collapsed)
        menu.addAction(collapse)
        settings = QAction("Settings…", self.mw)
        settings.triggered.connect(lambda: show_settings(self))
        menu.addAction(settings)

    def active(self) -> bool:
        return bool(
            self.mw.col
            and self.mw.state == "review"
            and self.config["enabled"]
            and self.config["visible"]
        )

    def on_profile(self) -> None:
        self.config = validated(self.mw.addonManager.getConfig(self.module))
        self.visible_action.setChecked(self.config["visible"])

    def _create_dock(self) -> None:
        if self.dock:
            return
        dock = QDockWidget("Anki Live HUD", self.mw)
        dock.setObjectName("anki_live_hud_dock")
        dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setTitleBarWidget(QWidget(dock))
        self.web = AnkiWebView(dock, title="Anki Live HUD")
        self.web.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.web.set_bridge_command(self.on_bridge, self)
        self.rail = QWidget(dock)
        rail_layout = QVBoxLayout(self.rail)
        rail_layout.setContentsMargins(4, 12, 4, 12)
        expand = QPushButton("‹", self.rail)
        expand.setAccessibleName("Expand Anki Live HUD")
        expand.setToolTip("Expand Anki Live HUD (widens the window if needed)")
        expand.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        expand.clicked.connect(self.expand)
        rail_layout.addWidget(expand)
        label = QLabel("H\nU\nD", self.rail)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rail_layout.addWidget(label)
        rail_layout.addStretch()
        # Both widgets stay alive: collapse never recreates the Chromium document.
        container = QWidget(dock)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.web)
        layout.addWidget(self.rail)
        dock.setWidget(container)
        self.dock = dock
        dock.installEventFilter(self)
        self.mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        self.web.stdHtml(
            (WEB / "hud.html").read_text(encoding="utf-8")
            + "<script>"
            + (WEB / "hud.js").read_text(encoding="utf-8")
            + "</script>",
            head="<style>" + (WEB / "hud.css").read_text(encoding="utf-8") + "</style>",
            css=[],
            js=[],
            context=self,
            default_css=False,
        )
        # Anki queues eval until its asynchronous QWebChannel bridge reports domDone.
        self.web.eval("window.AnkiLiveHUD.connect()")
        self._layout(force=True)

    def on_bridge(self, command: str):
        if command == "hud:ready":
            self.ready = True
            self._push()
        elif command == "hud:collapse":
            self.toggle_collapsed()
        elif command == "hud:hide":
            self.toggle_visible(False)
        elif command == "hud:settings":
            show_settings(self)
        if self.mw.state == "review":
            self.mw.web.setFocus()
        return None

    def on_state(self, new_state: str, old_state: str) -> None:
        if new_state == "review":
            self._update_visibility()
            self.request_refresh("sync")
        else:
            self.on_end()

    def on_card(self, card) -> None:
        self._update_visibility()
        self.request_refresh()

    def on_answer(self, reviewer, card, ease: int) -> None:
        self.request_refresh("answer")

    def on_operation(self, changes, handler) -> None:
        # Includes undo/redo, bury, suspend, deck changes and database edits.
        self.request_refresh()

    def on_theme(self) -> None:
        self._push()

    def on_end(self) -> None:
        self.poll.stop()
        self.refresh_timer.stop()
        if self.dock:
            self.dock.hide()

    def on_collection_close(self, col) -> None:
        self.on_end()
        self.gate.invalidate()
        self.inflight = None
        self.snapshot = None

    def on_close(self) -> None:
        self.on_collection_close(None)
        self.width_timer.stop()
        self.ready = False
        if self.web:
            self.web.cleanup()
        if self.dock:
            self.mw.removeDockWidget(self.dock)
            self.dock.deleteLater()
        self.dock = self.web = self.rail = None
        self.effective_collapsed = None

    def _update_visibility(self) -> None:
        if self.active():
            self._create_dock()
            self._layout()
            self.dock.show()
            self.poll.start()
        else:
            self.on_end()

    def request_refresh(self, reason: str = "sync") -> None:
        if not self.active():
            return
        self.gate.request()
        if reason == "answer":
            self.pending_reason = reason
        self.refresh_timer.start(0)

    def _refresh(self) -> None:
        if not self.active() or self.inflight is not None:
            return
        token = self.gate.token
        reason = self.pending_reason
        self.pending_reason = "sync"
        goal = self.config["daily_goal"]
        self.inflight = token

        def done(snapshot):
            if self.inflight != token:
                return
            self.inflight = None
            if not self.gate.accepts(token):
                if reason == "answer":
                    self.pending_reason = reason
                self.refresh_timer.start(0)
                return
            self.snapshot = snapshot
            self._push(reason)

        def failed(error):
            if self.inflight != token:
                return
            self.inflight = None
            log.warning("HUD refresh failed: %s", error)
            if self.web and self.ready:
                self.web.eval("window.AnkiLiveHUD.setStatus('Statistics temporarily unavailable')")
            # No modal errors and no retry loop; next event or poll retries.

        QueryOp(
            parent=self.mw, op=lambda col: collection_snapshot(col, goal), success=done
        ).failure(failed).run_in_background()

    def _push(self, reason: str = "sync") -> None:
        if not self.web or not self.ready:
            return
        theme = self.config["theme"]
        if theme == "auto":
            theme = "dark" if theme_manager.night_mode else "light"
        payload = {
            "stats": self.snapshot,
            "reason": reason,
            "config": {
                **self.config,
                "theme": theme,
                "animations": self.config["animations"] and not self.mw.pm.reduce_motion(),
            },
        }
        self.web.eval("window.AnkiLiveHUD.update(" + json.dumps(payload) + ")")

    def save_config(self, raw: dict) -> None:
        self.config = validated(raw)
        self.mw.addonManager.writeConfig(self.module, self.config)
        self.visible_action.setChecked(self.config["visible"])
        self._update_visibility()
        self._layout(force=True)
        self._push()
        self.request_refresh()

    def on_config_updated(self, raw: dict) -> None:
        self.save_config(raw)

    def toggle_visible(self, checked: bool) -> None:
        self.save_config({**self.config, "visible": checked})

    def toggle_collapsed(self) -> None:
        self.save_config({**self.config, "collapsed": not self.config["collapsed"]})
        if self.mw.state == "review":
            self.mw.web.setFocus()

    def expand(self) -> None:
        if self.mw.width() < 820:
            self.mw.resize(900, self.mw.height())
        self.save_config({**self.config, "collapsed": False})
        self.mw.web.setFocus()

    def _layout(self, force: bool = False) -> None:
        if not self.dock or self._layout_busy:
            return
        self._layout_busy = True
        try:
            collapsed = self.config["collapsed"] or self.mw.width() < 820
            changed = collapsed != self.effective_collapsed
            self.effective_collapsed = collapsed
            self.web.setVisible(not collapsed)
            self.rail.setVisible(collapsed)
            self.dock.setMinimumSize(42 if collapsed else 240, 0)
            self.dock.setMaximumWidth(42 if collapsed else 480)
            if changed or force:
                width = 42 if collapsed else min(self.config["width"], self.mw.width() - 500)
                self.mw.resizeDocks([self.dock], [width], Qt.Orientation.Horizontal)
        finally:
            self._layout_busy = False

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.Resize:
            if watched is self.mw:
                self._layout()
            elif watched is self.dock and not self._layout_busy:
                self.width_timer.start(500)
        return False

    def _remember_width(self) -> None:
        if self.dock and self.dock.isVisible() and not self.effective_collapsed:
            width = max(240, min(480, self.dock.width()))
            if width != self.config["width"]:
                self.config["width"] = width
                self.mw.addonManager.writeConfig(self.module, self.config)
