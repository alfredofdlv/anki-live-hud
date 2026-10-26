# Changelog

## 0.2.0-rc.2 — 2026-10-26 (development preview)

- Add an animated answer-streak card: current Hard/Good/Easy run, best today and Good-only run.
- Add a categorical timeline of the last 24 rated answers and a rolling five-answer accuracy chart.
- Derive exact full-day streaks from rated review-log entries; no 24-answer cap on streak length.
- Restore streaks and graphs after undo/redo, deck changes and restart; respect Anki's study day.
- Add native streak medals at 5, 10, 20, 50 and 100 consecutive passing answers.
- Add independent display switches for the streak card and recent-answer chart.

## 0.2.0-rc.1 — 2026-10-26 (development preview)

- Add a prominent native feedback layer over the review area after each committed rating.
- Animated pop-in medal, +1 review, selected rating, progress ring and daily-goal bar.
- Gold milestone/goal variants derived from real review counts, without XP or rating bonuses.
- Keep one interruptible layer during rapid answers; never capture mouse clicks or keyboard focus.
- Add an impact feedback switch and adjustable 1.2–5 second duration (default 2.4 seconds).
- Preserve a stationary notification under Anki/OS reduced motion and disabled animations.
- Dismiss stale rewards on undo, profile changes and reviewer exit.
- Make native installation/evidence tooling choose the exact versioned package.

## 0.1.0-rc.1 — 2026-10-23

Initial release candidate.

- Persistent native reviewer sidebar with independent webview.
- Animated daily review events, correct answers, Again answers, answer accuracy,
  scheduler queue remaining and a configurable daily goal.
- Separate unique-card count and Again / Hard / Good / Easy distribution.
- Undo/redo synchronization from actual Anki review history.
- Light/dark/automatic theme, compact layout, collapse, hide and native resizing.
- Anki and OS reduced-motion support, plus an animation toggle.
- Background collection reads, stale-result rejection and profile lifecycle cleanup.
- Deterministic Anki add-on packaging, automated tests and release documentation.
