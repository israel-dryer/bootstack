"""The PasswordField reveal (eye) toggle stays usable on a read-only field.

Revealing only flips the mask character — it never mutates the value — so a
read-only password (e.g. a generated secret shown for the user to peek at) can
still be revealed. A fully disabled field dims everything, including the toggle.

The `active_when_readonly` addon flag postdates this widget, so the toggle never
adopted it until this fix; this guards the wire-up.
"""
import pytest

import bootstack as bs


@pytest.fixture(scope="module")
def app():
    a = bs.App()
    a.__enter__()
    a._tk_root.deiconify()
    a._tk_root.update_idletasks()
    try:
        yield a
    finally:
        try:
            a.__exit__(None, None, None)
        except Exception:
            pass
        try:
            a._tk_root.destroy()
        except Exception:
            pass


def _eye(pf):
    return pf._internal.addons["visibility"]


def test_reveal_toggle_active_when_readonly(app):
    pf = bs.PasswordField(value="secret123", read_only=True)
    app._tk_root.update_idletasks()
    assert "disabled" not in _eye(pf).state()


def test_reveal_toggle_disabled_when_field_disabled(app):
    pf = bs.PasswordField(value="secret123", disabled=True)
    app._tk_root.update_idletasks()
    assert "disabled" in _eye(pf).state()


def test_reveal_toggle_follows_live_readonly_toggle(app):
    pf = bs.PasswordField(value="secret123")
    app._tk_root.update_idletasks()
    assert "disabled" not in _eye(pf).state()

    pf.read_only = True
    app._tk_root.update_idletasks()
    assert "disabled" not in _eye(pf).state()  # stays active under read-only

    pf.disabled = True
    app._tk_root.update_idletasks()
    assert "disabled" in _eye(pf).state()       # dims when fully disabled

    pf.disabled = False
    app._tk_root.update_idletasks()
    assert "disabled" not in _eye(pf).state()


def test_reveal_still_unmasks_under_readonly(app):
    pf = bs.PasswordField(value="secret123", read_only=True)
    app._tk_root.update_idletasks()
    entry = pf._internal._entry
    pf._internal.reveal()
    app._tk_root.update_idletasks()
    assert entry.cget("show") == ""     # unmasked
    pf._internal.hide()
    app._tk_root.update_idletasks()
    assert entry.cget("show") != ""     # re-masked
