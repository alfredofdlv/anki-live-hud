"""Validated add-on settings and a small native settings dialog."""

from __future__ import annotations

DEFAULTS = {
    "enabled": True,
    "visible": True,
    "collapsed": False,
    "width": 304,
    "daily_goal": 100,
    "animations": True,
    "compact": False,
    "theme": "auto",
    "show_distribution": True,
    "answer_feedback": True,
    "feedback_duration": 2400,
    "show_streak": True,
    "show_recent_chart": True,
}


def validated(raw: dict | None) -> dict:
    result = dict(DEFAULTS)
    if not isinstance(raw, dict):
        return result
    for key, default in DEFAULTS.items():
        value = raw.get(key, default)
        if isinstance(default, bool):
            result[key] = value if isinstance(value, bool) else default
        elif isinstance(default, int):
            if isinstance(value, int) and not isinstance(value, bool):
                low, high = {
                    "width": (240, 480),
                    "daily_goal": (1, 100000),
                    "feedback_duration": (1200, 5000),
                }[key]
                result[key] = max(low, min(high, value))
        elif key == "theme" and value in ("auto", "light", "dark"):
            result[key] = value
    return result


def show_settings(controller) -> None:
    from aqt.qt import (
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QLabel,
        QSpinBox,
        QVBoxLayout,
    )

    dialog = QDialog(controller.mw)
    dialog.setWindowTitle("Anki Live HUD · Settings")
    dialog.setMinimumWidth(400)
    layout = QVBoxLayout(dialog)
    explanation = QLabel(
        "Daily statistics cover the whole collection.\n"
        "Queue remaining follows the selected study deck.\n\n"
        "Impact feedback appears over the review area after each answer. "
        "Anki/OS reduced motion keeps the notification visible without movement."
    )
    explanation.setWordWrap(True)
    layout.addWidget(explanation)
    form = QFormLayout()
    layout.addLayout(form)
    controls = {}
    for key, label in (
        ("enabled", "Enable Anki Live HUD"),
        ("visible", "Show during reviews"),
        ("animations", "Animate changes"),
        ("compact", "Compact layout"),
        ("show_distribution", "Show answer distribution"),
        ("answer_feedback", "Show impact feedback over the review area"),
        ("show_streak", "Show answer streak and today's best"),
        ("show_recent_chart", "Show recent-answer chart"),
    ):
        box = QCheckBox(label)
        box.setChecked(controller.config[key])
        form.addRow(box)
        controls[key] = box
    for key, label, low, high in (
        ("daily_goal", "Daily goal (answer events)", 1, 100000),
        ("width", "Sidebar width (pixels)", 240, 480),
        ("feedback_duration", "Impact feedback duration (milliseconds)", 1200, 5000),
    ):
        spin = QSpinBox()
        spin.setRange(low, high)
        spin.setValue(controller.config[key])
        form.addRow(label, spin)
        controls[key] = spin
    theme = QComboBox()
    theme.addItems(["auto", "light", "dark"])
    theme.setCurrentText(controller.config["theme"])
    form.addRow("Theme", theme)
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
    )
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        updated = dict(controller.config)
        for key, control in controls.items():
            updated[key] = (
                control.isChecked() if isinstance(control, QCheckBox) else control.value()
            )
        updated["theme"] = theme.currentText()
        controller.save_config(updated)
