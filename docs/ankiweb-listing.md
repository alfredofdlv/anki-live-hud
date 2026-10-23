# AnkiWeb listing draft — approval required before publication

## Title

Anki Live HUD — Animated Review Statistics

## Short description

See your study progress move with every answer. A quiet, persistent sidebar with
animated counters, answer accuracy, queue remaining and a daily goal.

## Description

Anki Live HUD brings immediate visual feedback to the native desktop reviewer.
Your flashcards and answer buttons continue to work normally while a compact
sidebar shows progress drawn from your real Anki collection.

Features:

- Smooth counters and change indicators after Again, Hard, Good and Easy.
- Daily review events, unique cards, correct answers and Again answers.
- Answer accuracy: Hard + Good + Easy divided by all rated answers today.
- Remaining queue counts from Anki's scheduler, including learning behavior.
- Configurable daily goal with an animated bar and subtle completion feedback.
- Again / Hard / Good / Easy distribution.
- Light/dark/automatic theme and a compact layout.
- Collapse, hide, disable and drag to resize.
- Undo/redo restoration from the actual review log.
- Anki study-day rollover and reduced-motion preferences.
- Offline operation, no telemetry and no external services.

Daily totals cover the whole collection; remaining covers the selected study
deck. Every answer is a review event, even if the same card appears again.
The accuracy metric is **not True Retention**.

## Installation and settings

After this add-on is approved on AnkiWeb, use its assigned code in Tools → Add-ons
→ Get Add-ons. Before approval, use the `.ankiaddon` file from GitHub Releases:
Tools → Add-ons → Install from file, select the file, then restart Anki.

Open a deck and begin reviewing. Change preferences under Tools → Anki Live HUD
→ Settings. Restore a hidden panel using Show during reviews in that menu.

## Compatibility

Anki Desktop 26.09.3 or newer, Qt 6. Initial release candidate; see the repository
test report for executed platform checks. AnkiMobile and AnkiDroid cannot run
desktop add-ons. Older Anki releases are not supported.

The add-on uses official GUI hooks and a separate Qt dock. It does not modify
card HTML, scheduling or synchronization. Full-screen UI replacements and other
right-side docks need combination testing. FSRS-specific metrics are not included.

## Source, support and screenshots

Source: https://github.com/alfredofdlv/anki-live-hud

First prerelease: https://github.com/alfredofdlv/anki-live-hud/releases/tag/v0.1.0-rc.1

Attach the verified native reviewer screenshots from `docs/images/` and the
animation GIF when available. Use the repository Issues tab for bug reports.
Free, MIT licensed. The project was largely developed with AI assistance; source
and testing evidence are public. The add-on itself does not use an AI service.
No AnkiWeb ID has been assigned and this draft has not been submitted.
