"""Reverse-tab keysym binding (#520).

`<ISO_Left_Tab>` is the keysym an X11 server reports for Shift+Tab. Tk builds
for other windowing systems need not know it, and some reject it outright, so
binding it unconditionally raised `bad event type or keysym "ISO_Left_Tab"`
while constructing a `TextArea` or a `CodeEditor`.

The binding belongs on X11 and nowhere else: dropping it altogether would cost
X11 users reverse traversal and dedent, since Shift+Tab never arrives there as
`<Shift-Tab>`.
"""
import tkinter as tk

import pytest

import bootstack as bs

pytestmark = pytest.mark.gui

WIDGETS = [bs.TextArea, bs.CodeEditor]
IDS = ["TextArea", "CodeEditor"]


def _windowing_system(root) -> str:
    return root.tk.call("tk", "windowingsystem")


@pytest.mark.parametrize("factory", WIDGETS, ids=IDS)
def test_builds_on_a_tk_that_rejects_the_reverse_tab_keysym(
    app, tmp_tk_root, monkeypatch, factory,
):
    if _windowing_system(tmp_tk_root) == "x11":
        pytest.skip("the keysym is valid on X11, where the binding is intended")

    original = tk.Misc.bind

    def rejecting_bind(self, sequence=None, func=None, add=None):
        if sequence is not None and "ISO_Left_Tab" in str(sequence):
            raise tk.TclError('bad event type or keysym "ISO_Left_Tab"')
        return original(self, sequence, func, add)

    monkeypatch.setattr(tk.Misc, "bind", rejecting_bind)

    # the simulated rejection is live, so a surviving construction means something
    with pytest.raises(tk.TclError):
        tk.Text(tmp_tk_root).bind("<ISO_Left_Tab>", lambda _: None)

    widget = factory()
    assert widget.value == ""


@pytest.mark.parametrize("factory", WIDGETS, ids=IDS)
def test_reverse_tab_keysym_is_bound_only_on_x11(
    app, tmp_tk_root, monkeypatch, factory,
):
    original = tk.Misc.bind
    bound: list[str] = []

    def recording_bind(self, sequence=None, func=None, add=None):
        bound.append(str(sequence))
        return original(self, sequence, func, add)

    monkeypatch.setattr(tk.Misc, "bind", recording_bind)
    factory()

    assert "<Shift-Tab>" in bound  # the recorder saw the reverse-tab bindings
    assert ("<ISO_Left_Tab>" in bound) is (_windowing_system(tmp_tk_root) == "x11")