"""Coverage for what a button press means, across every consumer of `DialogButton`.

#437 gave a button command the ability to refuse its own press by returning
`False`, and #438 removed `closes` in favor of it. That reshaped four call
sites. Three of them had no test at all: `QueryDialog._on_submit` and
`DateDialog._on_confirm_range` were rewritten onto the veto and verified only by
reading, and `Form`'s button row — the second consumer of `DialogButton`, one
file over from the dialogs — went on recording a result for a press its command
had just declined.

These drive the real footer button rather than calling the spec's command,
because the veto lives in the wrapper `Dialog` puts around it: the part that
stamps the result and the part that closes the window. Calling the command
directly skips both, which is exactly the gap that let the rewrite ship
untested.
"""
from __future__ import annotations

from datetime import date

import pytest

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton

pytestmark = pytest.mark.gui


def _drive(dialog, app, action):
    """Show an internal dialog, run `action(dialog)` once it is really up.

    ⚠ `show()` runs a modal wait loop that no scheduled `close()` escapes — it
    hangs. Every action here leaves the dialog by one of its own paths.

    Polls for the modal grab rather than firing on a fixed delay: `show()`
    builds and positions the window — both of which pump the event loop on
    Windows — before `grab_set()`, so a timer landing inside that window acts on
    a half-built dialog. `grab_set()` is the last thing `show()` does before it
    waits, which makes it the barrier. Same hazard and remedy as
    `test_formdialog_result_value.py`.
    """
    root = app._tk_root
    pending: list[str] = []
    failures: list[BaseException] = []

    def toplevel():
        top = dialog._dialog.toplevel
        return top if top is not None and top.winfo_exists() else None

    def run(attempt=0):
        top = toplevel()
        if top is None or top.grab_current() is not top:
            if attempt < 200:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            return
        try:
            action(dialog)
        except BaseException as exc:  # noqa: BLE001 - re-raised below
            # Tkinter swallows an exception raised in a callback, so without
            # this the dialog would never close and the suite would hang until
            # force_close fired ten seconds later.
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


def _press(dialog, *, cancel: bool):
    """Press the real footer button for a cancel / non-cancel role.

    `_create_standard_buttons` builds one button per spec in reverse order,
    which is what makes the pairing positional.
    """
    impl = dialog._dialog
    specs = list(reversed(impl._buttons))
    widgets = list(impl._footer.winfo_children())
    assert len(widgets) == len(specs), "precondition: one footer button per spec"

    for spec, widget in zip(specs, widgets):
        if (spec.role == "cancel") is cancel:
            widget.invoke()
            return
    raise AssertionError(f"no {'cancel' if cancel else 'submit'} button in the footer")


class _Wrapped:
    """Adapt a bare `Dialog` to the `impl._dialog` shape `_drive` expects."""

    def __init__(self, dialog):
        self._dialog = dialog

    def show(self):
        self._dialog.show()


# --- QueryDialog: the submit path rewritten onto the veto -------------------


def test_query_dialog_submit_records_the_value_and_closes(app):
    """The accept half: `_on_submit` returns True, so `Dialog` closes.

    ⚠ The close is asserted where it happens, not inferred from the result.
    `_on_submit` writes `dialog.result` BEFORE it returns, so a regression that
    refused every press would leave the value standing, the window open, and
    `_drive`'s ten-second `force_close` would tear it down — and the result
    assertion alone would still pass. Measured: it did. Same vacuity as #417's
    chevron test, caught here by the control in
    `development/probe_437_review2_controls.py`.
    """
    from bootstack.dialogs._impl.query import QueryDialog

    dialog = QueryDialog("Name:", master=app._tk_root)

    def type_and_submit(dlg):
        assert dlg._entry_widget is not None, "precondition: the entry was built"
        dlg._entry_widget.value = "Ada"
        app._tk_root.update_idletasks()
        top = dlg._dialog.toplevel
        _press(dlg, cancel=False)
        assert not top.winfo_exists(), \
            "the submit was refused: the dialog is still open"

    _drive(dialog, app, type_and_submit)

    assert dialog.result == "Ada"


def test_query_dialog_refuses_a_submit_it_cannot_accept(app):
    """The refuse half: a `None` value returns False, so the window stays open.

    A date query with nothing entered is the one refusal `_on_submit` reaches
    without opening a `MessageBox` — the other two would stack a second modal
    on top of this one and stall the run.
    """
    from bootstack.dialogs._impl.query import QueryDialog

    dialog = QueryDialog("Day:", master=app._tk_root, datatype=date)

    def submit_empty_then_close(dlg):
        assert dlg._entry_widget.value is None, "precondition: nothing entered"
        _press(dlg, cancel=False)
        assert dlg._dialog.toplevel.winfo_exists(), (
            "the refused submit closed the dialog anyway"
        )
        dlg._dialog._on_close_request()  # the window's X button

    _drive(dialog, app, submit_empty_then_close)

    assert dialog.result is None


# --- DateDialog: the range footer rewritten onto the veto -------------------


def test_date_range_ok_returns_both_endpoints_and_closes(app):
    """⚠ The close is asserted at the press, for the reason spelled out in
    `test_query_dialog_submit_records_the_value_and_closes`: `_on_confirm_range`
    records the range before it returns, so asserting only the result passes
    against a version that refuses every press.
    """
    from bootstack.dialogs._impl.datedialog import DateDialog

    dialog = DateDialog(master=app._tk_root, selection_mode="range",
                        start_date=date(2026, 3, 2), end_date=date(2026, 3, 5))

    def confirm(dlg):
        top = dlg._dialog.toplevel
        _press(dlg, cancel=False)
        assert not top.winfo_exists(), \
            "the complete range was refused: the dialog is still open"

    _drive(dialog, app, confirm)

    assert dialog.result == (date(2026, 3, 2), date(2026, 3, 5))


def test_date_range_ok_is_refused_until_both_endpoints_are_picked(app):
    """Half a range must leave the dialog open rather than commit a partial one."""
    from bootstack.dialogs._impl.datedialog import DateDialog

    dialog = DateDialog(master=app._tk_root, selection_mode="range",
                        start_date=date(2026, 3, 2))

    def confirm_partial_then_cancel(dlg):
        assert dlg._picker.get_range()[1] is None, "precondition: no end date"
        _press(dlg, cancel=False)
        assert dlg._dialog.toplevel.winfo_exists(), (
            "the incomplete range closed the dialog anyway"
        )
        _press(dlg, cancel=True)

    _drive(dialog, app, confirm_partial_then_cancel)

    assert dialog.result is None


# --- the keypad Enter key --------------------------------------------------


def _keypad_dialog(app, buttons=None):
    return Dialog(
        title="Keypad",
        content_builder=lambda: bs.Label("body"),
        buttons=buttons or [DialogButton(text="OK", role="primary", result="ok", default=True)],
        parent=app._tk_root,
    )


def _footer_widget(impl, text):
    """The real footer button built for the spec whose text is `text`."""
    specs = list(reversed(impl._buttons))
    widgets = list(impl._footer.winfo_children())
    assert len(widgets) == len(specs), "precondition: one footer button per spec"
    for spec, widget in zip(specs, widgets):
        if spec.text == text:
            return widget
    raise AssertionError(f"no footer button labelled {text!r}")


def test_enter_presses_the_default_button(app):
    """The behavior half, driven end to end through the real key."""
    dialog = _keypad_dialog(app)

    def hit_enter(dlg):
        top = dlg._dialog.toplevel
        assert top.winfo_ismapped(), "precondition: the dialog is on screen"
        # A key press is delivered to the FOCUS widget, which on a freshly
        # opened dialog is the toplevel itself — measured. `Dialog` asks for
        # the default button to be focused, and that request does not take
        # (the button is built before the window is deiconified), so nothing
        # inside the window holds focus and this binding is the only thing
        # that answers Enter. Generating on the toplevel is therefore the
        # faithful simulation HERE, and only here; the two tests below give a
        # button focus first, the way a click does.
        #
        # `focus_lastfor`, not `focus_get`: the latter reports nothing unless
        # the window is active, which is not dependable in the shared root.
        assert top.focus_lastfor() is top, "precondition: nothing inside holds focus"
        top.event_generate("<Return>", when="now")

    # This dialog IS the `Dialog`, so `_drive`'s `dialog._dialog` needs a hop.
    _drive(_Wrapped(dialog), app, hit_enter)

    assert dialog.result == "ok", "Enter did not press the default button"


def test_enter_on_the_default_button_invokes_it_once(app):
    """One press, one command run — even when the press is refused.

    Two things have to be true for this to be reachable, and both are:

    The button has to hold focus. A freshly opened dialog focuses nothing (see
    above), but a CLICK focuses the button it lands on — ttk's own `Press`
    binding does `focus $w` unconditionally. So this is the state a user is in
    after clicking a button whose command refused the press, which is exactly
    the state the veto was added to create. The focus is set explicitly here
    rather than by synthesizing a click, to keep the test about the key.

    And the press has to be refused. An accepted press destroys the window,
    and the destroy aborts the second dispatch before it invokes anything —
    measured: the same dialog with an accepting command reads one invocation
    whether the guard is there or not.
    """
    calls: list[str] = []
    dialog = _keypad_dialog(app, [DialogButton(
        text="OK", role="primary", result="ok", default=True,
        command=lambda dlg: (calls.append("ok"), False)[1],
    )])

    def hit_enter(dlg):
        top = dlg._dialog.toplevel
        assert top.winfo_ismapped(), "precondition: the dialog is on screen"
        button = _footer_widget(dlg._dialog, "OK")
        button.focus_set()
        assert top.focus_lastfor() is button, "precondition: the default button has focus"
        button.event_generate("<Return>", when="now")
        assert calls == ["ok"], f"one press should run one command, ran {calls}"
        assert top.winfo_exists(), "the refused press should have left the dialog open"
        top.destroy()

    _drive(_Wrapped(dialog), app, hit_enter)

    assert dialog.result is None, "a refused press recorded a result"


def test_enter_on_a_focused_button_does_not_also_press_the_default(app):
    """Keyboard traversal: Enter presses the button you tabbed to, alone.

    The crossfire case, and the damaging one — `Apply` refuses the press, so
    without the guard the toplevel binding invokes `OK` on top of it and the
    dialog closes reporting a submission the user never made.
    """
    calls: list[str] = []
    dialog = _keypad_dialog(app, [
        DialogButton(text="Cancel", role="cancel", result=None),
        DialogButton(
            text="Apply", role="secondary", result="apply",
            command=lambda dlg: (calls.append("apply"), False)[1],
        ),
        DialogButton(
            text="OK", role="primary", result="ok", default=True,
            command=lambda dlg: calls.append("ok"),
        ),
    ])

    def hit_enter(dlg):
        top = dlg._dialog.toplevel
        assert top.winfo_ismapped(), "precondition: the dialog is on screen"
        apply_widget = _footer_widget(dlg._dialog, "Apply")
        apply_widget.focus_set()
        assert top.focus_lastfor() is apply_widget, "precondition: Apply holds focus"
        apply_widget.event_generate("<Return>", when="now")
        assert calls == ["apply"], f"Enter ran more than the focused button: {calls}"
        assert top.winfo_exists(), "the refused press should have left the dialog open"
        top.destroy()

    _drive(_Wrapped(dialog), app, hit_enter)

    assert dialog.result is None, "the default button submitted on someone else's press"


def test_the_keypad_enter_key_is_bound_alongside_enter(app):
    """The structural half, because the keypad key CANNOT be synthesized.

    ⚠ Measured on Windows Tk 8.6.15: `event_generate("<KP_Enter>")` produces an
    event with keysym `'??'` and keycode `0`, which matches no binding — a
    `<Key>` catch-all sees it, `<KP_Enter>` does not. Passing `keycode=13`
    makes it arrive as `Return` instead. So a behavioral test of this key is not
    a stricter version of the one above, it is one that silently tests nothing:
    the first draft passed its `winfo_ismapped` precondition, generated the
    event, and then failed on the result ten seconds later via the harness
    timeout.

    What is assertable is that the sequence is bound at all, which is the whole
    of the defect — `KP_Enter` is a distinct keysym from `Return` on Windows,
    X11 and Aqua, and only `Return` was wired up. `test_enter_presses_the_
    default_button` covers what the binding does; the two are installed by one
    loop over both sequences.
    """
    dialog = _keypad_dialog(app)

    def check_bindings(dlg):
        top = dlg._dialog.toplevel
        bound = {str(seq) for seq in top.bind()}
        assert "<Key-Return>" in bound, "precondition: Enter is bound at all"
        assert "<Key-KP_Enter>" in bound, f"keypad Enter is not bound: {sorted(bound)}"
        assert top.bind("<KP_Enter>"), "the sequence is bound to an empty script"
        top.destroy()

    _drive(_Wrapped(dialog), app, check_bindings)


# --- Form: the second consumer of DialogButton -----------------------------


def _text_item(key="k"):
    return bs.FieldItem(key=key, label="K", editor="text")


def _press_form_button(form):
    """Invoke the single footer button on a public `bs.Form`."""
    buttons = []
    stack = [form._internal]
    while stack:
        widget = stack.pop()
        stack.extend(widget.winfo_children())
        if "button" in widget.winfo_class().lower():
            buttons.append(widget)
    assert len(buttons) == 1, f"precondition: one footer button, found {len(buttons)}"
    buttons[0].invoke()


def test_a_form_button_command_can_refuse_its_press(app):
    """`DialogButton.command` documents the veto unconditionally — `Form` is a consumer.

    `Form` discarded the return value and stamped `result` regardless, which is
    the same "a declined press still records a result" shape #437 removed from
    `Dialog`, left standing one file over.
    """
    ran = []

    def refuse(form):
        ran.append(form)
        return False

    form = bs.Form(items=[_text_item()],
                   buttons=[DialogButton(text="Save", role="primary", command=refuse)])
    app._tk_root.update_idletasks()
    form._internal._widgets["k"].value = "typed"
    app._tk_root.update_idletasks()

    _press_form_button(form)

    assert ran, "precondition: the command ran at all"
    assert form.result is None, f"a refused press recorded {form.result!r}"


def test_a_form_button_command_that_accepts_still_records(app):
    """The control: without it, a `Form` that recorded nothing ever would pass above."""
    ran = []

    form = bs.Form(
        items=[_text_item()],
        buttons=[DialogButton(text="Save", role="primary",
                              command=lambda f: ran.append(f))],  # returns None
    )
    app._tk_root.update_idletasks()
    form._internal._widgets["k"].value = "typed"
    app._tk_root.update_idletasks()

    _press_form_button(form)

    assert ran, "precondition: the command ran at all"
    assert form.result == {"k": "typed"}, f"an accepted press recorded {form.result!r}"


def test_a_refused_form_press_clears_the_previous_result(app):
    """A refusal must not leave the last accepted press readable at `form.result`.

    The two tests above only ever refuse from a clean form, where `result` is
    still the `None` it was constructed with — so both pass whether or not a
    refusal clears anything. The sequence that separates them is accept, edit,
    refuse, which a `Form` invites in a way a `Dialog` cannot: the accepted
    press closes a dialog, while a form keeps its button row up. Without the
    clear, a caller reading `form.result` here gets `{'k': 'accepted'}` — data
    the user has since changed, from a press the command declined.
    """
    refusing = []

    def save(form):
        return False if refusing else None

    form = bs.Form(items=[_text_item()],
                   buttons=[DialogButton(text="Save", role="primary", command=save)])
    app._tk_root.update_idletasks()

    form.set({"k": "accepted"})
    app._tk_root.update_idletasks()
    _press_form_button(form)
    assert form.result == {"k": "accepted"}, (
        f"precondition: the accepted press recorded {form.result!r}")

    refusing.append(True)
    form.set({"k": "edited"})
    app._tk_root.update_idletasks()
    _press_form_button(form)

    assert form.data == {"k": "edited"}, (
        f"precondition: the edit landed, data is {form.data!r}")
    assert form.result is None, f"a refused press left {form.result!r} readable"
