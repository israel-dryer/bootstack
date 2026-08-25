"""#465 review round 1 — what value kind does a `Select` actually hand a rule?

The branch makes `Select` inherit `FieldAddonMixin`, which brings
`_VALIDATION_KIND = "text"` and with it a gate that rejects a `range` rule at
attach time. PLAN.md justifies shipping that gate in a minor rather than in the
`0.5.0` strictness batch on the ground that a `range` rule on a `Select` "can
never pass today", so the migration count is zero.

This probe measures that claim on BOTH sides of the fix.

    py -3.12 development/probe_465_select_range_kind.py

    # and against the pre-fix source, from a worktree at main:
    PYTHONPATH=<worktree>/src py -3.12 development/probe_465_select_range_kind.py

The distinction the original measurement missed is DECOUPLING.
`SelectBox._validation_value` (selectbox.py:384) maps the displayed text back to
the option's value only when the two differ. A probe built on
`Select(["1", "7", "12"], value="7")` has text == value, so it never reaches the
decode and always sees a `str` — which is what "can never pass" was read off.
Give the options distinct labels and the rule receives the option's real Python
object, so `range` works.

Output is ASCII only (the Windows console is cp1252).
"""
import datetime as dt

import bootstack as bs


def _provenance() -> None:
    import os
    print("bootstack loaded from:", os.path.dirname(bs.__file__))
    print()


def _arm(app, label, options, value, lo, hi):
    """Report the value kind handed to a rule, and whether `range` lo..hi holds."""
    seen = {}
    probe = bs.Select(options, value=value, parent=app)
    app._tk_root.update_idletasks()
    probe.add_validation_rule("custom", func=lambda v: seen.setdefault("v", v) or True)
    probe.validate()
    handed = seen.get("v", "<rule never ran>")

    subject = bs.Select(options, value=value, parent=app)
    app._tk_root.update_idletasks()
    try:
        subject.add_validation_rule("range", min=lo, max=hi)
    except Exception as exc:
        verdict = "REJECTED at attach: %s" % type(exc).__name__
    else:
        verdict = "range passes = %s" % subject.validate()
    print("  %-38s handed=%-12r (%-4s)  %s"
          % (label, handed, type(handed).__name__, verdict))


def main() -> None:
    _provenance()
    app = bs.App(title="probe-465")
    with app:
        pass

    print("A rule sees the option's VALUE. Coupled options (text == value) can")
    print("only ever hand it text; decoupled ones hand it the real object.")
    print()
    _arm(app, "plain str options, value '7'", ["1", "7", "12"], "7", 5, 10)
    _arm(app, "decoupled str ('Seven', '7')", [("Seven", "7")], "7", 5, 10)
    _arm(app, "decoupled int, in range (7)",
         [("One", 1), ("Seven", 7), ("Twelve", 12)], 7, 5, 10)
    _arm(app, "decoupled int, out of range (12)",
         [("One", 1), ("Seven", 7), ("Twelve", 12)], 12, 5, 10)
    _arm(app, "dict options, int value", [{"text": "Seven", "value": 7}], 7, 5, 10)

    d1, d2, d3 = dt.date(2024, 1, 1), dt.date(2024, 6, 1), dt.date(2024, 12, 1)
    _arm(app, "decoupled date, in range", [("Jan", d1), ("Jun", d2), ("Dec", d3)],
         d2, d1, dt.date(2024, 8, 1))
    _arm(app, "decoupled date, out of range", [("Jan", d1), ("Jun", d2), ("Dec", d3)],
         d3, d1, dt.date(2024, 8, 1))

    print()
    print("READING: a row that reports 'range passes = True' for an in-range value")
    print("and 'False' for an out-of-range one is a WORKING range rule. If those")
    print("rows say 'REJECTED at attach', the gate broke code that worked.")
    print()
    print("Measured 2026-08-21, Windows box, py -3.12, three states:")
    print("  main (9a910235)          int and date rows -> True / False.")
    print("                           The rule works. Nothing is rejected.")
    print("  branch at fadedf9d       EVERY row -> REJECTED at attach. This is")
    print("                           the review's F1: a working rule now raises")
    print("                           at construction, so a running app breaks.")
    print("  branch after the fix     identical to main, row for row.")


if __name__ == "__main__":
    main()
