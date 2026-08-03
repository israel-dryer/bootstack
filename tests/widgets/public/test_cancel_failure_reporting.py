"""Regression tests for a cancellation that claims success it did not achieve (#400).

`Subscription.cancel()` swallowed `TclError` and set `_cancelled = True`
regardless, so `sub.cancelled` read `True` for a subscription that was still
delivering events. Swallowing is right — teardown should not fail on an
already-dead widget — but reporting it as cancelled is a silent wrong answer.

The collaborator is stubbed so the failure is *behavioral*: a test that merely
provoked a real `TclError` would prove only that the widget was gone.
"""
from __future__ import annotations

import tkinter

from bootstack.events import Subscription


def test_cancel_does_not_mark_cancelled_when_the_unbind_fails():
    class _Failing:
        def unbind(self, sequence, funcid=None):
            raise tkinter.TclError("boom")

    sub = Subscription(_Failing(), "<<Change>>", "fid1")
    sub.cancel()

    assert sub.cancelled is False


def test_cancel_marks_cancelled_on_success():
    class _Ok:
        def __init__(self):
            self.calls = []

        def unbind(self, sequence, funcid=None):
            self.calls.append((sequence, funcid))

    widget = _Ok()
    sub = Subscription(widget, "<<Change>>", "fid1")
    sub.cancel()

    assert sub.cancelled is True
    assert widget.calls == [("<<Change>>", "fid1")]

    sub.cancel()  # idempotent
    assert widget.calls == [("<<Change>>", "fid1")]


def test_cancel_marks_cancelled_when_the_binding_was_already_gone(app):
    """The other half of the invariant, and the one that reads as a contradiction.

    A removal that matches nothing does not raise — `_patched_unbind` returns
    quietly, having deliberately declined to delete a command it cannot prove is
    ours (#399). So `cancel()` falls through and marks the subscription
    cancelled for a removal that took nothing out of the script.

    That is the right answer rather than a hole in the one above, and this test
    pins both halves of why: the handler really is unreachable afterwards, and
    no later `cancel()` could ever match, so anything other than `cancelled`
    would be permanently wrong. The case where the handler is genuinely still
    live is the failed-rewrite path above, which does raise.
    """
    import bootstack as bs
    from bootstack.events import ChangeEvent

    field = bs.TextField()
    seen: list = []
    sub = field.on_change(lambda e: seen.append(e.value))
    app._tk_root.update_idletasks()

    # A wholesale removal clears the script without deleting the commands, so
    # the per-funcid removal inside cancel() finds nothing to match.
    field._event_target("<<Change>>").unbind("<<Change>>")

    field.emit("change", data=ChangeEvent(value="before"))
    app._tk_root.update()
    assert seen == [], "precondition: the handler must already be unreachable"

    sub.cancel()

    assert sub.cancelled is True
    field.emit("change", data=ChangeEvent(value="after"))
    app._tk_root.update()
    assert seen == []
