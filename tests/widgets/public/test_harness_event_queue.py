"""#449 -- the shared-root harness must not leak a queued event between tests.

A virtual event generated with `when="tail"` is queued against the emitting
WINDOW, not against the Python widget object. `SelectBox.value` emits one on
every committed change (`selectbox.py:1213`) and about twenty other composites do
the same. If the scene reset destroys that widget while its event is still
queued, the toolkit is free to deliver the event to whatever window it hands out
next -- a widget the NEXT test built.

That is measured, not theorised. Instrumenting a full shared-root leg caught both
ends: the event that failed `test_select_change_event_value_space` was
byte-for-byte the one `test_select_options_reassignment_reconciles` emitted two
tests earlier -- `(value=None, prev_value='Small', text='')` -- arriving at a
different `Select`'s handler.

Rate over the shared-root leg, three arms interleaved, five rounds each:

    no pump in _reset_scene    4 / 5 runs fail
    update_idletasks()         0 / 5
    update()                   0 / 5

WARNING: both pumps silence the flake and only ONE of them is a fix.
`update_idletasks()` does not service queued window events at all -- measured in
`development/probe_449_queued_event_after_destroy.py` -- so it silences the flake
by shifting timing, which is exactly how instrumenting the leg also silenced it.
A rate is therefore NOT sufficient evidence here. This test asserts the invariant
instead: the reset has to actually DELIVER what was queued.
"""
import sys


def _conftest():
    """The harness conftest module.

    Looked up through `sys.modules` rather than imported by name: pytest
    registers a conftest under a path-derived module name that depends on rootdir
    and import mode, so a hardcoded import is the fragile spelling, not this one.
    """
    for name, mod in list(sys.modules.items()):
        if name.rsplit(".", 1)[-1] == "conftest" and hasattr(mod, "_reset_scene"):
            return mod
    raise AssertionError("the harness conftest is not reachable from sys.modules")


def test_scene_reset_delivers_events_queued_with_when_tail(app):
    conftest = _conftest()
    root = app._tk_root
    delivered = []

    # Bound on the ROOT, which the reset never destroys -- so a failure here
    # means the event was left sitting in the queue, not that the binding went
    # away along with its widget.
    funcid = root.bind("<<Bs449Probe>>", lambda e: delivered.append(True), add="+")
    try:
        root.event_generate("<<Bs449Probe>>", when="tail")

        # Precondition. Without it this test would pass vacuously on a build
        # where `when="tail"` had become synchronous, while asserting nothing
        # whatsoever about the scene reset.
        assert delivered == [], (
            "precondition failed: a when='tail' event arrived synchronously, so "
            "this test cannot say anything about the scene reset"
        )

        conftest._reset_scene(app, conftest._snapshot(app))

        assert delivered == [True], (
            "the scene reset returned with a queued virtual event still pending "
            "(#449). It has to pump the event loop -- and update_idletasks() "
            "does not service queued window events, so it is not enough"
        )
    finally:
        root.unbind("<<Bs449Probe>>", funcid)
