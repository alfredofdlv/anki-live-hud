# v0.1.0-rc.1 release preparation

Status: **public GitHub repository created with owner authorization**.
The prerelease is distributed through GitHub Releases; AnkiWeb submission is pending.

- [Repository](https://github.com/alfredofdlv/anki-live-hud)
- [Release page](https://github.com/alfredofdlv/anki-live-hud/releases/tag/v0.1.0-rc.1)
- [CI](https://github.com/alfredofdlv/anki-live-hud/actions)
- [Spanish publication guide](publicar.md) · [Announcement drafts](anuncios.md)

## Prepared

- Original MIT-licensed source, README, changelog, contributing guide and bug template.
- Actual Anki integration, automated tests, native screenshots and animation GIF.
- Clean deterministic `.ankiaddon` archive and SHA-256 sidecar in `dist/`.
- Minimum Anki version enforced through `min_point_version: 260903`.
- GitHub Actions for lint, tests, Chromium validation and package building.
- [Windows installation guide](install-windows.md) and [AnkiWeb draft](ankiweb-listing.md).

The Python project uses normalized PEP 440 version `0.1.0rc1`; the human-facing
release and package version are SemVer `0.1.0-rc.1`.

## Release procedure

1. Review the source, screenshots, test evidence and documented limitations.
2. The owner requested public GitHub publication on 23 October 2026. That request
   authorizes this initial repository and prerelease; it does not send community posts.
3. Push the reviewed source and documentation to `alfredofdlv/anki-live-hud` on `main`.
4. Wait for the remote Actions checks. Tag the tested commit `v0.1.0-rc.1`.
5. Publish a prerelease with the `.ankiaddon` archive and its `.sha256` file.
   Use CHANGELOG.md as the release description and link the test report.
6. Confirm the source URL in the AnkiWeb draft and add screenshots from `docs/images/`.
7. Obtain separate explicit approval before submitting the add-on to AnkiWeb.
8. After AnkiWeb assigns a numeric ID, update the README/listing with the actual code.
   Plan migration/conflict metadata for users switching from the GitHub package
   folder `anki_live_hud` to an AnkiWeb numeric folder, avoiding duplicate installs.

No AnkiWeb number or signature is invented. The GitHub connector did not expose
repository/release creation, so publication uses GitHub's official API and the
account's existing Git Credential Manager authorization. Credentials are never
included in source or release archives. Git commits use the account's GitHub
no-reply address rather than the locally configured private contact address.

## Rebuild

```powershell
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\ruff check addon tests scripts
.\.venv\Scripts\ruff format --check addon tests scripts
.\.venv\Scripts\python scripts\build.py
```

The builder has an explicit runtime allowlist. The archive includes no development
environment, tests, logs, screenshots, profiles, compiled Python, caches or downloads.
Archive contents start directly with `__init__.py`, not a parent directory.
