"""Shared pytest fixtures for the bootstack test suite."""
from __future__ import annotations

import pytest


@pytest.fixture
def tmp_tk_root():
    """A throwaway root window for tests that exercise event binding.

    Backed by a bootstack ``App`` (a bare ``tkinter.Tk()`` can't be created
    once bootstack's autostyle patch is installed without an active App).
    Withdrawn (never shown) and destroyed on teardown. Requires a display, so
    consumers should be marked ``@pytest.mark.gui``.
    """
    import bootstack as bs

    app = bs.App()
    root = app._tk_root
    root.withdraw()
    try:
        yield root
    finally:
        try:
            root.destroy()
        except Exception:
            pass
