"""Regression tests for the dialog result helpers recomputing their target (#397).

Four internal dialog helpers paired an `on_*` binder with an `off_*` unbinder,
and each side worked out the widget to act on rather than remembering it.
`Dialog._toplevel` is `None` until `show()`, so subscribing before and
unsubscribing after resolved to two different widgets and the removal quietly
matched nothing.

The fix is to stop passing bare funcids around: a `Subscription` already carries
the right triple (widget, sequence, bind id), so the target cannot drift, and it
matches the framework's own idiom instead of a bespoke `on_*`/`off_*` pair.
"""
from __future__ import annotations

from bootstack.events import Subscription


def test_dialog_on_result_returns_a_subscription(app):
    from bootstack.dialogs._impl.message import MessageDialog

    dialog = MessageDialog("hi", master=app._tk_root)
    sub = dialog.on_dialog_result(lambda payload: None)

    assert isinstance(sub, Subscription)
    assert str(sub._widget) == str(app._tk_root)


def test_dialog_subscription_survives_the_show_boundary(app):
    """Cancelling must target the bind-time widget, not a later-resolved one."""
    from bootstack.dialogs._impl.message import MessageDialog

    dialog = MessageDialog("hi", master=app._tk_root)
    seen = []
    sub = dialog.on_dialog_result(lambda payload: seen.append(payload))
    app._tk_root.update_idletasks()

    app._tk_root.event_generate("<<DialogResult>>", data={"result": "a"})
    app._tk_root.update()
    assert len(seen) == 1, "precondition: the handler is live before cancelling"

    sub.cancel()
    app._tk_root.update()

    app._tk_root.event_generate("<<DialogResult>>", data={"result": "b"})
    app._tk_root.update()
    assert len(seen) == 1, "handler still fired after cancel()"


# --- delivery: the target must still be alive when the result fires ---------
#
# The two tests above generate `<<DialogResult>>` by hand, which is why they
# passed while delivery was broken end to end. Nothing reset `Dialog._toplevel`
# when the modal wait ended, so `toplevel or master` resolved to a *destroyed*
# widget after `show()` returned; `event_generate` raised and a bare
# `except Exception: pass` swallowed it. The callback never ran.


def test_result_reaches_a_subscriber_once_the_toplevel_is_gone(app):
    """The post-show state, without the modal loop.

    Deliberately asserts on delivery rather than on which widget was chosen:
    a test that imported the new target helper would fail pre-fix with
    `ImportError`, which only proves the helper is new.
    """
    from datetime import date

    from bootstack.dialogs._impl.datedialog import DateDialog

    root = app._tk_root
    dialog = DateDialog(master=root)
    seen: list = []
    dialog.on_result(lambda payload: seen.append(payload))

    dialog._dialog._create_toplevel()
    top = dialog._dialog.toplevel
    top.destroy()
    root.update_idletasks()

    assert dialog._dialog.toplevel is not None, (
        "precondition: nothing clears _toplevel, so it is still a dead handle"
    )
    assert not top.winfo_exists(), "precondition: that handle is destroyed"

    picked = date(2026, 8, 3)
    dialog._emit_result(picked, True)
    root.update()

    assert seen == [{"result": picked, "confirmed": True}]


def test_show_delivers_the_result_to_a_presubscribed_handler(shown_app):
    """End to end through the real modal `show()`, dismissed on a timer."""
    import tkinter

    from bootstack.dialogs._impl.message import MessageDialog

    root = shown_app._tk_root
    seen: list = []

    dialog = MessageDialog("hi", master=root, buttons=["OK"])
    dialog.on_dialog_result(lambda payload: seen.append(payload))

    def live_toplevel():
        for child in root.winfo_children():
            if isinstance(child, tkinter.Toplevel) and child.winfo_exists():
                return child
        return None

    pending: list[str] = []

    def dismiss(attempt=0):
        """Press the dialog's button, once the dialog is really on screen.

        Polls rather than firing on a fixed delay: `show()` creates the
        toplevel well before it positions and maps it, and a timer that lands
        inside that window destroys a half-built dialog. That is load-bearing
        under the shared-root suite, where the run is slow enough to hit it.
        """
        top = live_toplevel()
        if top is None or not top.winfo_ismapped():
            if attempt < 100:
                pending.append(root.after(50, lambda: dismiss(attempt + 1)))
            return
        stack = [top]
        while stack:
            w = stack.pop()
            stack.extend(w.winfo_children())
            if "button" in w.winfo_class().lower():
                w.invoke()
                return

    def force_close():
        """Hard fallback so a missed button cannot hang the suite."""
        top = live_toplevel()
        if top is not None:
            top.destroy()

    pending.append(root.after(50, dismiss))
    pending.append(root.after(10000, force_close))
    try:
        dialog.show()
        root.update()
    finally:
        # The root outlives this test, so a timer left queued here fires during
        # a LATER one — and force_close destroys any live Toplevel it finds,
        # while a stale dismiss presses any button it finds. Measured: without
        # this, force_close is still pending when the test ends and destroys an
        # unrelated Toplevel ~10s later. Leaked deferred cleanup on a shared
        # root is the very class this cluster exists to fix.
        for job in pending:
            root.after_cancel(job)

    assert dialog.result == "OK", "precondition: the dialog was dismissed by its button"
    assert seen == [{"result": "OK", "confirmed": True}]
