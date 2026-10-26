"""Anki Live HUD. No collection or scheduler mutations at runtime."""

import sys

__version__ = "0.2.0-rc.1"


def _bootstrap() -> None:
    from aqt import mw

    from .hooks import HudController

    if mw is not None and not hasattr(mw, "anki_live_hud"):
        mw.anki_live_hud = HudController(mw, __name__)


# Keep the aggregation modules importable without Qt/Anki for unit tests.
if "aqt" in sys.modules:
    _bootstrap()
