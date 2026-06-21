"""StatusBar review (feat/statusbar-review).

The audit found no correctness bugs — StatusBar reuses the (separately-reviewed)
internal Toolbar. These lock down the StatusBar-specific behaviors: the right
cluster inserts its spacer exactly once, `clear()` resets the band, and a
`textsignal` segment updates live.

One module-scoped App (creating several Apps crashes Tk).
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


def test_right_side_inserts_spacer_once(app):
    import bootstack as bs

    sb = bs.StatusBar()
    sb.add_text("Ready", icon="check-circle")          # left
    sb.add_text("Errors: 0", side="right")             # inserts the spacer
    sb.add_text("Warnings: 2", side="right")           # reuses it
    app._tk_root.update_idletasks()
    assert sb._has_right_spacer is True
    # 2 left/right labels + 1 right label + exactly one spacer = 4 children
    assert len(sb._internal.content.winfo_children()) == 4


def test_clear_resets_band(app):
    import bootstack as bs

    sb = bs.StatusBar()
    sb.add_text("Ready")
    sb.add_text("main", side="right")
    app._tk_root.update_idletasks()
    sb.clear()
    app._tk_root.update_idletasks()
    assert len(sb._internal.content.winfo_children()) == 0
    assert sb._has_right_spacer is False


def test_textsignal_segment_updates_live(app):
    import bootstack as bs

    sb = bs.StatusBar()
    sig = bs.Signal("0 issues")
    sb.add_text(textsignal=sig, icon="exclamation-triangle")
    app._tk_root.update_idletasks()
    label = sb._internal.content.winfo_children()[-1]
    assert label.cget("text") == "0 issues"
    sig.set("3 issues")
    app._tk_root.update_idletasks()
    assert label.cget("text") == "3 issues"
