"""Dev-mode environment detection for bootstack hot reload.

PROVISIONAL — the `bootstack.dev` surface ships in 0.1.0 but is carved out of
the API freeze: it may change in a minor release while it settles.

`bootstack dev <file>` launches an app with these variables set so that
`App.run()` installs the hot-reload loop instead of a plain mainloop.
"""
from __future__ import annotations

import os

#: Set to ``"1"`` by ``bootstack dev`` to enable hot reload in the child process.
DEV_ENV_VAR = "BOOTSTACK_DEV"

#: Selects the reload strategy: ``"inprocess"`` (default — re-exec the with-body
#: in place, preserving state) or ``"restart"`` (re-exec the whole process on
#: save). ``bootstack dev --restart`` sets this to ``"restart"``.
DEV_MODE_VAR = "BOOTSTACK_DEV_MODE"

#: Reasonable minimum window size applied under ``bootstack dev`` when the app
#: did not set its own ``min_size`` — so the reload window starts usable and a
#: reload that shrinks content never collapses it below this floor. Dev-only;
#: production launches are unaffected.
DEV_MIN_SIZE = (640, 480)


def is_dev_mode() -> bool:
    """Return True when running under ``bootstack dev`` (hot reload enabled)."""
    return os.environ.get(DEV_ENV_VAR) == "1"


def dev_mode() -> str:
    """Return the configured reload strategy: ``"inprocess"`` or ``"restart"``."""
    mode = os.environ.get(DEV_MODE_VAR, "inprocess")
    return mode if mode in ("inprocess", "restart") else "inprocess"