"""Dialog.show(anchor_to=) accepts a public widget, not a raw tk widget.

The public positioning target is a `PublicWidgetBase` (e.g. a `bs.Button`); the
dialog unwraps it to its internal tk handle for `winfo_*`-based positioning. The
public signature must not leak `tkinter.Widget`.
"""
import inspect

import bootstack as bs
from bootstack.dialogs import Dialog
from bootstack.dialogs._impl.dialog import _resolve_anchor_target


def test_show_signature_has_no_tk_leak():
    sig = str(inspect.signature(Dialog.show))
    assert "tkinter" not in sig and "Widget" not in sig, sig


def test_resolve_unwraps_public_widget(app):
    import tkinter

    btn = bs.Button("anchor")
    resolved = _resolve_anchor_target(btn)
    assert isinstance(resolved, tkinter.Misc)
    assert resolved is btn._internal


def test_resolve_passes_through_strings_and_none():
    for value in ("screen", "cursor", "parent", None):
        assert _resolve_anchor_target(value) == value


def test_resolve_passes_through_raw_tk_widget(app):
    btn = bs.Button("anchor")
    raw = btn._internal
    assert _resolve_anchor_target(raw) is raw


def test_anchor_to_public_widget_end_to_end(app):
    btn = bs.Button("target")
    d = Dialog(title="t", mode="popover")
    d.show(anchor_to=btn, anchor_point="se", window_point="nw")
    assert d.toplevel is not None
    d.toplevel.destroy()
