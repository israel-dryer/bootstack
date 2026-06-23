"""Guard: every public event name is documented in the events API reference.

`bootstack.events.__all__` is the event catalog's public surface; the
`docs/api-reference/events.rst` page is its one autodoc home. New payloads are
easy to add to `__all__` and forget on the page (it happened with
`SashMoveEvent`/`ScrollEvent`), so this asserts the page lists every name —
either in an `autosummary` group or, for the string-literal aliases, as a
`.. py:type::` entry.
"""
from __future__ import annotations

import re
from pathlib import Path

import bootstack.events as events

EVENTS_RST = Path(__file__).resolve().parent.parent / "docs" / "api-reference" / "events.rst"


def test_events_rst_documents_every_public_name():
    text = EVENTS_RST.read_text(encoding="utf-8")
    # Tokenize on non-identifier characters so each match is a WHOLE identifier
    # ("ChangeEvent" stays one token — no substring false positives against
    # "Event"), then check membership exactly.
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text))
    missing = sorted(name for name in events.__all__ if name not in tokens)
    assert not missing, (
        f"{len(missing)} name(s) in bootstack.events.__all__ are not documented "
        f"in docs/api-reference/events.rst: {missing}. Add each to the matching "
        f"payload autosummary group, or — for a string-literal alias — as a "
        f".. py:type:: entry under Enumerations."
    )
