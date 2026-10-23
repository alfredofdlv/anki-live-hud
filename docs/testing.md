# Testing and verification

Executed on Windows on **23 October 2026**. These are observed results, not a
claim that every OS, Anki version or add-on combination is supported.

## Executed suites

- **28 pytest tests passed**, including statistics aggregation, rating
  classification, goal progress, empty/malformed settings, repeated answers,
  half-open date boundaries, DST rollover, undo/redo, revision gating, archive
  reproducibility and actual Anki collections.
- **21 Chromium frontend checks passed**, including rapid retargeting, undo,
  empty accuracy, progress caps, compact layout, light/dark captures, disabled
  animation, OS reduced motion, rollover, narrow layout, no JavaScript errors
  and no network requests. Browser: Chromium 143.0.7499.4.
- **Native installed Anki 26.09.3 tested**, with Python 3.13.15 and Qt 6.11.2.
  Three separate application launches cover reviews, restart and natural queue
  completion. The package was also accepted as compatible by Anki's own add-on installer.
- The same Anki release was exercised in a development runtime with Python 3.12
  and Qt 6.8.1 during investigation.
- Ruff lint/format checks and deterministic package build executed successfully.

Machine-readable successful reports are in [evidence/](evidence/). They contain
only disposable test-deck statistics. Logs with environment-specific paths remain
in the ignored `test-results/` folder. Remote GitHub Actions results are available
on the [Actions page](https://github.com/alfredofdlv/anki-live-hud/actions); check
the workflow associated with the release commit rather than assuming local tests
guarantee a successful remote run.

## Native test coverage

The native harness installs the built archive into a new temporary base directory,
creates a `HUD Test` profile, adds small Basic decks and launches Anki with `-b`
and a unique `ANKI_SINGLE_INSTANCE_KEY`. It never opens, copies or changes the
primary profile. The installed application is tested without installing packages
into its bundled Python environment.

The harness sends actual Qt key and mouse events to the reviewer and HUD. It checks:

- Sidebar appearance and actual collection values in its DOM.
- Space to reveal and Again/Hard/Good/Easy via number keys.
- Native button clicks and rapid successive answers.
- Scheduler remaining counts, including a learning queue that does not simply decrement.
- Counter/accuracy/goal updates and document identity across card changes.
- Anki undo and restored frontend totals.
- HUD collapse/expand/hide buttons, settings dialog and enable/disable controls.
- Width changes using Qt's native dock divider geometry and persistence after restart.
- Automatic collapse in a narrow window and restoration when widened.
- Anki's reduced-motion preference and the HUD's animation switch.
- Session exit/reentry, actual queue exhaustion, switching decks and recovering the last answer.
- Normal restart with retained settings and collection statistics.
- Anki's package installer accepts the release candidate and reports compatible.
- No Python exceptions or JavaScript error-console messages during the scenario.

Native screenshots and the GIF in [images/](images/) show the real Anki reviewer,
not a reconstruction. The GIF records a real answered-card transition on the test deck.

### Test host networking detail

Initial launches produced blank views in Anki's own reviewer/toolbar as well as the
HUD. The local page server returned valid HTML; Chromium page loads stalled.
Disabling proxy discovery **inside the test process only** allowed the views to
load and the tests to pass on both Qt runtimes. This override is isolated to
`native_driver.py`; it is not shipped in the add-on and does not alter system or
primary Anki settings. This is evidence of the workaround, not a general diagnosis
of every blank-screen problem.

## Run unit and real-collection tests

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install pytest ruff tzdata
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\ruff check addon tests scripts
.\.venv\Scripts\ruff format --check addon tests scripts
.\.venv\Scripts\python scripts\build.py
```

Without Anki installed in that virtual environment, the real-collection test module
is explicitly skipped. Enable it with:

```powershell
.\.venv\Scripts\python -m pip install "aqt[qt]==26.9.3"
.\.venv\Scripts\python -m pytest -q
```

## Run native reviewer tests

Install development dependencies in the virtual environment, then use the installed
Anki executable or the development runtime. The harness creates a fresh base on
every invocation. Its test windows may appear briefly; its events target that
application, and a different single-instance key prevents dispatch to your normal Anki.

```powershell
.\.venv\Scripts\python -m pip install pillow
.\.venv\Scripts\python scripts\test_native.py --installed-exe "$env:LOCALAPPDATA\Programs\Anki\Anki.exe"
# Alternatively, use the development Anki runtime:
.\.venv\Scripts\python scripts\test_native.py
```

Temporary bases are retained for inspection and printed at the end. Reports,
screenshots and frames are written to `test-results/native/`. That directory and
the temporary profile must never be distributed in the add-on archive.

## Run browser animation tests or preview

```powershell
.\.venv\Scripts\python -m pip install playwright
.\.venv\Scripts\python -m playwright install chromium
.\.venv\Scripts\python scripts\test_ui.py
.\.venv\Scripts\python scripts\preview.py
```

If using an existing Chromium binary, set `HUD_CHROMIUM` to its executable path.
The preview generator creates `test-results/preview.html`, a self-contained UI
fixture that can be opened directly. Its answer data is explicitly synthetic.
Production markup, styles and JavaScript are embedded from `addon/web/` to avoid
maintaining a separate mock frontend.

After a successful native and browser run, `python scripts/prepare_evidence.py`
copies only passing reports and the sample-deck images into `docs/`.

## Still unverified

- Native Linux/macOS UI and Anki versions other than 26.09.3.
- Compatibility combinations with AnkiConnect, progress bars, heatmaps, full-screen
  reviewer replacements and other popular third-party add-ons.
- Real-device changes of OS timezone/DST while Anki remains open; boundary arithmetic
  is tested automatically, including 23-hour and 25-hour study days.
- Synchronization against a live AnkiWeb account; no credentials are used by tests.
  Collection operations and temporary-close lifecycle hooks are handled in code.
- AnkiWeb's publication review and a numeric AnkiWeb installation code.

P2 FSRS analytics, heatmaps, achievements and exports are intentionally absent.
