"""#407 — does the shared-root scene reset reach what a test actually builds?

Two arms, and the second one RECORDS A REFUTED HYPOTHESIS rather than a fix.

  arm 1  the defect and the fix, side by side in one process
  arm 2  a hypothesis that was WRONG: that destroying a content widget leaks a
         queued event into the next test

Run:  py -3.12 development/probe_407_scene_reset.py

Output is ASCII only (this box's console is cp1252).
"""
from __future__ import annotations

import sys

sys.path.insert(0, "tests")

import bootstack as bs  # noqa: E402
from conftest import _region, _snapshot, _reset_scene  # noqa: E402


def _old_region(app):
    """The expression that shipped before the fix, kept as the control arm."""
    return getattr(app, "_region_root", app._tk_root)


def arm1(app) -> None:
    """The defect: the reset never looked inside `_content_frame`."""
    root = app._tk_root
    print("ARM 1  which container does the reset walk?")
    print(f"  old expression -> {_old_region(app)}")
    print(f"  new expression -> {_region(app)}")
    print(f"  root           -> {root}")
    print(f"  _content_frame -> {app._content_frame}")

    keep = _snapshot(app)
    with app:
        for i in range(5):
            bs.Label(f"leftover {i}")

    content = app._content_frame
    made = [str(w) for w in content.winfo_children()]

    # What the OLD walk could see: root children plus old-region children --
    # which are the same set, so `_content_frame` itself and nothing under it.
    old_reachable = {str(w) for w in root.winfo_children()}
    old_reachable |= {str(w) for w in _old_region(app).winfo_children()}
    visible_old = len([p for p in made if p in old_reachable])

    before = len(content.winfo_children())
    _reset_scene(app, keep)
    after = len(content.winfo_children())

    print(f"\n  test-created widgets: {len(made)}")
    print(f"  visible to the OLD walk: {visible_old} of {len(made)}")
    print(f"  content children: {before} before reset, {after} after")
    verdict = "reset REACHES them" if after == 0 else f"{after} SURVIVED"
    print(f"  VERDICT: {verdict}")
    print("  EXPECTED: 0 of 5 visible to the old walk, 5 -> 0 with the fix.")


def arm2(app) -> None:
    """REFUTED. Kept because a wrong hypothesis with a control is worth more
    than a deleted one.

    The `_region()` fix made the reset destroy content widgets for the first
    time, and `test_select_change_event_value_space` then failed once in about
    ten full runs with `[None, 's'] == ['s']` -- a phantom change event ahead
    of the test's own. The hypothesis was that destroying a `Select` leaves its
    `<<Change>>` QUEUED (`SelectBox` emits with `when="tail"`), to be delivered
    inside the next test, and that the reset therefore needed a drain.

    It does not. Neither arm below leaks anything, so the drain was removed
    again. The failure is a pre-existing fragility in that test -- it asserts an
    exact list against an event stream, which the sibling
    `test_selectbutton_change_event_value_space` already documents as emitting
    more than once per set, and handles by asserting set membership instead.
    """
    root = app._tk_root
    print("\nARM 2  does a destroyed widget leak a queued event? (REFUTED)")

    def run(drain: bool) -> int:
        seen: list[int] = []
        root.bind_all("<<Change>>", lambda e: seen.append(1), add="+")
        keep = _snapshot(app)
        with app:
            sel = bs.Select(options=["a", "b"], value="a")
        root.update()
        seen.clear()

        sel.value = "b"
        _reset_scene(app, keep)
        if drain:
            root.update()

        seen.clear()
        root.update()  # stands in for the NEXT test running
        leaked = len(seen)
        root.unbind_all("<<Change>>")
        return leaked

    no_drain = run(drain=False)
    with_drain = run(drain=True)
    print(f"  no drain -> leaked into next test: {no_drain}")
    print(f"  drain    -> leaked into next test: {with_drain}")
    if no_drain == 0:
        print("  VERDICT: NO leak. The drain is NOT justified -- and was removed.")
    else:
        print("  VERDICT: a leak reproduced; re-open the question.")
    print("  EXPECTED: 0 and 0. A non-zero first column would reverse this.")


def main() -> int:
    app = bs.App(title="probe 407 scene reset")
    app._tk_root.update()
    try:
        arm1(app)
        arm2(app)
    finally:
        app._tk_root.destroy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
