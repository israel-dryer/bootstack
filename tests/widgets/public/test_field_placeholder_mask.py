"""Regression guard for #195 — an input mask (`show=`, e.g. a password bullet)
must NOT mask the placeholder text. The placeholder is a readable hint, not user
input: it renders unmasked, and the mask reappears only for real, committed input.
"""
import pytest

import bootstack as bs


def test_password_placeholder_renders_unmasked(app):
    pf = bs.PasswordField(placeholder="Enter password")
    app._tk_root.update_idletasks()
    entry = pf._internal._entry

    # Empty + unfocused: placeholder shows in plain text, mask is suppressed.
    assert entry._showing_placeholder is True
    assert entry.cget("show") == ""
    assert entry.get() == "Enter password"


def test_password_mask_restored_for_real_input(app):
    pf = bs.PasswordField(placeholder="Enter password")
    app._tk_root.update_idletasks()
    entry = pf._internal._entry

    # Focus + type: placeholder is gone and the mask is back.
    entry.event_generate("<FocusIn>")
    entry.insert(0, "hunter2")
    app._tk_root.update_idletasks()
    assert entry._showing_placeholder is False
    assert entry.cget("show") == "•"  # the bullet mask
    assert entry.get() == "hunter2"


def test_password_placeholder_returns_unmasked_after_clearing(app):
    pf = bs.PasswordField(placeholder="Enter password")
    app._tk_root.update_idletasks()
    entry = pf._internal._entry

    entry.event_generate("<FocusIn>")
    entry.insert(0, "abc")
    app._tk_root.update_idletasks()
    entry.delete(0, "end")
    entry.event_generate("<FocusOut>")
    app._tk_root.update_idletasks()

    # Empty again: placeholder is back and unmasked.
    assert entry._showing_placeholder is True
    assert entry.cget("show") == ""
    assert entry.get() == "Enter password"


def test_visibility_toggle_does_not_mask_placeholder(app):
    # Pressing the eye toggle while the placeholder is showing must not re-mask it.
    pf = bs.PasswordField(placeholder="Enter password")
    app._tk_root.update_idletasks()
    entry = pf._internal._entry

    pf._internal._show_password(None)
    pf._internal._hide_password(None)
    app._tk_root.update_idletasks()

    assert entry._showing_placeholder is True
    assert entry.cget("show") == ""
    assert entry.get() == "Enter password"


def test_textfield_placeholder_unaffected_without_mask(app):
    # A plain field has no mask; placeholder still shows and clears normally.
    tf = bs.TextField(placeholder="Search...")
    app._tk_root.update_idletasks()
    entry = tf._internal._entry

    assert entry._showing_placeholder is True
    assert entry.cget("show") == ""
    assert entry.get() == "Search..."

    entry.event_generate("<FocusIn>")
    entry.insert(0, "query")
    app._tk_root.update_idletasks()
    assert entry._showing_placeholder is False
    assert entry.cget("show") == ""
    assert entry.get() == "query"