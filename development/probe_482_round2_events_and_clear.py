"""#482 round 2 -- does the fix move <<Change>> on a LATER focus/blur cycle, and
does `value` now follow `Signal.clear()`?

Round 1 pinned events at the MOMENT of a programmatic write. `_prev_changed_value`
is snapshotted from `_value` on FocusIn and compared on blur, so re-deriving
`_value` earlier can remove -- or add -- a `<<Change>>` one cycle later.

Run once per arm and diff:

    py -3.12 development/probe_482_round2_events_and_clear.py
    PYTHONPATH=<main-worktree>/src py -3.12 <main-worktree>/development/probe_482_round2_events_and_clear.py

Every arm is independent; one that raises reports and the rest still run.
"""
import os

import bootstack as bs

print("PROVENANCE", os.path.dirname(bs.__file__))

app = bs.App(title="probe482r2")
root = app.tk.winfo_toplevel()
root.geometry("500x400+60+60")
root.deiconify()
root.update()


def arm(label, fn):
    try:
        print("[%s] %s" % (label, fn()))
    except Exception as exc:
        print("[%s] EXC %s: %s" % (label, type(exc).__name__, exc))


def _cycle(entry):
    """Focus the entry, then blur it, with no edit in between."""
    entry.focus_force()
    root.update()
    entry.event_generate("<FocusOut>")
    root.update()


def _watch(field):
    changes = []
    field.on_change(lambda e: changes.append((e.prev_value, e.value)))
    return changes


# --- Q1: <<Change>> on the focus/blur cycle AFTER a programmatic write --------

def q1_write_then_cycle():
    sig = bs.Signal("hello")
    f = bs.TextField(parent=app, textsignal=sig)
    root.update()
    changes = _watch(f)
    sig.set("world")
    root.update()
    at_write = list(changes)
    _cycle(f._internal._entry)
    return "at_write=%r after_cycle=%r value=%r" % (at_write, changes, f.value)


def q1_spinner_write_then_cycle():
    sig = bs.Signal("hello")
    f = bs.SpinnerField(parent=app, textsignal=sig)
    root.update()
    changes = _watch(f)
    sig.set("world")
    root.update()
    at_write = list(changes)
    _cycle(f._internal._entry)
    return "at_write=%r after_cycle=%r value=%r" % (at_write, changes, f.value)


def q1_control_no_write():
    # Control: a focus/blur cycle with nothing written must emit nothing on
    # either arm, so a difference above cannot be the cycle itself.
    sig = bs.Signal("hello")
    f = bs.TextField(parent=app, textsignal=sig)
    root.update()
    changes = _watch(f)
    _cycle(f._internal._entry)
    return "after_cycle=%r value=%r" % (changes, f.value)


def q1_control_typed_edit():
    # Control: a real typed edit must still emit on both arms.
    sig = bs.Signal("hello")
    f = bs.TextField(parent=app, textsignal=sig)
    root.update()
    changes = _watch(f)
    entry = f._internal._entry
    entry.focus_force()
    root.update()
    entry.delete(0, "end")
    entry.insert("end", "typed")
    root.update()
    entry.event_generate("<FocusOut>")
    root.update()
    return "after_cycle=%r value=%r" % (changes, f.value)


def q1_write_then_type_it_back():
    # The mirror: a write moves the display, then the user types the ORIGINAL
    # text back and blurs. Whichever way the snapshot moves, this row and
    # q1_write_then_cycle disagree in opposite directions.
    sig = bs.Signal("hello")
    f = bs.TextField(parent=app, textsignal=sig)
    root.update()
    changes = _watch(f)
    sig.set("world")
    root.update()
    entry = f._internal._entry
    entry.focus_force()
    root.update()
    entry.delete(0, "end")
    entry.insert("end", "hello")
    root.update()
    entry.event_generate("<FocusOut>")
    root.update()
    return "after_cycle=%r value=%r" % (changes, f.value)


# --- Q2: does `value` follow Signal.clear()? ---------------------------------

def q2_clear_value():
    sig = bs.Signal("hello", allow_empty=True)
    f = bs.TextField(parent=app, textsignal=sig)
    root.update()
    changes = _watch(f)
    sig.clear()
    root.update()
    return "sig=%r display=%r value=%r changes=%r" % (
        sig(), f._internal._entry.get(), f.value, changes)


def q2_clear_then_cycle():
    sig = bs.Signal("hello", allow_empty=True)
    f = bs.TextField(parent=app, textsignal=sig)
    root.update()
    changes = _watch(f)
    sig.clear()
    root.update()
    at_clear = list(changes)
    _cycle(f._internal._entry)
    return "at_clear=%r after_cycle=%r value=%r" % (at_clear, changes, f.value)


def q2_clear_allow_blank_false():
    # allow_blank=False on the part keeps the prior value on an empty parse.
    sig = bs.Signal("hello", allow_empty=True)
    f = bs.TextField(parent=app, textsignal=sig, allow_blank=False)
    root.update()
    sig.clear()
    root.update()
    return "display=%r value=%r" % (f._internal._entry.get(), f.value)


# --- The placeholder guard round 1 added: is it ever True here? --------------

def guard_reachability():
    from bootstack.widgets._impl._parts.textentry_part import TextEntryPart
    seen = []
    original = TextEntryPart._commit_if_not_editing

    def spy(self):
        seen.append(self._showing_placeholder)
        return original(self)

    TextEntryPart._commit_if_not_editing = spy
    try:
        sig = bs.Signal("")
        f = bs.TextField(parent=app, textsignal=sig, placeholder="Type here")
        root.update()
        sig.set("written by code")
        root.update()
        sig.set("")
        root.update()
        sig.set("again")
        root.update()
        return "showing_placeholder_at_entry=%r value=%r display=%r" % (
            seen, f.value, f._internal._entry.get())
    finally:
        TextEntryPart._commit_if_not_editing = original


# --- Round 1 finding 2's resolution, re-measured -----------------------------

def nf_bounds():
    f = bs.NumberField(parent=app, value=5, min_value=0, max_value=10,
                       value_format="#,##0.00")
    entry = f._internal._entry
    root.update()
    f.value = 99
    root.update()
    before = "value=%r type=%s display=%r" % (f.value, type(f.value).__name__, entry.get())
    _cycle(entry)
    return "%s | after_blur value=%r display=%r" % (before, f.value, entry.get())


def nf_signal_write():
    sig = bs.Signal("5")
    f = bs.NumberField(parent=app, textsignal=sig) if False else None
    return "skipped: NumberField takes signal=, not textsignal="



def q1_property_setter_then_cycle():
    # Blast radius: `field.value = x` already set `_value` on BOTH arms, so the
    # snapshot on the next FocusIn was never stale here. Only the signal-write
    # path can differ.
    sig = bs.Signal("hello")
    f = bs.TextField(parent=app, textsignal=sig)
    root.update()
    changes = _watch(f)
    f.value = "world"
    root.update()
    at_write = list(changes)
    _cycle(f._internal._entry)
    return "at_write=%r after_cycle=%r value=%r" % (at_write, changes, f.value)


def q1_password_and_path():
    out = []
    for name in ("PasswordField", "PathField"):
        sig = bs.Signal("hello")
        f = getattr(bs, name)(parent=app, textsignal=sig)
        root.update()
        changes = _watch(f)
        sig.set("world")
        root.update()
        _cycle(f._internal._entry)
        out.append("%s after_cycle=%r value=%r" % (name, changes, f.value))
    return " | ".join(out)


for label, fn in [
    ("q1-write-then-cycle", q1_write_then_cycle),
    ("q1-spinner-write-then-cycle", q1_spinner_write_then_cycle),
    ("q1-control-no-write", q1_control_no_write),
    ("q1-control-typed-edit", q1_control_typed_edit),
    ("q1-write-then-type-it-back", q1_write_then_type_it_back),
    ("q2-clear-value", q2_clear_value),
    ("q2-clear-then-cycle", q2_clear_then_cycle),
    ("q2-clear-allow-blank-false", q2_clear_allow_blank_false),
    ("guard-reachability", guard_reachability),
    ("nf-bounds", nf_bounds),
    ("q1-property-setter-then-cycle", q1_property_setter_then_cycle),
    ("q1-password-and-path", q1_password_and_path),
]:
    arm(label, fn)

root.destroy()
