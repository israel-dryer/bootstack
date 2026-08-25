"""#461 / #459 baseline -- what space does a `SelectButton` signal live in, and
who emits a change event while seeding?

    py -3.12 development/probe_461_selectbutton_signal_space.py

Two questions, measured by construction rather than read off the wiring.

ARM 1 (#461) `SelectButton` maps public `signal=` onto the internal
`textsignal=`, which backs `_textvariable` -- and that variable holds the
option's TEXT, not its value. So the signal is label-space while `value=`,
`.value` and the `<<Change>>` payload are all value-space.

ARM 2 (#459) Binding through `ValueSignalMixin` seeds by assigning `.value`.
A widget whose value setter emits therefore raises `<<Change>>` during
construction, for a selection the user never made. The `value=` door is the
control: it seeds the same field and stays quiet.

ARM 3 asks ARM 2's question of `SelectButton` as it stands today, so the fix
knows whether it must carry `Select`'s seed suppression across.

Output is ASCII only (the Windows console is cp1252).
"""
import datetime as dt
import os

import bootstack as bs

OPTIONS = [("One", "1"), ("Two", "2"), ("Three", "3")]


def _provenance() -> None:
    print("bootstack loaded from:", os.path.dirname(bs.__file__))
    print()


def _pump(app) -> None:
    """Turn the event loop. `update_idletasks` does NOT drain queued events."""
    app._tk_root.update()


def _row(label, sb, sig, seeded_with=None):
    same = (sb.signal is sig) if sig is not None else "-"
    print("  %-34s text=%-7r value=%-5r selection=%-8s signal=%-7r is-same-object=%s"
          % (label, sb.text, sb.value,
             (sb.selection or {}).get("value", None) if sb.selection else None,
             sig() if sig is not None else None, same))


def _build(app, label, make, sig=None):
    """Build a button, reporting a raise as a row rather than ending the run.

    Either arm can legitimately raise depending on which side of the fix this
    is measuring, and the arms below must still run.
    """
    try:
        sb = make()
    except Exception as exc:
        print("  %-34s RAISED %s: %s" % (label, type(exc).__name__, exc))
        return None
    _pump(app)
    _row(label, sb, sig)
    return sb


def arm1(app) -> None:
    print("ARM 1 -- #461: which space does SelectButton's signal speak?")
    print("  options %r" % (OPTIONS,))

    sig_label = bs.Signal("Two")
    _build(app, "signal seeded with LABEL 'Two'",
           lambda: bs.SelectButton(OPTIONS, signal=sig_label, parent=app), sig_label)

    sig_value = bs.Signal("2")
    sb2 = _build(app, "signal seeded with VALUE '2'",
                 lambda: bs.SelectButton(OPTIONS, signal=sig_value, parent=app), sig_value)

    _build(app, "value='Two' (label, control)",
           lambda: bs.SelectButton(OPTIONS, value="Two", parent=app))
    _build(app, "value='2'   (value, control)",
           lambda: bs.SelectButton(OPTIONS, value="2", parent=app))

    print()
    print("  write-back: on whichever button seeded, assign .value = '3'")
    sb = sb2 if sb2 is not None else None
    sig = sig_value if sb2 is not None else None
    if sb is not None:
        sb.value = "3"
        _pump(app)
        _row("after sb.value = '3'", sb, sig)
    print()


def _seed_emit(app, label, build):
    """Build a widget, bind a handler on the NEXT line, and pump the loop."""
    seen = []
    try:
        w = build()
    except Exception as exc:
        print("  %-42s RAISED %s: %s" % (label, type(exc).__name__, exc))
        return
    w.on_change(lambda e: seen.append(getattr(e, "value", e)))
    _pump(app)
    print("  %-42s change events after construction: %r" % (label, seen))


def arm2(app) -> None:
    print("ARM 2 -- #459: does seeding a signal emit a change event?")
    t = dt.time(9, 0)
    _seed_emit(app, "TimeField(signal=Signal(time(9,0)))",
               lambda: bs.TimeField(signal=bs.Signal(t), parent=app))
    _seed_emit(app, "TimeField(value=time(9,0))   control",
               lambda: bs.TimeField(value=t, parent=app))
    _seed_emit(app, "NumberField(signal=Signal(5))  sibling",
               lambda: bs.NumberField(signal=bs.Signal(5), parent=app))
    _seed_emit(app, "DateField(signal=Signal(date))  sibling",
               lambda: bs.DateField(signal=bs.Signal(dt.date(2026, 1, 1)), parent=app))
    _seed_emit(app, "Select(signal=Signal('2'))   fixed by #458",
               lambda: bs.Select(OPTIONS, signal=bs.Signal("2"), parent=app))
    print()


def arm3(app) -> None:
    print("ARM 3 -- does a SelectButton seed emit a change event?")
    # Seeded in whichever space the build under measurement speaks, so the row
    # reports an emit rather than a raise on both sides of the fix.
    _seed_emit(app, "SelectButton(signal=Signal('2'))  value",
               lambda: bs.SelectButton(OPTIONS, signal=bs.Signal("2"), parent=app))
    _seed_emit(app, "SelectButton(signal=Signal('Two')) label",
               lambda: bs.SelectButton(OPTIONS, signal=bs.Signal("Two"), parent=app))
    _seed_emit(app, "SelectButton(value='2')      control",
               lambda: bs.SelectButton(OPTIONS, value="2", parent=app))
    print()


def main() -> None:
    _provenance()
    app = bs.App(title="probe-461")
    with app:
        pass

    arm1(app)
    arm2(app)
    arm3(app)

    print("READING")
    print("  ARM 1: the LABEL row selecting an option while the VALUE row leaves")
    print("         selection=None is the #461 defect. A fixed build inverts it:")
    print("         VALUE selects, LABEL raises ValueError (matching the value=")
    print("         door, which raises on an off-list value today).")
    print("  ARM 2: a non-empty list on the TimeField signal row, beside an empty")
    print("         one on its own value= control, is #459.")
    print("  ARM 3: whether the #461 fix must carry Select's seed suppression.")
    print("         OptionMenu emits from a textsignal subscription with the")
    print("         default when='now', so the answer is not obvious from the")
    print("         Select precedent -- measure it, do not infer it.")


if __name__ == "__main__":
    main()
