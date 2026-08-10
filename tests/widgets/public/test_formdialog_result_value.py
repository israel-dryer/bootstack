"""Regression tests for `FormDialog.result` returning values, not display text (#428).

Reported by an external user: with `options=[('One', 1), ...]`, a plain
`bs.Select` and a `Form` select both return the value `1`, while
`FormDialog.result` returned the text `'One'`.

The cause was a read-after-teardown. `FormDialog.show()` only returns once the
dialog is gone, and it then read `self.form.data` — from destroyed editors.
`Form._read_value_from_widget` falls back from a raising `widget.value` to
`self._variables[key].get()`, and that Tk variable holds display text. Because Tk
variables are string-backed, EVERY value type was flattened to `str` on that
path, so this was never select-specific.

These drive the dialog the way a person does — press the OK button's own command
— rather than reaching past it, because the defect lived in what happens between
the press and `show()` returning.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.dialogs import FormDialog

pytestmark = pytest.mark.gui

OPTIONS = [("One", 1), ("Two", 2), ("Three", 3)]


def _select_item(key="k"):
    return bs.FieldItem(key=key, label="K", editor="select",
                        editor_options={"options": OPTIONS})


def _submit(dialog, app, fill):
    """Show `dialog`, run `fill`, press OK, and return its result.

    ⚠ `show()` runs a modal wait loop that neither `app.close()` nor a scheduled
    destroy escapes — it hangs. Invoking the OK button's own command closes the
    dialog by its normal path, which is also the path under test.
    """
    def press_ok():
        impl = dialog._internal
        if impl.form is None:  # pragma: no cover - would mean the build failed
            return
        fill(impl.form)
        app._tk_root.update_idletasks()
        for button in impl._buttons:
            if button.role != "cancel":
                button.command()
                return

    app._tk_root.after(200, press_ok)
    dialog.show()
    return dialog.result


def test_formdialog_returns_the_option_value_not_its_text(app):
    """The reported defect: `'One'` came back where `1` was entered."""
    dialog = FormDialog(items=[_select_item()])

    result = _submit(dialog, app,
                     lambda form: setattr(form._widgets["k"], "value", "One"))

    assert result is not None, "the dialog returned no data at all"
    assert result["k"] == 1


def test_formdialog_preserves_the_value_type(app):
    """The half that breaks callers.

    The broken path read back through a string-backed Tk variable, so an `int`
    arrived as `str`. Asserting equality alone would not catch a regression that
    returned `'1'`.
    """
    dialog = FormDialog(items=[_select_item()])

    result = _submit(dialog, app,
                     lambda form: setattr(form._widgets["k"], "value", "Two"))

    assert result["k"] == 2
    assert type(result["k"]) is int, f"got {type(result['k']).__name__}"


def test_a_plain_form_agrees_with_the_dialog(app):
    """The control, and the reporter's actual complaint.

    A `Form` built from the identical `FieldItem` was never broken — it is never
    torn down before being read. It passes before and after the fix, so a
    failure in the tests above is attributable to the dialog rather than to the
    select or to the option list.
    """
    form = bs.Form(items=[_select_item()])
    app._tk_root.update_idletasks()
    form._internal._widgets["k"].value = "One"
    app._tk_root.update_idletasks()

    assert form.get()["k"] == 1
    assert type(form.get()["k"]) is int


def _cancel(dialog, app):
    """Show `dialog` and dismiss it the way Cancel does, then return its result.

    ⚠ A cancel button keeps `closes = True`, so the dialog framework is what
    closes it — only non-cancel buttons are switched to `closes = False` and
    destroy the toplevel themselves. Invoking `command()` on cancel therefore
    returns early WITHOUT closing, leaving `show()` blocked; the first version of
    this helper did exactly that and the dialog was still open when the next
    thing ran, which reported a previous dialog's data. Destroying the toplevel
    is what the framework does for it.
    """
    def dismiss():
        impl = dialog._internal
        for button in impl._buttons:
            if button.role == "cancel":
                button.command()
                break
        if impl._dialog and impl._dialog.toplevel:
            impl._dialog.toplevel.destroy()

    app._tk_root.after(200, dismiss)
    dialog.show()
    return dialog.result


def test_a_cancelled_dialog_still_returns_none(app):
    """Cancel must not start reporting the snapshot."""
    dialog = FormDialog(items=[_select_item()])

    assert _cancel(dialog, app) is None


def test_a_reshown_dialog_does_not_report_the_previous_entries(app):
    """The snapshot is reset on show, so run two cannot inherit run one.

    Without the reset in `show()`, cancelling the second run would hand back the
    first run's data instead of `None`.
    """
    dialog = FormDialog(items=[_select_item()])

    first = _submit(dialog, app,
                    lambda form: setattr(form._widgets["k"], "value", "Three"))
    assert first["k"] == 3

    assert _cancel(dialog, app) is None, \
        "the second run reported the first run's data"
