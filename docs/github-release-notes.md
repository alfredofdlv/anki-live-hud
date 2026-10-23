First public prerelease of **Anki Live HUD**, a free, MIT-licensed statistics
sidebar for the native Anki Desktop reviewer.

## Install

1. Use **Anki Desktop 26.09.3 or newer**.
2. Download **`anki-live-hud-0.1.0-rc.1.ankiaddon`** from the assets below.
3. Open **Tools → Add-ons → Install from file…**, select it, then restart Anki.
4. Start reviewing. Configure the panel under **Tools → Anki Live HUD → Settings…**.

The source ZIP is for development; install the `.ankiaddon` file.
No AnkiWeb installation code has been assigned yet.

## Included

- A persistent, resizable native sidebar alongside your cards.
- Animated answer events, correct/Again counts, answer accuracy and queue remaining.
- Daily goal, answer distribution and a separate unique-card count.
- Undo restoration, light/dark/automatic themes, compact mode, collapse and hide.
- Offline operation and Anki/OS reduced-motion support.

Daily totals cover the whole collection. Remaining follows the selected study
deck. “Accuracy” is Hard + Good + Easy divided by all rated answers, including
learning; **it is not True Retention**. Card templates and scheduling are unchanged.

## Validation and limits

28 Python tests and 21 browser checks passed. Real installed Anki 26.09.3 was
tested on Windows with a temporary profile, covering keyboard/mouse answers,
undo, settings, resizing, restart and natural queue completion. Anki's own
installer accepts the package. See the [test report](https://github.com/alfredofdlv/anki-live-hud/blob/main/docs/testing.md).

**This is a prerelease.** Native macOS/Linux behavior, future Anki versions and
combinations with popular third-party add-ons remain unverified. AnkiMobile and
AnkiDroid are unsupported. There is no claim of better retention or exam performance.

The project was largely developed with AI assistance. Source and test evidence
are public; the add-on itself has no AI-service dependency, account or telemetry.

Report reproducible bugs in [Issues](https://github.com/alfredofdlv/anki-live-hud/issues)
with your OS, exact Anki version and other reviewer add-ons. Omit private cards and logs.

[Windows installation guide](https://github.com/alfredofdlv/anki-live-hud/blob/main/docs/install-windows.md)
· [Guía en español](https://github.com/alfredofdlv/anki-live-hud/blob/main/docs/publicar.md)
· [Animation demo](https://github.com/alfredofdlv/anki-live-hud/blob/main/docs/images/native-review.gif)
