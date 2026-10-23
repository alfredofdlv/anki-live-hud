# Contributing

Use Python 3.10+ for unit tests and Python 3.12 for the documented GUI test runtime.
The shipped add-on has no third-party runtime dependencies beyond Anki itself.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install pytest ruff tzdata
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\ruff check addon tests scripts
.\.venv\Scripts\ruff format --check addon tests scripts
.\.venv\Scripts\python scripts\build.py
```

For real scheduler and GUI tests, install `aqt[qt]==26.9.3`, Pillow and Playwright
inside the development environment. See [testing](docs/testing.md). Never use a
personal collection for automated tests. The native harness creates a fresh
temporary base directory and a unique Anki single-instance key on every run.

Keep modules focused: `statistics.py` is read-only aggregation, `state.py` gates
asynchronous snapshots, `hooks.py` owns lifecycle/UI integration, `settings.py`
validates preferences, and `web/` owns presentation. Avoid scheduler wrappers,
card-template injection, external requests and frontend dependencies.

Changes to metrics need unit tests against the actual definitions. Changes to
answer/undo handling need a temporary-collection integration test. UI changes
should include light/dark and reduced-motion checks. Record executed tests in PRs;
identify any platform or add-on combination you could not test.

Report bugs with Anki version, OS, HUD settings and reproduction steps using a
small sample deck. Omit card contents, profile paths and other personal data.
Contributions are licensed under MIT. Anki and Qt retain their own licenses.
