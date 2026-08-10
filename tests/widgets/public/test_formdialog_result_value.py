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

These drive the dialog the way a person does — press the footer button itself —
rather than reaching past it, because the defect lived in what happens between
the press and `show()` returning.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.dialogs import DialogButton, FormDialog

pytestmark = pytest.mark.gui

OPTIONS = [("One", 1), ("Two", 2), ("Three", 3)]


def _select_item(key="k"):
    return bs.FieldItem(key=key, label="K", editor="select",
                        editor_options={"options": OPTIONS})


def _required_item(key="r"):
    return bs.FieldItem(key=key, label="R", editor="text", required=True)


def _drive(dialog, app, action):
    """Show `dialog`, run `action(impl)` once it is really up, return its result.

    ⚠ `show()` runs a modal wait loop that neither `app.close()` nor a scheduled
    destroy escapes — it hangs. Every action here closes the dialog by one of
    its own paths instead.

    Polls for the modal grab rather than firing on a fixed delay. `show()`
    builds the content and positions the window — both of which pump the event
    loop on Windows — before it calls `grab_set()`, so a timer landing inside
    that window acts on a half-built dialog and can destroy it mid-build.
    `grab_set()` is the last thing `show()` does before it starts waiting, which
    makes it the barrier we want. Same hazard, and same remedy, as
    `test_dialog_result_subscription.py`.
    """
    root = app._tk_root
    pending: list[str] = []
    failures: list[BaseException] = []

    def toplevel():
        impl_dialog = dialog._internal._dialog
        top = impl_dialog.toplevel if impl_dialog else None
        return top if top is not None and top.winfo_exists() else None

    def run(attempt=0):
        top = toplevel()
        if top is None or top.grab_current() is not top:
            if attempt < 200:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            return
        try:
            action(dialog._internal)
        except BaseException as exc:  # noqa: BLE001 - re-raised below
            # Tkinter swallows an exception raised in a callback, so without
            # this the dialog would simply never close and the suite would hang
            # until `force_close` fired ten seconds later.
            failures.append(exc)
            top.destroy()

    def force_close():
        """Hard fallback so an action that fails to close cannot hang the suite."""
        top = toplevel()
        if top is not None:
            top.destroy()

    pending.append(root.after(50, run))
    pending.append(root.after(10000, force_close))
    try:
        dialog.show()
    finally:
        # The root outlives this test, so a timer left queued here fires during
        # a LATER one, where force_close would destroy an unrelated Toplevel.
        for job in pending:
            root.after_cancel(job)

    if failures:
        raise failures[0]
    return dialog.result


def _press(impl, *, cancel: bool):
    """Press the real footer button for a cancel / non-cancel role.

    Invoking the button spec's own `command` instead would skip `Dialog`'s
    wrapper — the part that stamps `dialog.result` from the spec, the part that
    honors a `False` return as a refusal, and the part that closes the dialog.
    All three matter here, so these tests go through the widget.
    `_create_standard_buttons` builds one button per spec in reverse order,
    which is what makes the pairing positional.
    """
    specs = list(reversed(impl._buttons))
    widgets = list(impl._dialog._footer.winfo_children())
    assert len(widgets) == len(specs), "precondition: one footer button per spec"

    for spec, widget in zip(specs, widgets):
        if (spec.role == "cancel") is cancel:
            widget.invoke()
            return
    raise AssertionError(f"no {'cancel' if cancel else 'submit'} button in the footer")


def _press_text(impl, text):
    """Press the footer button carrying `text`.

    `_press` picks by role, which cannot separate two non-cancel buttons — a
    Delete and a Save both qualify. The #437 tests need a named one.
    """
    specs = list(reversed(impl._buttons))
    widgets = list(impl._dialog._footer.winfo_children())
    assert len(widgets) == len(specs), "precondition: one footer button per spec"

    for spec, widget in zip(specs, widgets):
        if spec.text == text:
            widget.invoke()
            return
    raise AssertionError(f"no button labelled {text!r} in the footer")


def _submit(dialog, app, fill):
    """Show `dialog`, run `fill` on its form, and press the submit button."""
    def press_ok(impl):
        assert impl.form is not None, "precondition: the form was built"
        fill(impl.form)
        app._tk_root.update_idletasks()
        _press(impl, cancel=False)

    return _drive(dialog, app, press_ok)


def _cancel(dialog, app):
    """Show `dialog` and dismiss it with its Cancel button."""
    return _drive(dialog, app, lambda impl: _press(impl, cancel=True))


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


def test_a_cancelled_dialog_still_returns_none(app):
    """Cancel must not start reporting the snapshot."""
    dialog = FormDialog(items=[_select_item()])

    assert _cancel(dialog, app) is None


def test_a_cancel_button_with_its_own_command_still_returns_none(app):
    """Giving Cancel a command must not turn it into a submit.

    A cancel button's own `result` is `None`, so a capture on this path would
    make the entered data the dialog result and a cancelled dialog would hand it
    back — the opposite of what the default (command-less) Cancel does.
    """
    ran = []
    dialog = FormDialog(
        items=[_select_item()],
        buttons=[
            DialogButton(text="Cancel", role="cancel", command=lambda dlg: ran.append(dlg)),
            DialogButton(text="OK", role="primary", result="ok", default=True),
        ],
    )

    def fill_then_cancel(impl):
        impl.form._widgets["k"].value = "One"
        app._tk_root.update_idletasks()
        _press(impl, cancel=True)

    result = _drive(dialog, app, fill_then_cancel)

    # The command is handed the impl dialog, not the public wrapper.
    assert ran == [dialog._internal], "precondition: the custom cancel command ran"
    assert result is None, f"cancelling returned the entered data: {result!r}"


def test_a_reshown_dialog_does_not_report_the_previous_entries(app):
    """A re-shown dialog must not report the previous run's entries.

    ⚠ WHAT MAKES THIS PASS CHANGED IN #437, and the docstring says so because a
    test that misnames its own mechanism is how #417's vacuous chevron test
    survived review.

    It was written for a `_submitted_data = None` reset in `show()`. Back then
    `make_command` stamped the button's result even when the wrapper refused the
    press, so run two could close carrying a data token it had never captured and
    resolve it against run one's snapshot. The veto suppresses that stamp, so
    every write to `dialog.result` is now paired with a capture in the same call
    and the stale-token state has become unreachable. The reset was measured
    inert against all four combinations of itself and the veto, and removed.

    What carries this test now is the PRECONDITION below: with the veto gone the
    refused press closes the dialog, so the precondition trips before the result
    is ever asserted. That is what makes it a real guard on the veto rather than
    a test that happens to pass.
    """
    dialog = FormDialog(items=[_select_item(), _required_item()])

    def fill(form):
        form._widgets["k"].value = "Three"
        form._widgets["r"].value = "filled"

    first = _submit(dialog, app, fill)
    assert first["k"] == 3, "precondition: run one captured a snapshot"

    def press_ok_then_close(impl):
        _press(impl, cancel=False)  # required field is empty: validation fails
        assert impl._dialog.toplevel.winfo_exists(), (
            "precondition: the invalid form left the dialog open, so the run "
            "ends without capturing a snapshot of its own"
        )
        impl._dialog._on_close_request()  # the window's X button

    assert _drive(dialog, app, press_ok_then_close) is None, \
        "the second run reported the first run's entries"


# ---------------------------------------------------------------------------
# #437 - validation is gated on what a button DOES, not on its role
# ---------------------------------------------------------------------------
#
# `_wrap_button_commands` used to validate every button whose role was not
# `cancel`, which treats an action button as a data submission. `DataTable`
# builds its Delete as `{"role": "secondary", "result": "delete"}`, so deleting
# a record required the record to be valid - and validation cannot mean anything
# for a press that never reads the form.


def _delete_dialog(**kwargs):
    """A form with a required field empty, plus a DataTable-shaped Delete."""
    return FormDialog(
        items=[_select_item(), _required_item()],
        buttons=[
            DialogButton(text="Cancel", role="cancel"),
            DialogButton(text="Delete", role="secondary", result="delete", **kwargs),
            DialogButton(text="Save", role="primary", result="save", default=True),
        ],
    )


def test_an_action_button_runs_on_a_form_that_fails_validation(app):
    """The reported defect: Delete was inert on the records worth deleting.

    The dialog opens on a record whose required field is empty - the ordinary
    case for a table populated from data the form never produced, since
    `DataTable(rows=...)` validates nothing. Pre-fix the press early-returned and
    the dialog just sat there.

    ⚠ Asserting the result alone is VACUOUS here, and measurably so: pre-fix the
    refused press still left `'delete'` on the dialog (that is the destructive
    half, covered below), the window stayed open, and `_drive`'s ten-second
    `force_close` eventually destroyed it — so the assertion passed without the
    delete ever running. Closing is what separates "the action ran" from "a stale
    token happened to match", so the press is checked where it happens.
    """
    dialog = _delete_dialog()

    def delete_and_check(impl):
        top = impl._dialog.toplevel
        _press_text(impl, "Delete")
        assert not top.winfo_exists(), \
            "the delete press was refused: the dialog is still open"

    result = _drive(dialog, app, delete_and_check)

    assert result == "delete", f"the delete press produced {result!r}"


def test_a_refused_press_leaves_no_result_behind(app):
    """The destructive half: backing out must not perform the action.

    `Dialog` stamps a button's result after calling its command, so a press the
    command declined still recorded one. Cancel could not clear it - the only
    write in `Dialog` is guarded by `if s.result is not None`, and Cancel's own
    result IS `None` - so cancelling closed the window with the token standing
    and `DataTable` deleted the record.

    Driven here with a command that declines, which is what refusing a press
    means now that role no longer decides it and an action button no longer
    validates the form.
    """
    dialog = _delete_dialog(command=lambda dlg: False)

    def refuse_then_cancel(impl):
        _press_text(impl, "Delete")  # the command declines the press
        assert impl._dialog.toplevel.winfo_exists(), \
            "precondition: the refused press left the dialog open"
        _press(impl, cancel=True)

    result = _drive(dialog, app, refuse_then_cancel)

    assert result is None, f"cancelling performed the refused action: {result!r}"


def test_a_data_token_button_still_validates(app):
    """No-regression: the tokens that always validated must keep validating."""
    dialog = _delete_dialog()

    def refuse_then_cancel(impl):
        _press_text(impl, "Save")  # required field empty
        assert impl._dialog.toplevel.winfo_exists(), \
            "the invalid form was submitted anyway"
        _press(impl, cancel=True)

    assert _drive(dialog, app, refuse_then_cancel) is None


def test_a_button_with_no_result_token_still_validates(app):
    """The other inferred-submit arm.

    A non-cancel button with no `result` of its own hands back the entered data,
    so it submits even though no token says so.
    """
    dialog = FormDialog(
        items=[_required_item()],
        buttons=[
            DialogButton(text="Cancel", role="cancel"),
            DialogButton(text="Apply", role="primary", default=True),
        ],
    )

    def refuse_then_cancel(impl):
        _press_text(impl, "Apply")  # required field empty
        assert impl._dialog.toplevel.winfo_exists(), \
            "a token-less submit skipped validation"
        _press(impl, cancel=True)

    assert _drive(dialog, app, refuse_then_cancel) is None


def test_a_caller_supplied_button_spec_is_not_mutated(app):
    """The dialog must not rewrite the object it was handed.

    `_wrap_button_commands` overwrites `command`, and that went straight into
    the caller's own `DialogButton` - so a spec reused across two dialogs came
    back altered, and the second dialog then wrapped an already-wrapped command.
    """
    spec = DialogButton(text="Save", role="primary", result="save", default=True)
    original_command = spec.command

    FormDialog(items=[_select_item()],
               buttons=[DialogButton(text="Cancel", role="cancel"), spec])

    assert spec.command is original_command, "the caller's command was rewritten"


def test_a_reused_button_spec_still_works_in_a_second_dialog(app):
    """What the copy is actually protecting - the observable half.

    Asserting the spec is unchanged proves the mutation is gone; it does not
    prove the second dialog works. Without the copy the second `FormDialog`
    wraps the first one's wrapper, so the press runs against a dialog that is
    already destroyed.
    """
    spec = DialogButton(text="OK", role="primary", result="ok", default=True)
    cancel = DialogButton(text="Cancel", role="cancel")

    first = FormDialog(items=[_select_item()], buttons=[cancel, spec])
    assert _submit(first, app,
                   lambda form: setattr(form._widgets["k"], "value", "One"))["k"] == 1

    second = FormDialog(items=[_select_item()], buttons=[cancel, spec])
    result = _submit(second, app,
                     lambda form: setattr(form._widgets["k"], "value", "Three"))

    assert result["k"] == 3, f"the reused spec broke the second dialog: {result!r}"


def test_a_submit_button_with_its_own_command_captures_the_value(app):
    """Coverage for the capture inside `wrapped_command`.

    Every other test here reaches `auto_command`, because a submit button with
    its OWN command is the only way into this branch - so a regression that
    dropped or re-ordered this capture would pass the whole suite while
    reintroducing #428 for anyone who passes `command=`.
    """
    ran = []
    dialog = FormDialog(
        items=[_select_item()],
        buttons=[
            DialogButton(text="Cancel", role="cancel"),
            DialogButton(text="OK", role="primary", result="ok", default=True,
                         command=lambda dlg: ran.append(dlg)),
        ],
    )

    def fill_then_ok(impl):
        impl.form._widgets["k"].value = "Two"
        app._tk_root.update_idletasks()
        _press(impl, cancel=False)

    result = _drive(dialog, app, fill_then_ok)

    assert ran == [dialog._internal], "precondition: the custom command ran"
    assert result["k"] == 2, f"the command path lost the value: {result!r}"
    assert type(result["k"]) is int


def test_a_command_that_closes_the_dialog_itself_still_gets_the_values(app):
    """The form is captured BEFORE the caller's command runs, not after.

    A command is free to close the dialog - and if the capture happened after
    it, the read would land on destroyed editors and fall back to their Tk
    variables, which is #428 again on the one path that passes `command=`. The
    assertion is on the TYPE as much as the value: the fallback returns display
    text, so a regression here reports `'Two'`, not `2`.
    """
    def close_it(dlg):
        dlg._dialog.toplevel.destroy()

    dialog = FormDialog(
        items=[_select_item()],
        buttons=[
            DialogButton(text="Cancel", role="cancel"),
            DialogButton(text="OK", role="primary", result="ok", default=True,
                         command=close_it),
        ],
    )

    def fill_then_ok(impl):
        impl.form._widgets["k"].value = "Two"
        app._tk_root.update_idletasks()
        _press(impl, cancel=False)

    result = _drive(dialog, app, fill_then_ok)

    assert result["k"] == 2, f"the capture ran after the close: {result!r}"
    assert type(result["k"]) is int, f"got {type(result['k']).__name__}"


def test_a_command_refusing_after_the_capture_leaves_no_result(app):
    """The ordering hazard inside `wrapped_command`.

    The form is captured before the caller's command runs, so a command that
    then refuses the press has a snapshot sitting behind it. Recording the
    result at capture time would leave that value standing, and cancelling could
    not clear it - a cancel button's own result is `None`, and `Dialog` skips the
    write for `None`. This is the #437 destructive shape reached through a
    submit button rather than an action one, so it gets its own coverage.
    """
    dialog = FormDialog(
        items=[_select_item()],
        buttons=[
            DialogButton(text="Cancel", role="cancel"),
            DialogButton(text="OK", role="primary", default=True,
                         command=lambda dlg: False),
        ],
    )

    def refuse_then_cancel(impl):
        impl.form._widgets["k"].value = "Two"
        app._tk_root.update_idletasks()
        _press(impl, cancel=False)
        assert impl._dialog.toplevel.winfo_exists(), \
            "precondition: the refused press left the dialog open"
        _press(impl, cancel=True)

    result = _drive(dialog, app, refuse_then_cancel)

    assert result is None, f"the refused press left its data behind: {result!r}"


def test_a_cancel_role_button_carrying_a_data_token_captures_its_own_run(app):
    """`_button_returns_data` and `_resolve_result` must ask the question the same way.

    `_resolve_result` reads the result TOKEN first, so a button declared
    `role="cancel", result="ok"` resolves through the snapshot. If the capture
    side let the ROLE win, that press would take no snapshot of its own — and
    since nothing resets `_submitted_data` between shows, the caller would be
    handed the PREVIOUS run's entries. Contradictory input, but the failure it
    produced was silent and wrong rather than loud.
    """
    dialog = FormDialog(
        items=[_select_item()],
        buttons=[
            DialogButton(text="Close", role="cancel", result="ok"),
            DialogButton(text="OK", role="primary", result="ok", default=True),
        ],
    )

    first = _submit(dialog, app,
                    lambda form: setattr(form._widgets["k"], "value", "Three"))
    assert first["k"] == 3, "precondition: run one captured a snapshot"

    second = _drive(dialog, app, lambda impl: _press_text(impl, "Close"))

    assert second is not None, "the token resolved through no snapshot at all"
    assert second["k"] != 3, f"run two reported run one's entries: {second!r}"


def test_a_removed_kwarg_names_the_button_it_came_from(app):
    """The error a caller upgrading past `closes=` meets first.

    A bare `DialogButton(**mapping)` raises `TypeError: unexpected keyword
    argument 'closes'` with nothing to say which button, or that a button is
    involved at all. `Dialog._normalize_buttons` already wraps this; the
    `FormDialog` copy did not, so the same mistake reported worse through the
    dialog that most callers reach for.
    """
    with pytest.raises(ValueError, match="Invalid button mapping"):
        FormDialog(items=[_select_item()],
                   buttons=[{"text": "Apply", "closes": False}])
