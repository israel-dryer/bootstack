"""Regression tests for reporting an unbind that matches nothing (#399).

`_patched_unbind` deliberately deletes nothing when the funcid it was handed is
not present in that widget's binding script. That guard is correct — deleting a
command you did not unbind orphans whatever is still bound to it, which is what
made #397 dangerous — but it converts the case into an unbounded, invisible
leak: the Tcl command and the closure behind it survive for the life of the
interpreter.

It cannot safely be made to delete, so it is made to *speak* instead, under
`BOOTSTACK_DEBUG`.

It speaks by printing, not by warning. This code runs inside event dispatch and
on the teardown path behind `Subscription.cancel()` and its `__exit__`, both
documented as safe on an already-removed handler — and a `warnings.warn` there
becomes an exception out of both under `-W error`. That was measured, not
inferred: `cancel()` raised `RuntimeWarning` and left `cancelled` reading False.
Breaking teardown is a worse outcome than the leak the message describes.
"""
from __future__ import annotations

import warnings


def test_unmatched_unbind_reports_under_debug(app, monkeypatch, capsys):
    monkeypatch.setenv("BOOTSTACK_DEBUG", "1")
    widget = app._tk_root
    bind_id = widget.bind("<<Probe399>>", lambda e: None, add="+")
    # A wholesale removal clears the script without deleting the commands, so
    # the per-funcid removal that follows finds nothing to match.
    widget.unbind("<<Probe399>>")

    widget.unbind("<<Probe399>>", bind_id)

    assert "matched no binding" in capsys.readouterr().out


def test_unmatched_unbind_is_silent_without_debug(app, monkeypatch, capsys):
    monkeypatch.delenv("BOOTSTACK_DEBUG", raising=False)
    widget = app._tk_root
    bind_id = widget.bind("<<Probe399b>>", lambda e: None, add="+")
    widget.unbind("<<Probe399b>>")

    widget.unbind("<<Probe399b>>", bind_id)

    assert capsys.readouterr().out == ""


def test_the_report_cannot_break_teardown_under_error_filters(app, monkeypatch):
    """The diagnostic must not be able to fail a documented-safe teardown.

    `cancel()` and `__exit__` are both documented as safe to call on a handler
    that is already gone, and both reach the unmatched path. A warning here
    would escape them whenever the caller runs under `-W error`.
    """
    import bootstack as bs

    monkeypatch.setenv("BOOTSTACK_DEBUG", "1")

    for use_context_manager in (False, True):
        field = bs.TextField()
        sub = field.on_change(lambda e: None)
        # Strand the funcid: the script is cleared, so the removal below has
        # nothing to match.
        field._event_target("<<Change>>").unbind("<<Change>>")

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            if use_context_manager:
                with sub:
                    pass
            else:
                sub.cancel()

        assert sub.cancelled is True
