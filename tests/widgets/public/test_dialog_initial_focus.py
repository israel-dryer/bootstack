"""Where focus sits when a dialog opens.

`DialogButton.default` is documented as "focused, triggered by Enter". The
first half was not true: `Dialog` focused the default button from
`_build_footer`, which runs while `_create_toplevel` still has the toplevel
WITHDRAWN. `focus_set()` is a silent no-op there — `TkSetFocusWin` walks the
widget's ancestry and returns without setting anything — so keyboard users got
no focus ring and a Tab order starting from nowhere (issue #439).

Two things are pinned here, because fixing the first one exposed the second:

  * the default button ends up focused, and
  * a content widget that wants initial focus BEATS it. `QueryDialog` needs
    this — focus on its OK button rather than its entry means `ask_string()`
    does not accept typing, and Space submits an empty value.

⚠ THE BARRIER IS THE SUBTLE PART. Focus is deferred to the button's `<Map>`,
and the modal grab is set BEFORE the geometry manager maps the footer's
children at idle. Polling on the grab alone therefore samples the window before
focus can have landed, and the test fails for a reason that has nothing to do
with the fix. `_drive` below waits for the grab AND for every footer child to
be mapped, the same barrier `test_dialog_press_contract.py` uses.

⚠ AND THAT WAS STILL TOO NARROW — it is a barrier over the FOOTER, while the
widget under test here is sometimes in the CONTENT. It shipped flaky at 1 in 8
(issue #446). `_drive` now also waits for whatever `show()` resolved initial
focus onto. See `focus_target_is_up()`.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton

pytestmark = pytest.mark.gui


def _drive(dialog, app, action, show=None):
    """Show `dialog`; run `action(top)` once it is really up, then close it.

    `show()` runs a modal wait loop that a close scheduled with `after` does
    not break, so the action closes the window itself.

    `show` overrides which callable opens the window, for a wrapper whose own
    `show()` does setup its inner `Dialog` never sees — `DateDialog` builds its
    buttons there, so opening the inner one directly hangs on a footer that is
    never built.
    """
    root = app._tk_root
    pending: list[str] = []
    failures: list[BaseException] = []

    def toplevel():
        top = dialog.toplevel
        return top if top is not None and top.winfo_exists() else None

    def footer_is_up():
        footer = getattr(dialog, "_footer", None)
        if footer is None or not footer.winfo_exists():
            return False
        children = footer.winfo_children()
        return bool(children) and all(w.winfo_ismapped() for w in children)

    def focus_target_is_up():
        """The widget initial focus TARGETS is mapped — see the warning below.

        ⚠ The footer being mapped does not imply this, and assuming it did cost
        a flaky test (issue #446, 1 failure in 8 runs of the shared leg).
        `QueryDialog` claims `_focus_target` for its entry, which lives in the
        CONTENT subtree — a different part of the widget tree that the footer
        check says nothing about. Focus is deferred to the target's own `<Map>`
        (`Dialog._focus_when_mapped`), so sampling before the entry maps reads
        the toplevel and the test fails on focus for a reason that is really
        about mapping.

        Measured in `development/probe_446_barrier_scope.py`: with the footer
        barrier alone the entry was still unmapped in **4 of 12** dialogs and
        focus missed in exactly those same 4; waiting for this as well took it
        to **0 of 12**, the two columns tracking one-for-one.

        `None` when no spec asked for focus — a dialog with no default button
        and no content claim has nothing to wait for, and must not hang here.
        """
        target = dialog._focus_target or dialog._default_button
        if target is None:
            return True
        return bool(target.winfo_exists()) and bool(target.winfo_ismapped())

    def run(attempt=0):
        top = toplevel()
        if (top is None or top.grab_current() is not top
                or not footer_is_up() or not focus_target_is_up()):
            if attempt < 200:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            return
        try:
            action(top)
        except BaseException as exc:  # noqa: BLE001 - re-raised below
            # Tkinter swallows an exception raised in a callback, so without
            # this the dialog never closes and the suite hangs until the
            # fallback fires.
            failures.append(exc)
        finally:
            if toplevel() is not None:
                top.destroy()

    def force_close():
        top = toplevel()
        if top is not None:
            top.destroy()

    pending.append(root.after(50, run))
    pending.append(root.after(10000, force_close))
    try:
        (show or dialog.show)()
    finally:
        # The root outlives this test, so a timer left queued here fires during
        # a LATER one, where force_close would destroy an unrelated Toplevel.
        for job in pending:
            root.after_cancel(job)

    if failures:
        raise failures[0]


def _footer_widget(impl, text):
    """The real footer button for the spec labelled `text`.

    `_create_standard_buttons` builds one button per spec in reverse order,
    which is what makes the pairing positional.
    """
    specs = list(reversed(impl._buttons))
    widgets = list(impl._footer.winfo_children())
    assert len(widgets) == len(specs), "precondition: one footer button per spec"
    for spec, widget in zip(specs, widgets):
        if spec.text == text:
            return widget
    raise AssertionError(f"no footer button labelled {text!r}")


def _dialog(app):
    return Dialog(
        title="focus",
        content_builder=lambda: bs.Label("body"),
        buttons=[
            DialogButton(text="Cancel", role="cancel", result=None),
            DialogButton(text="OK", role="primary", result="ok", default=True),
        ],
        parent=app._tk_root,
    )


def test_the_default_button_is_focused_when_the_dialog_opens(app):
    """#439. The half of `DialogButton.default` that was not true."""
    dialog = _dialog(app)
    seen = {}

    def check(top):
        button = _footer_widget(dialog, "OK")
        # A precondition, because an unmapped widget cannot hold focus and the
        # assertion below would then fail for the wrong reason.
        assert button.winfo_ismapped(), "precondition: the button is mapped"
        # `focus_lastfor`, not `focus_get`: the latter reports nothing unless
        # the window is active, which is not dependable in the shared root.
        seen["focused"] = top.focus_lastfor()
        seen["button"] = button

    _drive(dialog, app, check)

    assert seen["focused"] is seen["button"], (
        "the default button did not receive focus when the dialog opened"
    )


def test_a_non_default_button_is_not_focused(app):
    """Control: focus lands on the DEFAULT button, not merely on some button.

    Without this, a regression that focused whichever button was built last
    would pass the test above — the default button is built last here.
    """
    dialog = _dialog(app)
    seen = {}

    def check(top):
        seen["focused"] = top.focus_lastfor()
        seen["cancel"] = _footer_widget(dialog, "Cancel")

    _drive(dialog, app, check)

    assert seen["focused"] is not seen["cancel"], (
        "focus landed on the cancel button rather than the default one"
    )


def test_a_dialog_with_no_default_button_focuses_nothing(app):
    """Control: the fix does not focus a button that no spec asked for."""
    dialog = Dialog(
        title="no default",
        content_builder=lambda: bs.Label("body"),
        buttons=[
            DialogButton(text="Cancel", role="cancel", result=None),
            DialogButton(text="OK", role="primary", result="ok"),
        ],
        parent=app._tk_root,
    )
    seen = {}

    def check(top):
        seen["focused"] = top.focus_lastfor()
        seen["buttons"] = [
            _footer_widget(dialog, "OK"), _footer_widget(dialog, "Cancel"),
        ]

    _drive(dialog, app, check)

    assert seen["focused"] not in seen["buttons"], (
        "a dialog with no default button focused one anyway"
    )


def test_date_dialog_focuses_its_default_button(app):
    """`DateDialog` overrides `show()` wholesale rather than extending it.

    That override duplicates the whole build sequence, so it does not inherit
    the initial-focus resolution — `ask_date()` would keep opening with nothing
    focused while every other dialog was fixed. This is the test that catches
    the duplicate drifting apart again.
    """
    from datetime import date

    from bootstack.dialogs._impl.datedialog import DateDialog

    # Range mode, because single mode has NO footer at all — it commits the
    # moment the second date is clicked, so there is no default button to
    # focus and nothing for this test to be about.
    picker = DateDialog(
        master=app._tk_root, selection_mode="range",
        start_date=date(2026, 3, 2), end_date=date(2026, 3, 5),
    )
    dialog = picker._dialog
    seen = {}

    def check(top):
        default_spec = next(s for s in dialog._buttons if s.default)
        seen["button"] = _footer_widget(dialog, default_spec.text)
        seen["focused"] = top.focus_lastfor()

    _drive(dialog, app, check, show=picker.show)

    assert seen["focused"] is seen["button"], (
        f"the date dialog opened with focus on {seen['focused']} rather than "
        f"its default button"
    )


def test_query_dialog_focuses_its_entry_not_the_default_button(app):
    """Content initial focus beats the default button.

    `ask_string()` is unusable otherwise: the user cannot type, and Space on
    the focused OK button submits an empty value. This is the regression that
    fixing #439 would have introduced had `Dialog` simply focused the button.
    """
    from bootstack.dialogs._impl.query import QueryDialog

    query = QueryDialog("Name:", master=app._tk_root)
    dialog = query._dialog
    seen = {}

    def check(top):
        entry = query._entry_widget
        target = getattr(entry, "entry_widget", entry)
        seen["focused"] = str(top.focus_lastfor())
        seen["entry"] = str(target)
        # By spec flag, not by label: the button texts are localized.
        default_spec = next(s for s in dialog._buttons if s.default)
        seen["ok"] = str(_footer_widget(dialog, default_spec.text))

    _drive(dialog, app, check)

    assert seen["focused"] == seen["entry"], (
        f"focus went to {seen['focused']} rather than the entry "
        f"{seen['entry']} — the default button ({seen['ok']}) stole it"
    )
