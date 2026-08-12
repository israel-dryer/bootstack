"""Who gets the Enter key inside a dialog.

A dialog binds Return/KP_Enter on its TOPLEVEL so the default button can be
pressed from an input field — that is what makes `ask_string()` finish on
Enter. The toplevel is last in the bindtag walk, so that binding has to stand
down when something already answered the key, or it fires the default button on
top of whatever just happened.

#437 added that stand-down for buttons. It recognized ONLY buttons, by testing
for the `TButton` bindtag, so a `TextArea` — which answers Enter by inserting a
newline — got the newline AND the dialog closed on top of it (#441). The user
is typing a paragraph and the dialog closes under them.

The rule is now "who treats THIS Enter key as content", by bindtag and keysym:
`TButton` invokes for both Enter keys, `Text` inserts for the main one only —
Tk binds its keypad twin to a no-op script. A disabled widget of either kind
answers nothing. In every "nothing answered" case the default button still gets
the key, rather than it dying in the widget.

⚠ Interrogating the BINDINGS rather than the class was tried and is wrong; the
docstring on `_key_was_consumed` records why, and
`development/probe_441_key_already_handled.py` measures it. The short version:
bootstack's own `TextField` binds `<Return>` to emit its `submit` event, so
"has a real binding for the key" is true for the widget that must keep
submitting.
"""
from __future__ import annotations

import tkinter

import pytest

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton
from bootstack.dialogs._impl.dialog import _key_was_consumed

pytestmark = pytest.mark.gui


# ---------------------------------------------------------------------------
# The rule itself — no dialog needed
# ---------------------------------------------------------------------------

def test_an_enabled_button_consumed_the_key(app):
    from bootstack.widgets._impl.primitives.button import Button as _Button

    button = _Button(app._tk_root, text="OK")
    try:
        assert _key_was_consumed(button, "Return") is True
    finally:
        button.destroy()


def test_a_disabled_button_did_not(app):
    """Its class binding runs but `invoke` does nothing, so nothing answered."""
    from bootstack.widgets._impl.primitives.button import Button as _Button

    button = _Button(app._tk_root, text="OK", state="disabled")
    try:
        assert _key_was_consumed(button, "Return") is False
    finally:
        button.destroy()


def test_an_editable_text_consumed_the_key(app):
    """#441 — Enter is a newline here, not a command."""
    text = tkinter.Text(app._tk_root, height=2)
    try:
        assert _key_was_consumed(text, "Return") is True
    finally:
        text.destroy()


def test_a_disabled_text_did_not(app):
    """`tk::TextInsert` returns early on a disabled text — nothing answered."""
    text = tkinter.Text(app._tk_root, height=2, state="disabled")
    try:
        assert _key_was_consumed(text, "Return") is False
    finally:
        text.destroy()


# ---------------------------------------------------------------------------
# The KEY half of the rule — a text widget answers only one of the two
# ---------------------------------------------------------------------------

def test_tk_binds_the_two_enter_keys_differently_on_a_text(app):
    """The PRECONDITION the scoping rests on — measured, not assumed.

    If Tk ever gives `Text <KP_Enter>` a real script, the stand-down below
    becomes wrong and this test says so first, naming the reason, rather than
    leaving the two behavioral tests to fail for an unexplained cause.
    """
    root = app._tk_root
    assert "TextInsert" in root.tk.call("bind", "Text", "<Key-Return>")
    assert root.tk.call("bind", "Text", "<Key-KP_Enter>").strip() == "# nothing"


def test_a_button_consumed_the_keypad_key_too(app):
    """A button is symmetric — bootstack binds BOTH keys to invoke."""
    from bootstack.widgets._impl.primitives.button import Button as _Button

    button = _Button(app._tk_root, text="OK")
    try:
        assert _key_was_consumed(button, "KP_Enter") is True
    finally:
        button.destroy()


def test_an_editable_text_did_not_consume_the_keypad_key(app):
    """A text widget is NOT symmetric, so the keypad key must stay alive.

    `Text <KP_Enter>` is the literal script `# nothing`, so nothing was
    inserted. Reporting it consumed would leave the keypad Enter dead for the
    whole dialog: it would neither type a newline nor press the default button.

    ⚠ NOT REACHABLE ON WINDOWS by either route — the platform folds the keypad
    key into `Return` (so `keysym` is never `KP_Enter`) and `event_generate`
    cannot synthesize it (keysym `??`, keycode 0, matching no binding). Both
    measured in `development/probe_441_kp_enter_platform.py`. This test drives
    the rule directly for exactly that reason; an end-to-end arm would pass
    vacuously here and could only ever run on X11.
    """
    text = tkinter.Text(app._tk_root, height=2)
    try:
        assert _key_was_consumed(text, "KP_Enter") is False
        # The control: the same widget, the other key, still consumed — so the
        # assertion above cannot pass merely because the widget went unread.
        assert _key_was_consumed(text, "Return") is True
    finally:
        text.destroy()


def test_an_unrecognized_keysym_leaves_a_text_widget_consuming(app):
    """The conservative side of the branch, pinned so it is not "simplified".

    The test is `keysym != "KP_Enter"`, not `keysym == "Return"`. Standing down
    wrongly costs a dead key; firing wrongly costs #441 itself — the dialog
    closing on top of a newline the user just typed. For a text widget the
    second is the worse failure, so an unknown key reads as consumed.
    """
    text = tkinter.Text(app._tk_root, height=2)
    try:
        assert _key_was_consumed(text, "Linefeed") is True
    finally:
        text.destroy()


def _descend(widget, klass):
    """The first descendant of Tk class `klass`, or None.

    ⚠ Needed because the public wrapper is NOT the widget the key reaches:
    `bs.TextField(...).tk` is the composite `TFrame`, four levels above the
    `TEntry`. Asserting on the wrapper would pass for the wrong reason — a
    TFrame is neither a button nor a text, so every rule says "not consumed"
    about it. Key events go to the FOCUS widget, which is the inner one.
    """
    if widget.winfo_class() == klass:
        return widget
    for child in widget.winfo_children():
        found = _descend(child, klass)
        if found is not None:
            return found
    return None


def test_an_entry_did_not(app):
    """The CONTROL, and the case the toplevel binding exists to serve.

    If this ever reads True, Enter stops submitting from a text field and
    `ask_string()` can no longer be finished from the keyboard.
    """
    field = bs.TextField(parent=app._tk_root)
    try:
        entry = _descend(field._internal, "TEntry")
        assert entry is not None, "precondition: found the inner TEntry"
        assert _key_was_consumed(entry, "Return") is False
    finally:
        field.destroy()


def test_a_widget_that_cannot_report_bindtags_does_not_swallow_the_key(app):
    """Degrade toward the default button, never toward a dead keyboard."""

    class Opaque:
        def bindtags(self):
            raise AttributeError("no bindtags here")

    assert _key_was_consumed(Opaque(), "Return") is False


# ---------------------------------------------------------------------------
# End to end, through the real key
# ---------------------------------------------------------------------------

def _drive(dialog, app, action, also_ready=None):
    """Show `dialog`; run `action()` once it is really up.

    Polls for the modal grab AND the footer being mapped: `show()` pumps the
    event loop while building and positioning, so a fixed delay can land on a
    half-built dialog, and the grab is set before the geometry manager maps the
    footer's children at idle.

    ⚠ The footer is NOT a barrier for the dialog BODY. They are mapped by
    separate geometry passes, so a body widget can still be unmapped when every
    footer button is up — measured, about 2 runs in 5 here. That matters for a
    key test twice over: an unmapped widget cannot take focus, and Tk says
    nothing when `focus_set()` fails on one, so the press lands on the toplevel
    and the dialog closes. That is the symptom of the bug under test, produced
    by the test itself. `also_ready` lets a caller add whatever else has to be
    on screen before it acts.
    """
    root = app._tk_root
    pending: list[str] = []
    failures: list[BaseException] = []

    def ready():
        top = dialog._toplevel
        if top is None or not top.winfo_exists() or top.grab_current() is not top:
            return False
        footer = getattr(dialog, "_footer", None)
        if footer is None or not footer.winfo_exists():
            return False
        children = footer.winfo_children()
        if not (children and all(w.winfo_ismapped() for w in children)):
            return False
        return also_ready is None or also_ready()

    def run(attempt=0):
        if not ready():
            if attempt < 200:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            return
        try:
            action()
        except BaseException as exc:  # noqa: BLE001 - re-raised below
            # Tkinter swallows exceptions raised in a callback; without this
            # the dialog never closes and the suite hangs.
            failures.append(exc)
        finally:
            top = dialog._toplevel
            if top is not None and top.winfo_exists():
                top.destroy()

    pending.append(root.after(50, run))
    pending.append(root.after(10000, lambda: (
        dialog._toplevel.destroy()
        if dialog._toplevel is not None and dialog._toplevel.winfo_exists()
        else None
    )))
    try:
        dialog.show()
    finally:
        # The root outlives this test, so a timer left queued here fires during
        # a LATER one and would destroy an unrelated Toplevel.
        for job in pending:
            root.after_cancel(job)

    if failures:
        raise failures[0]


def _leaf(public):
    """The widget a key press actually reaches inside a composite body.

    The public wrapper is not it: `bs.TextArea(...).tk` is the composite
    `TFrame`, with the `Text` four levels down.
    """
    return (_descend(public._internal, "Text")
            or _descend(public._internal, "TEntry")
            or public.tk)


def _enter_in(app, factory):
    """Open a dialog whose body is `factory()`, press Enter in it, report."""
    holder: dict = {}
    calls: list[str] = []

    def build():
        holder["widget"] = factory()

    def on_ok(_dialog):
        # Read while the content is alive — after the dialog closes the widget
        # is destroyed and the text is unreachable either way.
        calls.append("ok")

    dialog = Dialog(
        title="enter",
        content_builder=build,
        buttons=[DialogButton(text="OK", role="primary", result="ok",
                              default=True, command=on_ok)],
        parent=app._tk_root,
    )

    def act():
        public = holder["widget"]
        # ⚠ Focus the LEAF, not the public wrapper, and confirm it landed
        # before generating the key. `bs.TextArea(...).tk` is the composite
        # `TFrame`; focusing it delegates inward, and that delegation is not
        # synchronous — so `event_generate` could fire while Tk still reported
        # the toplevel as the focus widget. A key event goes to the FOCUS
        # widget, so the press then reached the toplevel, the default button
        # fired, and the dialog closed: the exact symptom of the bug under
        # test, produced by the test itself. It failed about 2 runs in 5.
        target = _leaf(public)
        assert target.winfo_ismapped(), "precondition: the body widget is mapped"

        target.focus_set()
        top = dialog._toplevel
        for _ in range(100):
            if str(top.tk.call("focus") or "") == str(target):
                break
            top.update()
        assert str(top.tk.call("focus") or "") == str(target), (
            f"precondition: focus is on the body widget, not "
            f"{top.tk.call('focus')!r}"
        )

        holder["before"] = public.value
        target.event_generate("<Return>", when="now")
        top = dialog._toplevel
        holder["closed"] = not top.winfo_exists()
        if not holder["closed"]:
            holder["after"] = public.value

    def body_is_up():
        public = holder.get("widget")
        if public is None:
            return False
        leaf = _leaf(public)
        return leaf is not None and leaf.winfo_ismapped()

    _drive(dialog, app, act, also_ready=body_is_up)
    holder["calls"] = calls
    return holder


def test_enter_in_a_text_area_inserts_a_newline_and_keeps_the_dialog_open(app):
    """#441. The dialog must not close under someone typing a paragraph."""
    seen = _enter_in(app, lambda: bs.TextArea(height=4))

    assert seen["closed"] is False, "the dialog closed on Enter in a TextArea"
    assert seen["calls"] == [], "the default button ran anyway"
    assert seen["after"] == "\n", (
        f"the newline was not inserted: {seen['after']!r}"
    )


def test_enter_in_a_text_field_still_submits(app):
    """The control: an entry does NOT answer Enter, so the dialog submits.

    This is the behavior the toplevel binding exists for. A fix for #441 that
    also silenced this would break `ask_string()`.
    """
    seen = _enter_in(app, lambda: bs.TextField())

    assert seen["closed"] is True, "Enter no longer submits from a text field"
    assert seen["calls"] == ["ok"], "the default button did not run"


def test_enter_in_a_read_only_text_area_still_submits(app):
    """Nothing answered the key there, so the default button should get it.

    `read_only=True` puts the inner `Text` in Tk's `disabled` state, which is
    what `_key_was_consumed` reads — measured, not assumed.
    """
    seen = _enter_in(app, lambda: bs.TextArea(height=4, read_only=True))

    assert seen["closed"] is True, (
        "a disabled TextArea swallowed Enter, leaving the keyboard dead"
    )
    assert seen["calls"] == ["ok"], "the default button did not run"
