"""A mouse-transparent native reward layer above the review webview.

The card DOM is untouched. One small painted widget is reused for successive
answers; its single animation and expiry timer are restarted, never queued.
"""

from __future__ import annotations

import math

from aqt.qt import (
    QColor,
    QEvent,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
    QPointF,
    QPolygonF,
    QRectF,
    Qt,
    QTimer,
    QVariantAnimation,
    QWidget,
)

from ..feedback import feedback_details, impact_frame
from ..statistics import RATING_NAMES


class AnswerFeedback(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("anki_live_hud_answer_feedback")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setAccessibleName("Anki Live HUD answer feedback")
        self.duration = 2400
        self.animated = True
        self.dark = True
        self.elapsed = 0.0
        self.rating = 3
        self.details = None
        self.animation = QVariantAnimation(self)
        self.animation.setStartValue(0.0)
        self.animation.valueChanged.connect(self._advance)
        self.expiry = QTimer(self)
        self.expiry.setSingleShot(True)
        self.expiry.timeout.connect(self.dismiss)
        parent.installEventFilter(self)
        self.hide()

    def configure(self, *, animated: bool, dark: bool, duration: int) -> None:
        self.dark = dark
        self.duration = duration
        if not animated and self.animated:
            self.animation.stop()
            self.elapsed = 600.0
        self.animated = animated
        self.update()

    def show_answer(self, rating: int) -> None:
        if rating not in RATING_NAMES:
            return
        self.animation.stop()
        self.rating = rating
        self.details = None
        self.elapsed = 0.0 if self.animated else 600.0
        self.setAccessibleDescription(f"{RATING_NAMES[rating]}. One review recorded.")
        self._place()
        self.show()
        self.raise_()
        self.expiry.start(self.duration)
        if self.animated:
            self.animation.setDuration(self.duration)
            self.animation.setEndValue(float(self.duration))
            self.animation.start()
        self.update()

    def confirm(self, snapshot: dict, previous: dict | None) -> None:
        if not self.isVisible():
            return
        self.details = feedback_details(snapshot, previous)
        self.setAccessibleDescription(
            f"{RATING_NAMES[self.rating]}. One review recorded. {self.details['summary']}."
        )
        self.update()

    def dismiss(self) -> None:
        self.expiry.stop()
        self.animation.stop()
        self.hide()
        self.details = None

    def _advance(self, value) -> None:
        self.elapsed = float(value)
        self.update()

    def _place(self) -> None:
        parent = self.parentWidget()
        width = min(470, max(200, parent.width() - 16))
        height = min(210, parent.height())
        self.setGeometry(
            (parent.width() - width) // 2, max(0, parent.height() - height - 32), width, height
        )

    def eventFilter(self, watched, event) -> bool:
        if watched is self.parentWidget() and event.type() == QEvent.Type.Resize:
            self._place()
        return False

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        opacity, scale = impact_frame(self.elapsed, self.duration, self.animated)
        painter.setOpacity(opacity)
        # The fixed design scales down uniformly in narrow review panes.
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(
            min(self.width() / 470, self.height() / 210) * scale,
            min(self.width() / 470, self.height() / 210) * scale,
        )
        painter.translate(-235, -105)
        special = bool(self.details and self.details["special"])
        accent = QColor("#ffd579" if special else "#89f4d0")
        ink = QColor("#f5f6ff" if self.dark else "#172c3b")
        muted = QColor("#abb8ce" if self.dark else "#516775")
        if not self.dark:
            accent = QColor("#a36b13" if special else "#16846c")

        # Short radial rays and a ring accentuate the entry; no full-screen flashes.
        if self.animated and self.elapsed < 750:
            burst = min(1.0, self.elapsed / 650)
            for index in range(12):
                angle = math.tau * index / 12
                inner, outer = 52 + burst * 18, 58 + burst * 30
                ray = QColor(accent)
                ray.setAlphaF(max(0.0, (1 - burst) * 0.65))
                painter.setPen(QPen(ray, 2))
                painter.drawLine(
                    QPointF(94 + math.cos(angle) * inner, 105 + math.sin(angle) * inner),
                    QPointF(94 + math.cos(angle) * outer, 105 + math.sin(angle) * outer),
                )

        panel = QRectF(20, 36, 430, 138)
        gradient = QLinearGradient(panel.topLeft(), panel.bottomRight())
        gradient.setColorAt(0, QColor("#252d49" if self.dark else "#effbf7"))
        gradient.setColorAt(1, QColor("#141b2a" if self.dark else "#f5f5ff"))
        painter.setBrush(gradient)
        border = QColor(accent)
        border.setAlpha(125)
        painter.setPen(QPen(border, 1.2))
        painter.drawRoundedRect(panel, 22, 22)

        # Original geometric medal, with a ribbon and an animated perimeter.
        ribbon = QPolygonF(
            [
                QPointF(73, 130),
                QPointF(69, 160),
                QPointF(94, 149),
                QPointF(119, 160),
                QPointF(115, 130),
            ]
        )
        ribbon_color = QColor(accent)
        ribbon_color.setAlpha(65)
        painter.setBrush(ribbon_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(ribbon)
        painter.setBrush(QColor("#18243a" if self.dark else "#e1f2eb"))
        painter.setPen(QPen(accent, 2))
        painter.drawEllipse(QRectF(53, 64, 82, 82))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        perimeter = min(1.0, self.elapsed / 550) if self.animated else 1.0
        painter.setPen(QPen(accent, 3.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(QRectF(47, 58, 94, 94), 90 * 16, -round(perimeter * 360 * 16))
        painter.setPen(accent)
        font = QFont("Segoe UI", 25, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(53, 76, 82, 50), Qt.AlignmentFlag.AlignCenter, "+1")

        font = QFont("Segoe UI", 8, QFont.Weight.DemiBold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.2)
        painter.setFont(font)
        painter.setPen(accent)
        headline = self.details["headline"] if self.details else "REVIEW RECORDED"
        painter.drawText(QRectF(161, 51, 277, 19), Qt.AlignmentFlag.AlignLeft, headline)
        painter.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        painter.setPen(ink)
        painter.drawText(
            QRectF(159, 72, 275, 43), Qt.AlignmentFlag.AlignLeft, RATING_NAMES[self.rating].upper()
        )
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(muted)
        summary = self.details["summary"] if self.details else "+1 review · keep moving"
        painter.drawText(QRectF(161, 119, 270, 21), Qt.AlignmentFlag.AlignLeft, summary)
        if self.details:
            track = QRectF(161, 151, 260, 5)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#3a4560" if self.dark else "#d8e4e2"))
            painter.drawRoundedRect(track, 2.5, 2.5)
            t = min(1.0, self.elapsed / 500) if self.animated else 1.0
            progress = self.details["progress_from"] + (
                self.details["progress"] - self.details["progress_from"]
            ) * (1 - (1 - t) ** 3)
            painter.setBrush(accent)
            painter.drawRoundedRect(
                QRectF(track.x(), track.y(), track.width() * progress / 100, track.height()),
                2.5,
                2.5,
            )
        painter.end()
